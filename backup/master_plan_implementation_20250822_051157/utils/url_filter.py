"""Utility for pre-extraction URL filtering with linking map priority and invariant enforcement."""
from typing import List, Dict, Any, Set, Optional
import logging

from utils.normalization import normalize_url

log = logging.getLogger(__name__)


def filter_unprocessed_products_with_hash_lookup(product_urls, linking_map_entries, cached_products):
    """
    Canonical LM → Cache → Extract classification with normalization.
    
    Order: 1) Linking Map (skip entirely) 2) Product Cache (needs Amazon only) 3) Needs full extraction
    
    Args:
        product_urls: List of product URLs to classify
        linking_map_entries: List of linking map entry dicts  
        cached_products: List of cached product dicts
        
    Returns:
        Dict with keys: skip_entirely, needs_amazon_only, needs_full_extraction, total_input
    """
    # 0) normalize input URLs
    urls_norm = [normalize_url(u) for u in product_urls if u]

    # 1) linking-map set
    lm_set = {
        normalize_url(e.get("supplier_url", ""))
        for e in linking_map_entries
        if e.get("supplier_url")
    }

    # 2) skip fully linked
    skip_entirely = [u for u in urls_norm if u in lm_set]
    remaining = [u for u in urls_norm if u not in lm_set]

    # 3) cache set
    cache_set = {
        normalize_url(p.get("url", ""))
        for p in cached_products
        if p.get("url")
    }

    needs_amazon_only = []
    needs_full_extraction = []
    for u in remaining:
        if u in cache_set:
            needs_amazon_only.append(u)
        else:
            needs_full_extraction.append(u)

    return {
        "skip_entirely": skip_entirely,
        "needs_amazon_only": needs_amazon_only,
        "needs_full_extraction": needs_full_extraction,
        "total_input": len(product_urls),
    }


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
