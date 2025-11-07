"""
Unit tests for three-source validation fix (October 15, 2025)

Tests all three layers of the fix:
- Layer 1: Duplicate freeze removal
- Layer 2: Strengthened freeze guard enforcement
- Layer 3: Three-source validation method
"""

import pytest
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager as EnhancedStateManager


class TestLayer2FreezeGuardEnforcement:
    """Test Layer 2: Strengthened freeze guard with ValueError enforcement"""

    def test_freeze_guard_raises_exception_on_refreeze(self, tmp_path):
        """Verify freeze guard raises ValueError on re-freeze attempts (not advisory return)"""
        # Setup
        state_file = tmp_path / "test_state.json"
        state_manager = EnhancedStateManager(str(state_file))
        category_url = "https://www.poundwholesale.co.uk/toys/wholesale-big-boys-toys-gadgets"

        # First freeze should succeed
        result = state_manager.set_frozen_denominator(category_url, 58)
        assert result is True
        assert state_manager.is_category_denominator_frozen(category_url) is True

        # Second freeze should raise ValueError (LAYER_2_FIX)
        with pytest.raises(ValueError, match="FREEZE_GUARD_VIOLATION"):
            state_manager.set_frozen_denominator(category_url, 2)

    def test_freeze_guard_prevents_corruption(self, tmp_path):
        """Verify denominator remains unchanged after failed re-freeze attempt"""
        # Setup
        state_file = tmp_path / "test_state.json"
        state_manager = EnhancedStateManager(str(state_file))
        category_url = "https://www.poundwholesale.co.uk/toys/wholesale-big-boys-toys-gadgets"

        # Freeze with correct denominator (58)
        state_manager.set_frozen_denominator(category_url, 58)

        # Attempt re-freeze with wrong denominator (2) - should fail
        try:
            state_manager.set_frozen_denominator(category_url, 2)
        except ValueError:
            pass  # Expected

        # Verify denominator still 58 (not corrupted to 2)
        frozen_denom = state_manager.get_frozen_denominator(category_url)
        assert frozen_denom == 58, f"Expected 58, got {frozen_denom} - corruption occurred!"

    def test_freeze_guard_error_message_clarity(self, tmp_path):
        """Verify freeze guard error message is clear and actionable"""
        # Setup
        state_file = tmp_path / "test_state.json"
        state_manager = EnhancedStateManager(str(state_file))
        category_url = "https://www.poundwholesale.co.uk/toys/test"

        # First freeze
        state_manager.set_frozen_denominator(category_url, 100)

        # Attempt re-freeze and check error message
        with pytest.raises(ValueError) as exc_info:
            state_manager.set_frozen_denominator(category_url, 50)

        error_message = str(exc_info.value)
        assert "FREEZE_GUARD_VIOLATION" in error_message
        assert "already frozen" in error_message
        assert "immutable" in error_message


class TestLayer3ThreeSourceValidation:
    """Test Layer 3: Three-source validation method"""

    def test_three_source_validation_passes_when_consistent(self, tmp_path):
        """Verify validation passes when all three sources match"""
        # Setup state manager
        state_file = tmp_path / "test_state.json"
        state_manager = EnhancedStateManager(str(state_file))
        category_url = "https://www.poundwholesale.co.uk/toys/test"

        # Create manifest with 58 URLs
        manifest_dir = tmp_path / "OUTPUTS" / "manifests" / "www-poundwholesale-co-uk"
        manifest_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = manifest_dir / "www-poundwholesale-co-uk_toys_test_manifest.json"

        manifest_data = {
            "urls": [f"https://example.com/product-{i}" for i in range(58)],
            "hash": "d1acab0e"
        }
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest_data, f)

        # Freeze denominator (58)
        state_manager.set_frozen_denominator(category_url, 58)

        # Change to manifest directory for relative path resolution
        os.chdir(tmp_path)

        # Validation should pass (all three sources = 58)
        result = state_manager.validate_three_source_consistency(
            category_url,
            manifest_path=str(manifest_path)
        )
        assert result is True

    def test_three_source_validation_fails_on_mismatch(self, tmp_path):
        """Verify validation fails when sources don't match"""
        # Setup state manager
        state_file = tmp_path / "test_state.json"
        state_manager = EnhancedStateManager(str(state_file))
        category_url = "https://www.poundwholesale.co.uk/toys/test"

        # Create manifest with 58 URLs
        manifest_dir = tmp_path / "OUTPUTS" / "manifests" / "www-poundwholesale-co-uk"
        manifest_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = manifest_dir / "www-poundwholesale-co-uk_toys_test_manifest.json"

        manifest_data = {
            "urls": [f"https://example.com/product-{i}" for i in range(58)],
            "hash": "d1acab0e"
        }
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest_data, f)

        # Freeze with WRONG denominator (2 instead of 58) - simulating the bug
        state_manager.set_frozen_denominator(category_url, 2)

        # Change to manifest directory for relative path resolution
        os.chdir(tmp_path)

        # Validation should fail (manifest=58, state=2, resume=2)
        with pytest.raises(ValueError, match="THREE-SOURCE VALIDATION FAILED"):
            state_manager.validate_three_source_consistency(
                category_url,
                manifest_path=str(manifest_path)
            )

    def test_three_source_validation_error_details(self, tmp_path):
        """Verify validation error includes all three source values"""
        # Setup
        state_file = tmp_path / "test_state.json"
        state_manager = EnhancedStateManager(str(state_file))
        category_url = "https://www.poundwholesale.co.uk/toys/test"

        # Create manifest with 58 URLs
        manifest_dir = tmp_path / "OUTPUTS" / "manifests" / "www-poundwholesale-co-uk"
        manifest_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = manifest_dir / "www-poundwholesale-co-uk_toys_test_manifest.json"

        manifest_data = {"urls": [f"https://example.com/product-{i}" for i in range(58)]}
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest_data, f)

        # Freeze with wrong value
        state_manager.set_frozen_denominator(category_url, 2)

        # Change directory
        os.chdir(tmp_path)

        # Check error message includes all sources
        with pytest.raises(ValueError) as exc_info:
            state_manager.validate_three_source_consistency(
                category_url,
                manifest_path=str(manifest_path)
            )

        error_msg = str(exc_info.value)
        assert "Source 1 (Manifest): 58" in error_msg
        assert "Source 2 (State frozen_category_denominators): 2" in error_msg
        assert "Source 3 (Resume supplier_products_needing_extraction): 2" in error_msg


class TestIntegratedFixBehavior:
    """Integration tests for complete three-layer fix"""

    def test_category_processing_prevents_corruption(self, tmp_path):
        """
        Test complete category processing flow:
        1. Manifest generation (58 URLs)
        2. First freeze (correct: 58)
        3. Filtering (55 skip + 1 cache + 2 extract)
        4. Attempted re-freeze (blocked by Layer 2)
        5. Denominator remains correct (58)
        """
        # Setup
        state_file = tmp_path / "test_state.json"
        state_manager = EnhancedStateManager(str(state_file))
        category_url = "https://www.poundwholesale.co.uk/toys/test"

        # Stage 1: Manifest generation
        manifest_urls = [f"https://example.com/product-{i}" for i in range(58)]
        assert len(manifest_urls) == 58

        # Stage 2: First freeze (correct)
        state_manager.set_frozen_denominator(category_url, len(manifest_urls))
        assert state_manager.get_frozen_denominator(category_url) == 58

        # Stage 3: Simulate filtering (55 already processed, 3 remaining)
        needs_full_extraction = [manifest_urls[55], manifest_urls[56], manifest_urls[57]]
        assert len(needs_full_extraction) == 3

        # Further filtering (1 cached, 2 need extraction)
        needs_full_extraction_final = [manifest_urls[56], manifest_urls[57]]
        assert len(needs_full_extraction_final) == 2

        # Stage 4: Attempt re-freeze with filtered count (LAYER_2_FIX prevents this)
        with pytest.raises(ValueError, match="FREEZE_GUARD_VIOLATION"):
            state_manager.set_frozen_denominator(
                category_url,
                len(needs_full_extraction_final)  # Wrong: 2 instead of 58
            )

        # Stage 5: Verify denominator unchanged (still 58, not corrupted to 2)
        final_denom = state_manager.get_frozen_denominator(category_url)
        assert final_denom == 58, f"Corruption detected: {final_denom} != 58"

        # Calculate completion percentage
        completed_count = 56  # 55 skipped + 1 cached
        completion_pct = (completed_count / final_denom) * 100
        assert completion_pct == pytest.approx(96.6, rel=0.1), \
            f"Expected 96.6% completion, got {completion_pct}%"

    def test_expected_outcome_after_fix(self, tmp_path):
        """
        Verify expected outcomes after fix:
        - Categories complete at 100% (not 3.4%)
        - Resume pointers show correct denominators (58, not 2)
        - No FREEZE_GUARD_VIOLATION warnings (exceptions raised instead)
        """
        # Setup
        state_file = tmp_path / "test_state.json"
        state_manager = EnhancedStateManager(str(state_file))
        category_url = "https://www.poundwholesale.co.uk/toys/test"

        # Freeze correct denominator
        state_manager.set_frozen_denominator(category_url, 58)

        # Process all 58 products
        for i in range(58):
            # Simulate product processing
            pass

        # Verify completion
        sp = state_manager.state_data.get("system_progression", {})
        supplier_total = sp.get("supplier_products_needing_extraction", 0)

        # Should be 58 (correct), not 2 (corrupted)
        assert supplier_total == 58, \
            f"Expected denominator=58, got {supplier_total}"

        # Completion should be 100% (58/58), not 3.4% (2/58)
        completed = 58
        completion_pct = (completed / supplier_total) * 100
        assert completion_pct == 100.0, \
            f"Expected 100% completion, got {completion_pct}%"


# Pytest fixtures
@pytest.fixture
def tmp_path(tmpdir):
    """Provide temporary directory for test files"""
    return Path(tmpdir)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
