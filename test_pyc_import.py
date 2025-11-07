#!/usr/bin/env python3
"""Test if .pyc files can work without source .py files"""

import sys
import os

# Add tools directory to path
tools_dir = os.path.join(os.path.dirname(__file__), 'tools')
sys.path.insert(0, tools_dir)

print("Testing .pyc import without .py source file...")

try:
    from amazon_playwright_extractor import AmazonExtractor
    print(f"SUCCESS: .pyc import worked! AmazonExtractor type: {type(AmazonExtractor)}")
    print(f"Has methods: {[m for m in dir(AmazonExtractor) if not m.startswith('_')][:5]}")

    # Try to create an instance
    try:
        # This should fail if the class is incomplete, but let's see
        print("Attempting to inspect class constructor...")
        print(f"Constructor signature available: {hasattr(AmazonExtractor, '__init__')}")
    except Exception as e:
        print(f"Class inspection failed: {e}")

except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Other exception: {e}")

print("Test complete")