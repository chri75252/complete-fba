import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent  # Go up to opus_agent then to workspace root
MEMORY_DIR = BASE_DIR / "memory"
RUNS_DIR = BASE_DIR / "AGENT REPORT"
DOCS_DIR = BASE_DIR / "docs"

# Ensure directories exist
MEMORY_DIR.mkdir(exist_ok=True, parents=True)
RUNS_DIR.mkdir(exist_ok=True, parents=True)

# API Config
MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY")
MOONSHOT_BASE_URL = os.getenv("MOONSHOT_BASE_URL", "https://api.moonshot.ai/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "moonshot-v1-8k")

# App Config
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Reporting Constants
TABLE_SCHEMA = [
    "Verdict", "Confidence", "SupplierTitle", "AmazonTitle", 
    "Supplier EAN", "Amazon EAN", "ASIN", 
    "SupplierPrice", "SellingPrice", "NetProfit", "ROI", "Sales", 
    "Pack Verdict", "Adjusted Profit", "Key Match Evidence", "Filter Reason"
]
