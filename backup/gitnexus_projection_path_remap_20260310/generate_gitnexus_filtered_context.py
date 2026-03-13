from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

TEXT_PREVIEW_EXTENSIONS = {
    ".json",
    ".log",
    ".txt",
    ".csv",
    ".md",
    ".yaml",
    ".yml",
}


@dataclass(frozen=True)
class SelectedItem:
    category: str
    kind: str
    source_path: Path
    source_relative_path: str
    size_bytes: int
    mtime_iso: str
    preview_lines: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate curated runtime context files for GitNexus indexing."
    )
    parser.add_argument(
        "--rules",
        default="config/gitnexus_scope_rules.json",
        help="Path to scope rules JSON (relative to repo root).",
    )
    parser.add_argument(
        "--output-dir",
        default="gitnexus_runtime_context",
        help="Output directory for generated context files.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print selections without writing output files.",
    )
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_rules(rules_path: Path) -> dict:
    if not rules_path.exists():
        raise FileNotFoundError(f"Rules file not found: {rules_path}")
    with rules_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def all_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return [path for path in root.rglob("*") if path.is_file()]


def normalized(path: Path) -> str:
    return path.as_posix().lower()


def is_sandbox(path: Path) -> bool:
    text = normalized(path)
    return "__sandbox__" in text or "run_id" in text or "sandbox" in text


def is_main(path: Path) -> bool:
    return not is_sandbox(path)


def is_archived(path: Path) -> bool:
    text = normalized(path)
    return "/archive/" in text or "/archived/" in text


def is_canonical_processing_state(path: Path) -> bool:
    name = path.name.lower()
    return name.endswith("_processing_state.json") and not is_archived(path)


def is_canonical_cached_products(path: Path) -> bool:
    name = path.name.lower()
    return name.endswith("_products_cache.json") and not is_archived(path)


def is_canonical_linking_map(path: Path) -> bool:
    name = path.name.lower()
    return name == "linking_map.json" and not is_archived(path)


def is_canonical_financial_report(path: Path) -> bool:
    name = path.name.lower()
    return name.endswith(".csv") and "fba_financial_report" in name and not is_archived(path)


def supplier_token(path: Path) -> str:
    name = path.name.lower()
    if "__sandbox__" in name:
        return name.split("__sandbox__", 1)[0]
    if "run_id" in name:
        return name.split("run_id", 1)[0]
    if path.parent.name:
        return path.parent.name.lower()
    return name


def mtime(path: Path) -> float:
    return path.stat().st_mtime


def iso_from_mtime(path: Path) -> str:
    return datetime.fromtimestamp(mtime(path), tz=timezone.utc).isoformat()


def safe_preview_lines(path: Path, line_limit: int) -> list[str]:
    if line_limit <= 0:
        return []
    if path.suffix.lower() not in TEXT_PREVIEW_EXTENSIONS:
        return []
    preview: list[str] = []
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for _, line in zip(range(line_limit), handle):
                preview.append(line.rstrip("\n")[:320])
    except OSError:
        return []
    return preview


def select_latest(paths: list[Path], count: int) -> list[Path]:
    if count <= 0:
        return []
    return sorted(paths, key=mtime, reverse=True)[:count]


def select_latest_with_supplier_floor(
    paths: list[Path], count: int, min_unique_suppliers: int
) -> list[Path]:
    ordered = sorted(paths, key=mtime, reverse=True)
    if count <= 0:
        return []
    if min_unique_suppliers <= 0:
        return ordered[:count]

    selected: list[Path] = []
    seen_suppliers: set[str] = set()

    for path in ordered:
        token = supplier_token(path)
        if token in seen_suppliers:
            continue
        selected.append(path)
        seen_suppliers.add(token)
        if len(seen_suppliers) >= min_unique_suppliers or len(selected) >= count:
            break

    for path in ordered:
        if path in selected:
            continue
        selected.append(path)
        if len(selected) >= count:
            break

    return selected[:count]


def build_items_for_files(
    paths: Iterable[Path],
    category: str,
    kind: str,
    repo: Path,
    preview_lines: int,
) -> list[SelectedItem]:
    items: list[SelectedItem] = []
    for path in paths:
        items.append(
            SelectedItem(
                category=category,
                kind=kind,
                source_path=path,
                source_relative_path=path.relative_to(repo).as_posix(),
                size_bytes=path.stat().st_size,
                mtime_iso=iso_from_mtime(path),
                preview_lines=safe_preview_lines(path, preview_lines),
            )
        )
    return items


def folder_latest_mtime(path: Path) -> float:
    files = [file_path for file_path in path.rglob("*") if file_path.is_file()]
    if not files:
        return path.stat().st_mtime
    return max(mtime(file_path) for file_path in files)


def build_manifest_folder_items(
    root: Path,
    repo: Path,
    sandbox_latest_folders: int,
    folder_latest_files_preview: int,
    supplier_floor: int,
) -> list[SelectedItem]:
    if not root.exists():
        return []

    folders = [folder for folder in root.iterdir() if folder.is_dir()]
    main_folders = sorted([folder for folder in folders if is_main(folder)], key=lambda f: f.name.lower())
    sandbox_folders = [folder for folder in folders if is_sandbox(folder)]

    sandbox_selected = select_latest_with_supplier_floor(
        sorted(sandbox_folders, key=folder_latest_mtime, reverse=True),
        sandbox_latest_folders,
        supplier_floor,
    )

    selected = [(folder, "main") for folder in main_folders] + [
        (folder, "sandbox") for folder in sandbox_selected
    ]

    items: list[SelectedItem] = []
    for folder, kind in selected:
        files = [file_path for file_path in folder.rglob("*") if file_path.is_file()]
        latest_files = sorted(files, key=mtime, reverse=True)[:folder_latest_files_preview]
        preview = [f"file_count={len(files)}"] + [
            file_path.relative_to(repo).as_posix() for file_path in latest_files
        ]
        items.append(
            SelectedItem(
                category="manifests",
                kind=kind,
                source_path=folder,
                source_relative_path=folder.relative_to(repo).as_posix(),
                size_bytes=0,
                mtime_iso=datetime.fromtimestamp(
                    folder_latest_mtime(folder), tz=timezone.utc
                ).isoformat(),
                preview_lines=preview,
            )
        )
    return items


def financial_supplier_key(path: Path, root: Path) -> str:
    rel = path.relative_to(root)
    if len(rel.parts) >= 2:
        return rel.parts[0].lower()
    name = path.stem.lower()
    marker = "_fba_financial_report"
    if marker in name:
        return name.split(marker, 1)[0]
    return "unknown"


def build_financial_items(
    root: Path,
    repo: Path,
    sandbox_latest: int,
    preview_lines: int,
    supplier_floor: int,
) -> list[SelectedItem]:
    files = [path for path in all_files(root) if is_canonical_financial_report(path)]
    main_files = [path for path in files if is_main(path)]
    sandbox_files = [path for path in files if is_sandbox(path)]

    largest_per_supplier: dict[str, Path] = {}
    for path in main_files:
        key = financial_supplier_key(path, root)
        current = largest_per_supplier.get(key)
        if current is None or path.stat().st_size > current.stat().st_size:
            largest_per_supplier[key] = path

    sandbox_selected = select_latest_with_supplier_floor(
        sandbox_files, sandbox_latest, supplier_floor
    )

    items = build_items_for_files(
        sorted(largest_per_supplier.values(), key=lambda p: p.name.lower()),
        category="financial_reports",
        kind="main_largest_per_supplier",
        repo=repo,
        preview_lines=preview_lines,
    )
    items.extend(
        build_items_for_files(
            sandbox_selected,
            category="financial_reports",
            kind="sandbox_latest",
            repo=repo,
            preview_lines=preview_lines,
        )
    )
    return items


def write_selected_item(out_root: Path, item: SelectedItem, index: int) -> Path:
    source_relative = Path(item.source_relative_path)
    digest = hashlib.sha1(item.source_relative_path.encode("utf-8")).hexdigest()[:10]
    if item.source_path.is_dir():
        out_file = out_root / source_relative / f"__folder_summary__{digest}.py"
    else:
        original_name = source_relative.name
        mirror_name = f"{original_name}__{digest}.py"
        out_file = out_root / source_relative.parent / mirror_name
    out_file.parent.mkdir(parents=True, exist_ok=True)

    content = (
        '"""Generated runtime context mirror for GitNexus.\n'
        "Do not edit manually.\n"
        '"""\n\n'
        f"SOURCE_CATEGORY = {json.dumps(item.category)}\n"
        f"SOURCE_KIND = {json.dumps(item.kind)}\n"
        f"SOURCE_RELATIVE_PATH = {json.dumps(item.source_relative_path)}\n"
        f"SOURCE_SIZE_BYTES = {item.size_bytes}\n"
        f"SOURCE_MTIME_ISO = {json.dumps(item.mtime_iso)}\n"
        f"SOURCE_PREVIEW = {json.dumps(item.preview_lines, ensure_ascii=True, indent=2)}\n"
    )
    out_file.write_text(content, encoding="utf-8")
    return out_file


def generate_context(repo: Path, rules: dict, out_dir: Path, dry_run: bool) -> dict:
    global_rules = rules.get("global", {})
    supplier_floor = int(global_rules.get("sandbox_min_unique_suppliers", 0))
    preview_lines = int(global_rules.get("preview_lines", 20))

    selected_items: list[SelectedItem] = []

    processing_root = repo / rules["processing_states"]["root"]
    processing_files = [path for path in all_files(processing_root) if is_canonical_processing_state(path)]
    selected_items.extend(
        build_items_for_files(
            sorted([path for path in processing_files if is_main(path)], key=lambda p: p.name.lower()),
            "processing_states",
            "main",
            repo,
            preview_lines,
        )
    )
    selected_items.extend(
        build_items_for_files(
            select_latest_with_supplier_floor(
                [path for path in processing_files if is_sandbox(path)],
                int(rules["processing_states"]["sandbox_latest"]),
                supplier_floor,
            ),
            "processing_states",
            "sandbox_latest",
            repo,
            preview_lines,
        )
    )

    cached_root = repo / rules["cached_products"]["root"]
    cached_files = [path for path in all_files(cached_root) if is_canonical_cached_products(path)]
    selected_items.extend(
        build_items_for_files(
            sorted([path for path in cached_files if is_main(path)], key=lambda p: p.name.lower()),
            "cached_products",
            "main",
            repo,
            preview_lines,
        )
    )
    selected_items.extend(
        build_items_for_files(
            select_latest_with_supplier_floor(
                [path for path in cached_files if is_sandbox(path)],
                int(rules["cached_products"]["sandbox_latest"]),
                supplier_floor,
            ),
            "cached_products",
            "sandbox_latest",
            repo,
            preview_lines,
        )
    )

    linking_root = repo / rules["linking_maps"]["root"]
    linking_files = [path for path in all_files(linking_root) if is_canonical_linking_map(path)]
    selected_items.extend(
        build_items_for_files(
            sorted([path for path in linking_files if is_main(path)], key=lambda p: p.name.lower()),
            "linking_maps",
            "main",
            repo,
            preview_lines,
        )
    )
    selected_items.extend(
        build_items_for_files(
            select_latest_with_supplier_floor(
                [path for path in linking_files if is_sandbox(path)],
                int(rules["linking_maps"]["sandbox_latest"]),
                supplier_floor,
            ),
            "linking_maps",
            "sandbox_latest",
            repo,
            preview_lines,
        )
    )

    amazon_root = repo / rules["amazon_cache"]["root"]
    selected_items.extend(
        build_items_for_files(
            select_latest(all_files(amazon_root), int(rules["amazon_cache"]["latest"])),
            "amazon_cache",
            "latest",
            repo,
            preview_lines,
        )
    )

    manifests_root = repo / rules["manifests"]["root"]
    selected_items.extend(
        build_manifest_folder_items(
            manifests_root,
            repo,
            sandbox_latest_folders=int(rules["manifests"]["sandbox_latest_folders"]),
            folder_latest_files_preview=int(rules["manifests"]["folder_latest_files_preview"]),
            supplier_floor=supplier_floor,
        )
    )

    products_root = repo / rules["products_lists"]["root"]
    selected_items.extend(
        build_items_for_files(
            select_latest(all_files(products_root), int(rules["products_lists"]["latest"])),
            "products_lists",
            "latest",
            repo,
            preview_lines,
        )
    )

    logs_root = repo / rules["logs_debug"]["root"]
    log_files = [path for path in all_files(logs_root) if path.suffix.lower() == ".log"]
    selected_items.extend(
        build_items_for_files(
            select_latest(
                [path for path in log_files if is_main(path)],
                int(rules["logs_debug"]["main_latest"]),
            ),
            "logs_debug",
            "main_latest",
            repo,
            preview_lines,
        )
    )
    selected_items.extend(
        build_items_for_files(
            select_latest_with_supplier_floor(
                [path for path in log_files if is_sandbox(path)],
                int(rules["logs_debug"]["sandbox_latest"]),
                supplier_floor,
            ),
            "logs_debug",
            "sandbox_latest",
            repo,
            preview_lines,
        )
    )

    financial_root = repo / rules["financial_reports"]["root"]
    selected_items.extend(
        build_financial_items(
            financial_root,
            repo,
            sandbox_latest=int(rules["financial_reports"]["sandbox_latest"]),
            preview_lines=preview_lines,
            supplier_floor=supplier_floor,
        )
    )

    selected_items = sorted(
        selected_items,
        key=lambda item: (item.category, item.kind, item.source_relative_path.lower()),
    )

    summary = {
        "generated_at_utc": datetime.now(tz=timezone.utc).isoformat(),
        "rules_file": str((repo / "config/gitnexus_scope_rules.json").as_posix()),
        "sandbox_min_unique_suppliers": supplier_floor,
        "total_selected_items": len(selected_items),
        "categories": {},
        "selected": [],
    }

    for item in selected_items:
        key = f"{item.category}:{item.kind}"
        summary["categories"][key] = summary["categories"].get(key, 0) + 1
        summary["selected"].append(
            {
                "category": item.category,
                "kind": item.kind,
                "source_relative_path": item.source_relative_path,
                "size_bytes": item.size_bytes,
                "mtime_iso": item.mtime_iso,
            }
        )

    if dry_run:
        return summary

    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    written: list[str] = []
    for index, item in enumerate(selected_items, start=1):
        out_file = write_selected_item(out_dir, item, index)
        written.append(out_file.relative_to(repo).as_posix())

    manifest_py = out_dir / "_manifest.py"
    manifest_py.write_text(
        '"""Generated selection manifest for GitNexus runtime context."""\n\n'
        f"SELECTION_SUMMARY = {json.dumps(summary, ensure_ascii=True, indent=2)}\n"
        f"GENERATED_FILES = {json.dumps(written, ensure_ascii=True, indent=2)}\n",
        encoding="utf-8",
    )

    manifest_json = out_dir / "_manifest.json"
    manifest_json.write_text(
        json.dumps(summary, ensure_ascii=True, indent=2) + "\n", encoding="utf-8"
    )

    return summary


def main() -> int:
    args = parse_args()
    repo = repo_root()
    rules_path = (repo / args.rules).resolve()
    out_dir = (repo / args.output_dir).resolve()

    rules = load_rules(rules_path)
    summary = generate_context(repo, rules, out_dir, dry_run=args.dry_run)

    print("GitNexus filtered context summary:")
    print(json.dumps(summary["categories"], indent=2, ensure_ascii=True))
    print(f"Total selected items: {summary['total_selected_items']}")
    if args.dry_run:
        print("Dry run complete; no files were written.")
    else:
        print(f"Output directory: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
