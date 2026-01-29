
import json

path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\finale\part 2\audit_v2_out.json"

try:
    with open(path, 'r') as f:
        # File contains log/print outputs before JSON, e.g. "Reading PART3..."
        content = f.read()
        
    # Extract JSON part
    json_str = content.split("RESULTS_START")[1].split("RESULTS_END")[0].strip()
    data = json.load(json_str) # wait, json.load takes a file pointer, json.loads takes a string
    data = json.loads(json_str)
    
    print("\nPARSED RESULTS:")
    for d in data:
        print(f"REPORT: {d['name']}")
        print(f"  Valid Found: {d['valid_found']}")
        print(f"  Recall: {d['recall']:.2%}")
        print(f"  Accuracy: {d['accuracy']:.2%}")
        print("-" * 15)
        
except Exception as e:
    print(e)
