import json

with open("temp/ses_36c74ae8bffetm2R1JkmApf9YE.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        if '"tool_name":"edit"' in line and '"tool_param_validation.py"' in line and '"tool_output"' in line:
            try:
                data = json.loads(line)
                # the edit tool result includes "after" which is the full file state after the edit!
                if "tool_output" in data and "filediff" in data["tool_output"] and "after" in data["tool_output"]["filediff"]:
                    out = data["tool_output"]["filediff"]["after"]
                    with open("temp/recovered_files/tool_param_validation.py", "w", encoding="utf-8") as outf:
                        outf.write(out)
                    print("Recovered tool_param_validation.py!")
            except Exception as e:
                print(e)
