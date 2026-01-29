
import json
import sys

section = sys.argv[1] if len(sys.argv) > 1 else 'all'

with open(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\audit_final.json", 'r') as f:
    data = json.load(f)

if section == 'baseline':
    print("### BASELINE ###")
    print(json.dumps(data['baseline'], indent=2))

elif section == 'scores':
    print("\n### SCORES ###")
    for name, rep in data['reports'].items():
        print(f"Report: {name}")
        print(f"  Score: {rep.get('calculated_score')}")
        print(f"  Valid Rate: {rep.get('validity_rate')}")
        print(f"  Coverage: {rep.get('coverage_pct')}")
        print(f"  Parsed Rows: {rep.get('parsed_row_count')}")
        print("-" * 20)

elif section == 'winner_missing':
    winner = data.get('winner')
    if winner:
        print(f"\n### WINNER: {winner} MISSING FROM PART3 ###")
        print(json.dumps(data['reports'][winner]['missing_top_10_from_part3'], indent=2))

elif section == 'gaps':
    winner = data.get('winner')
    print("\n### GAPS ###")
    for k, v in data['gaps'].items():
        if winner in k:
            print(f"--- GAP: {k} ---")
            print(json.dumps(v, indent=2))

elif section == 'winner_name':
    print(data.get('winner'))
