# Installation and Setup

<cite>
**Referenced Files in This Document**   
- [requirements.txt](file://requirements.txt)
- [INSTALLATION_GUIDE.md](file://INSTALLATION_GUIDE.md)
- [WINDOWS_SETUP_GUIDE.md](file://WINDOWS_SETUP_GUIDE.md)
- [system_config.json](file://config/system_config.json)
- [atomic_file_operations.py](file://utils/atomic_file_operations.py)
</cite>

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Windows Installation](#windows-installation)
3. [Linux/WSL Installation](#linuxwsl-installation)
4. [Dependency Management](#dependency-management)
5. [Chrome Configuration](#chrome-configuration)
6. [Environment Setup](#environment-setup)
7. [Configuration Files](#configuration-files)
8. [Common Issues and Solutions](#common-issues-and-solutions)
9. [Performance Considerations](#performance-considerations)
10. [Validation and Testing](#validation-and-testing)

## Prerequisites

Before installing the Amazon FBA Agent System, ensure your system meets the following requirements:

- **Python 3.8+**: Required for system operation. The system has been tested with Python 3.13.3.
- **Google Chrome**: Latest version required for browser automation via Chrome DevTools Protocol (CDP).
- **Operating Systems**: Windows 10/11, Linux (Ubuntu 20.04+), or WSL2.
- **Hardware**: Minimum 8GB RAM recommended for optimal performance.
- **API Keys**: Optional OpenAI and Keepa API keys for AI features (disabled by default).

The system leverages Windows-native support for enhanced memory management and atomic file operations, providing improved stability and performance on Windows platforms.

**Section sources**
- [INSTALLATION_GUIDE.md](file://INSTALLATION_GUIDE.md#L1-L587)
- [WINDOWS_SETUP_GUIDE.md](file://WINDOWS_SETUP_GUIDE.md#L1-L341)

## Windows Installation

### Automated Setup

The Amazon FBA Agent System provides automated setup scripts for Windows environments:

```cmd
setup-windows.bat
```

This script performs the following operations:
- Installs all Python dependencies from `requirements.txt`
- Installs Playwright browsers using `playwright install chromium`
- Creates required directories (OUTPUTS, logs, etc.)
- Tests Windows memory manager compatibility
- Verifies system requirements

### Manual Setup Steps

1. **Install Python**: Download from python.org and ensure "Add Python to PATH" is checked during installation.
2. **Clone Repository**: 
   ```cmd
   git clone [repository-url]
   cd Amazon-FBA-Agent-System-v32
   ```
3. **Run Setup Script**: Execute `setup-windows.bat` to install dependencies and configure the environment.
4. **Start Chrome with Debug Port**:
   ```cmd
   chrome --remote-debugging-port=9222 --user-data-dir=C:\temp\chrome-debug
   ```

### Windows-Specific Features

The system implements Windows-native support for enhanced functionality:
- **Atomic File Operations**: Ensures data integrity during file operations using Windows file locking mechanisms.
- **Enhanced Memory Management**: Native Windows memory monitoring and cleanup.
- **Direct Process Control**: Real-time Chrome process monitoring and management.

**Section sources**
- [INSTALLATION_GUIDE.md](file://INSTALLATION_GUIDE.md#L59-L206)
- [WINDOWS_SETUP_GUIDE.md](file://WINDOWS_SETUP_GUIDE.md#L1-L341)
- [atomic_file_operations.py](file://utils/atomic_file_operations.py#L1-L189)

## Linux/WSL Installation

### System Dependencies

Install essential system packages:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git curl wget unzip build-essential libssl-dev libffi-dev python3-dev
```

### Python Environment Setup

Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Browser Configuration

Install Chrome and Playwright dependencies:
```bash
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install -y google-chrome-stable
playwright install chromium
playwright install-deps
```

### WSL-Specific Configuration

For WSL2 environments, add the following to your shell configuration:
```bash
export DISPLAY=:0
export LIBGL_ALWAYS_INDIRECT=1
```

Configure WSL memory management by adding to `/etc/wsl.conf`:
```ini
[wsl2]
memory=8GB
processors=4
```

**Section sources**
- [INSTALLATION_GUIDE.md](file://INSTALLATION_GUIDE.md#L207-L338)

## Dependency Management

### Core Dependencies

The system relies on the following core dependencies specified in `requirements.txt`:

```txt
aiohttp==3.9.1
beautifulsoup4==4.12.2
requests==2.31.0
pandas==2.1.4
numpy==1.26.2
playwright==1.40.0
python-dotenv==1.0.0
```

### Installation Process

Dependencies are installed using pip:
```bash
pip install -r requirements.txt
```

Playwright-specific browser dependencies:
```bash
playwright install chromium
```

For Linux systems, additional dependencies may be required:
```bash
playwright install-deps
```

The system uses atomic file operations to ensure dependency integrity during installation and runtime operations.

**Section sources**
- [requirements.txt](file://requirements.txt#L1-L81)
- [INSTALLATION_GUIDE.md](file://INSTALLATION_GUIDE.md#L59-L587)

## Chrome Configuration

### Debug Port Setup

The system requires Chrome to run with remote debugging enabled:

**Windows**:
```cmd
chrome --remote-debugging-port=9222 --user-data-dir=C:\temp\chrome-debug
```

**Linux/WSL**:
```bash
google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug --no-sandbox &
```

### Verification

Verify Chrome is running with debugging enabled by navigating to:
```
http://localhost:9222
```

You should see the Chrome DevTools Protocol page displaying active browser contexts.

### Configuration in System

Chrome settings are configured in `config/system_config.json`:
```json
"chrome": {
  "debug_port": 9222,
  "headless": false
}
```

The system automatically connects to the specified debug port for browser automation tasks.

**Section sources**
- [INSTALLATION_GUIDE.md](file://INSTALLATION_GUIDE.md#L130-L148)
- [system_config.json](file://config/system_config.json#L270-L274)

## Environment Setup

### Environment Variables

Create a `.env` file in the project root directory:
```bash
OPENAI_API_KEY=your-openai-api-key-here
KEEPA_API_KEY=your-keepa-api-key-here
CHROME_DEBUG_PORT=9222
BROWSER_MEMORY_THRESHOLD_MB=2048
```

### API Key Configuration

Three methods are available for API key setup:

1. **Environment Variable (Temporary)**:
   ```cmd
   set OPENAI_API_KEY=your-api-key-here
   ```

2. **.env File (Permanent)**:
   Create `.env` with API key values.

3. **System Environment Variable (Global)**:
   Add `OPENAI_API_KEY` to system environment variables.

### Running the System

**Windows**:
```cmd
run-windows.bat
```

**Linux/WSL**:
```bash
python3 run_custom_poundwholesale.py
```

The system will automatically detect the platform and apply appropriate configuration settings.

**Section sources**
- [INSTALLATION_GUIDE.md](file://INSTALLATION_GUIDE.md#L149-L174)
- [WINDOWS_SETUP_GUIDE.md](file://WINDOWS_SETUP_GUIDE.md#L1-L341)

## Configuration Files

### system_config.json

The main configuration file contains system-wide settings:

```json
{
  "system": {
    "max_products": 1000000,
    "max_products_per_category": 1000,
    "supplier_extraction_batch_size": 100
  },
  "processing_limits": {
    "min_price_gbp": 0.01,
    "max_price_gbp": 20.0
  },
  "chrome": {
    "debug_port": 9222,
    "headless": false
  }
}
```

Key configuration sections include:
- **system**: Core system parameters and limits
- **processing_limits**: Price and product quantity filters
- **chrome**: Browser automation settings
- **authentication**: Supplier login configuration
- **performance**: Request and timeout settings

### atomic_file_operations.py

This module provides atomic file operations with cross-platform support:

- **Thread-safe operations**: Ensures data integrity during concurrent access
- **File locking**: Implements platform-specific file locking mechanisms
- **Atomic writes**: Uses temporary files and atomic renames
- **JSON validation**: Validates file integrity before and after operations

The atomic operations are critical for maintaining data consistency during system operation, especially for state management files.

**Section sources**
- [system_config.json](file://config/system_config.json#L1-L300)
- [atomic_file_operations.py](file://utils/atomic_file_operations.py#L1-L189)

## Common Issues and Solutions

### Chrome Debug Port Accessibility

**Issue**: Chrome debug port not accessible at `localhost:9222`

**Solutions**:
- **Windows**:
  ```cmd
  taskkill /F /IM chrome.exe
  chrome --remote-debugging-port=9222 --user-data-dir=C:\temp\chrome-debug
  ```
- **Linux/WSL**:
  ```bash
  pkill chrome
  google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug --no-sandbox &
  ```

### File Permission Errors

**Issue**: Permission denied errors during file operations

**Solutions**:
- **Windows**: Run Command Prompt as Administrator
- **Linux/WSL**: 
  ```bash
  chmod +x run_custom_poundwholesale.py
  sudo chown -R $USER:$USER .
  ```

### Dependency Installation Issues

**Issue**: Module not found errors

**Solutions**:
```bash
pip install -r requirements.txt --force-reinstall
playwright install chromium
```

### Memory Management Issues

The system includes built-in memory management that automatically handles:
- Chrome process monitoring
- Memory cleanup when thresholds are exceeded
- Browser restarts when memory usage is high

Monitor memory usage through the system logs in `logs/health/`.

**Section sources**
- [INSTALLATION_GUIDE.md](file://INSTALLATION_GUIDE.md#L478-L538)
- [CHROME_CDP_CONNECTIVITY_TROUBLESHOOTING_REPORT.md](file://CHROME_CDP_CONNECTIVITY_TROUBLESHOOTING_REPORT.md#L1-L126)

## Performance Considerations

### Hardware Requirements

- **Minimum**: 8GB RAM, 2+ CPU cores
- **Recommended**: 16GB+ RAM, SSD storage, 4+ CPU cores

### Platform-Specific Performance

**Windows Advantages**:
- **Accurate Memory Monitoring**: Direct Chrome process monitoring
- **Stable WebSocket Connections**: No WSL networking layer
- **Direct Process Control**: Native Chrome management
- **No VmmemWSL Issues**: Eliminates WSL memory accumulation

**WSL2 Considerations**:
- Configure adequate memory allocation in `/etc/wsl.conf`
- Monitor VmmemWSL process for memory usage
- Use SSD storage for better I/O performance

### Long-Running Sessions

The system is optimized for extended operations:
- **8-12+ hour sessions**: Stable long-running operations
- **Automatic recovery**: Enhanced restart logic
- **Memory efficiency**: <2GB sustained usage
- **Session reliability**: Marathon sessions without failures

### Optimization Tips

- Close unnecessary applications to free system resources
- Use SSD storage for faster I/O operations
- Monitor system resources using Task Manager (Windows) or htop (Linux)
- Ensure adequate virtual memory configuration

**Section sources**
- [INSTALLATION_GUIDE.md](file://INSTALLATION_GUIDE.md#L539-L587)
- [WINDOWS_SETUP_GUIDE.md](file://WINDOWS_SETUP_GUIDE.md#L1-L341)

## Validation and Testing

### System Compatibility Test

Run the Windows compatibility test:
```cmd
python test_windows_compatibility.py
```

Expected output:
```
🪟 Windows Compatibility Test Suite
==================================================
✅ Windows detected - will use Windows-native memory management
✅ PassiveExtractionWorkflow imported successfully
✅ BrowserManager imported successfully
✅ WindowsMemoryManager imported successfully
✅ Memory monitoring function working
🎉 ALL TESTS PASSED - System is Windows compatible!
```

### Browser Connectivity Test

Verify Chrome connectivity:
```bash
curl http://localhost:9222/json/version
```

### Expected Startup Output

Upon successful installation, the system should display:
```
🚀 --- Starting Amazon FBA Agent System v3.7+ ---
✅ Platform: Windows (or Linux)
✅ Python: 3.11.0
✅ Smart Memory Management: Enabled
✅ File-Based Progress Tracking: Enabled
✅ Browser Health Management: Enabled
```

### Monitoring Commands

**Real-time log monitoring**:
```bash
# Windows
type logs\debug\run_custom_poundwholesale_*.log

# Linux/WSL
tail -f logs/debug/run_custom_poundwholesale_*.log
```

**Performance dashboard**:
```bash
# Check cached products
python -c "import json; print(len(json.load(open('OUTPUTS/cached_products/poundwholesale-co-uk_products_cache.json', 'r'))))"
```

**Section sources**
- [INSTALLATION_GUIDE.md](file://INSTALLATION_GUIDE.md#L339-L477)