# Pagination Configuration

<cite>
**Referenced Files in This Document**   
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py)
- [poundwholesale-co-uk.json](file://config/supplier_configs/poundwholesale-co-uk.json)
</cite>

## Table of Contents
1. [Pagination Configuration](#pagination-configuration)
2. [Pattern Field](#pattern-field)
3. [use_url_navigation Flag](#use_url_navigation-flag)
4. [next_button_selector Array](#next_button_selector-array)
5. [get_next_page_url Method](#get_next_page_url-method)
6. [Practical Example: Pound Wholesale](#practical-example-pound-wholesale)
7. [Edge Cases and Troubleshooting](#edge-cases-and-troubleshooting)

## Pattern Field
The `pattern` field in the pagination configuration defines the URL structure used for multi-page category listings. It uses a placeholder `{page_num}` that is dynamically replaced with the actual page number during navigation. For example, the pattern `?p={page_num}` indicates that page numbers are appended to the URL as query parameters, resulting in URLs like `https://www.poundwholesale.co.uk/category?p=2` for the second page.

This pattern-based approach allows the scraper to construct URLs for subsequent pages without relying on the presence of navigation buttons, providing a reliable method for pagination when the site's structure is consistent.

**Section sources**
- [poundwholesale-co-uk.json](file://config/supplier_configs/poundwholesale-co-uk.json#L115-L117)

## use_url_navigation Flag
The `use_url_navigation` flag determines the method used for navigating between pages. When set to `true`, the scraper uses URL manipulation based on the `pattern` field to navigate to the next page. This approach is efficient and reduces dependency on the presence of specific UI elements like "Next" buttons.

When `use_url_navigation` is `false`, the scraper relies on locating and clicking the "Next" button using CSS selectors defined in the `next_button_selector` array. This method is useful for sites where pagination is implemented via JavaScript or where URL patterns are not consistent.

**Section sources**
- [poundwholesale-co-uk.json](file://config/supplier_configs/poundwholesale-co-uk.json#L118-L119)

## next_button_selector Array
The `next_button_selector` array provides multiple CSS selector options for locating the 'Next' button on a page. These selectors are used as fallbacks, allowing the scraper to find the 'Next' button even if its HTML structure changes. The array is ordered by priority, with the most specific selectors listed first.

For example, the selectors `a.next`, `.pagination .next a`, and `a[rel='next']` target different possible implementations of the 'Next' button. This redundancy ensures robust navigation through paginated results, even when the site's design evolves.

**Section sources**
- [poundwholesale-co-uk.json](file://config/supplier_configs/poundwholesale-co-uk.json#L120-L123)

## get_next_page_url Method
The `get_next_page_url` method in `configurable_supplier_scraper.py` is responsible for determining the URL of the next page in a paginated sequence. It employs a multi-step strategy to ensure reliable navigation:

1. **Specific next button selector**: The method first attempts to locate the 'Next' button using selectors from the `next_button_selector` array.
2. **Pattern-based pagination**: If no button is found, it constructs the next page URL using the `pattern` field.
3. **Generic selectors**: As a fallback, it uses a set of common CSS selectors to locate the 'Next' button.
4. **URL inference**: If all else fails, it infers the next page URL based on the current URL structure.

This layered approach maximizes the chances of successful navigation, even in the face of inconsistent pagination patterns or missing navigation elements.

**Section sources**
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L2459-L2546)

## Practical Example: Pound Wholesale
The `poundwholesale-co-uk.json` configuration file provides a concrete example of pagination settings for Pound Wholesale. The `pagination` section specifies the URL pattern `?p={page_num}` and enables URL-based navigation with `use_url_navigation: true`. The `next_button_selector` array includes three CSS selectors as fallbacks: `a.next`, `.pagination .next a`, and `a[rel='next']`.

These settings allow the scraper to navigate through Pound Wholesale's category pages efficiently, using URL manipulation as the primary method and CSS selectors as a backup. This configuration ensures reliable extraction of product listings across multiple pages.

```mermaid
flowchart TD
A[Start] --> B{Page 1?}
B --> |Yes| C[Use base URL]
B --> |No| D[Apply pattern ?p={page_num}]
D --> E[Construct next page URL]
E --> F{URL valid?}
F --> |No| G[Use next_button_selector]
G --> H[Find 'Next' button]
H --> I[Get button href]
I --> J[Validate URL]
J --> K[Next page URL]
F --> |Yes| K
K --> L[End]
```

**Diagram sources**
- [poundwholesale-co-uk.json](file://config/supplier_configs/poundwholesale-co-uk.json#L115-L123)
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L2459-L2546)

## Edge Cases and Troubleshooting
Pagination can fail due to various edge cases, such as inconsistent URL patterns, JavaScript-based navigation, or missing 'Next' buttons. To handle these issues, the scraper employs several strategies:

- **Inconsistent patterns**: The `get_next_page_url` method uses URL inference to guess the next page URL based on the current URL structure.
- **JavaScript navigation**: When URL-based navigation fails, the scraper falls back to clicking the 'Next' button using CSS selectors.
- **Missing buttons**: The `next_button_selector` array provides multiple selectors, increasing the likelihood of finding the 'Next' button even if its HTML structure changes.

If pagination fails, the following troubleshooting steps are recommended:
1. Verify the `pattern` field matches the site's URL structure.
2. Update the `next_button_selector` array with current CSS selectors.
3. Check for JavaScript-based navigation and adjust the scraping strategy accordingly.
4. Use browser developer tools to inspect the 'Next' button and update selectors as needed.

**Section sources**
- [configurable_supplier_scraper.py](file://tools/configurable_supplier_scraper.py#L2459-L2546)
- [poundwholesale-co-uk.json](file://config/supplier_configs/poundwholesale-co-uk.json#L115-L123)