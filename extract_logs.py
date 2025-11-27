import json
import os
import re

base_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
log_dir = os.path.join(base_path, "logs", "debug")
output_dir = os.path.join(base_path, "LLM_ANALYSIS_PACKAGE", "logs")

# Define logs to extract with relevant line ranges
logs_to_extract = [
    {
        "file": "run_custom_poundwholesale_20251125_083638.log",
        "desc": "Early morning run showing reprocessing",
        "sections": [
            {"name": "startup", "start": 0, "end": 100},
            {"name": "end_of_run", "start": -200, "end": None}
        ]
    },
    {
        "file": "run_custom_poundwholesale_20251125_154127.log",
        "desc": "Initial run ending at product 297",
        "sections": [
            {"name": "startup", "start": 0, "end": 100},
            {"name": "end_at_298", "start": -200, "end": None}
        ]
    },
    {
        "file": "run_custom_poundwholesale_20251125_155617.log",
        "desc": "Resume run with 397 denominator mismatch",
        "sections": [
            {"name": "startup_and_resume", "start": 0, "end": 200}
        ]
    },
    {
        "file": "run_custom_poundwholesale_20251125_201223.log",
        "desc": "Long run showing workflow deviation at category 8",
        "sections": [
            {"name": "startup", "start": 0, "end": 100},
            {"name": "end_showing_workflow_switch", "start": -300, "end": None}
        ]
    }
]

print("Extracting relevant log sections...")
os.makedirs(output_dir, exist_ok=True)

for log_config in logs_to_extract:
    log_file = os.path.join(log_dir, log_config["file"])
    if not os.path.exists(log_file):
        print(f"SKIP: {log_config['file']} not found")
        continue

    output_file = os.path.join(output_dir, f"EXTRACTED_{log_config['file']}")

    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    with open(output_file, 'w', encoding='utf-8') as out:
        out.write(f"# EXTRACTED SECTIONS FROM: {log_config['file']}\n")
        out.write(f"# Description: {log_config['desc']}\n")
        out.write(f"# Total lines in original: {len(lines)}\n\n")
        out.write("=" * 80 + "\n\n")

        for section in log_config["sections"]:
            out.write(f"\n{'='*80}\n")
            out.write(f"SECTION: {section['name']}\n")
            out.write(f"{'='*80}\n\n")

            start = section["start"] if section["start"] is not None else 0
            end = section["end"] if section["end"] is not None else len(lines)

            if start < 0:
                start = len(lines) + start
            if end and end < 0:
                end = len(lines) + end

            for line_num, line in enumerate(lines[start:end], start=start+1):
                out.write(f"{line_num:6d}: {line}")

            out.write("\n")

    print(f"OK Extracted: {log_config['file']}")

print("\nLog extraction complete!")
