from __future__ import annotations

import sys
from pathlib import Path


def pytest_configure() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    src = repo_root / "src"
    if src.is_dir():
        sys.path.insert(0, str(src))

