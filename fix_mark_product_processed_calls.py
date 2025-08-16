#!/usr/bin/env python3
"""
Script to fix all mark_product_processed calls to include source_category_url parameter
"""

import re
import sys

def fix_mark_product_processed_calls(file_path):
    """Fix all mark_product_processed calls in the file"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match mark_product_processed calls that don't already have 3 parameters
    # This matches calls with exactly 2 parameters (url, status)
    pattern = r'(\s+)self\.state_manager\.mark_product_processed\(([^,]+),\s*([^,)]+)\)(?!\s*,)'
    
    def replacement(match):
        indent = match.group(1)
        url_param = match.group(2)
        status_param = match.group(3)
        
        # Add source_category_url extraction before the call
        source_line = f"{indent}source_category_url = product_data.get('source_url', 'unknown')\n"
        fixed_call = f"{indent}self.state_manager.mark_product_processed({url_param}, {status_param}, source_category_url)"
        
        return source_line + fixed_call
    
    # Apply the replacement
    fixed_content = re.sub(pattern, replacement, content)
    
    # Count how many replacements were made
    original_count = len(re.findall(r'mark_product_processed\([^,]+,\s*[^,)]+\)(?!\s*,)', content))
    fixed_count = len(re.findall(r'mark_product_processed\([^,]+,\s*[^,)]+,\s*source_category_url\)', fixed_content))
    
    print(f"Found {original_count} calls that needed fixing")
    print(f"Fixed {fixed_count} calls with source_category_url parameter")
    
    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    return fixed_count

if __name__ == "__main__":
    file_path = "tools/passive_extraction_workflow_latest.py"
    fixed_count = fix_mark_product_processed_calls(file_path)
    print(f"✅ Successfully fixed {fixed_count} mark_product_processed calls")