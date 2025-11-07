# Project Index: Amazon FBA Agent System v3.7+

**Generated:** 2025-10-31T16:30:00Z
**Type:** Production Automation Platform
**Primary Language:** Python + Playwright + Chrome CDP

---

## 🎯 System Overview

The Amazon FBA Agent System v3.7+ is a production-ready automation platform for FBA product sourcing from supplier websites to Amazon marketplace. It features file-grounded state management, Chrome v139+ compatibility, smart memory management, and resumable processing workflows using Playwright browser automation.

**Key Characteristics:**
- **Configurable Entry Point**: Launched via `run_custom_poundwholesale.py` with operational settings from `config/system_config.json`
- **No AI Logic**: All AI features are **disabled** - uses deterministic, selector-based scraping and matching
- **Complete Resumable Processing**: Full workflow implementation with state persistence after every operation
- **Chrome v139+ Compatible**: IPv6/IPv4 dual-stack implementation with automatic endpoint detection
- **File-Grounded State**: All state calculations based on actual files, not memory variables

---

## 🚀 Entry Points

### Primary CLI Launchers

| Entry Point | File | Line | Usage | Dependencies |
|-------------|------|------|-------|--------------|
| **Main PoundWholesale Runner** | `run_custom_poundwholesale.py` | 1 | `python run_custom_poundwholesale.py` | Chrome CDP, Playwright, system_config.json |
| **Clearance King Runner** | `run_custom_clearance_king.py` | 1 | `python run_custom_clearance_king.py` | Chrome CDP, Playwright, system_config.json |

**Development Entry Points:**
- `tools/passive_extraction_workflow_latest.py:93` - PassiveExtractionWorkflow class
- `utils/fixed_enhanced_state_manager.py:314` - State management load method
- `config/system_config.json:1` - Master configuration settings

---

## 🏗️ Core Workflow Architecture

### Main Orchestrator (2,650 lines)

**PassiveExtractionWorkflow** (`tools/passive_extraction_workflow_latest.py:851`)
- **Main Entry Point**: `run()` method (line 1970)
- **Key Methods**:
  - `_extract_supplier_products()` (line 2318) - Batched supplier scraping
  - `_get_amazon_data()` (line 2437) - EAN-first, title-fallback matching
  - `_validate_product_match()` (line 2548) - Title similarity scoring

### Amazon Integration (400+ lines)

**FixedAmazonExtractor** (`tools/passive_extraction_workflow_latest.py:435`)
- **Primary Search**: `search_by_ean_and_extract_data()` (line 625)
- **Data Extraction**: `extract_data()` (line 824)
- **Chrome Extension Support**: Browser page reuse for extension functionality

---

## 🔧 Critical Utilities

| Component | File | Purpose | Key Features |
|-----------|------|---------|--------------|
| **State Manager** | `utils/fixed_enhanced_state_manager.py` | File-grounded state management | Freeze-Mark-Resume, atomic operations |
| **Browser Manager** | `utils/browser_manager.py` | Chrome CDP connection | IPv6/IPv4 dual-stack, auto-restart |
| **Windows Guardian** | `utils/windows_save_guardian.py` | Atomic file operations | Windows compatibility, crash protection |
| **Path Manager** | `utils/path_manager.py` | Cross-platform paths | Unified path handling across OS |

---

## 📁 Output Structure & Data Flow

### State Management
```
OUTPUTS/CACHE/processing_states/
└── poundwholesale_co_uk_processing_state.json
    ├── created_at (timestamp)
    ├── current_phase (supplier|amazon_analysis)
    ├── persistent_category_index (NEVER resets)
    └── frozen_category_denominators (write-once)
```

### Data Caching
```
OUTPUTS/
├── cached_products/
│   └── poundwholesale-co-uk_products_cache.json (supplier data)
├── FBA_ANALYSIS/
│   ├── amazon_cache/ (200+ Amazon product files)
│   ├── linking_maps/ (EAN→ASIN mappings by supplier)
│   └── financial_reports/ (CSV profitability reports)
└── logs/debug/ (48-day execution history)
```

### Configuration System
- **Master Config**: `config/system_config.json` (processing limits, browser settings)
- **Category URLs**: `config/poundwholesale_categories.json`, `config/clearance_king_categories.json`
- **Supplier Configs**: `config/supplier_configs/` (credentials and settings)

---

## 🔄 Workflow Phases

### Phase 1: System Initialization
- Chrome CDP connection (IPv6/IPv4 auto-detection)
- Authentication verification
- Configuration loading from `system_config.json`
- Startup state analysis (file-grounded calculations)

### Phase 2: Category Processing Sequence
For each category in config:
1. **URL Discovery & Manifest Generation** (BEFORE initialization)
2. **Category Initialization** (AFTER freezing denominator)
3. **Product Processing Loop** with resume pointer validation

### Phase 3: Main Processing Loop
- Supplier data extraction with O(1) duplicate prevention
- Amazon analysis (EAN-first, title fallback)
- Financial calculations (UK marketplace, 20% VAT)
- Atomic state commits every N products

### Phase 4: Output Generation
- Comprehensive financial reports (CSV)
- JSON product lists
- State persistence for resumption

---

## 🧪 Test Infrastructure

### Test Suites
- **Unit Tests**: `tests/test_atomic_operations.py`
- **Integration Tests**: `tests/test_three_source_validation_fix.py`
- **Regression Guards**: `tests/test_p0_regression_guard_fix.py`
- **Validation Testing**: `testing/` directory utilities

### Quality Assurance
- Comprehensive logging system (debug, health, application logs)
- Real-time performance monitoring
- System diagnostics and validation tools
- Sentinel monitoring for divergence detection

---

## ⚡ Key Architectural Patterns

### Freeze-Mark-Resume Sequence
1. **Freeze**: Denominator frozen on first category encounter (write-once)
2. **Mark**: State committed atomically with WindowsSaveGuardian
3. **Resume**: Direct routing to correct phase and position

### File-Grounded State Management
- Seven zero-risk methods for progress tracking from persistent files
- Thread-safe atomic operations with RLock
- Monotonic pointer advancement (never goes backward)

### Smart Memory Management
- Sliding window approach (clear at 500 products, keep recent 100)
- 99% reduction in memory clearing operations
- Automatic browser restart every 2.5 hours

---

## 🎯 Quick Start Guide

### Prerequisites
1. **Start Chrome with debug port** (REQUIRED):
   ```bash
   chrome --remote-debugging-port=9222 --user-data-dir=C:\temp\chrome-debug
   ```
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Install Playwright browsers**: `playwright install chromium`

### Launch Commands
```bash
# Main automation (PoundWholesale)
python run_custom_poundwholesale.py

# Alternative supplier (ClearanceKing)
python run_custom_clearance_king.py
```

### Verification Points
- ✅ Check `OUTPUTS/CACHE/processing_states/` for state files
- ✅ Monitor `logs/debug/` for execution progress
- ✅ Review `OUTPUTS/FBA_ANALYSIS/financial_reports/` for results

---

## ⚠️ Technical Debt & Cleanup

### Known Issues
- **17 backup directories** consuming space (recommend cleanup after validation)
- **8 duplicate tool versions** with `*-good.py`, `-Copy.py` suffixes
- Multiple archived implementations in `archive/` directory

### Repository Health
- ✅ **Well-structured** with clear separation of concerns
- ✅ **Comprehensive testing** infrastructure
- ✅ **Robust error handling** and logging
- ✅ **Cross-platform compatibility** (Windows/Linux/WSL2)
- ⚠️ **Contains archived files** that could be cleaned up

---

## 📊 System Metrics

| Metric | Value | Status |
|--------|-------|--------|
| **Codebase Size** | 12,039 lines (main workflow) | Production |
| **Test Coverage** | Comprehensive | ✅ Active |
| **Documentation** | Enterprise-grade | ✅ Current |
| **Chrome Compatibility** | v139+ with dual-stack | ✅ Validated |
| **Platform Support** | Windows 10/11, Linux, WSL2 | ✅ Tested |
| **Python Version** | 3.8+ compatible | ✅ Verified |

**System Status**: ✅ Production Ready
**Last Updated**: October 17, 2025
**Recommended for**: Enterprise FBA automation workflows