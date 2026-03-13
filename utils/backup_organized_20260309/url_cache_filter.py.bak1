#!/usr/bin/env python3
"""
URL Cache Filter for Amazon FBA Agent System
===========================================

Provides efficient URL pre-filtering to prevent unnecessary page visits for products
already in the cache. Implements high-performance URL lookup using in-memory sets
for O(1) duplicate detection before page scraping.

Key Features:
- Fast URL lookup using hash-based sets (O(1) performance)
- Automatic cache loading from product cache files
- Real-time cache updates when new products added
- Memory-efficient URL-only storage (not full product data)
- Integration with existing cache management system

Author: Amazon FBA Agent System
Date: 2025-07-22
Priority: HIGH - Critical efficiency improvement
"""

import os
import json
import logging
from typing import Set, Dict, Any, List, Optional
from pathlib import Path

# Configure logging
log = logging.getLogger(__name__)

class CachedURLManager:
    """
    Manages cached URLs for efficient duplicate detection before page visits
    """
    
    def __init__(self, output_root: str = "OUTPUTS"):
        """
        Initialize URL cache manager
        
        Args:
            output_root: Root directory for cache files (from system config)
        """
        self.output_root = output_root
        self.cached_urls: Set[str] = set()
        self.cache_files_loaded: Dict[str, str] = {}  # supplier_name -> cache_file_path
        
        log.info(f"🚀 CachedURLManager initialized with output_root: {output_root}")
    
    def load_supplier_cache_urls(self, supplier_name: str, force_reload: bool = False) -> int:
        """
        Load URLs from supplier cache file into memory set
        
        Args:
            supplier_name: Name of supplier (e.g., 'poundwholesale.co.uk')
            force_reload: Force reload even if already loaded
            
        Returns:
            Number of URLs loaded
        """
        # Convert supplier name to cache filename format
        cache_filename = f"{supplier_name.replace('.', '-')}_products_cache.json"
        cache_file_path = os.path.join(self.output_root, "cached_products", cache_filename)
        
        # Check if already loaded (unless force reload)
        if not force_reload and supplier_name in self.cache_files_loaded:
            if self.cache_files_loaded[supplier_name] == cache_file_path:
                log.debug(f"🔄 URLs already loaded for {supplier_name}: {len(self.cached_urls)} URLs")
                return len(self.cached_urls)
        
        # Load cache file if it exists
        if not os.path.exists(cache_file_path):
            log.info(f"📄 No cache file found for {supplier_name}: {cache_file_path}")
            return 0
        
        try:
            with open(cache_file_path, 'r', encoding='utf-8') as f:
                products = json.load(f)
            
            # Extract URLs from products
            new_urls = set()
            for product in products:
                if isinstance(product, dict) and 'url' in product:
                    url = product['url'].strip()
                    if url and url.startswith('http'):
                        new_urls.add(url)
            
            # Update cached URLs set
            initial_count = len(self.cached_urls)
            self.cached_urls.update(new_urls)
            final_count = len(self.cached_urls)
            
            # Track loaded file
            self.cache_files_loaded[supplier_name] = cache_file_path
            
            log.info(f"✅ Loaded {len(new_urls)} URLs from {supplier_name} cache")
            log.info(f"📊 Total cached URLs: {final_count} (+{final_count - initial_count} new)")
            
            return len(new_urls)
            
        except Exception as e:
            log.error(f"❌ Failed to load cache URLs for {supplier_name}: {e}")
            return 0
    
    def is_url_cached(self, url: str) -> bool:
        """
        Check if URL exists in cache (O(1) lookup)
        
        Args:
            url: Product URL to check
            
        Returns:
            True if URL is already cached, False otherwise
        """
        if not url or not isinstance(url, str):
            return False
        
        return url.strip() in self.cached_urls
    
    def add_url_to_cache(self, url: str) -> bool:
        """
        Add new URL to cached set (for real-time updates)
        
        Args:
            url: Product URL to add
            
        Returns:
            True if URL was new and added, False if already existed
        """
        if not url or not isinstance(url, str):
            return False
        
        url = url.strip()
        if url in self.cached_urls:
            return False  # Already exists
        
        self.cached_urls.add(url)
        log.debug(f"➕ Added new URL to cache: {url}")
        return True
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics for monitoring
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            "total_cached_urls": len(self.cached_urls),
            "loaded_suppliers": list(self.cache_files_loaded.keys()),
            "memory_estimation_mb": len(self.cached_urls) * 100 / (1024 * 1024)  # Rough estimate
        }
    
    def filter_new_urls(self, product_urls: List[str]) -> List[str]:
        """
        Filter list of URLs to only include those NOT in cache
        
        Args:
            product_urls: List of product URLs to filter
            
        Returns:
            List of URLs that are not in cache (need processing)
        """
        new_urls = []
        for url in product_urls:
            if not self.is_url_cached(url):
                new_urls.append(url)
        
        cached_count = len(product_urls) - len(new_urls)
        log.info(f"🔍 URL Filter Results: {len(new_urls)} new URLs, {cached_count} already cached")
        
        return new_urls
    
    def clear_cache(self):
        """Clear all cached URLs from memory"""
        self.cached_urls.clear()
        self.cache_files_loaded.clear()
        log.info("🗑️ Cleared all cached URLs from memory")

# Global instance for easy access
_cached_url_manager = None

def get_cached_url_manager(output_root: str = "OUTPUTS") -> CachedURLManager:
    """
    Get global cached URL manager instance
    
    Args:
        output_root: Root directory for cache files
        
    Returns:
        CachedURLManager instance
    """
    global _cached_url_manager
    if _cached_url_manager is None:
        _cached_url_manager = CachedURLManager(output_root)
    return _cached_url_manager

def prefilter_urls_against_cache(product_urls: List[str], 
                                supplier_name: str, 
                                output_root: str = "OUTPUTS") -> List[str]:
    """
    Convenience function to filter URLs against cache
    
    Args:
        product_urls: List of product URLs to filter
        supplier_name: Name of supplier for cache loading
        output_root: Root directory for cache files
        
    Returns:
        List of URLs that need processing (not in cache)
    """
    manager = get_cached_url_manager(output_root)
    
    # Load supplier cache if not already loaded
    manager.load_supplier_cache_urls(supplier_name)
    
    # Filter URLs
    return manager.filter_new_urls(product_urls)

if __name__ == "__main__":
    # Test the URL cache filter
    print("🧪 Testing URL Cache Filter...")
    
    # Create test manager
    manager = CachedURLManager("OUTPUTS")
    
    # Test with sample URLs
    test_urls = [
        "https://poundwholesale.co.uk/product1",
        "https://poundwholesale.co.uk/product2",
        "https://poundwholesale.co.uk/product3"
    ]
    
    # Add some to cache
    manager.add_url_to_cache(test_urls[0])
    manager.add_url_to_cache(test_urls[1])
    
    # Test filtering
    new_urls = manager.filter_new_urls(test_urls)
    print(f"Test results: {len(new_urls)} new URLs out of {len(test_urls)} total")
    print(f"New URLs: {new_urls}")
    print(f"Cache stats: {manager.get_cache_stats()}")
    
    print("✅ URL Cache Filter test complete")