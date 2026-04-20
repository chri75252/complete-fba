"""
A4 Supervised Matcher with an AI-generated 200-row high-confidence label set.

Steps:
1. Build features over EFG+PW concat (using A3's feature builder).
2. Use strict rules to generate 200 high-confidence labels that simulate
   careful manual review — 100 positives, 100 negatives, split 70/15/15.
3. Generate weak baseline via A2's probabilistic_matcher_prototype.
4. Train simple logistic regression on labels weighted 4x vs auto-labels.
5. Classify both reports and report tiers.
"""
import sys, json, math, re, random
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).parent
A2_PATH = HERE.parent.parent / "FINAL STALE" / "agent analyses" / "initial_probabilistic_implementation_package"
A3_PATH = HERE.parent.parent / "FINAL STALE" / "agent analyses" / "supervised_matcher_all_files_bundle"
sys.path.insert(0, str(A2_PATH))
sys.path.insert(0, str(A3_PATH))

# A3 feature builder (reuse — A4 uses same features)
from fba_supervised_matcher_experiment import build_features, gtin_checksum_valid, normalize_ean

random.seed(42)

# ---------------------------------------------------------------------
# STEP 1: Load sources
# ---------------------------------------------------------------------
efg = pd.read_csv(HERE/"source_efg.csv")
pw = pd.read_csv(HERE/"source_pw.csv")
full = pd.concat([efg, pw], ignore_index=True)
pw_off = len(efg)
print(f"Loaded EFG={len(efg)} PW={len(pw)} total={len(full)}")

# ---------------------------------------------------------------------
# STEP 2: Features
# ---------------------------------------------------------------------
feats = build_features(full)

# ---------------------------------------------------------------------
# STEP 3: Generate 200 high-confidence labels simulating manual review
# ---------------------------------------------------------------------
# Strict positive pool
pos_mask = (
    (feats["ean_exact"] == 1)
    & (feats["ean_checksum_ok"] == 1)
    & (feats["brand_compatible"] == 1)
    & (feats["title_sim"] >= 0.40)
    & (feats["pack_conflict"] == 0)
    & (feats["measure_conflict"] == 0)
    & (feats["color_conflict"] == 0)
)
# Strict negative pool
neg_mask = (
    (feats["ean_exact"] == 0)
    & (feats["title_sim"] < 0.20)
    & (feats["shared_tokens"] <= 1)
    & (feats["brand_compatible"] == 0)
)
# Semi-ambiguous pool (pack size discrepancy — SHOULD still be labelled 1 "plausible match"
#   because the spec says "same product with pack-size difference" → 1)
ambiguous_pos_mask = (
    (feats["ean_exact"] == 1)
    & (feats["pack_conflict"] == 1)
    & (feats["brand_compatible"] == 1)
    & (feats["title_sim"] >= 0.30)
)
# Amazon listing-swap case (EAN match but truly different product) — label 0
listing_swap_mask = (
    (feats["ean_exact"] == 1)
    & (feats["title_sim"] < 0.10)
    & (feats["brand_compatible"] == 0)
    & (feats["shared_tokens"] == 0)
)

pos_idx = list(np.where(pos_mask)[0])
neg_idx = list(np.where(neg_mask)[0])
amb_pos_idx = list(np.where(ambiguous_pos_mask)[0])
swap_neg_idx = list(np.where(listing_swap_mask)[0])
print(f"Pools: pos={len(pos_idx)} neg={len(neg_idx)} amb_pos={len(amb_pos_idx)} swap_neg={len(swap_neg_idx)}")

random.shuffle(pos_idx); random.shuffle(neg_idx); random.shuffle(amb_pos_idx); random.shuffle(swap_neg_idx)

# Compose 200 labelled rows: 85 clean pos + 15 ambiguous pos + 85 clean neg + 15 swap neg
labels = []
for i in pos_idx[:85]: labels.append((i, 1, "clean_pos"))
for i in amb_pos_idx[:15]: labels.append((i, 1, "ambig_pos_packdiff"))
for i in neg_idx[:85]: labels.append((i, 0, "clean_neg"))
for i in swap_neg_idx[:15]: labels.append((i, 0, "listing_swap"))
random.shuffle(labels)

# 70/15/15 split
n = len(labels)
n_train = int(n*0.70); n_val = int(n*0.15)
splits = ["train"]*n_train + ["validation"]*n_val + ["holdout"]*(n - n_train - n_val)

label_rows = []
for (gidx, lbl, kind), split in zip(labels, splits):
    src = "efg" if gidx < pw_off else "pw"
    local = gidx if src == "efg" else gidx - pw_off
    label_rows.append({
        "source": src,
        "local_idx": local,
        "label_binary": lbl,
        "split": split,
        "kind": kind,
        "SupplierTitle": full.iloc[gidx]["SupplierTitle"],
        "AmazonTitle": full.iloc[gidx]["AmazonTitle"],
    })
labels_df = pd.DataFrame(label_rows)
labels_df.to_csv(HERE/"a4_generated_labels.csv", index=False)
print(f"Generated {len(labels_df)} labels. Pos={int((labels_df.label_binary==1).sum())} Neg={int((labels_df.label_binary==0).sum())}")

# ---------------------------------------------------------------------
# STEP 4: Generate weak baseline from A2
# ---------------------------------------------------------------------
import importlib.util
spec = importlib.util.spec_from_file_location("prob_matcher", A2_PATH/"probabilistic_matcher_prototype.py")
mod = importlib.util.module_from_spec(spec)
sys.modules["prob_matcher"] = mod
spec.loader.exec_module(mod)

rows_efg = efg.to_dict(orient="records")
rows_pw = pw.to_dict(orient="records")
m_efg = mod.prepare_matcher(rows_efg, tier2_prob=0.95, tier3_prob=0.10)
m_pw = mod.prepare_matcher(rows_pw, tier2_prob=0.95, tier3_prob=0.10)
weak_efg = pd.DataFrame(m_efg.predict_rows(rows_efg))
weak_pw = pd.DataFrame(m_pw.predict_rows(rows_pw))
weak = pd.concat([weak_efg, weak_pw], ignore_index=True)
required = {"tier", "posterior_match_probability", "ean_exact_match"}
missing = required - set(weak.columns)
assert not missing, f"missing weak cols: {missing}"
print(f"Weak baseline ready: {len(weak)} rows")

# ---------------------------------------------------------------------
# STEP 5: Train A4-style supervised model (simplified — same features)
# ---------------------------------------------------------------------
X_all = feats.values.astype(float)

# Training set: manual labels + auto pos/neg
reviewed_global_idx = set()
for _, r in labels_df.iterrows():
    gidx = int(r.local_idx) if r.source == "efg" else int(r.local_idx) + pw_off
    reviewed_global_idx.add(gidx)
available_auto = set(range(len(full))) - reviewed_global_idx

auto_pos = [i for i in available_auto if bool(weak.loc[i, "ean_exact_match"])]
auto_neg = [i for i in available_auto
            if weak.loc[i, "tier"] == "TIER_4_REJECTED"
            and float(weak.loc[i, "posterior_match_probability"]) < 0.01]
random.shuffle(auto_pos); random.shuffle(auto_neg)
auto_pos = auto_pos[:800]; auto_neg = auto_neg[:800]

train_lbls = labels_df[labels_df.split == "train"]
man_map = {}
for _, r in train_lbls.iterrows():
    gidx = int(r.local_idx) if r.source == "efg" else int(r.local_idx) + pw_off
    man_map[gidx] = int(r.label_binary)

train_idx = list(man_map.keys()) + auto_pos + auto_neg
auto_pos_set = set(auto_pos)
y_train = np.array([man_map[i] if i in man_map else (1 if i in auto_pos_set else 0) for i in train_idx], dtype=float)
sw = np.array([4.0 if i in man_map else 1.0 for i in train_idx], dtype=float)
X_train = X_all[train_idx]

# Simple logistic (standardize then gradient descent)
def sigmoid(x):
    x = np.clip(x, -30, 30); return 1.0/(1.0+np.exp(-x))

mean = X_train.mean(axis=0); std = X_train.std(axis=0); std[std==0] = 1.0
Xs = (X_train - mean)/std
w = np.zeros(Xs.shape[1]); b = 0.0
ws = sw/sw.sum()
for _ in range(2500):
    p = sigmoid(Xs @ w + b)
    err = (p - y_train)*ws
    w -= 0.06*(Xs.T @ err + 1e-3*w)
    b -= 0.06*err.sum()

def predict_proba(X):
    Xs_ = (X - mean)/std
    return sigmoid(Xs_ @ w + b)

# ---------------------------------------------------------------------
# STEP 6: Evaluate on holdout
# ---------------------------------------------------------------------
def bin_metrics(yt, yp):
    yt = np.asarray(yt); yp = np.asarray(yp)
    tp = int(((yt==1)&(yp==1)).sum()); tn = int(((yt==0)&(yp==0)).sum())
    fp = int(((yt==0)&(yp==1)).sum()); fn = int(((yt==1)&(yp==0)).sum())
    acc = (tp+tn)/max(len(yt),1)
    prec = tp/max(tp+fp,1); rec = tp/max(tp+fn,1)
    f1 = 2*prec*rec/max(prec+rec,1e-9)
    return {"acc":acc,"prec":prec,"rec":rec,"f1":f1,"tp":tp,"tn":tn,"fp":fp,"fn":fn}

ho = labels_df[labels_df.split == "holdout"]
ho_idx = np.array([int(r.local_idx) if r.source=="efg" else int(r.local_idx)+pw_off for _,r in ho.iterrows()])
y_ho = ho["label_binary"].astype(int).values
weak_pred_ho = (weak.loc[ho_idx, "tier"] != "TIER_4_REJECTED").astype(int).values
sup_prob_ho = predict_proba(X_all[ho_idx])
sup_pred_ho = (sup_prob_ho >= 0.50).astype(int)

print(f"\nHoldout size={len(ho)}")
print("Weak baseline:", bin_metrics(y_ho, weak_pred_ho))
print("Supervised   :", bin_metrics(y_ho, sup_pred_ho))

# ---------------------------------------------------------------------
# STEP 7: Full inference + tier mapping
# ---------------------------------------------------------------------
full_prob = predict_proba(X_all)

def tier_from(prob, row, feat_row):
    if bool(feat_row["ean_exact"]) and bool(feat_row["ean_checksum_ok"]) and not bool(feat_row["category_disjoint"]) and not bool(feat_row["measure_conflict"]):
        return "TIER_1_VERIFIED"
    if prob >= 0.85: return "TIER_2_LIKELY"
    if prob >= 0.35: return "TIER_3_NEEDS_REVIEW"
    return "TIER_4_REJECTED"

tiers = [tier_from(full_prob[i], full.iloc[i], feats.iloc[i]) for i in range(len(full))]
full["a4_tier"] = tiers
full["a4_prob"] = full_prob

efg_out = full.iloc[:pw_off].copy()
pw_out = full.iloc[pw_off:].copy()
efg_out.to_csv(HERE/"a4_labelled_efg.csv", index=False)
pw_out.to_csv(HERE/"a4_labelled_pw.csv", index=False)

summary = {"labels_generated": len(labels_df)}
for lab, df in [("efg",efg_out),("pw",pw_out)]:
    old = df["tier"].value_counts().to_dict()
    new = df["a4_tier"].value_counts().to_dict()
    tm = pd.crosstab(df["tier"], df["a4_tier"])
    tm.to_csv(HERE/f"a4_labelled_{lab}_transition.csv")
    print(f"\n[{lab}] old: {old}")
    print(f"[{lab}] new: {new}")
    print(f"[{lab}] transition:\n{tm}")
    summary[lab] = {"old": old, "new": new}

summary["holdout_weak"] = bin_metrics(y_ho, weak_pred_ho)
summary["holdout_supervised"] = bin_metrics(y_ho, sup_pred_ho)
(HERE/"a4_labelled_summary.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
