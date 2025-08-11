"""Utility for pre-extraction URL filtering with linking map priority."""

from typing import Any, Dict, List

from utils.normalization import normalize_ean, normalize_url


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
        normalize_url(entry.get("supplier_url") or entry.get("url")).lower()
        for entry in linking_map
    }
    linking_map_eans = {
        normalize_ean(entry.get("ean")) for entry in linking_map if entry.get("ean")
    }

    cached_by_url = {normalize_url(p.get("url")).lower(): p for p in cached_products}
    cached_eans = {normalize_ean(p.get("ean")) for p in cached_products if p.get("ean")}

    result = {
        "skip_entirely": [],
        "needs_amazon_only": [],
        "needs_full_extraction": [],
    }
    for url in product_urls:
        norm_url = normalize_url(url).lower()
        cached_entry = cached_by_url.get(norm_url)
        norm_ean = (
            normalize_ean(cached_entry.get("ean"))
            if cached_entry and cached_entry.get("ean")
            else None
        )

        if norm_url in linking_map_urls or (norm_ean and norm_ean in linking_map_eans):
            result["skip_entirely"].append(norm_url)
        elif norm_url in cached_by_url or (norm_ean and norm_ean in cached_eans):
            result["needs_amazon_only"].append(norm_url)
        else:
            result["needs_full_extraction"].append(norm_url)

    return result
