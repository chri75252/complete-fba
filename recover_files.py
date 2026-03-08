import json
import re
from pathlib import Path
from collections import defaultdict

transcript_dir = Path(r"C:\Users\chris\claude-clean\transcripts")
main_session_file = transcript_dir / "ses_349c8600cffeqiFNWYjgluqHCM.jsonl"
output_dir = Path("temp/recovered_files")
output_dir.mkdir(parents=True, exist_ok=True)

def parse_line_numbers(text):
    """Parse text with line numbers (e.g. '1: import os') into a dictionary of line_num -> content"""
    lines_dict = {}
    for line in text.splitlines():
        match = re.match(r'^(\d+):\s(.*)', line)
        if match:
            line_num = int(match.group(1))
            content = match.group(2)
            lines_dict[line_num] = content
        elif "<content>" in line or "</content>" in line or "<path>" in line or "<type>" in line:
            continue
    return lines_dict

def recover_file(filename):
    print(f"\n--- Recovering {filename} ---")
    file_chunks = defaultdict(str)
    latest_timestamp = None
    
    with open(main_session_file, 'r', encoding='utf-8') as f:
        for line_str in f:
            try:
                event = json.loads(line_str)
                if event.get("type") == "tool_result" and event.get("tool_name") == "read":
                    content = event.get("content", "")
                    if filename in content:
                        parsed_lines = parse_line_numbers(content)
                        if parsed_lines:
                            # Update our chunks with the latest read lines
                            for line_num, line_content in parsed_lines.items():
                                file_chunks[line_num] = line_content
                                latest_timestamp = event.get("timestamp", "unknown")
            except Exception as e:
                pass
                
    if not file_chunks:
        print(f"Could not find any parsed lines for {filename}")
        return False
        
    # Reconstruct the file
    max_line = max(file_chunks.keys())
    recovered_text = []
    
    missing_lines = []
    for i in range(1, max_line + 1):
        if i in file_chunks:
            recovered_text.append(file_chunks[i])
        else:
            recovered_text.append(f"# WARNING: Line {i} missing from recovery logs")
            missing_lines.append(i)
            
    # Write to temp file
    safe_name = filename.replace("/", "_").replace("\\", "_")
    out_path = output_dir / safe_name
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(recovered_text))
        
    print(f"Recovered {max_line} lines to {out_path}")
    print(f"Latest read timestamp used: {latest_timestamp}")
    if missing_lines:
        print(f"Warning: {len(missing_lines)} lines are missing (could not be found in read logs).")
        if len(missing_lines) < 20:
            print(f"Missing lines: {missing_lines}")
    else:
        print("100% complete recovery of all lines read.")
        
    return True

recover_file("chat_orchestrator.py")
recover_file("worker.py")
recover_file("run_validation.py")
recover_file("tool_param_validation.py")

