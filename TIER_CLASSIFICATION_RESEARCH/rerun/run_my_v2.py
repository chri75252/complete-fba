"""Run tier_classifier_v2.py on full EFG and PW files."""
import sys
import json
from pathlib import Path
import pandas as pd

HERE = Path(__file__).parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from tier_classifier_v2 import classify_batch

def run(label, src):
    df = pd.read_csv(src)
    rows = df.to_dict(orient="records")
    results = classify_batch(rows)
    new_tiers = [r["tier"] for r in results]
    new_conf = [r["confidence_score"] for r in results]
    new_flags = [" | ".join(r.get("flags", [])) for r in results]

    out = df.copy()
    out["v2_tier"] = new_tiers
    out["v2_confidence"] = new_conf
    out["v2_flags"] = new_flags

    out.to_csv(HERE / f"my_v2_{label}.csv", index=False)

    # Tier distribution
    old = df["tier"].value_counts().to_dict()
    new = pd.Series(new_tiers).value_counts().to_dict()
    # Transition matrix
    tm = pd.crosstab(df["tier"], pd.Series(new_tiers, index=df.index))
    tm.to_csv(HERE / f"my_v2_{label}_transition.csv")
    changed = (df["tier"] != pd.Series(new_tiers, index=df.index)).sum()
    print(f"[{label}] rows={len(df)} changed={changed}")
    print(f"  old: {old}")
    print(f"  new: {new}")
    print(f"  transition:\n{tm}")
    return {"label": label, "rows": len(df), "changed": int(changed), "old": old, "new": new}

if __name__ == "__main__":
    summary = {}
    for label in ("efg","pw"):
        summary[label] = run(label, HERE / f"source_{label}.csv")
    (HERE / "my_v2_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("\nDone.")
