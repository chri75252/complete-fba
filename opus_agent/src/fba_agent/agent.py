"""
FBA Product Analysis Agent.

Main agent orchestrator that coordinates the analysis pipeline.
"""

import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

from .config import Config, SupplierCalibration
from .models.schemas import RowDecisionRecord, RunSummary, ValidationResult
from .tools.data_loading import load_report, normalize_columns, sample_rows
from .tools.categorization import analyze_all_rows
from .tools.validation import validate_ledger, check_all_gates, get_gate_summary
from .tools.output import render_phasea_report, write_run_artifacts, build_run_summary


class FBAAgent:
    """
    Main FBA Product Analysis Agent.
    
    Orchestrates the deterministic pipeline:
    1. Load and normalize data
    2. Run preflight calibration (optional)
    3. Analyze all rows
    4. Validate results
    5. Generate output artifacts
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the agent.
        
        Args:
            config: Optional Config object. If not provided, loads from environment.
        """
        self.config = config or Config()
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration is complete."""
        # For now, just check that config exists
        # API key validation happens only when LLM is actually used
        pass
    
    def analyze(
        self,
        input_path: str,
        supplier_id: Optional[str] = None,
        output_dir: Optional[str] = None,
        skip_browser: bool = True,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Run full analysis on an input file.
        
        Args:
            input_path: Path to input file (CSV/XLSX)
            supplier_id: Optional supplier identifier (auto-detected from filename if not provided)
            output_dir: Optional output directory (uses config default if not provided)
            skip_browser: Skip Phase 5 browser verification (default True per PRD)
            verbose: Enable verbose logging
            
        Returns:
            Dict containing run results and artifact paths
        """
        start_time = time.time()
        
        # Generate run ID
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Auto-detect supplier ID from filename if not provided
        if not supplier_id:
            supplier_id = self._extract_supplier_id(input_path)
        
        # Set output directory
        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = self.config.default_output_dir
        
        if verbose:
            print(f"[FBA Agent] Starting analysis")
            print(f"  Run ID: {run_id}")
            print(f"  Input: {input_path}")
            print(f"  Supplier: {supplier_id}")
            print(f"  Output: {output_path}")
        
        # Step 1: Load and normalize data
        if verbose:
            print("[FBA Agent] Step 1: Loading data...")
        
        df, schema_info = load_report(input_path)
        df = normalize_columns(df, schema_info)
        
        if verbose:
            print(f"  Loaded {len(df)} rows")
            print(f"  Columns: {schema_info.detected_columns[:5]}...")
        
        # Step 2: Run preflight calibration (optional)
        # For MVP, we use default calibration
        calibration_config = self._get_calibration(supplier_id, df)
        
        # Step 3: Analyze all rows
        if verbose:
            print("[FBA Agent] Step 3: Analyzing rows...")
        
        def progress_callback(current, total):
            if verbose:
                print(f"  Progress: {current}/{total} rows")
        
        records = analyze_all_rows(df, calibration_config, progress_callback if verbose else None)
        
        if verbose:
            print(f"  Analyzed {len(records)} rows")
        
        # Step 4: Validate results
        if verbose:
            print("[FBA Agent] Step 4: Validating results...")
        
        validation_results = validate_ledger(records, df)
        all_passed = check_all_gates(validation_results)
        
        if verbose:
            print(get_gate_summary(validation_results))
        
        if not all_passed:
            # Check for hard failures
            hard_failures = [vr for vr in validation_results 
                           if not vr.passed and vr.gate_name in ["coverage", "profit"]]
            if hard_failures:
                raise RuntimeError(
                    f"Validation failed: {hard_failures[0].error}\n"
                    f"Cannot generate report with validation failures."
                )
        
        # Step 5: Generate output
        if verbose:
            print("[FBA Agent] Step 5: Generating output...")
        
        metadata = {
            "input_file": input_path,
            "supplier_id": supplier_id,
            "run_id": run_id,
            "skip_browser": skip_browser
        }
        
        report_md = render_phasea_report(records, metadata, validation_results)
        
        timing_ms = int((time.time() - start_time) * 1000)
        
        summary = build_run_summary(
            run_id=run_id,
            input_file=input_path,
            supplier_id=supplier_id,
            records=records,
            validation_results=validation_results,
            timing_ms=timing_ms
        )
        
        artifact_paths = write_run_artifacts(
            run_id=run_id,
            records=records,
            report_md=report_md,
            summary=summary,
            output_dir=output_path
        )
        
        if verbose:
            print(f"[FBA Agent] Complete!")
            print(f"  Time: {timing_ms}ms")
            print(f"  Report: {artifact_paths['report']}")
        
        return {
            "run_id": run_id,
            "success": True,
            "summary": summary.to_dict(),
            "artifacts": {k: str(v) for k, v in artifact_paths.items()},
            "validation_passed": all_passed
        }
    
    def get_top_candidates(
        self,
        run_id: str,
        min_confidence: int = 70,
        limit: int = 20,
        bucket_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get top candidates from a previous run.
        
        Args:
            run_id: Run ID to query
            min_confidence: Minimum confidence score
            limit: Maximum number of results
            bucket_filter: Optional bucket to filter by
            
        Returns:
            List of candidate dictionaries
        """
        import json
        
        evidence_path = self.config.default_output_dir / run_id / "evidence.jsonl"
        
        if not evidence_path.exists():
            raise FileNotFoundError(f"Run not found: {run_id}")
        
        candidates = []
        with open(evidence_path, 'r', encoding='utf-8') as f:
            for line in f:
                record = json.loads(line)
                if record['confidence'] >= min_confidence:
                    if bucket_filter and record['bucket'] != bucket_filter:
                        continue
                    candidates.append(record)
        
        # Sort by confidence descending, then by adjusted profit
        candidates.sort(key=lambda x: (-x['confidence'], -x.get('adjusted_profit', 0)))
        
        return candidates[:limit]
    
    def explain_row(self, run_id: str, row_id: int) -> Dict[str, Any]:
        """
        Get detailed explanation for a specific row.
        
        Args:
            run_id: Run ID to query
            row_id: RowID to explain
            
        Returns:
            Full evidence record for the row
        """
        import json
        
        evidence_path = self.config.default_output_dir / run_id / "evidence.jsonl"
        
        if not evidence_path.exists():
            raise FileNotFoundError(f"Run not found: {run_id}")
        
        with open(evidence_path, 'r', encoding='utf-8') as f:
            for line in f:
                record = json.loads(line)
                if record['row_id'] == row_id:
                    return record
        
        raise ValueError(f"RowID {row_id} not found in run {run_id}")
    
    def _extract_supplier_id(self, input_path: str) -> str:
        """Extract supplier ID from filename."""
        path = Path(input_path)
        # Use stem (filename without extension), cleaned up
        name = path.stem.lower()
        # Remove common suffixes
        for suffix in ['_jan', '_feb', '_mar', '_part', '_1', '_2', '_3']:
            name = name.replace(suffix, '')
        return name.replace(' ', '_').replace('-', '_')
    
    def _get_calibration(self, supplier_id: str, df) -> Dict[str, Any]:
        """Get calibration config for supplier."""
        # For MVP, return default calibration
        # V2 will load from memory and run preflight
        return SupplierCalibration(supplier_id=supplier_id).to_dict()
    
    def list_runs(self) -> List[Dict[str, Any]]:
        """
        List all previous runs.
        
        Returns:
            List of run summary dictionaries
        """
        import json
        
        runs = []
        output_dir = self.config.default_output_dir
        
        if not output_dir.exists():
            return runs
        
        for run_dir in output_dir.iterdir():
            if run_dir.is_dir():
                summary_path = run_dir / "run_summary.json"
                if summary_path.exists():
                    with open(summary_path, 'r', encoding='utf-8') as f:
                        runs.append(json.loads(f.read()))
        
        # Sort by created_at descending
        runs.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return runs
