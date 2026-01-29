import pandas as pd
from pathlib import Path
from datetime import datetime
import logging
from typing import Optional

# Tools
from ..tools.loader import DataLoader
from ..tools.preflight import PreflightManager
from ..tools.analyzer import RowAnalyzer
from ..tools.validator import Validator
from ..tools.reporting import ReportGenerator

# Config
from ..config import RUNS_DIR

logger = logging.getLogger(__name__)

class AnalysisEngine:
    
    def run_analysis(self, input_path: str, supplier_id: str, skip_browser: bool = True):
        """
        Orchestrates the full FBA Analysis Pipeline.
        """
        run_date = datetime.now().strftime("%Y%m%d")
        run_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_timestamp = datetime.now().strftime("%m%d%H%M")  # MMDDHHMM for report filename
        run_id = f"run_{run_ts}_{supplier_id}"
        run_dir = RUNS_DIR / run_id
        
        logger.info(f"Starting Run {run_id} for {supplier_id}")
        
        # 1. Load Data
        loader = DataLoader()
        df, meta = loader.load_file(input_path)
        logger.info(f"Loaded {len(df)} rows form {input_path}")
        
        # 2. Preflight Calibration
        preflight = PreflightManager(supplier_id)
        config = preflight.run_preflight(df)
        logger.info("Preflight Calibration Complete")
        
        # 3. Deterministic Analysis
        analyzer = RowAnalyzer(config)
        results = []
        
        # Sequential Processing (Analyzer is fast enough for 5k rows)
        for _, row in df.iterrows():
            decision = analyzer.analyze_row(row.to_dict())
            results.append(decision)
            
        ledger_df = pd.DataFrame(results)
        
        # 4. Validation
        validator = Validator()
        coverage_ok = validator.validate_coverage(len(df), ledger_df)
        profit_ok = validator.validate_profit_gates(ledger_df)
        
        if not coverage_ok:
            logger.error("CRITICAL: Coverage Validation Failed")
        if not profit_ok:
            logger.error("CRITICAL: Profit Gate Validation Failed")
            
        # 5. Reporting
        reporter = ReportGenerator(run_dir)
        run_meta = {
            "run_id": run_id,
            "run_date": run_date,
            "run_timestamp": run_timestamp,
            "supplier_id": supplier_id,
            "input_file": input_path,
            "total_rows": len(df),
            "config_used": config,
            "validation": {
                "coverage": coverage_ok,
                "profit": profit_ok
            }
        }
        
        # Prepare evidence list for simple serialization
        evidence = ledger_df.to_dict(orient='records')
        
        reporter.generate_artifacts(ledger_df, evidence, run_meta)
        
        logger.info(f"Analysis Complete. Artifacts in {run_dir}")
        return run_dir
