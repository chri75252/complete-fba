#!/usr/bin/env python3
"""Quick fix for total_products < successful_products issue"""

import json

# Load state
with open("OUTPUTS/processing_state.json", 'r') as f:
    state = json.load(f)

# Fix the issue
successful = state.get("successful_products", 0)
total = state.get("total_products", 0)

if successful > total:
    print(f"Fixing total_products: {total} -> {successful}")
    state["total_products"] = successful
    
    # Save atomically
    with open("OUTPUTS/processing_state.json.tmp", 'w') as f:
        json.dump(state, f, indent=2)
    
    import os
    os.replace("OUTPUTS/processing_state.json.tmp", "OUTPUTS/processing_state.json")
    print("✅ Fixed total_products")
else:
    print("✅ No fix needed")