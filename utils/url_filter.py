"""Utility for pre-extraction URL filtering with linking map priority."""
from typing import List, Dict, Any

from utils.normalization import normalize_url


def filter_urls(
    product_urls: List[str],
    linking_map: List[Dict[str, Any]],
    cached_products: List[Dict[str, Any]],
) -> Dict[str, List[str]]:

    """Classify product URLs based on linking map and cache presence.

    Priority: linking map (fully processed) > product cache (supplier data available).
    Returns dict with keys: skip_entirely, needs_amazon_only, needs_full_extraction.
    """

    linking_map_urls = {
        normalize_url(entry.get("supplier_url") or entry.get("url")) for entry in linking_map
    }
    cached_urls = {normalize_url(p.get("url")) for p in cached_products}


    result = {
        "skip_entirely": [],
        "needs_amazon_only": [],
        "needs_full_extraction": [],
    }
    for url in product_urls:
        norm_url = normalize_url(url)
        if norm_url in linking_map_urls:
            result["skip_entirely"].append(url)
        elif norm_url in cached_urls:

            result["needs_amazon_only"].append(url)
        else:
            result["needs_full_extraction"].append(url)
    return result
