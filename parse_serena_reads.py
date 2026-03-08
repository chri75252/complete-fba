import json
import re
from pathlib import Path
from collections import defaultdict

transcript_dir = Path(r"C:\Users\chris\claude-clean\transcripts")
transcript_files = [
    f for f in transcript_dir.iterdir() 
    if f.suffix == '.jsonl' and f.stat().st_mtime > 1740000000 
]

output_dir = Path("temp/recovered_files")
output_dir.mkdir(parents=True, exist_ok=True)

# We map filename to a list of lines. We'll reconstruct without line numbers if it's raw text.
# The serena_read_file tool returns raw text, NOT line-numbered text!
file_contents = {
    "control_plane/chat_orchestrator.py": {},
    "control_plane/worker.py": {},
    "control_plane/tools/run_validation.py": {},
    "control_plane/tools/tool_param_validation.py": {},
}

print(f"Scanning for raw tool reads...")
for tf in transcript_files:
    with open(tf, 'r', encoding='utf-8') as f:
        for line in f:
            if "serena_read_file" not in line and "read" not in line:
                continue
            try:
                event = json.loads(line)
                if event.get("type") == "tool_result" and "read" in event.get("tool_name", ""):
                    content = event.get("content", "")
                    # For serena_read_file, it's just raw text.
                    # We need to figure out which file it was. The tool_input has it.
                    # But tool_input is in the PREVIOUS message or we can check the text.
                    pass
                
                # Check tool_calls
                if event.get("type") == "message" and event.get("message", {}).get("role") == "assistant":
                    for block in event.get("message", {}).get("content", []):
                        if block.get("type") == "tool_use" and "read" in block.get("name", ""):
                            # We found a read call. We need its result.
                            pass
                            
            except Exception:
                pass

# Let's use a simpler approach. Grep the log files for the exact tool results.
