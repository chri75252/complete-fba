#!/usr/bin/env python3
"""
State Dump Diagnostic Script - READ-ONLY Analysis
Captures all state sources for inconsistency investigation
"""

import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
import sys

def capture_state_snapshot():
    """Capture comprehensive state snapshot from all sources"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot = {
        "timestamp": timestamp,
        "investigation": "state-consistency-analysis",
        "sources": {},
        "contradictions": {},
        "invariant_violations": []
    }
    
    # 1. Main processing state
    try:
        with open("OUTPUTS/processing_state.json", 'r') as f:
            main_state = json.load(f)
            snapshot["sources"]["main_processing_state"] = {
                "file": "OUTPUTS/processing_state.json",
                "current_category_url": main_state.get("supplier_extraction_progress", {}).get("current_category_url", ""),
                "current_category_index": main_state.get("supplier_extraction_progress", {}).get("current_category_index", 0),
                "products_extracted_total": main_state.get("supplier_extraction_progress", {}).get("products_extracted_total", 0),
                "successful_products": main_state.get("successful_products", 0),
                "total_products": main_state.get("total_products", 0),
                "last_updated": main_state.get("last_updated", ""),
                "system_progression": main_state.get("system_progression", {}),
                "supplier_extraction_progress": main_state.get("supplier_extraction_progress", {})
            }
    except Exception as e:
        snapshot["sources"]["main_processing_state"] = {"error": str(e)}
    
    # 2. Look for other state files
    state_files = []
    for root, dirs, files in os.walk("OUTPUTS"):
        for file in files:
            if "state" in file.lower() or "progress" in file.lower():
                state_files.append(os.path.join(root, file))
    
    for state_file in state_files:
        try:
            if state_file.endswith('.json'):
                with open(state_file, 'r') as f:
                    data = json.load(f)
                    snapshot["sources"][f"file_{os.path.basename(state_file)}"] = {
                        "file": state_file,
                        "current_category_url": extract_nested_value(data, "current_category_url"),
                        "current_category_index": extract_nested_value(data, "current_category_index"),
                        "products_extracted_total": extract_nested_value(data, "products_extracted_total"),
                        "successful_products": extract_nested_value(data, "successful_products"),
                        "last_updated": extract_nested_value(data, "last_updated"),
                        "size_kb": os.path.getsize(state_file) // 1024
                    }
        except Exception as e:
            snapshot["sources"][f"file_{os.path.basename(state_file)}"] = {"error": str(e)}
    
    # 3. Check for SQLite databases
    db_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith('.db') or file.endswith('.sqlite'):
                db_files.append(os.path.join(root, file))
    
    for db_file in db_files:
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            snapshot["sources"][f"db_{os.path.basename(db_file)}"] = {
                "file": db_file,
                "tables": [table[0] for table in tables],
                "size_kb": os.path.getsize(db_file) // 1024
            }
            conn.close()
        except Exception as e:
            snapshot["sources"][f"db_{os.path.basename(db_file)}"] = {"error": str(e)}
    
    # 4. Analyze contradictions
    analyze_contradictions(snapshot)
    
    # 5. Check invariants
    check_invariants(snapshot)
    
    return snapshot

def extract_nested_value(data, key):
    """Extract value from nested dictionary structure"""
    if isinstance(data, dict):
        if key in data:
            return data[key]
        for value in data.values():
            if isinstance(value, dict):
                result = extract_nested_value(value, key)
                if result is not None:
                    return result
    return None

def analyze_contradictions(snapshot):
    """Analyze state contradictions based on evidence"""
    sources = snapshot["sources"]
    contradictions = []
    
    # Extract current_category_url values
    urls = {}
    indices = {}
    products_totals = {}
    successful_products = {}
    
    for source_name, source_data in sources.items():
        if isinstance(source_data, dict) and "error" not in source_data:
            if source_data.get("current_category_url"):
                urls[source_name] = source_data["current_category_url"]
            if source_data.get("current_category_index") is not None:
                indices[source_name] = source_data["current_category_index"]
            if source_data.get("products_extracted_total") is not None:
                products_totals[source_name] = source_data["products_extracted_total"]
            if source_data.get("successful_products") is not None:
                successful_products[source_name] = source_data["successful_products"]
    
    # Check for URL contradictions
    unique_urls = set(urls.values())
    if len(unique_urls) > 1:
        contradictions.append({
            "type": "current_category_url_mismatch",
            "description": "Different sources report different current_category_url values",
            "values": urls,
            "evidence": "Supplier Extraction Progress vs Resume Calculated Data mismatch"
        })
    
    # Check for index contradictions
    unique_indices = set(indices.values())
    if len(unique_indices) > 1:
        contradictions.append({
            "type": "current_category_index_mismatch", 
            "description": "Different sources report different current_category_index values",
            "values": indices
        })
    
    # Check products_extracted_total vs successful_products
    for source in sources:
        if source in products_totals and source in successful_products:
            if products_totals[source] != successful_products[source]:
                contradictions.append({
                    "type": "product_count_mismatch",
                    "description": f"products_extracted_total ({products_totals[source]}) != successful_products ({successful_products[source]})",
                    "source": source,
                    "products_extracted_total": products_totals[source],
                    "successful_products": successful_products[source]
                })
    
    snapshot["contradictions"] = contradictions

def check_invariants(snapshot):
    """Check system invariants"""
    violations = []
    
    # Get main state data
    main_state = snapshot["sources"].get("main_processing_state", {})
    if "error" in main_state:
        violations.append({
            "invariant": "main_state_accessible",
            "violation": "Cannot access main processing state",
            "details": main_state["error"]
        })
        return
    
    # Invariant 1: products_extracted_total should equal successful_products
    products_extracted = main_state.get("products_extracted_total", 0)
    successful_products = main_state.get("successful_products", 0)
    
    if products_extracted != successful_products:
        violations.append({
            "invariant": "products_extracted_total == successful_products",
            "violation": f"{products_extracted} != {successful_products}",
            "severity": "high"
        })
    
    # Invariant 2: current_category_index should be consistent across state sections
    sep = main_state.get("supplier_extraction_progress", {})
    sp = main_state.get("system_progression", {})
    
    sep_index = sep.get("current_category_index")
    sp_index = sp.get("current_category_index")
    
    if sep_index is not None and sp_index is not None and sep_index != sp_index:
        violations.append({
            "invariant": "consistent_category_index",
            "violation": f"supplier_extraction_progress.current_category_index ({sep_index}) != system_progression.current_category_index ({sp_index})",
            "severity": "high"
        })
    
    # Invariant 3: current_category_url should be consistent
    sep_url = sep.get("current_category_url", "")
    sp_url = sp.get("current_category_url", "")
    
    if sep_url and sp_url and sep_url != sp_url:
        violations.append({
            "invariant": "consistent_category_url",
            "violation": f"supplier_extraction_progress.current_category_url ({sep_url}) != system_progression.current_category_url ({sp_url})",
            "severity": "high"
        })
    
    snapshot["invariant_violations"] = violations

def main():
    """Main diagnostic execution"""
    print("🔍 State Consistency Diagnostic - READ-ONLY Analysis")
    print("=" * 60)
    
    # Capture snapshot
    snapshot = capture_state_snapshot()
    
    # Save to artifacts
    timestamp = snapshot["timestamp"]
    output_file = f"artifacts/diagnostics/{timestamp}/state_snapshot.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(snapshot, f, indent=2)
    
    print(f"📊 Snapshot saved to: {output_file}")
    print(f"🕒 Timestamp: {timestamp}")
    print()
    
    # Report findings
    print("📋 STATE SOURCES FOUND:")
    for source_name, source_data in snapshot["sources"].items():
        if isinstance(source_data, dict):
            if "error" in source_data:
                print(f"  ❌ {source_name}: {source_data['error']}")
            else:
                print(f"  ✅ {source_name}: {source_data.get('file', 'N/A')}")
                if "current_category_url" in source_data:
                    print(f"     current_category_url: {source_data['current_category_url']}")
                if "current_category_index" in source_data:
                    print(f"     current_category_index: {source_data['current_category_index']}")
    
    print()
    print("🚨 CONTRADICTIONS DETECTED:")
    if snapshot["contradictions"]:
        for contradiction in snapshot["contradictions"]:
            print(f"  • {contradiction['type']}: {contradiction['description']}")
            if "values" in contradiction:
                for source, value in contradiction["values"].items():
                    print(f"    - {source}: {value}")
    else:
        print("  ✅ No contradictions detected")
    
    print()
    print("⚠️  INVARIANT VIOLATIONS:")
    if snapshot["invariant_violations"]:
        for violation in snapshot["invariant_violations"]:
            print(f"  • {violation['invariant']}: {violation['violation']}")
            if "severity" in violation:
                print(f"    Severity: {violation['severity']}")
    else:
        print("  ✅ No invariant violations detected")
    
    print()
    print("🔧 NEXT STEPS:")
    print("  1. Review snapshot data in artifacts/diagnostics/")
    print("  2. Analyze write paths to identify non-atomic operations")
    print("  3. Design atomic state management solution")
    print("  4. Implement reconciliation mechanism")
    
    return len(snapshot["contradictions"]) + len(snapshot["invariant_violations"])

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)