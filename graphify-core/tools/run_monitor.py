import json
import time
import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG_PATH = ROOT / "OUTPUTS" / "DIAGNOSTICS" / "save_telemetry.log"
STATE_PATH = ROOT / "OUTPUTS" / "CACHE" / "processing_states" / "poundwholesale_co_uk_processing_state.json"
OUT_PATH = ROOT / "OUTPUTS" / "DIAGNOSTICS" / "monitor_trace.log"
PID_PATH = ROOT / "OUTPUTS" / "DIAGNOSTICS" / "run_monitor.pid"

POLL_INTERVAL = 2.0


def utc_ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_state_summary():
    if not STATE_PATH.exists():
        return None
    try:
        raw = STATE_PATH.read_text(encoding="utf-8")
        data = json.loads(raw)
    except Exception as exc:
        return {"error": f"state_read_failed: {exc}"}

    sp = data.get("system_progression", {})
    ptr = sp.get("resumption_ptr", {})
    hwm = data.get("_high_water_mark", {})
    legacy = {
        "resumption_index": data.get("resumption_index"),
        "last_processed_index": data.get("last_processed_index"),
        "progress_index": data.get("progress_index"),
    }
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()
    return {
        "phase": sp.get("current_phase"),
        "ptr_phase": ptr.get("phase"),
        "ptr_cat": ptr.get("cat_idx"),
        "ptr_prod": ptr.get("prod_idx"),
        "hwm_cat": hwm.get("cat_idx"),
        "hwm_prod": hwm.get("prod_idx"),
        "legacy": legacy,
        "sha1": digest,
    }


def main():
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("a", encoding="utf-8") as out:
        out.write(f"{utc_ts()} monitor_start root={ROOT}\n")
        out.flush()
        log_pos = 0
        last_state = None
        while True:
            try:
                if LOG_PATH.exists():
                    size = LOG_PATH.stat().st_size
                    if size < log_pos:
                        log_pos = 0
                    with LOG_PATH.open("r", encoding="utf-8", errors="replace") as log_file:
                        log_file.seek(log_pos)
                        chunk = log_file.read()
                        log_pos = log_file.tell()
                    if chunk:
                        for line in chunk.splitlines():
                            out.write(f"{utc_ts()} LOG {line}\n")
                state_summary = read_state_summary()
                if state_summary is not None and state_summary != last_state:
                    out.write(
                        f"{utc_ts()} STATE phase={state_summary.get('phase')} ptr=({state_summary.get('ptr_phase')},"
                        f"{state_summary.get('ptr_cat')},{state_summary.get('ptr_prod')}) hwm="
                        f"({state_summary.get('hwm_cat')},{state_summary.get('hwm_prod')}) legacy={state_summary.get('legacy')} sha1={state_summary.get('sha1')}\n"
                    )
                    last_state = state_summary
                elif state_summary is None and last_state is not None:
                    out.write(f"{utc_ts()} STATE missing\n")
                    last_state = None
                out.flush()
                time.sleep(POLL_INTERVAL)
            except KeyboardInterrupt:
                out.write(f"{utc_ts()} monitor_stop keyboard_interrupt\n")
                out.flush()
                break
            except Exception as exc:
                out.write(f"{utc_ts()} monitor_error {exc}\n")
                out.flush()
                time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    PID_PATH.write_text(str(os.getpid()), encoding="utf-8")
    main()
