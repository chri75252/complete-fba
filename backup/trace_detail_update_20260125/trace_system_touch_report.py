import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Set

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_ENTRY_POINT = "run_custom_poundwholesale.py"
DEFAULT_REPORT_PATH = PROJECT_ROOT / "OUTPUTS" / "DIAGNOSTICS" / "system_touch_report.json"

EXCLUDE_SUBSTRINGS = [
    "\\site-packages\\",
    "\\dist-packages\\",
    "\\__pycache__\\",
]

INPUT_HINT_PATHS = [
    PROJECT_ROOT / "config" / "system_config.json",
    PROJECT_ROOT / "config" / "supplier_configs",
    PROJECT_ROOT / "config" / "supplier_credentials.json",
    PROJECT_ROOT / "config" / "supplier_categories.json",
    PROJECT_ROOT / "config" / "poundwholesale_categories.json",
    PROJECT_ROOT / "config" / "clearance-king_categories.json",
    PROJECT_ROOT / "config" / "angelwholesale_categories.json",
    PROJECT_ROOT / "config" / "kdwholesale_categories.json",
    PROJECT_ROOT / "config" / "laceywholesale_categories.json",
    PROJECT_ROOT / "config" / "dkwholesale_categories.json",
    PROJECT_ROOT / "config" / "efghousewares_workflow_categories.json",
    PROJECT_ROOT / "config" / "wholesaletradingsupplies_categories.json",
]

OUTPUT_HINT_ROOTS = [
    PROJECT_ROOT / "OUTPUTS",
    PROJECT_ROOT / "logs",
]


def _normalize_path(value: Any) -> str:
    if isinstance(value, (str, bytes)):
        return os.path.abspath(os.fspath(value))
    return os.path.abspath(os.fspath(str(value)))


def _should_exclude(path: str) -> bool:
    normalized = path.lower()
    return any(fragment in normalized for fragment in EXCLUDE_SUBSTRINGS)


def _is_under(path: str, roots: Iterable[Path]) -> bool:
    try:
        target = Path(path).resolve()
    except OSError:
        return False
    for root in roots:
        try:
            if target.is_relative_to(root):
                return True
        except AttributeError:
            try:
                target.relative_to(root)
                return True
            except ValueError:
                continue
    return False


def build_config_inputs(config_path: Path) -> Set[str]:
    inputs: Set[str] = set()
    if not config_path.exists():
        return inputs
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return inputs

    workflows = data.get("workflows", {})
    for workflow in workflows.values():
        path_value = workflow.get("categories_config_path")
        if path_value:
            inputs.add(_normalize_path(PROJECT_ROOT / path_value))
    return inputs


def load_input_hints() -> Set[str]:
    inputs: Set[str] = set()
    for path in INPUT_HINT_PATHS:
        if path.exists():
            inputs.add(str(path.resolve()))
    inputs.update(build_config_inputs(PROJECT_ROOT / "config" / "system_config.json"))
    return inputs


class SystemTouchTracer:
    def __init__(self) -> None:
        self.files_read: Set[str] = set()
        self.files_written: Set[str] = set()
        self.folders_scanned: Set[str] = set()
        self.scripts_loaded: Set[str] = set()
        self.network_endpoints: Set[str] = set()
        self.input_hints: Set[str] = load_input_hints()

    def audit_hook(self, event: str, args: tuple[Any, ...]) -> None:
        if event == "open":
            path = _normalize_path(args[0]) if args else ""
            if not path or _should_exclude(path):
                return
            mode = args[1] if len(args) > 1 else "r"
            if mode is None:
                mode = "r"
            if any(flag in mode for flag in ("w", "a", "+", "x")):
                self.files_written.add(path)
            else:
                self.files_read.add(path)
        elif event in {"os.listdir", "os.scandir"}:
            path = _normalize_path(args[0]) if args else ""
            if path and not _should_exclude(path):
                self.folders_scanned.add(path)
        elif event == "exec":
            if args and hasattr(args[0], "co_filename"):
                path = _normalize_path(args[0].co_filename)
                if path.endswith(".py") and not _should_exclude(path):
                    self.scripts_loaded.add(path)
        elif event == "socket.connect":
            if len(args) > 1 and isinstance(args[1], tuple):
                host, port = args[1][:2]
                self.network_endpoints.add(f"{host}:{port}")

    def classify_inputs(self) -> Set[str]:
        inputs = set(self.files_read)
        inputs.update(self.input_hints)
        return inputs

    def classify_outputs(self) -> Set[str]:
        outputs = set(self.files_written)
        for path in self.files_written:
            if _is_under(path, OUTPUT_HINT_ROOTS):
                outputs.add(path)
        return outputs

    def to_report(self, entry_point: str) -> Dict[str, Any]:
        inputs = self.classify_inputs()
        outputs = self.classify_outputs()

        return {
            "metadata": {
                "entry_point": entry_point,
                "timestamp": datetime.now().isoformat(),
                "project_root": str(PROJECT_ROOT),
                "summary": {
                    "files_read": len(self.files_read),
                    "files_written": len(self.files_written),
                    "folders_scanned": len(self.folders_scanned),
                    "scripts_loaded": len(self.scripts_loaded),
                    "network_endpoints": len(self.network_endpoints),
                    "input_candidates": len(inputs),
                    "output_candidates": len(outputs),
                },
            },
            "inputs": sorted(inputs),
            "outputs": sorted(outputs),
            "files_read": sorted(self.files_read),
            "files_written": sorted(self.files_written),
            "folders_scanned": sorted(self.folders_scanned),
            "scripts_loaded": sorted(self.scripts_loaded),
            "network_endpoints": sorted(self.network_endpoints),
        }


def run_entry_point(entry_point: str) -> None:
    script_path = PROJECT_ROOT / entry_point
    if not script_path.exists():
        raise FileNotFoundError(f"Entry point not found: {script_path}")

    code = compile(script_path.read_text(encoding="utf-8"), str(script_path), "exec")
    globals_dict = {
        "__name__": "__main__",
        "__file__": str(script_path),
    }
    exec(code, globals_dict)


def main() -> None:
    entry_point = DEFAULT_ENTRY_POINT
    report_path = DEFAULT_REPORT_PATH

    if len(sys.argv) > 1:
        entry_point = sys.argv[1]
    if len(sys.argv) > 2:
        report_path = Path(sys.argv[2])

    tracer = SystemTouchTracer()
    sys.addaudithook(tracer.audit_hook)

    try:
        run_entry_point(entry_point)
    except KeyboardInterrupt:
        print("Trace interrupted by user.")
    finally:
        report = tracer.to_report(entry_point)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Trace report written to: {report_path}")


if __name__ == "__main__":
    main()
