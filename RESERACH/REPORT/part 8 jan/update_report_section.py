import json

# Read current report
with open('FINAL_COMPREHENSIVE_REPORT_20260113.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Strip existing Section 5 if present
split_marker = "## SECTION 5:"
if split_marker in content:
    content = content.split(split_marker)[0]

# Read new good candidates
with open('candidates_list.json', 'r', encoding='utf-8') as f:
    candidates = json.load(f)

# Create new section
section = "## SECTION 5: RECOMMENDED FOR NEXT BATCH VERIFICATION (Top 20 of 616 High-Confidence)\n\n"
section += "*Unverified products from source file showing strong matches (Brand Match + Word Overlap) and positive profit.*\n\n"
section += "| Score | ASIN | Profit | Supplier Title | Amazon Title | Reason |\n"
section += "|-------|------|--------|----------------|--------------|--------|\n"

for c in candidates[:20]:
    sup = c['supplier_title'][:35].replace('|', '')
    amz = c['amazon_title'][:35].replace('|', '')
    score = int(c['score'])
    profit = c['net_profit']
    reason = c['reason']
    asin = c['asin']
    section += f"| {score} | {asin} | £{profit:.2f} | {sup}... | {amz}... | {reason} |\n"

# Write back
with open('FINAL_COMPREHENSIVE_REPORT_20260113.md', 'w', encoding='utf-8') as f:
    f.write(content + section)

print("Report updated with clean Section 5.")
