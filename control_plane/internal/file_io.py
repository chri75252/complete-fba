from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from utils.windows_save_guardian import WindowsSaveGuardian


def write_json_atomic(path: Path, data: Any) -> None:
    guardian = WindowsSaveGuardian()
    ok = guardian.save_json_atomic(path, data, min_entries_guard=0)
    if not ok:
        raise OSError(f"Atomic save failed: {path}")


def write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp_fd, tmp_path = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
        raise


def read_json(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
