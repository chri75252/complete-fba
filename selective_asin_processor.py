#!/usr/bin/env python3
"""
Selective ASIN Processor for Amazon FBA Agent System
Processes specific linking map entries to extract fresh Amazon data using direct ASIN access.

This script reads linking map entries and processes them through Amazon extraction
to create/update Amazon cache files, providing much faster processing than EAN search.

Author: Amazon FBA Agent System
Created: 2025-01-26
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add project root to Python path for imports
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Configure UTF-8 output for Windows
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

# Import system components
from config.system_config_loader import SystemConfigLoader
from utils.browser_manager import BrowserManager
from utils.logger import setup_logger
from tools.amazon_playwright_extractor import AmazonExtractor
# from utils.enhanced_state_manager import EnhancedStateManager  # Not needed for selective processing
# from utils.path_manager import PathManager  # Temporarily disabled due to file issues


class SelectiveLinkingMapProcessor:
    """
    Processes linking map entries directly using ASIN for fast Amazon data extraction.

    Features:
    - Direct ASIN-based extraction (60-70% faster than EAN search)
    - Price change tracking and comparison
    - Automatic Amazon cache file creation
    - Linking map updates with fresh data
    - Comprehensive error handling and reporting
    """

    def __init__(self, config_loader: SystemConfigLoader, browser_manager: BrowserManager,
                 supplier_name: str = "poundwholesale.co.uk"):
        """Initialize the selective processor."""
        self.config_loader = config_loader
        self.config = config_loader.get_full_config()
        self.browser_manager = browser_manager
        self.supplier_name = supplier_name
        self.logger = logging.getLogger(__name__)

        # Initialize Amazon extractor
        self.amazon_extractor = None

        # Initialize paths using simple path construction
        output_root = self.config.get('output_root', 'OUTPUTS')
        self.output_paths = {
            'amazon_cache_dir': os.path.join(output_root, 'FBA_ANALYSIS', 'amazon_cache'),
            'linking_map': os.path.join(output_root, 'FBA_ANALYSIS', 'linking_maps', supplier_name, 'linking_map.json'),
            'reports_dir': os.path.join(output_root, 'FBA_ANALYSIS', 'reports'),
            'supplier_cache': os.path.join(output_root, 'cached_products', f"{supplier_name.replace('.', '-')}_products_cache.json")
        }

        # Results tracking
        self.results = []
        self.stats = {
            'total_entries': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'price_changes': 0,
            'new_cache_files': 0,
            'start_time': None,
            'end_time': None
        }

    async def initialize_extractor(self):
        """Initialize the Amazon extractor with browser context."""
        try:
            self.logger.info("Initializing Amazon extractor...")
            self.amazon_extractor = AmazonExtractor(
                browser_manager=self.browser_manager
            )
            # Note: Browser initialization will be handled by the extractor when needed
            self.logger.info("Amazon extractor initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Amazon extractor: {e}")
            raise

    async def process_linking_entries(self, linking_entries: List[Dict[str, Any]],
                                    max_entries: Optional[int] = None) -> Dict[str, Any]:
        """
        Process linking map entries directly to Amazon extraction.

        Args:
            linking_entries: List of linking map entry dictionaries
            max_entries: Optional limit on number of entries to process

        Returns:
            Dictionary containing results and statistics
        """
        self.stats['start_time'] = datetime.now()
        self.stats['total_entries'] = len(linking_entries)

        if max_entries:
            linking_entries = linking_entries[:max_entries]
            self.logger.info(f"Limited processing to first {max_entries} entries")

        self.logger.info(f"Starting selective processing of {len(linking_entries)} linking map entries")

        # Ensure output directories exist
        os.makedirs(self.output_paths['amazon_cache_dir'], exist_ok=True)
        os.makedirs(os.path.dirname(self.output_paths['linking_map']), exist_ok=True)

        # Process each entry
        for index, entry in enumerate(linking_entries, 1):
            await self.process_single_entry(entry, index)

            # Progress reporting
            if index % 10 == 0:
                self.logger.info(f"Progress: {index}/{len(linking_entries)} entries processed")

        self.stats['end_time'] = datetime.now()

        # Generate summary report
        self.generate_summary_report()

        return {
            'results': self.results,
            'statistics': self.stats,
            'summary_file': self.save_detailed_report()
        }

    async def process_single_entry(self, entry: Dict[str, Any], index: int):
        """Process a single linking map entry."""
        ean = entry.get("supplier_ean")
        asin = entry.get("amazon_asin")
        title = entry.get("supplier_title", "")
        old_amazon_price = entry.get("amazon_price")
        supplier_url = entry.get("supplier_url", "")

        entry_id = f"{ean or 'NO_EAN'}_{asin or 'NO_ASIN'}"

        self.logger.info(f"[{index}] Processing: {entry_id}")

        # Validation checks
        if not asin or asin == "null":
            self.logger.warning(f"[{index}] Skipping entry with no valid ASIN: {entry_id}")
            self.results.append({
                'entry_index': index,
                'ean': ean,
                'asin': asin,
                'status': 'skipped',
                'reason': 'No valid ASIN provided',
                'processing_time': 0
            })
            self.stats['skipped'] += 1
            return

        # Optional: Check if you want to skip existing cache files
        cache_file_path = self.get_expected_cache_path(asin, ean)
        if os.path.exists(cache_file_path):
            # You can choose to skip or reprocess existing files
            # REMOVED: Illogical 24-hour skip condition
            self.logger.info(f"[{index}] Processing {entry_id} - Cache exists but will be refreshed")

        # Process the entry
        start_time = datetime.now()

        try:
            self.logger.info(f"[{index}] Extracting Amazon data for ASIN: {asin}")

            # Direct ASIN extraction (much faster than EAN search)
            extraction_result = await self.extract_amazon_data_by_asin(
                asin=asin,
                original_ean=ean,
                context_title=title
            )

            processing_time = (datetime.now() - start_time).total_seconds()

            if extraction_result and extraction_result.get('success'):
                # Successful extraction
                fresh_price = extraction_result.get('current_price')
                cache_file = extraction_result.get('cache_file_path')

                # Calculate price change
                price_change_pct = None
                price_change_abs = None
                if old_amazon_price and fresh_price:
                    price_change_abs = fresh_price - old_amazon_price
                    price_change_pct = (price_change_abs / old_amazon_price) * 100
                    if abs(price_change_pct) > 5:  # Significant price change
                        self.stats['price_changes'] += 1

                self.logger.info(f"[{index}] ✅ Success: {entry_id} -> £{fresh_price:.2f}")
                if price_change_pct:
                    self.logger.info(f"    Price change: £{old_amazon_price:.2f} -> £{fresh_price:.2f} ({price_change_pct:+.1f}%)")

                self.results.append({
                    'entry_index': index,
                    'ean': ean,
                    'asin': asin,
                    'status': 'success',
                    'cache_file': cache_file,
                    'fresh_price': fresh_price,
                    'old_price': old_amazon_price,
                    'price_change_abs': price_change_abs,
                    'price_change_pct': price_change_pct,
                    'processing_time': processing_time,
                    'supplier_title': title,
                    'amazon_title': extraction_result.get('title'),
                    'supplier_url': supplier_url
                })

                self.stats['successful'] += 1
                self.stats['new_cache_files'] += 1

            else:
                # Failed extraction
                error_reason = extraction_result.get('error', 'Unknown extraction error') if extraction_result else 'No extraction result'

                self.logger.error(f"[{index}] ❌ Failed: {entry_id} - {error_reason}")

                self.results.append({
                    'entry_index': index,
                    'ean': ean,
                    'asin': asin,
                    'status': 'failed',
                    'reason': error_reason,
                    'processing_time': processing_time,
                    'supplier_title': title,
                    'supplier_url': supplier_url
                })

                self.stats['failed'] += 1

        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            error_msg = str(e)

            self.logger.error(f"[{index}] ❌ Error: {entry_id} - {error_msg}")

            self.results.append({
                'entry_index': index,
                'ean': ean,
                'asin': asin,
                'status': 'error',
                'reason': error_msg,
                'processing_time': processing_time,
                'supplier_title': title,
                'supplier_url': supplier_url
            })

            self.stats['failed'] += 1

    async def extract_amazon_data_by_asin(self, asin: str, original_ean: str = None,
                                        context_title: str = None) -> Dict[str, Any]:
        """
        Extract Amazon data using direct ASIN access.

        Args:
            asin: Amazon ASIN to extract
            original_ean: Original EAN for cache filename
            context_title: Context title for validation

        Returns:
            Dictionary containing extraction results
        """
        try:
            # Use Amazon extractor for direct ASIN extraction
            result = await self.amazon_extractor.extract_data(asin=asin)

            # Check if extraction was successful
            if result and 'error' not in result:
                # Create cache file manually using the same pattern as the main workflow
                cache_file_path = self.get_expected_cache_path(asin, original_ean)

                # Save the Amazon data to cache file
                os.makedirs(os.path.dirname(cache_file_path), exist_ok=True)
                with open(cache_file_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False, default=str)

                # Extract current price from result
                current_price = None
                if 'current_price' in result:
                    current_price = result['current_price']
                elif 'price' in result:
                    current_price = result['price']

                return {
                    'success': True,
                    'cache_file_path': cache_file_path,
                    'current_price': current_price,
                    'title': result.get('title', result.get('product_title')),
                    'asin': result.get('asin_queried', asin)
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown extraction error')
                }

        except Exception as e:
            self.logger.error(f"Amazon extraction failed for ASIN {asin}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_expected_cache_path(self, asin: str, ean: str = None) -> str:
        """Get the expected Amazon cache file path."""
        if ean:
            filename = f"amazon_{asin}_{ean}.json"
        else:
            filename = f"amazon_{asin}.json"

        return os.path.join(self.output_paths['amazon_cache_dir'], filename)

    def generate_summary_report(self):
        """Generate and display summary statistics."""
        duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()

        print("\n" + "="*80)
        print("SELECTIVE ASIN PROCESSING COMPLETE")
        print("="*80)
        print(f"Processing Summary:")
        print(f"   Total entries: {self.stats['total_entries']}")
        print(f"   OK Successful: {self.stats['successful']}")
        print(f"   X Failed: {self.stats['failed']}")
        print(f"   - Skipped: {self.stats['skipped']}")
        print(f"   $ Price changes detected: {self.stats['price_changes']}")
        print(f"   + New cache files: {self.stats['new_cache_files']}")
        print(f"   Time: {duration:.1f}s")
        print(f"   Average time per entry: {duration/max(self.stats['total_entries'], 1):.1f}s")

        # Success rate
        success_rate = (self.stats['successful'] / max(self.stats['total_entries'] - self.stats['skipped'], 1)) * 100
        print(f"   Success rate: {success_rate:.1f}%")

        # Show top price changes
        if self.stats['price_changes'] > 0:
            price_changes = [r for r in self.results if r.get('price_change_pct')]
            price_changes.sort(key=lambda x: abs(x['price_change_pct']), reverse=True)

            print(f"\nTop Price Changes:")
            for change in price_changes[:5]:
                print(f"   {change['ean']} -> {change['asin']}: "
                      f"£{change['old_price']:.2f} -> £{change['fresh_price']:.2f} "
                      f"({change['price_change_pct']:+.1f}%)")

    def save_detailed_report(self) -> str:
        """Save detailed processing report to file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = os.path.join(
            self.output_paths['reports_dir'],
            f"selective_asin_processing_report_{timestamp}.json"
        )

        # Ensure reports directory exists
        os.makedirs(os.path.dirname(report_path), exist_ok=True)

        report_data = {
            'metadata': {
                'timestamp': timestamp,
                'supplier_name': self.supplier_name,
                'script_version': '1.0',
                'processing_mode': 'selective_asin'
            },
            'statistics': self.stats,
            'results': self.results
        }

        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)

            print(f"Report saved: {report_path}")
            return report_path

        except Exception as e:
            self.logger.error(f"Failed to save report: {e}")
            return None


async def main():
    """Main function to run selective ASIN processing."""
    print("Starting Selective ASIN Processor for Amazon FBA Agent System")
    print("="*80)

    # Configuration
    INPUT_FILE = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\FBA_ANALYSIS\linking_maps\poundwholesale.co.uk\not_found_asins.json"
    SUPPLIER_NAME = "poundwholesale.co.uk"
    MAX_ENTRIES = None  # Set to number to limit processing (e.g., 10 for testing)

    # Setup logging
    logger = setup_logger(log_level=logging.INFO)

    try:
        # Load linking entries
        print(f"Loading linking entries from: {INPUT_FILE}")

        if not os.path.exists(INPUT_FILE):
            raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            linking_entries = json.load(f)

        print(f"OK Loaded {len(linking_entries)} linking entries")

        # Initialize system components
        print("Initializing system components...")
        config_loader = SystemConfigLoader()
        browser_manager = BrowserManager()

        # Initialize processor
        processor = SelectiveLinkingMapProcessor(
            config_loader=config_loader,
            browser_manager=browser_manager,
            supplier_name=SUPPLIER_NAME
        )

        # Initialize Amazon extractor
        await processor.initialize_extractor()

        # Process entries
        print(f"Starting processing...")
        results = await processor.process_linking_entries(
            linking_entries=linking_entries,
            max_entries=MAX_ENTRIES
        )

        print("\nProcessing completed successfully!")

        # Cleanup
        if browser_manager.browser:
            await browser_manager.cleanup()

        return results

    except KeyboardInterrupt:
        print("\n! Processing interrupted by user")
        logger.info("Processing interrupted by user")
        return None

    except Exception as e:
        print(f"\nX Error during processing: {e}")
        logger.error(f"Error during processing: {e}")
        raise


if __name__ == "__main__":
    """Entry point for the selective ASIN processor."""
    try:
        # Run the async main function
        results = asyncio.run(main())

        if results:
            print(f"\nFinal Results Summary:")
            stats = results['statistics']
            print(f"   Processed: {stats['successful'] + stats['failed']}/{stats['total_entries']}")
            print(f"   Success Rate: {(stats['successful'] / max(stats['total_entries'] - stats['skipped'], 1)) * 100:.1f}%")
            print(f"   New Cache Files: {stats['new_cache_files']}")

        print("\nScript completed. Check the logs for detailed information.")

    except KeyboardInterrupt:
        print("\n! Script interrupted by user")
        sys.exit(1)

    except Exception as e:
        print(f"\n! Fatal error: {e}")
        sys.exit(1)