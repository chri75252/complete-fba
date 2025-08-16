#!/usr/bin/env python3
"""
Direct fix for state corruption - manually correct the processing state
"""

import sys
import os
import json
from pathlib import Path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def fix_state_corruption():
    """Directly fix the corrupted processing state"""
    print("🔧 Fixing state corruption directly...")
    
    state_file = Path("OUTPUTS/CACHE/processing_states/poundwholesale_co_uk_processing_state.json")
    
    if not state_file.exists():
        print("❌ State file not found")
        return False
    
    try:
        # Load current state
        with open(state_file, 'r', encoding='utf-8') as f:
            state_data = json.load(f)
        
        print("📊 Current state:")
        sep = state_data.get("supplier_extraction_progress", {})
        sp = state_data.get("system_progression", {})
        
        print(f"   • Operational: index={sep.get('current_category_index')}, url={sep.get('current_category_url', '')[:50]}...")
        print(f"   • Tracking: index={sp.get('current_category_index')}, url={sp.get('current_category_url', '')[:50]}...")
        
        # Apply manual correction
        correct_index = 1
        correct_url = "https://www.poundwholesale.co.uk/seasonal/wholesale-winter-essentials"
        
        # Fix supplier_extraction_progress (operational data)
        if "supplier_extraction_progress" in state_data:
            state_data["supplier_extraction_progress"]["current_category_index"] = correct_index
            state_data["supplier_extraction_progress"]["current_category_url"] = correct_url
        
        # Fix system_progression (tracking data)
        if "system_progression" in state_data:
            state_data["system_progression"]["current_category_index"] = correct_index
            state_data["system_progression"]["current_category_url"] = correct_url
        
        # Fix any breadcrumb data
        if "breadcrumb_log" in state_data and isinstance(state_data["breadcrumb_log"], list):
            for entry in state_data["breadcrumb_log"]:
                if isinstance(entry, dict) and "data" in entry:
                    entry_data = entry["data"]
                    if entry_data.get("current_category_index") == 0:
                        entry_data["current_category_index"] = correct_index
                    if "wholesale-halloween" in entry_data.get("current_category_url", ""):
                        entry_data["current_category_url"] = correct_url
        
        # Update timestamp
        from datetime import datetime, timezone
        state_data["last_updated"] = datetime.now(timezone.utc).isoformat()
        
        # Save corrected state
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state_data, f, indent=2, ensure_ascii=False)
        
        print("✅ State corruption fixed:")
        print(f"   • current_category_index: {correct_index}")
        print(f"   • current_category_url: {correct_url}")
        print("💾 Corrected state saved")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing state corruption: {e}")
        return False

def verify_fix():
    """Verify the fix was applied correctly"""
    print("🔧 Verifying fix...")
    
    state_file = Path("OUTPUTS/CACHE/processing_states/poundwholesale_co_uk_processing_state.json")
    
    try:
        with open(state_file, 'r', encoding='utf-8') as f:
            state_data = json.load(f)
        
        sep = state_data.get("supplier_extraction_progress", {})
        sp = state_data.get("system_progression", {})
        
        sep_index = sep.get("current_category_index")
        sep_url = sep.get("current_category_url", "")
        sp_index = sp.get("current_category_index")
        sp_url = sp.get("current_category_url", "")
        
        print(f"📊 After fix:")
        print(f"   • Operational: index={sep_index}, url={sep_url[:50]}...")
        print(f"   • Tracking: index={sp_index}, url={sp_url[:50]}...")
        
        # Check if fix was successful
        winter_url = "wholesale-winter-essentials"
        if (sep_index == 1 and winter_url in sep_url and 
            sp_index == 1 and winter_url in sp_url):
            print("✅ VERIFICATION: Fix successfully applied")
            return True
        else:
            print("❌ VERIFICATION: Fix not properly applied")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying fix: {e}")
        return False

def main():
    """Apply direct state corruption fix"""
    print("🚨 DIRECT STATE CORRUPTION FIX")
    print("=" * 40)
    
    # Apply fix
    fix_success = fix_state_corruption()
    
    if fix_success:
        # Verify fix
        verify_success = verify_fix()
        
        if verify_success:
            print("\n🎉 STATE CORRUPTION SUCCESSFULLY FIXED!")
            print("   The system should now resume from category 1 (winter-essentials)")
            print("   instead of always restarting from category 0 (halloween)")
        else:
            print("\n⚠️ Fix applied but verification failed")
    else:
        print("\n❌ Failed to apply fix")

if __name__ == "__main__":
    main()