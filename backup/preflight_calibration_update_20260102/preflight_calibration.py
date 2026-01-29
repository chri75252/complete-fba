"""
Pre-flight calibration for FBA financial report CSVs.

Goal: read the first N rows of a supplier financial report and infer:
- pack quantity patterns (explicit units, trailing qty, leading multipliers, dimensions)
- which sales column to use
- whether brand tends to be at the start of SupplierTitle

Outputs a Python snippet the analyst can paste into a downstream script.
"""

from __future__ import annotations

import argparse
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd

logger = logging.getLogger(__name__)


DIMENSION_UNITS_BASE = [
    "cm",
    "mm",
    "ml",
    "ltr",
    "l",
    "kg",
    "g",
    "oz",
    "inch",
    "in",
    "ft",
    "m",
]

DEFAULT_DIMENSION_SHIELD_KEYWORDS = ["cm", "mm", "ml", "ltr", "kg", "g", "oz", "inch"]

DEFAULT_EXPLICIT_UNITS = ["pce", "pcs", "pk", "pack", "unit"]


_LEADING_MULTIPLIER_RE = re.compile(r"^\s*(\d{1,4})\s*[x×]\s+\S+", re.IGNORECASE)
_TRAILING_NUMBER_RE = re.compile(r"(?<!\w)(\d{1,4})\s*$")
_EXPLICIT_UNIT_TOKEN_RE = re.compile(
    r"\b(pcs?|pce|pc|pk|pack|unit|units|ct|count|ea|each)\b", re.IGNORECASE
)
_EXPLICIT_UNIT_QTY_RE = re.compile(
    r"\b(\d{1,4})\s*(pcs?|pce|pc|pk|pack|unit|units|ct|count|ea|each)\b", re.IGNORECASE
)
_PACK_OF_QTY_RE = re.compile(r"\b(pack\s*of|set\s*of)\s*(\d{1,4})\b", re.IGNORECASE)

_DIMENSION_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*(cm|mm|ml|l|ltr|litre|liter|kg|g|oz|inch|in|ft|m)\b", re.IGNORECASE
)
_DIMENSION_X_RE = re.compile(
    r"\b\d+(?:\.\d+)?\s*[x×]\s*\d+(?:\.\d+)?(?:\s*[x×]\s*\d+(?:\.\d+)?)?\s*"
    r"(cm|mm|m|inch|in|ft)\b",
    re.IGNORECASE,
)

_STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "for",
    "with",
    "of",
    "to",
    "in",
    "on",
    "at",
    "new",
    "set",
    "pack",
}


@dataclass(frozen=True)
class CalibrationResult:
    explicit_units: list[str]
    allow_trailing_number_as_qty: bool
    leading_multiplier_check: bool
    dimension_shield_keywords: list[str]
    brand_position: str  # "start" | "mixed"
    sales_column: str
    warnings: list[str]


def _safe_str(x: object) -> str:
    if x is None:
        return ""
    if pd.isna(x):
        return ""
    return str(x).strip()


def _iter_titles(df: pd.DataFrame, col: str) -> Iterable[str]:
    if col not in df.columns:
        return []
    return (_safe_str(v) for v in df[col].tolist())


def _detect_sales_column(columns: Iterable[str]) -> str:
    cols = list(columns)
    preferred = ["sales_numeric", "bought_in_past_month", "Sales"]
    for c in preferred:
        if c in cols:
            return c

    # Heuristic fallback: first column containing 'sales' or 'bought'
    for c in cols:
        cl = c.lower()
        if "sales" in cl or "bought" in cl:
            return c

    return "sales_numeric"


def _extract_observed_explicit_units(titles: Iterable[str]) -> list[str]:
    found: set[str] = set()
    for t in titles:
        for m in _EXPLICIT_UNIT_TOKEN_RE.finditer(t):
            unit = m.group(1).lower()
            # normalize plurals
            if unit == "pieces":
                unit = "pcs"
            elif unit == "piece":
                unit = "pcs"
            elif unit == "units":
                unit = "unit"
            found.add(unit)
    # Put common units first; then any additional found.
    ordered: list[str] = []
    for u in DEFAULT_EXPLICIT_UNITS:
        if u in found:
            ordered.append(u)
            found.remove(u)
    ordered.extend(sorted(found))
    return ordered if ordered else DEFAULT_EXPLICIT_UNITS.copy()


def _detect_leading_multiplier_common(titles: list[str]) -> bool:
    if not titles:
        return False
    hits = sum(1 for t in titles if _LEADING_MULTIPLIER_RE.search(t))
    return (hits / len(titles)) >= 0.10


def _is_dimension_like_token(token: str) -> bool:
    token = token.strip().lower()
    if not token:
        return False
    if token in DIMENSION_UNITS_BASE:
        return True
    if _DIMENSION_RE.search(token):
        return True
    return False


def _detect_trailing_number_as_qty_common(titles: list[str]) -> tuple[bool, list[tuple[int, str]]]:
    """
    Returns:
      - allow_trailing_number_as_qty: bool (common enough and plausible)
      - suspicious_rows: list of (row_index_1_based, title) for warnings
    """
    if not titles:
        return False, []

    plausible = 0
    total = 0
    suspicious: list[tuple[int, str]] = []

    for i, raw in enumerate(titles, start=1):
        t = raw.strip()
        if not t:
            continue
        total += 1
        m = _TRAILING_NUMBER_RE.search(t)
        if not m:
            continue

        qty = int(m.group(1))
        if qty <= 1:
            continue

        # Inspect the preceding token; if it looks like a unit/dimension, do NOT treat as qty.
        prefix = t[: m.start(1)].strip()
        prev_token = prefix.split()[-1].strip("()[]{}.,;:/\\-") if prefix.split() else ""
        if _is_dimension_like_token(prev_token):
            continue

        # Likely model numbers / codes: very large trailing numbers or immediately preceded by 'no'/'model'
        lower = t.lower()
        if qty > 500 or re.search(r"\b(no\.?|model|ref|item|code)\s*$", prefix.lower()):
            suspicious.append((i, t))
            continue

        plausible += 1

    allow = (plausible / max(total, 1)) >= 0.15
    return allow, suspicious


def _detect_dimension_keywords(titles: Iterable[str]) -> list[str]:
    found: set[str] = set()
    for t in titles:
        if _DIMENSION_X_RE.search(t):
            found.add("x")  # marker for NxM style dimensions
        for m in _DIMENSION_RE.finditer(t):
            unit = m.group(2).lower()
            # normalize unit variants
            if unit in ("litre", "liter"):
                unit = "ltr"
            found.add(unit)

    ordered: list[str] = []
    for u in DEFAULT_DIMENSION_SHIELD_KEYWORDS:
        if u in found:
            ordered.append(u)
            found.remove(u)
    # Keep 'l' only if explicitly present; it can be noisy (e.g. 'xl' styles).
    if "l" in found:
        ordered.append("l")
        found.remove("l")
    ordered.extend(sorted(found))
    return ordered if ordered else DEFAULT_DIMENSION_SHIELD_KEYWORDS.copy()


def _detect_brand_position(supplier_titles: list[str]) -> str:
    """
    Heuristic: if a clear first-token "brand" exists for most rows, label 'start'.
    Otherwise, 'mixed'.
    """
    if not supplier_titles:
        return "mixed"

    brandish = 0
    total = 0
    for t in supplier_titles:
        t = t.strip()
        if not t:
            continue
        total += 1
        first = re.split(r"\s+", t, maxsplit=1)[0].strip("()[]{}.,;:/\\-")
        if not first or first.lower() in _STOPWORDS:
            continue
        if any(ch.isdigit() for ch in first):
            continue
        if len(first) < 3:
            continue
        # Brands in these files often appear as ALLCAPS tokens (e.g., AMTECH, ROLSON).
        if first.isupper():
            brandish += 1
        else:
            # Titlecase tokens also count, but lower confidence.
            if first[0].isupper() and first[1:].islower():
                brandish += 0.5

    if total == 0:
        return "mixed"
    return "start" if (brandish / total) >= 0.65 else "mixed"


def _build_warnings(
    df: pd.DataFrame,
    trailing_suspicious: list[tuple[int, str]],
    supplier_titles: list[str],
    amazon_titles: list[str],
) -> list[str]:
    warnings: list[str] = []

    for row_idx, title in trailing_suspicious[:10]:
        warnings.append(
            f"Row {row_idx}: trailing number looks like qty but may be a model/code -> {title[:120]!r}"
        )

    # Titles where explicit unit tokens exist but no quantity is nearby (may confuse simplistic extractors).
    for i, t in enumerate(supplier_titles, start=1):
        if len(warnings) >= 15:
            break
        if _EXPLICIT_UNIT_TOKEN_RE.search(t) and not (_EXPLICIT_UNIT_QTY_RE.search(t) or _PACK_OF_QTY_RE.search(t)):
            warnings.append(f"Row {i}: unit keyword without clear qty -> {t[:120]!r}")

    # Leading multipliers that might be dimensions (e.g., 10x5cm) rather than pack qty.
    for i, t in enumerate(amazon_titles, start=1):
        if len(warnings) >= 20:
            break
        if _LEADING_MULTIPLIER_RE.search(t) and _DIMENSION_RE.search(t):
            warnings.append(f"Row {i}: 'Nx' present with dimensions; avoid treating as pack qty -> {t[:120]!r}")

    # Duplicated numeric tokens at end (e.g., "... 200 200") often codes.
    for i, t in enumerate(supplier_titles, start=1):
        if len(warnings) >= 25:
            break
        parts = re.findall(r"\b\d+\b", t)
        if len(parts) >= 2 and parts[-1] == parts[-2]:
            warnings.append(f"Row {i}: repeated trailing number may be code, not qty -> {t[:120]!r}")

    return warnings


def calibrate_from_csv(csv_path: Path, sample_rows: int = 50) -> CalibrationResult:
    if not csv_path.exists():
        raise FileNotFoundError(str(csv_path))

    # Try common read_csv settings; keep it robust against odd encodings / separators.
    read_attempts = [
        dict(nrows=sample_rows),
        dict(nrows=sample_rows, encoding="utf-8-sig"),
        dict(nrows=sample_rows, encoding="cp1252"),
        dict(nrows=sample_rows, sep=";"),
        dict(nrows=sample_rows, sep=";", encoding="cp1252"),
    ]
    last_err: Exception | None = None
    df: pd.DataFrame | None = None
    for kwargs in read_attempts:
        try:
            df = pd.read_csv(csv_path, on_bad_lines="skip", low_memory=False, **kwargs)
            break
        except Exception as e:  # noqa: BLE001 - CLI robustness
            last_err = e
    if df is None:
        raise RuntimeError(f"Failed to read CSV: {csv_path}") from last_err

    sales_column = _detect_sales_column(df.columns)

    supplier_titles = list(_iter_titles(df, "SupplierTitle"))
    amazon_titles = list(_iter_titles(df, "AmazonTitle"))

    explicit_units = _extract_observed_explicit_units(supplier_titles + amazon_titles)
    leading_multiplier_check = _detect_leading_multiplier_common(supplier_titles + amazon_titles)
    allow_trailing, trailing_suspicious = _detect_trailing_number_as_qty_common(supplier_titles)
    dimension_shield_keywords = _detect_dimension_keywords(supplier_titles + amazon_titles)
    brand_position = _detect_brand_position(supplier_titles)

    warnings = _build_warnings(df, trailing_suspicious, supplier_titles, amazon_titles)

    return CalibrationResult(
        explicit_units=explicit_units,
        allow_trailing_number_as_qty=allow_trailing,
        leading_multiplier_check=leading_multiplier_check,
        dimension_shield_keywords=dimension_shield_keywords,
        brand_position=brand_position,
        sales_column=sales_column,
        warnings=warnings,
    )


def _format_python_config(result: CalibrationResult) -> str:
    def _py_list_str(items: list[str]) -> str:
        return "[" + ", ".join(repr(x) for x in items) + "]"

    lines: list[str] = []
    lines.append("# --- CALIBRATION CONFIGURATION ---")
    lines.append("SUPPLIER_NAMING_CONVENTION = {")
    lines.append(f"    \"explicit_units\": {_py_list_str(result.explicit_units)},")
    lines.append(f"    \"allow_trailing_number_as_qty\": {result.allow_trailing_number_as_qty},")
    lines.append(f"    \"leading_multiplier_check\": {result.leading_multiplier_check},")
    lines.append(f"    \"dimension_shield_keywords\": {_py_list_str(result.dimension_shield_keywords)},")
    lines.append(f"    \"brand_position\": {result.brand_position!r},")
    lines.append(f"    \"sales_column\": {result.sales_column!r},")
    lines.append("}")
    lines.append("# ---------------------------------")
    if result.warnings:
        lines.append("")
        lines.append("# --- CALIBRATION WARNINGS (sample) ---")
        for w in result.warnings:
            lines.append(f"# - {w}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect supplier naming conventions from a financial report CSV.")
    parser.add_argument("csv_path", type=Path, help="Path to the financial report CSV")
    parser.add_argument("--rows", type=int, default=50, help="Number of rows to sample (default: 50)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    result = calibrate_from_csv(args.csv_path, sample_rows=args.rows)
    print(_format_python_config(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

