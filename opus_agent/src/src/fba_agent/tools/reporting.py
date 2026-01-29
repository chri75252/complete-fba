import pandas as pd
import json
from typing import List, Dict, Any
from pathlib import Path
from ..config import TABLE_SCHEMA

class ReportGenerator:
    """
    Generates the Phase A Markdown Report and Run Artifacts.
    """
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_artifacts(self, ledger: pd.DataFrame, evidence: List[Dict], metadata: Dict):
        """
        Main runner: writes CSV, JSONL, and MD.
        """
        # 1. Write Ledger CSV
        ledger.to_csv(self.output_dir / "coverage_ledger.csv", index=False)
        
        # 2. Write Evidence JSONL
        with open(self.output_dir / "evidence.jsonl", "w", encoding="utf-8") as f:
            for item in evidence:
                f.write(json.dumps(item) + "\n")
                
        # 3. Write Summary JSON
        with open(self.output_dir / "run_summary.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
            
        # 4. Generate Markdown Report
        md_content = self._render_markdown(ledger, metadata)
        with open(self.output_dir / f"CODEX_MANUAL_REPORT_{metadata.get('run_timestamp')}.md", "w", encoding="utf-8") as f:
            f.write(md_content)

    def _render_markdown(self, ledger: pd.DataFrame, metadata: Dict) -> str:
        """
        Renders the full report string.
        """
        lines = []
        lines.append(f"# FBA MANUAL ANALYSIS REPORT - {metadata.get('run_date')}")
        lines.append(f"**Run ID:** {metadata.get('run_id')}")
        lines.append(f"**Supplier:** {metadata.get('supplier_id')}")
        lines.append("")
        
        # Summary Section
        lines.append("## Executive Summary")
        counts = ledger["Verdict"].value_counts().to_dict()
        lines.append("| Category | Count |")
        lines.append("|---|---|")
        for bucket in ["VERIFIED", "HIGHLY_LIKELY", "NEEDS_VERIFICATION", "FILTERED_OUT", "UNRELATED"]:
            lines.append(f"| {bucket} | {counts.get(bucket, 0)} |")
        lines.append("")
        
        # Tables Loop
        # We assume the ledger has columns matching TABLE_SCHEMA or we need to map them.
        # The Analyzer populates them correctly.
        
        buckets_to_print = ["VERIFIED", "HIGHLY_LIKELY", "NEEDS_VERIFICATION", "FILTERED_OUT"]
        
        for bucket in buckets_to_print:
            subset = ledger[ledger["Verdict"] == bucket]
            if subset.empty:
                continue
                
            lines.append(f"## {bucket}")
            lines.append("```text")
            
            # Prepare data for table
            # We strictly need to follow TABLE_SCHEMA columns.
            # Convert subset to list of dicts
            records = subset.to_dict(orient='records')
            
            # Format Fixed Width
            table_str = self._format_fixed_width_table(records, TABLE_SCHEMA)
            lines.append(table_str)
            lines.append("```")
            lines.append("")
            
        return "\n".join(lines)

    def _format_fixed_width_table(self, data: List[Dict], headers: List[str]) -> str:
        """
        Creates a fixed-width ASCII table.
        """
        if not data:
            return ""
            
        # 1. Determine Widths
        widths = {h: len(h) for h in headers}
        
        formatted_rows = []
        for row in data:
            cleaned_row = {}
            for h in headers:
                val = str(row.get(h, ""))
                # Sanitize pipes and newlines
                val = val.replace("|", "/").replace("\n", " ")
                cleaned_row[h] = val
                widths[h] = max(widths[h], len(val))
            formatted_rows.append(cleaned_row)
            
        # 2. Build Header
        header_line = "| " + " | ".join(h.ljust(widths[h]) for h in headers) + " |"
        separator = "|-" + "-|-".join("-" * widths[h] for h in headers) + "-|"
        
        # 3. Build Rows
        lines = [header_line, separator]
        for row in formatted_rows:
            line = "| " + " | ".join(row[h].ljust(widths[h]) for h in headers) + " |"
            lines.append(line)
            
        return "\n".join(lines)
