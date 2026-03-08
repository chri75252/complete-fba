import json
from pathlib import Path

transcript_dir = Path(r"C:\Users\chris\claude-clean\transcripts")
main_session_file = transcript_dir / "ses_349c8600cffeqiFNWYjgluqHCM.jsonl"

def debug_transcript(target):
    with open(main_session_file, 'r', encoding='utf-8') as f:
        for line in f:
            if target in line:
                print(f"FOUND EXACT STRING '{target}' IN RAW LINE. Length: {len(line)}")
                print(line[:500])
                print("..." + line[-500:])
                return

debug_transcript("def execute_tool_call")
debug_transcript("def _sanitize_chat_history")
