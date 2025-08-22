"""Utility for pre-extraction URL filtering with linking map priority and invariant enforcement."""
from typing import List, Dict, Any, Set, Optional
import logging

from utils.normalization import normalize_url

log = logging.getLogger(__name__)


def filter_urls(
    product_urls: List[str],
    linking_map: List[Dict[str, Any]],
    cached_products: List[Dict[str, Any]],
    processed_urls_set: Optional[Set[str]] = None,
    category_id: Optional[str] = None
) -> Dict[str, List[str]]:
    """
    Classify product URLs with mandatory invariant validation and reconciliation.

    Priority: linking map (fully processed) > product cache (supplier data available).
    
    Args:
        product_urls: URLs to classify
        linking_map: Fully processed products
        cached_products: Products with supplier data only
        processed_urls_set: URLs marked as processed in state (for reconciliation)
        category_id: Category identifier for logging
        
    Returns:
        Dict with keys: skip_entirely, needs_amazon_only, needs_full_extraction,
        plus invariant validation and denominator calculation
    """
    category_id = category_id or "unknown"
    processed_urls_set = processed_urls_set or set()

    linking_map_urls = {
        normalize_url(entry.get("supplier_url") or entry.get("url", "")) 
        for entry in linking_map if entry.get("supplier_url") or entry.get("url")
    }
    cached_urls = {
        normalize_url(p.get("url", "")) 
        for p in cached_products if p.get("url")
    }

    result = {
        "skip_entirely": [],
        "needs_amazon_only": [],
        "needs_full_extraction": [],
        "linking_map_items": [],  # NEW: Track items in linking map for potential Amazon processing
        "reconciled_items": [],
        "total_input": len(product_urls),
        "category_id": category_id,
        "linking_map_hits": 0
    }
    
    # Initial classification
    for url in product_urls:
        norm_url = normalize_url(url)
        if norm_url in linking_map_urls:
            result["skip_entirely"].append(url)
            result["linking_map_items"].append(url)  # NEW: Track for potential Amazon processing
            result["linking_map_hits"] += 1
        elif norm_url in cached_urls:
            result["needs_amazon_only"].append(url)
        else:
            result["needs_full_extraction"].append(url)
    
    # 🚨 RECONCILIATION: Move processed-but-unlinked items from needs_full to needs_amazon
    reconciled_full = []
    
    # 🚀 HASH OPTIMIZATION: Use hash lookup if processed_urls_set is empty (optimization enabled)
    use_hash_optimization = len(processed_urls_set) == 0
    
    for url in result["needs_full_extraction"]:
        norm_url = normalize_url(url)
        
        # Check if URL is processed using optimized or legacy method
        is_processed = False
        if use_hash_optimization:
            # 🚀 DIRECT HASH LOOKUP: Check linking map directly instead of processed_products
            try:
                from utils.hash_lookup_optimizer import HashLookupOptimizer
                hash_optimizer = HashLookupOptimizer()
                is_processed = hash_optimizer.check_product_in_linking_map(supplier_url=url)
            except Exception as e:
                log.warning(f"⚠️ Hash optimization failed for {url}: {e}, falling back to legacy")
                is_processed = norm_url in processed_urls_set
        else:
            # Legacy method: check processed_urls_set
            is_processed = norm_url in processed_urls_set
            
        if is_processed:
            # Product processed but not in linking map - needs Amazon analysis
            result["needs_amazon_only"].append(url)
            result["reconciled_items"].append(f"moved_to_amazon:{url}")
            log.info(f"🔧 RECONCILED: Moved {url} from needs_full to needs_amazon (processed but unlinked)")
        else:
            reconciled_full.append(url)
    
    result["needs_full_extraction"] = reconciled_full
    
    # 🚨 MANDATORY INVARIANT VALIDATION
    invariant_passed = validate_filter_invariant(result)
    
    if not invariant_passed:
        # Create diagnostic snapshot and enter repair mode
        snapshot_filter_failure(result, product_urls, linking_map_urls, cached_urls, processed_urls_set)
        # For now, log error but continue - could be enhanced to halt/repair
        log.error(f"❌ FILTER INVARIANT FAILED for category {category_id} - continuing with best effort")
    
    # 🚨 FORMAL DENOMINATOR CALCULATION
    result["denominator"] = result["total_input"] - result["linking_map_hits"]
    
    # Log denominator with category ID for traceability
    log.info(f"DENOMINATOR[{category_id}]: {result['denominator']} = {result['total_input']} - {result['linking_map_hits']}")
    
    return result


def validate_filter_invariant(result: Dict[str, List[str]]) -> bool:
    """
    🚨 MANDATORY: Validate filter invariant skip + needs_amazon + needs_full == total_input
    
    Args:
        result: Filter result dictionary
        
    Returns:
        bool: True if invariant passes
    """
    skip_count = len(result['skip_entirely'])
    amazon_count = len(result['needs_amazon_only'])
    full_count = len(result['needs_full_extraction'])
    total_classified = skip_count + amazon_count + full_count
    total_input = result['total_input']
    
    invariant_passed = total_classified == total_input
    
    # Add detailed breakdown for debugging
    result["invariant_details"] = {
        "skip_count": skip_count,
        "amazon_count": amazon_count,
        "full_count": full_count,
        "total_classified": total_classified,
        "invariant_passed": invariant_passed
    }
    result["invariant_check"] = invariant_passed
    
    if not invariant_passed:
        log.error(
            f"🚨 INVARIANT FAILURE: {total_classified} != {total_input} "
            f"(skip={skip_count}, amazon={amazon_count}, full={full_count})"
        )
    
    return invariant_passed


def snapshot_filter_failure(result: Dict, product_urls: List[str], linking_map_urls: Set[str], 
                           cached_urls: Set[str], processed_urls_set: Set[str]):
    """
    Create diagnostic snapshot for filter invariant failures.
    
    Args:
        result: Filter result with failure
        product_urls: Original input URLs
        linking_map_urls: Normalized linking map URLs
        cached_urls: Normalized cached URLs
        processed_urls_set: Processed URLs from state
    """
    try:
        from datetime import datetime
        import json
        from pathlib import Path
        
        # Create snapshot data
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "category_id": result.get("category_id", "unknown"),
            "invariant_failure": result.get("invariant_details", {}),
            "input_urls_count": len(product_urls),
            "linking_map_urls_count": len(linking_map_urls),
            "cached_urls_count": len(cached_urls),
            "processed_urls_count": len(processed_urls_set),
            "sample_urls": {
                "input_sample": product_urls[:5],
                "skip_sample": result["skip_entirely"][:5],
                "amazon_sample": result["needs_amazon_only"][:5],
                "full_sample": result["needs_full_extraction"][:5]
            },
            "reconciliation": {
                "reconciled_items": result.get("reconciled_items", []),
                "reconciled_count": len(result.get("reconciled_items", []))
            }
        }
        
        # Save snapshot to diagnostics directory
        diagnostics_dir = Path("OUTPUTS") / "diagnostics" / "filter_failures"
        diagnostics_dir.mkdir(parents=True, exist_ok=True)
        
        snapshot_file = diagnostics_dir / f"filter_failure_{result.get('category_id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(snapshot_file, 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)
        
        log.error(f"📸 DIAGNOSTIC SNAPSHOT: Filter failure saved to {snapshot_file}")
        
    except Exception as e:
        log.error(f"❌ Failed to create filter failure snapshot: {e}")


# Backward compatibility - keep original function signature
def filter_urls_legacy(
    product_urls: List[str],
    linking_map: List[Dict[str, Any]],
    cached_products: List[Dict[str, Any]],
) -> Dict[str, List[str]]:
    """Legacy filter function for backward compatibility."""
    return filter_urls(product_urls, linking_map, cached_products)
