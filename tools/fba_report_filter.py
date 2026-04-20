#!/usr/bin/env python3
"""
FBA Report Filter & Scoring System
Standalone script - no dependencies on existing workflow modules.
Reads financial report CSVs, classifies rows into confidence tiers,
outputs filtered CSVs and a summary JSON.

Usage:
    python tools/fba_report_filter.py <csv_path> [--output-dir <dir>]
"""

import csv
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from difflib import SequenceMatcher

_USE_LEGACY = os.getenv("FBA_USE_LEGACY_CLASSIFIER", "0") == "1"
if not _USE_LEGACY:
    try:
        from tools.fba_probabilistic_classifier import classify_row_probabilistic, prepare_matcher
    except Exception as _e:
        _USE_LEGACY = True
        print(f"[fba_report_filter] probabilistic import failed ({_e}); using legacy")


def normalize_ean(raw: str) -> str:
    """Clean and normalize an EAN/barcode value."""
    if not raw:
        return ""
    s = str(raw).strip()
    # Handle float notation (e.g. 5033601694236.0)
    if s.endswith(".0"):
        s = s[:-2]
    # Handle scientific notation (e.g. 5.03360169424E+12 from Excel exports)
    if 'e' in s.lower():
        try:
            s = str(int(float(s)))
        except (ValueError, OverflowError):
            pass
    s = re.sub(r"[^0-9]", "", s)
    if len(s) not in (8, 12, 13, 14):
        return ""
    return s


def gtin_checksum_valid(ean: str) -> bool:
    """Validate GTIN checksum for 8/12/13/14 digit barcodes."""
    if not ean or len(ean) not in (8, 12, 13, 14):
        return False
    digits = [int(d) for d in ean]
    check = digits[-1]
    payload = digits[:-1]
    total = 0
    for i, d in enumerate(reversed(payload)):
        weight = 3 if i % 2 == 0 else 1
        total += d * weight
    expected = (10 - (total % 10)) % 10
    return expected == check


def title_similarity(a: str, b: str) -> float:
    """Compute normalized title similarity (0-1)."""
    if not a or not b:
        return 0.0
    a_clean = re.sub(r"[^a-z0-9 ]", "", a.lower())
    b_clean = re.sub(r"[^a-z0-9 ]", "", b.lower())
    return SequenceMatcher(None, a_clean, b_clean).ratio()


def shared_token_count(a: str, b: str) -> int:
    """Count meaningful shared tokens between two titles."""
    if not a or not b:
        return 0
    stop_words = {
        "the", "a", "an", "and", "or", "for", "of", "in", "to", "with",
        "is", "by", "on", "at", "from", "pack", "set", "new", "free",
    }
    a_tokens = set(re.findall(r"[a-z0-9]+", a.lower())) - stop_words
    b_tokens = set(re.findall(r"[a-z0-9]+", b.lower())) - stop_words
    shared = {t for t in a_tokens & b_tokens if len(t) >= 3}
    return len(shared)


def extract_brand(title: str) -> str:
    """Extract likely brand from start of title."""
    if not title:
        return ""
    parts = title.strip().split()
    if len(parts) >= 2:
        return parts[0].lower()
    return title.strip().lower()


def classify_row(row: dict, loose_mode: bool = False) -> dict:
    """
    Classify a single financial report row into a confidence tier.
    Returns dict with: tier, confidence_score, reasons[], flags[]
    """
    if not _USE_LEGACY:
        try:
            res = classify_row_probabilistic(row)
            res.setdefault("title_similarity", round(title_similarity(row.get("SupplierTitle", ""), row.get("AmazonTitle", "")), 3))
            res.setdefault("shared_tokens", shared_token_count(row.get("SupplierTitle", ""), row.get("AmazonTitle", "")))
            return res
        except RuntimeError:
            pass

    supplier_ean = normalize_ean(row.get("EAN", ""))
    amazon_ean = normalize_ean(row.get("EAN_OnPage", ""))
    supplier_title = row.get("SupplierTitle", "")
    amazon_title = row.get("AmazonTitle", "")

    reasons = []
    flags = []
    confidence = 0

    # --- EAN Analysis ---
    ean_exact_match = False
    if supplier_ean and amazon_ean:
        if supplier_ean == amazon_ean:
            supplier_valid = gtin_checksum_valid(supplier_ean)
            amazon_valid = gtin_checksum_valid(amazon_ean)
            if supplier_valid and amazon_valid:
                ean_exact_match = True
                confidence += 50
                reasons.append("Exact EAN match (checksum verified)")
            else:
                confidence += 25
                reasons.append("EAN digits match but checksum invalid")
                flags.append("EAN_CHECKSUM_FAIL")
        else:
            confidence -= 20
            reasons.append(f"EAN mismatch: supplier={supplier_ean} vs amazon={amazon_ean}")
            flags.append("EAN_MISMATCH")
    elif supplier_ean and not amazon_ean:
        reasons.append("Supplier EAN present, Amazon EAN missing")
        flags.append("AMAZON_EAN_MISSING")
    elif not supplier_ean:
        reasons.append("No supplier EAN")
        flags.append("NO_SUPPLIER_EAN")

    # --- Title Similarity ---
    sim = title_similarity(supplier_title, amazon_title)
    shared = shared_token_count(supplier_title, amazon_title)

    if sim >= 0.6 and shared >= 4:
        confidence += 30
        reasons.append(f"Strong title match (sim={sim:.2f}, shared={shared})")
    elif sim >= 0.35 and shared >= 3:
        confidence += 15
        reasons.append(f"Moderate title match (sim={sim:.2f}, shared={shared})")
    elif sim < 0.15 and shared < 2:
        confidence -= 30
        reasons.append(f"Very weak title match (sim={sim:.2f}, shared={shared})")
        flags.append("TITLE_MISMATCH")
    else:
        reasons.append(f"Weak title match (sim={sim:.2f}, shared={shared})")

    # --- Brand Check ---
    # NOTE: First-word brand extraction is a rough heuristic. Works for "Philips X" vs "Prima Y" but not universal. Low weight to limit impact.
    supplier_brand = extract_brand(supplier_title)
    amazon_brand = extract_brand(amazon_title)
    if supplier_brand and amazon_brand and supplier_brand == amazon_brand:
        confidence += 5
        reasons.append(f"Brand match: {supplier_brand}")
    elif supplier_brand and amazon_brand and supplier_brand != amazon_brand:
        confidence -= 5
        flags.append("BRAND_MISMATCH")

    # --- Financial Sanity ---
    try:
        roi = float(row.get("ROI", 0))
        net_profit = float(row.get("NetProfit", 0))
        supplier_price = float(row.get("SupplierPrice_incVAT", 0))
        sell_price = float(row.get("SellingPrice_incVAT", 0))
    except (ValueError, TypeError):
        roi = 0
        net_profit = 0
        supplier_price = 0
        sell_price = 0

    if roi > 1000:
        flags.append("EXTREME_ROI")
        reasons.append(f"Suspiciously high ROI: {roi:.0f}%")
    if sell_price > 0 and supplier_price > 0:
        price_ratio = sell_price / supplier_price
        if price_ratio > 20:
            flags.append("EXTREME_PRICE_RATIO")
            reasons.append(f"Price ratio {price_ratio:.1f}x - likely mismatch")
            confidence -= 15

    if net_profit <= 0:
        flags.append("UNPROFITABLE")

    # --- Category Mismatch Detection ---
    supplier_lower = supplier_title.lower() if supplier_title else ""
    amazon_lower = amazon_title.lower() if amazon_title else ""
    category_keywords = {
        "electronics": ["trimmer", "charger", "battery", "headphone", "speaker", "phone", "tablet", "laptop"],
        "food": ["chocolate", "biscuit", "cereal", "snack", "sweet", "candy"],
        "health": ["cream", "soap", "shampoo", "wash", "lotion", "gel", "wipe"],
        "cleaning": ["bleach", "detergent", "cloth", "mop", "brush"],
        "toys": ["toy", "game", "puzzle", "doll", "figure"],
    }
    supplier_cats = set()
    amazon_cats = set()
    for cat, keywords in category_keywords.items():
        if any(kw in supplier_lower for kw in keywords):
            supplier_cats.add(cat)
        if any(kw in amazon_lower for kw in keywords):
            amazon_cats.add(cat)
    if supplier_cats and amazon_cats and not supplier_cats.intersection(amazon_cats):
        confidence -= 25
        flags.append("CATEGORY_MISMATCH")
        reasons.append(f"Category mismatch: supplier={supplier_cats} vs amazon={amazon_cats}")

    # --- Tier Classification ---
    confidence = max(0, min(100, confidence))

    # EAN match + profitable + no category mismatch -> always T1
    if ean_exact_match and net_profit > 0 and "CATEGORY_MISMATCH" not in flags:
        tier = "TIER_1_VERIFIED"
    # EAN match (unprofitable or category mismatch) -> T2
    elif ean_exact_match:
        tier = "TIER_2_LIKELY"
    # No EAN: high confidence, no flags -> T2 max
    elif confidence >= 40 and "TITLE_MISMATCH" not in flags and "CATEGORY_MISMATCH" not in flags:
        tier = "TIER_2_LIKELY"
    elif confidence >= 15 and net_profit > 0:
        tier = "TIER_3_NEEDS_REVIEW"
    else:
        tier = "TIER_4_REJECTED"

    return {
        "tier": tier,
        "confidence_score": confidence,
        "reasons": reasons,
        "flags": flags,
        "ean_exact_match": ean_exact_match,
        "title_similarity": round(sim, 3),
        "shared_tokens": shared,
    }


def process_report(csv_path: str, output_dir: str = None) -> dict:
    """Process a financial report CSV and produce filtered outputs."""
    csv_path = Path(csv_path)
    if not csv_path.exists():
        print(f"ERROR: File not found: {csv_path}")
        sys.exit(1)

    if output_dir is None:
        output_dir = csv_path.parent / "filtered"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    global _USE_LEGACY

    rows = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        all_rows = []
        for i, row in enumerate(reader, start=2):
            row["_row_id"] = i
            all_rows.append(row)

    use_legacy = _USE_LEGACY
    if not use_legacy:
        try:
            prepare_matcher(all_rows, report_id=str(csv_path.resolve()))
        except Exception as e:
            print(f"[fba_report_filter] matcher fit failed ({e}); using legacy")
            use_legacy = True

    for row in all_rows:
        if use_legacy != _USE_LEGACY:
            original_legacy = _USE_LEGACY
            _USE_LEGACY = use_legacy
            try:
                classification = classify_row(row)
            finally:
                _USE_LEGACY = original_legacy
        else:
            classification = classify_row(row)
        row.update(classification)
        rows.append(row)

    tiers = {
        "TIER_1_A_VERIFIED": [],
        "TIER_1_B_AUDIT_OUT": [],
        "TIER_1_VERIFIED": [],
        "TIER_2_LIKELY": [],
        "TIER_3_NEEDS_REVIEW": [],
        "TIER_4_REJECTED": [],
    }
    for row in rows:
        t = row.get("tier", "TIER_4_REJECTED")
        if t not in tiers:
            tiers[t] = []
        tiers[t].append(row)

    extra_cols = ["_row_id", "tier", "confidence_score", "reasons", "flags",
                  "ean_exact_match", "title_similarity", "shared_tokens", "prob_estimate",
                  "sup_pack", "amz_pack", "pack_bucket"]
    out_fieldnames = fieldnames + extra_cols

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    serializable_rows = []
    for row in rows:
        serializable_row = dict(row)
        serializable_row["reasons"] = " | ".join(serializable_row.get("reasons", []))
        serializable_row["flags"] = " | ".join(serializable_row.get("flags", []))
        serializable_rows.append(serializable_row)

    serializable_by_row_id = {row.get("_row_id"): row for row in serializable_rows}
    for tier_name, tier_rows in tiers.items():
        out_path = output_dir / f"{tier_name.lower()}_{timestamp}.csv"
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=out_fieldnames, extrasaction="ignore")
            writer.writeheader()
            for row in sorted(tier_rows, key=lambda r: r.get("confidence_score", 0), reverse=True):
                writer.writerow(serializable_by_row_id.get(row.get("_row_id"), row))
        print(f"  Wrote {len(tier_rows)} rows to {out_path.name}")

    summary = {
        "source_file": str(csv_path),
        "processed_at": datetime.now().isoformat(),
        "total_rows": len(rows),
        "tier_counts": {k: len(v) for k, v in tiers.items()},
        "tier_percentages": {
            k: round(len(v) / max(len(rows), 1) * 100, 1)
            for k, v in tiers.items()
        },
        "flags_summary": {},
        "avg_confidence_by_tier": {},
    }

    all_flags = {}
    for row in rows:
        for flag in row.get("flags", []):
            all_flags[flag] = all_flags.get(flag, 0) + 1
    summary["flags_summary"] = dict(sorted(all_flags.items(), key=lambda x: x[1], reverse=True))

    for tier_name, tier_rows in tiers.items():
        if tier_rows:
            avg = sum(r.get("confidence_score", 0) for r in tier_rows) / len(tier_rows)
            summary["avg_confidence_by_tier"][tier_name] = round(avg, 1)
        else:
            summary["avg_confidence_by_tier"][tier_name] = 0

    summary_path = output_dir / f"filter_summary_{timestamp}.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"  Summary written to {summary_path.name}")

    return summary


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/fba_report_filter.py <csv_path> [--output-dir <dir>]")
        sys.exit(1)

    csv_file = sys.argv[1]
    out_dir = None
    if "--output-dir" in sys.argv:
        idx = sys.argv.index("--output-dir")
        if idx + 1 < len(sys.argv):
            out_dir = sys.argv[idx + 1]

    print(f"\nFBA Report Filter")
    print(f"Processing: {csv_file}")
    print(f"{'=' * 60}")

    result = process_report(csv_file, out_dir)

    print(f"\n{'=' * 60}")
    print(f"RESULTS:")
    print(f"  Total rows:       {result['total_rows']}")
    for tier, count in result["tier_counts"].items():
        pct = result["tier_percentages"][tier]
        print(f"  {tier}: {count} ({pct}%)")
    print(f"\nTop flags:")
    for flag, count in list(result["flags_summary"].items())[:10]:
        print(f"  {flag}: {count}")
