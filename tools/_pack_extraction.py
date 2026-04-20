from __future__ import annotations

import math
import re
from typing import Any, Optional


PACK_PATTERNS = [
    r"pack of (\d+)",
    r"(\d+)\s*pack\b",
    r"(\d+)\s*pk\b",
    r"(\d+)\s*pcs?\b",
    r"set of (\d+)",
    r"\b(\d+)x\b",
    r"\bx(\d+)\b",
    r"(\d+)\s*piece[s]?\b",
    r"\bpk\s*(\d+)\b",
    r"(\d+)\s*count\b",
    r"(\d+)\s*ct\b",
    r"\bpack\s+(\d+)\b",
    r"\b(\d+)\s*-\s*pack\b",
]


def _clean(value: Any) -> str:
    s = "" if value is None or (isinstance(value, float) and math.isnan(value)) else str(value).lower()
    s = s.replace("×", "x").replace("‑", "-").replace("–", "-").replace("—", "-")
    s = re.sub(r"[^a-z0-9\.\-\+ ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def extract_pack(value: Any) -> Optional[int]:
    s = _clean(value)
    for pattern in PACK_PATTERNS:
        m = re.search(pattern, s)
        if not m:
            continue
        try:
            n = int(m.group(1))
        except ValueError:
            continue
        if 1 <= n <= 999:
            return n
    return None
