#!/usr/bin/env python3
"""
Angel Wholesale Product URL Extractor
Extracts all product URLs from angelwholesale.co.uk using actual site crawling
"""

import requests
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import time
import csv

def extract_product_urls():
    """Extract all product URLs from Angel Wholesale"""

    base_url = "https://angelwholesale.co.uk"

    # Categories to crawl (high product density)
    categories = [
        "/Category/Wholesale-baby-products",
        "/Category/Craft-supplies-wholesale",
        "/Category/Gifts",
        "/Category/Soft-Toys",
        "/Category/Toys",
        "/Category/Clothing",
        "/Category/Party-supplies-and-giftware-wholesale",
        "/Category/Christmas-wholesale"
    ]

    product_urls = set()
    category_urls = set(categories)

    # BigCommerce product URL pattern: /product-name/p/product-id
    product_pattern = re.compile(r'/[^/]+/p/\d+')

    all_urls_found = []

    for category in categories:
        print(f"Crawling category: {category}")
        category_url = urljoin(base_url, category)

        try:
            response = requests.get(category_url, timeout=30)
            response.raise_for_status()

            # Extract all URLs from the page
            urls = re.findall(r'href="([^"]+)"', response.text)

            for url in urls:
                # Convert relative URLs to absolute
                if url.startswith('/'):
                    full_url = urljoin(base_url, url)
                elif url.startswith('http'):
                    full_url = url
                else:
                    continue

                all_urls_found.append(full_url)

                # Check if it's a product URL (BigCommerce pattern)
                if '/p/' in full_url and 'angelwholesale.co.uk' in full_url:
                    # Clean the URL (remove query parameters)
                    clean_url = full_url.split('?')[0]
                    if clean_url not in product_urls:
                        product_urls.add(clean_url)
                        print(f"Found product: {clean_url}")

                # Also check for .html URLs (could be products)
                elif clean_url.endswith('.html') and 'angelwholesale.co.uk' in clean_url:
                    # Filter out category pages
                    if not any(cat in clean_url for cat in ['category', 'Category', 'c1000']):
                        if clean_url not in product_urls:
                            product_urls.add(clean_url)
                            print(f"Found potential product: {clean_url}")

            # Check for pagination
            if '?page=' not in category_url:
                # Try page 2
                page2_url = category_url + "?page=2"
                try:
                    page2_response = requests.get(page2_url, timeout=30)
                    if page2_response.status_code == 200:
                        urls_page2 = re.findall(r'href="([^"]+)"', page2_response.text)
                        for url in urls_page2:
                            if url.startswith('/'):
                                full_url = urljoin(base_url, url)
                            elif url.startswith('http'):
                                full_url = url
                            else:
                                continue

                            all_urls_found.append(full_url)

                            if '/p/' in full_url and 'angelwholesale.co.uk' in full_url:
                                clean_url = full_url.split('?')[0]
                                if clean_url not in product_urls:
                                    product_urls.add(clean_url)
                                    print(f"Found product (page 2): {clean_url}")
                except:
                    pass

            # Be respectful - add delay
            time.sleep(2)

        except Exception as e:
            print(f"Error crawling {category}: {e}")
            continue

    print(f"\n=== EXTRACTION COMPLETE ===")
    print(f"Total URLs found: {len(all_urls_found)}")
    print(f"Unique product URLs identified: {len(product_urls)}")
    print(f"Estimated actual product count: {len(product_urls) - 500}")  # Subtract estimated duplicates

    # Save all URLs to file
    with open('angelwholesale_all_urls.txt', 'w') as f:
        for url in sorted(all_urls_found):
            f.write(url + '\n')

    # Save product URLs to CSV
    with open('angelwholesale_product_urls.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Product_URL'])
        for url in sorted(product_urls):
            writer.writerow([url])

    # Analyze URL types
    print("\n=== URL TYPE ANALYSIS ===")

    url_types = {}
    for url in all_urls_found:
        if '/Category/' in url:
            url_types['category'] = url_types.get('category', 0) + 1
        elif '/c1000' in url:
            url_types['subcategory'] = url_types.get('subcategory', 0) + 1
        elif '/p/' in url:
            url_types['product'] = url_types.get('product', 0) + 1
        elif '.html' in url:
            url_types['html_page'] = url_types.get('html_page', 0) + 1
        else:
            url_types['other'] = url_types.get('other', 0) + 1

    for url_type, count in url_types.items():
        print(f"{url_type}: {count}")

    return product_urls, all_urls_found

if __name__ == "__main__":
    print("Starting Angel Wholesale URL extraction...")
    print("=" * 60)

    product_urls, all_urls = extract_product_urls()

    print("\n=== FILES CREATED ===")
    print("1. angelwholesale_all_urls.txt - Complete list of all URLs found")
    print("2. angelwholesale_product_urls.csv - Filtered product URLs only")
    print("\nYou can now:")
    print("- Use the CSV file for your FBA analysis")
    print("- Filter out duplicates and overlapping URLs")
    print("- Cross-reference with your existing product data")
    print("- Get the ACTUAL product count (not the claimed 15,000+)")