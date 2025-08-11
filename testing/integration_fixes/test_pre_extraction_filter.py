import pytest
from utils.url_filter import filter_urls


def test_filter_urls_priority():
    product_urls = ["u1", "u2", "u3", "u4"]
    linking_map = [
        {"supplier_url": "u1"},
        {"supplier_url": "u2"},
    ]
    cached_products = [
        {"url": "u2"},
        {"url": "u3"},
    ]

    result = filter_urls(product_urls, linking_map, cached_products)
    assert result["skip_entirely"] == ["u1", "u2"]
    assert result["needs_amazon_only"] == ["u3"]
    assert result["needs_full_extraction"] == ["u4"]
