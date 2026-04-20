"""Tavily API queries for Phase 2 validation — Bucket B category demand + Bucket C price trends + seasonal signals."""
import json
import urllib.request
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

API_KEY = "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"
URL = "https://api.tavily.com/search"

queries = [
    # Bucket B category demand (3 queries)
    ("B_CAT_1", "UK demand for household cleaning products Amazon bestsellers 2026 Q1"),
    ("B_CAT_2", "UK demand for car air fresheners Little Trees Magic Trees Amazon 2026"),
    ("B_CAT_3", "UK demand for arts crafts supplies birthday candles embroidery thread Amazon 2026"),
    
    # Bucket C price trend checks (3 queries)
    ("C_PRICE_1", "Chef Aid kitchen utensils Amazon UK price trend 2026 ladle thermometer"),
    ("C_PRICE_2", "Kilner clip top jar 1.5L Amazon UK price history 2026"),
    ("C_PRICE_3", "Lynx gift set Amazon UK price trend 2026 Sunset Fresh"),
    
    # Seasonal signals (3 queries)
    ("SEASONAL_1", "UK spring garden products demand forecast April 2026"),
    ("SEASONAL_2", "UK DIY home improvement market trend spring 2026"),
    ("SEASONAL_3", "Amazon UK bestselling household products April 2026 categories"),
]

results = {}

for label, q in queries:
    data = json.dumps({
        "api_key": API_KEY,
        "query": q,
        "search_depth": "advanced",
        "include_answer": True,
        "max_results": 3
    }).encode("utf-8")
    
    req = urllib.request.Request(URL, data=data, headers={"Content-Type": "application/json"})
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            res_content = response.read().decode("utf-8")
            res_json = json.loads(res_content)
            answer = res_json.get("answer", "No answer provided")
            sources = [r.get("url", "") for r in res_json.get("results", [])[:3]]
            results[label] = {"query": q, "answer": answer, "sources": sources}
            print(f"\n[{label}] {q}")
            print(f"Answer: {answer[:300]}")
            print(f"Sources: {', '.join(sources[:2])}")
    except Exception as e:
        results[label] = {"query": q, "answer": f"ERROR: {e}", "sources": []}
        print(f"\n[{label}] ERROR: {e}")

# Save full results
with open('tavily_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print("\nSaved to tavily_results.json")
