"""
Pre-flight calibration for FBA financial reports (CSV/XLSX).

Goal: read the first N rows of a supplier financial report and infer:
- pack quantity patterns (explicit units, trailing qty, leading multipliers, dimensions)
- capacity multipack patterns in Amazon titles (e.g. "3 x 400ml" => RSU=3)
- which sales column to use
- where brands tend to appear in SupplierTitle

Outputs a configuration block that a downstream analysis can reuse.
"""

from __future__ import annotations

import argparse
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

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
_EXPLICIT_UNITS_PATTERN = (
    r"(pcs?|pce|pc|piece|pieces|pk|pack|unit|units|ct|count|ea|each|"
    r"case|cases|bag|bags|sheet|sheets|stick|sticks|capsule|capsules|tablet|tablets|"
    r"roll|rolls|pair|pairs|bottle|bottles|box|boxes)"
)
_EXPLICIT_UNIT_TOKEN_RE = re.compile(rf"\b{_EXPLICIT_UNITS_PATTERN}\b", re.IGNORECASE)
_EXPLICIT_UNIT_QTY_RE = re.compile(rf"\b(\d{{1,4}})\s*{_EXPLICIT_UNITS_PATTERN}\b", re.IGNORECASE)
_PACK_OF_QTY_RE = re.compile(r"\b(pack\s*of|set\s*of)\s*(\d{1,4})\b", re.IGNORECASE)
_PK_PREFIX_QTY_RE = re.compile(r"\bpk\s*(\d{1,4})\b|\bpk(\d{1,4})\b", re.IGNORECASE)
_DATE_CODE_HINT_RE = re.compile(r"\b\d{1,2}/\d{1,2}\b")

_DIMENSION_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*(cm|mm|ml|l|ltr|litre|liter|kg|g|oz|inch|in|ft|m)\b", re.IGNORECASE
)
_DIMENSION_X_RE = re.compile(
    r"\b\d+(?:\.\d+)?\s*[x×]\s*\d+(?:\.\d+)?(?:\s*[x×]\s*\d+(?:\.\d+)?)?\s*"
    r"(cm|mm|m|inch|in|ft)\b",
    re.IGNORECASE,
)

_CAPACITY_MULTIPACK_RE = re.compile(
    r"\b(\d{1,4})\s*[x×]\s*(\d+(?:\.\d+)?)\s*(ml|l|ltr|litre|liter|g|kg|oz)\b",
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
    brand_position: str  # "start" | "middle" | "end" | "mixed"
    sales_column: str
    capacity_pattern_as_rsu: bool
    supplier_domain: str | None
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
        if _PK_PREFIX_QTY_RE.search(t):
            found.add("pk")
        for m in _EXPLICIT_UNIT_TOKEN_RE.finditer(t):
            unit = m.group(1).lower()
            # normalize plurals
            if unit in ("piece", "pieces"):
                unit = "pcs"
            elif unit == "pc":
                unit = "pcs"
            elif unit == "units":
                unit = "unit"
            elif unit == "boxes":
                unit = "box"
            elif unit.endswith("s") and unit[:-1] in {
                "case",
                "bag",
                "sheet",
                "stick",
                "capsule",
                "tablet",
                "roll",
                "pair",
                "bottle",
                "box",
            }:
                unit = unit[:-1]
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


_VARIANT_NUMBER_HINT_RE = re.compile(
    r"\b(girl|boy|number|no\.?|circle|candle|age|years?)\s*\d{1,4}\s*$",
    re.IGNORECASE,
)
_RANGE_SUFFIX_RE = re.compile(r"\b\d{1,4}\s*[-–]\s*\d{1,4}\s*$")


def _collect_trailing_number_examples(titles: list[str]) -> list[tuple[int, int, str]]:
    """
    Collect titles with a trailing bare number (excluding dimension-like endings).

    Returns: list of (row_index_1_based, qty, title)
    """
    examples: list[tuple[int, int, str]] = []
    for i, raw in enumerate(titles, start=1):
        t = raw.strip()
        if not t:
            continue
        m = _TRAILING_NUMBER_RE.search(t)
        if not m:
            continue
        qty = int(m.group(1))
        if qty <= 1:
            continue

        prefix = t[: m.start(1)].strip()
        prev_token = prefix.split()[-1].strip("()[]{}.,;:/\\-") if prefix.split() else ""
        if _is_dimension_like_token(prev_token):
            continue

        # If a pack qty is already explicitly stated, this trailing number is less likely to be a trap.
        if _PACK_OF_QTY_RE.search(t) or _EXPLICIT_UNIT_QTY_RE.search(t) or _PK_PREFIX_QTY_RE.search(t):
            continue

        examples.append((i, qty, t))
    return examples


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


def _infer_supplier_domain(df: pd.DataFrame) -> str | None:
    if "SupplierURL" not in df.columns:
        return None
    for raw in df["SupplierURL"].tolist():
        url = _safe_str(raw)
        if not url:
            continue
        try:
            host = urlparse(url).netloc.lower()
        except Exception:  # noqa: BLE001
            continue
        host = host.split("@")[-1]
        if host.startswith("www."):
            host = host[4:]
        if host:
            return host
    return None


def _detect_capacity_multipack_common(
    amazon_titles: list[str],
) -> tuple[bool, list[tuple[int, str, int, float, str]]]:
    """
    Returns:
      - capacity_pattern_as_rsu: True if patterns like '3 x 400ml' appear
      - examples: list of (row_index_1_based, matched_substring, n, size_value, size_unit) for warnings
    """
    examples: list[tuple[int, str, int, float, str]] = []
    if not amazon_titles:
        return False, examples

    hits = 0
    total = 0
    for i, t in enumerate(amazon_titles, start=1):
        t = t.strip()
        if not t:
            continue
        total += 1
        m = _CAPACITY_MULTIPACK_RE.search(t)
        if not m:
            continue
        hits += 1
        if len(examples) < 10:
            n = int(m.group(1))
            size_value = float(m.group(2))
            size_unit = m.group(3).lower()
            if size_unit in ("litre", "liter"):
                size_unit = "ltr"
            examples.append((i, m.group(0), n, size_value, size_unit))

    return (hits / max(total, 1)) >= 0.02, examples


def _build_warnings(
    df: pd.DataFrame,
    trailing_suspicious: list[tuple[int, str]],
    trailing_examples: list[tuple[int, int, str]],
    supplier_titles: list[str],
    amazon_titles: list[str],
    capacity_multipack_examples: list[tuple[int, str, int, float, str]],
    allow_trailing_number_as_qty: bool,
) -> list[str]:
    warnings: list[str] = []

    for row_idx, title in trailing_suspicious[:10]:
        warnings.append(
            f"Row {row_idx}: '{title[:80]}' should treat trailing number as model/code, not pack quantity"
        )

    # Date/code suffixes (e.g. "05/11") can trick trailing-number logic.
    for i, t in enumerate(supplier_titles, start=1):
        if len(warnings) >= 12:
            break
        if _DATE_CODE_HINT_RE.search(t) and _TRAILING_NUMBER_RE.search(t):
            warnings.append(
                f"Row {i}: '{t[:80]}' should treat date/code suffix as reference, not pack quantity"
            )

    # Prefix pack tokens like "PK12" (unit before digits) are easy to miss.
    for i, t in enumerate(supplier_titles, start=1):
        if len(warnings) >= 14:
            break
        m = _PK_PREFIX_QTY_RE.search(t)
        if m:
            qty = int(m.group(1) or m.group(2))
            warnings.append(f"Row {i}: '{m.group(0)}' should be RSU={qty} (pack qty), not RSU=1")

    if not allow_trailing_number_as_qty:
        for row_idx, qty, title in trailing_examples[:10]:
            if len(warnings) >= 15:
                break
            if _RANGE_SUFFIX_RE.search(title):
                warnings.append(
                    f"Row {row_idx}: '{title[:80]}' should be RSU=1 (size range), not RSU={qty}"
                )
            elif _VARIANT_NUMBER_HINT_RE.search(title):
                warnings.append(
                    f"Row {row_idx}: '{title[:80]}' should be RSU=1 (variant/age/number), not RSU={qty}"
                )
            else:
                warnings.append(
                    f"Row {row_idx}: '{title[:80]}' likely indicates pack qty RSU={qty}, not RSU=1"
                )

    for row_idx, snippet, n, size_value, size_unit in capacity_multipack_examples[:10]:
        multiplied = n * size_value
        wrong_rsu = f"{multiplied:g}"
        warnings.append(
            f"Row {row_idx}: '{snippet}' should be RSU={n} (units), not RSU={wrong_rsu}"
        )

    # Titles where explicit unit tokens exist but no quantity is nearby (may confuse simplistic extractors).
    for i, t in enumerate(supplier_titles, start=1):
        if len(warnings) >= 20:
            break
        if _EXPLICIT_UNIT_TOKEN_RE.search(t) and not (_EXPLICIT_UNIT_QTY_RE.search(t) or _PACK_OF_QTY_RE.search(t)):
            warnings.append(
                f"Row {i}: '{t[:80]}' should not infer RSU without a nearby quantity, not default to a random qty"
            )

    # Dimension traps: NxM with a dimension unit (e.g. "70x100cm").
    for i, t in enumerate(supplier_titles, start=1):
        if len(warnings) >= 25:
            break
        if _DIMENSION_X_RE.search(t):
            warnings.append(
                f"Row {i}: '{t[:80]}' should treat NxM as dimensions, not RSU=multiplied dimensions"
            )

    # Amazon titles: NxM dimension blocks can appear alongside qty multipacks; don't multiply dimensions into RSU.
    for i, t in enumerate(amazon_titles, start=1):
        if len(warnings) >= 30:
            break
        if _DIMENSION_X_RE.search(t):
            warnings.append(
                f"Row {i}: '{t[:80]}' should treat NxM as dimensions, not RSU=multiplied dimensions"
            )

    # Duplicated numeric tokens at end (e.g., "... 200 200") often codes.
    for i, t in enumerate(supplier_titles, start=1):
        if len(warnings) >= 35:
            break
        parts = re.findall(r"\b\d+\b", t)
        if len(parts) >= 2 and parts[-1] == parts[-2]:
            warnings.append(
                f"Row {i}: '{t[:80]}' should treat repeated trailing number as code, not pack quantity"
            )

    return warnings


def _read_report_sample(report_path: Path, sample_rows: int, sheet: str | int | None) -> pd.DataFrame:
    if not report_path.exists():
        raise FileNotFoundError(str(report_path))

    suffix = report_path.suffix.lower()
    if suffix in {".xlsx", ".xlsm", ".xls"}:
        return pd.read_excel(report_path, nrows=sample_rows, sheet_name=sheet or 0, engine="openpyxl")

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
            df = pd.read_csv(report_path, on_bad_lines="skip", low_memory=False, **kwargs)
            break
        except Exception as e:  # noqa: BLE001 - CLI robustness
            last_err = e
    if df is None:
        raise RuntimeError(f"Failed to read report file: {report_path}") from last_err

    return df


def calibrate_from_report(report_path: Path, sample_rows: int = 50, sheet: str | int | None = None) -> CalibrationResult:
    df = _read_report_sample(report_path, sample_rows=sample_rows, sheet=sheet)

    sales_column = _detect_sales_column(df.columns)

    supplier_titles = list(_iter_titles(df, "SupplierTitle"))
    amazon_titles = list(_iter_titles(df, "AmazonTitle"))

    explicit_units = _extract_observed_explicit_units(supplier_titles + amazon_titles)
    leading_multiplier_check = _detect_leading_multiplier_common(supplier_titles + amazon_titles)
    allow_trailing, trailing_suspicious = _detect_trailing_number_as_qty_common(supplier_titles)
    trailing_examples = _collect_trailing_number_examples(supplier_titles)
    dimension_shield_keywords = _detect_dimension_keywords(supplier_titles + amazon_titles)
    brand_position = _detect_brand_position(supplier_titles)
    capacity_pattern_as_rsu, capacity_examples = _detect_capacity_multipack_common(amazon_titles)
    supplier_domain = _infer_supplier_domain(df)

    warnings = _build_warnings(
        df,
        trailing_suspicious,
        trailing_examples,
        supplier_titles,
        amazon_titles,
        capacity_examples,
        allow_trailing_number_as_qty=allow_trailing,
    )

    return CalibrationResult(
        explicit_units=explicit_units,
        allow_trailing_number_as_qty=allow_trailing,
        leading_multiplier_check=leading_multiplier_check,
        dimension_shield_keywords=dimension_shield_keywords,
        brand_position=brand_position,
        sales_column=sales_column,
        capacity_pattern_as_rsu=capacity_pattern_as_rsu,
        supplier_domain=supplier_domain,
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
    lines.append(f"    \"capacity_pattern_as_rsu\": {result.capacity_pattern_as_rsu},")
    lines.append("}")
    lines.append("# ---------------------------------")
    return "\n".join(lines)


def _format_markdown(result: CalibrationResult, report_path: Path, sample_rows: int) -> str:
    lines: list[str] = []
    lines.append("# Preflight calibration (v1.1)")
    lines.append("")
    lines.append(f"- Source: `{report_path}`")
    lines.append(f"- Sample rows: `{sample_rows}`")
    if result.supplier_domain:
        lines.append(f"- Detected supplier domain: `{result.supplier_domain}`")
    lines.append("")
    lines.append("## Calibration configuration")
    lines.append("")
    lines.append("```python")
    lines.append(_format_python_config(result))
    lines.append("```")
    lines.append("")
    lines.append("## Calibration warnings (sample)")
    lines.append("")
    if not result.warnings:
        lines.append("- (none detected in sample)")
    else:
        for w in result.warnings:
            lines.append(f"- {w}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect supplier naming conventions from a financial report (CSV/XLSX).")
    parser.add_argument("report_path", type=Path, help="Path to the financial report (.csv/.xlsx)")
    parser.add_argument("--rows", type=int, default=50, help="Number of rows to sample (default: 50)")
    parser.add_argument(
        "--sheet",
        default=None,
        help="Excel sheet name/index (XLSX only). Default: first sheet.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write output to a file (recommended: .md). Default: print to stdout.",
    )
    parser.add_argument(
        "--format",
        choices=["python", "markdown"],
        default=None,
        help="Output format. Default: markdown if --output is set, else python.",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    sheet: str | int | None
    if args.sheet is None:
        sheet = None
    else:
        try:
            sheet = int(args.sheet)
        except ValueError:
            sheet = str(args.sheet)

    result = calibrate_from_report(args.report_path, sample_rows=args.rows, sheet=sheet)

    out_format = args.format
    if out_format is None:
        out_format = "markdown" if args.output else "python"

    if out_format == "markdown":
        rendered = _format_markdown(result, report_path=args.report_path, sample_rows=args.rows)
    else:
        rendered = _format_python_config(result)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
