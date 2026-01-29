import pandas as pd
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class Validator:
    """
    Ensures integrity of the analysis results.
    """
    
    GREEN_BUCKETS = ["VERIFIED", "HIGHLY_LIKELY", "NEEDS_VERIFICATION"]

    def validate_coverage(self, initial_row_count: int, ledger: pd.DataFrame) -> bool:
        """
        Asserts that every input row has exactly one entry in the ledger.
        """
        ledger_rows = len(ledger)
        unique_ids = ledger["RowID"].nunique()
        
        if ledger_rows != initial_row_count:
            logger.error(f"Coverage Fail: Input={initial_row_count}, Output={ledger_rows}")
            return False
            
        if unique_ids != initial_row_count:
             logger.error(f"Duplicate RowIDs detected: {ledger_rows - unique_ids}")
             return False
             
        return True

    def validate_profit_gates(self, ledger: pd.DataFrame) -> bool:
        """
        Asserts that no row in GREEN_BUCKETS has Adjusted Profit <= 0.
        """
        # Filter for Green Buckets
        green = ledger[ledger["Verdict"].isin(self.GREEN_BUCKETS)]
        
        # Check for negative profit
        negatives = green[green["Adjusted Profit"] <= 0]
        
        if not negatives.empty:
            logger.error(f"Profit Gate Fail: {len(negatives)} rows in Green Buckets have negative profit.")
            return False
            
        return True
