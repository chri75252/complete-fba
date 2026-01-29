"""Comprehensive Adjudication Module.

This module implements methodology §2.0A requirements:
- Read ENTIRE generated MD report
- Review EVERY product entry
- Identify errors (false positives, false negatives, miscategorizations)
- Provide root cause analysis
- Recommend recategorizations
- Retrieve missed products

This is NOT per-row automation - this IS comprehensive manual-style review.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd
    from fba_agent.providers import BaseProvider
    from fba_agent.types import MergedConfig


def run_comprehensive_adjudication(
    report_path: Path,
    ledger: "pd.DataFrame",
    source_excel_path: str,
    config: "MergedConfig",
    provider: "BaseProvider",
) -> dict[str, Any]:
    """
    Perform comprehensive manual-style review of ENTIRE MD report.
    
    Implements methodology §2.0A requirements:
    - Read ALL entries in report (not just DataFrame rows)
    - Validate each categorization
    - Identify errors (false positives, false negatives)
    - Root cause analysis
    - Recommend recategorizations
    - Retrieve missed products
    
    This is NOT row-by-row automation.
    This IS comprehensive audit like a human analyst would do.
    
    Args:
        report_path: Path to generated Markdown report
        ledger: Current analysis ledger DataFrame
        source_excel_path: Path to source Excel file
        config: Merged configuration
        provider: LLM provider instance
        
    Returns:
        Dict with errors_found, recategorizations, root_causes, etc.
    """
    # 1. Read FULL MD report
    with open(report_path, "r", encoding="utf-8") as f:
        report_content = f.read()  # ← FULL REPORT, ALL ENTRIES
    
    # 2. Build comprehensive system prompt
    system = """You are an expert FBA product analyst conducting a thorough manual review.

Your task is to analyze a complete FBA analysis report and identify ALL errors,
false positives, false negatives, and miscategorizations.

This is NOT automated processing - you must read and analyze EVERY entry
in the report as a human analyst would.

Key Validation Criteria:
1. EAN matches must be truly exact (not assumptions or partial)
2. Pack sizes must be correctly identified (watch for dimension traps like "9x9 inch")
3. Adjusted profit calculations must be accurate
4. Variants must match (size, color, scent, model)
5. Categorizations must align with methodology

Common Error Patterns to Watch For:
- Dimension numbers misread as pack counts (e.g., "9x9 inch" → 81 packs)
- Capacity patterns misunderstood (e.g., "3 x 400ml" → 1200 units)
- Brand partial matches not recognized
- Strong product matches without brand incorrectly filtered
- Different brands not properly excluded
- Pack math errors in adjusted profit

Return comprehensive, structured JSON analysis."""

    # 3. Build user prompt with full report
    user = f"""Review this complete FBA analysis report:

{report_content}

COMPREHENSIVE AUDIT REQUIREMENTS:

1. Read EVERY product entry across ALL sections:
   - VERIFIED - RECOMMENDED
   - VERIFIED - AUDITED OUT
   - HIGHLY LIKELY - RECOMMENDED
   - HIGHLY LIKELY - AUDITED OUT
   - NEEDS VERIFICATION

2. For EACH entry, validate:
   - EAN matches are truly exact (not assumptions)
   - Pack sizes correctly identified (no dimension traps)
   - Adjusted profit calculations are correct
   - Variants match (size, color, scent)
   - Categorization is appropriate

3. Identify ALL errors:
   - False Positives: Products incorrectly included
   - False Negatives: Valid products that should have been included but are missing
   - Miscategorizations: Products in wrong category
   - Pack detection errors: Dimensions misread as packs
   - Profit calculation errors

4. For EACH error found, document:
   - Row ID (or "N/A" if product not in current report)
   - Current bucket (or "MISSING" if not in report)
   - Issue description
   - Severity (high/medium/low)
   
5. For each miscategorization, provide:
   - Row ID
   - Current bucket
   - Correct bucket
   - Reason for change
   - Suggested confidence (0-100)

6. Identify root causes:
   - Group errors by type (e.g., "brand_partial_not_recognized")
   - Count occurrences
   - Provide examples (row IDs)
   - Propose systematic fixes

7. Check for missed products:
   - Products that match methodology but were excluded
   - Provide supplier title, Amazon title, and reason missed

8. Provide reconciliation:
   - Total entries reviewed in each section
   - Total errors found
   - Total recategorizations recommended

9. Decide if Critique should run:
   - If systematic config issues found → recommend Critique
   - If only isolated errors → manual fixes sufficient

Return JSON following this exact schema:
{{
  "errors_found": [
    {{
      "row_id": "int or 'N/A'",
      "current_bucket": "string or 'MISSING'",
      "issue": "description",
      "severity": "high|medium|low"
    }}
  ],
  "recategorizations": [
    {{
      "row_id": int,
      "from_bucket": "string",
      "to_bucket": "string",
      "reason": "string",
      "confidence": int
    }}
  ],
  "root_causes": {{
    "error_category": {{
      "count": int,
      "examples": ["row_ids"],
      "proposed_fix": "string"
    }}
  }},
  "missed_products_signals": [
    {{
      "supplier_pattern": "string",
      "amazon_pattern": "string",
      "reason_missed": "string"
    }}
  ],
  "reconciliation": {{
    "verified_reviewed": int,
    "highly_likely_reviewed": int,
    "needs_ver_reviewed": int,
    "audited_out_reviewed": int,
    "total_errors": int,
    "total_recategorizations": int
  }},
  "should_run_critique": boolean,
  "critique_reasoning": "string",
  "overall_assessment": "string",
  "config_recommendations": [
    {{
      "target": "string",
      "current_value": "any",
      "proposed_value": "any",
      "reasoning": "string"
    }}
  ]
}}

Be thorough and precise. Read every row carefully."""

    # 4. Call AI with comprehensive prompt
    try:
        result = provider.chat_json(system, user)
        
        # Ensure all required keys exist
        result.setdefault("errors_found", [])
        result.setdefault("recategorizations", [])
        result.setdefault("root_causes", {})
        result.setdefault("missed_products_signals", [])
        result.setdefault("reconciliation", {})
        result.setdefault("should_run_critique", False)
        result.setdefault("overall_assessment", "")
        result.setdefault("config_recommendations", [])
        
        return result
        
    except Exception as e:
        # Return error structure if AI call fails
        return {
            "errors_found": [],
            "recategorizations": [],
            "root_causes": {},
            "missed_products_signals": [],
            "reconciliation": {},
            "should_run_critique": False,
            "overall_assessment": f"Comprehensive adjudication failed: {str(e)}",
            "config_recommendations": [],
            "error": str(e),
        }
