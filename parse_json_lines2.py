import json
import re
from pathlib import Path

def process_file(raw_json_path, output_filename):
    print(f"\nProcessing {raw_json_path}")
    if not Path(raw_json_path).exists():
        return
        
    with open(raw_json_path, 'r', encoding='utf-8') as f:
        data = json.loads(f.read())
        
    tool_input = data.get("tool_input", {})
    tool_name = data.get("tool_name", "")
    
    print(f"Tool name: {tool_name}")
    
    if tool_name == "edit":
        # The edit tool doesn't have the whole file, it just has the patch.
        # But we previously read the entire file using Serena_read_file.
        pass

# Let's search the transcript specifically for the serena_read_file output
transcript_dir = Path(r"C:\Users\chris\claude-clean\transcripts")
main_session_file = transcript_dir / "ses_349c8600cffeqiFNWYjgluqHCM.jsonl"

def extract_serena_read(filename):
    print(f"\nExtracting {filename} via serena_read_file...")
    content = None
    with open(main_session_file, 'r', encoding='utf-8') as f:
        for line in f:
            if "serena_read_file" in line and filename in line:
                try:
                    event = json.loads(line)
                    if event.get("type") == "tool_result" and event.get("tool_name") == "serena_read_file":
                        content = event.get("content", "")
                        # Save it!
                        if len(content) > 100:
                            out_path = Path("temp/recovered_files") / Path(filename).name
                            with open(out_path, 'w', encoding='utf-8') as outf:
                                outf.write(content)
                            print(f"Recovered {len(content)} bytes to {out_path}")
                except:
                    pass

extract_serena_read("control_plane/chat_orchestrator.py")
extract_serena_read("control_plane/tools/run_validation.py")
extract_serena_read("control_plane/tools/tool_param_validation.py")

