"""
Extended pack extraction — new patterns only, NO common-integer fallback.

Added patterns (derived from actual miss cases in pack_extraction_audit.json):
  1. "N Piece(s)"            — Amazon dominant phrasing
  2. "Pk N" / "PK N" / "pk N"— supplier reversed of existing (\\d+)pk
  3. "N count" / "N ct"      — count-style pack markers
  4. "Pack N" (without 'of') — Amazon "Pack 6" / "Pack of 6" (of-less variant)
  5. "\\bN-pack\\b" / "N PACK" — hyphenated / spaced
NOT added (explicit decisions):
  - Common-integer fallback (user explicitly warned it caused past inconsistencies)
  - "N Double/Single/Triple" — describes product feature, not pack count
  - Bare "N Dishes/Tubs/Bags" — too many false positives with product sizes
"""
from __future__ import annotations
import re
from typing import Optional, Any
import math

PACK_PATTERNS = [
    # existing
    r"pack of (\d+)",
    r"(\d+)\s*pack\b",
    r"(\d+)\s*pk\b",
    r"(\d+)\s*pcs?\b",
    r"set of (\d+)",
    r"\b(\d+)x\b",
    r"\bx(\d+)\b",
    # new, deterministic only
    r"(\d+)\s*piece[s]?\b",
    r"\bpk\s*(\d+)\b",
    r"(\d+)\s*count\b",
    r"(\d+)\s*ct\b",
    r"\bpack\s+(\d+)\b",
    r"\b(\d+)\s*-\s*pack\b",
]

def clean_text(value: Any) -> str:
    s = "" if value is None or (isinstance(value, float) and math.isnan(value)) else str(value).lower()
    s = s.replace("\u00d7", "x").replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "-")
    s = re.sub(r"[^a-z0-9\.\-\+ ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def extract_pack_v2(value: Any) -> Optional[int]:
    s = clean_text(value)
    for pattern in PACK_PATTERNS:
        m = re.search(pattern, s)
        if m:
            try:
                n = int(m.group(1))
                if 1 <= n <= 999:  # sanity guard — packs > 999 are almost always false positives (e.g. model numbers)
                    return n
            except ValueError:
                continue
    return None
