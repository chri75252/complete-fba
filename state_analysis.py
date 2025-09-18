import json

# Load current state
with open('/mnt/c/Users/chris/desktop/Amazon-FBA-Agent-System-v32 - latest good - Copy (3)/OUTPUTS/CACHE/processing_states/poundwholesale_co_uk_processing_state.json') as f:
    state = json.load(f)

# Load supplier cache to verify
with open('/mnt/c/Users/chris/desktop/Amazon-FBA-Agent-System-v32 - latest good - Copy (3)/OUTPUTS/cached_products/poundwholesale-co-uk_products_cache.json') as f:
    cache = json.load(f)

# Load linking map to verify  
with open('/mnt/c/Users/chris/desktop/Amazon-FBA-Agent-System-v32 - latest good - Copy (3)/OUTPUTS/FBA_ANALYSIS/linking_maps/poundwholesale.co.uk/linking_map.json') as f:
    linking_map = json.load(f)

print('=== CRITICAL INCONSISTENCY ANALYSIS ===')
print(f'State says last_processed_index: {state["last_processed_index"]}')
print(f'State says total_products: {state["total_products"]}')
print(f'Actual supplier cache count: {len(cache)}')
print(f'Actual linking map count: {len(linking_map)}')
print(f'Processed products in state: {len(state["processed_products"])}')

# Check validation issues
print(f'\n=== VALIDATION ISSUES ===')
if len(state['processed_products']) > len(cache):
    print(f'❌ CRITICAL: Processed products ({len(state["processed_products"])}) > Supplier cache ({len(cache)})')
else:
    print(f'✅ Processed products count is reasonable')

if state['last_processed_index'] >= len(cache):
    print(f'❌ CRITICAL: last_processed_index ({state["last_processed_index"]}) >= supplier cache size ({len(cache)})')
else:
    print(f'✅ last_processed_index is within bounds')

if state['total_products'] != len(cache):
    print(f'⚠️  WARNING: total_products ({state["total_products"]}) != actual cache size ({len(cache)})')
else:
    print(f'✅ total_products matches cache size')

# Check linking map vs processed products
processed_count = len(state['processed_products'])
if len(linking_map) > processed_count:
    print(f'⚠️  INFO: Linking map ({len(linking_map)}) > processed products ({processed_count}) - expected in batch processing')
elif len(linking_map) < processed_count:
    print(f'❌ WARNING: Linking map ({len(linking_map)}) < processed products ({processed_count}) - possible data loss')
else:
    print(f'✅ Linking map size reasonable vs processed products')

print(f'\n=== RESUME CAPABILITY ASSESSMENT ===')
if state['last_processed_index'] < len(cache):
    remaining = len(cache) - state['last_processed_index']
    print(f'✅ System can resume: {remaining} products remaining to process')
    print(f'   Next product to process: index {state["last_processed_index"]}')
    if state['last_processed_index'] < len(cache):
        next_product = cache[state['last_processed_index']]
        print(f'   Next product URL: {next_product.get("url", "Unknown")}')
else:
    print(f'❌ CRITICAL: Cannot resume - index out of bounds')