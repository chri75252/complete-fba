#!/usr/bin/env python3
"""
FBA Tier Classification v2 — Multi-Signal Probabilistic Classifier

Drop-in replacement for classify_row() in tools/fba_report_filter.py.
Uses rapidfuzz token-set matching, TF-IDF-weighted token importance,
probabilistic EAN interpretation, and fuzzy multi-word brand matching
to produce calibrated confidence scores.

Dependencies: rapidfuzz (already installed), numpy (already installed)
Optional: scikit-learn (for TF-IDF; falls back to manual IDF if missing)

Author: Claude Code research output
Date: 2026-04-16
"""

import math
import re
from collections import Counter
from difflib import SequenceMatcher
from typing import Optional

try:
    from rapidfuzz import fuzz as rf_fuzz
    HAS_RAPIDFUZZ = True
except ImportError:
    HAS_RAPIDFUZZ = False

# ---------------------------------------------------------------------------
# Abbreviation / synonym table for product-title normalization
# ---------------------------------------------------------------------------
SYNONYM_MAP = {
    # Units
    "mtr": "metre", "mtrs": "metres", "mts": "metres",
    "5mtr": "5metre", "2mtr": "2metre", "3mtr": "3metre", "10mtr": "10metre",
    "ltr": "litre", "ltrs": "litres",
    "ml": "ml", "cm": "cm", "mm": "mm", "kg": "kg",
    "oz": "oz", "gm": "gram", "gms": "grams",
    "pce": "piece", "pcs": "pieces", "pc": "piece",
    "pk": "pack", "pck": "pack",
    # Number words
    "1": "1", "one": "1", "single": "1",
    "2": "2", "two": "2", "double": "2", "twin": "2", "dual": "2", "pair": "2",
    "3": "3", "three": "3", "triple": "3",
    "4": "4", "four": "4",
    "5": "5", "five": "5",
    "6": "6", "six": "6",
    "8": "8", "eight": "8",
    "10": "10", "ten": "10",
    "12": "12", "twelve": "12",
    # Product terms
    "recharge": "rechargeable", "recharg": "rechargeable",
    "w": "watt", "wt": "watt",
    "led": "led",
    "usb": "usb",
    "hd": "heavy duty", "hvy": "heavy",
    "lge": "large", "lg": "large", "lrg": "large",
    "sm": "small", "sml": "small",
    "med": "medium",
    "asst": "assorted", "asstd": "assorted",
    "blk": "black", "wht": "white", "brn": "brown", "grn": "green",
    "chr": "chrome",
    "ss": "stainless steel",
    "s/s": "stainless steel",
    "gang": "socket",
    "pm": "",  # price-marked — supplier-only, not meaningful for matching
}

STOP_WORDS = frozenset({
    "the", "a", "an", "and", "or", "for", "of", "in", "to", "with",
    "is", "by", "on", "at", "from", "new", "free", "each", "per",
    "size", "type", "style", "range", "quality", "premium", "professional",
    "ideal", "perfect", "great", "best", "super", "ultra", "pro",
})

# Tokens that are too generic to be meaningful in product matching
LOW_VALUE_TOKENS = frozenset({
    "pack", "set", "box", "bag", "piece", "pieces", "count",
    "assorted", "mixed", "various", "multi", "colours", "colors",
})


# ---------------------------------------------------------------------------
# EAN / GTIN utilities
# ---------------------------------------------------------------------------
def normalize_ean(raw: str) -> str:
    """Clean and normalize an EAN/barcode value."""
    if not raw:
        return ""
    s = str(raw).strip()
    if s.endswith(".0"):
        s = s[:-2]
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


def ean_prefix_match(ean_a: str, ean_b: str) -> int:
    """
    Count shared leading digits between two EANs.
    Longer prefix match → higher likelihood of same manufacturer/product family.
    GS1 company prefixes are typically 7-10 digits for 13-digit EANs.
    """
    if not ean_a or not ean_b:
        return 0
    max_len = min(len(ean_a), len(ean_b))
    shared = 0
    for i in range(max_len):
        if ean_a[i] == ean_b[i]:
            shared += 1
        else:
            break
    return shared


# ---------------------------------------------------------------------------
# Title normalization and tokenization
# ---------------------------------------------------------------------------
def normalize_title(title: str) -> str:
    """
    Normalize a product title for matching:
    - lowercase
    - expand abbreviations/synonyms
    - remove punctuation except meaningful separators
    - collapse whitespace
    """
    if not title:
        return ""
    t = title.lower().strip()
    # Remove common noise patterns
    t = re.sub(r'\bpm\b$', '', t)  # price-marked suffix
    t = re.sub(r'[,\-–—/\\()[\]{}]', ' ', t)
    t = re.sub(r"[^a-z0-9 .]", "", t)
    # Split into tokens and apply synonym map
    tokens = t.split()
    normalized = []
    for tok in tokens:
        mapped = SYNONYM_MAP.get(tok, tok)
        if mapped:  # skip empty mappings (like "pm" -> "")
            normalized.append(mapped)
    return " ".join(normalized)


def tokenize(title: str) -> list:
    """Tokenize a normalized title into meaningful tokens."""
    if not title:
        return []
    tokens = re.findall(r"[a-z0-9]+", title.lower())
    return [t for t in tokens if len(t) >= 2 and t not in STOP_WORDS]


def extract_brand_fuzzy(title: str, max_words: int = 3) -> str:
    """
    Extract brand from title — takes up to max_words from the start,
    stopping at common product-type words.
    Returns lowercased brand string.
    """
    if not title:
        return ""
    product_type_words = {
        "led", "usb", "battery", "batteries", "brush", "tape", "cable",
        "fitted", "sheet", "wipes", "spray", "roller", "knife", "lamp",
        "torch", "lantern", "pot", "pan", "bowl", "plate", "cup", "mug",
        "bag", "case", "box", "tray", "rack", "hook", "ring", "ball",
        "toy", "game", "book", "pad", "pen", "pencil", "ruler",
        "inflatable", "rechargeable", "portable", "mini", "large", "small",
        "round", "square", "flat", "heavy", "light", "extra",
        "stainless", "plastic", "glass", "wooden", "metal", "cotton",
        "synthetic", "leather", "vinyl", "rubber", "foam", "gel",
        "assorted", "mixed", "various", "multi", "colour", "color",
        "hanging", "folding", "combination", "digital", "manual",
        "fluorescent", "correction", "sketch",
    }
    parts = title.strip().split()
    brand_parts = []
    for i, word in enumerate(parts[:max_words]):
        w = word.lower().strip(",-()[]")
        if w in product_type_words:
            break
        # Stop at pure numbers (likely size/quantity)
        if re.match(r'^\d+$', w) and i > 0:
            break
        brand_parts.append(w)
    return " ".join(brand_parts) if brand_parts else parts[0].lower() if parts else ""


def brand_similarity(brand_a: str, brand_b: str) -> float:
    """
    Fuzzy brand comparison that handles:
    - "greenshield" vs "green shield" (compound words)
    - "infapower" vs "infapower" (exact)
    - "fit" vs "fit for the job" (prefix match)
    """
    if not brand_a or not brand_b:
        return 0.0
    if brand_a == brand_b:
        return 1.0

    # Try removing spaces and comparing
    a_nospace = brand_a.replace(" ", "")
    b_nospace = brand_b.replace(" ", "")
    if a_nospace == b_nospace:
        return 0.95

    # Check if one contains the other
    if a_nospace.startswith(b_nospace) or b_nospace.startswith(a_nospace):
        return 0.85

    # Fuzzy match
    if HAS_RAPIDFUZZ:
        ratio = rf_fuzz.ratio(a_nospace, b_nospace) / 100.0
    else:
        ratio = SequenceMatcher(None, a_nospace, b_nospace).ratio()

    return ratio


# ---------------------------------------------------------------------------
# Token-level similarity (TF-IDF weighted)
# ---------------------------------------------------------------------------
class TokenWeighter:
    """
    Computes IDF weights for tokens across a corpus of titles.
    Rare tokens (brand names, specific model numbers) get higher weight
    than common tokens (pack, set, assorted).
    """

    def __init__(self):
        self.doc_freq = Counter()
        self.n_docs = 0
        self._fitted = False

    def fit(self, titles: list):
        """Build IDF from a list of title strings."""
        self.doc_freq = Counter()
        self.n_docs = len(titles)
        for title in titles:
            tokens = set(tokenize(normalize_title(title)))
            for tok in tokens:
                self.doc_freq[tok] += 1
        self._fitted = True

    def idf(self, token: str) -> float:
        """Get IDF weight for a token. Higher = rarer = more informative."""
        if not self._fitted or self.n_docs == 0:
            # Fallback: use heuristic weights
            if token in LOW_VALUE_TOKENS:
                return 0.5
            if len(token) >= 6:  # Longer tokens tend to be more specific
                return 2.0
            return 1.0
        df = self.doc_freq.get(token, 0)
        if df == 0:
            return 3.0  # Very rare token — high weight
        return math.log(self.n_docs / df) + 1.0

    def weighted_token_overlap(self, tokens_a: list, tokens_b: list) -> float:
        """
        Compute weighted Jaccard-like overlap between two token sets.
        Returns value in [0, 1].
        """
        set_a = set(tokens_a)
        set_b = set(tokens_b)
        if not set_a or not set_b:
            return 0.0

        intersection = set_a & set_b
        union = set_a | set_b

        if not union:
            return 0.0

        weighted_intersection = sum(self.idf(t) for t in intersection)
        weighted_union = sum(self.idf(t) for t in union)

        if weighted_union == 0:
            return 0.0

        return weighted_intersection / weighted_union


# ---------------------------------------------------------------------------
# Core multi-signal similarity computation
# ---------------------------------------------------------------------------
def compute_title_signals(supplier_title: str, amazon_title: str,
                          weighter: Optional[TokenWeighter] = None) -> dict:
    """
    Compute multiple orthogonal similarity signals between two titles.
    Returns a dict of named signals, each in [0, 1].
    """
    norm_s = normalize_title(supplier_title)
    norm_a = normalize_title(amazon_title)
    tok_s = tokenize(norm_s)
    tok_a = tokenize(norm_a)

    signals = {}

    # Signal 1: rapidfuzz token_set_ratio (handles word reordering + partial overlap)
    if HAS_RAPIDFUZZ:
        signals["token_set_ratio"] = rf_fuzz.token_set_ratio(norm_s, norm_a) / 100.0
        signals["token_sort_ratio"] = rf_fuzz.token_sort_ratio(norm_s, norm_a) / 100.0
        signals["partial_ratio"] = rf_fuzz.partial_ratio(norm_s, norm_a) / 100.0
    else:
        # Fallback to SequenceMatcher
        signals["token_set_ratio"] = SequenceMatcher(None, norm_s, norm_a).ratio()
        signals["token_sort_ratio"] = signals["token_set_ratio"]
        signals["partial_ratio"] = signals["token_set_ratio"]

    # Signal 2: Weighted token overlap (IDF-weighted Jaccard)
    if weighter:
        signals["weighted_overlap"] = weighter.weighted_token_overlap(tok_s, tok_a)
    else:
        # Simple Jaccard
        set_s, set_a = set(tok_s), set(tok_a)
        if set_s | set_a:
            signals["weighted_overlap"] = len(set_s & set_a) / len(set_s | set_a)
        else:
            signals["weighted_overlap"] = 0.0

    # Signal 3: Raw shared token count (still useful as a discrete signal)
    shared = set(tok_s) & set(tok_a) - LOW_VALUE_TOKENS
    signals["shared_meaningful_tokens"] = len(shared)
    signals["shared_token_names"] = sorted(shared)

    # Signal 4: SequenceMatcher ratio on normalized text (backward compat)
    signals["sequence_ratio"] = SequenceMatcher(None, norm_s, norm_a).ratio()

    # Signal 5: Brand similarity
    brand_s = extract_brand_fuzzy(supplier_title)
    brand_a = extract_brand_fuzzy(amazon_title)
    signals["brand_sim"] = brand_similarity(brand_s, brand_a)
    signals["brand_s"] = brand_s
    signals["brand_a"] = brand_a

    return signals


def compute_ean_signals(supplier_ean: str, amazon_ean: str) -> dict:
    """
    Probabilistic EAN interpretation.
    Returns signals about EAN relationship.
    """
    s_ean = normalize_ean(supplier_ean)
    a_ean = normalize_ean(amazon_ean)

    signals = {
        "supplier_ean": s_ean,
        "amazon_ean": a_ean,
        "ean_state": "none",
        "ean_exact_match": False,
        "ean_checksum_valid_s": False,
        "ean_checksum_valid_a": False,
        "ean_prefix_shared": 0,
        "ean_same_manufacturer": False,
    }

    if s_ean:
        signals["ean_checksum_valid_s"] = gtin_checksum_valid(s_ean)
    if a_ean:
        signals["ean_checksum_valid_a"] = gtin_checksum_valid(a_ean)

    if s_ean and a_ean:
        if s_ean == a_ean:
            signals["ean_state"] = "exact_match"
            signals["ean_exact_match"] = True
        else:
            signals["ean_state"] = "mismatch"
            prefix = ean_prefix_match(s_ean, a_ean)
            signals["ean_prefix_shared"] = prefix
            # GS1 company prefix is typically first 7-10 digits
            # Sharing 7+ digits strongly suggests same manufacturer
            signals["ean_same_manufacturer"] = prefix >= 7
    elif s_ean and not a_ean:
        signals["ean_state"] = "amazon_missing"
    elif not s_ean and a_ean:
        signals["ean_state"] = "supplier_missing"
    else:
        signals["ean_state"] = "both_missing"

    return signals


# ---------------------------------------------------------------------------
# Probabilistic confidence scoring
# ---------------------------------------------------------------------------
def compute_confidence(title_signals: dict, ean_signals: dict) -> tuple:
    """
    Combine signals into a single confidence score using a weighted
    logistic-inspired combination.

    Returns: (confidence_score: float 0-100, reasons: list, flags: list)

    Design principles:
    - EAN exact match is strong positive evidence but not required
    - EAN mismatch is NEUTRAL (not punitive) — variants have different EANs
    - EAN same-manufacturer prefix is moderate positive evidence
    - Missing Amazon EAN is explicitly neutral (very common on Amazon)
    - Title similarity is the primary signal when EAN is unavailable
    - Brand match amplifies title evidence; brand mismatch is weak negative
    - Multiple agreeing signals compound (independence assumption)
    """
    reasons = []
    flags = []

    # --- EAN contribution ---
    ean_score = 0.0

    if ean_signals["ean_exact_match"]:
        if ean_signals["ean_checksum_valid_s"] and ean_signals["ean_checksum_valid_a"]:
            ean_score = 0.95  # Near-certain match
            reasons.append("Exact EAN match (checksum verified)")
        else:
            ean_score = 0.75
            reasons.append("EAN digits match (checksum invalid)")
            flags.append("EAN_CHECKSUM_FAIL")

    elif ean_signals["ean_state"] == "mismatch":
        prefix = ean_signals["ean_prefix_shared"]
        if ean_signals["ean_same_manufacturer"]:
            ean_score = 0.15  # Same manufacturer, different product/variant
            reasons.append(f"EAN mismatch but same manufacturer prefix ({prefix} digits shared)")
            flags.append("EAN_VARIANT")
        elif prefix >= 4:
            ean_score = 0.05  # Some prefix overlap
            reasons.append(f"EAN mismatch, partial prefix overlap ({prefix} digits)")
            flags.append("EAN_MISMATCH")
        else:
            ean_score = -0.05  # Very weak negative — different EANs tell us little
            reasons.append(f"EAN mismatch, no prefix overlap")
            flags.append("EAN_MISMATCH")

    elif ean_signals["ean_state"] == "amazon_missing":
        ean_score = 0.0  # Explicitly neutral
        reasons.append("Amazon EAN missing (neutral — common on Amazon listings)")
        flags.append("AMAZON_EAN_MISSING")

    elif ean_signals["ean_state"] == "supplier_missing":
        ean_score = 0.0
        reasons.append("Supplier EAN missing")
        flags.append("NO_SUPPLIER_EAN")

    else:
        ean_score = 0.0
        reasons.append("No EAN data available")
        flags.append("NO_EAN_DATA")

    # --- Title contribution ---
    # Use the best of multiple similarity measures
    tsr = title_signals.get("token_set_ratio", 0)
    tso = title_signals.get("token_sort_ratio", 0)
    pr = title_signals.get("partial_ratio", 0)
    wo = title_signals.get("weighted_overlap", 0)
    sr = title_signals.get("sequence_ratio", 0)
    shared_count = title_signals.get("shared_meaningful_tokens", 0)

    # Composite title score — weighted blend of signals
    # token_set_ratio handles word reordering best; weighted_overlap handles importance
    title_score = (
        0.35 * tsr +
        0.20 * tso +
        0.15 * pr +
        0.20 * wo +
        0.10 * sr
    )

    # Shared token bonus — having 3+ meaningful shared tokens is strong evidence
    if shared_count >= 5:
        title_score = min(1.0, title_score + 0.10)
    elif shared_count >= 3:
        title_score = min(1.0, title_score + 0.05)

    shared_names = title_signals.get("shared_token_names", [])
    if shared_names:
        reasons.append(f"Title match: composite={title_score:.2f} (tsr={tsr:.2f}, wo={wo:.2f}, shared={shared_count}: {', '.join(shared_names[:8])})")
    else:
        reasons.append(f"Title match: composite={title_score:.2f} (tsr={tsr:.2f}, wo={wo:.2f}, shared=0)")

    if title_score < 0.20:
        flags.append("TITLE_MISMATCH")
    elif title_score < 0.40:
        flags.append("TITLE_WEAK")

    # --- Brand contribution ---
    brand_sim = title_signals.get("brand_sim", 0)
    brand_s = title_signals.get("brand_s", "")
    brand_a = title_signals.get("brand_a", "")

    if brand_sim >= 0.90:
        brand_score = 0.15
        reasons.append(f"Brand match: '{brand_s}' ~ '{brand_a}' (sim={brand_sim:.2f})")
    elif brand_sim >= 0.70:
        brand_score = 0.08
        reasons.append(f"Brand likely match: '{brand_s}' ~ '{brand_a}' (sim={brand_sim:.2f})")
    elif brand_sim >= 0.40:
        brand_score = 0.0  # Inconclusive
        reasons.append(f"Brand unclear: '{brand_s}' vs '{brand_a}' (sim={brand_sim:.2f})")
    else:
        brand_score = -0.05  # Mild negative
        reasons.append(f"Brand mismatch: '{brand_s}' vs '{brand_a}' (sim={brand_sim:.2f})")
        flags.append("BRAND_MISMATCH")

    # --- Combined confidence ---
    # The key insight: these signals should compound, not add.
    # High EAN + high title = very confident.
    # No EAN + high title = moderately confident (should be T2/T3, not T4).
    # EAN mismatch + high title = probably variant (should be T3, not T4).

    if ean_signals["ean_exact_match"]:
        # EAN match: title is confirmatory, brand is bonus
        raw_confidence = ean_score + (title_score * 0.05) + (brand_score * 0.5)
    else:
        # No EAN match: title is PRIMARY signal, brand amplifies
        raw_confidence = (title_score * 0.85) + (brand_score * 0.8) + (ean_score * 0.5)

    # Scale to 0-100
    # The raw_confidence ranges roughly from -0.1 to 1.0
    # Map to 0-100 with a sigmoid-like curve that separates the tiers well
    confidence = max(0, min(100, int(raw_confidence * 100)))

    return confidence, reasons, flags


# ---------------------------------------------------------------------------
# Tier assignment
# ---------------------------------------------------------------------------
def assign_tier(confidence: int, ean_signals: dict, flags: list,
                row: dict = None) -> str:
    """
    Assign tier based on confidence and signals.

    Tier semantics:
    - TIER_1_VERIFIED: Confirmed same product (EAN match + title confirms)
    - TIER_2_LIKELY: Probable same product (strong title match, or EAN variant)
    - TIER_3_NEEDS_REVIEW: Possible match, human should verify
    - TIER_4_REJECTED: No plausible match evidence
    """
    has_title_mismatch = "TITLE_MISMATCH" in flags

    # T1: Verified — requires EAN exact match + no red flags
    if ean_signals["ean_exact_match"] and not has_title_mismatch:
        return "TIER_1_VERIFIED"

    # T1 edge case: EAN match but title looks wrong → demote to T2
    if ean_signals["ean_exact_match"] and has_title_mismatch:
        return "TIER_2_LIKELY"

    # T2: Likely — high title confidence without EAN proof
    if confidence >= 55:
        return "TIER_2_LIKELY"

    # T3: Needs review — moderate evidence
    if confidence >= 30:
        return "TIER_3_NEEDS_REVIEW"

    # T3 rescue: EAN same manufacturer + any title signal
    if ean_signals.get("ean_same_manufacturer") and confidence >= 15:
        return "TIER_3_NEEDS_REVIEW"

    # T4: genuinely low confidence
    if confidence < 15:
        return "TIER_4_REJECTED"

    # Everything between 15-30 that didn't match above
    return "TIER_3_NEEDS_REVIEW"


# ---------------------------------------------------------------------------
# Main classify_row() — drop-in replacement
# ---------------------------------------------------------------------------
# Module-level weighter (lazy-initialized)
_global_weighter = None


def init_weighter(all_titles: list):
    """
    Initialize the TF-IDF weighter with all titles from the dataset.
    Call this once before classifying rows for best results.
    Falls back gracefully if not called.
    """
    global _global_weighter
    _global_weighter = TokenWeighter()
    _global_weighter.fit(all_titles)


def classify_row(row: dict, loose_mode: bool = False,
                 weighter: Optional[TokenWeighter] = None) -> dict:
    """
    Classify a single financial report row into a confidence tier.

    Drop-in compatible with the existing classify_row() interface.
    Returns dict with: tier, confidence_score, reasons[], flags[],
                       ean_exact_match, title_similarity, shared_tokens

    Args:
        row: Dict of CSV row data with keys: EAN, EAN_OnPage,
             SupplierTitle, AmazonTitle, ROI, NetProfit, etc.
        loose_mode: When True, uses more permissive tier boundaries.
        weighter: Optional TokenWeighter for IDF-weighted matching.
                  Falls back to heuristic weights if None.
    """
    w = weighter or _global_weighter

    supplier_title = row.get("SupplierTitle", "")
    amazon_title = row.get("AmazonTitle", "")
    supplier_ean_raw = row.get("EAN", "")
    amazon_ean_raw = row.get("EAN_OnPage", "")

    # Compute signals
    ean_signals = compute_ean_signals(supplier_ean_raw, amazon_ean_raw)
    title_signals = compute_title_signals(supplier_title, amazon_title, w)

    # Compute confidence
    confidence, reasons, flags = compute_confidence(title_signals, ean_signals)

    # Loose mode: lower tier boundaries
    if loose_mode:
        # Shift confidence up by ~15 points to cast wider net
        confidence = min(100, confidence + 15)
        reasons.append("(loose_mode: +15 confidence)")

    # Financial sanity flags (informational, not tier-affecting)
    try:
        roi = float(row.get("ROI", 0) or 0)
        net_profit = float(row.get("NetProfit", 0) or 0)
        supplier_price = float(row.get("SupplierPrice_incVAT", 0) or 0)
        sell_price = float(row.get("SellingPrice_incVAT", 0) or 0)
    except (ValueError, TypeError):
        roi = net_profit = supplier_price = sell_price = 0

    if roi > 1000:
        flags.append("EXTREME_ROI")
        reasons.append(f"Suspiciously high ROI: {roi:.0f}%")
    if sell_price > 0 and supplier_price > 0 and sell_price / supplier_price > 20:
        flags.append("EXTREME_PRICE_RATIO")
        reasons.append(f"Price ratio {sell_price/supplier_price:.1f}x")
    if net_profit <= 0:
        flags.append("UNPROFITABLE")

    # Assign tier
    tier = assign_tier(confidence, ean_signals, flags, row)

    # Backward-compatible output fields
    return {
        "tier": tier,
        "confidence_score": confidence,
        "reasons": reasons,
        "flags": flags,
        "ean_exact_match": ean_signals["ean_exact_match"],
        "title_similarity": round(title_signals.get("sequence_ratio", 0), 3),
        "shared_tokens": title_signals.get("shared_meaningful_tokens", 0),
    }


# ---------------------------------------------------------------------------
# Batch processing helper
# ---------------------------------------------------------------------------
def classify_batch(rows: list, loose_mode: bool = False) -> list:
    """
    Classify a batch of rows, initializing TF-IDF weighter from the corpus.
    More accurate than classifying rows individually.
    """
    # Build corpus from both supplier and Amazon titles
    all_titles = []
    for row in rows:
        st = row.get("SupplierTitle", "")
        at = row.get("AmazonTitle", "")
        if st:
            all_titles.append(st)
        if at:
            all_titles.append(at)

    weighter = TokenWeighter()
    weighter.fit(all_titles)

    results = []
    for row in rows:
        result = classify_row(row, loose_mode=loose_mode, weighter=weighter)
        results.append(result)

    return results


# ---------------------------------------------------------------------------
# CLI entry point for testing
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import csv
    import sys

    if len(sys.argv) < 2:
        print("Usage: python tier_classifier_v2.py <csv_path>")
        sys.exit(1)

    csv_path = sys.argv[1]
    print(f"Processing: {csv_path}")

    rows = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    # Classify batch (with TF-IDF)
    results = classify_batch(rows)

    # Tier distribution
    tiers = {}
    for i, result in enumerate(results):
        tier = result["tier"]
        tiers[tier] = tiers.get(tier, 0) + 1
        rows[i].update(result)

    total = len(rows)
    print(f"\nTotal rows: {total}")
    for t in ["TIER_1_VERIFIED", "TIER_2_LIKELY", "TIER_3_NEEDS_REVIEW", "TIER_4_REJECTED"]:
        c = tiers.get(t, 0)
        print(f"  {t}: {c} ({c*100/total:.1f}%)")

    # Show some reclassified examples
    print("\n=== Sample reclassifications ===")
    shown = 0
    for row in rows:
        old_tier = row.get("tier_original", row.get("tier", ""))
        if "tier" in row and shown < 10:
            if row["confidence_score"] > 0:
                st = row.get("SupplierTitle", "")[:55]
                at = row.get("AmazonTitle", "")[:55]
                print(f"  {row['tier']} (conf={row['confidence_score']}) | S: {st}")
                print(f"    A: {at}")
                print(f"    Reasons: {' | '.join(row['reasons'][:3])}")
                print()
                shown += 1
