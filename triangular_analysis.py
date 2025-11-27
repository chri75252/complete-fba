"""
Triangular Protocol Analysis: Cross-verify linking_map, cache, and manifest data
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

BASE_DIR = Path(__file__).parent

def load_json_safe(path: Path) -> dict:
    """Load JSON with error handling"""
    try:
        if not path.exists():
            return None
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {path}: {e}")
        return None

def analyze_linking_map(supplier_domain: str) -> Tuple[int, List[str], Dict[str, int]]:
    """Count entries in linking_map and group by category"""
    linking_map_path = BASE_DIR / "OUTPUTS" / "FBA_ANALYSIS" / "linking_maps" / supplier_domain / "linking_map.json"
    data = load_json_safe(linking_map_path)

    if not data:
        return 0, [], {}

    total_entries = 0
    all_urls = []
    category_counts = defaultdict(int)

    # Handle both list format and dict with 'entries' key
    entries = data if isinstance(data, list) else data.get('entries', [])

    for entry in entries:
        total_entries += 1
        source_url = entry.get('supplier_url', '')  # Changed from 'source_url'
        all_urls.append(source_url)

        # Extract category from URL
        if '/Category/' in source_url:
            category = source_url.split('/Category/')[1] if '/Category/' in source_url else 'unknown'
        else:
            category = 'unknown'
        category_counts[category] += 1

    return total_entries, all_urls, dict(category_counts)

def analyze_cache(supplier_key: str, target_category_url: str) -> Tuple[int, List[str], int]:
    """Count cached products and filter by category URL"""
    cache_path = BASE_DIR / "OUTPUTS" / "cached_products" / f"{supplier_key}_products_cache.json"
    data = load_json_safe(cache_path)

    if not data:
        return 0, [], 0

    total_cached = len(data)
    category_urls = []
    category_match_count = 0

    for url, product_data in data.items():
        if isinstance(product_data, dict):
            cat_url = product_data.get('category_url', '')
            category_urls.append(cat_url)
            if cat_url == target_category_url:
                category_match_count += 1

    return total_cached, category_urls, category_match_count

def analyze_manifest(supplier_domain: str, category_slug: str) -> Tuple[int, List[str]]:
    """Load manifest and count URLs"""
    manifest_path = BASE_DIR / "OUTPUTS" / "manifests" / supplier_domain / f"{supplier_domain}_Category_{category_slug}_manifest.json"
    data = load_json_safe(manifest_path)

    if not data:
        return 0, []

    urls = data.get('urls', [])
    return len(urls), urls

def analyze_state_file(supplier_key: str) -> dict:
    """Load processing state for analysis"""
    state_path = BASE_DIR / "OUTPUTS" / "CACHE" / "processing_states" / f"{supplier_key}_processing_state.json"
    return load_json_safe(state_path) or {}

def extract_log_claims(log_path: str, search_category: str) -> Dict[str, any]:
    """Extract claims from log file for specific category"""
    claims = {
        'skip_count': None,
        'cached_count': None,
        'full_count': None,
        'resume_ptr': None,
        'denominator': None,
        'filter_invariant_pass': False
    }

    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line in lines:
            if search_category in line:
                if 'FILTER INVARIANT VALIDATED' in line:
                    # Extract: in=401 == skip=393 + cached=5 + full=3
                    if 'skip=' in line and 'cached=' in line:
                        parts = line.split('skip=')[1].split()
                        skip = int(parts[0])
                        cached = int(parts[2])
                        full = int(parts[4])
                        claims['skip_count'] = skip
                        claims['cached_count'] = cached
                        claims['full_count'] = full
                        claims['filter_invariant_pass'] = 'PASS' in line

                if 'FROZEN DENOMINATOR' in line:
                    # Extract: 🔒 FROZEN DENOMINATOR: url = 401
                    parts = line.split('=')
                    if len(parts) >= 2:
                        claims['denominator'] = int(parts[-1].strip())

                if 'Resume from product:' in line:
                    parts = line.split('Resume from product:')
                    if len(parts) >= 2:
                        claims['resume_ptr'] = int(parts[1].strip().split()[0])

    except Exception as e:
        print(f"⚠️ Error reading log {log_path}: {e}")

    return claims

def main():
    print("\n" + "="*80)
    print("[TRIANGULAR PROTOCOL ANALYSIS]")
    print("="*80 + "\n")

    # Configuration
    SUPPLIER_DOMAIN = "angelwholesale.co.uk"
    SUPPLIER_KEY = "angelwholesale-co-uk"
    TARGET_CATEGORY_URL = "https://angelwholesale.co.uk/Category/All-Baby-and-child"
    CATEGORY_SLUG = "All-Baby-and-child"

    # Run timestamps to analyze
    GOOD_RUN_LOG = "logs/debug/run_custom_poundwholesale_20251127_072429.log"
    BAD_RUN_LOG = "logs/debug/run_custom_poundwholesale_20251127_093803.log"

    print(f"[*] Target Category: {TARGET_CATEGORY_URL}")
    print(f"[*] Supplier: {SUPPLIER_DOMAIN}\n")

    # SOURCE 1: Linking Map Analysis
    print("\n" + "-"*80)
    print("SOURCE 1: LINKING MAP ANALYSIS")
    print("-"*80)
    total_links, all_link_urls, category_breakdown = analyze_linking_map(SUPPLIER_DOMAIN)

    # Count specific category in linking map
    target_cat_links = sum(1 for url in all_link_urls if TARGET_CATEGORY_URL in url or f"/Category/{CATEGORY_SLUG}" in url)

    print(f"✅ Total entries in linking_map.json: {total_links}")
    print(f"✅ Entries for '{CATEGORY_SLUG}': {target_cat_links}")
    print(f"\nCategory breakdown (top 5):")
    sorted_cats = sorted(category_breakdown.items(), key=lambda x: x[1], reverse=True)[:5]
    for cat, count in sorted_cats:
        print(f"  - {cat}: {count}")

    # SOURCE 2: Cache Analysis
    print("\n" + "-"*80)
    print("SOURCE 2: CACHE FILE ANALYSIS")
    print("-"*80)
    total_cached, cache_cat_urls, target_cat_cached = analyze_cache(SUPPLIER_KEY, TARGET_CATEGORY_URL)

    print(f"✅ Total cached products: {total_cached}")
    print(f"✅ Cached for target category: {target_cat_cached}")

    # SOURCE 3: Manifest Analysis
    print("\n" + "-"*80)
    print("SOURCE 3: MANIFEST FILE ANALYSIS")
    print("-"*80)
    manifest_count, manifest_urls = analyze_manifest(SUPPLIER_DOMAIN, CATEGORY_SLUG)

    print(f"✅ URLs in manifest: {manifest_count}")

    # CROSS-VERIFICATION
    print("\n" + "="*80)
    print("🔍 CROSS-VERIFICATION: TRUTH VS CLAIMS")
    print("="*80)

    # Ground truth
    print(f"\n📊 GROUND TRUTH (from actual files):")
    print(f"  - Manifest URLs (denominator): {manifest_count}")
    print(f"  - Linking map entries: {target_cat_links}")
    print(f"  - Cached products: {target_cat_cached}")
    print(f"  - Expected remaining: {manifest_count - target_cat_links}")

    # Analyze good run claims
    print(f"\n📋 GOOD RUN CLAIMS ({GOOD_RUN_LOG}):")
    good_claims = extract_log_claims(GOOD_RUN_LOG, TARGET_CATEGORY_URL)
    print(f"  - Skip (linking map): {good_claims['skip_count']}")
    print(f"  - Cached: {good_claims['cached_count']}")
    print(f"  - Full extraction: {good_claims['full_count']}")
    print(f"  - Resume pointer: {good_claims['resume_ptr']}")
    print(f"  - Denominator: {good_claims['denominator']}")
    print(f"  - Filter invariant: {'✅ PASS' if good_claims['filter_invariant_pass'] else '❌ FAIL'}")

    # Verify good run
    if good_claims['skip_count'] is not None:
        skip_match = good_claims['skip_count'] == target_cat_links
        cached_match = good_claims['cached_count'] == target_cat_cached
        denom_match = good_claims['denominator'] == manifest_count
        sum_check = good_claims['skip_count'] + good_claims['cached_count'] + good_claims['full_count'] == good_claims['denominator']

        print(f"\n  🔍 VERIFICATION:")
        print(f"    - Skip matches linking map: {'✅' if skip_match else '❌'} ({good_claims['skip_count']} vs {target_cat_links})")
        print(f"    - Cached matches cache file: {'✅' if cached_match else '❌'} ({good_claims['cached_count']} vs {target_cat_cached})")
        print(f"    - Denominator matches manifest: {'✅' if denom_match else '❌'} ({good_claims['denominator']} vs {manifest_count})")
        print(f"    - Sum invariant: {'✅' if sum_check else '❌'} ({good_claims['skip_count']}+{good_claims['cached_count']}+{good_claims['full_count']}={good_claims['denominator']})")

    # Analyze bad run claims
    print(f"\n📋 BAD RUN CLAIMS ({BAD_RUN_LOG}):")
    bad_claims = extract_log_claims(BAD_RUN_LOG, TARGET_CATEGORY_URL)
    print(f"  - Skip (linking map): {bad_claims['skip_count']}")
    print(f"  - Cached: {bad_claims['cached_count']}")
    print(f"  - Full extraction: {bad_claims['full_count']}")
    print(f"  - Resume pointer: {bad_claims['resume_ptr']}")
    print(f"  - Denominator: {bad_claims['denominator']}")
    print(f"  - Filter invariant: {'✅ PASS' if bad_claims['filter_invariant_pass'] else '❌ FAIL'}")

    # Verify bad run
    if bad_claims['skip_count'] is not None:
        skip_match = bad_claims['skip_count'] == target_cat_links
        cached_match = bad_claims['cached_count'] == target_cat_cached
        denom_match = bad_claims['denominator'] == manifest_count
        sum_check = bad_claims['skip_count'] + bad_claims['cached_count'] + bad_claims['full_count'] == bad_claims['denominator']

        print(f"\n  🔍 VERIFICATION:")
        print(f"    - Skip matches linking map: {'✅' if skip_match else '❌'} ({bad_claims['skip_count']} vs {target_cat_links})")
        print(f"    - Cached matches cache file: {'✅' if cached_match else '❌'} ({bad_claims['cached_count']} vs {target_cat_cached})")
        print(f"    - Denominator matches manifest: {'✅' if denom_match else '❌'} ({bad_claims['denominator']} vs {manifest_count})")
        print(f"    - Sum invariant: {'✅' if sum_check else '❌'} ({bad_claims['skip_count']}+{bad_claims['cached_count']}+{bad_claims['full_count']}={bad_claims['denominator']})")

    # DISCREPANCY ANALYSIS
    print("\n" + "="*80)
    print("🚨 DISCREPANCY ANALYSIS")
    print("="*80)

    if good_claims['skip_count'] and bad_claims['skip_count']:
        skip_diff = bad_claims['skip_count'] - good_claims['skip_count']
        cached_diff = bad_claims['cached_count'] - good_claims['cached_count']

        print(f"\n📊 BETWEEN RUNS:")
        print(f"  - Skip count changed by: {skip_diff} ({good_claims['skip_count']} → {bad_claims['skip_count']})")
        print(f"  - Cached count changed by: {cached_diff} ({good_claims['cached_count']} → {bad_claims['cached_count']})")
        print(f"  - Sum moved from cached to skip: {abs(skip_diff) == abs(cached_diff)}")

        if abs(skip_diff) == abs(cached_diff) and skip_diff < 0:
            print(f"\n  ⚠️ PATTERN DETECTED: {abs(cached_diff)} products migrated from skip → cached")
            print(f"     This suggests linking map is being UNDERCOUNTED in bad run!")

    # Check resume pointer validity
    print(f"\n📊 RESUME POINTER ANALYSIS:")
    if good_claims['resume_ptr'] and good_claims['denominator']:
        good_valid = good_claims['resume_ptr'] <= good_claims['denominator']
        print(f"  - Good run: {good_claims['resume_ptr']}/{good_claims['denominator']} ({'✅ valid' if good_valid else '❌ OUT OF BOUNDS'})")

    if bad_claims['resume_ptr'] and bad_claims['denominator']:
        bad_valid = bad_claims['resume_ptr'] <= bad_claims['denominator']
        print(f"  - Bad run: {bad_claims['resume_ptr']}/{bad_claims['denominator']} ({'✅ valid' if bad_valid else '❌ OUT OF BOUNDS'})")

        if not bad_valid:
            print(f"\n  🚨 CRITICAL ERROR: Resume pointer {bad_claims['resume_ptr']} exceeds denominator {bad_claims['denominator']}")
            print(f"     This will cause category to be skipped entirely!")

    # State file analysis
    print("\n" + "="*80)
    print("STATE FILE ANALYSIS")
    print("="*80)
    state_data = analyze_state_file(SUPPLIER_KEY)

    if state_data:
        sys_prog = state_data.get('system_progression', {})
        if sys_prog:
            cat_idx = sys_prog.get('current_category_index', 0)
            prod_ptr = sys_prog.get('current_product_pointer', 0)
            phase = sys_prog.get('current_phase', 'unknown')

            print(f"  - Current category index: {cat_idx}")
            print(f"  - Current product pointer: {prod_ptr}")
            print(f"  - Current phase: {phase}")

    print("\n" + "="*80)
    print("✅ TRIANGULAR ANALYSIS COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
