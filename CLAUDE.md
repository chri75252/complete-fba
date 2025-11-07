# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚨 CRITICAL IMPLEMENTATION STANDARDS

### **MANDATORY VERIFICATION PROTOCOLS**
- **🚨 NO CLAIMS WITHOUT VERIFICATION**: Tasks cannot be marked complete without actual file verification
- **🚨 MANDATORY_FILE_VERIFICATION**: When referencing files you MUST:
  1. ✅ **VERIFY_EXISTENCE**: Check file/directory exists at specified path
  2. ✅ **CHECK_TIMESTAMP**: Verify file creation/modification timestamp is recent
  3. ✅ **VERIFY_CONTENT**: Read and analyze actual file content before making claims
  4. ✅ **CONFIRM_SUPPLIER**: Ensure correct supplier reference (poundwholesale.co.uk vs clearance-king.co.uk)
  5. ✅ **PROVIDE_FULL_PATHS**: Always use complete absolute directory paths
  6. ✅ **NO_ASSUMPTIONS**: Never reference files without first reading and verifying

### **🚨 MANDATORY BACKUP PROTOCOL**
Before testing any script or making major edits:
1. ✅ **CREATE_BACKUP_DIRECTORY**: Create "backup" folder in same directory
2. ✅ **DATED_SUBFOLDER**: Create subfolder with brief reason + date (e.g., "test_change_20251006")
3. ✅ **BACKUP_ALL_AFFECTED**: Copy ALL files/folders/scripts that might be affected
4. ✅ **VERIFY_BACKUP**: Confirm backup created successfully before proceeding

### **🚨 UPDATE PROTOCOL - CRITICAL COMPLIANCE**
When updating ANY file, script, output, or folder:
1. **⚠️ CASCADING UPDATES**: Check ALL related files that reference the changed item
2. **⚠️ DOCUMENTATION SYNC**: Update ALL relevant documentation with new paths/procedures
3. **⚠️ PATH CONSISTENCY CHECK**: Verify path_manager.py and system_config.json reflect changes

### **🔒 SERENA MCP READ-ONLY USAGE**
**Purpose**: Discovery & verification only - NEVER write/mutate with Serena
**Order**: Investigate → hypothesize minimal change → use Serena to validate coverage → manual edits

## Project Overview

The Amazon FBA Agent System v3.7+ is a production-ready automation platform for FBA product sourcing from supplier websites to Amazon marketplace. It features file-grounded state management, Chrome v139+ compatibility, smart memory management, and resumable processing workflows using Playwright browser automation.

### **🎯 System Characteristics**
- **Configurable Entry Point**: Launched via `run_custom_poundwholesale.py` with operational settings from `config/system_config.json`
- **No AI Logic**: All AI features are **disabled** - uses deterministic, selector-based scraping and matching
- **Single-Phase Price Scraping**: Processes full price range (`min_price_gbp` to `max_price_gbp` from config)
- **Complete Resumable Processing**: Full workflow implementation with state persistence after every operation
- **Chrome v139+ Compatible**: IPv6/IPv4 dual-stack implementation with automatic endpoint detection
- **File-Grounded State**: All state calculations based on actual files, not memory variables

## Commands

### **🚀 Running the System**

**Main Entry Point:**
```bash
python run_custom_poundwholesale.py
```

**Prerequisites:**
1. **Start Chrome with debug port** (REQUIRED):
   - Windows: `chrome --remote-debugging-port=9222 --user-data-dir=C:\temp\chrome-debug`
   - Linux: `chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug`
2. **Verify Chrome connection**: `curl http://localhost:9222/json/version`
3. **Install dependencies**: `pip install -r requirements.txt`
4. **Install Playwright browsers**: `playwright install chromium`

**Alternative Entry Point:**
```bash
python run_complete_fba_system.py
```

### **🧪 Testing**

**Environment Setup:**
```bash
# Create isolated environment (REQUIRED)
python -m venv .venv
source .venv/bin/activate  # Linux/WSL
# .venv\Scripts\activate   # Windows

# Install test dependencies
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-mock pytest-cov
```

**Test Execution:**
```bash
# Run all tests
pytest

# Specific test categories
pytest tests/unit/                    # Unit tests only
pytest -m integration                  # Integration tests (requires external services)
pytest -m e2e                         # End-to-end tests (requires full system setup)
pytest tests/performance/ --benchmark-only  # Performance tests

# Code quality checks
tox -e lint                          # Linting and formatting
tox -e format                        # Auto-format code
tox -e type-check                    # Type checking with mypy
tox -e security                      # Security vulnerability scanning

# Coverage reporting
tox -e coverage-report
```

**🚨 TASK_SUCCESS_CRITERIA**: For testing to be considered successful:
1. ✅ **CORRECT_TIMESTAMP**: Every file must have accurate creation/modification timestamp
2. ✅ **CORRECT_FILE_PATH**: Exact absolute path verified and accessible
3. ✅ **CORRECT_SCRIPT_EXECUTION**: All expected scripts ran in correct order
4. ✅ **CONTENT_VERIFICATION**: File content analyzed and verified against expectations

### **🔧 Development Tools**

**System Diagnostics:**
```bash
# Chrome v139+ compatibility verification
python utils/browser_manager.py --health-check --auto-restart

# Memory management validation
python test_memory_leak_fixes.py

# State file validation
python utils/fixed_enhanced_state_manager.py --validate-state --supplier=poundwholesale-co-uk

# Comprehensive system audit
python run_system_audit.py
```

## Architecture

### **🏗️ Complete Workflow Architecture**

The system follows a **Freeze-Mark-Resume** sequence with file-grounded state management:

```
[run_custom_poundwholesale.py] (Entry Point)
     │
     ▼
[PassiveExtractionWorkflow::run] (Core Orchestrator - 413 KB implementation)
     │
     ├─> 1. 🎯 System Initialization
     │    ├─> Chrome CDP connection (IPv6/IPv4 auto-detection)
     │    ├─> Authentication verification
     │    ├─> Configuration loading (system_config.json)
     │    └─> Startup state analysis (file-grounded calculations)
     │
     ├─> 2. 📂 Category Processing Sequence (NEW SEQUENCE)
     │    └─> For each category in config/poundwholesale_categories.json:
     │        ├─> a. URL Discovery & Manifest Generation (BEFORE initialization)
     │        │   ├─> Scrape category page for all product URLs
     │        │   ├─> Save complete URL list atomically to manifest
     │        │   └─> Freeze denominator (write-once, never changes)
     │        ├─> b. Category Initialization (AFTER freezing)
     │        │   ├─> Initialize category processing with frozen denominators
     │        │   ├─> Setup progress tracking with access to frozen totals
     │        │   └─> Handle empty categories (denominator=0, mark complete)
     │        └─> c. Product Processing Loop
     │            ├─> Resume pointer validation using frozen denominators
     │            ├─> Supplier data extraction
     │            ├─> Amazon analysis (EAN-first, title fallback)
     │            ├─> Financial calculations (UK marketplace, 20% VAT)
     │            └─> Atomic state commits
     │
     ├─> 3. 🔄 Interruption & Resume Behavior
     │    ├─> Atomic state persistence using WindowsSaveGuardian
     │    ├─> Resume pointer storage as {phase, cat_idx, prod_idx}
     │    ├─> Phase-aware resumption (supplier or amazon_analysis)
     │    └─> Monotonic validation (pointers only advance, never regress)
     │
     └─> 4. 📊 Output Generation
```

### **🔧 Core Components & Dependencies**

**Entry Points:**
- `run_custom_poundwholesale.py` - Primary launcher with authentication and browser setup
- `run_complete_fba_system.py` - Alternative system launcher

**Core Workflow Engine:**
- `tools/passive_extraction_workflow_latest.py` - Main orchestrator (413 KB, PassiveExtractionWorkflow class)

**Direct Dependencies (Core Workflow Tools):**
- `tools/configurable_supplier_scraper.py` - Supplier data extraction with URL filtering and O(1) hash-based duplicate prevention
- `tools/amazon_playwright_extractor.py` - Amazon product extraction via Playwright with EAN-first matching
- `tools/FBA_Financial_calculator.py` - Financial analysis and ROI calculations for UK marketplace
- `tools/supplier_authentication_service.py` - Session management and login automation

**Essential Utilities:**
- `utils/fixed_enhanced_state_manager.py` - **CRITICAL**: File-grounded state management with freeze-mark-resume sequence
- `utils/browser_manager.py` - Chrome CDP connection management with IPv6/IPv4 dual-stack support
- `utils/windows_save_guardian.py` - Atomic file operations for Windows compatibility
- `utils/path_manager.py` - Cross-platform path management
- `utils/sentinel_monitor.py` - System monitoring and divergence detection

**Configuration System:**
- `config/system_config_loader.py` - System configuration loading with helper methods
- `config/system_config.json` - Main configuration (processing limits, performance, browser settings)
- `config/poundwholesale_categories.json` - Predefined category URLs
- `config/supplier_configs/` - Supplier-specific configurations and credentials

**Indirect Dependencies (Secondary Utilities):**
- `utils/url_cache_filter.py` - URL deduplication (used by configurable_supplier_scraper)
- `utils/browser_circuit_breaker.py` - Failure protection (used by browser_manager)
- `utils/hash_lookup_optimizer.py` - O(1) duplicate prevention optimization
- `tools/category_completion_tracker.py` - Category processing optimization

### **🎯 Key Architectural Patterns**

**File-Grounded State Management:**
- All state calculations based on actual files, not memory variables
- Seven zero-risk methods for progress tracking from persistent files
- EnhancedStateManager with thread-safe atomic operations
- Resume capability from exact interruption point across sessions

**Freeze-Mark-Resume Sequence:**
1. **Freeze**: Denominator frozen on first category encounter (write-once)
2. **Mark**: State committed atomically with WindowsSaveGuardian
3. **Resume**: Direct routing to correct phase and position

**Smart Memory Management:**
- Sliding window approach (clear at 500 products, keep recent 100)
- 99% reduction in memory clearing operations
- Automatic browser restart every 2.5 hours
- Python garbage collection triggered at 3GB memory usage

**Chrome v139+ Compatibility:**
- IPv6/IPv4 dual-stack implementation with automatic endpoint detection
- Dynamic endpoint detection (no hardcoded localhost:9222)
- Production validated with automatic connection fallback

**Processing Flow:**
1. Load supplier categories and perform startup analysis
2. For each category: URL discovery → manifest generation → denominator freezing → processing
3. Product processing: supplier extraction → Amazon matching → financial analysis → state commit
4. Output generation with comprehensive file tracking

### **📁 Output Structure**

```
OUTPUTS/
├── cached_products/                              # Supplier product cache
│   └── poundwholesale-co-uk_products_cache.json
├── FBA_ANALYSIS/
│   ├── amazon_cache/                             # Individual Amazon product data
│   │   ├── amazon_B09W64GKR4_5050375010819.json
│   │   └── amazon_{ASIN}_{EAN_or_title}.json
│   ├── linking_maps/                             # EAN→ASIN mappings
│   │   └── poundwholesale.co.uk/                 # Note: dotted folder format
│   │       └── linking_map.json
│   └── financial_reports/                        # Profitability analysis
│       └── fba_financial_report_{timestamp}.csv
├── CACHE/
│   └── processing_states/                        # State management for resumability
│       └── poundwholesale-co-uk_processing_state.json
├── DIAGNOSTICS/                                  # System diagnostics
│   ├── save_telemetry.log
│   ├── sentinels.log
│   └── state_validation.json
└── logs/
    ├── debug/                                    # Detailed execution logs
    │   └── run_custom_poundwholesale_{timestamp}.log
    ├── health/                                   # System health monitoring
    └── application/                              # Application-level logs
```

### **⚙️ Configuration System**

**Hierarchical Configuration:**
- **system_config.json**: Global settings (processing limits, performance, browser config)
- **supplier_configs/*.json**: Supplier-specific settings and credentials
- **categories JSON files**: Predefined category URLs for each supplier

**Critical Configuration Sections:**
```json
{
  "system": {
    "max_products": 1000000,
    "max_products_per_category": 1000,
    "financial_report_batch_size": 50,
    "chrome_debug_port": 9222,
    "reuse_browser": true
  },
  "processing_limits": {
    "min_price_gbp": 0.01,
    "max_price_gbp": 20.0,
    "min_products_per_category": 1
  },
  "pipeline_toggles": {
    "separate_supplier_amazon_loops": true,
    "frozen_category_denominator": true,
    "resume_abs_index_math": true
  },
  "authentication": {
    "enabled": true,
    "consecutive_failure_threshold": 5
  }
}
```

**Financial Configuration (UK Marketplace):**
- Default FBA fee percentage: 15%
- UK VAT rate: 20%
- Target profit margin: 25%
- Currency: GBP

### **🌐 Browser Automation**

**Playwright Integration:**
- Chrome CDP (Chrome DevTools Protocol) with IPv6/IPv4 dual-stack
- Automatic browser health monitoring and restart
- Session persistence across browser restarts
- Connection timeout handling with automatic recovery

**Browser Management:**
- Time-based restart (every 2.5 hours)
- Memory-based restart (Python >3GB, Node.js >2GB)
- Zero downtime restart (~2.7 seconds)
- Authentication integration with restart system

### **🔄 State Management System**

**File-Grounded State Principles:**
- State calculated from persistent files, not memory variables
- Atomic operations using WindowsSaveGuardian
- Thread-safe operations with RLock
- Seven zero-risk progress tracking methods

**State Structure:**
```json
{
  "system_progression": {
    "current_phase": "supplier",                      // supplier | amazon_analysis
    "persistent_category_index": 0,                 // NEVER resets, tracks absolute position
    "supplier_products_needing_extraction": 47,      // RESET per category
    "supplier_products_completed": 0,                 // RESET per category
    "amazon_products_needing_analysis": 45,           // RESET per category
    "amazon_products_completed": 0                    // RESET per category
  }
}
```

**Resume Behavior:**
- Phase-aware resumption (direct routing to supplier or amazon_analysis)
- Monotonic pointer advancement (never goes backward)
- Structured resume pointer storage: {phase, cat_idx, prod_idx}
- Overflow safety with clamping (not reset)

## Development Notes

### **🪟 Windows Compatibility**
- Full Windows 10/11 support with native memory management
- Atomic file operations to prevent permission issues
- Windows Memory Manager with accurate process monitoring
- PowerShell and Command Prompt compatibility

### **⚡ Performance Optimizations**
- O(1) hash-based duplicate prevention (20-40% improvement)
- Smart memory clearing (99% reduction in operations)
- URL pre-filtering eliminates duplicate processing
- Configurable batch processing for different system capabilities

### **🧪 Testing Infrastructure**
- Comprehensive test suite with unit, integration, and E2E tests
- Performance benchmarking capabilities
- Security vulnerability scanning
- Type checking with mypy
- File-grounded state testing

### **📊 Monitoring and Debugging**
- Multi-level logging system (debug, health, application logs)
- Real-time performance monitoring
- Comprehensive error reporting with stack traces
- System diagnostics and validation tools
- Sentinel monitoring for divergence detection

### **🔐 Security Management**
- **🚨 CRITICAL API KEY PRESERVATION**: NEVER remove or modify existing API keys
- Session isolation and security for each supplier
- Encrypted credential storage where possible
- UTF-8 encoding enforcement at every file boundary
- Configuration validation and fallbacks

**Current Working API Keys (USE WHEN NEEDED):**
- OpenAI API Key: `sk-ZVcoRkU6brREgixWUDk7lTq_aBNRZwdh_PWwOZuJwKT3BlbkFJvOyKLWAM8OhjyHN0b8e66E1O2G7N2Ew_g3SngsDToA`
- GitHub Token: `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`

## Environment Variables

### **Required Variables**
```bash
# Browser Automation
CHROME_REMOTE_PORT=9222
PLAYWRIGHT_BROWSERS_PATH=/opt/playwright

# Output Management
OUTPUTS_BASE_PATH=./OUTPUTS
output_root=./OUTPUTS

# Supplier Configuration
SUPPLIER_SESSION_TIMEOUT=3600
AUTHENTICATION_RETRY_ATTEMPTS=3
SESSION_VALIDATION_INTERVAL=300

# Amazon API Configuration
AMAZON_REQUEST_DELAY_MS=1000
AMAZON_CACHE_TTL_HOURS=24
EAN_MATCHING_CONFIDENCE_THRESHOLD=0.85

# Financial Analysis (UK Marketplace)
DEFAULT_FBA_FEE_PERCENTAGE=15
VAT_RATE_UK=20
PROFIT_MARGIN_TARGET=25

# System Optimization
MAX_CONCURRENT_EXTRACTIONS=3
CACHE_RETENTION_DAYS=30
```

## Troubleshooting

### **🔧 Common Issues**

**Chrome Connection Issues:**
```bash
# Check Chrome v139+ IPv6/IPv4 connectivity
netstat -tuln | grep 9222
curl -6 http://localhost:9222/json/version  # IPv6
curl -4 http://localhost:9222/json/version  # IPv4

# Auto-recovery with dynamic endpoint detection
python utils/browser_manager.py --health-check --auto-restart --ipv6-first
```

**Authentication Failures:**
```bash
# Reset Chrome session and restart browser
pkill -f chrome && sleep 2
python utils/browser_manager.py --health-check --auto-restart

# Clear authentication cache
rm -rf OUTPUTS/CACHE/auth_sessions/*.json
python tools/supplier_authentication_service.py --reset-auth
```

**State Corruption Recovery:**
```bash
# Validate and rebuild state from files
python utils/fixed_enhanced_state_manager.py --validate-state --supplier=poundwholesale-co-uk
python utils/fixed_enhanced_state_manager.py --rebuild-from-cache --file-grounded
```

**Memory Issues:**
```bash
# Monitor and optimize memory usage
python -m memory_profiler run_custom_poundwholesale.py

# Manual memory optimization
python -c "from tools.passive_extraction_workflow_latest import PassiveExtractionWorkflow; workflow = PassiveExtractionWorkflow(); workflow.safe_memory_clear_with_file_fallback()"
```

## Multi-Agent Orchestration

### **🤖 Agent Communication Protocol**
For multi-step or feature development:
1. **START** with `tech-lead-orchestrator` for routing map
2. **WAIT** for structured agent sequence
3. **USE ONLY** listed agents in specified order
4. **MANAGE** all information handoff as main agent
5. **NEVER** improvise agent selection or skip orchestrator

### **🔄 Sub-Agent Deployment Strategy**
```
Main Claude (coordinator)
├── Authentication Specialist (login/session management)
├── Data Quality Reviewer (validation specialist)
├── Performance Monitor (resource optimization)
└── Error Recovery Agent (failure handling)
```

## Documentation References

**Complete Technical Documentation:**
- `docs/README.md` - Comprehensive technical documentation
- `config/system-config-toggle-v2.md` - System settings and toggles
- `docs/PULL_REQUEST_CHECKLIST.md` - Development and security standards
- `latest_workflow.md` - Detailed workflow behavior and sequence
- `AGENTS.md` - Multi-agent orchestration and deployment guide

**System Status**: ✅ Production Ready
**Chrome Compatibility**: ✅ v139+ with IPv6/IPv4 dual-stack
**Last Updated**: October 6, 2025
**Platform Support**: Windows 10/11, Linux, WSL2
**Python Compatibility**: 3.8+