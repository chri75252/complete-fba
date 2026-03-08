import json

with open("temp/ses_36c74ae8bffetm2R1JkmApf9YE.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        if '"command":"cat control_plane/tools/run_validation.py"' in line and '"tool_output"' in line:
            try:
                data = json.loads(line)
                out = data["tool_output"]["output"]
                with open("temp/recovered_files/run_validation.py", "w", encoding="utf-8") as outf:
                    outf.write(out)
                print("Recovered run_validation.py!")
            except Exception as e:
                print(e)
