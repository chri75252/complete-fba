#!/usr/bin/env python3
"""
WORKING EXAMPLE: wholesaletradingsupplies.com supplier with .com domain in config
but .co.uk operational naming for consistency.

This example shows the CORRECT setup where:
- Configuration uses actual domain (.com)
- Operational files use .co.uk convention
"""

# Domain extraction example
from urllib.parse import urlparse

# Extract domain from actual supplier URL
supplier_url = "https://wholesaletradingsupplies.com"
extracted_domain = urlparse(supplier_url).hostname  # Result: wholesaletradingsupplies.com

# Configuration MUST use actual domain
config_domain = extracted_domain  # wholesaletradingsupplies.com

# Operational naming uses .co.uk convention
operational_name = "wholesaletradingsupplies-co-uk"

print(f"URL: {supplier_url}")
print(f"Extracted domain: {extracted_domain}")
print(f"Config domain: {config_domain}")
print(f"Operational name: {operational_name}")
print()

# Show the complete setup
print("✅ CORRECT SETUP:")
print(f"  Config file: {config_domain}.json")
print(f"  Config supplier_id: {config_domain}")
print(f"  System config supplier_name: {config_domain}")
print(f"  Runner script: run_custom_{operational_name}.py")
print(f"  Cache file: {operational_name}_products_cache.json")
print(f"  Linking map dir: {config_domain}/")
print(f"  State file: {operational_name.replace('-', '_')}_processing_state.json")

# Validation checklist
print("\n📋 VALIDATION CHECKLIST:")
print(f"  ✓ Config filename uses actual domain: {config_domain}.json")
print(f"  ✓ Config supplier_id uses actual domain: {config_domain}")
print(f"  ✓ System config uses actual domain: {config_domain}")
print(f"  ✓ Runner uses hyphen-form: {operational_name}")
print(f"  ✓ Cache uses hyphen-form: {operational_name}")
print(f"  ✓ Linking map uses dot-form: {config_domain}/")
print(f"  ✓ State file uses underscore-form: {operational_name.replace('-', '_')}")