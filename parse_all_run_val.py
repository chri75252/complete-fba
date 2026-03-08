import json
from pathlib import Path

transcript_dir = Path(r"C:\Users\chris\claude-clean\transcripts")
files = sorted([f for f in transcript_dir.iterdir() if f.suffix == '.jsonl'], 
              key=lambda x: x.stat().st_mtime, reverse=True)

latest_run_val = None
latest_ts = ""

for tf in files:
    with open(tf, 'r', encoding='utf-8') as f:
        for line in f:
            if "run_validation.py" in line:
                if '"tool_name":"edit"' in line and '"after":' in line:
                    try:
                        data = json.loads(line)
                        if data.get("type") == "tool_result" and "filediff" in data.get("tool_output", {}):
                            fn = data["tool_output"]["filediff"].get("file", "")
                            if "run_validation.py" in fn:
                                ts = data.get("timestamp", "")
                                if ts > latest_ts:
                                    latest_ts = ts
                                    latest_run_val = data["tool_output"]["filediff"].get("after", "")
                    except: pass
                elif '"command":"cat control_plane/tools/run_validation.py"' in line:
                    try:
                        data = json.loads(line)
                        if data.get("type") == "tool_result" and "output" in data.get("tool_output", {}):
                            ts = data.get("timestamp", "")
                            if ts > latest_ts:
                                latest_ts = ts
                                latest_run_val = data["tool_output"]["output"]
                    except: pass
                elif '"tool_name":"serena_read_file"' in line:
                    try:
                        data = json.loads(line)
                        if data.get("type") == "tool_result":
                            content = data.get("content", "")
                            if "def validate_run_integrity" in content:
                                ts = data.get("timestamp", "")
                                if ts > latest_ts:
                                    latest_ts = ts
                                    latest_run_val = content
                    except: pass

if latest_run_val:
    print(f"Found newer run_validation.py timestamp: {latest_ts}")
    with open("temp/recovered_files/run_validation.py", "w", encoding="utf-8") as out:
        out.write(latest_run_val)
else:
    print("No newer version found.")
