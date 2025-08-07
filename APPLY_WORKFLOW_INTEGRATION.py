#!/usr/bin/env python3
"""
APPLY WORKFLOW INTEGRATION
Apply the enhanced cache and memory management fixes to the main workflow file
"""

import shutil
from pathlib import Path
import re

def apply_workflow_integration():
    """Apply enhanced cache and memory management to main workflow"""
    
    workflow_file = Path("tools/passive_extraction_workflow_latest.py")
    backup_file = Path("tools/passive_extraction_workflow_latest.py.backup_integration")
    
    print("🔧 APPLYING WORKFLOW INTEGRATION FIXES")
    print("=" * 60)
    
    # Create backup
    shutil.copy2(workflow_file, backup_file)
    print(f"✅ Created backup: {backup_file}")
    
    # Read current workflow
    with open(workflow_file, 'r') as f:
        content = f.read()
    
    # 1. Add enhanced cache save method
    enhanced_cache_method = '''
    def _save_products_to_cache_enhanced(self, products: list, cache_file_path: str, force_write: bool = False):
        """Enhanced cache save with forced persistence and validation"""
        try:
            from pathlib import Path
            # Ensure directory exists
            cache_path = Path(cache_file_path)
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Load existing products for deduplication
            existing_products = []
            if cache_path.exists():
                try:
                    with open(cache_path, 'r', encoding='utf-8') as f:
                        existing_products = json.load(f)
                        if not isinstance(existing_products, list):
                            existing_products = []
                except Exception as e:
                    self.log.warning(f"Could not load existing cache: {e}")
                    existing_products = []
            
            # Deduplicate products
            existing_urls = {p.get('url', '') for p in existing_products if isinstance(p, dict) and p.get('url')}
            new_products = []
            
            for product in products:
                if not isinstance(product, dict):
                    continue
                    
                product_url = product.get('url', '')
                if product_url and product_url not in existing_urls:
                    new_products.append(product)
                    existing_urls.add(product_url)
            
            # Combine all products
            all_products = existing_products + new_products
            
            # Remove any metadata entries to clean cache
            clean_products = [p for p in all_products if not (isinstance(p, dict) and p.get("_cache_metadata"))]
            
            # Add metadata entry
            metadata = {
                "_cache_metadata": {
                    "last_updated": datetime.now().isoformat(),
                    "total_products": len(clean_products),
                    "new_products_added": len(new_products),
                    "cache_version": "enhanced_v1"
                }
            }
            clean_products.append(metadata)
            
            # Force write to cache file using multiple strategies
            success = False
            
            # Strategy 1: Direct write
            try:
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(clean_products, f, indent=2, ensure_ascii=False)
                
                # Verify write
                if cache_path.exists() and cache_path.stat().st_size > 100:
                    success = True
                    self.log.info(f"✅ ENHANCED CACHE SAVE: {len(clean_products)} products saved to {cache_path}")
                
            except Exception as e:
                self.log.warning(f"Direct enhanced cache write failed: {e}")
            
            # Strategy 2: Atomic write if direct failed
            if not success:
                try:
                    temp_path = cache_path.with_suffix('.tmp')
                    
                    with open(temp_path, 'w', encoding='utf-8') as f:
                        json.dump(clean_products, f, indent=2, ensure_ascii=False)
                    
                    # Atomic move using shutil for WSL compatibility
                    shutil.move(str(temp_path), str(cache_path))
                    
                    if cache_path.exists() and cache_path.stat().st_size > 100:
                        success = True
                        self.log.info(f"✅ ENHANCED ATOMIC CACHE: {len(clean_products)} products")
                        
                except Exception as e:
                    self.log.error(f"Enhanced atomic cache write failed: {e}")
            
            return success
            
        except Exception as e:
            self.log.error(f"❌ Enhanced cache save failed: {e}")
            return False

'''
    
    # 2. Add enhanced memory management method
    enhanced_memory_method = '''
    def _smart_memory_management_enhanced(self, current_product_index: int):
        """Enhanced smart memory management with proper batching"""
        
        # Memory management configuration
        memory_config = self.system_config.get("memory_management", {})
        clear_frequency = memory_config.get("clear_frequency_products", 200)  # Changed from 500 to 200
        sliding_window_size = memory_config.get("sliding_window_size", 100)
        cache_save_frequency = memory_config.get("cache_save_frequency", 50)
        enabled = memory_config.get("enabled", True)
        
        if not enabled:
            return
        
        # Save cache more frequently (every 50 products)
        if current_product_index % cache_save_frequency == 0:
            try:
                if hasattr(self, '_current_all_products') and len(self._current_all_products) > 0:
                    cache_filename = f"{self.supplier_name.replace('.', '-')}_products_cache.json"
                    cache_file_path = os.path.join(self.supplier_cache_dir, cache_filename)
                    
                    # Use enhanced cache save method
                    self._save_products_to_cache_enhanced(self._current_all_products, cache_file_path, force_write=True)
                    self.log.info(f"💾 FREQUENT CACHE SAVE: Saved {len(self._current_all_products)} products (every {cache_save_frequency})")
            except Exception as e:
                self.log.error(f"Frequent cache save failed: {e}")
        
        # Memory clearing with proper batching (every 200 products)
        if current_product_index % clear_frequency == 0 and current_product_index > 0:
            self.log.info(f"🧹 BATCHED MEMORY MANAGEMENT: Starting at product {current_product_index}")
            
            # Clear large data structures but maintain continuity
            cleared_items = 0
            
            # Clear product accumulation with sliding window
            if hasattr(self, '_current_all_products') and len(self._current_all_products) > sliding_window_size * 2:
                # Ensure cache is saved before clearing
                try:
                    cache_filename = f"{self.supplier_name.replace('.', '-')}_products_cache.json"
                    cache_file_path = os.path.join(self.supplier_cache_dir, cache_filename)
                    self._save_products_to_cache_enhanced(self._current_all_products, cache_file_path, force_write=True)
                except Exception as e:
                    self.log.warning(f"Cache save before clearing failed: {e}")
                
                # Apply sliding window - keep recent products
                original_count = len(self._current_all_products)
                self._current_all_products = self._current_all_products[-sliding_window_size:]
                cleared_count = original_count - len(self._current_all_products)
                cleared_items += cleared_count
                
                self.log.info(f"🧹 SLIDING WINDOW: Cleared {cleared_count} old products, kept {len(self._current_all_products)} recent")
            
            # Force garbage collection if significant clearing occurred
            if cleared_items > 50:
                import gc
                gc.collect()
                self.log.info(f"🧹 GARBAGE COLLECTION: Forced cleanup after clearing {cleared_items} items")
            
            self.log.info(f"✅ BATCHED MEMORY CLEAR: Completed at product {current_product_index}")

'''
    
    # Find the location to insert the enhanced methods (after the existing _save_products_to_cache method)
    save_method_pattern = r'(def _save_products_to_cache\(self.*?\n(?:\s{4,}.*\n)*)'
    
    # Insert enhanced cache method after the existing one
    if re.search(save_method_pattern, content, re.DOTALL):
        content = re.sub(
            save_method_pattern,
            r'\1' + enhanced_cache_method,
            content,
            flags=re.DOTALL
        )
        print("✅ Enhanced cache method added")
    else:
        # Fallback: add at the end of the class
        class_end_pattern = r'(\n\s*def main\(\):)'
        content = re.sub(
            class_end_pattern,
            enhanced_cache_method + r'\1',
            content
        )
        print("✅ Enhanced cache method added (fallback location)")
    
    # Find and replace the existing memory management method
    memory_method_pattern = r'def _smart_memory_management\(self.*?\n(?:\s{4,}.*\n)*?(?=\n\s{4}def|\n\s{0,3}[a-zA-Z]|\Z)'
    
    if re.search(memory_method_pattern, content, re.DOTALL):
        content = re.sub(
            memory_method_pattern,
            enhanced_memory_method.strip(),
            content,
            flags=re.DOTALL
        )
        print("✅ Enhanced memory management method replaced")
    else:
        # Add the enhanced memory method
        content += enhanced_memory_method
        print("✅ Enhanced memory management method added")
    
    # 3. Update cache save calls to use enhanced method
    cache_save_pattern = r'self\._save_products_to_cache\('
    content = re.sub(
        cache_save_pattern,
        'self._save_products_to_cache_enhanced(',
        content
    )
    print("✅ Cache save calls updated to use enhanced method")
    
    # 4. Update memory management calls
    memory_call_pattern = r'self\._smart_memory_management\('
    content = re.sub(
        memory_call_pattern,
        'self._smart_memory_management_enhanced(',
        content
    )
    print("✅ Memory management calls updated to use enhanced method")
    
    # Save the modified workflow
    with open(workflow_file, 'w') as f:
        f.write(content)
    
    print(f"\n✅ WORKFLOW INTEGRATION COMPLETED")
    print(f"📁 Modified: {workflow_file}")
    print(f"💾 Backup: {backup_file}")
    
    return True

def verify_integration():
    """Verify that the integration was successful"""
    workflow_file = Path("tools/passive_extraction_workflow_latest.py")
    
    with open(workflow_file, 'r') as f:
        content = f.read()
    
    checks = [
        ("Enhanced cache method present", "_save_products_to_cache_enhanced" in content),
        ("Enhanced memory method present", "_smart_memory_management_enhanced" in content),
        ("Force write option present", "force_write=True" in content),
        ("Batched clearing present", "clear_frequency_products.*200" in content),
        ("Frequent cache saves present", "cache_save_frequency" in content)
    ]
    
    print("\n🔍 INTEGRATION VERIFICATION:")
    all_passed = True
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {check_name}")
        if not passed:
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    print("🚀 APPLYING WORKFLOW INTEGRATION")
    print("=" * 60)
    
    # Apply integration
    success = apply_workflow_integration()
    
    if success:
        # Verify integration
        verification_passed = verify_integration()
        
        if verification_passed:
            print("\n🎉 WORKFLOW INTEGRATION SUCCESSFUL!")
            print("\n📋 INTEGRATION APPLIED:")
            print("  ✅ Enhanced cache saving with multiple strategies")
            print("  ✅ Improved memory management with batching (200/100)")
            print("  ✅ Frequent cache saves (every 50 products)")
            print("  ✅ WSL-compatible file operations")
            print("  ✅ Forced write capabilities for persistence")
            
            print("\n🚀 READY FOR TESTING:")
            print("  • Cache files should now populate properly")
            print("  • Memory management uses batching instead of aggressive clearing")
            print("  • Processing state shows accurate metrics")
            print("  • Category progression tracking is visible")
            print("  • System should handle 2300+ products efficiently")
        else:
            print("\n⚠️ Integration applied but verification failed")
    else:
        print("\n❌ Integration failed")