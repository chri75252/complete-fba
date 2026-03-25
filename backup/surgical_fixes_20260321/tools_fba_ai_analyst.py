#!/usr/bin/env python3
"""
FBA AI Analyst — Standalone LLM-powered report analysis.
Reads financial report CSVs, sends batches to configured LLM for analysis.

Does NOT import from or modify any existing workflow modules.

Usage:
    python tools/fba_ai_analyst.py <csv_path> [--batch-size 20] [--tiers T1,T2,T3]
"""

import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Import the filter module (standalone, no workflow deps)
sys.path.insert(0, str(Path(__file__).parent))
from fba_report_filter import classify_row, normalize_ean


def _get_llm_client():
    """
    Get LLM client. Checks ANALYST_LLM_PROVIDER first (analyst-specific),
    then falls back to CONTROL_PLANE_LLM_PROVIDER (chat UI setting).
    For opencode: uses https://opencode.ai/zen as base URL.
    """
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from control_plane.env_config import ensure_llm_env
        ensure_llm_env()
    except ImportError:
        pass

    # ANALYST_LLM_PROVIDER overrides the chat UI provider for analyst runs
    provider = (
        os.environ.get("ANALYST_LLM_PROVIDER")
        or os.environ.get("CONTROL_PLANE_LLM_PROVIDER", "")
    ).lower()

    if provider == "opencode":
        api_key = os.environ.get("OPENCODE_API_KEY", "")
        # For opencode: ALWAYS use OPENCODE_MODEL, never CONTROL_PLANE_LLM_MODEL
        model = os.environ.get("OPENCODE_MODEL") or "minimax-m2.5-free"
        # openai client appends /chat/completions, so base needs /v1
        base_url = "https://opencode.ai/zen/v1"
        if not api_key:
            print("ERROR: OPENCODE_API_KEY not set in environment")
            sys.exit(1)
        try:
            import openai
        except ImportError:
            print("ERROR: openai package not installed. Run: pip install openai")
            sys.exit(1)
        return openai.OpenAI(api_key=api_key, base_url=base_url), model

    if provider == "kimi":
        api_key = os.environ.get("KIMI_API_KEY", "")
        kimi_model = os.environ.get("KIMI_MODEL") or os.environ.get("CONTROL_PLANE_LLM_MODEL") or "kimi"
        base_url = os.environ.get("CONTROL_PLANE_LLM_BASE_URL")
        if not api_key:
            print("ERROR: KIMI_API_KEY not set in environment")
            sys.exit(1)
        try:
            import openai
        except ImportError:
            print("ERROR: openai package not installed. Run: pip install openai")
            sys.exit(1)
        return openai.OpenAI(api_key=api_key, base_url=base_url), kimi_model

    # Fallback: plain OpenAI
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print("ERROR: No LLM provider configured. Set ANALYST_LLM_PROVIDER or OPENAI_API_KEY")
        sys.exit(1)
    fallback_model = os.environ.get("CONTROL_PLANE_LLM_MODEL") or "gpt-4o"
    try:
        import openai
    except ImportError:
        print("ERROR: openai package not installed. Run: pip install openai")
        sys.exit(1)
    return openai.OpenAI(api_key=api_key), fallback_model


ANALYSIS_PROMPT_TEMPLATE = """You are a Principal E-Commerce Analyst specializing in Amazon FBA arbitrage.

Analyze the following batch of {row_count} product rows from a financial report. For each row, determine:

1. **Match Verdict**: Is this a TRUE match (same product) or FALSE POSITIVE (different products)?
2. **Evidence**: What specific title tokens, EAN data, or category clues support your verdict?
3. **Pack Size Check**: Are there pack size discrepancies (supplier singles vs Amazon multipacks)?
4. **Adjusted Profit**: If pack sizes differ, recalculate profit per unit.
5. **Final Category**: VERIFIED / HIGHLY LIKELY / NEEDS VERIFICATION / AUDITED OUT

Rules:
- Be skeptical: assume high ROI is a false positive until verified
- Check if SupplierTitle and AmazonTitle describe the SAME physical product
- EAN match alone is not sufficient if titles clearly describe different products
- Flag brand mismatches, category mismatches, and variant traps

Group results by verdict section. For each section, output a markdown table sorted by Sales desc.
Format: prices as \u00a3X.XX, ROI as X.X%, Sales as integer.

Sections (in order):
1. **VERIFIED** — Exact EAN match, recommended
2. **HIGH LIKELIHOOD** — Strong title/evidence match, recommended
3. **NEEDS VERIFICATION** — Moderate evidence, requires manual check
4. **AUDITED OUT** — False positives, excluded

Table columns (same for each section):
| Verdict | Confidence (0-100) | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice_incVAT | SellingPrice_incVAT | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit (approx) | Key Match Evidence | Key Risks / Notes |

After all sections, provide a summary paragraph with counts per verdict.

DATA:
{rows_csv}
"""


def _load_category_map() -> dict:
    """Build product URL -> category name map from all non-sandbox cached products files."""
    url_to_cat = {}
    try:
        project_root = Path(__file__).resolve().parents[1]
        cp_dir = project_root / "OUTPUTS" / "cached_products"
        if not cp_dir.exists():
            return url_to_cat
        candidates = sorted(
            [f for f in cp_dir.glob("*_products_cache.json") if "__sandbox__" not in f.name],
            key=lambda p: p.stat().st_mtime, reverse=True
        )
        if not candidates:
            candidates = sorted(cp_dir.glob("*_products_cache.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        for cand in candidates:
            data = json.loads(cand.read_text(encoding="utf-8"))
            for item in (data if isinstance(data, list) else []):
                url = item.get("url", "").rstrip("/")
                src = item.get("source_url", "")
                if url and src:
                    parts = [p for p in src.split("/") if p and "." not in p and "http" not in p and len(p) > 2]
                    url_to_cat[url] = parts[-1].replace("-", " ").title() if parts else "Other"
    except Exception:
        pass
    return url_to_cat


def load_and_classify(csv_path: str, tiers: list = None) -> list:
    """Load CSV, classify rows, filter to requested tiers."""
    if tiers is None:
        tiers = ["TIER_1_VERIFIED", "TIER_2_LIKELY", "TIER_3_NEEDS_REVIEW"]

    cat_map = _load_category_map()
    rows = []
    tier_counts = {}
    total_csv = 0
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            total_csv += 1
            row["_row_id"] = i
            classification = classify_row(row)
            row.update(classification)
            tier_counts[row["tier"]] = tier_counts.get(row["tier"], 0) + 1
            sup_url = (row.get("SupplierURL") or "").rstrip("/")
            row["Category"] = cat_map.get(sup_url, "Other")
            if row["tier"] in tiers:
                rows.append(row)

    rows.sort(key=lambda r: r.get("confidence_score", 0), reverse=True)

    print(f"  Tier breakdown ({total_csv} total rows):")
    for t in ["TIER_1_VERIFIED", "TIER_2_LIKELY", "TIER_3_NEEDS_REVIEW", "TIER_4_REJECTED"]:
        print(f"    {t}: {tier_counts.get(t, 0)}")
    print(f"  Rows passing filter ({', '.join(tiers)}): {len(rows)}")

    return rows


def rows_to_csv_string(rows: list, max_title_len: int = 60) -> str:
    """Convert rows to a compact CSV string for the LLM prompt."""
    lines = ["Row#,EAN,EAN_OnPage,ASIN,SupplierTitle,AmazonTitle,SupplierPrice_incVAT,SellingPrice_incVAT,NetProfit,ROI,Sales,Tier,Confidence,Category"]
    for row in rows:
        s_title = (row.get("SupplierTitle", ""))[:max_title_len]
        a_title = (row.get("AmazonTitle", ""))[:max_title_len]
        s_title = s_title.replace(",", ";")
        a_title = a_title.replace(",", ";")
        lines.append(
            f"{row.get('_row_id','')},{row.get('EAN','')},{row.get('EAN_OnPage','')},"
            f"{row.get('ASIN','')},{s_title},{a_title},"
            f"{row.get('SupplierPrice_incVAT','')},{row.get('SellingPrice_incVAT','')}," 
            f"{row.get('NetProfit','')},{row.get('ROI','')},{row.get('bought_in_past_month','')},{row.get('tier','')},{row.get('confidence_score','')}," 
            f"{row.get('Category','Other')}"
        )
    return "\n".join(lines)


def call_openai(prompt: str) -> str:
    """Call configured LLM provider with the analysis prompt."""
    client, model = _get_llm_client()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=4000,
        )
        if not response.choices:
            return "[ERROR] LLM returned no choices in response"
        return response.choices[0].message.content or "[ERROR] LLM returned empty/null content"
    except Exception as e:
        return f"[ERROR] LLM API call failed: {e}"


def analyze_report(
    csv_path: str,
    batch_size: int = 20,
    tiers: list = None,
    output_dir: str = None,
) -> None:
    """
    Main analysis pipeline:
    1. Load and classify rows
    2. Batch into groups of batch_size
    3. Send each batch to LLM
    4. Save results as markdown files
    """
    csv_path = Path(csv_path)
    if output_dir is None:
        _project_root = Path(__file__).resolve().parents[1]
        output_dir = _project_root / "OUTPUTS" / "CONTROL_PLANE" / "FINANCIAL_REPORTS"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create per-run subfolder
    run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = output_dir / f"run_{run_timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading and classifying rows from {csv_path.name}...")
    rows = load_and_classify(str(csv_path), tiers)
    print(f"  Found {len(rows)} rows in tiers: {tiers}")

    # Save run configuration for traceability
    run_config = {
        "csv_path": str(csv_path),
        "csv_filename": csv_path.name,
        "batch_size": batch_size,
        "tiers_requested": tiers,
        "total_qualifying_rows": len(rows),
        "output_dir": str(run_dir),
        "timestamp": datetime.now().isoformat(),
    }
    config_path = run_dir / "run_config.json"
    with open(config_path, "w", encoding="utf-8") as cf:
        json.dump(run_config, cf, indent=2)
    print(f"  Run config saved: {config_path}")

    if not rows:
        print("  No rows to analyze. Exiting.")
        return

    batches = [rows[i:i + batch_size] for i in range(0, len(rows), batch_size)]
    print(f"  Split into {len(batches)} batches of up to {batch_size} rows")

    all_results = []

    for batch_num, batch in enumerate(batches, start=1):
        print(f"\n  Processing batch {batch_num}/{len(batches)} ({len(batch)} rows)...")

        csv_string = rows_to_csv_string(batch)
        prompt = ANALYSIS_PROMPT_TEMPLATE.format(
            row_count=len(batch),
            rows_csv=csv_string,
        )

        try:
            result = call_openai(prompt)
            all_results.append(result)

            batch_path = run_dir / f"batch_{batch_num:03d}.md"
            with open(batch_path, "w", encoding="utf-8") as f:
                f.write(f"# FBA Analysis Batch {batch_num}\n")
                f.write(f"**Source:** {csv_path.name}\n")
                f.write(f"**Rows:** {batch[0].get('_row_id', '?')}-{batch[-1].get('_row_id', '?')}\n")
                f.write(f"**Tiers:** {tiers}\n")
                f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
                f.write(result)
            print(f"    Saved to {batch_path.name}")

        except Exception as e:
            print(f"    ERROR on batch {batch_num}: {e}")
            all_results.append(f"ERROR: {e}")

    combined_path = run_dir / "COMBINED_AI_ANALYSIS.md"
    with open(combined_path, "w", encoding="utf-8") as f:
        f.write(f"# FBA AI Analysis Report\n")
        f.write(f"**Source:** {csv_path.name}\n")
        f.write(f"**Total Rows Analyzed:** {len(rows)}\n")
        f.write(f"**Tiers Included:** {tiers}\n")
        _, model_name = _get_llm_client()
        f.write(f"**Model:** {model_name}\n")
        f.write(f"**Generated:** {datetime.now().isoformat()}\n\n---\n\n")
        for i, result in enumerate(all_results, start=1):
            f.write(f"## Batch {i}\n\n{result}\n\n---\n\n")
    print(f"\n  Combined report: {combined_path}")

    # Update run_config with completion info and errors
    run_config["completed_at"] = datetime.now().isoformat()
    run_config["batches_processed"] = len(batches)
    run_config["errors"] = [r for r in all_results if "[ERROR]" in str(r)]
    with open(config_path, "w", encoding="utf-8") as cf:
        json.dump(run_config, cf, indent=2)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/fba_ai_analyst.py <csv_path> [--batch-size 20] [--tiers T1,T2,T3]")
        sys.exit(1)

    csv_file = sys.argv[1]
    batch_sz = 20
    tier_list = ["TIER_1_VERIFIED", "TIER_2_LIKELY", "TIER_3_NEEDS_REVIEW"]

    if "--batch-size" in sys.argv:
        idx = sys.argv.index("--batch-size")
        if idx + 1 < len(sys.argv):
            batch_sz = int(sys.argv[idx + 1])

    if "--tiers" in sys.argv:
        idx = sys.argv.index("--tiers")
        if idx + 1 < len(sys.argv):
            tier_list = [f"TIER_{t.strip().upper()}" if not t.startswith("TIER_") else t.strip().upper()
                         for t in sys.argv[idx + 1].split(",")]

    print(f"\nFBA AI Analyst")
    print(f"CSV: {csv_file}")
    print(f"Batch size: {batch_sz}")
    print(f"Tiers: {tier_list}")
    out_dir = None
    if "--output-dir" in sys.argv:
        idx = sys.argv.index("--output-dir")
        if idx + 1 < len(sys.argv):
            out_dir = sys.argv[idx + 1]

    print(f"{'=' * 60}")

    analyze_report(csv_file, batch_size=batch_sz, tiers=tier_list, output_dir=out_dir)
