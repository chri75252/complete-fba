# Amazon FBA Agent System v3.8+

![System Status](https://img.shields.io/badge/Status-Production_Ready-green) ![Version](https://img.shields.io/badge/Version-3.8_enhanced-blue) ![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey) ![Architecture](https://img.shields.io/badge/Architecture-Enhanced-brightgreen)

**Last Updated:** August 18, 2025  
**Major Enhancement:** State Consistency Fixes & Production Workflow Optimization Complete

---

## 🎯 **SYSTEM OVERVIEW**

The Amazon FBA Agent System v3.8+ is a production-ready automation platform designed for robust, resumable, and highly efficient FBA product sourcing from supplier websites. The system features comprehensive architectural enhancements including **always-extract workflow fixes**, **unified state management**, **invariant enforcement**, and **comprehensive error recovery**.

### **🚀 Key Features**

- ✅ **Unified State Management**: Eliminates state drift and resume failures with atomic operations
- ✅ **Filter Invariant Enforcement**: Mandatory validation with automatic repair mechanisms
- ✅ **Data Integrity Guardian**: Startup reconciliation and corruption detection
- ✅ **Resume Controller**: Intelligent resume point validation with safe fallbacks
- ✅ **Product Cache Hash Optimization**: O(1) duplicate prevention with 240x performance improvement
- ✅ **Smart Memory Management**: Sliding window approach with 99% reduction in clearing operations
- ✅ **File-Based Progress Tracking**: Seven zero-risk methods for always-accurate progress counts
- ✅ **Windows Native Support**: Full Windows compatibility with enhanced memory monitoring
- ✅ **Comprehensive Error Recovery**: Automatic detection and repair of data inconsistencies

---

## 🎯 **SYSTEM ARCHITECTURE**

The Amazon FBA Agent System features a robust, multi-tier architecture designed for scalability, reliability, and performance. The system processes supplier data, matches products with Amazon listings, and calculates profitability metrics.

---

## 🚀 **QUICK START**

### **Windows Setup (Recommended)**

```cmd
# 1. Run automated Windows setup
setup-windows.bat

# 2. Start Chrome with debug port
chrome --remote-debugging-port=9222 --user-data-dir=C:\temp\chrome-debug

# 3. Set API key (optional - can be configured in .env)
set OPENAI_API_KEY=your-api-key-here

# 4. Run the system
run-windows.bat
```

### **Linux/WSL Setup**

```bash
# 1. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 2. Start Chrome with debug port
chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug

# 3. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 4. Run the system
python run_custom_poundwholesale.py
```

---

## 📋 **PREREQUISITES**

### **Required Software**
- **Python 3.8+** with pip
- **Google Chrome** (latest version)
- **8GB+ RAM** (recommended for large processing sessions)

### **Optional API Keys**
- **OpenAI API Key** (for AI-powered features - currently disabled by default)
- **Keepa API Key** (for enhanced Amazon data - optional)

### **Platform-Specific Requirements**

#### **Windows**
- Windows 10/11 (any edition)
- Windows Terminal (recommended)
- No WSL required

#### **Linux/WSL**
- Ubuntu 20.04+ or compatible distribution
- WSL2 (if running on Windows)

---

## 🏗️ **ENHANCED WORKFLOW ARCHITECTURE**

```
┌─────────────────────────────────────────────────────────────────┐
│                   ENHANCED WORKFLOW EXECUTION                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🎯 ENTRY POINTS                                               │
│  ├── run_custom_poundwholesale.py                              │
│  └── run_complete_fba_system.py                                │
│                         │                                       │
│                         ▼                                       │
│  🏭 CORE WORKFLOW ENGINE (Enhanced)                            │
│  └── tools/passive_extraction_workflow_latest.py               │
│                         │                                       │
│  ┌─────────────────────┼─────────────────────┐                │
│  │                     │                     │                │
│  ▼                     ▼                     ▼                │
│  🛡️ STATE MANAGEMENT   🔧 PROCESSING TOOLS   ⚙️ CONFIG         │
│  ├── fixed_enhanced_   ├── configurable_     ├── system_       │
│  │   state_manager     │   supplier_scraper  │   config_loader │
│  ├── url_filter        ├── amazon_playwright_└── [loads JSON]  │
│  │   (enhanced)        │   extractor                           │
│  ├── data_integrity_   ├── FBA_Financial_                      │
│  │   guardian          │   calculator                          │
│  └── resume_controller └── cache_manager                       │
│                                                                 │
│  🔗 ENHANCED UTILITIES                                          │
│  ├── windows_save_guardian ←─── atomic file operations         │
│  ├── sentinel_monitor ←─── system monitoring                   │
│  ├── browser_manager ←─── browser health management            │
│  └── path_manager ←─── standardized path management            │
│                                                                 │
│  🚨 NEW COMPONENTS (v3.8+)                                     │
│  ├── StartupOrchestrator - Mandatory startup sequence          │
│  ├── ErrorHandler - Comprehensive error recovery               │
│  ├── QueueProcessor - Separate phase processing                │
│  └── ResumeController - Intelligent resume validation          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 **CORE COMPONENTS**

### **🎯 ENHANCED WORKFLOW EXECUTION CHAIN**

**Main Entry Points:**
- **`run_custom_poundwholesale.py`** ✅ - Primary launcher script
- **`run_complete_fba_system.py`** ✅ - Alternative system launcher

**Central Workflow Engine:**
- **`tools/passive_extraction_workflow_latest.py`** ✅ - Core orchestrator with enhanced state management

### **🛡️ STATE MANAGEMENT COMPONENTS (NEW)**

**Core State Management:**
- **`utils/fixed_enhanced_state_manager.py`** ✅ - Unified state management with atomic operations
- **`utils/url_filter.py`** ✅ - Enhanced URL filtering with invariant enforcement
- **Data Integrity Guardian** ✅ - Startup reconciliation and corruption detection
- **Resume Controller** ✅ - Intelligent resume point validation with safe fallbacks

**Processing Components:**
- **Queue Processor** ✅ - Separate supplier and Amazon processing phases
- **Startup Orchestrator** ✅ - Mandatory startup sequence orchestration
- **Error Handler** ✅ - Comprehensive error handling and recovery

### **📦 PROCESSING TOOLS (Enhanced)**

**Core Processing Tools:**
- **`tools/configurable_supplier_scraper.py`** ✅ - Supplier data extraction with enhanced filtering
- **`tools/amazon_playwright_extractor.py`** ✅ - Amazon data extraction with Playwright
- **`tools/FBA_Financial_calculator.py`** ✅ - Financial analysis and ROI calculations
- **`tools/cache_manager.py`** ✅ - Data caching and persistence

**Essential Utils:**
- **`utils/windows_save_guardian.py`** ✅ - Atomic file operations for Windows
- **`utils/sentinel_monitor.py`** ✅ - System monitoring and divergence detection
- **`utils/browser_manager.py`** ✅ - Browser health management and restart
- **`utils/path_manager.py`** ✅ - Standardized path management



---

## 📊 **MONITORING & LOGGING**

### **System Monitoring**
```bash
# Monitor system execution
tail -f logs/debug/*.log

# Check processing progress
grep "Processing" logs/debug/*.log

# Monitor performance metrics
grep "Performance" logs/debug/*.log

# Check system health
python scripts/state_dump.py --health-check
```

---

## ⚙️ **CONFIGURATION**

### **System Configuration (`config/system_config.json`)**

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
  "browser": {
    "restart_interval_hours": 2.5,
    "memory_threshold_gb": 2
  }
}
```

### **Environment Variables**

```bash
# API Configuration
OPENAI_API_KEY=your-api-key-here
KEEPA_API_KEY=your-keepa-key-here

# System Settings
CHROME_DEBUG_PORT=9222
```

---

## 📁 **OUTPUT STRUCTURE**

```
OUTPUTS/
├── cached_products/                    # Supplier product cache
├── FBA_ANALYSIS/
│   ├── amazon_cache/                   # Individual Amazon product data
│   ├── linking_maps/                   # EAN→ASIN mappings
│   └── financial_reports/              # Profitability analysis
├── CACHE/
│   └── processing_states/              # State management
│       └── poundwholesale-co-uk_processing_state.json
└── logs/
    └── debug/                          # Execution logs
```

---

## 🧪 **TESTING**

### **Run System Tests**

```bash
# Basic functionality tests
python tests/test_basic_functionality.py

# Integration tests
python tests/test_integration.py

# Performance tests
python tests/test_calculation_performance.py
```

---

## 📚 **DOCUMENTATION**

### **User Guides**
- **[Configuration Guide](docs/CONFIGURATION_GUIDE.md)** - System configuration
- **[Troubleshooting Guide](docs/TROUBLESHOOTING.md)** - Problem diagnosis and resolution
- **[Installation Guide](INSTALLATION_GUIDE.md)** - Setup instructions

### **Technical References**
- **[API Documentation](docs/API_REFERENCE.md)** - Complete API reference
- **[State Management Guide](docs/UNIFIED_STATE_MANAGEMENT_GUIDE.md)** - State management details
- **[Filter Guide](docs/FILTER_INVARIANT_GUIDE.md)** - URL filtering system

---

## 🎯 **PERFORMANCE METRICS**

### **System Capabilities**
- **Processing Capacity**: 1M+ products per run
- **Session Duration**: 18+ hours without intervention
- **Cache Performance**: 240x improvement with hash optimization
- **Memory Management**: 99% reduction in clearing operations
- **Resume Reliability**: Intelligent resume point validation

---

## 🛠️ **TROUBLESHOOTING**

### **Common Issues**

#### **Browser Connection Issues**
```bash
# Check Chrome debug port
netstat -an | findstr 9222

# Restart Chrome with debug port
chrome --remote-debugging-port=9222 --user-data-dir=C:\temp\chrome-debug
```

#### **Authentication Issues**
```bash
# Check authentication status
python -c "from tools.authentication_manager import AuthenticationManager; auth = AuthenticationManager(); print(auth.check_status())"
```

#### **Performance Issues**
```bash
# Check system resources
python -c "import psutil; print(f'Memory: {psutil.virtual_memory().percent}%')"

# Monitor processing logs
tail -f logs/debug/*.log
```

---

## 🆘 **SUPPORT**

### **Getting Help**
1. **Check Documentation**: Review guides in `/docs`
2. **Run Tests**: Use test scripts in `/tests` for diagnostics
3. **Check Logs**: Review logs in `logs/debug/`
4. **Review Configuration**: Verify `config/system_config.json`

### **Success Indicators**
- ✅ System starts without errors
- ✅ Browser connects successfully
- ✅ Authentication completes
- ✅ Processing begins normally

---

**System Status:** ✅ Production Ready  
**Last Tested:** August 18, 2025  
**Platform Compatibility:** Windows 10/11, Linux, WSL2  
**Python Compatibility:** 3.8+

**Happy scraping!** 🚀