"""
Output Generation Tools for FBA Agent.

Generates PhaseA report, coverage ledger, evidence files, and run artifacts.
"""

import json
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from ..models.schemas import RowDecisionRecord, RunSummary, ValidationResult, Bucket


def render_phasea_report(
    records: List[RowDecisionRecord],
    metadata: Dict[str, Any],
    validation_results: List[ValidationResult] = None
) -> str:
    """
    Render the PhaseA Manual Report in Markdown format.
    
    Follows exact structure from Main.txt with fixed-width tables.
    
    Args:
        records: List of decision records
        metadata: Run metadata (input_file, supplier, etc.)
        validation_results: Optional validation results
        
    Returns:
        Markdown report string
    """
    # Group records by bucket
    verified = [r for r in records if r.bucket == Bucket.VERIFIED.value]
    highly_likely = [r for r in records if r.bucket == Bucket.HIGHLY_LIKELY.value]
    needs_ver = [r for r in records if r.bucket == Bucket.NEEDS_VERIFICATION.value]
    filtered = [r for r in records if r.bucket == Bucket.FILTERED_OUT.value]
    
    # Split verified/highly_likely into recommended vs filtered
    verified_rec = [r for r in verified if r.adjusted_profit > 0 and r.filter_reason == "-"]
    verified_filt = [r for r in verified if r.adjusted_profit <= 0 or r.filter_reason != "-"]
    highly_rec = [r for r in highly_likely if r.adjusted_profit > 0 and r.filter_reason == "-"]
    highly_filt = [r for r in highly_likely if r.adjusted_profit <= 0 or r.filter_reason != "-"]
    
    # Build report
    lines = []
    
    # Header
    lines.append("# PHASEA MANUAL REPORT")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Input File:** {metadata.get('input_file', 'Unknown')}")
    lines.append(f"**Supplier:** {metadata.get('supplier_id', 'Unknown')}")
    lines.append("")
    
    # Summary counts
    lines.append("## Summary Counts")
    lines.append("")
    lines.append(f"- VERIFIED — RECOMMENDED: {len(verified_rec)}")
    lines.append(f"- VERIFIED — FILTERED OUT / EXCLUDED: {len(verified_filt)}")
    lines.append(f"- HIGHLY LIKELY — RECOMMENDED: {len(highly_rec)}")
    lines.append(f"- HIGHLY LIKELY — FILTERED OUT / EXCLUDED: {len(highly_filt)}")
    lines.append(f"- NEEDS VERIFICATION: {len(needs_ver)}")
    lines.append(f"- FILTERED OUT: {len(filtered)}")
    lines.append(f"- TOTAL ANALYZED: {len(records)}")
    lines.append("")
    lines.append("This report applies v4.1 Deterministic Agent Analysis:")
    lines.append("- Scores computed by deterministic code formulas")
    lines.append("- HIGHLY LIKELY requires Brand + Product type match with positive profit")
    lines.append("- NEEDS VERIFICATION is selective: only items where 1-2 confirmable details would upgrade")
    lines.append("- FILTERED OUT contains CONFIRMED matches that are unprofitable (for audit)")
    lines.append("")
    
    # Validation results
    if validation_results:
        lines.append("## Validation Gates")
        lines.append("")
        for vr in validation_results:
            status = "✅ PASSED" if vr.passed else "❌ FAILED"
            lines.append(f"- {vr.gate_name}: {status}")
            if vr.error:
                lines.append(f"  - Error: {vr.error}")
        lines.append("")
    
    # VERIFIED — RECOMMENDED
    lines.append(f"## VERIFIED — RECOMMENDED (count={len(verified_rec)})")
    lines.append("")
    if verified_rec:
        lines.append(_render_table(verified_rec))
    else:
        lines.append("*No verified recommended products.*")
    lines.append("")
    
    # VERIFIED — FILTERED OUT
    if verified_filt:
        lines.append(f"## VERIFIED — FILTERED OUT / EXCLUDED (count={len(verified_filt)})")
        lines.append("")
        lines.append(_render_table(verified_filt))
        lines.append("")
    
    # HIGHLY LIKELY — RECOMMENDED
    lines.append(f"## HIGHLY LIKELY — RECOMMENDED (count={len(highly_rec)})")
    lines.append("")
    if highly_rec:
        lines.append(_render_table(highly_rec))
    else:
        lines.append("*No highly likely recommended products.*")
    lines.append("")
    
    # HIGHLY LIKELY — FILTERED OUT
    if highly_filt:
        lines.append(f"## HIGHLY LIKELY — FILTERED OUT / EXCLUDED (count={len(highly_filt)})")
        lines.append("")
        lines.append(_render_table(highly_filt))
        lines.append("")
    
    # NEEDS VERIFICATION
    lines.append(f"## NEEDS VERIFICATION (count={len(needs_ver)})")
    lines.append("")
    if needs_ver:
        lines.append(_render_table(needs_ver))
    else:
        lines.append("*No products need verification.*")
    lines.append("")
    
    # FILTERED OUT
    if filtered:
        lines.append(f"## FILTERED OUT (count={len(filtered)})")
        lines.append("")
        lines.append(_render_table(filtered[:50]))  # Limit for readability
        if len(filtered) > 50:
            lines.append(f"\n*... and {len(filtered) - 50} more filtered items (see coverage_ledger.csv for full list)*")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Report generated by FBA Product Analysis Agent v1.0*")
    lines.append(f"*Timestamp: {datetime.now().isoformat()}*")
    
    return "\n".join(lines)


def _render_table(records: List[RowDecisionRecord]) -> str:
    """Render a fixed-width Markdown table."""
    if not records:
        return "*No items*"
    
    # Define columns and headers
    headers = [
        "RowID", "Verdict", "Conf", "SupplierTitle", "AmazonTitle", 
        "Supplier EAN", "Amazon EAN", "ASIN", "SupPrice", "SellPrice",
        "NetProfit", "ROI", "Sales", "Pack Verdict", "Adj Profit",
        "Key Match Evidence", "Filter Reason"
    ]
    
    # Build rows
    rows = []
    for r in records:
        raw = r.raw_row
        rows.append([
            str(r.row_id),
            r.bucket[:10],
            str(r.confidence),
            _sanitize_cell(r.supplier_attributes.raw_title, 35),
            _sanitize_cell(r.amazon_attributes.raw_title, 40),
            _sanitize_cell(str(raw.get('EAN_clean', raw.get('EAN', '-'))), 15),
            _sanitize_cell(str(raw.get('EAN_OnPage_clean', raw.get('EAN_OnPage', '-'))), 15),
            _sanitize_cell(str(raw.get('ASIN', '-')), 12),
            f"£{raw.get('SupplierPrice_incVAT', 0):.2f}"[:8],
            f"£{raw.get('SellingPrice_incVAT', 0):.2f}"[:8],
            f"£{raw.get('NetProfit', 0):.2f}"[:8],
            f"{raw.get('ROI', 0):.1f}%"[:7],
            str(int(raw.get('sales', 0)))[:5],
            _sanitize_cell(r.pack_verdict, 20),
            f"£{r.adjusted_profit:.2f}"[:8],
            _sanitize_cell(r.key_match_evidence, 30),
            _sanitize_cell(r.filter_reason, 25)
        ])
    
    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))
    
    # Build table
    lines = ["```text"]
    
    # Header row
    header_line = "| " + " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers)) + " |"
    lines.append(header_line)
    
    # Separator row
    sep_line = "|" + "|".join("-" * (w + 2) for w in widths) + "|"
    lines.append(sep_line)
    
    # Data rows
    for row in rows:
        data_line = "| " + " | ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)) + " |"
        lines.append(data_line)
    
    lines.append("```")
    
    return "\n".join(lines)


def _sanitize_cell(value: str, max_len: int = 50) -> str:
    """Sanitize a cell value for table display."""
    if not value:
        return "-"
    
    # Replace pipe characters (would break table)
    value = str(value).replace("|", "/")
    
    # Remove newlines
    value = value.replace("\n", " ").replace("\r", " ")
    
    # Truncate if too long
    if len(value) > max_len:
        value = value[:max_len-3] + "..."
    
    return value


def write_run_artifacts(
    run_id: str,
    records: List[RowDecisionRecord],
    report_md: str,
    summary: RunSummary,
    output_dir: Path
) -> Dict[str, Path]:
    """
    Write all run artifacts to disk.
    
    Creates:
    - PHASEA_MANUAL_REPORT_YYYYMMDD.md
    - coverage_ledger.csv
    - evidence.jsonl
    - run_summary.json
    
    Args:
        run_id: Unique run identifier
        records: List of decision records
        report_md: Rendered Markdown report
        summary: Run summary
        output_dir: Base output directory
        
    Returns:
        Dict mapping artifact name to file path
    """
    # Create run directory
    run_dir = output_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    
    paths = {}
    
    # Write report
    report_path = run_dir / f"PHASEA_MANUAL_REPORT_{datetime.now().strftime('%Y%m%d')}.md"
    report_path.write_text(report_md, encoding='utf-8')
    paths['report'] = report_path
    
    # Write coverage ledger
    ledger_path = run_dir / "coverage_ledger.csv"
    with open(ledger_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'row_id', 'bucket', 'confidence', 'pack_ratio', 'adjusted_profit',
            'is_exact_ean_strict', 'brand_match', 'product_match', 'trap_flags', 'evidence_pointer'
        ])
        writer.writeheader()
        for r in records:
            writer.writerow(r.to_ledger_row())
    paths['ledger'] = ledger_path
    
    # Write evidence JSONL
    evidence_path = run_dir / "evidence.jsonl"
    with open(evidence_path, 'w', encoding='utf-8') as f:
        for r in records:
            f.write(json.dumps(r.to_dict()) + "\n")
    paths['evidence'] = evidence_path
    
    # Write run summary
    summary_path = run_dir / "run_summary.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary.to_dict(), f, indent=2)
    paths['summary'] = summary_path
    
    return paths


def build_run_summary(
    run_id: str,
    input_file: str,
    supplier_id: str,
    records: List[RowDecisionRecord],
    validation_results: List[ValidationResult],
    timing_ms: int = 0
) -> RunSummary:
    """
    Build a run summary from analysis results.
    
    Args:
        run_id: Unique run identifier
        input_file: Path to input file
        supplier_id: Supplier identifier
        records: List of decision records
        validation_results: Validation results
        timing_ms: Processing time in milliseconds
        
    Returns:
        RunSummary
    """
    from collections import Counter
    
    bucket_counts = Counter(r.bucket for r in records)
    
    return RunSummary(
        run_id=run_id,
        input_file=input_file,
        supplier_id=supplier_id,
        row_count=len(records),
        bucket_counts=dict(bucket_counts),
        validation_passed=all(vr.passed for vr in validation_results),
        validation_details={vr.gate_name: vr.to_dict() for vr in validation_results},
        timing_ms=timing_ms
    )
