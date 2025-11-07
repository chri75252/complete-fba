#!/usr/bin/env python3
"""Test script to understand how corrupted imports behave"""

import sys
import os

# Add tools directory to path
tools_dir = os.path.join(os.path.dirname(__file__), 'tools')
sys.path.insert(0, tools_dir)

print("About to import corrupted amazon_playwright_extractor...")

try:
    from amazon_playwright_extractor import AmazonExtractor
    print(f"SUCCESS: Import worked! AmazonExtractor type: {type(AmazonExtractor)}")
    print(f"AmazonExtractor has methods: {dir(AmazonExtractor)}")
except ImportError as e:
    print(f"ImportError: {e}")
    print("Script should terminate here...")
    raise
except Exception as e:
    print(f"Other exception: {e}")
    print("Script should terminate here...")
    raise

print("If we reach here, something very strange happened...")

# Test creating a class that inherits from the corrupted import
try:
    class TestExtractor(AmazonExtractor):
        pass
    print("Created class inheriting from corrupted import!")
except Exception as e:
    print(f"Failed to create inheriting class: {e}")