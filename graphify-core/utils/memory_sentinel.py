import os
import json
import hashlib
import argparse
import sys
from datetime import datetime
from pathlib import Path


def get_file_checksum(file_path):
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


def scan_files(root_dir):
    patterns = ["config/**/*.json", "tools/**/*.py", "control_plane/**/*.py", "utils/**/*.py"]
    files_info = {}
    for pattern in patterns:
        for file_path in root_dir.glob(pattern):
            if file_path.is_file():
                if "memory_baseline.json" in file_path.name:
                    continue

                try:
                    relative_path = str(file_path.relative_to(root_dir))
                    checksum = get_file_checksum(file_path)
                    if checksum:
                        files_info[relative_path] = {
                            "checksum": checksum,
                            "mtime": file_path.stat().st_mtime,
                        }
                except ValueError:
                    continue
    return files_info


def main():
    parser = argparse.ArgumentParser(
        description="Memory Sentinel: Detect drift between code and Supermemory."
    )
    parser.add_argument(
        "--update", action="store_true", help="Update the baseline after verification"
    )
    parser.add_argument(
        "--check", action="store_true", default=True, help="Report drift without updating (default)"
    )
    args = parser.parse_args()

    root_dir = Path(os.getcwd()).absolute()
    baseline_path = root_dir / "OUTPUTS" / "DIAGNOSTICS" / "memory_baseline.json"

    if args.update or not baseline_path.exists():
        current_state = scan_files(root_dir)
        baseline_data = {"files": current_state, "last_updated": datetime.now().isoformat()}
        os.makedirs(baseline_path.parent, exist_ok=True)
        with open(baseline_path, "w") as f:
            json.dump(baseline_data, f, indent=4)
        print(f"Baseline {'updated' if baseline_path.exists() else 'created'} at {baseline_path}")
        print(f"Tracked {len(current_state)} files.")
        return

    with open(baseline_path, "r") as f:
        baseline_data = json.load(f)

    baseline_files = baseline_data.get("files", {})
    current_state = scan_files(root_dir)

    changed = []
    added = []
    removed = []

    for path, info in current_state.items():
        if path not in baseline_files:
            added.append(path)
        elif info["checksum"] != baseline_files[path]["checksum"]:
            changed.append(path)

    for path in baseline_files:
        if path not in current_state:
            removed.append(path)

    if not changed and not added and not removed:
        print(
            f"No drift detected since {baseline_data.get('last_updated')}. Code matches Supermemory baseline."
        )
        sys.exit(0)
    else:
        print(f"Drift detected since last update ({baseline_data.get('last_updated')}):")
        if added:
            print(f"  Added files ({len(added)}):")
            for f in added[:10]:
                print(f"    + {f}")
            if len(added) > 10:
                print(f"    ... and {len(added) - 10} more")
        if changed:
            print(f"  Changed files ({len(changed)}):")
            for f in changed[:10]:
                print(f"    * {f}")
            if len(changed) > 10:
                print(f"    ... and {len(changed) - 10} more")
        if removed:
            print(f"  Removed files ({len(removed)}):")
            for f in removed[:10]:
                print(f"    - {f}")
            if len(removed) > 10:
                print(f"    ... and {len(removed) - 10} more")

        print(f"\nTotal: {len(added) + len(changed) + len(removed)} files affected.")
        print("Run with --update to refresh the baseline after verifying changes.")
        sys.exit(1)


if __name__ == "__main__":
    main()
