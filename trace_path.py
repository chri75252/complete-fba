import os

# What get_base_directory() returns (from the API's CWD)
api_cwd = os.getcwd()
print("API CWD:", api_cwd)

# Check OUTPUTS exists from CWD
outputs_from_cwd = os.path.join(api_cwd, "OUTPUTS")
print("OUTPUTS from CWD exists:", os.path.exists(outputs_from_cwd))

# Actual project path (with trailing dash - verified correct)
actual_project = r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-'
print("Actual project OUTPUTS exists:", os.path.exists(os.path.join(actual_project, "OUTPUTS")))

# The financial reports directory
fin_root_actual = os.path.join(actual_project, "OUTPUTS", "FBA_ANALYSIS", "financial_reports")
print("financial_reports from actual:", fin_root_actual)
print("financial_reports from actual exists:", os.path.exists(fin_root_actual))

# What resolve_paths constructs for this supplier
supplier_hint = 'efghousewares.co.uk__sandbox__4e269fb4'
parts = supplier_hint.split("__", 1)
base_hint = parts[0]
suffix = "__" + parts[1] if len(parts) > 1 else ""

hyphenated_base = base_hint.replace(".", "-").replace("_", "-").lower()
hyphenated_supplier = f"{hyphenated_base}{suffix}"
print("\nhyphenated_supplier constructed:", hyphenated_supplier)

# But the actual folder name on disk is:
actual_folder = "efghousewares-co-uk__sandbox__4e269fb4"
print("Actual folder name on disk:", actual_folder)

# These don't match! Let's see why
print("\nbase_hint:", base_hint)
print("suffix:", suffix)
print("hyphenated_base:", hyphenated_base)
print("Result:", hyphenated_base + suffix)

# The correct folder: efghousewares-co-uk__sandbox__4e269fb4
# The constructed: efghousewares-co-uk__sandbox__4e269fb4 (should match...)

# Actually let's trace step by step
print("\n--- Step by step ---")
print(f"supplier_hint = {supplier_hint!r}")
parts = supplier_hint.split("__", 1)
print(f"parts after split: {parts}")
base_hint = parts[0]
suffix = "__" + parts[1] if len(parts) > 1 else ""
print(f"base_hint: {base_hint!r}")
print(f"suffix: {suffix!r}")

hyphenated_base = base_hint.replace(".", "-").replace("_", "-").lower()
print(f"hyphenated_base: {hyphenated_base!r}")

hyphenated_supplier = f"{hyphenated_base}{suffix}"
print(f"hyphenated_supplier: {hyphenated_supplier!r}")

# Construct the path resolve_paths would try
constructed_path = os.path.join(fin_root_actual, hyphenated_supplier)
print(f"\nConstructed path: {constructed_path}")
print(f"Exists: {os.path.exists(constructed_path)}")

# What the folder actually is
actual_path = os.path.join(fin_root_actual, actual_folder)
print(f"Actual path: {actual_path}")
print(f"Exists: {os.path.exists(actual_path)}")
