
import json

with open(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\audit_final.json", 'r') as f:
    data = json.load(f)

winner = data.get('winner')
print(f"Winner: {winner}")
for k, v in data['gaps'].items():
    if winner in k and v:
        other = k.replace(f"_MissingFrom_{winner}", "").replace("In_", "")
        print(f"\n--- GAP: Present in {other} (Top 3) ---\n")
        # limit to 3 to fit buffer
        for item in v[:3]: 
            print(f"ASIN: {item['ASIN']}")
            print(f"Title: {item['Title']}")
            print(f"Profit: {item['Profit']}")
            print(f"Status: {item['Status']}")
            print("...")
