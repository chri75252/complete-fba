#!/usr/bin/env python3
"""
Probabilistic FBA pair matcher prototype.

Core idea
---------
Replace additive points with a calibrated posterior probability:
    P(match | evidence)

Evidence combines:
- exact / missing / mismatched GTIN state
- lexical similarity from title TF-IDF (word + character n-grams)
- attribute consistency (numbers, units, pack count)
- soft surface cues (prefix token agreement, shared rare tokens)

This module supports batch fitting on one report at a time, which is the
recommended integration path. A literal row-only drop-in without any report-level
context is possible, but weaker, because posterior calibration benefits from
the empirical distribution of one report/supplier.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any, Iterable, Optional

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


STOP_WORDS = {
    "the", "a", "an", "and", "or", "for", "of", "in", "to", "with", "is", "by",
    "on", "at", "from", "pack", "set", "new", "free", "x", "pcs", "pc"
}
SIZE_WORDS = {"single", "double", "king", "queen", "small", "medium", "large", "xl", "xxl"}
COLOR_WORDS = {
    "black", "white", "grey", "gray", "blue", "red", "green", "pink", "purple",
    "brown", "fawn", "cement", "silver", "gold", "copper", "yellow", "orange", "clear"
}


def normalize_ean(raw: Any) -> str:
    if raw is None or (isinstance(raw, float) and math.isnan(raw)):
        return ""
    s = str(raw).strip()
    if not s:
        return ""
    if s.endswith(".0"):
        s = s[:-2]
    if "e" in s.lower():
        try:
            s = str(int(float(s)))
        except (ValueError, OverflowError):
            pass
    s = re.sub(r"[^0-9]", "", s)
    return s if len(s) in (8, 12, 13, 14) else ""


def gtin_checksum_valid(ean: str) -> bool:
    if not ean or len(ean) not in (8, 12, 13, 14):
        return False
    digits = [int(d) for d in ean]
    check = digits[-1]
    payload = digits[:-1]
    total = 0
    for i, d in enumerate(reversed(payload)):
        total += d * (3 if i % 2 == 0 else 1)
    expected = (10 - (total % 10)) % 10
    return expected == check


def clean_text(value: Any) -> str:
    s = "" if value is None or (isinstance(value, float) and math.isnan(value)) else str(value).lower()
    s = s.replace("×", "x").replace("‑", "-").replace("–", "-").replace("—", "-")
    s = re.sub(r"[^a-z0-9\.\-\+ ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def token_set(value: Any) -> set[str]:
    toks = re.findall(r"[a-z0-9]+", clean_text(value))
    return {t for t in toks if t not in STOP_WORDS}


def first_alpha_token(value: Any) -> str:
    for tok in token_set(value):
        if not tok.isdigit():
            return tok
    return ""


def numeric_tokens(value: Any) -> set[str]:
    return set(re.findall(r"[a-z]*\d+[a-z\d]*", clean_text(value)))


def extract_pack(value: Any) -> Optional[int]:
    s = clean_text(value)
    patterns = [
        r"pack of (\d+)",
        r"(\d+)\s*pack\b",
        r"(\d+)\s*pk\b",
        r"(\d+)\s*pcs?\b",
        r"set of (\d+)",
        r"\b(\d+)x\b",
        r"\bx(\d+)\b",
    ]
    for pattern in patterns:
        m = re.search(pattern, s)
        if m:
            return int(m.group(1))
    return None


def extract_measurements(value: Any) -> dict[str, list[float]]:
    s = clean_text(value)
    out: dict[str, list[float]] = {}
    for m in re.finditer(r"(\d+(?:\.\d+)?)\s*(ml|l|cl|ltr|litre|litres|g|kg|mg|cm|mm|m|inch|in|w|kw|v|mah|hz)\b", s):
        num = float(m.group(1))
        unit = m.group(2)
        if unit in {"ltr", "litre", "litres"}:
            unit = "l"
        if unit == "in":
            unit = "inch"
        out.setdefault(unit, []).append(num)
    return out


def best_measurement_closeness(ma: dict[str, list[float]], mb: dict[str, list[float]]) -> float:
    best = 0.0
    for unit in set(ma) & set(mb):
        for a in ma[unit]:
            for b in mb[unit]:
                closeness = min(a, b) / max(a, b)
                best = max(best, closeness)
    return best


@dataclass
class Thresholds:
    tier2_prob: float = 0.95
    tier3_prob: float = 0.10


class ProbabilisticPairMatcher:
    def __init__(self, thresholds: Thresholds | None = None) -> None:
        self.thresholds = thresholds or Thresholds()
        self.word_vectorizer: Optional[TfidfVectorizer] = None
        self.char_vectorizer: Optional[TfidfVectorizer] = None
        self.model: Optional[LogisticRegression] = None
        self._fitted = False

    def _feature_frame(self, df: pd.DataFrame, fit_vectorizers: bool) -> pd.DataFrame:
        supplier_titles = df["SupplierTitle"].fillna("").astype(str).tolist()
        amazon_titles = df["AmazonTitle"].fillna("").astype(str).tolist()

        if fit_vectorizers:
            self.word_vectorizer = TfidfVectorizer(analyzer="word", ngram_range=(1, 2), min_df=2)
            self.char_vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2)
            word_all = self.word_vectorizer.fit_transform(supplier_titles + amazon_titles)
            char_all = self.char_vectorizer.fit_transform([clean_text(x) for x in supplier_titles + amazon_titles])
        else:
            assert self.word_vectorizer is not None and self.char_vectorizer is not None
            word_all = self.word_vectorizer.transform(supplier_titles + amazon_titles)
            char_all = self.char_vectorizer.transform([clean_text(x) for x in supplier_titles + amazon_titles])

        n = len(df)
        supplier_word = word_all[:n]
        amazon_word = word_all[n:]
        supplier_char = char_all[:n]
        amazon_char = char_all[n:]
        word_cos = np.asarray(supplier_word.multiply(amazon_word).sum(axis=1)).ravel()
        char_cos = np.asarray(supplier_char.multiply(amazon_char).sum(axis=1)).ravel()

        rows: list[list[float]] = []
        for i, (supplier_title, amazon_title) in enumerate(zip(supplier_titles, amazon_titles)):
            sup_tokens = token_set(supplier_title)
            amz_tokens = token_set(amazon_title)
            shared = sup_tokens & amz_tokens
            union = max(1, len(sup_tokens | amz_tokens))
            overlap = len(shared) / max(1, min(len(sup_tokens), len(amz_tokens)))
            jaccard = len(shared) / union
            seq = SequenceMatcher(None, clean_text(supplier_title), clean_text(amazon_title)).ratio()

            prefix_same = int(first_alpha_token(supplier_title) == first_alpha_token(amazon_title) != "")
            num_overlap = len(numeric_tokens(supplier_title) & numeric_tokens(amazon_title))

            meas = best_measurement_closeness(
                extract_measurements(supplier_title),
                extract_measurements(amazon_title),
            )

            pack_a = extract_pack(supplier_title)
            pack_b = extract_pack(amazon_title)
            if pack_a is not None and pack_b is not None:
                pack_ratio = min(pack_a, pack_b) / max(pack_a, pack_b)
                pack_conflict = int(pack_a != pack_b)
            else:
                pack_ratio = 0.0
                pack_conflict = 0

            lower_a = clean_text(supplier_title)
            lower_b = clean_text(amazon_title)
            size_overlap = int(any(word in lower_a and word in lower_b for word in SIZE_WORDS))
            color_overlap = int(any(word in lower_a and word in lower_b for word in COLOR_WORDS))

            supplier_ean = normalize_ean(df.iloc[i].get("EAN"))
            amazon_ean = normalize_ean(df.iloc[i].get("EAN_OnPage"))
            ean_exact = int(supplier_ean != "" and supplier_ean == amazon_ean)
            ean_both_present = int(supplier_ean != "" and amazon_ean != "")
            ean_missing_amz = int(supplier_ean != "" and amazon_ean == "")
            ean_mismatch = int(supplier_ean != "" and amazon_ean != "" and supplier_ean != amazon_ean)

            rows.append([
                seq,
                float(word_cos[i]),
                float(char_cos[i]),
                jaccard,
                overlap,
                len(shared),
                prefix_same,
                num_overlap,
                meas,
                pack_ratio,
                pack_conflict,
                size_overlap,
                color_overlap,
                ean_exact,
                ean_both_present,
                ean_missing_amz,
                ean_mismatch,
            ])

        return pd.DataFrame(rows, columns=[
            "seq", "word_cos", "char_cos", "jaccard", "overlap", "shared_tokens",
            "prefix_same", "num_overlap", "meas_closeness", "pack_ratio",
            "pack_conflict", "size_overlap", "color_overlap", "ean_exact",
            "ean_both_present", "ean_missing_amz", "ean_mismatch"
        ])

    def _weak_labels(self, feats: pd.DataFrame) -> pd.Series:
        y = pd.Series([np.nan] * len(feats))
        pos = feats["ean_exact"].astype(bool)

        # Silver positives: strong semantic evidence despite missing/different GTIN.
        silver_pos = (
            ((feats["prefix_same"] == 1) & (feats["char_cos"] > 0.45) & (feats["shared_tokens"] >= 3)) |
            ((feats["prefix_same"] == 1) & (feats["shared_tokens"] >= 4) & (feats["seq"] > 0.28)) |
            ((feats["ean_mismatch"] == 1) & (feats["char_cos"] > 0.50) & (feats["shared_tokens"] >= 4))
        ) & ~pos

        # Clean negatives only. Avoid using ambiguous pairs as negatives.
        neg = (
            (feats["seq"] < 0.18) &
            (feats["char_cos"] < 0.15) &
            (feats["jaccard"] < 0.12) &
            ((feats["prefix_same"] == 0) | (feats["shared_tokens"] <= 1))
        )
        neg = neg | (
            (feats["ean_mismatch"] == 1) &
            (feats["seq"] < 0.25) &
            (feats["char_cos"] < 0.20) &
            (feats["shared_tokens"] < 2)
        )

        y[pos | silver_pos] = 1
        y[neg & ~(pos | silver_pos)] = 0
        return y

    def fit(self, rows: Iterable[dict[str, Any]] | pd.DataFrame) -> "ProbabilisticPairMatcher":
        df = pd.DataFrame(list(rows)) if not isinstance(rows, pd.DataFrame) else rows.copy()
        feats = self._feature_frame(df, fit_vectorizers=True)
        labels = self._weak_labels(feats)
        train_mask = labels.notna()
        self.model = LogisticRegression(max_iter=3000, class_weight="balanced")
        self.model.fit(feats.loc[train_mask], labels.loc[train_mask].astype(int))
        self._fitted = True
        return self

    def predict_rows(self, rows: Iterable[dict[str, Any]] | pd.DataFrame) -> list[dict[str, Any]]:
        if not self._fitted or self.model is None:
            raise RuntimeError("Matcher must be fitted before prediction")

        df = pd.DataFrame(list(rows)) if not isinstance(rows, pd.DataFrame) else rows.copy()
        feats = self._feature_frame(df, fit_vectorizers=False)
        probs = self.model.predict_proba(feats)[:, 1]

        results: list[dict[str, Any]] = []
        for idx, row in df.iterrows():
            results.append(self._format_prediction(row.to_dict(), feats.iloc[idx], float(probs[idx])))
        return results

    def _format_prediction(self, row: dict[str, Any], feat_row: pd.Series, prob: float) -> dict[str, Any]:
        supplier_ean = normalize_ean(row.get("EAN"))
        amazon_ean = normalize_ean(row.get("EAN_OnPage"))
        exact_ean = supplier_ean != "" and supplier_ean == amazon_ean and gtin_checksum_valid(supplier_ean) and gtin_checksum_valid(amazon_ean)

        reasons: list[str] = []
        flags: list[str] = []

        if exact_ean:
            reasons.append("Exact GTIN/EAN match with valid checksum")
        elif supplier_ean and amazon_ean and supplier_ean != amazon_ean:
            flags.append("EAN_MISMATCH")
            reasons.append("Different GTINs; treat as ambiguous evidence, not auto-rejection")
        elif supplier_ean and not amazon_ean:
            flags.append("AMAZON_EAN_MISSING")
            reasons.append("Supplier GTIN present, Amazon GTIN missing")

        reasons.append(f"Posterior match probability={prob:.3f}")
        reasons.append(f"Char TF-IDF cosine={feat_row['char_cos']:.3f}")
        reasons.append(f"Word TF-IDF cosine={feat_row['word_cos']:.3f}")
        reasons.append(f"Shared tokens={int(feat_row['shared_tokens'])}")
        if feat_row["pack_conflict"]:
            reasons.append("Pack-count difference detected")
        if feat_row["meas_closeness"] > 0:
            reasons.append(f"Measurement closeness={feat_row['meas_closeness']:.3f}")

        if exact_ean:
            tier = "TIER_1_VERIFIED"
        elif prob >= self.thresholds.tier2_prob:
            tier = "TIER_2_LIKELY"
        elif prob >= self.thresholds.tier3_prob:
            tier = "TIER_3_NEEDS_REVIEW"
        else:
            tier = "TIER_4_REJECTED"

        return {
            "tier": tier,
            "confidence_score": round(prob * 100, 1),
            "posterior_match_probability": round(prob, 6),
            "reasons": reasons,
            "flags": flags,
            "ean_exact_match": exact_ean,
            "title_similarity": round(float(feat_row["seq"]), 3),
            "shared_tokens": int(feat_row["shared_tokens"]),
        }


# Optional row-wise compatibility wrapper.
# Best results require one report-level fit, then passing the matcher in.
_GLOBAL_MATCHER: Optional[ProbabilisticPairMatcher] = None


def prepare_matcher(rows: Iterable[dict[str, Any]] | pd.DataFrame,
                    tier2_prob: float = 0.95,
                    tier3_prob: float = 0.10) -> ProbabilisticPairMatcher:
    global _GLOBAL_MATCHER
    matcher = ProbabilisticPairMatcher(Thresholds(tier2_prob=tier2_prob, tier3_prob=tier3_prob))
    matcher.fit(rows)
    _GLOBAL_MATCHER = matcher
    return matcher


def classify_row(row: dict[str, Any], loose_mode: bool = False,
                 matcher: Optional[ProbabilisticPairMatcher] = None) -> dict[str, Any]:
    # loose_mode intentionally ignored: the redesign is probabilistic, not threshold-relaxation.
    active_matcher = matcher or _GLOBAL_MATCHER
    if active_matcher is None:
        raise RuntimeError(
            "No matcher prepared. Call prepare_matcher(rows) once per report, "
            "then classify_row(row, matcher=matcher)."
        )
    return active_matcher.predict_rows([row])[0]
