import json
import re
import os
from pathlib import Path
from collections import defaultdict

transcript_dir = Path(r"C:\Users\chris\claude-clean\transcripts")
# Process recent transcripts
transcript_files = [
    f for f in transcript_dir.iterdir() 
    if f.suffix == '.jsonl' and f.stat().st_mtime > 1740000000 
]

output_dir = Path("temp/recovered_files")
output_dir.mkdir(parents=True, exist_ok=True)

# Try to extract the whole file from the serena_read_file tool or bash 'cat' outputs
target_files = [
    "control_plane/chat_orchestrator.py",
    "control_plane/worker.py", 
    "control_plane/tools/run_validation.py",
    "control_plane/tools/tool_param_validation.py"
]

print("Hunting for exact file contents...")
# We will use simple substring matching on the raw JSON lines to find large blocks of code
for tf in transcript_files:
    with open(tf, 'r', encoding='utf-8') as f:
        for line in f:
            if "def _sanitize_chat_history" in line and "def execute_tool_call" in line:
                # We found a chunk containing chat_orchestrator.py
                print(f"Found massive chunk of chat_orchestrator in {tf.name}")
                with open(output_dir / f"raw_chunk_chat_orch_{tf.name}.txt", "w", encoding="utf-8") as out:
                    out.write(line)
            
            if "def validate_run_integrity" in line and "missing_expected_files" in line:
                print(f"Found chunk of run_validation in {tf.name}")
                with open(output_dir / f"raw_chunk_run_val_{tf.name}.txt", "w", encoding="utf-8") as out:
                    out.write(line)
                    
            if "_expected_outputs_for_standard_job" in line:
                print(f"Found _expected_outputs_for_standard_job in {tf.name}")
                with open(output_dir / f"raw_chunk_expected_outs_{tf.name}.txt", "w", encoding="utf-8") as out:
                    out.write(line)
