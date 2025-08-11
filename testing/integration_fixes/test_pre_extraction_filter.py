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


def test_filter_urls_normalization():
    product_urls = [
        "https://site.com/product/A/",
        "https://site.com/product/A?utm_source=123",
    ]
    linking_map = [{"supplier_url": "https://site.com/product/a"}]
    cached_products = []
    result = filter_urls(product_urls, linking_map, cached_products)
    # Both URLs should be treated as same and skipped entirely
    assert result["skip_entirely"] == product_urls
    assert result["needs_amazon_only"] == []
    assert result["needs_full_extraction"] == []
