"""Run A1 hybrid classifier with corrected column names on full files."""
import sys, json
from pathlib import Path
import pandas as pd

HERE = Path(__file__).parent
A1_PATH = HERE.parent.parent / "FINAL STALE" / "agent analyses" / "hybrid_probabilistic_classifier_package"
sys.path.insert(0, str(A1_PATH))
from fba_tier_classifier import FBATierClassifier

CLASS_TO_TIER = {1: "TIER_1_VERIFIED", 2: "TIER_2_LIKELY", 3: "TIER_3_NEEDS_REVIEW", 4: "TIER_4_REJECTED"}

def run(label, src):
    df = pd.read_csv(src)
    clf = FBATierClassifier()
    tiers, confs, reasons = [], [], []
    for _, r in df.iterrows():
        # Map real column names to the names A1 expects
        row = {
            "Supplier Title": r.get("SupplierTitle", ""),
            "Amazon Title": r.get("AmazonTitle", ""),
            "Supplier EAN": r.get("EAN", ""),
            "Amazon EAN": r.get("EAN_OnPage", ""),
        }
        t, reason, c = clf.classify_row(row)
        tiers.append(CLASS_TO_TIER[t]); confs.append(c); reasons.append(reason)

    df["a1_tier"] = tiers
    df["a1_confidence"] = confs
    df["a1_reason"] = reasons
    df.to_csv(HERE / f"a1_fixed_{label}.csv", index=False)

    old = df["tier"].value_counts().to_dict()
    new = pd.Series(tiers).value_counts().to_dict()
    tm = pd.crosstab(df["tier"], pd.Series(tiers, index=df.index))
    tm.to_csv(HERE / f"a1_fixed_{label}_transition.csv")
    changed = (df["tier"] != pd.Series(tiers, index=df.index)).sum()
    print(f"[{label}] rows={len(df)} changed={changed}")
    print(f"  old: {old}")
    print(f"  new: {new}")
    print(f"  transition:\n{tm}")
    return {"label": label, "rows": len(df), "changed": int(changed), "old": old, "new": new}

if __name__ == "__main__":
    out = {}
    for label in ("efg","pw"):
        out[label] = run(label, HERE / f"source_{label}.csv")
    (HERE / "a1_fixed_summary.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
