import json
import re
from pathlib import Path

transcript_dir = Path(r"C:\Users\chris\claude-clean\transcripts")
output_dir = Path("temp/recovered_files")
output_dir.mkdir(parents=True, exist_ok=True)

# Use the specific transcript where we read the files earlier
target_transcript = transcript_dir / "ses_349c8600cffeqiFNWYjgluqHCM.jsonl"

def extract_file(filename, sig_string):
    print(f"Extracting {filename}...")
    content = None
    best_len = 0
    with open(target_transcript, 'r', encoding='utf-8') as f:
        for line in f:
            if sig_string in line:
                try:
                    event = json.loads(line)
                    if event.get("type") == "tool_result" and event.get("tool_name") == "edit":
                        # The text after the edit
                        pass
                    elif event.get("type") == "tool_result" and event.get("tool_name") == "bash":
                        pass
                    # If it's a huge block, it might be the read output
                    if len(line) > best_len:
                        best_len = len(line)
                        content = line
                except:
                    pass
    if content:
        # Save raw JSON line
        with open(output_dir / f"{filename.replace('/', '_')}_raw.json", "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Found match! Length: {best_len}")
    else:
        print("Not found")

extract_file("chat_orchestrator.py", "def execute_tool_call")
extract_file("run_validation.py", "def validate_run_integrity")
extract_file("tool_param_validation.py", "def validate_tool_params")

