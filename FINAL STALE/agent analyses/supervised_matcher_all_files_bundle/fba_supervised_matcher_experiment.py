#!/usr/bin/env python3
"""
Supervised Matcher Experiment (v2)
- Inputs: two CSVs with SupplierTitle/AmazonTitle/EAN/EAN_OnPage (+ optional numeric fields)
- Trains a 3-class matcher using WEAK labels derived from existing 'tier' column.
- Calibrates probabilities on a held-out calibration split (Platt scaling / sigmoid).
- Selects probability thresholds from the calibration split to hit a target precision.
- Generates:
  - tiered outputs for both files (with original + supervised tiers)
  - summary counts + JSON
  - original-vs-supervised crosstabs
"""

import argparse
import json
import math
import re
from difflib import SequenceMatcher
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split


# -----------------------------
# Tunable dictionaries / parsing knobs
# -----------------------------
STOP_WORDS = {
    "the","a","an","and","or","for","of","in","to","with","is","by","on","at","from",
    "new","free","ideal","safe","gift","great","classic","quality","lightweight","heavy",
    "duty","kitchen","home","office","outdoor","indoor",
}
PACK_WORDS = {"pack","pk","set","pc","pcs","pair","pairs","assorted","cdu"}
UNIT_WORDS = {"ml","l","litre","liter","g","kg","cm","mm","m","inch","in","oz","w","v","mah","lm","ft","foot"}
COLOR_WORDS = {
    "black","white","blue","red","green","yellow","pink","purple","grey","gray","silver","gold",
    "orange","brown","cream","clear","assorted","natural","fawn","pearl","daylight","warm","cool","matt",
}
CATEGORY_KEYWORDS = {
    "lighting": ["led","bulb","gu10","e27","b22","bc","es","lamp","batten","daylight","warm","lumens"],
    "kitchenware": ["bowl","plate","mug","glass","cup","baking","pastry","dough","cookies","earthenware"],
    "aircare": ["freshener","air","gel","scent","scents","potpourri","diffuser"],
    "cleaning": ["wipe","wipes","detergent","soap","bleach","brush","cloth"],
    "hardware": ["nails","screws","knife","utility","padlock","glue","epoxy","tool"],
    "garden": ["pot","planter","hose","spray","connector"],
}

TIER_TO_CLASS = {
    "TIER_1_VERIFIED": 2,
    "TIER_2_LIKELY": 2,
    "TIER_3_NEEDS_REVIEW": 1,
    "TIER_4_REJECTED": 0,
}

# -----------------------------
# Text / parsing utilities
# -----------------------------
def normalize_text(text: str) -> str:
    text = (text or "").lower()
    text = text.replace("&", " and ").replace("+", " plus ")
    text = re.sub(r"[^a-z0-9./ -]", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def text_tokens(text: str):
    return re.findall(r"[a-z0-9]+", normalize_text(text))

def meaningful_tokens(text: str):
    toks=[]
    for t in text_tokens(text):
        if t in STOP_WORDS or t in PACK_WORDS or t in COLOR_WORDS or t in UNIT_WORDS:
            continue
        if len(t) < 3:
            continue
        toks.append(t)
    return toks

def shared_token_count(a: str, b: str) -> int:
    return len(set(meaningful_tokens(a)) & set(meaningful_tokens(b)))

def title_similarity(a: str, b: str) -> float:
    a_clean = normalize_text(a); b_clean = normalize_text(b)
    if not a_clean or not b_clean:
        return 0.0
    return SequenceMatcher(None, a_clean, b_clean).ratio()

def normalize_ean(raw) -> str:
    if raw is None:
        return ""
    if isinstance(raw, float) and math.isnan(raw):
        return ""
    s = str(raw).strip()
    if not s:
        return ""
    if s.endswith(".0"):
        s = s[:-2]
    if "e" in s.lower():
        try:
            s = str(int(float(s)))
        except Exception:
            pass
    s = re.sub(r"[^0-9]", "", s)
    return s if len(s) in (8, 12, 13, 14) else ""

def gtin_checksum_valid(ean: str) -> bool:
    if not ean or len(ean) not in (8,12,13,14):
        return False
    digits = [int(d) for d in ean]
    check = digits[-1]
    payload = digits[:-1]
    total = 0
    for i, d in enumerate(reversed(payload)):
        total += d * (3 if i % 2 == 0 else 1)
    expected = (10 - (total % 10)) % 10
    return expected == check

def infer_categories(text: str):
    t = normalize_text(text)
    cats=set()
    for cat, kws in CATEGORY_KEYWORDS.items():
        if any(k in t for k in kws):
            cats.add(cat)
    return cats

def extract_pack_count(text: str):
    t = normalize_text(text)
    pats = [
        r"pack of (\d+)", r"set of (\d+)",
        r"\b(\d+)\s*pack\b", r"\b(\d+)\s*pk\b",
        r"\b(\d+)\s*pc\b", r"\b(\d+)\s*pcs\b",
        r"\b(\d+)\s*pair\b", r"\b(\d+)\s*pairs\b",
    ]
    vals=[]
    for p in pats:
        for m in re.finditer(p, t):
            vals.append(int(m.group(1)))
    return max(vals) if vals else None

def extract_measurements(text: str):
    t = normalize_text(text)
    out=[]
    for m in re.finditer(r"(\d+(?:\.\d+)?)\s*(ml|l|litre|liter|g|kg|cm|mm|m|inch|in|oz|w|v|mah|lm|ft)\b", t):
        val=float(m.group(1))
        unit=m.group(2)
        if unit=="liter":
            unit="litre"
        out.append((unit,val))
    return out

def comparable_measure_alignment(a: str, b: str):
    ma=extract_measurements(a); mb=extract_measurements(b)
    if not ma or not mb:
        return 0,0
    for ua,va in ma:
        same=[vb for ub,vb in mb if ub==ua]
        if not same:
            continue
        vb=same[0]
        ratio=max(va,vb)/max(min(va,vb),1e-9)
        if ratio<=1.15:
            return 1,0
        if ratio>=1.6:
            return 0,1
    return 0,0

def color_sets(text: str):
    return {t for t in text_tokens(text) if t in COLOR_WORDS}

def color_conflict(a: str, b: str) -> int:
    ca=color_sets(a); cb=color_sets(b)
    return int(bool(ca) and bool(cb) and ca.isdisjoint(cb))

def model_tokens(text: str):
    out=set()
    for tok in text_tokens(text):
        if re.search(r"[a-z]", tok) and re.search(r"\d", tok) and len(tok) >= 3:
            out.add(tok)
        elif re.fullmatch(r"(gu10|e27|b22|bc|es|aa|aaa)", tok):
            out.add(tok)
    return out

def extract_brand_guess(title: str) -> str:
    generic = {"glass","bowl","led","bulb","mini","mixing","pot","pack","air","freshener","fresheners"}
    toks=text_tokens(title); parts=[]
    for tok in toks[:6]:
        if tok.isdigit() or tok in UNIT_WORDS or tok in PACK_WORDS or len(tok)<=1:
            continue
        if not parts and tok in generic:
            continue
        parts.append(tok)
        if len(parts)==2:
            break
    return "".join(parts) if parts else ""

def brand_compatible(a: str, b: str) -> int:
    if not a or not b:
        return 0
    return int(a==b or a in b or b in a)

def safe_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

# -----------------------------
# Feature builder
# -----------------------------
def build_features(df: pd.DataFrame) -> pd.DataFrame:
    required = ["SupplierTitle","AmazonTitle","EAN","EAN_OnPage"]
    for c in required:
        if c not in df.columns:
            raise ValueError(f"Missing required column: {c}")

    st=df["SupplierTitle"].fillna("")
    at=df["AmazonTitle"].fillna("")
    se=df["EAN"].apply(normalize_ean)
    ae=df["EAN_OnPage"].apply(normalize_ean)

    feats=pd.DataFrame(index=df.index)
    feats["supplier_ean_present"]=(se!="").astype(int)
    feats["amazon_ean_present"]=(ae!="").astype(int)
    feats["ean_exact"]=((se!="")&(ae!="")&(se==ae)).astype(int)
    feats["ean_mismatch"]=((se!="")&(ae!="")&(se!=ae)).astype(int)
    feats["ean_checksum_ok"]=se.apply(gtin_checksum_valid).astype(int)*ae.apply(gtin_checksum_valid).astype(int)

    feats["title_sim"]=[title_similarity(a,b) for a,b in zip(st,at)]
    feats["shared_tokens"]=[shared_token_count(a,b) for a,b in zip(st,at)]

    sb=st.apply(extract_brand_guess); ab=at.apply(extract_brand_guess)
    feats["brand_compatible"]=[brand_compatible(a,b) for a,b in zip(sb,ab)]

    sp=st.apply(extract_pack_count); ap=at.apply(extract_pack_count)
    feats["pack_supplier"]=sp.fillna(0).astype(int)
    feats["pack_amazon"]=ap.fillna(0).astype(int)
    feats["pack_conflict"]=((sp.notna())&(ap.notna())&(sp!=ap)).astype(int)

    al_conf=[comparable_measure_alignment(a,b) for a,b in zip(st,at)]
    feats["measure_aligned"]=[x for x,y in al_conf]
    feats["measure_conflict"]=[y for x,y in al_conf]
    feats["color_conflict"]=[color_conflict(a,b) for a,b in zip(st,at)]

    sm=st.apply(model_tokens); am=at.apply(model_tokens)
    feats["model_overlap"]=[len(x&y) for x,y in zip(sm,am)]

    sc=st.apply(infer_categories); ac=at.apply(infer_categories)
    feats["category_overlap"]=[len(x&y) for x,y in zip(sc,ac)]
    feats["category_disjoint"]=[int(bool(x) and bool(y) and len(x&y)==0) for x,y in zip(sc,ac)]

    s_price=df.get("SupplierPrice_incVAT",0).apply(safe_float)
    a_price=df.get("SellingPrice_incVAT",0).apply(safe_float)
    roi=df.get("ROI",0).apply(safe_float)
    profit=df.get("NetProfit",0).apply(safe_float)

    feats["log_price_ratio"]=np.log(np.clip((a_price+1e-6)/(s_price+1e-6),1e-6,1e6))
    feats["roi_capped"]=np.clip(roi,0,500)/500.0
    feats["profit_sign"]=(profit>0).astype(int)
    return feats

# -----------------------------
# Threshold selection
# -----------------------------
def pick_threshold(p: np.ndarray, y_true: np.ndarray, target_class: int, precision_target: float, min_support: int) -> float:
    candidates=np.unique(np.quantile(p, np.linspace(0.5, 0.99, 80)))
    for thr in sorted(candidates, reverse=True):
        sel=p>=thr
        if sel.sum() < min_support:
            continue
        prec=(y_true[sel]==target_class).mean()
        if prec >= precision_target:
            return float(thr)
    return float(np.quantile(p, 0.95))

def map_tiers(X: pd.DataFrame, proba: np.ndarray, p_exact_t1: float, p_exact_t2: float, p_nonmatch_t4: float):
    p_non,p_rel,p_ex = proba[:,0], proba[:,1], proba[:,2]
    hard = (X["category_disjoint"].astype(bool) | X["measure_conflict"].astype(bool)).values
    ean_exact = X["ean_exact"].values.astype(bool)
    checksum = X["ean_checksum_ok"].values.astype(bool)

    tiers=[]; states=[]
    for i in range(len(X)):
        if ean_exact[i] and checksum[i] and (p_ex[i] >= p_exact_t1) and not hard[i]:
            tiers.append("TIER_1_VERIFIED"); states.append("EXACT_UNIT")
        elif (p_non[i] >= p_nonmatch_t4) and not ean_exact[i]:
            tiers.append("TIER_4_REJECTED"); states.append("NON_MATCH")
        elif (p_ex[i] >= p_exact_t2) and not hard[i]:
            tiers.append("TIER_2_LIKELY"); states.append("LIKELY_SAME_UNIT")
        else:
            tiers.append("TIER_3_NEEDS_REVIEW"); states.append("RELATED_OR_INCOMPLETE")
    return tiers, states, p_ex, p_rel, p_non

# -----------------------------
# Main
# -----------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pound", required=True, help="Path to poundwholesale analysis CSV (must include tier column for weak labels)")
    ap.add_argument("--efg", required=True, help="Path to efg analysis CSV (must include tier column for weak labels)")
    ap.add_argument("--outdir", required=True, help="Output directory")
    ap.add_argument("--precision_target", type=float, default=0.95, help="Target precision for threshold selection (weak-label eval)")
    ap.add_argument("--min_support", type=int, default=200, help="Minimum rows above threshold when selecting thresholds")
    ap.add_argument("--calibration_size", type=float, default=0.25, help="Held-out calibration split size")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    pound_df = pd.read_csv(args.pound)
    efg_df   = pd.read_csv(args.efg)

    if "tier" not in pound_df.columns or "tier" not in efg_df.columns:
        raise ValueError("Both inputs must include a 'tier' column for the weak-label experiment baseline.")

    Xp = build_features(pound_df)
    Xe = build_features(efg_df)

    yp = pound_df["tier"].astype(str).map(TIER_TO_CLASS).astype(int)
    ye = efg_df["tier"].astype(str).map(TIER_TO_CLASS).astype(int)

    X_all = pd.concat([Xp, Xe], ignore_index=True)
    y_all = pd.concat([yp, ye], ignore_index=True)

    X_train, X_cal, y_train, y_cal = train_test_split(
        X_all, y_all, test_size=args.calibration_size, random_state=42, stratify=y_all
    )

    base = LogisticRegression(max_iter=6000, solver="lbfgs", multi_class="multinomial", n_jobs=-1)
    base.fit(X_train, y_train)

    cal = CalibratedClassifierCV(base, method="sigmoid", cv="prefit")
    cal.fit(X_cal, y_cal)

    proba_cal = cal.predict_proba(X_cal)
    p_non_cal, p_ex_cal = proba_cal[:,0], proba_cal[:,2]

    p_exact_t2 = pick_threshold(p_ex_cal, y_cal.values, 2, args.precision_target, args.min_support)
    p_nonmatch_t4 = pick_threshold(p_non_cal, y_cal.values, 0, args.precision_target, args.min_support)
    # T1 slightly stricter than T2; also require exact EAN + checksum
    if (y_cal.values == 2).any():
        p_exact_t1 = max(p_exact_t2, float(np.quantile(p_ex_cal[y_cal.values==2], 0.75)))
    else:
        p_exact_t1 = p_exact_t2

    # Predict + map tiers
    tiers_p, states_p, pex_p, prel_p, pnon_p = map_tiers(Xp, cal.predict_proba(Xp), p_exact_t1, p_exact_t2, p_nonmatch_t4)
    tiers_e, states_e, pex_e, prel_e, pnon_e = map_tiers(Xe, cal.predict_proba(Xe), p_exact_t1, p_exact_t2, p_nonmatch_t4)

    def merge(df_in, tiers, states, pex, prel, pnon):
        df = df_in.rename(columns={
            "tier":"tier_original",
            "confidence_score":"confidence_original",
            "flags":"flags_original",
            "reasons":"reasons_original",
            "ean_exact_match":"ean_exact_match_original",
        })
        df["tier_supervised"]=tiers
        df["match_state_supervised"]=states
        df["p_exact"]=np.round(pex,4)
        df["p_related"]=np.round(prel,4)
        df["p_nonmatch"]=np.round(pnon,4)
        return df

    pound_out = merge(pound_df, tiers_p, states_p, pex_p, prel_p, pnon_p)
    efg_out   = merge(efg_df, tiers_e, states_e, pex_e, prel_e, pnon_e)

    pound_out_path = outdir / "poundwholesale_supervised_tiered.csv"
    efg_out_path   = outdir / "efghousewares_supervised_tiered.csv"
    pound_out.to_csv(pound_out_path, index=False)
    efg_out.to_csv(efg_out_path, index=False)

    # Crosstabs
    pound_ct = pd.crosstab(pound_out["tier_original"], pound_out["tier_supervised"])
    efg_ct   = pd.crosstab(efg_out["tier_original"], efg_out["tier_supervised"])
    pound_ct.to_csv(outdir / "poundwholesale_original_vs_supervised_crosstab.csv")
    efg_ct.to_csv(outdir / "efghousewares_original_vs_supervised_crosstab.csv")

    # Summary counts
    def tier_counts(s): return s.value_counts().to_dict()
    summary = {
        "inputs": {"pound": str(args.pound), "efg": str(args.efg)},
        "weak_labeling": {"tier_to_class": TIER_TO_CLASS},
        "model": {"type":"LogisticRegression(multinomial)", "calibration":"Platt/sigmoid on held-out split"},
        "thresholds_selected_from_calibration": {
            "precision_target": args.precision_target,
            "min_support": args.min_support,
            "calibration_size": args.calibration_size,
            "P_EXACT_T2": p_exact_t2,
            "P_EXACT_T1": p_exact_t1,
            "P_NONMATCH_T4": p_nonmatch_t4,
        },
        "counts": {
            "pound_original": tier_counts(pound_out["tier_original"]),
            "pound_supervised": tier_counts(pound_out["tier_supervised"]),
            "efg_original": tier_counts(efg_out["tier_original"]),
            "efg_supervised": tier_counts(efg_out["tier_supervised"]),
        }
    }
    (outdir / "supervised_matcher_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    rows=[]
    for rep,orig,sup in [("poundwholesale", summary["counts"]["pound_original"], summary["counts"]["pound_supervised"]),
                         ("efghousewares", summary["counts"]["efg_original"], summary["counts"]["efg_supervised"])]:
        for t in sorted(set(orig)|set(sup)):
            rows.append({"report":rep,"tier":t,"count_original":orig.get(t,0),"count_supervised":sup.get(t,0)})
    pd.DataFrame(rows).to_csv(outdir / "supervised_matcher_summary_counts.csv", index=False)

    print("Wrote:")
    print(" ", pound_out_path.name)
    print(" ", efg_out_path.name)
    print(" ", "supervised_matcher_summary_counts.csv")
    print(" ", "supervised_matcher_summary.json")

if __name__ == "__main__":
    main()
