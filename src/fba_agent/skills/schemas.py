"""
Schemas for the Gemini FBA Analysis Skill.
Defines the structure for Function Calling (Tools).
"""

PREFLIGHT_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "save_calibration_config",
        "description": "Saves the detected supplier naming conventions and patterns.",
        "parameters": {
            "type": "object",
            "properties": {
                "explicit_units": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of unit keywords e.g. ['pcs', 'pk']"
                },
                "brand_position": {
                    "type": "string",
                    "enum": ["start", "end", "mixed"],
                    "description": "Typical position of brand in title"
                },
                "dimension_shield_keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Keywords that indicate dimensions, not packs (e.g. 'cm', 'mm')"
                },
                "allow_trailing_number_as_qty": {
                    "type": "boolean",
                    "description": "If true, 'Product 200' means 200 count"
                }
            },
            "required": ["explicit_units", "brand_position"]
        }
    }
}

ANALYSIS_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "submit_analysis_result",
        "description": "Submits the final analysis verdict for a product row.",
        "parameters": {
            "type": "object",
            "properties": {
                "verdict": {
                    "type": "string",
                    "enum": [
                        "VERIFIED",
                        "HIGHLY_LIKELY",
                        "NEEDS_VERIFICATION",
                        "AUDITED_OUT",
                        "UNRELATED"
                    ],
                    "description": "The final classification category."
                },
                "confidence": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 100,
                    "description": "Confidence score (0-100)."
                },
                "pack_verdict": {
                    "type": "string",
                    "description": "Description of pack match (e.g. '1:1', 'Bundle 4x')."
                },
                "rsu": {
                    "type": "number",
                    "description": "Required Supplier Units (e.g. 4.0 if we need 4 packs)."
                },
                "adjusted_profit": {
                    "type": "number",
                    "description": "Profit after pack adjustment."
                },
                "key_match_evidence": {
                    "type": "string",
                    "description": "Concise evidence supporting the verdict."
                },
                "filter_reason": {
                    "type": "string",
                    "description": "Reason for exclusion or verification needs."
                }
            },
            "required": ["verdict", "confidence", "pack_verdict", "rsu", "adjusted_profit", "key_match_evidence"]
        }
    }
}
