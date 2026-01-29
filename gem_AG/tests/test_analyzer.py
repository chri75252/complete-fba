import pytest
from src.fba_agent.tools.analyzer import RowAnalyzer

@pytest.fixture
def basic_config():
    return {
        "dimension_shield_keywords": ["cm", "mm", "ml", "inch"],
        "leading_multiplier_check": True
    }

def test_ean_validation(basic_config):
    analyzer = RowAnalyzer(basic_config)
    
    # Valid EAN-13
    valid, norm = analyzer._validate_ean("5010853235530")
    assert valid is True
    assert norm == "5010853235530"
    
    # Invalid Checksum
    valid, norm = analyzer._validate_ean("5010853235531")
    assert valid is False
    
    # Short but padded valid (GTIN-8 padded to GTIN-13 is NOT valid checksum generally, 
    # but 12->13 padding or 8->13 padding logic depends on standard. 
    # Our code pads to 13 and checks. 
    # Let's test a valid GTIN-8 "12345670"
    # Padded to 13: "0000012345670". Checksum of that might match?
    # Actually GTIN-8 checksum digit calculation is same algo but length differs.
    # Our code pads string THEN checks.
    pass

def test_pack_extraction(basic_config):
    analyzer = RowAnalyzer(basic_config)
    
    # Simple
    assert analyzer._extract_qty("Pack of 10") == 10
    
    # Shielded
    assert analyzer._extract_amz_qty("9 x 9 inch")[0] == 1 # Should match 1, not 9
    
    # Multipack Brackets
    assert analyzer._extract_amz_qty("Product (4 x 50)")[0] == 200
    
    # N x Capacity
    assert analyzer._extract_amz_qty("3 x 400ml")[0] == 3

def test_profit_calc(basic_config):
    analyzer = RowAnalyzer(basic_config)
    # RSU = 1
    prof = analyzer._calculate_adjusted_profit(10.0, 5.0, 20.0, 1)
    assert prof == 10.0
    
    # RSU = 2 (Cost doubles)
    # NetProfit(orig) = 10.0 (based on cost 5.0)
    # New Cost = 10.0. Increase = 5.0. 
    # Adj Profit = 10.0 - 5.0 = 5.0
    prof = analyzer._calculate_adjusted_profit(10.0, 5.0, 20.0, 2)
    assert prof == 5.0
    
    # RSU = 4 (Cost quadruples)
    # Increase = 5.0 * 3 = 15.0
    # Adj Profit = 10.0 - 15.0 = -5.0
    prof = analyzer._calculate_adjusted_profit(10.0, 5.0, 20.0, 4)
    assert prof == -5.0
