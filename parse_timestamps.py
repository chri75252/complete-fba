import json
from pathlib import Path

transcript_dir = Path(r"C:\Users\chris\claude-clean\transcripts")

# We know exactly which two transcript files we used:
main_tf = transcript_dir / "ses_349c8600cffeqiFNWYjgluqHCM.jsonl"
val_tf = transcript_dir / "ses_36c74ae8bffetm2R1JkmApf9YE.jsonl"

def get_timestamps(filename, tf_path):
    latest_time = None
    with open(tf_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            
            # The way we extracted chat_orchestrator, worker, and tool_param_val was from the "after" block of the edit tool.
            if '"tool_name":"edit"' in line and '"after":' in line and filename in line:
                try:
                    data = json.loads(line)
                    if data.get("type") == "tool_result" and "filediff" in data.get("tool_output", {}):
                        fn = data["tool_output"]["filediff"].get("file", "")
                        if filename in fn:
                            ts = data.get("timestamp")
                            if ts:
                                latest_time = ts
                except Exception:
                    pass
            
            # The way we extracted run_validation was from a bash cat command or write command
            elif "run_validation.py" in filename:
                if '"command":"cat control_plane/tools/run_validation.py"' in line:
                    try:
                        data = json.loads(line)
                        if data.get("type") == "tool_result" and "output" in data.get("tool_output", {}):
                            ts = data.get("timestamp")
                            if ts:
                                latest_time = ts
                    except Exception:
                        pass
                elif '"tool_name":"write"' in line and 'run_validation.py' in line:
                    try:
                        data = json.loads(line)
                        if data.get("type") == "tool_use":
                            ts = data.get("timestamp")
                            if ts:
                                latest_time = ts
                    except Exception:
                        pass

    return latest_time

print("chat_orchestrator.py timestamp:", get_timestamps("chat_orchestrator.py", main_tf))
print("worker.py timestamp:", get_timestamps("worker.py", main_tf))
print("tool_param_validation.py timestamp:", get_timestamps("tool_param_validation.py", main_tf))
print("run_validation.py timestamp:", get_timestamps("run_validation.py", val_tf))

