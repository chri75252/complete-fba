import os
import sys
sys.path.insert(0, r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion')
from dashboard_legacy_streamlit.metrics_core import MetricsLoader

# Same base_dir as test_metrics.py
base_dir = r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion'
print("base_dir:", base_dir)
print("base_dir exists:", os.path.exists(base_dir))

# Check what MetricsLoader.__init__ uses
loader = MetricsLoader(base_dir)
print("loader.base_dir:", loader.base_dir)
print("loader.base_dir exists:", os.path.exists(loader.base_dir))

# Manually trace resolve_paths for this supplier
supplier_hint = 'efghousewares.co.uk__sandbox__4e269fb4'
base_hint = supplier_hint
suffix = ''
if '__' in supplier_hint:
    base_hint, tail = supplier_hint.split('__', 1)
    suffix = f'__{tail}' if tail else '__'

print(f"\nbase_hint: {base_hint!r}")
print(f"suffix: {suffix!r}")

normalized_base = base_hint.replace('.', '_').lower()
hyphenated_base = base_hint.replace('.', '-').replace('_', '-').lower()
normalized_supplier = f"{normalized_base}{suffix}"
hyphenated_supplier = f"{hyphenated_base}{suffix}"
print(f"normalized_supplier: {normalized_supplier!r}")
print(f"hyphenated_supplier: {hyphenated_supplier!r}")

financial_root = os.path.join(loader.base_dir, 'OUTPUTS', 'FBA_ANALYSIS', 'financial_reports')
preferred_dir = os.path.join(financial_root, hyphenated_supplier)
print(f"\nfinancial_root: {financial_root}")
print(f"financial_root exists: {os.path.exists(financial_root)}")
print(f"preferred_dir: {preferred_dir}")
print(f"preferred_dir exists: {os.path.exists(preferred_dir)}")

# Now call the actual method
paths = loader.resolve_paths('efghousewares.co.uk__sandbox__4e269fb4')
print(f"\nresolve_paths returned:")
print(f"  financial_dir: {paths['financial_dir']}")
print(f"  supplier_variants: {paths['supplier_variants']}")
