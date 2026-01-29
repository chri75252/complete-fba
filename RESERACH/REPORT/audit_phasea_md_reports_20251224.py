from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

ASIN_RE = re.compile(r"\bB[0-9A-Z]{9}\b")


def read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except Exception:
            pass
    return path.read_text(errors="replace")


def digits_only(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, float) and np.isnan(value):
        return None
    if isinstance(value, (int, np.integer)):
        return str(int(value))
    if isinstance(value, float):
        return str(int(round(value)))
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none"}:
        return None
    text = re.sub(r"\D+", "", text)
    return text or None


def checksum_ok(code: str | None) -> bool | None:
    if not code or not code.isdigit():
        return None

    if len(code) == 13:  # EAN-13
        digits = [int(c) for c in code]
        s = 0
        for i, dig in enumerate(digits[:-1]):
            pos = i + 1
            s += 3 * dig if (pos % 2 == 0) else dig
        return ((10 - (s % 10)) % 10) == digits[-1]

    if len(code) == 8:  # EAN-8
        digits = [int(c) for c in code]
        s = 0
        for i, dig in enumerate(digits[:-1]):
            pos = i + 1
            s += 3 * dig if (pos % 2 == 1) else dig
        return ((10 - (s % 10)) % 10) == digits[-1]

    if len(code) == 12:  # UPC-A
        digits = [int(c) for c in code]
        s = 0
        for i, dig in enumerate(digits[:-1]):
            pos = i + 1
            s += 3 * dig if (pos % 2 == 1) else dig
        return ((10 - (s % 10)) % 10) == digits[-1]

    return None


STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "of",
    "a",
    "an",
    "to",
    "in",
    "on",
    "by",
    "from",
    "new",
    "genuine",
    "original",
    "pack",
    "packs",
    "set",
    "pcs",
    "pc",
    "pce",
    "piece",
    "pieces",
    "count",
    "x",
    "mm",
    "cm",
    "ml",
    "l",
    "litre",
    "liter",
    "kg",
    "g",
    "oz",
    "lb",
    "inch",
    "in",
}


def norm_text(text: str) -> str:
    text = (text or "").lower().replace("×", "x")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def tokenise(text: str) -> list[str]:
    return [t for t in norm_text(text).split() if t and t not in STOPWORDS]


def jaccard(a: Iterable[str], b: Iterable[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def fuzzy_ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, norm_text(a), norm_text(b)).ratio()


def extract_pack(title: str) -> list[int]:
    t = (title or "").lower().replace("×", "x")
    pack: list[int] = []

    for m in re.finditer(r"\bpack\s*of\s*(\d+)\b", t):
        pack.append(int(m.group(1)))
    for m in re.finditer(r"\b(?:pk|pack)\s*(\d+)\b", t):
        pack.append(int(m.group(1)))
    for m in re.finditer(r"\b(\d+)\s*(?:pcs|pc|pce|pieces|piece|count)\b", t):
        pack.append(int(m.group(1)))
    for m in re.finditer(r"\bset\s*of\s*(\d+)\b", t):
        pack.append(int(m.group(1)))

    # multiplicative patterns like (4 x 50) but avoid dimensions (280 x 120 mm)
    for m in re.finditer(r"\b(\d+)\s*x\s*(\d+)\b", t):
        window = t[m.start() : m.end() + 12]
        if re.search(r'\b(?:mm|cm|m|inch|in|")\b', window):
            continue
        a, b = int(m.group(1)), int(m.group(2))
        if 1 <= a <= 100 and 1 <= b <= 1000:
            pack.append(a * b)

    return sorted(set(pack))


def extract_specs(title: str) -> dict[str, Any]:
    t = (title or "").lower().replace("×", "x")

    volumes_ml: list[float] = []
    weights_g: list[float] = []
    sizes: list[str] = []
    assorted = bool(re.search(r"\b(assorted|variety|random|mixed)\b", t))

    for m in re.finditer(r"\b(\d+(?:\.\d+)?)\s*(ml|l|litre|liter|g|kg)\b", t):
        val = float(m.group(1))
        unit = m.group(2)
        if unit in {"l", "litre", "liter"}:
            volumes_ml.append(val * 1000)
        elif unit == "kg":
            weights_g.append(val * 1000)
        elif unit == "ml":
            volumes_ml.append(val)
        elif unit == "g":
            weights_g.append(val)

    for m in re.finditer(r"\b(xs|s|m|l|xl|xxl|xxxl)\b", t):
        sizes.append(m.group(1))

    return {
        "volumes_ml": sorted(set(round(v, 3) for v in volumes_ml)),
        "weights_g": sorted(set(round(v, 3) for v in weights_g)),
        "sizes": sorted(set(sizes)),
        "assorted": assorted,
    }


@dataclass(frozen=True)
class ValidityMeta:
    similarity: float
    shared_tokens: int
    contradiction: str | None
    ean_match: bool
    ean_checksum_ok: bool | None


def assess_validity(
    supplier_title: str, amazon_title: str, supplier_ean: str | None, amazon_ean: str | None
) -> tuple[str, ValidityMeta]:
    supplier_title = supplier_title or ""
    amazon_title = amazon_title or ""

    tok_s = tokenise(supplier_title)
    tok_a = tokenise(amazon_title)
    similarity = 0.6 * jaccard(tok_s, tok_a) + 0.4 * fuzzy_ratio(supplier_title, amazon_title)
    shared = len(set(tok_s) & set(tok_a))

    pack_s = extract_pack(supplier_title)
    pack_a = extract_pack(amazon_title)
    spec_s = extract_specs(supplier_title)
    spec_a = extract_specs(amazon_title)

    contradiction: str | None = None
    if pack_s and pack_a:
        ps, pa = min(pack_s), min(pack_a)
        if ps != pa:
            contradiction = f"pack mismatch ({ps} vs {pa})"

    if not contradiction and spec_s["volumes_ml"] and spec_a["volumes_ml"]:
        vs, va = min(spec_s["volumes_ml"]), min(spec_a["volumes_ml"])
        if abs(vs - va) / max(vs, va) > 0.2:
            contradiction = f"volume mismatch ({vs}ml vs {va}ml)"

    if not contradiction and spec_s["weights_g"] and spec_a["weights_g"]:
        ws, wa = min(spec_s["weights_g"]), min(spec_a["weights_g"])
        if abs(ws - wa) / max(ws, wa) > 0.2:
            contradiction = f"weight mismatch ({ws}g vs {wa}g)"

    if not contradiction and spec_s["sizes"] and spec_a["sizes"]:
        if set(spec_s["sizes"]) != set(spec_a["sizes"]):
            contradiction = f"size token mismatch ({spec_s['sizes']} vs {spec_a['sizes']})"

    if not contradiction and (spec_s["assorted"] or spec_a["assorted"]):
        contradiction = "assorted/variety indicator"

    ean_match = bool(supplier_ean and amazon_ean and supplier_ean == amazon_ean)
    checksum_s = checksum_ok(supplier_ean)
    checksum_a = checksum_ok(amazon_ean)
    checksum_both = (
        True
        if (checksum_s is True and checksum_a is True)
        else (False if (checksum_s is False or checksum_a is False) else None)
    )

    meta = ValidityMeta(
        similarity=similarity,
        shared_tokens=shared,
        contradiction=contradiction,
        ean_match=ean_match,
        ean_checksum_ok=checksum_both,
    )

    # VALID if exact EAN match + checksum valid and no contradiction.
    if ean_match and checksum_s is True and checksum_a is True:
        if contradiction:
            return "NEEDS REVIEW", meta
        if similarity < 0.10 and shared == 0:
            return (
                "NEEDS REVIEW",
                ValidityMeta(
                    similarity=similarity,
                    shared_tokens=shared,
                    contradiction="EAN exact but title sanity weak",
                    ean_match=ean_match,
                    ean_checksum_ok=checksum_both,
                ),
            )
        return "VALID", meta

    # Non-EAN path: similarity + contradiction gates.
    if contradiction and similarity < 0.35:
        return "INVALID", meta

    if similarity >= 0.82 and shared >= 3 and not contradiction:
        return "LIKELY VALID", meta

    if similarity >= 0.60 and shared >= 2 and not contradiction:
        return "NEEDS REVIEW", meta

    if similarity >= 0.45 and shared >= 2:
        return "NEEDS REVIEW", meta

    return "INVALID", meta


def parse_metrics(text: str) -> dict[str, int | float | str]:
    out: dict[str, int | float | str] = {}

    m = re.search(
        r"\n\|\s*Metric\s*\|\s*Count\s*\|\n\|[^\n]+\n(?P<body>(?:\|[^\n]+\n)+)",
        text,
        flags=re.IGNORECASE,
    )
    if m:
        for line in m.group("body").splitlines():
            if not line.strip().startswith("|"):
                continue
            parts = [p.strip() for p in line.strip().strip("|").split("|")]
            if len(parts) < 2:
                continue
            key, val = parts[0], parts[1]
            num = re.sub(r"[^0-9.+-]", "", val)
            out[key] = int(num) if num.isdigit() else (float(num) if num else val)

    for line in text.splitlines():
        m2 = re.match(r"^\s*[-*]\s+([^:]+):\s*\*\*([^*]+)\*\*\s*$", line)
        if not m2:
            continue
        key = m2.group(1).strip()
        val = m2.group(2).strip()
        num = re.sub(r"[^0-9.+-]", "", val)
        out[key] = int(num) if num.isdigit() else (float(num) if num else val)

    return out


@dataclass(frozen=True)
class ParsedRow:
    report: str
    section: str
    verdict: str | None
    confidence: float | None
    supplier_title: str | None
    amazon_title: str | None
    supplier_ean: str | None
    amazon_ean: str | None
    asin: str | None
    raw_line: str


def to_floatish(text: str | None) -> float | None:
    if text is None:
        return None
    t = re.sub(r"[^0-9.+-]", "", text.replace(",", ""))
    if not t:
        return None
    try:
        return float(t)
    except Exception:
        return None


def split_md_row(line: str) -> list[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    parts = re.split(r"(?<!\\)\|", s)
    return [p.strip().replace("\\|", "|") for p in parts]


def parse_md_tables(report_path: Path) -> list[ParsedRow]:
    text = read_text(report_path)
    lines = text.splitlines()

    rows: list[ParsedRow] = []
    section = ""
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("#"):
            section = line.lstrip("#").strip()

        if line.strip().startswith("|") and "Verdict" in line and "ASIN" in line:
            header = split_md_row(line)

            def idx(col: str) -> int | None:
                col = col.lower().strip()
                for j, h in enumerate(header):
                    if h.lower().strip() == col:
                        return j
                return None

            expected = len(header)
            asin_idx = idx("ASIN")

            i += 2  # skip alignment row
            while i < len(lines) and lines[i].strip().startswith("|"):
                raw = lines[i]
                cells = split_md_row(raw)

                # If a title contains '|' characters, the row may have more cells than expected.
                if asin_idx is not None and len(cells) != expected and len(cells) >= expected:
                    tail_needed = expected - asin_idx
                    tail = cells[-tail_needed:]
                    head = cells[: len(cells) - tail_needed]

                    # Common Phase A table shape has 6 cells before ASIN:
                    # Verdict, Confidence, SupplierTitle, AmazonTitle, Supplier EAN, Amazon EAN
                    if asin_idx >= 6 and len(head) > 6:
                        verdict = head[0]
                        conf = head[1]
                        sup_title = head[2]
                        sup_ean = head[-2]
                        amz_ean = head[-1]
                        amz_title = "|".join(head[3:-2]).strip()
                        head_fixed = [verdict, conf, sup_title, amz_title, sup_ean, amz_ean]
                        while len(head_fixed) < asin_idx:
                            head_fixed.append("")
                        cells = head_fixed[:asin_idx] + tail

                def get(col: str) -> str | None:
                    j = idx(col)
                    if j is None or j >= len(cells):
                        return None
                    v = cells[j].strip()
                    return v if v and v != "-" else None

                asin = get("ASIN")
                if asin:
                    m_asin = ASIN_RE.search(asin)
                    asin = m_asin.group(0) if m_asin else asin

                rows.append(
                    ParsedRow(
                        report=report_path.name,
                        section=section,
                        verdict=get("Verdict"),
                        confidence=to_floatish(get("Confidence (0-100)")) or to_floatish(get("Confidence")),
                        supplier_title=get("SupplierTitle"),
                        amazon_title=get("AmazonTitle"),
                        supplier_ean=digits_only(get("Supplier EAN")),
                        amazon_ean=digits_only(get("Amazon EAN")),
                        asin=asin,
                        raw_line=raw,
                    )
                )
                i += 1
            continue

        i += 1

    return rows


def best_match_index(sub: pd.DataFrame, supplier_title: str | None, amazon_title: str | None) -> int | None:
    if sub.empty:
        return None
    if len(sub) == 1:
        return int(sub.index[0])

    st = supplier_title or ""
    at = amazon_title or ""

    def score(row: pd.Series) -> float:
        s = 0.0
        if st:
            s += 0.7 * SequenceMatcher(None, norm_text(st), norm_text(row["supplier_title"])).ratio()
        if at:
            s += 0.3 * SequenceMatcher(None, norm_text(at), norm_text(row["amazon_title"])).ratio()
        return s

    return int(max(((score(sub.loc[i]), i) for i in sub.index), key=lambda x: x[0])[1])


def fmt_pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def md_escape(s: str) -> str:
    return (s or "").replace("|", "\\\\|")


def main() -> None:
    repo_root = Path.cwd()
    part3_path = (repo_root / "RESERACH" / "REPORT" / "PART3" / "PART3.xlsx").resolve()

    report_paths = [
        Path(r"C:\Users\chris\Downloads\PHASEA_MANUAL_REPORT_20251224.md"),
        Path(r"C:\Users\chris\Downloads\PHASEA_MANUAL_REPORT_2512240724.md"),
        Path(r"C:\Users\chris\Downloads\PHASEA_MANUAL_REPORT_2512240124.md"),
        Path(r"C:\Users\chris\Downloads\PHASEA_MANUAL_REPORT_2512240128.md"),
    ]

    if not part3_path.exists():
        raise FileNotFoundError(part3_path)
    for rp in report_paths:
        if not rp.exists():
            raise FileNotFoundError(rp)

    df_raw = pd.read_excel(part3_path, sheet_name="PART3")
    canon = pd.DataFrame(
        {
            "supplier_ean": df_raw["EAN"].map(digits_only),
            "amazon_ean": df_raw["EAN_OnPage"].map(digits_only),
            "asin": df_raw["ASIN"].astype(str),
            "supplier_title": df_raw["SupplierTitle"].astype(str),
            "amazon_title": df_raw["AmazonTitle"].astype(str),
            "supplier_url": df_raw["SupplierURL"].astype(str),
            "sales": pd.to_numeric(df_raw["bought_in_past_month"], errors="coerce"),
            "net_profit": pd.to_numeric(df_raw["NetProfit"], errors="coerce"),
            "roi": pd.to_numeric(df_raw["ROI"], errors="coerce"),
        }
    )

    canon["key_asin_sup_ean"] = canon.apply(
        lambda r: f"{r['asin']}|{r['supplier_ean']}" if r["supplier_ean"] else f"{r['asin']}|NO_SUP_EAN",
        axis=1,
    )

    baseline = {
        "total_rows": int(len(canon)),
        "supplier_title_present": int(canon["supplier_title"].notna().sum()),
        "amazon_title_present": int(canon["amazon_title"].notna().sum()),
        "supplier_ean_present": int(canon["supplier_ean"].notna().sum()),
        "amazon_ean_present": int(canon["amazon_ean"].notna().sum()),
        "asin_present": int(canon["asin"].replace("nan", np.nan).notna().sum()),
        "sales_gt_0": int((canon["sales"].fillna(0) > 0).sum()),
        "net_profit_gt_0": int((canon["net_profit"].fillna(0) > 0).sum()),
        "unique_asin": int(canon["asin"].nunique(dropna=True)),
        "unique_key_asin_sup_ean": int(canon["key_asin_sup_ean"].nunique(dropna=True)),
    }

    supplier_domains = (
        canon["supplier_url"]
        .str.extract(r"https?://(?:www\\.)?([^/]+)/", expand=False)
        .value_counts()
        .head(5)
    )

    # validity rubric
    metas: dict[int, ValidityMeta] = {}
    validity_labels = []
    for idx, r in canon.iterrows():
        lbl, meta = assess_validity(r["supplier_title"], r["amazon_title"], r["supplier_ean"], r["amazon_ean"])
        validity_labels.append(lbl)
        metas[int(idx)] = meta
    canon["validity"] = validity_labels
    label_dist = Counter(canon["validity"].tolist())

    exact_ean = (
        canon["supplier_ean"].notna()
        & canon["amazon_ean"].notna()
        & (canon["supplier_ean"] == canon["amazon_ean"])
    )
    exact_ean_count = int(exact_ean.sum())
    exact_ean_checksum_ok = int(
        sum(
            (checksum_ok(s) is True and checksum_ok(a) is True)
            for s, a in zip(canon.loc[exact_ean, "supplier_ean"], canon.loc[exact_ean, "amazon_ean"], strict=False)
        )
    )

    # high-impact pool = not INVALID (fallback to all rows if pool is tiny)
    impact_pool = canon[canon["validity"] != "INVALID"]
    if len(impact_pool) < 40:
        impact_pool = canon
    hi_sales = set(impact_pool.sort_values(["sales", "net_profit"], ascending=False).head(50).index.astype(int))
    hi_profit = set(impact_pool.sort_values(["net_profit", "sales"], ascending=False).head(50).index.astype(int))
    high_impact = hi_sales | hi_profit

    def weighted_validity_score(dist: Counter) -> float:
        weights = {"VALID": 1.0, "LIKELY VALID": 0.7, "NEEDS REVIEW": 0.3, "INVALID": 0.0}
        total = sum(dist.values())
        if total == 0:
            return 0.0
        return sum(weights.get(k, 0.0) * v for k, v in dist.items()) / total

    def coverage_score(matched: list[int]) -> float:
        if not high_impact:
            return 0.0
        return len(set(matched) & high_impact) / len(high_impact)

    def contradiction_rate(matched: list[int]) -> float:
        if not matched:
            return 0.0
        return sum(1 for i in matched if metas[i].contradiction) / len(matched)

    def clarity_score(rec_rows: list[ParsedRow]) -> float:
        if not rec_rows:
            return 0.0
        ok = 0
        for r in rec_rows:
            if r.asin and r.supplier_title and r.amazon_title and (r.confidence is not None):
                ok += 1
        return ok / len(rec_rows)

    # parse reports
    report_results = []
    membership: dict[int, set[str]] = defaultdict(set)

    for rp in report_paths:
        text = read_text(rp)
        claimed = parse_metrics(text)
        parsed_all = parse_md_tables(rp)

        def is_recommended(pr: ParsedRow) -> bool:
            sec = (pr.section or "").lower()
            if "filter" in sec and "audit" in sec:
                return False
            if "excluded" in sec or "audit" in sec:
                return False
            if "recommended" in sec:
                return True
            if pr.verdict and pr.verdict.strip().upper() in {"VERIFIED", "HIGH LIKELIHOOD", "NEEDS VERIFICATION"}:
                return True
            return False

        rec_rows = [r for r in parsed_all if is_recommended(r)]
        rec_verdict_counts = Counter((r.verdict or "").strip().upper() for r in rec_rows)

        mapped: list[int | None] = []
        for r in rec_rows:
            sub = canon
            if r.asin:
                sub = sub[sub["asin"] == r.asin]
            if r.supplier_ean:
                sub = sub[sub["supplier_ean"] == r.supplier_ean]
            elif r.amazon_ean:
                sub = sub[sub["amazon_ean"] == r.amazon_ean]
            mapped.append(best_match_index(sub, r.supplier_title, r.amazon_title))

        matched = [i for i in mapped if i is not None]
        for i in matched:
            membership[i].add(rp.name)

        match_rate = (len(matched) / len(rec_rows)) if rec_rows else 0.0
        dist = Counter(canon.loc[matched, "validity"].tolist()) if matched else Counter()
        unique_asin = len({r.asin for r in rec_rows if r.asin})
        unique_key = len({canon.loc[i, "key_asin_sup_ean"] for i in matched})

        report_results.append(
            {
                "report": rp,
                "claimed": claimed,
                "parsed_rows_total": len(parsed_all),
                "parsed_rows_recommended": len(rec_rows),
                "rec_verdict_counts": rec_verdict_counts,
                "recommended_match_rate": match_rate,
                "unique_asin": unique_asin,
                "unique_key": unique_key,
                "validity_dist": dist,
                "matched": matched,
                "rec_rows": rec_rows,
            }
        )

    # scoring + winner selection
    scores = []
    for rr in report_results:
        vscore = weighted_validity_score(rr["validity_dist"])
        cscore = coverage_score(rr["matched"])
        prate = contradiction_rate(rr["matched"])
        clscore = clarity_score(rr["rec_rows"])
        total = 0.55 * vscore + 0.25 * cscore + 0.15 * (1 - prate) + 0.05 * clscore
        scores.append(
            {
                "report": rr["report"],
                "validity_score": vscore,
                "completeness_score": cscore,
                "pack_variant_score": 1 - prate,
                "clarity_score": clscore,
                "total_score": total,
            }
        )

    scores_sorted = sorted(scores, key=lambda x: x["total_score"], reverse=True)
    winner = scores_sorted[0]["report"] if scores_sorted else None
    winner_info = next((r for r in report_results if r["report"] == winner), None)
    winner_matched = set(winner_info["matched"]) if winner_info else set()

    missing_from_winner = canon.loc[~canon.index.isin(winner_matched)].sort_values(
        ["net_profit", "sales"], ascending=False
    )
    missing_top = missing_from_winner.head(25)

    questionable_idx = [
        i for i in sorted(winner_matched) if canon.loc[i, "validity"] not in {"VALID", "LIKELY VALID"}
    ]
    questionable = canon.loc[questionable_idx].sort_values(["sales", "net_profit"], ascending=False).head(25)

    other_rec_idx = set()
    for rr in report_results:
        if rr["report"] == winner:
            continue
        other_rec_idx |= set(rr["matched"])
    missing_in_winner_but_in_others = canon.loc[list(other_rec_idx - winner_matched)].sort_values(
        ["sales", "net_profit"], ascending=False
    ).head(25)

    # --------------------- markdown output ---------------------
    print('# Phase A MD Report Audit vs PART3.xlsx\n')
    print(f"**Reference dataset:** `{part3_path}`  " )
    print('**MD reports audited:**')
    for p in report_paths:
        print(f'- `{p}`')
    print('\n---\n')

    print('## 1) Executive Summary\n')
    if winner:
        win_score = next(s for s in scores_sorted if s['report'] == winner)
        print(f"**Winner:** `{winner}` (total score **{win_score['total_score']:.3f}**)\n")
    else:
        print('**Winner:** (none)\n')

    print(
        '- PART3 has **{rows} rows**; unique ASINs **{asins}**; exact EAN matches **{exact}** '
        '(checksum-valid: **{exact_ok}**).'.format(
            rows=baseline['total_rows'],
            asins=baseline['unique_asin'],
            exact=exact_ean_count,
            exact_ok=exact_ean_checksum_ok,
        )
    )
    print(
        '- PART3 rubric distribution: '
        f"VALID **{label_dist.get('VALID',0)}**, LIKELY VALID **{label_dist.get('LIKELY VALID',0)}**, "
        f"NEEDS REVIEW **{label_dist.get('NEEDS REVIEW',0)}**, INVALID **{label_dist.get('INVALID',0)}**."
    )
    print(f"- Two reports claim **1240** total rows; this PART3 has **{baseline['total_rows']}** rows.")
    if winner_info:
        dist = winner_info['validity_dist']
        print(
            f"- Winner parsed recommended rows: **{winner_info['parsed_rows_recommended']}**; "
            f"match-back: **{fmt_pct(winner_info['recommended_match_rate'])}**; unique ASINs: "
            f"**{winner_info['unique_asin']}**."
        )
        print(
            '- Winner validity (mapped recommendations): '
            f"VALID **{dist.get('VALID',0)}**, LIKELY VALID **{dist.get('LIKELY VALID',0)}**, "
            f"NEEDS REVIEW **{dist.get('NEEDS REVIEW',0)}**, INVALID **{dist.get('INVALID',0)}**."
        )
    print('\n---\n')

    print('## 2) PART3.xlsx Baseline Analysis\n')
    print('| Metric | Count |')
    print('|:--|--:|')
    for k, v in (
        ('Total rows', baseline['total_rows']),
        ('Rows with SupplierTitle', baseline['supplier_title_present']),
        ('Rows with AmazonTitle', baseline['amazon_title_present']),
        ('Rows with Supplier EAN present', baseline['supplier_ean_present']),
        ('Rows with Amazon EAN present', baseline['amazon_ean_present']),
        ('Rows with ASIN present', baseline['asin_present']),
        ('Rows with Sales > 0', baseline['sales_gt_0']),
        ('Rows with NetProfit > 0', baseline['net_profit_gt_0']),
        ('Unique ASINs', baseline['unique_asin']),
        ('Unique (ASIN, SupplierEAN) keys', baseline['unique_key_asin_sup_ean']),
    ):
        print(f'| {k} | {v} |')

    print('\n**Supplier URL domain (top):**')
    for dom, cnt in supplier_domains.items():
        print(f'- {dom}: {int(cnt)} rows')
    print('\n---\n')

    print('## 3) Rubric (how validity is determined)\n')
    print('- **VALID:** exact EAN match (checksum-valid) + no pack/spec contradiction')
    print('- **LIKELY VALID:** similarity >= 0.82 + >=3 shared anchor tokens + no contradiction (non-EAN path)')
    print('- **NEEDS REVIEW:** exact EAN but contradiction, or similarity >= 0.60 (>=2 anchors), or similarity >= 0.45 (>=2 anchors)')
    print('- **INVALID:** low similarity/anchors, especially with contradiction\n')

    print('| Label | Rows |')
    print('|:--|--:|')
    for lbl in ('VALID', 'LIKELY VALID', 'NEEDS REVIEW', 'INVALID'):
        print(f'| {lbl} | {label_dist.get(lbl,0)} |')
    print('\n---\n')

    print('## 4) Per-Report Evaluation\n')
    for rr in report_results:
        rp = rr['report']
        print(f"### `{rp}`\n")

        if rr['claimed']:
            interesting = {
                k: v
                for k, v in rr['claimed'].items()
                if any(s in k.lower() for s in ('total rows', 'verified', 'high likelihood', 'needs verification'))
            }
            if interesting:
                print('**Stated metrics (as parsed):**')
                for k, v in list(interesting.items())[:10]:
                    print(f'- {k}: {v}')

        print('\n**Parsed rows:**')
        print(f"- Total parsed table rows: **{rr['parsed_rows_total']}**")
        print(f"- Parsed recommended rows: **{rr['parsed_rows_recommended']}**")
        print(
            f"- Parsed recommended by verdict: VERIFIED {rr['rec_verdict_counts'].get('VERIFIED',0)}, "
            f"HIGH LIKELIHOOD {rr['rec_verdict_counts'].get('HIGH LIKELIHOOD',0)}, "
            f"NEEDS VERIFICATION {rr['rec_verdict_counts'].get('NEEDS VERIFICATION',0)}"
        )

        print('\n**Coverage vs PART3:**')
        print(f"- Unique ASINs covered (recommended): **{rr['unique_asin']}** / {baseline['unique_asin']}")
        print(f"- Unique (ASIN, SupplierEAN) keys mapped: **{rr['unique_key']}** / {baseline['unique_key_asin_sup_ean']}")
        print(f"- Recommended rows matched back to PART3: **{fmt_pct(rr['recommended_match_rate'])}**")

        print('\n**Validity rate (recommended, mapped to PART3):**')
        dist = rr['validity_dist']
        total = sum(dist.values()) or 1
        print(
            f"- VALID {dist.get('VALID',0)} ({dist.get('VALID',0)/total:.1%}), "
            f"LIKELY VALID {dist.get('LIKELY VALID',0)} ({dist.get('LIKELY VALID',0)/total:.1%}), "
            f"NEEDS REVIEW {dist.get('NEEDS REVIEW',0)} ({dist.get('NEEDS REVIEW',0)/total:.1%}), "
            f"INVALID {dist.get('INVALID',0)} ({dist.get('INVALID',0)/total:.1%})"
        )

        invalid_examples = [i for i in rr['matched'] if canon.loc[i, 'validity'] == 'INVALID'][:3]
        if invalid_examples:
            print('\n**Most concerning mismatch patterns (examples):**')
            for i in invalid_examples:
                r = canon.loc[i]
                meta = metas[i]
                print(
                    f"- ASIN {r['asin']} | SupplierEAN {r['supplier_ean'] or '-'} | AmazonEAN {r['amazon_ean'] or '-'} "
                    f"| sim={meta.similarity:.2f} | {meta.contradiction or 'no explicit pack/spec contradiction'}"
                )
                print(f"  - Supplier: {md_escape(r['supplier_title'])[:120]}")
                print(f"  - Amazon: {md_escape(r['amazon_title'])[:120]}")

        print('\n---\n')

    print('## 5) Scorecard Table\n')
    print('Weights: Validity 0.55, Completeness 0.25, Pack/Variant 0.15, Clarity 0.05.\n')
    print('| Report | Validity | Completeness | Pack/Variant | Clarity | Total |')
    print('|:--|--:|--:|--:|--:|--:|')
    for s in scores_sorted:
        print(
            f"| `{s['report']}` | {s['validity_score']:.3f} | {s['completeness_score']:.3f} | "
            f"{s['pack_variant_score']:.3f} | {s['clarity_score']:.3f} | **{s['total_score']:.3f}** |"
        )
    print('\n---\n')

    print('## 6) Winner Deep Dive: Strengths + Weaknesses\n')
    if not winner_info:
        print('(No winner computed.)\n')
    else:
        dist = winner_info['validity_dist']
        print(f"**Winner:** `{winner}`\n")
        print('**Strengths:**')
        print('- Higher total score driven by validity + high-impact coverage under the rubric.')
        print(f"- VALID {dist.get('VALID',0)} and LIKELY VALID {dist.get('LIKELY VALID',0)} among mapped recommendations.")
        print('\n**Weaknesses:**')
        print(f"- Contains {len(questionable)} mapped recommendations that are NEEDS REVIEW/INVALID under rubric.")
    print('\n---\n')

    print('## 7) Coverage & Missing Items\n')
    print('### Missing-from-winner vs PART3 (Top 10-25)\n')
    print('| ASIN | SupplierEAN | AmazonEAN | Sales | NetProfit | Rubric | Why (rubric) |')
    print('|:--|:--|:--|--:|--:|:--|:--|')
    for _, r in missing_top.head(10).iterrows():
        meta = metas[int(r.name)]
        why = meta.contradiction or f"low similarity (sim={meta.similarity:.2f}, anchors={meta.shared_tokens})"
        print(
            f"| {r['asin']} | {r['supplier_ean'] or '-'} | {r['amazon_ean'] or '-'} | {int(r['sales'])} | "
            f"{r['net_profit']:.2f} | {r['validity']} | {md_escape(why)} |"
        )

    print('\n### Missing-from-winner but present in other MDs (Top 10-25)\n')
    print('| ASIN | SupplierEAN | Sales | NetProfit | Present in reports |')
    print('|:--|:--|--:|--:|:--|')
    for _, r in missing_in_winner_but_in_others.head(10).iterrows():
        present = ', '.join(sorted(membership[int(r.name)]))
        print(f"| {r['asin']} | {r['supplier_ean'] or '-'} | {int(r['sales'])} | {r['net_profit']:.2f} | {md_escape(present)} |")

    print('\n### Questionable-in-winner items (Top 10-25)\n')
    print('| ASIN | SupplierEAN | AmazonEAN | Sales | NetProfit | Rubric | What to verify |')
    print('|:--|:--|:--|--:|--:|:--|:--|')
    for _, r in questionable.head(10).iterrows():
        meta = metas[int(r.name)]
        verify = meta.contradiction or f"title match weak (sim={meta.similarity:.2f}, anchors={meta.shared_tokens})"
        print(
            f"| {r['asin']} | {r['supplier_ean'] or '-'} | {r['amazon_ean'] or '-'} | {int(r['sales'])} | "
            f"{r['net_profit']:.2f} | {r['validity']} | {md_escape(verify)} |"
        )
    print('\n---\n')

    print('## 8) What to fix next (prioritized)\n')
    print('1. Enforce a **hard floor** for title-only matches (e.g., similarity < 0.45 => never recommended).')
    print('2. Make pack/variant parity mandatory for non-EAN rows (qty/spec mismatch => exclude or NEEDS REVIEW).')
    print('3. Standardize report keys as `(ASIN, SupplierEAN)` to avoid silent ASIN-level collapsing.')
    print('4. Standardize summary-count definitions so totals/recommended/audit counts reconcile from one filter set.')


if __name__ == '__main__':
    main()
