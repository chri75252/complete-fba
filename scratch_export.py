import asyncio
import os
import shutil
from pathlib import Path
from playwright.async_api import async_playwright

async def export_view(page, tier_value, min_profit, min_sales, name):
    print(f"\n--- Exporting {name} ---")
    
    await page.select_option('#analysisTierFilter', value=tier_value)
        
    await page.fill('#analysisMinProfit', str(min_profit) if min_profit is not None else '')
    await page.fill('#analysisMinSales', str(min_sales) if min_sales is not None else '')
    
    # Click APPLY
    await page.locator('button', has_text='APPLY').click()
    print("Clicked APPLY")
    
    await asyncio.sleep(2) # wait for render
    
    result_count = await page.locator('#analysisResultCount').text_content()
    print(f"Result count for {name}: {result_count.strip()}")
    
    # Click EXPORT CSV
    async with page.expect_download(timeout=10000) as download_info:
        await page.locator('#exportAnalysisBtn').click()
    
    download = await download_info.value
    downloads_dir = Path(os.path.expanduser('~')) / 'Downloads'
    source_path = await download.path()
    
    target_path = Path("OUTPUTS/PRODUCTS_LISTS") / f"{name}.csv"
    os.makedirs(target_path.parent, exist_ok=True)
    
    # copy the file
    import shutil
    shutil.copy(source_path, target_path)
    print(f"Saved to {target_path}")


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        
        target_page = None
        for page in context.pages:
            if '127.0.0.1:8001' in page.url or 'localhost:8001' in page.url:
                target_page = page
                break
                
        if not target_page:
            print("Dashboard not found")
            return
            
        print("Connected to Dashboard!")
        
        # We assume the user has already navigated to the Analysis tab and selected the correct report.
        
        # BUCKET A
        await export_view(target_page, "TIER_1_VERIFIED", 0.01, 1, "efg_t1_profit_gt0_sales_gt0")
        await export_view(target_page, "TIER_2_LIKELY", 0.01, 1, "efg_t2_profit_gt0_sales_gt0")
        await export_view(target_page, "TIER_3_NEEDS_REVIEW", 0.01, 1, "efg_t3_profit_gt0_sales_gt0")
        
        # BUCKET B (Profit > 0, all sales - we will filter zero in Python)
        await export_view(target_page, "TIER_1_VERIFIED", 0.01, '', "efg_t1_profit_gt0_all_sales")
        await export_view(target_page, "TIER_2_LIKELY", 0.01, '', "efg_t2_profit_gt0_all_sales")
        await export_view(target_page, "TIER_3_NEEDS_REVIEW", 0.01, '', "efg_t3_profit_gt0_all_sales")
        
        # BUCKET C (Near profit: > -3, high sales: > 50)
        await export_view(target_page, "TIER_1_VERIFIED", -3.00, 50, "efg_t1_nearzero_profit_high_sales")
        await export_view(target_page, "TIER_2_LIKELY", -3.00, 50, "efg_t2_nearzero_profit_high_sales")
        await export_view(target_page, "TIER_3_NEEDS_REVIEW", -3.00, 50, "efg_t3_nearzero_profit_high_sales")
        
        print("Done!")

asyncio.run(main())
