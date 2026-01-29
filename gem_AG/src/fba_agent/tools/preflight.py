import json
import logging
from typing import Dict, Any, List
import pandas as pd
from openai import OpenAI
from ..config import MOONSHOT_API_KEY, MOONSHOT_BASE_URL, MODEL_NAME
from ..core.memory import SupplierMemory

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "explicit_units": ["pce", "pcs", "pk", "pack", "unit", "set"],
    "allow_trailing_number_as_qty": False,
    "leading_multiplier_check": True,
    "dimension_shield_keywords": ["cm", "mm", "ml", "ltr", "L", "kg", "g", "oz", "inch", "in", "watt", "w", "v"],
    "brand_position": "mixed",
    "sales_column": "Sales",
    "capacity_pattern_as_rsu": True,
    "spec_x_shield_keywords": ["magnification", "zoom", "microscope", "scope", "times", "x strength"],
    "table_pipe_sanitization": True
}

PREFLIGHT_SYSTEM_PROMPT = """
You are a Data Pattern Specialist. Analyze these 50 rows of product data to identify supplier naming conventions.
Output strictly valid JSON matching this schema:
{
    "explicit_units": ["list", "of", "units"],
    "allow_trailing_number_as_qty": boolean,
    "leading_multiplier_check": boolean,
    "dimension_shield_keywords": ["list", "of", "units"],
    "brand_position": "start" | "mixed" | "end",
    "sales_column": "detected_column_name",
    "capacity_pattern_as_rsu": boolean,
    "spec_x_shield_keywords": ["list", "of", "keywords"],
    "table_pipe_sanitization": boolean
}
"""

class PreflightManager:
    def __init__(self, supplier_id: str):
        self.supplier_id = supplier_id
        self.memory = SupplierMemory(supplier_id)
        self.client = OpenAI(
            api_key=MOONSHOT_API_KEY, 
            base_url=MOONSHOT_BASE_URL
        )

    def run_preflight(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Runs the full preflight sequence:
        1. Load existing memory.
        2. Analyze sample rows via LLM.
        3. Merge configs (Overrides > Memory > LLM > Default).
        """
        # 1. Load Memory
        stored_calibration = self.memory.load_calibration()
        overrides = self.memory.load_overrides() # Not used for config merge, but available

        # 2. LLM Analysis (Safe guard against empty or short DFs)
        sample_rows = df.head(50).to_dict(orient='records')
        llm_calibration = self._call_llm_calibration(sample_rows)

        # 3. Merge
        merged = self._merge_configs(DEFAULT_CONFIG, llm_calibration, stored_calibration)
        
        # Save the *new* derived calibration to memory (optional, or manual save later)
        # We generally want to persist the LLM's findings if they are new.
        # For now, we will NOT overwrite memory automatically to prevent drift, 
        # unless we explicitly implement a learning step. 
        # The PRD says "Run Preflight again (do not skip)... append new traps/examples".
        # We will return the merged config.
        
        return merged

    def _call_llm_calibration(self, rows: List[Dict]) -> Dict[str, Any]:
        """Calls the LLM to analyze the rows."""
        try:
            # Format row sample for prompt
            row_text = ""
            for i, r in enumerate(rows[:20]): # Limit to 20 for prompt size safety
                row_text += f"Row {i}: SupTitle='{r.get('SupplierTitle')}' | AmzTitle='{r.get('AmazonTitle')}'\n"

            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": PREFLIGHT_SYSTEM_PROMPT},
                    {"role": "user", "content": f"Analyze these rows:\n{row_text}"}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            logger.error(f"LLM Calibration failed: {e}")
            return {}

    def _merge_configs(self, defaults: Dict, llm: Dict, stored: Dict) -> Dict:
        """
        Merges configs with precedence: Stored > LLM > Defaults.
        (Overrides are usually Row-level, not Config-level, unless we add ConfigOverrides later).
        """
        # Start with defaults
        merged = defaults.copy()
        
        # Update with LLM findings (only keys that exist in schema)
        for k, v in llm.items():
            if k in merged and v is not None:
                # For lists, we might want to union them? 
                # For now, LLM replacement is safer than union to avoid growing garbage.
                merged[k] = v
        
        # Update with Stored Memory (Highest Precedence for Config)
        for k, v in stored.items():
            if k in merged and v is not None:
                merged[k] = v
                
        return merged
