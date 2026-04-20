"""
A3 Supervised v2 RETRAINED on clean labels derived from data itself (not from
the broken 'tier' column). Uses the same feature framework as the original.

Clean-label policy:
- Positive (class 2 EXACT): EAN exact + GS1 checksum valid on BOTH sides AND
  title_sim >= 0.25 (guards against Amazon listing-swap)
- Negative (class 0 NON_MATCH): very low char_cos AND jaccard AND no brand
  overlap AND no EAN match
- Middle (class 1 RELATED): everything else is unlabelled; we do NOT train
  on it to avoid tier-column pollution.

Training uses only the high-confidence positives and negatives.
"""
import sys, json, math, re
from pathlib import Path
from difflib import SequenceMatcher
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

HERE = Path(__file__).parent
A3_PATH = HERE.parent.parent / "FINAL STALE" / "agent analyses" / "supervised_matcher_all_files_bundle"
sys.path.insert(0, str(A3_PATH))
from fba_supervised_matcher_experiment import build_features, pick_threshold, map_tiers, normalize_ean, gtin_checksum_valid, normalize_text, text_tokens, meaningful_tokens, extract_brand_guess

def clean_labels(df, feats):
    """Derive CLEAN labels from features, ignoring the broken tier column."""
    labels = np.full(len(df), -1, dtype=int)  # -1 = unlabelled
    for i in range(len(df)):
        ean_exact = bool(feats.iloc[i]["ean_exact"])
        checksum_ok = bool(feats.iloc[i]["ean_checksum_ok"])
        title_sim = float(feats.iloc[i]["title_sim"])
        shared_tok = int(feats.iloc[i]["shared_tokens"])
        brand_compat = bool(feats.iloc[i]["brand_compatible"])
        pack_conflict = bool(feats.iloc[i]["pack_conflict"])
        meas_conflict = bool(feats.iloc[i]["measure_conflict"])
        color_conf = bool(feats.iloc[i]["color_conflict"])
        ean_mismatch = bool(feats.iloc[i]["ean_mismatch"])

        # POSITIVE (EXACT=class 2)
        if ean_exact and checksum_ok and title_sim >= 0.25:
            labels[i] = 2
            continue
        # Strong non-EAN positive: high title_sim + brand match + no hard conflict
        if title_sim >= 0.70 and brand_compat and shared_tok >= 3 and not (pack_conflict or meas_conflict or color_conf):
            labels[i] = 2
            continue
        # NEGATIVE (NON_MATCH=class 0)
        if title_sim < 0.15 and shared_tok <= 1 and not brand_compat and not ean_exact:
            labels[i] = 0
            continue
        if ean_mismatch and title_sim < 0.25 and not brand_compat:
            labels[i] = 0
            continue
        # otherwise unlabelled
    return labels

def main():
    dfs = {lab: pd.read_csv(HERE/f"source_{lab}.csv") for lab in ("efg","pw")}
    feats_all = {lab: build_features(dfs[lab]) for lab in dfs}

    # Clean labels for training
    lbl_efg = clean_labels(dfs["efg"], feats_all["efg"])
    lbl_pw = clean_labels(dfs["pw"], feats_all["pw"])

    X_all = pd.concat([feats_all["efg"], feats_all["pw"]], ignore_index=True)
    y_all = np.concatenate([lbl_efg, lbl_pw])

    mask = y_all != -1
    X_tr_cal = X_all[mask]
    y_tr_cal = y_all[mask]

    print(f"Clean label distribution: pos={int((y_tr_cal==2).sum())} neg={int((y_tr_cal==0).sum())} skipped={int((~mask).sum())}/{len(y_all)}")

    # Ensure at least two classes; add synthetic RELATED (class 1) from borderline rows for multinomial
    # Use rows with title_sim in [0.4, 0.6] and brand_compat as class 1 anchors
    related_mask = (
        (X_all["title_sim"].between(0.35, 0.65))
        & (X_all["brand_compatible"] == 1)
        & (y_all == -1)
    )
    rel_idx = np.where(related_mask)[0][:400]  # cap
    X_tr_cal = pd.concat([X_tr_cal, X_all.iloc[rel_idx]], ignore_index=True)
    y_tr_cal = np.concatenate([y_tr_cal, np.ones(len(rel_idx), dtype=int)])
    print(f"Added {len(rel_idx)} synthetic class-1 (RELATED) anchors")

    X_train, X_cal, y_train, y_cal = train_test_split(
        X_tr_cal, y_tr_cal, test_size=0.25, random_state=42, stratify=y_tr_cal
    )
    from sklearn.frozen import FrozenEstimator
    base = LogisticRegression(max_iter=6000, solver="lbfgs")
    base.fit(X_train, y_train)
    cal = CalibratedClassifierCV(FrozenEstimator(base), method="sigmoid")
    cal.fit(X_cal, y_cal)

    # Threshold selection on cal split
    proba_cal = cal.predict_proba(X_cal)
    classes = list(cal.classes_)
    idx_ex = classes.index(2); idx_non = classes.index(0)
    p_ex_cal = proba_cal[:, idx_ex]; p_non_cal = proba_cal[:, idx_non]
    p_exact_t2 = pick_threshold(p_ex_cal, y_cal, 2, 0.95, 100)
    p_nonmatch_t4 = pick_threshold(p_non_cal, y_cal, 0, 0.95, 100)
    p_exact_t1 = max(p_exact_t2, float(np.quantile(p_ex_cal[y_cal == 2], 0.75)) if (y_cal == 2).any() else p_exact_t2)
    print(f"Thresholds: T1_exact={p_exact_t1:.3f}  T2_exact={p_exact_t2:.3f}  T4_non={p_nonmatch_t4:.3f}")

    # Predict per supplier
    summary = {"thresholds": {"p_exact_t1":p_exact_t1,"p_exact_t2":p_exact_t2,"p_nonmatch_t4":p_nonmatch_t4}}
    for lab in ("efg","pw"):
        X = feats_all[lab]
        proba = cal.predict_proba(X)
        # Reorder to ensure [non, rel, ex]
        proba_ordered = np.column_stack([
            proba[:, classes.index(0)],
            proba[:, classes.index(1)] if 1 in classes else np.zeros(len(X)),
            proba[:, classes.index(2)],
        ])
        tiers, states, pex, prel, pnon = map_tiers(X, proba_ordered, p_exact_t1, p_exact_t2, p_nonmatch_t4)
        df = dfs[lab].copy()
        df["a3corr_tier"] = tiers
        df["a3corr_p_exact"] = np.round(pex, 4)
        df["a3corr_p_non"] = np.round(pnon, 4)
        df.to_csv(HERE/f"a3_corrected_{lab}.csv", index=False)

        new = pd.Series(tiers).value_counts().to_dict()
        old = df["tier"].value_counts().to_dict()
        tm = pd.crosstab(df["tier"], pd.Series(tiers, index=df.index))
        tm.to_csv(HERE/f"a3_corrected_{lab}_transition.csv")
        print(f"[{lab}] old: {old}")
        print(f"[{lab}] new: {new}")
        print(f"[{lab}] transition:\n{tm}\n")
        summary[lab] = {"old": old, "new": new}

    (HERE/"a3_corrected_summary.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")

if __name__ == "__main__":
    main()
