import json
from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager
from utils.path_manager import get_processing_state_path


def test_state_manager_tracks_phase_separately():
    supplier = "unit_test_supplier"
    sm = FixedEnhancedStateManager(supplier_name=supplier)
    sm.initialize_category_processing(0, "http://example.com/cat", 2)
    sm.update_supplier_extraction_progress_new("http://example.com/p1")
    sm.update_amazon_analysis_progress_new("http://example.com/p1")

    state_path = get_processing_state_path(supplier)
    assert state_path.exists()
    with open(state_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    sp = data["system_progression"]
    ud = data["user_display_metrics"]
    assert sp["supplier_extraction_resumption_index"] == 1
    assert sp["amazon_analysis_resumption_index"] == 1
    assert sp["current_phase"] == "amazon_analysis"
    assert ud["progress_count"] == 1
    assert ud["session_products_processed"] == 1

    # cleanup
    state_path.unlink(missing_ok=True)


def test_update_supplier_extraction_progress_uses_current_key():
    supplier = "unit_test_supplier_key"
    sm = FixedEnhancedStateManager(supplier_name=supplier)
    sm.update_supplier_extraction_progress(3, 10)
    assert sm.state_data["supplier_extraction_progress"]["current_category_index"] == 3
    get_processing_state_path(supplier).unlink(missing_ok=True)


def test_correct_category_totals_realtime_updates_denominator():
    supplier = "unit_test_category_total"
    sm = FixedEnhancedStateManager(supplier_name=supplier)
    cat_url = "http://example.com/cat"
    sm.initialize_category_processing(0, cat_url, 1)
    # initial total zero, update to discovered 5
    sm.correct_category_totals_realtime(cat_url, 5)
    path = get_processing_state_path(supplier)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["supplier_extraction_progress"]["total_products_in_current_category"] == 5
    path.unlink(missing_ok=True)
