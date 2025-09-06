import json, sys
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: python compare_state_views.py <state_file_path>")
    sys.exit(1)

p = Path(sys.argv[1])
if not p.exists():
    print(f"File not found: {p}")
    sys.exit(1)

data = json.load(p.open(encoding="utf-8"))
leg = data.get("supplier_extraction_progress", {}) or {}
sysv = data.get("system_progression", {}) or {}
rs = data.get("runtime_settings", {}) or {}
meta = data.get("_meta", {}) or {}

print("=== supplier_extraction_progress ===")
print(json.dumps(leg, indent=2)[:4000])
print("\n=== system_progression ===")
print(json.dumps(sysv, indent=2)[:4000])
print("\n=== runtime_settings ===")
print(json.dumps(rs, indent=2))
print("\n=== _meta ===")
print(json.dumps(meta, indent=2))

print("\nQuickchecks:")
for k in ("total_categories","last_processed_index","resumption_index","total_products"):
    print(f"{k:>20}  legacy={leg.get(k)}  system={sysv.get(k)}  runtime={rs.get(k)}  root={data.get(k)}")

print(f"\nSchema version: {meta.get('state_schema_version', 'MISSING')}")
print(f"Config hash: {rs.get('supplier_config_hash', 'MISSING')}")