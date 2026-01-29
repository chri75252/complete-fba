import os
import re
from datetime import datetime

log_files = [
    "run_custom_poundwholesale_20251201_031842.log",
    "run_custom_poundwholesale_20251128_071114.log",
    "run_custom_poundwholesale_20251128_071719.log",
    "run_custom_poundwholesale_20251129_113646.log",
    "run_custom_poundwholesale_20251130_033535.log"
]

base_path = r"c:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\logs\debug"

def get_timestamp(line):
    match = re.match(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})', line)
    if match:
        return datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S,%f')
    return None

print(f"{'File':<50} | {'Dur(h)':<6} | {'Prods':<5}")
print("-" * 80)

total_duration = 0
total_products = 0

for f in log_files:
    path = os.path.join(base_path, f)
    if not os.path.exists(path):
        continue

    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as file:
            lines = file.readlines()
            if not lines:
                continue
                
            start_time = get_timestamp(lines[0])
            
            end_time = None
            for line in reversed(lines):
                ts = get_timestamp(line)
                if ts:
                    end_time = ts
                    break
            
            if start_time and end_time:
                duration = (end_time - start_time).total_seconds()
                
                # Count products processed in this log
                # Using "AMAZON PROGRESS:" as the indicator based on log inspection
                products_count = sum(1 for line in lines if "AMAZON PROGRESS:" in line)
                
                if products_count > 0:
                    total_duration += duration
                    total_products += products_count
                    print(f"{f:<50} | {duration/3600:.2f}   | {products_count:<5}")

    except Exception as e:
        print(f"{f:<50} | Error: {e}")

print("-" * 80)
total_hours = total_duration / 3600
print(f"Total Active Hours:      {total_hours:.2f}")
print(f"Total Products Analyzed: {total_products}")

if total_hours > 0:
    print(f"Analysis Speed:          {total_products / total_hours:.2f} products/hour")
