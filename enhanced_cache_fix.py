
    def _save_products_to_cache_enhanced(self, products: list, cache_file_path: str, force_write: bool = False):
        """Enhanced cache save with forced persistence and validation"""
        try:
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
                    self.log.info(f"✅ CACHE SAVE SUCCESS: {len(clean_products)} products saved to {cache_path}")
                
            except Exception as e:
                self.log.warning(f"Direct cache write failed: {e}")
            
            # Strategy 2: Atomic write if direct failed
            if not success:
                try:
                    import tempfile
                    temp_path = cache_path.with_suffix('.tmp')
                    
                    with open(temp_path, 'w', encoding='utf-8') as f:
                        json.dump(clean_products, f, indent=2, ensure_ascii=False)
                    
                    # Atomic move
                    import shutil
                    shutil.move(str(temp_path), str(cache_path))
                    
                    if cache_path.exists() and cache_path.stat().st_size > 100:
                        success = True
                        self.log.info(f"✅ CACHE ATOMIC SAVE SUCCESS: {len(clean_products)} products")
                        
                except Exception as e:
                    self.log.error(f"Atomic cache write failed: {e}")
            
            # Strategy 3: Backup and recovery if atomic failed
            if not success and force_write:
                try:
                    # Create backup
                    backup_path = cache_path.with_suffix('.backup')
                    if cache_path.exists():
                        shutil.copy2(cache_path, backup_path)
                    
                    # Force write
                    with open(cache_path, 'w', encoding='utf-8') as f:
                        json.dump(clean_products, f, indent=2, ensure_ascii=False)
                    
                    success = cache_path.exists() and cache_path.stat().st_size > 100
                    self.log.info(f"✅ FORCE CACHE SAVE: {len(clean_products)} products")
                    
                except Exception as e:
                    self.log.error(f"Force cache write failed: {e}")
                    # Restore backup if exists
                    if backup_path.exists():
                        shutil.move(str(backup_path), str(cache_path))
            
            return success
            
        except Exception as e:
            self.log.error(f"❌ Enhanced cache save failed: {e}")
            return False
