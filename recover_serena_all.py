import json
from pathlib import Path

transcript_dir = Path(r"C:\Users\chris\claude-clean\transcripts")
transcript_files = [f for f in transcript_dir.iterdir() if f.suffix == '.jsonl']
output_dir = Path("temp/recovered_files")
output_dir.mkdir(parents=True, exist_ok=True)

print(f"Scanning {len(transcript_files)} transcript files for massive serena reads...")

for tf in transcript_files:
    try:
        with open(tf, 'r', encoding='utf-8') as f:
            for line in f:
                if 'serena_read_file' in line:
                    if 'chat_orchestrator.py' in line or 'worker.py' in line:
                        try:
                            data = json.loads(line)
                            if data.get('type') == 'tool_result' and data.get('tool_name') == 'serena_read_file':
                                content = data.get('content', '')
                                if len(content) > 10000: # large file
                                    # Try to figure out which file it is based on contents
                                    if "def _sanitize_chat_history" in content:
                                        name = "chat_orchestrator.py"
                                    elif "def _move_job" in content:
                                        name = "worker.py"
                                    else:
                                        continue
                                        
                                    print(f"Found {name} in {tf.name}! Length: {len(content)}")
                                    with open(output_dir / name, 'w', encoding='utf-8') as outf:
                                        outf.write(content)
                        except Exception as e:
                            pass
    except Exception:
        pass
