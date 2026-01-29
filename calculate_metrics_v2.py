import os
import re
import json
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
linking_map_path = r"c:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\FBA_ANALYSIS\linking_maps\angelwholesale.co.uk\linking_map.json"

def get_timestamp(line):
    match = re.match(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})', line)
    if match:
        return datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S,%f')
    return None

# Load Linking Map
print("Loading linking map...")
with open(linking_map_path, 'r', encoding='utf-8') as f:
    linking_data = json.load(f)

match_timestamps = []
for item in linking_data:
    if 'created_at' in item:
        try:
            ts = datetime.strptime(item['created_at'], '%Y-%m-%dT%H:%M:%S.%f')
            match_timestamps.append(ts)
        except:
            pass
match_timestamps.sort()
print(f"Loaded {len(match_timestamps)} matches.")

total_duration = 0
total_products_processed = 0
total_matches_in_window = 0

print(f"{'File':<50} | {'Dur(h)':<6} | {'Prods':<5} | {'Matches':<7}")
print("-" * 80)

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
            
            # Find end time (scan backwards)
            end_time = None
            for line in reversed(lines):
                ts = get_timestamp(line)
                if ts:
                    end_time = ts
                    break
            
            if start_time and end_time:
                duration = (end_time - start_time).total_seconds()
                total_duration += duration
                
                # Count products processed in this log
                # Looking for "PROGRESS: Product"
                products_count = sum(1 for line in lines if "PROGRESS: Product" in line)
                total_products_processed += products_count
                
                # Count matches in this time window
                matches_count = sum(1 for ts in match_timestamps if start_time <= ts <= end_time)
                total_matches_in_window += matches_count
                
                print(f"{f:<50} | {duration/3600:.2f}   | {products_count:<5} | {matches_count:<7}")

    except Exception as e:
        print(f"{f:<50} | Error: {e}")

print("-" * 80)
total_hours = total_duration / 3600
print(f"Total Active Hours:      {total_hours:.2f}")
print(f"Total Products Analyzed: {total_products_processed}")
print(f"Total Matches Found:     {total_matches_in_window}")

if total_hours > 0:
    print(f"Analysis Speed:          {total_products_processed / total_hours:.2f} products/hour")
    print(f"Match Speed:             {total_matches_in_window / total_hours:.2f} matches/hour")
    if total_products_processed > 0:
        print(f"Match Rate:              {(total_matches_in_window / total_products_processed * 100):.1f}%")
