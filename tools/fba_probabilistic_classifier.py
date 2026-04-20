from __future__ import annotations

import os
import threading
from typing import Any, Dict, List, Optional

import pandas as pd

from tools._pack_extraction import extract_pack
from tools._probabilistic_matcher_core import ProbabilisticPairMatcher, Thresholds


_DEFAULT_T2_PROB = float(os.getenv("FBA_TIER2_PROB", "0.95"))
_DEFAULT_T3_PROB = float(os.getenv("FBA_TIER3_PROB", "0.10"))

_matchers: Dict[str, ProbabilisticPairMatcher] = {}
_matchers_lock = threading.Lock()
_current_report = threading.local()


def prepare_matcher(report_rows: List[Dict[str, Any]], report_id: str) -> None:
    with _matchers_lock:
        if report_id not in _matchers:
            matcher = ProbabilisticPairMatcher(
                Thresholds(tier2_prob=_DEFAULT_T2_PROB, tier3_prob=_DEFAULT_T3_PROB)
            )
            matcher.fit(pd.DataFrame(report_rows))
            _matchers[report_id] = matcher
    _current_report.id = report_id


def reset_matcher(report_id: Optional[str] = None) -> None:
    with _matchers_lock:
        if report_id is None:
            _matchers.clear()
        else:
            _matchers.pop(report_id, None)
    current_id = getattr(_current_report, "id", None)
    if report_id is None or current_id == report_id:
        if hasattr(_current_report, "id"):
            delattr(_current_report, "id")


def _category_sets(supplier_title: str, amazon_title: str) -> tuple[set[str], set[str]]:
    category_keywords = {
        "electronics": ["trimmer", "charger", "battery", "headphone", "speaker", "phone", "tablet", "laptop"],
        "food": ["chocolate", "biscuit", "cereal", "snack", "sweet", "candy"],
        "health": ["cream", "soap", "shampoo", "wash", "lotion", "gel", "wipe"],
        "cleaning": ["bleach", "detergent", "cloth", "mop", "brush"],
        "toys": ["toy", "game", "puzzle", "doll", "figure"],
    }
    supplier_lower = supplier_title.lower() if supplier_title else ""
    amazon_lower = amazon_title.lower() if amazon_title else ""
    supplier_cats: set[str] = set()
    amazon_cats: set[str] = set()
    for cat, keywords in category_keywords.items():
        if any(kw in supplier_lower for kw in keywords):
            supplier_cats.add(cat)
        if any(kw in amazon_lower for kw in keywords):
            amazon_cats.add(cat)
    return supplier_cats, amazon_cats


def classify_row_probabilistic(row: Dict[str, Any]) -> Dict[str, Any]:
    report_id = getattr(_current_report, "id", None)
    matcher = _matchers.get(report_id) if report_id else None
    if matcher is None:
        raise RuntimeError("prepare_matcher() must be called before classify_row_probabilistic()")

    base_result = matcher.predict_rows([row])[0]
    prob_estimate = float(base_result.get("posterior_match_probability", 0.0))
    reasons: List[str] = list(base_result.get("reasons", []))
    flags: List[str] = list(base_result.get("flags", []))

    supplier_title = row.get("SupplierTitle", "") or ""
    amazon_title = row.get("AmazonTitle", "") or ""
    supplier_ean = str(row.get("EAN", "") or "").strip()
    amazon_ean = str(row.get("EAN_OnPage", "") or "").strip()

    sup_pack = extract_pack(supplier_title)
    amz_pack = extract_pack(amazon_title)
    if sup_pack is not None and amz_pack is not None:
        pack_bucket = "BOTH_EQUAL" if sup_pack == amz_pack else "BOTH_DIFFERENT"
    elif sup_pack is not None:
        pack_bucket = "ONLY_SUP"
    elif amz_pack is not None:
        pack_bucket = "ONLY_AMZ"
    else:
        pack_bucket = "NEITHER"

    try:
        roi = float(row.get("ROI", 0) or 0)
        net_profit = float(row.get("NetProfit", 0) or 0)
        supplier_price = float(row.get("SupplierPrice_incVAT", 0) or 0)
        sell_price = float(row.get("SellingPrice_incVAT", 0) or 0)
    except (TypeError, ValueError):
        roi = net_profit = supplier_price = sell_price = 0.0

    if roi > 1000 and "EXTREME_ROI" not in flags:
        flags.append("EXTREME_ROI")
        reasons.append(f"Suspiciously high ROI: {roi:.0f}%")
    if sell_price > 0 and supplier_price > 0 and (sell_price / supplier_price) > 20:
        if "EXTREME_PRICE_RATIO" not in flags:
            flags.append("EXTREME_PRICE_RATIO")
            reasons.append(f"Price ratio {sell_price / supplier_price:.1f}x")
    if net_profit <= 0 and "UNPROFITABLE" not in flags:
        flags.append("UNPROFITABLE")

    supplier_cats, amazon_cats = _category_sets(supplier_title, amazon_title)
    if supplier_cats and amazon_cats and not supplier_cats.intersection(amazon_cats):
        if "CATEGORY_MISMATCH" not in flags:
            flags.append("CATEGORY_MISMATCH")
            reasons.append(f"Category mismatch: supplier={supplier_cats} vs amazon={amazon_cats}")

    supplier_brand = supplier_title.strip().split()[0].lower() if supplier_title.strip() else ""
    amazon_brand = amazon_title.strip().split()[0].lower() if amazon_title.strip() else ""
    if supplier_brand and amazon_brand and supplier_brand != amazon_brand and "BRAND_MISMATCH" not in flags:
        flags.append("BRAND_MISMATCH")

    from tools.fba_report_filter import gtin_checksum_valid, normalize_ean, title_similarity as _sim

    nsup = normalize_ean(supplier_ean)
    namz = normalize_ean(amazon_ean)
    ean_exact_match = bool(
        nsup and namz and nsup == namz and gtin_checksum_valid(nsup) and gtin_checksum_valid(namz)
    )
    sim = _sim(supplier_title, amazon_title)

    if ean_exact_match:
        if sim < 0.15 and "BRAND_MISMATCH" in flags and "SUSPICIOUS_TITLE_MISMATCH" not in flags:
            flags.append("SUSPICIOUS_TITLE_MISMATCH")
            reasons.append(f"EAN match but titles very dissimilar (sim={sim:.2f}) — manual check advised")

        if pack_bucket == "BOTH_EQUAL":
            tier = "TIER_1_A_VERIFIED"
            reasons.append("EAN match + pack sizes equal")
        elif pack_bucket == "BOTH_DIFFERENT":
            tier = "TIER_1_B_AUDIT_OUT"
            reasons.append(f"EAN match but pack differs (sup={sup_pack}, amz={amz_pack}) — audit NetProfit")
        elif pack_bucket in ("ONLY_SUP", "ONLY_AMZ"):
            tier = "TIER_1_B_AUDIT_OUT"
            reasons.append(f"EAN match, pack visible on one side only ({pack_bucket})")
        else:
            tier = "TIER_1_A_VERIFIED"
            reasons.append("EAN match, no pack markers in either title (assumed single-unit)")
        return {
            "tier": tier,
            "confidence_score": int(round(prob_estimate * 100)),
            "prob_estimate": round(prob_estimate, 4),
            "reasons": reasons,
            "flags": flags,
            "ean_exact_match": True,
            "title_similarity": round(base_result.get("title_similarity", sim), 3),
            "shared_tokens": int(base_result.get("shared_tokens", 0)),
            "sup_pack": sup_pack,
            "amz_pack": amz_pack,
            "pack_bucket": pack_bucket,
        }

    if prob_estimate >= _DEFAULT_T2_PROB:
        tier = "TIER_2_LIKELY"
    elif prob_estimate >= _DEFAULT_T3_PROB:
        tier = "TIER_3_NEEDS_REVIEW"
    else:
        tier = "TIER_4_REJECTED"

    if tier == "TIER_2_LIKELY" and "BRAND_MISMATCH" in flags:
        tier = "TIER_3_NEEDS_REVIEW"
        reasons.append("Demoted T2→T3: brand mismatch on non-EAN match")
    if "CATEGORY_MISMATCH" in flags and tier in ("TIER_2_LIKELY", "TIER_3_NEEDS_REVIEW"):
        tier = "TIER_4_REJECTED"
        reasons.append("Rejected: category mismatch")
    if "EXTREME_PRICE_RATIO" in flags and tier == "TIER_2_LIKELY":
        tier = "TIER_3_NEEDS_REVIEW"

    return {
        "tier": tier,
        "confidence_score": int(round(prob_estimate * 100)),
        "prob_estimate": round(prob_estimate, 4),
        "reasons": reasons,
        "flags": flags,
        "ean_exact_match": False,
        "title_similarity": round(base_result.get("title_similarity", sim), 3),
        "shared_tokens": int(base_result.get("shared_tokens", 0)),
        "sup_pack": sup_pack,
        "amz_pack": amz_pack,
        "pack_bucket": pack_bucket,
    }
