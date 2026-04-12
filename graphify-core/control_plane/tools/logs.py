from __future__ import annotations

from pathlib import Path


def tail_file(path: Path, lines: int = 200) -> list[str]:
    if lines <= 0:
        return []
    if not path.exists():
        return []

    # Read last ~64KB and split; good enough for logs.
    with open(path, "rb") as fh:
        fh.seek(0, 2)
        size = fh.tell()
        fh.seek(max(size - 65536, 0), 0)
        data = fh.read().decode("utf-8", errors="ignore")

    split = [ln.rstrip("\n") for ln in data.splitlines()]
    return split[-lines:]
