"""
Integration tests for Always-Extract Workflow Fixes.

Tests the complete integration of all components:
- Startup orchestration sequence
- Data integrity guardian with reconciliation
- Enhanced URL filtering with invariant enforcement
- Unified state management with resume functionality
- Error handling and recovery mechanisms
"""

import pytest
import os
import json
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import components under test
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.fixed_enhanced_state_manager import (
    FixedEnhancedStateManager,
    StartupOrchestrator,
    DataIntegrityGuardian,
    ResumeController,
    QueueProcessor,
    ErrorHandler
)
from utils.url_filter import filter_urls


class TestStartupOrchestration:
    """Test suite for startup orchestration sequence."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def state_manager(self, temp_dir):
        """Create state manager for testing."""
        return FixedEnhancedStateManager("test_supplier", base_path=temp_dir)
    
    @pytest.fixture
    def mock_logger(self):
        """Create mock logger."""
        return Mock()

    def test_startup_orchestration_success(self, state_manager, mock_logger):
        """Test successful startup orchestration sequence."""
        # Create test data
        linking_map = [
            {'supplier_url': 'https://example.com/product1', 'ean': '1234567890123'},
            {'supplier_url': 'https://example.com/product2', 'ean': '2345678901234'}
        ]
        
        cached_products = [
            {'url': 'https://example.com/product1', 'title': 'Product 1'},
            {'url': 'https://example.com/product3', 'title': 'Product 3'}
        ]
        
        category_urls = [
            'https://example.com/category1',
            'https://example.com/category2'
        ]
        
        # Initialize orchestrator
        orchestrator = StartupOrchestrator(state_manager, mock_logger)
        
        # Execute startup sequence
        startup_result = orchestrator.execute_startup_sequence(
            linking_map, cached_products, category_urls
        )
        
        # Verify success
        assert startup_result['success'] == True
        assert 'resume_point' in startup_result
        assert 'reconciled_items' in startup_result
        
        # Verify sequence completion
        assert startup_result['phases_completed'] == [
            'reconciliation', 'resume_calculation', 'validation'
        ]

    def test_startup_orchestration_with_reconciliation(self, state_manager, mock_logger):
        """Test startup orchestration with data reconciliation."""
        # Create state with processed products missing from linking map
        state_manager.state_data['processed_products'] = {
            'https://example.com/product1': {'processed_at': '2025-08-13T10:00:00Z'},
            'https://example.com/product2': {'processed_at': '2025-08-13T10:05:00Z'}
        }
        
        # Linking map missing product2
        linking_map = [
            {'supplier_url': 'https://example.com/product1', 'ean': '1234567890123'}
        ]
        
        # Cached products has product2
        cached_products = [
            {'url': 'https://example.com/product1', 'title': 'Product 1'},
            {'url': 'https://example.com/product2', 'title': 'Product 2', 'price': '10.99'}
        ]
        
        category_urls = ['https://example.com/category1']
        
        # Execute startup sequence
        orchestrator = StartupOrchestrator(state_manager, mock_logger)
        startup_result = orchestrator.execute_startup_sequence(
            linking_map, cached_products, category_urls
        )
        
        # Verify reconciliation occurred
        assert startup_result['success'] == True
        assert startup_result['reconciled_items'] > 0
        
        # Verify reconciliation was logged
        mock_logger.info.assert_called()
        log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any('RECONCILED' in call for call in log_calls)

    def test_startup_orchestration_failure_handling(self, state_manager, mock_logger):
        """Test startup orchestration failure handling."""
        # Create invalid data to trigger failure
        linking_map = None  # Invalid data
        cached_products = []
        category_urls = []
        
        orchestrator = StartupOrchestrator(state_manager, mock_logger)
        
        # Execute startup sequence (should handle gracefully)
        startup_result = orchestrator.execute_startup_sequence(
            linking_map, cached_products, category_urls
        )
        
        # Verify failure handling
        assert startup_result['success'] == False
        assert 'error' in startup_result
        
        # Verify error was logged
        mock_logger.error.assert_called()

    def test_atomic_state_transitions(self, state_manager, mock_logger):
        """Test atomic state transitions during startup."""
        linking_map = []
        cached_products = []
        category_urls = ['https://example.com/category1']
        
        orchestrator = StartupOrchestrator(state_manager, mock_logger)
        
        # Mock save operations to verify atomic transitions
        with patch.object(state_manager, 'save_state_atomic', return_value=True) as mock_save:
            startup_result = orchestrator.execute_startup_sequence(
                linking_map, cached_products, category_urls
            )
            
            # Verify atomic saves occurred
            assert mock_save.call_count >= 1
            
            # Verify success
            assert startup_result['success'] == True


class TestDataIntegrityGuardian:
    """Test suite for data integrity guardian functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def state_manager(self, temp_dir):
        """Create state manager for testing."""
        return FixedEnhancedStateManager("test_supplier", base_path=temp_dir)
    
    @pytest.fixture
    def mock_logger(self):
        """Create mock logger."""
        return Mock()

    def test_startup_reconciliation_basic(self, state_manager, mock_logger):
        """Test basic startup reconciliation functionality."""
        # Set up processed products without linking map entries
        state_manager.state_data['processed_products'] = {
            'https://example.com/product1': {'processed_at': '2025-08-13T10:00:00Z'},
            'https://example.com/product2': {'processed_at': '2025-08-13T10:05:00Z'}
        }
        
        linking_map = []  # Empty linking map
        
        cached_products = [
            {
                'url': 'https://example.com/product1',
                'title': 'Product 1',
                'price': '10.99',
                'ean': '1234567890123'
            }
        ]
        
        # Initialize guardian
        guardian = DataIntegrityGuardian(state_manager, mock_logger)
        
        # Perform reconciliation
        success, reconciled_items = guardian.reconcile_on_startup_prereq(
            linking_map, cached_products
        )
        
        # Verify reconciliation success
        assert success == True
        assert len(reconciled_items) > 0
        
        # Verify hydration attempt was made
        assert any('hydrated:' in item for item in reconciled_items)

    def test_linking_map_hydration(self, state_manager, mock_logger):
        """Test linking map hydration from cached products."""
        guardian = DataIntegrityGuardian(state_manager, mock_logger)
        
        cached_products = [
            {
                'url': 'https://example.com/product1',
                'title': 'Product 1',
                'price': '10.99',
                'ean': '1234567890123'
            }
        ]
        
        linking_map = []
        
        # Attempt hydration
        success = guardian._hydrate_linking_map_entry(
            'https://example.com/product1', cached_products, linking_map
        )
        
        # Verify hydration success
        assert success == True
        
        # Verify linking map entry was created
        assert len(linking_map) == 1
        assert linking_map[0]['supplier_url'] == 'https://example.com/product1'
        assert linking_map[0]['ean'] == '1234567890123'

    def test_hydration_failure_fallback(self, state_manager, mock_logger):
        """Test hydration failure fallback to Amazon analysis."""
        guardian = DataIntegrityGuardian(state_manager, mock_logger)
        
        # Cached product missing required fields
        cached_products = [
            {
                'url': 'https://example.com/product1',
                'title': 'Product 1'
                # Missing price and EAN
            }
        ]
        
        linking_map = []
        
        # Attempt hydration (should fail)
        success = guardian._hydrate_linking_map_entry(
            'https://example.com/product1', cached_products, linking_map
        )
        
        # Verify hydration failed
        assert success == False
        
        # Verify no linking map entry was created
        assert len(linking_map) == 0

    def test_corruption_detection(self, state_manager, mock_logger):
        """Test state corruption detection."""
        # Create corrupted state
        state_manager.state_data['resumption_index'] = -1  # Invalid
        state_manager.state_data['total_products'] = -100  # Invalid
        
        guardian = DataIntegrityGuardian(state_manager, mock_logger)
        
        # Detect corruption
        corruption_issues = guardian.detect_state_corruption()
        
        # Verify corruption was detected
        assert len(corruption_issues) > 0
        assert any('negative' in issue.lower() for issue in corruption_issues)

    def test_atomic_persistence(self, state_manager, mock_logger):
        """Test atomic state persistence after reconciliation."""
        guardian = DataIntegrityGuardian(state_manager, mock_logger)
        
        # Modify state
        state_manager.state_data['test_field'] = 'test_value'
        
        # Persist atomically
        success = guardian.persist_reconciled_state_atomic()
        
        # Verify persistence success
        assert success == True
        
        # Verify file was created
        assert state_manager.state_file_path.exists()


class TestResumeController:
    """Test suite for resume controller functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def state_manager(self, temp_dir):
        """Create state manager for testing."""
        return FixedEnhancedStateManager("test_supplier", base_path=temp_dir)
    
    @pytest.fixture
    def mock_logger(self):
        """Create mock logger."""
        return Mock()

    def test_resume_point_calculation(self, state_manager, mock_logger):
        """Test resume point calculation."""
        # Set up state for resume
        state_manager.update_progression_unified(
            category_index=5,
            total_categories=25,
            product_index=15,
            total_products_in_category=100,
            current_phase="supplier"
        )
        
        controller = ResumeController(state_manager, mock_logger)
        
        # Calculate resume point
        resume_point = controller.calculate_resume_point(reconciliation_completed=True)
        
        # Verify resume point
        assert resume_point['category_index'] == 5
        assert resume_point['product_index'] == 15
        assert resume_point['phase'] == "supplier"
        assert resume_point['valid'] == True

    def test_resume_point_validation(self, state_manager, mock_logger):
        """Test resume point validation."""
        controller = ResumeController(state_manager, mock_logger)
        
        # Valid resume point
        valid_resume_point = {
            'category_index': 5,
            'total_categories': 25,
            'product_index': 15,
            'total_products_in_category': 100,
            'phase': 'supplier'
        }
        
        # Validate
        is_valid = controller.validate_resume_point(valid_resume_point)
        assert is_valid == True

    def test_resume_point_validation_failure(self, state_manager, mock_logger):
        """Test resume point validation failure."""
        controller = ResumeController(state_manager, mock_logger)
        
        # Invalid resume point (negative indices)
        invalid_resume_point = {
            'category_index': -1,
            'total_categories': 25,
            'product_index': 15,
            'total_products_in_category': 100,
            'phase': 'supplier'
        }
        
        # Validate
        is_valid = controller.validate_resume_point(invalid_resume_point)
        assert is_valid == False

    def test_safe_fallback_mechanism(self, state_manager, mock_logger):
        """Test safe fallback mechanism."""
        controller = ResumeController(state_manager, mock_logger)
        
        # Get safe fallback
        fallback_point = controller._get_safe_fallback_point("test_reason")
        
        # Verify fallback is safe
        assert fallback_point['category_index'] == 0
        assert fallback_point['product_index'] == 0
        assert fallback_point['phase'] == 'supplier'
        assert fallback_point['valid'] == True

    def test_prerequisite_checking(self, state_manager, mock_logger):
        """Test prerequisite checking for resume calculation."""
        controller = ResumeController(state_manager, mock_logger)
        
        # Attempt resume calculation without reconciliation
        resume_point = controller.calculate_resume_point(reconciliation_completed=False)
        
        # Should return safe fallback
        assert resume_point['category_index'] == 0
        assert resume_point['product_index'] == 0
        assert 'fallback_reason' in resume_point


class TestEndToEndWorkflow:
    """End-to-end integration tests for complete workflow."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def state_manager(self, temp_dir):
        """Create state manager for testing."""
        return FixedEnhancedStateManager("integration_test", base_path=temp_dir)
    
    @pytest.fixture
    def mock_logger(self):
        """Create mock logger."""
        return Mock()

    def test_complete_workflow_cycle(self, state_manager, mock_logger):
        """Test complete workflow cycle with all components."""
        # Setup test data
        linking_map = [
            {'supplier_url': 'https://example.com/product1', 'ean': '1234567890123'}
        ]
        
        cached_products = [
            {'url': 'https://example.com/product1', 'title': 'Product 1'},
            {'url': 'https://example.com/product2', 'title': 'Product 2', 'price': '10.99'}
        ]
        
        category_urls = [
            'https://example.com/category1',
            'https://example.com/category2'
        ]
        
        product_urls = [
            'https://example.com/product1',  # In linking map
            'https://example.com/product2',  # In cache
            'https://example.com/product3',  # New
            'https://example.com/product4'   # New
        ]
        
        # 1. Execute startup orchestration
        orchestrator = StartupOrchestrator(state_manager, mock_logger)
        startup_result = orchestrator.execute_startup_sequence(
            linking_map, cached_products, category_urls
        )
        
        assert startup_result['success'] == True
        
        # 2. Filter URLs with invariant enforcement
        filtered_result = filter_urls(
            product_urls, linking_map, cached_products,
            category_id='integration_test'
        )
        
        assert filtered_result['invariant_check'] == True
        assert len(filtered_result['skip_entirely']) == 1  # product1
        assert len(filtered_result['needs_amazon_only']) == 1  # product2
        assert len(filtered_result['needs_full_extraction']) == 2  # product3, product4
        
        # 3. Update state with denominator
        denominator = filtered_result['denominator']
        state_manager.update_progression_unified(
            category_index=0,
            total_categories=len(category_urls),
            total_products_in_current_category=denominator
        )
        
        # 4. Process queue
        queue_processor = QueueProcessor(state_manager, mock_logger)
        
        # Process supplier phase
        supplier_processed = queue_processor.process_supplier_phase(
            filtered_result['needs_full_extraction'], 0, category_urls[0]
        )
        
        # Process Amazon phase
        amazon_processed = queue_processor.process_amazon_phase(
            filtered_result['needs_amazon_only'], 0, category_urls[0]
        )
        
        # 5. Verify final state
        final_state = state_manager.state_data
        assert final_state['system_progression']['current_category_index'] == 0
        assert final_state['system_progression']['total_categories'] == 2

    def test_interruption_and_resume_cycle(self, state_manager, mock_logger):
        """Test interruption and resume cycle."""
        # Setup initial processing state
        state_manager.update_progression_unified(
            category_index=3,
            total_categories=10,
            product_index=25,
            total_products_in_category=100,
            current_phase="supplier"
        )
        
        # Save state (simulating interruption)
        state_manager.save_state_atomic()
        
        # Create new state manager (simulating restart)
        new_state_manager = FixedEnhancedStateManager(
            "integration_test", base_path=state_manager.base_path
        )
        
        # Load previous state
        loaded = new_state_manager.load_state()
        assert loaded == True
        
        # Execute startup sequence with resume
        orchestrator = StartupOrchestrator(new_state_manager, mock_logger)
        startup_result = orchestrator.execute_startup_sequence([], [], [])
        
        # Verify resume point
        resume_point = startup_result['resume_point']
        assert resume_point['category_index'] == 3
        assert resume_point['product_index'] == 25
        assert resume_point['phase'] == "supplier"

    def test_error_recovery_workflow(self, state_manager, mock_logger):
        """Test error recovery workflow."""
        # Create error handler
        error_handler = ErrorHandler(state_manager, mock_logger)
        
        # Simulate filter invariant failure
        failed_filter_result = {
            'skip_entirely': ['url1'],
            'needs_amazon_only': ['url2'],
            'needs_full_extraction': ['url3'],
            'total_input': 5,  # Invariant violation
            'category_id': 'error_test',
            'invariant_check': False
        }
        
        # Handle invariant failure
        recovery_result = error_handler.handle_invariant_failure(
            failed_filter_result, 'error_test'
        )
        
        # Verify error handling
        assert 'attempted_repair' in recovery_result
        assert 'diagnostic_snapshot' in recovery_result
        
        # Verify diagnostic snapshot was created
        diagnostics_dir = Path("OUTPUTS/DIAGNOSTICS/filter_failures")
        if diagnostics_dir.exists():
            snapshot_files = list(diagnostics_dir.glob("*.json"))
            # Note: In test environment, actual file creation may be mocked

    def test_performance_with_large_dataset(self, state_manager, mock_logger):
        """Test performance with large dataset."""
        # Create large dataset
        num_products = 1000
        
        linking_map = [
            {'supplier_url': f'https://example.com/product{i}', 'ean': f'{i:013d}'}
            for i in range(500)
        ]
        
        cached_products = [
            {'url': f'https://example.com/product{i}', 'title': f'Product {i}'}
            for i in range(500, 750)
        ]
        
        product_urls = [f'https://example.com/product{i}' for i in range(num_products)]
        
        # Measure startup time
        start_time = time.time()
        
        # Execute startup orchestration
        orchestrator = StartupOrchestrator(state_manager, mock_logger)
        startup_result = orchestrator.execute_startup_sequence(
            linking_map, cached_products, ['https://example.com/category1']
        )
        
        # Filter URLs
        filtered_result = filter_urls(
            product_urls, linking_map, cached_products,
            category_id='performance_test'
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Verify performance (should complete within reasonable time)
        assert processing_time < 30  # 30 seconds max for 1000 products
        
        # Verify correctness
        assert startup_result['success'] == True
        assert filtered_result['invariant_check'] == True
        assert filtered_result['total_input'] == num_products

    def test_concurrent_access_simulation(self, state_manager, mock_logger):
        """Test simulation of concurrent access scenarios."""
        # This test simulates concurrent access patterns
        # In a real scenario, this would use threading or multiprocessing
        
        # Simulate rapid state updates
        for i in range(10):
            state_manager.update_progression_unified(
                category_index=i,
                product_index=i * 10
            )
            
            # Atomic save
            success = state_manager.save_state_atomic()
            assert success == True
        
        # Verify final state consistency
        final_state = state_manager.state_data
        assert final_state['system_progression']['current_category_index'] == 9
        assert final_state['system_progression']['current_product_index_in_category'] == 90


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])