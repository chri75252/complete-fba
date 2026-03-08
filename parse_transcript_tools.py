import json
import re
from pathlib import Path
from collections import defaultdict

transcript_dir = Path(r"C:\Users\chris\claude-clean\transcripts")
# Process all recent transcripts from today
transcript_files = [
    f for f in transcript_dir.iterdir() 
    if f.suffix == '.jsonl' and f.stat().st_mtime > 1740000000 
]

output_dir = Path("temp/recovered_files")
output_dir.mkdir(parents=True, exist_ok=True)

def parse_line_numbers(text):
    lines_dict = {}
    for line in text.splitlines():
        match = re.match(r'^(\d+):\s(.*)', line)
        if match:
            line_num = int(match.group(1))
            lines_dict[line_num] = match.group(2)
    return lines_dict

file_chunks = {
    "chat_orchestrator.py": defaultdict(str),
    "worker.py": defaultdict(str),
    "run_validation.py": defaultdict(str),
    "tool_param_validation.py": defaultdict(str),
}

print(f"Scanning {len(transcript_files)} transcripts...")
for tf in transcript_files:
    with open(tf, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                event = json.loads(line)
                # Messages from user containing tool results
                if event.get("type") == "message" and event.get("message", {}).get("role") == "user":
                    for block in event.get("message", {}).get("content", []):
                        if block.get("type") == "tool_result":
                            for text_block in block.get("content", []):
                                text = text_block.get("text", "")
                                for target in file_chunks.keys():
                                    if target in text:
                                        parsed = parse_line_numbers(text)
                                        for ln, lc in parsed.items():
                                            file_chunks[target][ln] = lc
                # Direct tool results
                if event.get("type") == "tool_result":
                    text = str(event.get("content", ""))
                    for target in file_chunks.keys():
                        if target in text:
                            parsed = parse_line_numbers(text)
                            for ln, lc in parsed.items():
                                file_chunks[target][ln] = lc
            except Exception:
                pass

for target, chunks in file_chunks.items():
    if not chunks:
        print(f"No parsed lines found for {target}")
        continue
        
    max_line = max(chunks.keys())
    recovered_text = []
    missing_lines = []
    
    for i in range(1, max_line + 1):
        if i in chunks:
            recovered_text.append(chunks[i])
        else:
            recovered_text.append(f"# WARNING: Line {i} missing from recovery logs")
            missing_lines.append(i)
            
    out_path = output_dir / target.replace("/", "_").replace("\\", "_")
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(recovered_text))
        
    print(f"\nRecovered {max_line} lines to {out_path}")
    if missing_lines:
        print(f"Missing {len(missing_lines)} lines.")
    else:
        print("100% complete recovery of all lines read.")

