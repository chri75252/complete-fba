#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Result Summarizer - Full Implementation

Generates actionable summaries from workflow output files using file-grounded approach.

Features:
- Read artifacts from OUTPUTS/ directories
- Calculate key metrics (processed, matched, profitable)
- Identify top opportunities by profit/ROI
- Detect anomalies (missing EANs, low match rate, etc.)
- Generate summary.md and curated.csv

Session 4 Implementation
"""

import json
import csv
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class ResultSummarizer:
    """
    Generates actionable summaries from workflow output files.
    
    Full implementation:
    - Read artifacts from OUTPUTS/ directories
    - Calculate key metrics
    - Identify top opportunities
    - Detect anomalies
    - Generate summary.md and curated.csv
    """
    
    def __init__(self, workspace_root: str = "."):
        """
        Initialize result summarizer.
        
        Args:
            workspace_root: Root directory of the workspace
        """
        self.workspace_root = Path(workspace_root)
        self.outputs_dir = self.workspace_root / "OUTPUTS"
        self.results_dir = self.outputs_dir / "AI_SETUP_RESULTS"
        logger.info(f"ResultSummarizer initialized with workspace: {workspace_root}")
    
    def summarize_run(self, supplier_id: str, run_timestamp: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate comprehensive summary from workflow artifacts.
        
        Args:
            supplier_id: Supplier identifier
            run_timestamp: Optional timestamp for specific run (uses latest if None)
            
        Returns:
            Summary dict with metrics, opportunities, and anomalies
        """
        logger.info(f"Summarizing run for: {supplier_id}")
        
        # Read all artifacts
        artifacts = self.read_artifacts(supplier_id)
        
        # Calculate metrics
        metrics = self.calculate_metrics(artifacts)
        
        # Identify top opportunities
        top_opportunities = self.identify_top_opportunities(artifacts["csv_rows"], n=20)
        
        # Detect anomalies
        anomalies = self.detect_anomalies(artifacts)
        
        summary = {
            "supplier_id": supplier_id,
            "timestamp": run_timestamp or datetime.now().isoformat(),
            "metrics": metrics,
            "top_opportunities": top_opportunities,
            "anomalies": anomalies,
            "artifacts_found": {
                "cache_files": len(artifacts["cache_files"]),
                "linking_entries": len(artifacts["linking_entries"]),
                "csv_rows": len(artifacts["csv_rows"]),
                "state_exists": bool(artifacts["state"])
            }
        }
        
        logger.info(f"Summary generated: {metrics['products_matched']} matched, "
                   f"{metrics['profitable_products']} profitable")
        
        return summary
    
    def read_artifacts(self, supplier_id: str) -> Dict[str, Any]:
        """
        Read workflow output artifacts from OUTPUTS/ directories.
        
        Args:
            supplier_id: Supplier identifier
            
        Returns:
            Dict containing all artifact data
        """
        artifacts = {
            "cache_files": [],
            "linking_entries": [],
            "csv_rows": [],
            "state": {}
        }
        
        # Read Amazon cache files
        amazon_cache_dir = self.outputs_dir / "FBA_ANALYSIS" / "amazon_cache"
        if amazon_cache_dir.exists():
            for cache_file in amazon_cache_dir.glob("amazon_*.json"):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        artifacts["cache_files"].append({
                            "file": cache_file.name,
                            "data": data
                        })
                except Exception as e:
                    logger.warning(f"Failed to read cache file {cache_file}: {e}")
        
        # Read linking map
        supplier_name = supplier_id.replace("-", "_")
        linking_map_path = (self.outputs_dir / "FBA_ANALYSIS" / "linking_maps" / 
                           supplier_name / "linking_map.json")
        
        if linking_map_path.exists():
            try:
                with open(linking_map_path, 'r', encoding='utf-8') as f:
                    linking_map = json.load(f)
                    # linking_map is a dict with EAN keys
                    for ean, entry in linking_map.items():
                        artifacts["linking_entries"].append({
                            "ean": ean,
                            **entry
                        })
            except Exception as e:
                logger.warning(f"Failed to read linking map: {e}")
        
        # Read latest financial CSV
        financial_reports_dir = self.outputs_dir / "FBA_ANALYSIS" / "financial_reports"
        if financial_reports_dir.exists():
            csv_files = sorted(financial_reports_dir.glob("*.csv"), 
                             key=lambda p: p.stat().st_mtime, 
                             reverse=True)
            
            if csv_files:
                latest_csv = csv_files[0]
                try:
                    with open(latest_csv, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        artifacts["csv_rows"] = list(reader)
                    logger.info(f"Read {len(artifacts['csv_rows'])} rows from {latest_csv.name}")
                except Exception as e:
                    logger.warning(f"Failed to read financial CSV: {e}")
        
        # Read processing state
        state_filename = f"{supplier_id.replace('-', '_')}_processing_state.json"
        state_path = self.outputs_dir / "CACHE" / "processing_states" / state_filename
        
        if state_path.exists():
            try:
                with open(state_path, 'r', encoding='utf-8') as f:
                    artifacts["state"] = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to read processing state: {e}")
        
        return artifacts
    
    def calculate_metrics(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate key metrics from artifacts.
        
        Args:
            artifacts: Artifact data from read_artifacts()
            
        Returns:
            Metrics dict
        """
        state = artifacts.get("state", {})
        csv_rows = artifacts.get("csv_rows", [])
        linking_entries = artifacts.get("linking_entries", [])
        
        # Products processed (from state)
        supplier_products = state.get("supplier_products_completed", 0)
        amazon_products = state.get("amazon_products_completed", 0)
        products_processed = supplier_products + amazon_products
        
        # Products matched (linking map entries with confidence > 0)
        products_matched = sum(1 for entry in linking_entries 
                              if entry.get("confidence", 0) > 0)
        
        # Profitable products (from CSV)
        profitable = []
        for row in csv_rows:
            try:
                net_profit = float(row.get("net_profit_gbp", 0))
                roi_pct = float(row.get("roi_pct", 0))
                margin_pct = float(row.get("margin_pct", 0))
                
                # Criteria: profit ≥ £2, ROI ≥ 30%, margin ≥ 25%
                if net_profit >= 2.0 and roi_pct >= 30.0 and margin_pct >= 25.0:
                    profitable.append(row)
            except (ValueError, KeyError):
                continue
        
        # Calculate totals
        total_profit = sum(float(row.get("net_profit_gbp", 0)) for row in profitable)
        avg_roi = (sum(float(row.get("roi_pct", 0)) for row in profitable) / len(profitable) 
                   if profitable else 0.0)
        avg_margin = (sum(float(row.get("margin_pct", 0)) for row in profitable) / len(profitable)
                     if profitable else 0.0)
        
        metrics = {
            "products_processed": products_processed,
            "products_matched": products_matched,
            "profitable_products": len(profitable),
            "total_potential_profit": round(total_profit, 2),
            "average_roi": round(avg_roi, 1),
            "average_margin": round(avg_margin, 1),
            "match_rate_pct": round((products_matched / products_processed * 100) 
                                   if products_processed > 0 else 0, 1)
        }
        
        return metrics
    
    def identify_top_opportunities(self, csv_rows: List[Dict[str, Any]], n: int = 20) -> List[Dict[str, Any]]:
        """
        Identify top N profitable opportunities.
        
        Args:
            csv_rows: Financial data rows
            n: Number of top opportunities to return
            
        Returns:
            List of top opportunities sorted by profit DESC
        """
        opportunities = []
        
        for row in csv_rows:
            try:
                net_profit = float(row.get("net_profit_gbp", 0))
                roi_pct = float(row.get("roi_pct", 0))
                margin_pct = float(row.get("margin_pct", 0))
                
                # Only include profitable products
                if net_profit >= 2.0 and roi_pct >= 30.0:
                    opportunities.append({
                        "supplier_title": row.get("supplier_title", "Unknown"),
                        "amazon_asin": row.get("amazon_asin", ""),
                        "amazon_title": row.get("amazon_title", ""),
                        "supplier_price_gbp": float(row.get("supplier_price_gbp", 0)),
                        "amazon_price_gbp": float(row.get("amazon_price_gbp", 0)),
                        "net_profit_gbp": net_profit,
                        "roi_pct": roi_pct,
                        "margin_pct": margin_pct,
                        "bsr_main": row.get("bsr_main", "N/A"),
                        "sellers_count": row.get("sellers_count", "N/A")
                    })
            except (ValueError, KeyError):
                continue
        
        # Sort by: (1) net_profit DESC, (2) roi DESC, (3) margin DESC
        opportunities.sort(
            key=lambda x: (x["net_profit_gbp"], x["roi_pct"], x["margin_pct"]),
            reverse=True
        )
        
        return opportunities[:n]
    
    def detect_anomalies(self, artifacts: Dict[str, Any]) -> List[str]:
        """
        Detect data quality issues and anomalies.
        
        Args:
            artifacts: Artifact data
            
        Returns:
            List of anomaly descriptions
        """
        anomalies = []
        
        csv_rows = artifacts.get("csv_rows", [])
        linking_entries = artifacts.get("linking_entries", [])
        state = artifacts.get("state", {})
        
        if not csv_rows and not linking_entries:
            anomalies.append("No data artifacts found - workflow may not have run")
            return anomalies
        
        # Missing EANs (linking entries with empty EAN)
        missing_eans = sum(1 for entry in linking_entries 
                          if not entry.get("ean") or entry.get("ean") == "")
        
        if linking_entries and missing_eans / len(linking_entries) > 0.3:
            anomalies.append(
                f"{missing_eans}/{len(linking_entries)} products missing EAN "
                f"({missing_eans/len(linking_entries)*100:.1f}%) - title matching used"
            )
        
        # Low match rate
        products_processed = state.get("supplier_products_completed", 0)
        products_matched = sum(1 for entry in linking_entries 
                              if entry.get("confidence", 0) > 0)
        
        if products_processed > 0 and products_matched / products_processed < 0.5:
            anomalies.append(
                f"Low match rate: {products_matched}/{products_processed} "
                f"({products_matched/products_processed*100:.1f}%) - check EAN availability"
            )
        
        # Price mismatches (supplier > Amazon)
        price_mismatches = []
        for row in csv_rows:
            try:
                supplier_price = float(row.get("supplier_price_gbp", 0))
                amazon_price = float(row.get("amazon_price_gbp", 0))
                
                if supplier_price > amazon_price:
                    price_mismatches.append(row.get("supplier_title", "Unknown"))
            except (ValueError, KeyError):
                continue
        
        if price_mismatches:
            anomalies.append(
                f"{len(price_mismatches)} products with supplier price > Amazon price "
                f"(impossible profit) - review: {', '.join(price_mismatches[:3])}"
            )
        
        # High rejection rate
        if csv_rows:
            # Assume rejected if profit < 0 or ROI < 0
            rejected = sum(1 for row in csv_rows 
                          if float(row.get("net_profit_gbp", 0)) < 0 
                          or float(row.get("roi_pct", 0)) < 0)
            
            if rejected / len(csv_rows) > 0.4:
                anomalies.append(
                    f"High rejection rate: {rejected}/{len(csv_rows)} "
                    f"({rejected/len(csv_rows)*100:.1f}%) - adjust profitability thresholds"
                )
        
        return anomalies
    
    def generate_summary_markdown(self, summary_dict: Dict[str, Any], output_path: str) -> None:
        """
        Generate summary.md report.
        
        Args:
            summary_dict: Summary data from summarize_run()
            output_path: Path for output file
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # Header
            f.write(f"# FBA Analysis Summary - {summary_dict['supplier_id']}\n\n")
            f.write(f"**Generated:** {summary_dict['timestamp']}\n\n")
            f.write("---\n\n")
            
            # Metrics
            f.write("## Key Metrics\n\n")
            metrics = summary_dict['metrics']
            f.write(f"- **Products Processed:** {metrics['products_processed']}\n")
            f.write(f"- **Products Matched:** {metrics['products_matched']} "
                   f"({metrics['match_rate_pct']}%)\n")
            f.write(f"- **Profitable Products:** {metrics['profitable_products']}\n")
            f.write(f"- **Total Potential Profit:** £{metrics['total_potential_profit']:.2f}\n")
            f.write(f"- **Average ROI:** {metrics['average_roi']:.1f}%\n")
            f.write(f"- **Average Margin:** {metrics['average_margin']:.1f}%\n\n")
            
            # Top opportunities
            f.write("## Top 20 Opportunities\n\n")
            top = summary_dict.get('top_opportunities', [])
            
            if top:
                f.write("| Rank | Product | Profit | ROI | Margin | ASIN |\n")
                f.write("|------|---------|--------|-----|--------|------|\n")
                
                for idx, opp in enumerate(top[:20], 1):
                    title = opp['supplier_title'][:50]  # Truncate long titles
                    f.write(f"| {idx} | {title} | £{opp['net_profit_gbp']:.2f} | "
                           f"{opp['roi_pct']:.0f}% | {opp['margin_pct']:.0f}% | "
                           f"{opp['amazon_asin']} |\n")
            else:
                f.write("*No profitable opportunities found.*\n")
            
            f.write("\n")
            
            # Anomalies
            f.write("## Anomalies Detected\n\n")
            anomalies = summary_dict.get('anomalies', [])
            
            if anomalies:
                for anomaly in anomalies:
                    f.write(f"- ⚠️ {anomaly}\n")
            else:
                f.write("*No anomalies detected.*\n")
            
            f.write("\n---\n\n")
            f.write("*Generated by AI-Enhanced FBA Setup System*\n")
        
        logger.info(f"✅ Summary markdown written to: {output_file}")
    
    def export_curated_csv(self, csv_rows: List[Dict[str, Any]], output_path: str) -> None:
        """
        Export curated CSV with profitable products only.
        
        Args:
            csv_rows: All financial data rows
            output_path: Path for output file
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Filter to profitable products
        profitable = []
        for row in csv_rows:
            try:
                net_profit = float(row.get("net_profit_gbp", 0))
                roi_pct = float(row.get("roi_pct", 0))
                margin_pct = float(row.get("margin_pct", 0))
                
                if net_profit >= 2.0 and roi_pct >= 30.0 and margin_pct >= 25.0:
                    profitable.append(row)
            except (ValueError, KeyError):
                continue
        
        # Sort by profit DESC
        profitable.sort(key=lambda x: float(x.get("net_profit_gbp", 0)), reverse=True)
        
        if profitable:
            # Write CSV
            fieldnames = profitable[0].keys() if profitable else []
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(profitable)
            
            logger.info(f"✅ Curated CSV written to: {output_file} ({len(profitable)} products)")
        else:
            logger.warning("No profitable products to export")


if __name__ == "__main__":
    # Test implementation
    logging.basicConfig(level=logging.INFO)
    
    summarizer = ResultSummarizer()
    
    print("ResultSummarizer Test")
    print("=" * 60)
    print()
    print("To generate summary, call:")
    print("  summary = summarizer.summarize_run('poundwholesale-co-uk')")
    print("  summarizer.generate_summary_markdown(summary, 'OUTPUTS/AI_SETUP_RESULTS/.../summary.md')")
    print("  summarizer.export_curated_csv(artifacts['csv_rows'], 'OUTPUTS/AI_SETUP_RESULTS/.../curated.csv')")
    print()
