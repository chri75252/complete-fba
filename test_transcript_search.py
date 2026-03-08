import json
from pathlib import Path

transcript_dir = Path(r"C:\Users\chris\claude-clean\transcripts")
# The largest, most recent file is usually the main session
main_session_file = transcript_dir / "ses_349c8600cffeqiFNWYjgluqHCM.jsonl"

def find_file_reads(filename):
    reads = []
    with open(main_session_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                event = json.loads(line)
                # Look for tool results where we read files
                if event.get("type") == "tool_result" and event.get("tool_name") in ["read", "serena_read_file"]:
                    content = event.get("content", "")
                    if filename in content or filename in str(event):
                        reads.append(event)
                # Also look for bash commands like 'cat file'
                if event.get("type") == "tool_result" and event.get("tool_name") == "bash":
                    command = event.get("command", "")
                    if filename in command or filename in str(event):
                        reads.append(event)
            except json.JSONDecodeError:
                pass
    return len(reads)

print("Found reads for chat_orchestrator.py:", find_file_reads("chat_orchestrator.py"))
print("Found reads for worker.py:", find_file_reads("worker.py"))
print("Found reads for run_validation.py:", find_file_reads("run_validation.py"))
print("Found reads for tool_param_validation.py:", find_file_reads("tool_param_validation.py"))

