#!/usr/bin/env python3
"""
URL-Aware State Manager for Amazon FBA Agent System
==================================================

Enhanced state management that properly handles URL pre-filtering while maintaining
backward compatibility with existing index-based tracking.

This solves the critical indexing conflict where URL pre-filtering changes array sizes,
breaking resumption logic that depends on index positions in full cache arrays.

Key Features:
- URL-based primary tracking for filtered processing
- Index-based backup for legacy compatibility
- Smart resumption logic that works with both systems
- State migration from index-based to URL-based tracking
- Seamless integration with URL cache filtering

Author: Amazon FBA Agent System
Date: 2025-07-22
Priority: CRITICAL - Fixes broken resumption logic
"""

import os
import json
import logging
from typing import Dict, Any, List, Set, Optional, Tuple
from utils.enhanced_state_manager import EnhancedStateManager

log = logging.getLogger(__name__)

class URLAwareStateManager(EnhancedStateManager):
    """
    Enhanced state manager that handles URL filtering without breaking resumption logic
    """
    
    def __init__(self, supplier_name: str):
        super().__init__(supplier_name)
        
        # URL-based tracking for reliable resumption
        self.processed_urls: Set[str] = set()
        self.load_processed_urls()
        
    def load_processed_urls(self):
        """Load processed URLs from state data"""
        processed_products = self.state_data.get("processed_products", {})
        self.processed_urls = set(processed_products.keys())
        log.info(f"🔄 Loaded {len(self.processed_urls)} processed URLs from state")
    
    def get_urls_to_process(self, all_urls: List[str]) -> List[str]:
        """
        Filter URLs to only include those that need processing
        
        This is the KEY METHOD that replaces index-based resumption
        with URL-based resumption for filtered processing.
        
        Args:
            all_urls: Complete list of URLs (from category scraping or cache)
            
        Returns:
            List of URLs that need processing (not already processed)
        """
        urls_to_process = [
            url for url in all_urls 
            if url not in self.processed_urls
        ]
        
        skipped_count = len(all_urls) - len(urls_to_process)
        log.info(f"📋 URL Resumption: {len(urls_to_process)} URLs to process, {skipped_count} already completed")
        
        return urls_to_process
    
    def mark_url_processed_with_index(self, url: str, status: str, processing_index: int, total_urls: int):
        """
        Mark URL as processed while maintaining index tracking for progress
        
        Args:
            url: Product URL that was processed
            status: Processing status (completed, failed, etc.)
            processing_index: Position in current processing session (for progress)
            total_urls: Total URLs in current processing session
        """
        # Primary: URL-based tracking
        self.mark_product_processed(url, status)
        self.processed_urls.add(url)
        
        # Secondary: Index-based tracking for progress reporting
        # NOTE: This index refers to CURRENT SESSION progress, not full cache position
        self.state_data["current_session_index"] = processing_index
        self.state_data["current_session_total"] = total_urls
        self.state_data["processing_status"] = "in_progress"
        
        # Calculate overall progress
        total_processed = len(self.processed_urls)
        self.state_data["total_urls_processed"] = total_processed
        
        log.debug(f"🔄 Progress: Session {processing_index+1}/{total_urls}, Overall {total_processed} URLs processed")
        
        # Auto-save
        self.save_state()
    
    def migrate_from_index_based_state(self, full_cache_products: List[Dict[str, Any]]) -> bool:
        """
        Migrate existing index-based state to URL-based state
        
        This handles the transition from index=539 to URL-based tracking
        
        Args:
            full_cache_products: Complete product cache array
            
        Returns:
            True if migration occurred, False if already URL-based
        """
        last_index = self.state_data.get("last_processed_index", 0)
        
        # Check if we need to migrate (has index but no processed URLs)
        has_index_state = last_index > 0
        has_url_state = len(self.processed_urls) > 0
        
        if has_index_state and not has_url_state:
            log.info(f"🔄 MIGRATION: Converting index-based state (index={last_index}) to URL-based state")
            
            # Extract URLs from products[0:last_index] 
            if last_index <= len(full_cache_products):
                processed_products = full_cache_products[:last_index]
                migrated_urls = []
                
                for product in processed_products:
                    url = product.get("url")
                    if url:
                        self.mark_product_processed(url, "migrated_from_index")
                        self.processed_urls.add(url)
                        migrated_urls.append(url)
                
                log.info(f"✅ Migration complete: {len(migrated_urls)} URLs migrated from index {last_index}")
                
                # Clear legacy index to prevent confusion
                self.state_data["legacy_last_processed_index"] = last_index  # Backup
                self.state_data["last_processed_index"] = 0  # Reset
                self.state_data["migration_completed_at"] = self._get_timestamp()
                
                self.save_state()
                return True
            else:
                log.warning(f"⚠️ Migration failed: Index {last_index} exceeds cache size {len(full_cache_products)}")
        
        return False
    
    def get_resumption_summary(self) -> Dict[str, Any]:
        """Get summary of resumption state for logging"""
        return {
            "processed_urls_count": len(self.processed_urls),
            "has_legacy_index": self.state_data.get("last_processed_index", 0) > 0,
            "current_session_progress": f"{self.state_data.get('current_session_index', 0)}/{self.state_data.get('current_session_total', 0)}",
            "total_urls_processed": self.state_data.get("total_urls_processed", 0),
            "migration_completed": "migration_completed_at" in self.state_data
        }
    
    def integrate_with_url_filtering(self, all_category_urls: List[str], cached_urls: Set[str]) -> Tuple[List[str], Dict[str, int]]:
        """
        Integrate URL-based state with URL cache filtering
        
        This is the complete solution that handles:
        1. URLs already in cache (skip)
        2. URLs already processed (skip) 
        3. New URLs that need processing
        
        Args:
            all_category_urls: URLs discovered from category scraping
            cached_urls: URLs already in product cache
            
        Returns:
            Tuple of (urls_to_process, stats_dict)
        """
        # Filter out cached URLs (already scraped)
        new_urls = [url for url in all_category_urls if url not in cached_urls]
        
        # Filter out already processed URLs (already analyzed)
        urls_to_process = [url for url in new_urls if url not in self.processed_urls]
        
        # Calculate statistics
        stats = {
            "total_category_urls": len(all_category_urls),
            "already_cached": len(all_category_urls) - len(new_urls),
            "already_processed": len(new_urls) - len(urls_to_process),
            "need_processing": len(urls_to_process)
        }
        
        log.info(f"🎯 URL Integration Summary:")
        log.info(f"   Category URLs: {stats['total_category_urls']}")
        log.info(f"   Already cached: {stats['already_cached']} (skip scraping)")
        log.info(f"   Already processed: {stats['already_processed']} (skip analysis)")  
        log.info(f"   Need processing: {stats['need_processing']} (will process)")
        
        return urls_to_process, stats
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()

# Convenience function for workflow integration
def create_url_aware_state_manager(supplier_name: str) -> URLAwareStateManager:
    """Create URL-aware state manager for supplier"""
    return URLAwareStateManager(supplier_name)

if __name__ == "__main__":
    # Test the URL-aware state manager
    print("🧪 Testing URL-Aware State Manager...")
    
    # Create test manager
    manager = URLAwareStateManager("test-supplier")
    
    # Test URL processing
    test_urls = [
        "https://example.com/product1",
        "https://example.com/product2", 
        "https://example.com/product3"
    ]
    
    # Mark some as processed
    manager.mark_url_processed_with_index(test_urls[0], "completed", 0, 3)
    manager.mark_url_processed_with_index(test_urls[1], "completed", 1, 3)
    
    # Test filtering
    remaining_urls = manager.get_urls_to_process(test_urls)
    print(f"URLs to process: {remaining_urls}")
    
    # Test integration
    cached_urls = {test_urls[2]}  # Simulate cache
    urls_to_process, stats = manager.integrate_with_url_filtering(test_urls, cached_urls)
    print(f"Integration result: {len(urls_to_process)} URLs, stats: {stats}")
    
    print("✅ URL-Aware State Manager test complete")