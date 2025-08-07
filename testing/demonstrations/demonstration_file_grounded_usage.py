#!/usr/bin/env python3
"""
Demonstration: File-Grounded Processing State Usage
==================================================

This script demonstrates how to use the enhanced file-grounded processing state
in the Amazon FBA Agent System workflow.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager as EnhancedStateManager

def demonstrate_file_grounded_usage():
    """Demonstrate file-grounded state manager usage in a workflow context"""
    
    print("🚀 File-Grounded Processing State Demonstration")
    print("=" * 60)
    
    # Initialize state manager
    supplier_name = "poundwholesale-co-uk"
    state_manager = EnhancedStateManager(supplier_name)
    
    print(f"📊 Supplier: {supplier_name}")
    print()
    
    # 1. Get real-time file-grounded metrics without saving state
    print("1️⃣ Real-time File-Grounded Metrics (without state save):")
    print("-" * 50)
    file_metrics = state_manager.get_file_grounded_metrics()
    
    print(f"📁 Cache file exists: {file_metrics['cache_file_exists']}")
    print(f"📁 Linking map exists: {file_metrics['linking_map_exists']}")
    print(f"📊 Total products (from cache file): {file_metrics['total_products']:,}")
    print(f"📊 Processed products (from linking map): {file_metrics['processed_products']:,}")
    print(f"📋 Categories tracked: {len(file_metrics['category_completion_status'])}")
    
    if file_metrics['processed_products'] > 0 and file_metrics['total_products'] > 0:
        progress_percent = (file_metrics['processed_products'] / file_metrics['total_products']) * 100
        print(f"📈 Overall progress: {progress_percent:.2f}%")
    
    print()
    
    # 2. Enhanced state summary with file-grounded accuracy
    print("2️⃣ Enhanced State Summary (file-grounded accuracy):")
    print("-" * 50)
    state_summary = state_manager.get_state_summary()
    
    print(f"📊 Progress: {state_summary['progress']} ({state_summary['progress_percent']}%)")
    print(f"✅ File-grounded: {state_summary['file_grounded']}")
    print(f"💰 Profitable products: {state_summary['profitable']}")
    print(f"📋 Categories processed: {state_summary['categories_processed']}")
    print(f"📋 Categories with completion data: {state_summary['categories_with_completion']}")
    print(f"❌ Errors logged: {state_summary['errors']}")
    print()
    
    # 3. Category completion breakdown (top 10 categories)
    print("3️⃣ Category Completion Breakdown (Top 10):")
    print("-" * 50)
    category_completion = file_metrics['category_completion_status']
    
    # Sort categories by completion percentage (lowest first to show gaps)
    sorted_categories = sorted(
        category_completion.items(),
        key=lambda x: (x[1]['percent'], -x[1]['total'])  # Sort by percent, then by total (desc)
    )
    
    for i, (category_url, status) in enumerate(sorted_categories[:10]):
        category_name = category_url.split('/')[-1] if '/' in category_url else category_url
        print(f"  {i+1:2d}. {category_name:<35} {status['processed']:4d}/{status['total']:4d} ({status['percent']:6.1f}%)")
    
    print()
    
    # 4. Gap processing initialization with file-grounded metrics
    print("4️⃣ Gap Processing Initialization:")
    print("-" * 50)
    
    # Calculate gap size
    gap_size = max(0, file_metrics['total_products'] - file_metrics['processed_products'])
    print(f"📊 Calculated gap size: {gap_size:,} products")
    
    if gap_size > 0:
        print("🔄 Would initialize gap processing for remaining products...")
        # In actual workflow, you would call:
        # state_manager.start_gap_processing()
        print("   (Gap processing initialization skipped in demo)")
    else:
        print("✅ No gap detected - all products have been processed!")
    
    print()
    
    # 5. File-grounded state save demonstration
    print("5️⃣ File-Grounded State Save:")
    print("-" * 50)
    print("💾 Saving state with file-grounded calculations...")
    
    # This will recalculate all totals from actual files before saving
    state_manager.save_state()
    
    print("✅ State saved with accurate file-based totals!")
    print(f"   • Total products: {state_manager.state_data['total_products']:,}")
    print(f"   • Last processed index: {state_manager.state_data['last_processed_index']:,}")
    print(f"   • Category completion entries: {len(state_manager.state_data.get('gap_processing', {}).get('category_completion_status', {}))}")
    
    print()
    
    # 6. Benefits summary
    print("6️⃣ Key Benefits of File-Grounded Processing:")
    print("-" * 50)
    print("✅ Always accurate - totals calculated from actual files on disk")
    print("✅ Handles file inconsistencies - detects when linking map > cache")
    print("✅ Category progress tracking - shows completion per category")
    print("✅ Real-time metrics - get current status without saving state")
    print("✅ Automatic gap detection - calculates remaining work accurately")
    print("✅ State validation - metadata tracks file existence and check times")
    
    print()
    print("🎉 File-grounded processing state demonstration completed!")

if __name__ == "__main__":
    demonstrate_file_grounded_usage()