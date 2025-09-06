import time, json, shutil
from pathlib import Path

STATE = Path(r"OUTPUTS/CACHE/processing_states/poundwholesale_co_uk_processing_state.json")
OUTDIR = Path(r"diagnostics/state_events")
OUTDIR.mkdir(parents=True, exist_ok=True)

prev = None
while True:
    if STATE.exists():
        cur = STATE.read_text(encoding="utf-8")
        if cur != prev:
            ts = str(int(time.time()))
            snap = OUTDIR / f"state_{ts}.json"
            snap.write_text(cur, encoding="utf-8")
            print(f"CHANGED at {ts} → {snap}")
            prev = cur
    time.sleep(1.0)