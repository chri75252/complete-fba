import json
import re
from pathlib import Path

# The user explicitly said the transcripts are in:
transcript_dir = Path(r"C:\Users\chris\claude-clean\transcripts")

def extract_from_transcripts():
    output_dir = Path("temp/recovered_files")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # We want the newest files first
    files = sorted([f for f in transcript_dir.iterdir() if f.suffix == '.jsonl'], 
                  key=lambda x: x.stat().st_mtime, reverse=True)
                  
    print(f"Scanning {len(files)} transcript files from newest to oldest...")
    
    found_worker = False
    found_chat_orch = False
    found_run_val = False
    found_tool_val = False
    
    for tf in files:
        if found_worker and found_chat_orch and found_run_val and found_tool_val:
            break
            
        with open(tf, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                    
                # Look for successful file edits (which output the full file diff)
                if '"tool_name":"edit"' in line and '"after":' in line:
                    try:
                        data = json.loads(line)
                        if data.get("type") == "tool_result" and "filediff" in data.get("tool_output", {}):
                            filename = data["tool_output"]["filediff"].get("file", "")
                            content = data["tool_output"]["filediff"].get("after", "")
                            
                            if content:
                                if "worker.py" in filename and not found_worker:
                                    print(f"[{tf.name}] Recovered worker.py!")
                                    with open(output_dir / "worker.py", "w", encoding="utf-8") as out:
                                        out.write(content)
                                    found_worker = True
                                    
                                elif "chat_orchestrator.py" in filename and not found_chat_orch:
                                    print(f"[{tf.name}] Recovered chat_orchestrator.py!")
                                    with open(output_dir / "chat_orchestrator.py", "w", encoding="utf-8") as out:
                                        out.write(content)
                                    found_chat_orch = True
                                    
                                elif "tool_param_validation.py" in filename and not found_tool_val:
                                    print(f"[{tf.name}] Recovered tool_param_validation.py!")
                                    with open(output_dir / "tool_param_validation.py", "w", encoding="utf-8") as out:
                                        out.write(content)
                                    found_tool_val = True
                    except Exception as e:
                        pass
                
                # Look for successful bash reads (cat)
                elif '"command":"cat control_plane/tools/run_validation.py"' in line:
                    try:
                        data = json.loads(line)
                        if data.get("type") == "tool_result" and "output" in data.get("tool_output", {}):
                            content = data["tool_output"]["output"]
                            if content and not found_run_val:
                                print(f"[{tf.name}] Recovered run_validation.py!")
                                with open(output_dir / "run_validation.py", "w", encoding="utf-8") as out:
                                    out.write(content)
                                found_run_val = True
                    except Exception as e:
                        pass
                        
                # Look for write tool usage
                elif '"tool_name":"write"' in line or '"tool_name":"serena_create_text_file"' in line:
                    try:
                        data = json.loads(line)
                        if data.get("type") == "tool_use":
                            inp = data.get("tool_input", {})
                            path = str(inp.get("filePath", inp.get("relative_path", "")))
                            content = inp.get("content", "")
                            
                            if content:
                                if "run_validation.py" in path and not found_run_val:
                                    print(f"[{tf.name}] Recovered run_validation.py from write tool!")
                                    with open(output_dir / "run_validation.py", "w", encoding="utf-8") as out:
                                        out.write(content)
                                    found_run_val = True
                    except Exception:
                        pass

    print("\nRecovery Status:")
    print(f"chat_orchestrator.py: {'FOUND' if found_chat_orch else 'MISSING'}")
    print(f"worker.py: {'FOUND' if found_worker else 'MISSING'}")
    print(f"run_validation.py: {'FOUND' if found_run_val else 'MISSING'}")
    print(f"tool_param_validation.py: {'FOUND' if found_tool_val else 'MISSING'}")

if __name__ == "__main__":
    extract_from_transcripts()
