import json, os

base = r'OUTPUTS\FBA_ANALYSIS\linking_maps\efghousewares.co.uk'
results = []

for f in sorted(os.listdir(base)):
    if not f.endswith('.json'):
        continue
    fpath = os.path.join(base, f)
    fsize = os.path.getsize(fpath)
    if fsize < 10:
        results.append((f, 0, fsize, "EMPTY"))
        continue
    try:
        with open(fpath, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
        count = len(data) if isinstance(data, list) else len(data.keys()) if isinstance(data, dict) else 'N/A'
        results.append((f, count, fsize, "OK"))
    except Exception as e:
        # Try counting by rough method
        try:
            with open(fpath, 'r', encoding='utf-8', errors='replace') as fh:
                content = fh.read()
            # Count "supplier_ean" or "amazon_asin" occurrences as proxy
            count_approx = content.count('"amazon_asin"')
            results.append((f, f"~{count_approx} (approx, JSON broken)", fsize, f"PARSE_ERROR: {str(e)[:60]}"))
        except Exception as e2:
            results.append((f, "UNKNOWN", fsize, f"READ_ERROR: {str(e2)[:60]}"))

print(f"{'File':<45} {'Entries':<35} {'Size':>12}  Status")
print("-" * 120)
for name, count, size, status in sorted(results, key=lambda x: x[2]):
    print(f"{name:<45} {str(count):<35} {size:>12,}  {status}")
