#!/usr/bin/env python3
"""
Quick Runner for Selective ASIN Processor

Simple script to run the selective ASIN processor with predefined settings.
Modify the configuration variables below to customize the processing.

Usage:
    python run_selective_asin_processor.py
"""

import asyncio
import os
import sys

# Add project root for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from selective_asin_processor import SelectiveLinkingMapProcessor, main

# =============================================================================
# CONFIGURATION - MODIFY THESE SETTINGS AS NEEDED
# =============================================================================

# Input file containing linking map entries to process
INPUT_FILE = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\FBA_ANALYSIS\linking_maps\poundwholesale.co.uk\not_found_asins.json"

# Supplier name for path management
SUPPLIER_NAME = "poundwholesale.co.uk"

# Processing limits
MAX_ENTRIES = 3  # Set to a number (e.g., 10) to limit processing for testing
                    # Set to None to process all entries

# Processing options
# REMOVED: SKIP_RECENT_CACHE - illogical 24-hour skip condition removed
# The system will now process ALL entries as requested

# =============================================================================
# QUICK START FUNCTIONS
# =============================================================================

def print_configuration():
    """Display current configuration settings."""
    print("📋 Current Configuration:")
    print(f"   Input File: {INPUT_FILE}")
    print(f"   Supplier: {SUPPLIER_NAME}")
    print(f"   Max Entries: {MAX_ENTRIES or 'All'}")
    print(f"   Processing Mode: Fresh data extraction (no time-based skipping)")
    print()

def validate_input_file():
    """Validate that the input file exists and is accessible."""
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Error: Input file not found: {INPUT_FILE}")
        print("\n💡 Available files in linking_maps directory:")

        linking_dir = os.path.dirname(INPUT_FILE)
        if os.path.exists(linking_dir):
            for file in os.listdir(linking_dir):
                if file.endswith('.json'):
                    full_path = os.path.join(linking_dir, file)
                    size = os.path.getsize(full_path)
                    print(f"   - {file} ({size:,} bytes)")

        return False

    # Check file size and content preview
    file_size = os.path.getsize(INPUT_FILE)
    print(f"OK Input file found: {os.path.basename(INPUT_FILE)} ({file_size:,} bytes)")

    try:
        import json
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Contains {len(data)} linking entries")

        if len(data) > 0:
            print("Sample entry:")
            sample = data[0]
            print(f"   EAN: {sample.get('supplier_ean', 'N/A')}")
            print(f"   ASIN: {sample.get('amazon_asin', 'N/A')}")
            print(f"   Title: {sample.get('supplier_title', 'N/A')[:50]}...")

        return True

    except Exception as e:
        print(f"X Error reading input file: {e}")
        return False

async def run_quick_test(max_entries=3):
    """Run a quick test with limited entries."""
    print(f"Running quick test with {max_entries} entries...")

    # Temporarily override MAX_ENTRIES for testing
    original_max = globals().get('MAX_ENTRIES')
    globals()['MAX_ENTRIES'] = max_entries

    try:
        results = await main()
        return results
    finally:
        globals()['MAX_ENTRIES'] = original_max

def show_menu():
    """Display interactive menu for script execution."""
    print("\n" + "="*60)
    print("🎯 SELECTIVE ASIN PROCESSOR - QUICK RUNNER")
    print("="*60)
    print("Choose an option:")
    print("1. 🧪 Quick Test (3 entries)")
    print("2. 🏃 Limited Run (10 entries)")
    print("3. 🚀 Full Processing (all entries)")
    print("4. ⚙️  Show Configuration")
    print("5. ❌ Exit")
    print()

    choice = input("Enter your choice (1-5): ").strip()
    return choice

async def main_interactive():
    """Interactive main function with menu options."""

    print("🚀 Selective ASIN Processor - Quick Runner")
    print("="*60)

    # Validate input file
    if not validate_input_file():
        return

    while True:
        choice = show_menu()

        if choice == '1':
            # Quick test
            print("\n" + "="*40)
            results = await run_quick_test(3)
            if results:
                stats = results['statistics']
                print(f"\n✅ Test completed: {stats['successful']}/{stats['total_entries']} successful")
            input("\nPress Enter to continue...")

        elif choice == '2':
            # Limited run
            print("\n" + "="*40)
            print("🏃 Starting limited run with 10 entries...")
            global MAX_ENTRIES
            original_max = MAX_ENTRIES
            MAX_ENTRIES = 10

            try:
                results = await main()
                if results:
                    stats = results['statistics']
                    print(f"\n✅ Limited run completed: {stats['successful']}/{stats['total_entries']} successful")
            finally:
                MAX_ENTRIES = original_max
            input("\nPress Enter to continue...")

        elif choice == '3':
            # Full processing
            print("\n" + "="*40)
            confirm = input("⚠️  This will process ALL entries. Continue? (y/N): ").strip().lower()
            if confirm == 'y':
                print("🚀 Starting full processing...")
                results = await main()
                if results:
                    stats = results['statistics']
                    print(f"\n✅ Full processing completed: {stats['successful']}/{stats['total_entries']} successful")
            else:
                print("❌ Full processing cancelled")
            input("\nPress Enter to continue...")

        elif choice == '4':
            # Show configuration
            print("\n" + "="*40)
            print_configuration()
            input("Press Enter to continue...")

        elif choice == '5':
            # Exit
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    """Entry point for the quick runner."""
    try:
        # Check if running in interactive mode
        if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
            # Interactive mode with menu
            asyncio.run(main_interactive())
        else:
            # Direct execution with current configuration
            print_configuration()

            if not validate_input_file():
                sys.exit(1)

            print("🚀 Starting processing with current configuration...")
            print("💡 Use --interactive flag for menu options")
            print()

            results = asyncio.run(main())

            if results:
                stats = results['statistics']
                print(f"\n🎉 Processing completed successfully!")
                print(f"📊 Final Results: {stats['successful']}/{stats['total_entries']} successful")

    except KeyboardInterrupt:
        print("\n⚠️  Script interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error: {e}")
        sys.exit(1)