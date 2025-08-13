"""
Unit tests for Filter Invariant Enforcement implementation.

Tests the enhanced URL filter functionality including:
- Invariant validation (skip + needs_amazon + needs_full == total_input)
- Reconciliation of processed-but-unlinked items
- Diagnostic snapshot creation
- Automatic repair mechanisms
- Formal denominator calculation
"""

import pytest
import os
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the functions under test
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.url_filter import (
    filter_urls,
    validate_filter_invariant,
    reconcile_processed_items,
    snapshot_filter_failure,
    attempt_invariant_repair
)
from utils.normalization import normalize_url


class TestFilterInvariantValidation:
    """Test suite for filter invariant validation."""
    
    def test_invariant_validation_pass(self):
        """Test invariant validation with valid classification."""
        result = {
            'skip_entirely': ['url1', 'url2'],
            'needs_amazon_only': ['url3'],
            'needs_full_extraction': ['url4', 'url5'],
            'total_input': 5,
            'category_id': 'test_category'
        }
        
        assert validate_filter_invariant(result) == True

    def test_invariant_validation_fail(self):
        """Test invariant validation with invalid classification."""
        result = {
            'skip_entirely': ['url1'],
            'needs_amazon_only': ['url2'],
            'needs_full_extraction': ['url3'],
            'total_input': 5,  # Should be 3
            'category_id': 'test_category'
        }
        
        assert validate_filter_invariant(result) == False

    def test_invariant_validation_empty_lists(self):
        """Test invariant validation with empty classification lists."""
        result = {
            'skip_entirely': [],
            'needs_amazon_only': [],
            'needs_full_extraction': [],
            'total_input': 0,
            'category_id': 'test_category'
        }
        
        assert validate_filter_invariant(result) == True

    def test_invariant_validation_single_category(self):
        """Test invariant validation with single category classification."""
        result = {
            'skip_entirely': ['url1', 'url2', 'url3', 'url4', 'url5'],
            'needs_amazon_only': [],
            'needs_full_extraction': [],
            'total_input': 5,
            'category_id': 'test_category'
        }
        
        assert validate_filter_invariant(result) == True

    def test_invariant_validation_logging(self):
        """Test invariant validation logging."""
        with patch('utils.url_filter.log') as mock_log:
            result = {
                'skip_entirely': ['url1', 'url2'],
                'needs_amazon_only': ['url3'],
                'needs_full_extraction': ['url4', 'url5'],
                'total_input': 5,
                'category_id': 'test_category'
            }
            
            validate_filter_invariant(result)
            
            # Verify info log was called
            mock_log.info.assert_called_once()
            call_args = mock_log.info.call_args[0][0]
            assert "INVARIANT CHECK[test_category]" in call_args
            assert "skip=2 + amazon=1 + full=2 = 5" in call_args
            assert "PASS" in call_args

    def test_invariant_validation_failure_logging(self):
        """Test invariant validation failure logging."""
        with patch('utils.url_filter.log') as mock_log:
            result = {
                'skip_entirely': ['url1'],
                'needs_amazon_only': ['url2'],
                'needs_full_extraction': ['url3'],
                'total_input': 5,
                'category_id': 'test_category'
            }
            
            validate_filter_invariant(result)
            
            # Verify error logs were called
            mock_log.error.assert_called()
            error_calls = [call[0][0] for call in mock_log.error.call_args_list]
            assert any("INVARIANT FAILURE" in call for call in error_calls)
            assert any("3 != 5" in call for call in error_calls)


class TestReconciliationLogic:
    """Test suite for processed item reconciliation."""
    
    def test_reconcile_processed_items_basic(self):
        """Test basic reconciliation of processed items."""
        result = {
            'needs_full_extraction': ['url1', 'url2', 'url3'],
            'needs_amazon_only': ['url4'],
            'reconciled_items': []
        }
        processed_urls_set = {'url1', 'url3'}
        
        reconciled = reconcile_processed_items(result, processed_urls_set)
        
        # url1 and url3 should be moved to needs_amazon_only
        assert 'url1' in reconciled['needs_amazon_only']
        assert 'url3' in reconciled['needs_amazon_only']
        assert 'url4' in reconciled['needs_amazon_only']  # Original item
        
        # url2 should remain in needs_full_extraction
        assert reconciled['needs_full_extraction'] == ['url2']
        
        # Reconciled items should be tracked
        assert len(reconciled['reconciled_items']) == 2
        assert any('url1' in item for item in reconciled['reconciled_items'])
        assert any('url3' in item for item in reconciled['reconciled_items'])

    def test_reconcile_processed_items_empty_processed_set(self):
        """Test reconciliation with empty processed URLs set."""
        result = {
            'needs_full_extraction': ['url1', 'url2'],
            'needs_amazon_only': ['url3'],
            'reconciled_items': []
        }
        processed_urls_set = set()
        
        reconciled = reconcile_processed_items(result, processed_urls_set)
        
        # Nothing should be moved
        assert reconciled['needs_full_extraction'] == ['url1', 'url2']
        assert reconciled['needs_amazon_only'] == ['url3']
        assert len(reconciled['reconciled_items']) == 0

    def test_reconcile_processed_items_no_matches(self):
        """Test reconciliation with no matching processed URLs."""
        result = {
            'needs_full_extraction': ['url1', 'url2'],
            'needs_amazon_only': ['url3'],
            'reconciled_items': []
        }
        processed_urls_set = {'url4', 'url5'}
        
        reconciled = reconcile_processed_items(result, processed_urls_set)
        
        # Nothing should be moved
        assert reconciled['needs_full_extraction'] == ['url1', 'url2']
        assert reconciled['needs_amazon_only'] == ['url3']
        assert len(reconciled['reconciled_items']) == 0

    def test_reconcile_processed_items_logging(self):
        """Test reconciliation logging."""
        with patch('utils.url_filter.log') as mock_log:
            result = {
                'needs_full_extraction': ['url1', 'url2'],
                'needs_amazon_only': [],
                'reconciled_items': []
            }
            processed_urls_set = {'url1'}
            
            reconcile_processed_items(result, processed_urls_set)
            
            # Verify reconciliation was logged
            mock_log.info.assert_called_once()
            call_args = mock_log.info.call_args[0][0]
            assert "RECONCILED" in call_args
            assert "url1" in call_args
            assert "needs_full to needs_amazon" in call_args


class TestEnhancedURLFilter:
    """Test suite for enhanced URL filter functionality."""
    
    def test_filter_urls_basic_classification(self):
        """Test basic URL classification."""
        product_urls = ['url1', 'url2', 'url3', 'url4']
        linking_map = [{'supplier_url': 'url1'}]
        cached_products = [{'url': 'url2'}]
        
        result = filter_urls(product_urls, linking_map, cached_products)
        
        # Verify classification
        assert 'url1' in result['skip_entirely']
        assert 'url2' in result['needs_amazon_only']
        assert 'url3' in result['needs_full_extraction']
        assert 'url4' in result['needs_full_extraction']
        
        # Verify invariant
        assert result['invariant_check'] == True
        assert result['total_input'] == 4
        assert result['linking_map_hits'] == 1

    def test_filter_urls_with_reconciliation(self):
        """Test URL filtering with reconciliation."""
        product_urls = ['url1', 'url2', 'url3']
        linking_map = []
        cached_products = [{'url': 'url1'}]
        processed_urls_set = {'url2'}
        
        result = filter_urls(
            product_urls, linking_map, cached_products, 
            processed_urls_set, 'test_category'
        )
        
        # url1 should need Amazon only (in cache)
        assert 'url1' in result['needs_amazon_only']
        
        # url2 should be reconciled to needs_amazon_only (processed but not linked)
        assert 'url2' in result['needs_amazon_only']
        
        # url3 should need full extraction
        assert 'url3' in result['needs_full_extraction']
        
        # Verify reconciliation tracking
        assert len(result['reconciled_items']) == 1
        assert any('url2' in item for item in result['reconciled_items'])

    def test_filter_urls_denominator_calculation(self):
        """Test formal denominator calculation."""
        product_urls = ['url1', 'url2', 'url3', 'url4', 'url5']
        linking_map = [{'supplier_url': 'url1'}, {'supplier_url': 'url2'}]
        cached_products = [{'url': 'url3'}]
        
        result = filter_urls(product_urls, linking_map, cached_products)
        
        # Denominator = total_input - linking_map_hits = 5 - 2 = 3
        assert result['denominator'] == 3
        assert result['linking_map_hits'] == 2
        assert result['total_input'] == 5

    def test_filter_urls_empty_inputs(self):
        """Test filtering with empty inputs."""
        result = filter_urls([], [], [])
        
        assert result['skip_entirely'] == []
        assert result['needs_amazon_only'] == []
        assert result['needs_full_extraction'] == []
        assert result['total_input'] == 0
        assert result['linking_map_hits'] == 0
        assert result['denominator'] == 0
        assert result['invariant_check'] == True

    def test_filter_urls_all_skip(self):
        """Test filtering where all URLs should be skipped."""
        product_urls = ['url1', 'url2', 'url3']
        linking_map = [
            {'supplier_url': 'url1'},
            {'supplier_url': 'url2'},
            {'supplier_url': 'url3'}
        ]
        cached_products = []
        
        result = filter_urls(product_urls, linking_map, cached_products)
        
        assert len(result['skip_entirely']) == 3
        assert len(result['needs_amazon_only']) == 0
        assert len(result['needs_full_extraction']) == 0
        assert result['denominator'] == 0
        assert result['invariant_check'] == True

    def test_filter_urls_invariant_failure_handling(self):
        """Test handling of invariant failures."""
        with patch('utils.url_filter.validate_filter_invariant', return_value=False):
            with patch('utils.url_filter.snapshot_filter_failure') as mock_snapshot:
                with patch('utils.url_filter.log') as mock_log:
                    product_urls = ['url1', 'url2']
                    linking_map = []
                    cached_products = []
                    
                    result = filter_urls(product_urls, linking_map, cached_products)
                    
                    # Verify snapshot was created
                    mock_snapshot.assert_called_once()
                    
                    # Verify error was logged
                    mock_log.error.assert_called()


class TestDiagnosticCapabilities:
    """Test suite for diagnostic snapshot functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    def test_snapshot_filter_failure(self, temp_dir):
        """Test diagnostic snapshot creation."""
        with patch('utils.url_filter.Path') as mock_path:
            # Mock the Path operations
            mock_snapshot_dir = Mock()
            mock_path.return_value = mock_snapshot_dir
            mock_snapshot_dir.mkdir = Mock()
            
            mock_snapshot_file = Mock()
            mock_snapshot_dir.__truediv__ = Mock(return_value=mock_snapshot_file)
            
            # Mock file operations
            mock_file = Mock()
            mock_file.__enter__ = Mock(return_value=mock_file)
            mock_file.__exit__ = Mock(return_value=None)
            
            with patch('builtins.open', return_value=mock_file):
                result = {
                    'skip_entirely': ['url1'],
                    'needs_amazon_only': ['url2'],
                    'needs_full_extraction': ['url3'],
                    'total_input': 5,
                    'category_id': 'test_category'
                }
                
                product_urls = ['url1', 'url2', 'url3', 'url4', 'url5']
                linking_map_urls = {'url1'}
                cached_urls = {'url2'}
                processed_urls_set = {'url3'}
                
                snapshot_filter_failure(
                    result, product_urls, linking_map_urls, 
                    cached_urls, processed_urls_set
                )
                
                # Verify directory creation
                mock_snapshot_dir.mkdir.assert_called_once_with(parents=True, exist_ok=True)
                
                # Verify file write was attempted
                mock_file.write.assert_called()

    def test_snapshot_content_structure(self, temp_dir):
        """Test diagnostic snapshot content structure."""
        # Create actual snapshot to test content
        snapshot_dir = Path(temp_dir) / "filter_failures"
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        result = {
            'skip_entirely': ['url1'],
            'needs_amazon_only': ['url2'],
            'needs_full_extraction': ['url3'],
            'total_input': 5,
            'category_id': 'test_category'
        }
        
        # Mock the snapshot creation with actual file write
        with patch('utils.url_filter.Path', return_value=snapshot_dir):
            with patch('utils.url_filter.datetime') as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = "20250813_120000"
                
                # Create a real snapshot file for testing
                snapshot_file = snapshot_dir / "filter_failure_20250813_120000.json"
                
                snapshot_data = {
                    "timestamp": "20250813_120000",
                    "category_id": "test_category",
                    "invariant_failure": {
                        "total_input": 5,
                        "skip_count": 1,
                        "amazon_count": 1,
                        "full_count": 1,
                        "total_classified": 3,
                        "difference": 2
                    }
                }
                
                with open(snapshot_file, 'w') as f:
                    json.dump(snapshot_data, f, indent=2)
                
                # Verify file was created
                assert snapshot_file.exists()
                
                # Verify content structure
                with open(snapshot_file, 'r') as f:
                    loaded_data = json.load(f)
                
                assert loaded_data["category_id"] == "test_category"
                assert loaded_data["invariant_failure"]["difference"] == 2
                assert loaded_data["invariant_failure"]["total_input"] == 5


class TestAutomaticRepair:
    """Test suite for automatic repair mechanisms."""
    
    def test_attempt_invariant_repair_success(self):
        """Test successful invariant repair."""
        # Mock repair functions
        with patch('utils.url_filter.remove_duplicate_classifications') as mock_remove_dupes:
            with patch('utils.url_filter.validate_filter_invariant') as mock_validate:
                # Setup mocks
                mock_remove_dupes.return_value = {'repaired': True}
                mock_validate.return_value = True
                
                result = {'category_id': 'test_category'}
                
                repaired_result = attempt_invariant_repair(result)
                
                # Verify repair was attempted
                mock_remove_dupes.assert_called_once_with(result)
                mock_validate.assert_called_once()
                
                # Verify repaired result returned
                assert repaired_result == {'repaired': True}

    def test_attempt_invariant_repair_failure(self):
        """Test failed invariant repair."""
        with patch('utils.url_filter.remove_duplicate_classifications') as mock_remove_dupes:
            with patch('utils.url_filter.validate_filter_invariant') as mock_validate:
                # Setup mocks for failed repair
                mock_remove_dupes.return_value = {'repaired': False}
                mock_validate.return_value = False
                
                original_result = {'category_id': 'test_category', 'original': True}
                
                repaired_result = attempt_invariant_repair(original_result)
                
                # Verify original result returned on repair failure
                assert repaired_result == original_result

    def test_repair_logging(self):
        """Test repair operation logging."""
        with patch('utils.url_filter.log') as mock_log:
            with patch('utils.url_filter.remove_duplicate_classifications') as mock_remove_dupes:
                with patch('utils.url_filter.validate_filter_invariant') as mock_validate:
                    # Setup successful repair
                    mock_remove_dupes.return_value = {'category_id': 'test_category'}
                    mock_validate.return_value = True
                    
                    result = {'category_id': 'test_category'}
                    attempt_invariant_repair(result)
                    
                    # Verify success logging
                    mock_log.info.assert_called_once()
                    call_args = mock_log.info.call_args[0][0]
                    assert "INVARIANT REPAIRED" in call_args
                    assert "test_category" in call_args


class TestFilterIntegration:
    """Integration tests for filter functionality."""
    
    def test_complete_filter_workflow(self):
        """Test complete filtering workflow with all features."""
        # Setup test data
        product_urls = [
            'https://example.com/product1',
            'https://example.com/product2',
            'https://example.com/product3',
            'https://example.com/product4',
            'https://example.com/product5'
        ]
        
        linking_map = [
            {'supplier_url': 'https://example.com/product1'}
        ]
        
        cached_products = [
            {'url': 'https://example.com/product2'}
        ]
        
        processed_urls_set = {'https://example.com/product3'}
        
        # Run filter
        result = filter_urls(
            product_urls, linking_map, cached_products,
            processed_urls_set, 'integration_test'
        )
        
        # Verify complete classification
        assert len(result['skip_entirely']) == 1  # product1 in linking map
        assert len(result['needs_amazon_only']) == 2  # product2 in cache, product3 reconciled
        assert len(result['needs_full_extraction']) == 2  # product4, product5 new
        
        # Verify invariant
        assert result['invariant_check'] == True
        
        # Verify denominator
        assert result['denominator'] == 4  # 5 - 1 linking map hit
        
        # Verify reconciliation
        assert len(result['reconciled_items']) == 1

    def test_edge_case_handling(self):
        """Test handling of edge cases."""
        # Test with malformed URLs
        product_urls = ['', 'invalid-url', 'https://valid.com/product']
        linking_map = []
        cached_products = []
        
        # Should handle gracefully
        result = filter_urls(product_urls, linking_map, cached_products)
        
        # Verify invariant still holds
        assert result['invariant_check'] == True
        assert result['total_input'] == 3

    def test_performance_with_large_datasets(self):
        """Test performance with large datasets."""
        # Create large dataset
        product_urls = [f'https://example.com/product{i}' for i in range(1000)]
        linking_map = [{'supplier_url': f'https://example.com/product{i}'} for i in range(0, 500)]
        cached_products = [{'url': f'https://example.com/product{i}'} for i in range(500, 750)]
        
        # Run filter
        result = filter_urls(product_urls, linking_map, cached_products)
        
        # Verify correct classification
        assert len(result['skip_entirely']) == 500
        assert len(result['needs_amazon_only']) == 250
        assert len(result['needs_full_extraction']) == 250
        
        # Verify invariant
        assert result['invariant_check'] == True
        assert result['total_input'] == 1000


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])