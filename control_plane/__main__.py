from __future__ import annotations

import argparse

from control_plane import worker
from control_plane.build_index import main as build_index_main


def main() -> None:
    parser = argparse.ArgumentParser(prog="control_plane")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("worker")
    sub.add_parser("build-index")

    args = parser.parse_args()

    if args.cmd == "worker":
        worker.main()
        return

    if args.cmd == "build-index":
        build_index_main()
        return


if __name__ == "__main__":
    main()
