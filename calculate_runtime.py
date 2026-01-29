import os
import re
from datetime import datetime

log_files = [
    "run_custom_poundwholesale_20251203_074818.log",
    "run_custom_poundwholesale_20251203_142758.log",
    "run_custom_poundwholesale_20251204_070824.log",
    "run_custom_poundwholesale_20251204_083943.log",
    "run_custom_poundwholesale_20251204_092814.log",
    "run_custom_poundwholesale_20251204_160113.log",
    "run_custom_poundwholesale_20251204_182806.log",
    "run_custom_poundwholesale_20251204_203844.log"
]

base_path = r"c:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\logs\debug"

def get_timestamp(line):
    match = re.match(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})', line)
    if match:
        return datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S,%f')
    return None

total_duration = 0

print(f"{'File':<50} | {'Start':<25} | {'End':<25} | {'Duration (hrs)':<15}")
print("-" * 120)

for f in log_files:
    path = os.path.join(base_path, f)
    if not os.path.exists(path):
        print(f"{f:<50} | NOT FOUND")
        continue

    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as file:
            first_line = file.readline()
            start_time = get_timestamp(first_line)
            
            # Read last lines efficiently
            file.seek(0, 2)
            file_size = file.tell()
            seek_offset = min(file_size, 10000) # Read last 10KB
            file.seek(file_size - seek_offset)
            last_lines = file.readlines()
            
            end_time = None
            for line in reversed(last_lines):
                ts = get_timestamp(line)
                if ts:
                    end_time = ts
                    break
            
            if start_time and end_time:
                duration = (end_time - start_time).total_seconds()
                total_duration += duration
                print(f"{f:<50} | {str(start_time):<25} | {str(end_time):<25} | {duration/3600:.2f}")
            else:
                print(f"{f:<50} | {str(start_time):<25} | {str(end_time):<25} | ERROR")

    except Exception as e:
        print(f"{f:<50} | Error: {e}")

print("-" * 120)
print(f"Total Active Duration: {total_duration/3600:.2f} hours")
