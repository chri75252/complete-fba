import json
from pathlib import Path

transcript_dir = Path(r"C:\Users\chris\claude-clean\transcripts")
main_session_file = transcript_dir / "ses_349c8600cffeqiFNWYjgluqHCM.jsonl"

def debug_transcript(filename):
    with open(main_session_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                event = json.loads(line)
                # Look at message blocks too
                if event.get("type") == "message" and event.get("message", {}).get("role") == "user":
                    content = event.get("message", {}).get("content", [])
                    for block in content:
                        if block.get("type") == "tool_result":
                            block_content = block.get("content", [])
                            for text_block in block_content:
                                if text_block.get("type") == "text" and filename in text_block.get("text", ""):
                                    print(f"Found tool result containing {filename}")
                                    print("Snippet of text:")
                                    print(text_block.get("text")[:500])
                                    return
            except Exception as e:
                pass

debug_transcript("chat_orchestrator.py")
