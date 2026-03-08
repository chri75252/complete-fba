import json
from pathlib import Path

transcript_dir = Path(r"C:\Users\chris\claude-clean\transcripts")
files = sorted([f for f in transcript_dir.iterdir() if f.suffix == '.jsonl'], 
              key=lambda x: x.stat().st_mtime, reverse=True)

target_timestamps = {
    "chat_orchestrator.py": "2026-03-04T22:04:58.603Z",
    "worker.py": "2026-03-04T14:19:25.197Z",
    "tool_param_validation.py": "2026-03-04T14:56:16.990Z",
    "run_validation.py": "2026-03-04T14:15:10.059Z"
}

found = {}

for tf in files:
    with open(tf, 'r', encoding='utf-8') as f:
        for line in f:
            for filename, ts in target_timestamps.items():
                if ts in line:
                    if filename not in found:
                        found[filename] = tf.name

for filename, session in found.items():
    print(f"{filename} came from session: {session}")

