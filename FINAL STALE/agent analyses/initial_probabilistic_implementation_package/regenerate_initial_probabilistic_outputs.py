#!/usr/bin/env python3
"""
Regenerate initial probabilistic matcher outputs on the correct full-row analysis files.

This script:
- loads the local probabilistic_matcher_prototype.py,
- runs it on the two specified analysis CSVs,
- preserves the existing tier/confidence columns already present in those CSVs,
- appends the newly generated outputs as:
    new_tier
    new_confidence_score
    new_reasons
    new_flags
    new_ean_exact_match
    posterior_match_probability
- writes per-file regenerated CSVs,
- writes tier-change CSVs,
- writes per-file and master summaries.

Expected local prerequisites:
- probabilistic_matcher_prototype.py exists locally
- the two analysis CSVs exist locally
"""

from pathlib import Path
import json
import types
import sys
import pandas as pd

BASE_DIR = Path(".")
PROTOTYPE_PATH = BASE_DIR / "probabilistic_matcher_prototype.py"
OUTPUT_DIR = BASE_DIR / "initial_probabilistic_regenerated_outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

INPUTS = {
    "efg_latest_analysis": BASE_DIR / "efg latestfba_analysis_2026-04-17.csv",
    "pound_latest_analysis": BASE_DIR / "poundhwolesalefba_analysis_2026-04-15 (1) (1).csv",
}

TIER2_PROB = 0.95
TIER3_PROB = 0.10


def load_module_via_exec(path: Path, module_name: str):
    module = types.ModuleType(module_name)
    module.__file__ = str(path)
    sys.modules[module_name] = module
    code = path.read_text(encoding="utf-8")
    exec(compile(code, str(path), "exec"), module.__dict__)
    return module


def stringify_list(value):
    if isinstance(value, list):
        return " | ".join(str(x) for x in value)
    return value


def main():
    if not PROTOTYPE_PATH.exists():
        raise FileNotFoundError(f"Missing probabilistic matcher prototype: {PROTOTYPE_PATH}")

    matcher_mod = load_module_via_exec(PROTOTYPE_PATH, "prob_matcher_runtime_local")

    summaries = []

    for label, path in INPUTS.items():
        if not path.exists():
            raise FileNotFoundError(f"Missing input CSV: {path}")

        df = pd.read_csv(path)
        rows = df.to_dict(orient="records")

        matcher = matcher_mod.prepare_matcher(rows, tier2_prob=TIER2_PROB, tier3_prob=TIER3_PROB)
        preds = pd.DataFrame(matcher.predict_rows(rows))

        rename_map = {}
        for col in preds.columns:
            if col in df.columns:
                rename_map[col] = f"new_{col}"
        preds = preds.rename(columns=rename_map)

        merged = pd.concat([df.reset_index(drop=True), preds.reset_index(drop=True)], axis=1)

        for col in ["reasons", "flags", "new_reasons", "new_flags"]:
            if col in merged.columns:
                merged[col] = merged[col].apply(stringify_list)

        output_csv = OUTPUT_DIR / f"{label}__probabilistic_regenerated.csv"
        merged.to_csv(output_csv, index=False)

        summary = {
            "label": label,
            "input_file": str(path),
            "rows": int(len(merged)),
            "existing_tier_counts": (
                {k: int(v) for k, v in merged["tier"].astype(str).value_counts(dropna=False).to_dict().items()}
                if "tier" in merged.columns else {}
            ),
            "new_tier_counts": (
                {k: int(v) for k, v in merged["new_tier"].astype(str).value_counts(dropna=False).to_dict().items()}
                if "new_tier" in merged.columns else {}
            ),
            "existing_avg_confidence": (
                float(pd.to_numeric(merged["confidence_score"], errors="coerce").fillna(0).mean())
                if "confidence_score" in merged.columns else None
            ),
            "new_avg_confidence": (
                float(pd.to_numeric(merged["new_confidence_score"], errors="coerce").fillna(0).mean())
                if "new_confidence_score" in merged.columns else None
            ),
            "ean_exact_matches_new": (
                int(merged["new_ean_exact_match"].fillna(False).sum())
                if "new_ean_exact_match" in merged.columns else 0
            ),
            "output_csv": str(output_csv),
        }

        if "tier" in merged.columns and "new_tier" in merged.columns:
            changed = merged["tier"].astype(str) != merged["new_tier"].astype(str)
            summary["changed_rows"] = int(changed.sum())

            delta_cols = [c for c in [
                "SupplierTitle", "AmazonTitle", "EAN", "EAN_OnPage", "ASIN",
                "tier", "new_tier",
                "confidence_score", "new_confidence_score",
                "posterior_match_probability"
            ] if c in merged.columns]

            delta = merged.loc[changed, delta_cols].copy()
            delta_csv = OUTPUT_DIR / f"{label}__tier_changes.csv"
            delta.to_csv(delta_csv, index=False)
            summary["tier_changes_csv"] = str(delta_csv)

        summary_json = OUTPUT_DIR / f"{label}__summary.json"
        summary_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        summaries.append(summary)

    master = {
        "notes": "Regenerated by rerunning the initial probabilistic matcher on the newly attached correct full-row analysis files; existing tiers preserved alongside newly assigned tiers.",
        "tier2_prob": TIER2_PROB,
        "tier3_prob": TIER3_PROB,
        "summaries": summaries,
    }
    (OUTPUT_DIR / "run_summary.json").write_text(json.dumps(master, indent=2), encoding="utf-8")
    print(json.dumps(master, indent=2))


if __name__ == "__main__":
    main()
