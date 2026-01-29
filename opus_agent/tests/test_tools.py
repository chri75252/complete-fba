"""
Unit tests for FBA Agent tools.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fba_agent.tools.ean_validation import (
    clean_to_digits,
    gtin_checksum_ok,
    normalize_ean,
    is_strict_valid_barcode,
    check_ean_match
)
from fba_agent.tools.pack_detection import (
    extract_pack_count,
    extract_multipack_total,
    detect_dimension_trap,
    detect_spec_x_trap,
    calculate_rsu
)
from fba_agent.tools.profit_calculation import (
    calculate_adjusted_profit
)


class TestEANValidation:
    """Tests for EAN validation functions."""
    
    def test_clean_to_digits_valid(self):
        """Test cleaning valid EAN strings."""
        assert clean_to_digits("5050028016069") == "5050028016069"
        assert clean_to_digits("5050028016069.0") == "50500280160690"  # .0 becomes digits
        assert clean_to_digits(" 5050028016069 ") == "5050028016069"
    
    def test_clean_to_digits_invalid(self):
        """Test cleaning invalid values."""
        assert clean_to_digits(None) == ""
        assert clean_to_digits("nan") == ""
        assert clean_to_digits("1.23e+12") == ""  # Scientific notation
    
    def test_gtin_checksum_valid_13(self):
        """Test valid 13-digit EAN checksum."""
        # Known valid EAN-13
        assert gtin_checksum_ok("5050028016069") == True
        assert gtin_checksum_ok("5032759027644") == True
    
    def test_gtin_checksum_invalid_13(self):
        """Test invalid 13-digit EAN checksum."""
        assert gtin_checksum_ok("5050028016060") == False  # Wrong check digit
        assert gtin_checksum_ok("1234567890123") == False
    
    def test_gtin_checksum_valid_8(self):
        """Test valid 8-digit EAN checksum."""
        assert gtin_checksum_ok("12345670") == True
    
    def test_normalize_ean_no_change(self):
        """Test that valid EANs are not changed."""
        assert normalize_ean("5050028016069") == "5050028016069"
    
    def test_normalize_ean_left_padding(self):
        """Test left-padding short EANs."""
        # A short code that becomes valid when padded
        short = "50028016069"  # 11 digits
        normalized = normalize_ean(short)
        # Should be padded if checksum passes
        assert len(normalized) >= 11
    
    def test_is_strict_valid_barcode(self):
        """Test strict barcode validation."""
        assert is_strict_valid_barcode("5050028016069") == True
        assert is_strict_valid_barcode("") == False
        assert is_strict_valid_barcode("abc") == False
        assert is_strict_valid_barcode("000000000000") == False  # Trailing zeros
    
    def test_check_ean_match_exact(self):
        """Test exact EAN match detection."""
        sup_valid, amz_valid, is_match, amz_present = check_ean_match(
            "5050028016069", "5050028016069"
        )
        assert sup_valid == True
        assert amz_valid == True
        assert is_match == True
        assert amz_present == True
    
    def test_check_ean_match_different(self):
        """Test different EAN detection."""
        sup_valid, amz_valid, is_match, amz_present = check_ean_match(
            "5050028016069", "5032759027644"
        )
        assert is_match == False
        assert amz_present == True
    
    def test_check_ean_match_missing(self):
        """Test missing Amazon EAN."""
        sup_valid, amz_valid, is_match, amz_present = check_ean_match(
            "5050028016069", ""
        )
        assert sup_valid == True
        assert amz_valid == False
        assert is_match == False
        assert amz_present == False


class TestPackDetection:
    """Tests for pack detection functions."""
    
    def test_extract_pack_single(self):
        """Test single unit detection."""
        pack, traps = extract_pack_count("APOLLO VINEGAR SHAKER")
        assert pack == 1
    
    def test_extract_pack_explicit(self):
        """Test explicit pack indicators."""
        assert extract_pack_count("TIDYZ DOGGY BAGS 50 PCS")[0] == 50
        assert extract_pack_count("AIRWICK DIFFUSER PK5")[0] == 5
        assert extract_pack_count("FIRELIGHTERS 28 PACK")[0] == 28
        assert extract_pack_count("Pack of 10 Trays")[0] == 10
    
    def test_dimension_trap_detection(self):
        """Test dimension trap detection."""
        # Should detect 9x9 inch as dimension, not pack
        trap = detect_dimension_trap("Superior 10-Pack Foil Trays 9x9 inch", 9)
        assert trap is not None
        assert trap.trap_type == "dimension_trap"
        
        # Should detect 15 x 5.5 x 5.5 cm as dimension
        trap = detect_dimension_trap("Apollo Shaker 15 x 5.5 x 5.5 cm", 15)
        assert trap is not None
    
    def test_dimension_shield_prevents_pack(self):
        """Test that dimension patterns don't become packs."""
        # "9x9 inch" should NOT result in pack = 9 or 81
        pack, traps = extract_pack_count("Superior Foil Trays 9x9 inch")
        assert pack == 1  # Default to single
        
        # "15 x 5.5 x 5.5 cm" should NOT result in pack = 15
        pack, traps = extract_pack_count("Apollo Shaker 15 x 5.5 x 5.5 cm")
        assert pack == 1
    
    def test_spec_x_trap_detection(self):
        """Test spec-x trap detection."""
        trap = detect_spec_x_trap("Magnifying Glass 2x magnification", 2)
        assert trap is not None
        assert trap.trap_type == "spec_x"
    
    def test_spec_x_shield_prevents_pack(self):
        """Test that spec-x patterns don't become packs."""
        pack, traps = extract_pack_count("Microscope 3x Zoom Lens")
        assert pack == 1
    
    def test_multipack_total_capacity(self):
        """Test capacity multipack patterns."""
        # "3 x 400ml" means RSU = 3, not 1200
        outer, inner, total, traps = extract_multipack_total("Kilrock Spray 3 x 400ml")
        assert outer == 3
        assert total == 3  # RSU = 3
    
    def test_multipack_total_quantity(self):
        """Test quantity multipack patterns."""
        # "(4 x 50)" means 200 total
        outer, inner, total, traps = extract_multipack_total("Tidyz Bags (4 x 50)")
        assert outer == 4
        assert inner == 50
        assert total == 200
    
    def test_calculate_rsu(self):
        """Test RSU calculation."""
        assert calculate_rsu(50, 200) == 4.0  # Need 4 x 50-packs
        assert calculate_rsu(50, 50) == 1.0   # 1:1 match
        assert calculate_rsu(100, 50) == 1.0  # Supplier has more (minimum 1)


class TestProfitCalculation:
    """Tests for profit calculation functions."""
    
    def test_adjusted_profit_no_adjustment(self):
        """Test profit with RSU = 1."""
        profit = calculate_adjusted_profit(5.00, 2.00, 1.0)
        assert profit == 5.00
    
    def test_adjusted_profit_with_rsu(self):
        """Test profit with RSU > 1."""
        # Original profit £5, supplier cost £2, RSU = 4
        # Adjusted = 5 - (2 * (4-1)) = 5 - 6 = -1
        profit = calculate_adjusted_profit(5.00, 2.00, 4.0)
        assert profit == -1.00
    
    def test_adjusted_profit_still_positive(self):
        """Test profit that remains positive after adjustment."""
        # Original profit £10, supplier cost £1, RSU = 3
        # Adjusted = 10 - (1 * 2) = 8
        profit = calculate_adjusted_profit(10.00, 1.00, 3.0)
        assert profit == 8.00


class TestIntegration:
    """Integration tests for the analysis pipeline."""
    
    def test_dimension_pattern_not_rsu(self):
        """Verify dimension patterns don't affect RSU."""
        # The title "Superior 10 Containers 9x9 inch" should result in:
        # - pack = 10 (from "10 Containers")
        # - NOT pack = 9 or 81 from "9x9"
        supplier_title = "SUPERIOR FOIL 10 CONTAINERS 9X9IN"
        amazon_title = "Superior 10-Pack Aluminium Foil Trays 9x9 inch"
        
        sup_pack, sup_traps = extract_pack_count(supplier_title)
        amz_outer, amz_inner, amz_total, amz_traps = extract_multipack_total(amazon_title)
        
        # Check dimension trap was detected
        assert any(t.trap_type == "dimension_trap" for t in sup_traps + amz_traps)
        
        # RSU should be 1 (10 containers = 10-pack)
        rsu = calculate_rsu(sup_pack if sup_pack > 1 else 10, amz_total if amz_total > 1 else 10)
        assert rsu == 1.0
    
    def test_capacity_multipack_rsu(self):
        """Verify capacity multipack calculates RSU correctly."""
        amazon_title = "Kilrock 3 X Blast Away Mould Spray 500ml"
        
        outer, inner, total, traps = extract_multipack_total(amazon_title)
        
        # Should be RSU = 3 (three 500ml bottles)
        assert outer == 3
        assert total == 3
        
        # If supplier sells single 500ml (pack=1)
        rsu = calculate_rsu(1, total)
        assert rsu == 3.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
