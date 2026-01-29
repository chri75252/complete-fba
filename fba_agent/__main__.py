from __future__ import annotations

import sys
from pathlib import Path


def _bootstrap_src_on_path() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    src = repo_root / "src"
    if src.is_dir():
        sys.path.insert(0, str(src))


def main() -> int:
    _bootstrap_src_on_path()
    from fba_agent.cli import main as cli_main  # noqa: PLC0415

    return cli_main()


if __name__ == "__main__":
    raise SystemExit(main())

