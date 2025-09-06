# Technology Stack & Build System

## Core Technologies

- **Python 3.8+**: Primary language with async/await support
- **Playwright**: Browser automation for web scraping and Amazon interaction
- **Chrome CDP**: Chrome DevTools Protocol for browser management
- **aiohttp**: Async HTTP client for API requests
- **BeautifulSoup4**: HTML parsing and data extraction
- **pandas/numpy**: Data processing and analysis
- **psutil**: System monitoring and memory management

## Key Libraries

- **Configuration**: python-dotenv, pyyaml, jsonschema
- **Data Processing**: lxml, openpyxl, xlrd
- **Async Support**: aiofiles, aiolimiter
- **Monitoring**: python-json-logger, colorama
- **Retry Logic**: tenacity
- **Optional AI**: openai (disabled by default)

## Build System

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Windows setup (automated)
setup-windows.bat

# Linux/WSL setup
chmod +x scripts/setup_unix.sh
./scripts/setup_unix.sh
```

### Common Commands

```bash
# Run main system
python run_custom_poundwholesale.py

# Alternative launcher
python run_complete_fba_system.py

# Start Chrome with debug port
chrome --remote-debugging-port=9222 --user-data-dir=C:\temp\chrome-debug

# Run tests
python test_windows_compatibility.py
pytest tests/

# Code formatting
black .
ruff check .

# System monitoring
python run_system_audit.py
```

### Environment Setup

Required environment variables in `.env`:
```bash
# Optional API keys
OPENAI_API_KEY=your-key-here
KEEPA_API_KEY=your-key-here

# Browser configuration
CHROME_DEBUG_PORT=9222

# Memory thresholds
BROWSER_MEMORY_THRESHOLD_MB=2048
```

## Platform-Specific Notes

### Windows
- Uses ProactorEventLoop for Python 3.13+
- Native memory management with psutil
- Atomic file operations via WindowsSaveGuardian
- Task Manager integration

### Linux/WSL
- Standard SelectorEventLoop
- WSL memory monitoring
- Standard file operations
- htop/system monitor integration