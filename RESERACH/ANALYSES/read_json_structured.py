
import json

with open(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\audit_final.json", 'r') as f:
    data = json.load(f)

print("### BASELINE ###")
print(json.dumps(data['baseline'], indent=2))

print("\n### SCORES ###")
for name, rep in data['reports'].items():
    print(f"Report: {name}")
    print(f"  Score: {rep.get('calculated_score')}")
    print(f"  Valid Rate: {rep.get('validity_rate')}")
    print(f"  Coverage: {rep.get('coverage_pct')}")
    print(f"  Parsed Rows: {rep.get('parsed_row_count')}")
    print("-" * 20)

print(f"\n### WINNER: {data.get('winner')} ###")

winner = data.get('winner')
if winner:
    print("\n### MISSING FROM WINNER (vs PART3) ###")
    print(json.dumps(data['reports'][winner]['missing_top_10_from_part3'], indent=2))

    print("\n### GAPS (In Others but Missing from Winner) ###")
    for k, v in data['gaps'].items():
        if winner in k:
            print(f"--- GAP: {k} ---")
            print(json.dumps(v, indent=2))
