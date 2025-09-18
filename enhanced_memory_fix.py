
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
                    cache_file_path = os.path.join(self.supplier_cache_dir, cache_file_path)
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
