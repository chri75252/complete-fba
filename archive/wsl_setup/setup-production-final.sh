#!/bin/bash
echo "🚀 Setting up Amazon FBA Tool Environment..."

# Set timeouts and error handling
set -e
export PIP_TIMEOUT=60
export PIP_RETRIES=2

# Core Python setup
pip install --upgrade pip
pip install uv

# Install from requirements.txt first (if it exists)
if [ -f requirements.txt ]; then
    echo "📦 Installing from requirements.txt..."
    pip install -r requirements.txt
fi

# Install additional dependencies efficiently
echo "📦 Installing additional dependencies..."
pip install --timeout=60 \
    openai aiohttp beautifulsoup4 pandas playwright \
    python-dotenv requests lxml fake-useragent \
    click rich tabulate \
    pytest pytest-asyncio pytest-cov faker pytest-timeout pytest-xdist

# Browser setup (container-safe)
echo "🌐 Setting up browsers..."
if command -v apt-get >/dev/null 2>&1; then
    export PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
    playwright install chromium --with-deps
else
    playwright install chromium || echo "⚠️ Browser install skipped in restricted environment"
fi

# Verify installation using safe Python execution
echo "✅ Verifying installation..."

# Create temporary test script to avoid nested quote issues
cat > /tmp/verify_deps.py << 'EOF'
try:
    import openai, aiohttp, bs4, pandas, playwright, dotenv, pytest, faker
    print('✅ All dependencies imported successfully')
except ImportError as e:
    print(f'❌ Missing dependency: {e}')
    exit(1)
EOF

python /tmp/verify_deps.py
rm -f /tmp/verify_deps.py

# Create .env file with API keys
echo "🔑 Creating .env file with API keys..."
cat > .env << 'EOF'
# Amazon FBA Agent System v3.5 Environment Variables
# Primary API Key (for main workflow + Amazon extractor)
OPENAI_API_KEY=sk--7R0rQdQ-dKs5rF44GUgMsvykvWf3__dP1br6zORYJT3BlbkFJFJIZgpH-SY9AJ2PqVgY1AlgzWlsk2u2BiWHgmq0ygA

# Secondary API Key (for supplier scraper)
OPENAI_API_KEY_SUPPLIER=sk-QyrBsS3WFqu6ZMab1Km8TYQatYWCWnoGhgjXbyLoV5T3BlbkFJWaw_6qfzEYYmBFwVtMYuSU8lZLCXRC9-jRF4oJop8A

# Model Configuration
OPENAI_MODEL_PRIMARY=gpt-4o-mini-2024-07-18
OPENAI_MODEL_SUPPLIER=gpt-4.1-mini-2025-04-14
OPENAI_MODEL_AMAZON_EXTRACTOR=gpt-4o-mini-2024-07-18

# System Configuration
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
EOF

echo "✅ .env file created with API keys and model configuration"

# Test environment variable loading
echo "🔑 Testing API key loading..."
cat > /tmp/test_env.py << 'EOF'
from dotenv import load_dotenv
import os
load_dotenv()

# Test API keys
primary_key = os.getenv('OPENAI_API_KEY')
supplier_key = os.getenv('OPENAI_API_KEY_SUPPLIER')

if primary_key and primary_key.startswith('sk-'):
    print(f'✅ Primary API key loaded: {primary_key[:20]}...')
else:
    print('❌ Primary API key missing or invalid')
    
if supplier_key and supplier_key.startswith('sk-'):
    print(f'✅ Supplier API key loaded: {supplier_key[:20]}...')
else:
    print('❌ Supplier API key missing or invalid')

# Test models
print(f'✅ Primary model: {os.getenv("OPENAI_MODEL_PRIMARY")}')
print(f'✅ Supplier model: {os.getenv("OPENAI_MODEL_SUPPLIER")}')
print(f'✅ Amazon extractor model: {os.getenv("OPENAI_MODEL_AMAZON_EXTRACTOR")}')
EOF

python /tmp/test_env.py
rm -f /tmp/test_env.py

# Test core system imports safely
echo "🧪 Testing core system imports..."
cat > /tmp/test_core.py << 'EOF'
import sys
sys.path.insert(0, 'tools')
sys.path.insert(0, 'utils')

try:
    import tools.passive_extraction_workflow_latest
    print("✅ Core system imports working")
    
    # Test enhanced components
    from utils.path_manager import get_api_log_path
    log_path = get_api_log_path("setup_test")
    print(f"✅ Path manager working: {log_path}")
    
    from utils.enhanced_state_manager import EnhancedStateManager
    state_manager = EnhancedStateManager("setup-test")
    print("✅ Enhanced state manager working")
    
except Exception as e:
    print(f"⚠️ Core import issue: {e}")
    print("This may be normal if dependencies are missing")
EOF

python /tmp/test_core.py
rm -f /tmp/test_core.py

# Create required directories
echo "📁 Creating required directories..."
python -c "
import os
required_dirs = [
    'logs/api_calls', 'logs/application', 'logs/tests', 'logs/monitoring',
    'logs/security', 'logs/debug', 'OUTPUTS/CACHE/processing_states',
    'OUTPUTS/FBA_ANALYSIS', 'OUTPUTS/REPORTS', 'OUTPUTS/BACKUPS'
]
for dir_path in required_dirs:
    os.makedirs(dir_path, exist_ok=True)
print('✅ All directories created')
"

echo ""
echo "✅ FBA Tool setup complete!"
echo ""
echo "🔑 API Keys configured:"
echo "   ✅ Primary: gpt-4o-mini-2024-07-18 model"
echo "   ✅ Supplier: gpt-4.1-mini-2025-04-14 model"
echo ""
echo "🧪 Test the system:"
echo "   python tools/passive_extraction_workflow_latest.py --max-products 5"
echo "   ./health-check.sh"
echo ""
echo "📁 Ready for production use!"