import json
from pathlib import Path

transcript_dir = Path(r"C:\Users\chris\claude-clean\transcripts")
# Let's search all recent files for tool_name="serena_create_text_file" or "write"
transcript_files = [f for f in transcript_dir.iterdir() if f.suffix == '.jsonl']

print("Looking for file creation...")
for tf in transcript_files:
    try:
        with open(tf, 'r', encoding='utf-8') as f:
            for line in f:
                if '"tool_name":"serena_create_text_file"' in line or '"tool_name":"write"' in line or '"tool_name":"edit"' in line:
                    if "run_validation.py" in line or "tool_param_validation.py" in line:
                        event = json.loads(line)
                        if event.get("type") == "tool_use" or event.get("type") == "message":
                            print(f"Found something in {tf.name}")
    except:
        pass
