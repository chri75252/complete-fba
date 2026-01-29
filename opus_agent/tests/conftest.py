"""
Pytest configuration and fixtures for FBA Agent tests.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def sample_row():
    """Sample row data for testing."""
    return {
        'RowID': 1,
        'EAN': '5050028016069',
        'EAN_OnPage': '5050028016069',
        'EAN_clean': '5050028016069',
        'EAN_OnPage_clean': '5050028016069',
        'ASIN': 'B001234567',
        'SupplierTitle': 'EVERREADY T8 4FT 36W TUBE LIGHT',
        'AmazonTitle': 'Eveready T8 Tube 4ft 36w White 3500k',
        'SupplierPrice_incVAT': 2.99,
        'SellingPrice_incVAT': 18.99,
        'NetProfit': 8.00,
        'ROI': 120.0,
        'sales': 200
    }


@pytest.fixture
def sample_row_pack_mismatch():
    """Sample row with pack mismatch."""
    return {
        'RowID': 2,
        'EAN': '5060357990107',
        'EAN_OnPage': '5060357990107',
        'EAN_clean': '5060357990107',
        'EAN_OnPage_clean': '5060357990107',
        'ASIN': 'B0DJDH23JW',
        'SupplierTitle': 'PHOODS FOIL TRAY ROASTER',
        'AmazonTitle': 'Superior Sandwich Platter Trays - Pack of 10',
        'SupplierPrice_incVAT': 1.08,
        'SellingPrice_incVAT': 14.97,
        'NetProfit': 3.90,
        'ROI': 80.0,
        'sales': 50
    }


@pytest.fixture
def sample_row_dimension_trap():
    """Sample row with dimension pattern that could be mistaken for pack."""
    return {
        'RowID': 3,
        'EAN': '5060357990107',
        'EAN_OnPage': '5060357990107',
        'EAN_clean': '5060357990107',
        'EAN_OnPage_clean': '5060357990107',
        'ASIN': 'B0DJDH23JW',
        'SupplierTitle': 'SUPERIOR FOIL 10 CONTAINERS & LID 9X9IN',
        'AmazonTitle': 'Superior 10-Pack Aluminium Foil Trays 9x9 inch',
        'SupplierPrice_incVAT': 2.50,
        'SellingPrice_incVAT': 8.99,
        'NetProfit': 2.13,
        'ROI': 85.0,
        'sales': 100
    }


@pytest.fixture
def sample_row_capacity_multipack():
    """Sample row with capacity multipack pattern."""
    return {
        'RowID': 4,
        'EAN': '5000158062221',
        'EAN_OnPage': '5000158062221',
        'EAN_clean': '5000158062221',
        'EAN_OnPage_clean': '5000158062221',
        'ASIN': 'B07ABCDEFG',
        'SupplierTitle': 'KILROCK MOULD REMOVER 500ML (SOLD EACH)',
        'AmazonTitle': 'Kilrock 3 X Blast Away Mould Spray 500ml',
        'SupplierPrice_incVAT': 2.09,
        'SellingPrice_incVAT': 9.99,
        'NetProfit': 0.82,
        'ROI': 25.0,
        'sales': 75
    }
