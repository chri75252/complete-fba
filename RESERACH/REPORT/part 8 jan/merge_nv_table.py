import os

base = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan"
report = os.path.join(base, "PHASEA_MANUAL_REPORT_0110210344.md")
nv_table = os.path.join(base, "NEEDS_VERIFICATION_TABLE.txt")

# Read report
with open(report, 'r', encoding='utf-8') as f:
    content = f.read()

# Read NV table
with open(nv_table, 'r', encoding='utf-8') as f:
    nv_content = f.read()

# Find the section to replace
marker = "## NEEDS VERIFICATION (count=151)"
end_marker = "---\n\n## Corrections Made"

start_idx = content.find(marker)
end_idx = content.find(end_marker)

if start_idx != -1 and end_idx != -1:
    new_section = f"""{marker}

Products requiring 1-2 confirmable details to upgrade to HIGHLY LIKELY or VERIFIED.

```text
{nv_content}
```

"""
    content = content[:start_idx] + new_section + content[end_idx:]

# Write updated report
output = os.path.join(base, "PHASEA_MANUAL_REPORT_0110212453_FULL.md")
with open(output, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Created: {output}")
print(f"NV entries: {nv_content.count('NEEDS VERIFICATION')} rows")
