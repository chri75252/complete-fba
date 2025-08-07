# API Reference - Amazon FBA Agent System v3.7+

**Last Updated:** August 6, 2025  
**Version:** v3.7+  
**Status:** ✅ Production Ready with Hash Optimization  

---

## 🎯 **OVERVIEW**

This document provides comprehensive API documentation for the Amazon FBA Agent System v3.7+. The system is built with a modular architecture featuring smart memory management, Windows native support, file-based progress tracking, and O(1) hash-based optimizations for maximum performance.

---

## 🏗️ **CORE CLASSES**

### **PassiveExtractionWorkflow**

**Location:** `tools/passive_extraction_workflow_latest.py`  
**Purpose:** Main orchestrator class for the entire product sourcing workflow

#### **Constructor**

```python
class PassiveExtractionWorkflow:
    def __init__(self, supplier_name: str = None, use_predefined_categories: bool = True, 
                 ai_client: Optional[OpenAI] = None, browser_manager=None):
        """
        Initialize the passive extraction workflow with hash optimization
        
        Args:
            supplier_name: Name of the supplier (e.g., 'poundwholesale.co.uk')
            use_predefined_categories: Use predefined category URLs instead of AI
            ai_client: OpenAI client instance (optional)
            browser_manager: Browser manager instance (optional)
            
        Features:
            - O(1) hash-based duplicate prevention
            - Smart memory management with sliding window
            - File-based progress tracking
            - Multi-category deduplication
        """
```

#### **Main Methods**

##### **run()**
```python
async def run(self) -> Dict[str, Any]:
    """
    Execute the complete extraction workflow with hash optimization
    
    Returns:
        Dict containing processing results and performance metrics
        
    Features:
        - Automatic duplicate detection across categories
        - 20-40% performance improvement through cache optimization
        - Real-time progress tracking with file-based state
        - Comprehensive error handling and recovery
    """
```

##### **Hash Optimization Methods**

##### **_filter_unprocessed_products_with_hash_lookup()**
```python
def _filter_unprocessed_products_with_hash_lookup(self, all_products: List[Dict], 
                                                 supplier_name: str) -> List[Dict]:
    """
    Filter products using O(1) hash-based lookup against both linking map and product cache
    
    Args:
        all_products: List of products to filter
        supplier_name: Supplier identifier for cache lookup
        
    Returns:
        List of unprocessed products requiring extraction
        
    Performance:
        - O(1) lookup time regardless of cache size
        - 20-40% processing time reduction
        - Automatic multi-category deduplication
        - ~2 seconds saved per cached product
    """
```

##### **get_current_progress_from_files()**
```python
def get_current_progress_from_files(self) -> Dict[str, Any]:
    """
    Get comprehensive progress status from actual files (not memory)
    
    Returns:
        Dict containing:
        - processed_products: Count from cache files
        - supplier_products: Total products available
        - linking_entries: Amazon matches found
        - auth_fallback_count: Authentication fallback instances
        - category_progression: Detailed category status
        
    Features:
        - Always accurate (file-based, not memory-based)
        - Zero-risk progress tracking
        - Real-time metrics
    """
```

##### **safe_memory_clear_with_file_fallback()**
```python
def safe_memory_clear_with_file_fallback(self) -> None:
    """
    Safely clear memory while preserving progress data in files
    
    Features:
        - Sliding window approach (keeps recent 100 products)
        - File-based progress preservation
        - Forced garbage collection
        - No data loss during clearing
    """