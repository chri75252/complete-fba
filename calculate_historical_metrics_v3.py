import os
import re
from datetime import datetime

log_files = [
    "run_custom_poundwholesale_20251202_092353.log",
    "run_custom_poundwholesale_20251201_102354.log",
    "run_custom_poundwholesale_20251201_031842.log"
]

base_path = r"c:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\logs\debug"

def get_timestamp(line):
    match = re.match(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})', line)
    if match:
        return datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S,%f')
    return None

print(f"{'File':<50} | {'Dur(h)':<6} | {'Amz':<5} | {'Sup':<5} | {'Proc':<5}")
print("-" * 90)

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
                
                amz_count = sum(1 for line in lines if "AMAZON PROGRESS:" in line)
                sup_count = sum(1 for line in lines if "SUPPLIER PROGRESS:" in line)
                proc_count = sum(1 for line in lines if "PROGRESS: Product" in line)
                
                # Use the max of these as the "products processed" count for this file
                # effectively assuming one main phase per file or non-overlapping counts
                # actually, "PROGRESS: Product" might be the most reliable for recent versions
                # but let's sum them if they look distinct, or just take the max to be safe/conservative
                
                count = max(amz_count, sup_count, proc_count)
                
                if count > 0:
                    total_duration += duration
                    total_products += count
                    print(f"{f:<50} | {duration/3600:.2f}   | {amz_count:<5} | {sup_count:<5} | {proc_count:<5}")

    except Exception as e:
        print(f"{f:<50} | Error: {e}")

print("-" * 90)
total_hours = total_duration / 3600
print(f"Total Active Hours:      {total_hours:.2f}")
print(f"Total Products Analyzed: {total_products}")

if total_hours > 0:
    print(f"Analysis Speed:          {total_products / total_hours:.2f} products/hour")
