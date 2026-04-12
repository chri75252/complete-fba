from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path


def backup_file(file_path: Path, backup_root: Path, *, reason: str) -> Path:
    """Copy a file to backup_root/<reason>_<YYYYMMDD>/ preserving filename."""

    date_stamp = datetime.now().strftime("%Y%m%d")
    dest_dir = backup_root / f"{reason}_{date_stamp}"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / file_path.name
    shutil.copy2(file_path, dest_path)
    return dest_path
