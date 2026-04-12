import os

base_dir = r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion'

financial_root = os.path.join(base_dir, "OUTPUTS", "FBA_ANALYSIS", "financial_reports")
print("financial_root exists:", os.path.exists(financial_root))
if os.path.exists(financial_root):
    subdirs = [d for d in os.listdir(financial_root) if 'efghousewares' in d.lower()]
    print("efghousewares subdirs:", subdirs)

supplier_hint = 'efghousewares.co.uk__sandbox__4e269fb4'
base_hint = supplier_hint
suffix = '__sandbox__4e269fb4'
hyphenated_base = base_hint.replace(".", "-").replace("_", "-").lower()
hyphenated_supplier = f"{hyphenated_base}{suffix}"
print("hyphenated_supplier:", hyphenated_supplier)

preferred_dir = os.path.join(financial_root, hyphenated_supplier)
print("preferred_dir:", preferred_dir)
print("preferred_dir exists:", os.path.exists(preferred_dir))

# What resolve_paths actually does
normalized_base = base_hint.replace(".", "_").lower()
normalized_supplier = f"{normalized_base}{suffix}"
print("normalized_supplier:", normalized_supplier)

# Try the dotted form path
dotted = supplier_hint  # efghousewares.co.uk__sandbox__4e269fb4
dotted_dir = os.path.join(financial_root, dotted)
print("dotted_dir:", dotted_dir)
print("dotted_dir exists:", os.path.exists(dotted_dir))

# List all subdirs in financial_reports
print("\nAll subdirs in financial_reports:")
for d in sorted(os.listdir(financial_root)):
    print(f"  {d}")
