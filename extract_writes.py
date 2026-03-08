import json
from pathlib import Path
import os

transcript_dir = Path(r"C:\Users\chris\claude-clean\transcripts")
tf = transcript_dir / "ses_36c74ae8bffetm2R1JkmApf9YE.jsonl"
output_dir = Path("temp/recovered_files")
output_dir.mkdir(parents=True, exist_ok=True)

with open(tf, 'r', encoding='utf-8') as f:
    for line in f:
        if '"tool_name":"serena_create_text_file"' in line or '"tool_name":"write"' in line:
            if "run_validation.py" in line or "tool_param_validation.py" in line:
                try:
                    event = json.loads(line)
                    if event.get("type") == "message":
                        for block in event.get("message", {}).get("content", []):
                            if block.get("type") == "tool_use" and block.get("name") in ["write", "serena_create_text_file"]:
                                inp = block.get("input", {})
                                path = inp.get("filePath") or inp.get("relative_path") or ""
                                content = inp.get("content", "")
                                
                                if "run_validation.py" in path or "tool_param_validation.py" in path:
                                    out_path = output_dir / Path(path).name
                                    with open(out_path, "w", encoding="utf-8") as outf:
                                        outf.write(content)
                                    print(f"Recovered {path} from tool write!")
                except Exception as e:
                    pass
