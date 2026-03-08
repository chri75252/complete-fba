import json
import re
from pathlib import Path

def parse_line_numbers(text):
    lines_dict = {}
    for line in text.splitlines():
        match = re.match(r'^(\d+):\s(.*)', line)
        if match:
            lines_dict[int(match.group(1))] = match.group(2)
        elif "<content>" in line or "</content>" in line or "<path>" in line or "<type>" in line:
            continue
        elif line == "":
            pass # ignore blank lines that don't have numbers
    return lines_dict

def process_file(raw_json_path, output_filename):
    print(f"\nProcessing {raw_json_path}")
    if not Path(raw_json_path).exists():
        print("File not found")
        return
        
    with open(raw_json_path, 'r', encoding='utf-8') as f:
        data = json.loads(f.read())
        
    content = data.get("content", "")
    
    # If the tool is 'read', it uses the line numbered format
    if data.get("tool_name") == "read":
        parsed = parse_line_numbers(content)
        if not parsed:
            print("Could not parse line numbers.")
            return
            
        max_line = max(parsed.keys())
        out_lines = []
        for i in range(1, max_line + 1):
            if i in parsed:
                out_lines.append(parsed[i])
            else:
                out_lines.append(f"# WARNING: Line {i} missing")
                
        out_path = Path("temp/recovered_files") / output_filename
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(out_lines))
        print(f"Recovered {max_line} lines to {out_path}")

process_file("temp/recovered_files/chat_orchestrator.py_raw.json", "chat_orchestrator.py")
process_file("temp/recovered_files/run_validation.py_raw.json", "run_validation.py")
process_file("temp/recovered_files/tool_param_validation.py_raw.json", "tool_param_validation.py")

