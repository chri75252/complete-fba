import builtins
import hashlib
import inspect
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

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

MAX_TEXT_CAPTURE_CHARS = 200000
MAX_JSON_LOG_ENTRIES = 5000


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


def _caller_context() -> Dict[str, Optional[Any]]:
    for frame_info in inspect.stack()[2:]:
        filename = os.path.abspath(frame_info.filename)
        if filename == os.path.abspath(__file__):
            continue
        return {
            "caller_file": filename,
            "caller_line": frame_info.lineno,
            "caller_function": frame_info.function,
        }
    return {
        "caller_file": None,
        "caller_line": None,
        "caller_function": None,
    }


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def _find_json_key_lines(text: str, keys: Iterable[str]) -> Dict[str, List[int]]:
    lines = text.splitlines()
    results: Dict[str, List[int]] = {key: [] for key in keys}
    for idx, line in enumerate(lines, start=1):
        for key in keys:
            if f'"{key}"' in line:
                results[key].append(idx)
    return results


def _truncate_text(text: str) -> str:
    if len(text) <= MAX_TEXT_CAPTURE_CHARS:
        return text
    return text[:MAX_TEXT_CAPTURE_CHARS]


def _is_json_path(path: str) -> bool:
    return path.lower().endswith(".json")


def _extract_json_payload(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


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

        self.json_file_reads: List[Dict[str, Any]] = []
        self.text_file_reads: List[Dict[str, Any]] = []

        self._orig_open = builtins.open
        self._orig_json_load = json.load
        self._orig_json_loads = json.loads
        self._orig_path_read_text = Path.read_text
        self._guard_depth = 0
        self._seen_file_hashes: Set[Tuple[str, str]] = set()

    def _enter_guard(self) -> bool:
        if self._guard_depth > 0:
            return False
        self._guard_depth += 1
        return True

    def _exit_guard(self) -> None:
        if self._guard_depth > 0:
            self._guard_depth -= 1

    def _record_text_read(self, path: str, text: str) -> None:
        if len(self.text_file_reads) >= MAX_JSON_LOG_ENTRIES:
            return
        text_hash = _hash_text(text)
        key = (path, text_hash)
        if key in self._seen_file_hashes:
            return
        self._seen_file_hashes.add(key)
        context = _caller_context()
        self.text_file_reads.append(
            {
                "file": path,
                "caller_file": context["caller_file"],
                "caller_line": context["caller_line"],
                "caller_function": context["caller_function"],
                "sha256": text_hash,
                "text": _truncate_text(text),
            }
        )

    def _record_json_read(self, path: str, text: str, payload: Any) -> None:
        if len(self.json_file_reads) >= MAX_JSON_LOG_ENTRIES:
            return
        text_hash = _hash_text(text)
        key = (path, text_hash)
        if key in self._seen_file_hashes:
            return
        self._seen_file_hashes.add(key)
        context = _caller_context()
        keys = list(payload.keys()) if isinstance(payload, dict) else []
        self.json_file_reads.append(
            {
                "file": path,
                "caller_file": context["caller_file"],
                "caller_line": context["caller_line"],
                "caller_function": context["caller_function"],
                "sha256": text_hash,
                "keys": keys,
                "key_lines": _find_json_key_lines(text, keys) if keys else {},
                "json_text": _truncate_text(text),
                "json_payload": payload,
            }
        )

    def install_detailed_tracing(self) -> None:
        tracer = self

        class _OpenWrapper:
            def __init__(self, fp, path: str, mode: str):
                self._fp = fp
                self._path = path
                self._mode = mode

            def __enter__(self):
                self._fp.__enter__()
                return self

            def __exit__(self, exc_type, exc, tb):
                return self._fp.__exit__(exc_type, exc, tb)

            def __iter__(self):
                return iter(self._fp)

            def __next__(self):
                return next(self._fp)

            def __getattr__(self, name: str):
                return getattr(self._fp, name)

            def read(self, *args, **kwargs):
                data = self._fp.read(*args, **kwargs)
                if isinstance(data, str) and self._path.startswith(str(PROJECT_ROOT)):
                    if tracer._enter_guard():
                        try:
                            tracer._record_text_read(self._path, data)
                            if _is_json_path(self._path):
                                payload = _extract_json_payload(data)
                                if payload is not None:
                                    tracer._record_json_read(self._path, data, payload)
                        finally:
                            tracer._exit_guard()
                return data

        def patched_open(file, mode="r", *args, **kwargs):
            fp = tracer._orig_open(file, mode, *args, **kwargs)
            try:
                path = _normalize_path(file)
            except Exception:
                return fp
            if tracer._guard_depth > 0:
                return fp
            if not path.startswith(str(PROJECT_ROOT)):
                return fp
            if "r" not in str(mode):
                return fp
            return _OpenWrapper(fp, path, str(mode))

        def patched_json_load(fp, *args, **kwargs):
            data = tracer._orig_json_load(fp, *args, **kwargs)
            try:
                path = _normalize_path(fp.name)
            except Exception:
                return data
            if tracer._guard_depth > 0:
                return data
            if not path.startswith(str(PROJECT_ROOT)):
                return data
            if not _is_json_path(path):
                return data
            if tracer._enter_guard():
                try:
                    try:
                        text = tracer._orig_open(path, "r", encoding="utf-8").read()
                    except Exception:
                        return data
                    payload = _extract_json_payload(text)
                    if payload is not None:
                        tracer._record_json_read(path, text, payload)
                finally:
                    tracer._exit_guard()
            return data

        def patched_json_loads(s, *args, **kwargs):
            return tracer._orig_json_loads(s, *args, **kwargs)

        def patched_read_text(self: Path, *args, **kwargs):
            text = tracer._orig_path_read_text(self, *args, **kwargs)
            path = _normalize_path(self)
            if tracer._guard_depth > 0:
                return text
            if not path.startswith(str(PROJECT_ROOT)):
                return text
            if tracer._enter_guard():
                try:
                    tracer._record_text_read(path, text)
                    if _is_json_path(path):
                        payload = _extract_json_payload(text)
                        if payload is not None:
                            tracer._record_json_read(path, text, payload)
                finally:
                    tracer._exit_guard()
            return text

        builtins.open = patched_open
        json.load = patched_json_load
        json.loads = patched_json_loads
        Path.read_text = patched_read_text

    def uninstall_detailed_tracing(self) -> None:
        builtins.open = self._orig_open
        json.load = self._orig_json_load
        json.loads = self._orig_json_loads
        Path.read_text = self._orig_path_read_text

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
                    "json_file_reads": len(self.json_file_reads),
                    "text_file_reads": len(self.text_file_reads),
                },
            },
            "inputs": sorted(inputs),
            "outputs": sorted(outputs),
            "files_read": sorted(self.files_read),
            "files_written": sorted(self.files_written),
            "folders_scanned": sorted(self.folders_scanned),
            "scripts_loaded": sorted(self.scripts_loaded),
            "network_endpoints": sorted(self.network_endpoints),
            "json_file_reads": self.json_file_reads,
            "text_file_reads": self.text_file_reads,
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
    tracer.install_detailed_tracing()

    try:
        run_entry_point(entry_point)
    except KeyboardInterrupt:
        print("Trace interrupted by user.")
    finally:
        tracer.uninstall_detailed_tracing()
        report = tracer.to_report(entry_point)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Trace report written to: {report_path}")


if __name__ == "__main__":
    main()
