#!/usr/bin/env python3
"""
Example: Using the Fixed Enhanced State Manager
==============================================

This example demonstrates the correct usage of the fixed state manager
to prevent processing state issues.
"""

from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager

def example_usage():
    """Example of correct state manager usage"""
    
    # Initialize the fixed state manager
    state_manager = FixedEnhancedStateManager("poundwholesale.co.uk")
    
    # 1. Load existing state
    state_loaded = state_manager.load_state()
    
    # 2. CRITICAL: Perform startup analysis ONCE at session start
    # This handles reverse gap detection and prevents index resets
    startup_categories = state_manager.perform_startup_analysis()
    
    print(f"Startup analysis complete. Found {len(startup_categories)} categories")
    
    # 3. Get resumption index (where to start processing)
    resumption_index = state_manager.get_resumption_index()
    print(f"Resuming from index: {resumption_index}")
    
    # 4. During processing: Update discovered products when scraper finds more
    # Example: scraper discovers makeup-supplies has 105 products, not 36
    category_url = "https://www.poundwholesale.co.uk/health-beauty/wholesale-makeup-supplies"
    discovered_products = 105
    state_manager.update_discovered_products_in_category(category_url, discovered_products)
    
    # 5. During processing: Update progress without affecting resumption index
    for i in range(10):  # Process 10 products
        product_url = f"https://example.com/product/{i}"
        
        # Process the product here...
        
        # Update progress (this won't reset the index)
        state_manager.update_processing_progress(increment=1, product_url=product_url)
        
        # Save state preserving interruption capability
        if i % 5 == 0:  # Save every 5 products
            state_manager.save_state(preserve_interruption_state=True)
    
    # 6. When category is completed
    state_manager.mark_category_completed(category_url)
    
    # 7. Get current progress information
    progress = state_manager.get_current_progress()
    print(f"Progress: {progress}")
    
    print("✅ Example completed successfully")

if __name__ == "__main__":
    example_usage()
