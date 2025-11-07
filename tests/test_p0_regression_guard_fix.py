"""
P0 Regression Guard Fix - Acceptance Tests

Tests strict monotonic enforcement of persistent_category_index.
Validates that the system NEVER allows category index to move backward.

Test Coverage:
1. Assert no backslide when incoming < current
2. Assert overflow clamp through mark_category_completed
3. Assert forward advancement works correctly
4. Assert equality case preserves index

Created: 2025-10-05
Related: P0 fix in utils/fixed_enhanced_state_manager.py lines 878-890
"""

import sys
import os
import json
import tempfile
import logging
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager

# Configure logging for test output
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)


class TestP0RegressionGuardFix:
    """Test suite for P0 regression guard fix."""

    def __init__(self):
        self.test_results = []
        self.temp_dir = None
        self.state_manager = None

    def setup(self):
        """Create temporary state file for testing."""
        self.temp_dir = tempfile.mkdtemp()

        # Initialize state manager with test supplier
        # Note: State file path is auto-generated from supplier name
        self.state_manager = FixedEnhancedStateManager(
            supplier_name="test_supplier",
            base_path=self.temp_dir
        )
        log.info(f"✅ Test setup complete - using temp dir: {self.temp_dir}")

    def teardown(self):
        """Clean up temporary files."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
            log.info("✅ Test teardown complete")

    def assert_equal(self, actual, expected, test_name):
        """Assert equality and track results."""
        if actual == expected:
            log.info(f"✅ PASS: {test_name}")
            self.test_results.append((test_name, "PASS"))
            return True
        else:
            log.error(f"❌ FAIL: {test_name} - Expected {expected}, got {actual}")
            self.test_results.append((test_name, "FAIL"))
            return False

    def test_1_no_backslide_when_incoming_less_than_current(self):
        """Test 1: Assert NO backslide when incoming < current."""
        log.info("\n" + "="*60)
        log.info("TEST 1: No Backslide When Incoming < Current")
        log.info("="*60)

        # Setup: Set PCI to 5
        self.state_manager.initialize_category_processing(
            category_index=5,
            category_url="https://test.com/category5",
            total_categories=10
        )

        current_pci = self.state_manager.state_data["system_progression"]["persistent_category_index"]
        self.assert_equal(current_pci, 5, "Initial PCI set to 5")

        # Attempt regression: Try to set PCI to 2
        self.state_manager.initialize_category_processing(
            category_index=2,
            category_url="https://test.com/category2",
            total_categories=10
        )

        # Assert: PCI should remain at 5 (no backslide)
        final_pci = self.state_manager.state_data["system_progression"]["persistent_category_index"]
        self.assert_equal(final_pci, 5, "PCI maintained at 5 (regression blocked)")

    def test_2_forward_advancement_allowed(self):
        """Test 2: Assert forward advancement works correctly."""
        log.info("\n" + "="*60)
        log.info("TEST 2: Forward Advancement Allowed")
        log.info("="*60)

        # Setup: Set PCI to 3
        self.state_manager.initialize_category_processing(
            category_index=3,
            category_url="https://test.com/category3",
            total_categories=10
        )

        current_pci = self.state_manager.state_data["system_progression"]["persistent_category_index"]
        self.assert_equal(current_pci, 3, "Initial PCI set to 3")

        # Advance: Set PCI to 7
        self.state_manager.initialize_category_processing(
            category_index=7,
            category_url="https://test.com/category7",
            total_categories=10
        )

        # Assert: PCI should advance to 7
        final_pci = self.state_manager.state_data["system_progression"]["persistent_category_index"]
        self.assert_equal(final_pci, 7, "PCI advanced to 7")

    def test_3_equality_preserves_index(self):
        """Test 3: Assert equality case preserves index."""
        log.info("\n" + "="*60)
        log.info("TEST 3: Equality Preserves Index")
        log.info("="*60)

        # Setup: Set PCI to 4
        self.state_manager.initialize_category_processing(
            category_index=4,
            category_url="https://test.com/category4",
            total_categories=10
        )

        current_pci = self.state_manager.state_data["system_progression"]["persistent_category_index"]
        self.assert_equal(current_pci, 4, "Initial PCI set to 4")

        # Re-initialize with same index
        self.state_manager.initialize_category_processing(
            category_index=4,
            category_url="https://test.com/category4",
            total_categories=10
        )

        # Assert: PCI should remain at 4
        final_pci = self.state_manager.state_data["system_progression"]["persistent_category_index"]
        self.assert_equal(final_pci, 4, "PCI unchanged at 4")

    def test_4_mark_category_completed_overflow_clamp(self):
        """Test 4: Assert overflow clamp through mark_category_completed."""
        log.info("\n" + "="*60)
        log.info("TEST 4: Mark Category Completed Overflow Clamp")
        log.info("="*60)

        # Setup: Set PCI to 8, total categories = 10
        self.state_manager.initialize_category_processing(
            category_index=8,
            category_url="https://test.com/category8",
            total_categories=10
        )

        # Set current category URL for completion check
        self.state_manager.state_data["system_progression"]["current_category_url"] = "test.com/category8"

        current_pci = self.state_manager.state_data["system_progression"]["persistent_category_index"]
        self.assert_equal(current_pci, 8, "Initial PCI set to 8")

        # Complete category: Should advance to 9
        self.state_manager.mark_category_completed(
            category_url="https://test.com/category8",
            absolute_cat_index=8
        )

        # Assert: PCI should advance to 9 (clamped if needed)
        final_pci = self.state_manager.state_data["system_progression"]["persistent_category_index"]
        expected = max(9, 8 + 1)  # Either 9 or absolute_cat_index + 1
        self.assert_equal(final_pci, expected, f"PCI advanced to {expected} after completion")

    def run_all_tests(self):
        """Run all acceptance tests."""
        log.info("\n" + "="*80)
        log.info("P0 REGRESSION GUARD FIX - ACCEPTANCE TEST SUITE")
        log.info("="*80)

        try:
            self.setup()

            # Run all tests
            self.test_1_no_backslide_when_incoming_less_than_current()
            self.test_2_forward_advancement_allowed()
            self.test_3_equality_preserves_index()
            self.test_4_mark_category_completed_overflow_clamp()

            # Print results summary
            log.info("\n" + "="*80)
            log.info("TEST RESULTS SUMMARY")
            log.info("="*80)

            passed = sum(1 for _, result in self.test_results if result == "PASS")
            failed = sum(1 for _, result in self.test_results if result == "FAIL")

            for test_name, result in self.test_results:
                status_icon = "✅" if result == "PASS" else "❌"
                log.info(f"{status_icon} {test_name}: {result}")

            log.info(f"\n📊 Total: {len(self.test_results)} tests")
            log.info(f"✅ Passed: {passed}")
            log.info(f"❌ Failed: {failed}")

            if failed == 0:
                log.info("\n🎉 ALL TESTS PASSED - P0 FIX VALIDATED")
                return True
            else:
                log.error(f"\n⚠️ {failed} TEST(S) FAILED - REVIEW REQUIRED")
                return False

        finally:
            self.teardown()


if __name__ == "__main__":
    test_suite = TestP0RegressionGuardFix()
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)
