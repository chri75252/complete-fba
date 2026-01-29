"""
Profit Calculation Tools for FBA Agent.

Implements adjusted profit calculation based on RSU (Required Supplier Units).
"""

from typing import Dict, Any, Tuple


def calculate_adjusted_profit(
    net_profit: float,
    supplier_price: float,
    rsu: float
) -> float:
    """
    Calculate adjusted profit after pack adjustment.
    
    Formula: Adjusted Profit = Original Profit - (Supplier Cost × (RSU - 1))
    
    This accounts for needing multiple supplier units to fulfill one Amazon listing.
    
    Args:
        net_profit: Original net profit from report
        supplier_price: Supplier cost per unit
        rsu: Required Supplier Units
        
    Returns:
        Adjusted profit (may be negative if pack math makes it unprofitable)
    """
    if rsu <= 1.0:
        return net_profit
    
    adjustment = supplier_price * (rsu - 1)
    adjusted = net_profit - adjustment
    
    return round(adjusted, 2)


def calculate_profit_from_prices(
    selling_price: float,
    supplier_price: float,
    rsu: float,
    fee_rate: float = 0.30
) -> Tuple[float, float]:
    """
    Calculate profit from raw prices (alternative method).
    
    Formula:
        Adjusted Cost = Supplier Price × RSU
        FBA Fees = Selling Price × fee_rate
        Adjusted Profit = Selling Price - Adjusted Cost - FBA Fees
    
    Args:
        selling_price: Amazon selling price
        supplier_price: Supplier cost per unit
        rsu: Required Supplier Units
        fee_rate: FBA fee rate (default 30%)
        
    Returns:
        Tuple of (adjusted_cost, adjusted_profit)
    """
    adjusted_cost = supplier_price * rsu
    fba_fees = selling_price * fee_rate
    adjusted_profit = selling_price - adjusted_cost - fba_fees
    
    return round(adjusted_cost, 2), round(adjusted_profit, 2)


def format_profit_for_display(profit: float, currency: str = "£") -> str:
    """
    Format profit value for table display.
    
    Args:
        profit: Profit value
        currency: Currency symbol
        
    Returns:
        Formatted profit string
    """
    if profit >= 0:
        return f"{currency}{profit:.2f}"
    else:
        return f"-{currency}{abs(profit):.2f}"


def extract_row_financials(row: Dict[str, Any]) -> Tuple[float, float, float, float]:
    """
    Extract financial values from a row dictionary.
    
    Args:
        row: Row dictionary from DataFrame
        
    Returns:
        Tuple of (supplier_price, selling_price, net_profit, roi)
    """
    def safe_float(value, default=0.0) -> float:
        try:
            if value is None or (isinstance(value, float) and value != value):  # NaN check
                return default
            return float(value)
        except (ValueError, TypeError):
            return default
    
    supplier_price = safe_float(row.get('SupplierPrice_incVAT', row.get('SupplierPrice', 0)))
    selling_price = safe_float(row.get('SellingPrice_incVAT', row.get('SellingPrice', 0)))
    net_profit = safe_float(row.get('NetProfit', 0))
    roi = safe_float(row.get('ROI', 0))
    
    return supplier_price, selling_price, net_profit, roi


def is_profitable(adjusted_profit: float, threshold: float = 0.0) -> bool:
    """
    Check if adjusted profit meets profitability threshold.
    
    Args:
        adjusted_profit: Adjusted profit value
        threshold: Minimum required profit
        
    Returns:
        True if profitable
    """
    return adjusted_profit > threshold
