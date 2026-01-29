from __future__ import annotations

DEFAULT_RUNS_DIRNAME = "runs"
DEFAULT_MEMORY_DIRNAME = "memory"

DEFAULT_FEE_RATE = 0.30

TABLE_COLUMNS = [
    "Verdict",
    "Confidence",
    "SupplierTitle",
    "AmazonTitle",
    "Supplier EAN",
    "Amazon EAN",
    "ASIN",
    "SupplierPrice",
    "SellingPrice",
    "NetProfit",
    "ROI",
    "Sales",
    "Pack Verdict",
    "Adjusted Profit",
    "Key Match Evidence",
    "Filter Reason",
]

# Minimal English stopwords for token overlap checks (deterministic, no external deps).
STOPWORDS = {
    "A",
    "AN",
    "AND",
    "AS",
    "AT",
    "BY",
    "FOR",
    "FROM",
    "IN",
    "INTO",
    "IS",
    "IT",
    "OF",
    "ON",
    "OR",
    "PACK",
    "PCS",
    "PCE",
    "PK",
    "SET",
    "THE",
    "TO",
    "WITH",
    "X",
}

UNIT_KEYWORDS = {"CM", "MM", "INCH", "IN", "ML", "L", "LTR", "G", "KG", "OZ", "W"}

COLORS = {
    "BLACK",
    "WHITE",
    "SILVER",
    "GOLD",
    "RED",
    "BLUE",
    "GREEN",
    "YELLOW",
    "PINK",
    "PURPLE",
    "GREY",
    "GRAY",
    "BROWN",
    "ORANGE",
    "CLEAR",
    "CREAM",
}

SCENTS = {
    "LEMON",
    "LIME",
    "LAVENDER",
    "VANILLA",
    "EUCALYPTUS",
    "ROSE",
    "JASMINE",
    "COCONUT",
    "APPLE",
    "CINNAMON",
    "MINT",
}

