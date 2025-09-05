import pytest

from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager


def test_set_get_resumption_ptr(tmp_path):
    sm = FixedEnhancedStateManager("test", base_path=tmp_path)
    sm.set_resumption_ptr(1, 5)
    assert sm.get_resumption_ptr() == (1, 5)
    # regression attempts should not decrease pointer
    sm.set_resumption_ptr(0, 10)
    assert sm.get_resumption_ptr() == (1, 5)
    sm.set_resumption_ptr(1, 3)
    assert sm.get_resumption_ptr() == (1, 5)
    sm.set_resumption_ptr(2, 1)
    assert sm.get_resumption_ptr() == (2, 1)


def test_compute_supplier_config_hash_consistent(tmp_path):
    sm = FixedEnhancedStateManager("test", base_path=tmp_path)
    urls1 = ["b", "a"]
    urls2 = ["a", "b"]
    h1 = sm.compute_supplier_config_hash(urls1)
    h2 = sm.compute_supplier_config_hash(urls2)
    assert h1 == h2
