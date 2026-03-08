import json
from pathlib import Path

transcript_dir = Path(r"C:\Users\chris\claude-clean\transcripts")
main_session_file = transcript_dir / "ses_349c8600cffeqiFNWYjgluqHCM.jsonl"

def find_file_reads(filename):
    with open(main_session_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                event = json.loads(line)
                if event.get("type") == "tool_result" and "read" in event.get("tool_name", ""):
                    content = event.get("content", "")
                    # The content is often an array of text objects
                    if isinstance(content, list):
                        content_str = str(content)
                        if filename in content_str:
                            print(f"\nFound match for {filename}:")
                            print(f"Tool: {event.get('tool_name')}")
                            # Print just a snippet to see the structure
                            print(str(content)[:500])
                            return
            except json.JSONDecodeError:
                pass

find_file_reads("chat_orchestrator.py")
