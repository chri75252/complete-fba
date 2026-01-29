from __future__ import annotations

import re

from fba_agent.constants import STOPWORDS


_NON_ALNUM_RE = re.compile(r"[^A-Z0-9]+")
_MULTISPACE_RE = re.compile(r"\s+")


def sanitize_cell(text: str) -> str:
    text = text.replace("\t", " ")
    text = text.replace("|", "/")
    text = text.replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
    return _MULTISPACE_RE.sub(" ", text).strip()


def normalize_title(text: str) -> str:
    text = text.upper()
    text = _NON_ALNUM_RE.sub(" ", text)
    text = _MULTISPACE_RE.sub(" ", text).strip()
    return text


def tokenize(text: str) -> list[str]:
    norm = normalize_title(text)
    tokens = [t for t in norm.split(" ") if t and t not in STOPWORDS]
    return tokens


def jaccard_similarity(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def clamp(value: int, low: int, high: int) -> int:
    if value < low:
        return low
    if value > high:
        return high
    return value

