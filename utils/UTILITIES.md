# Utilities

**Location:** `utils/`

## Overview

Utilities provide core infrastructure services: browser management, atomic file operations, state management, monitoring, and path resolution.

---

## Directory Structure

```
utils/
├── browser_manager.py               # Chrome CDP management
├── fixed_enhanced_state_manager.py # Resumable state
├── windows_save_guardian.py          # Atomic file operations
├── sentinel_monitor.py              # System monitoring
├── path_manager.py                  # Path resolution
├── logger.py                        # Logging configuration
├── browser_circuit_breaker.py       # Browser failure protection
├── url_cache_filter.py              # URL deduplication
├── supplier_config_loader.py         # Supplier config loading
├── url_aware_state_manager.py       # Alternative state manager
├── enhanced_state_manager.py         # Legacy state manager
├── data_store.py                   # Data persistence
├── file_organization_migrator.py   # File migration
├── windows_memory_manager.py        # Windows memory monitoring
├── wsl_memory_manager.py           # WSL memory monitoring
└── supplier_circuit_breaker.py     # Supplier failure protection
```

---

## Browser Manager

**Location:** `utils/browser_manager.py`

### Purpose
Manages Chrome browser lifecycle via CDP (Chrome DevTools Protocol).

### Key Features

| Feature | Description |
|---------|-------------|
| Singleton pattern | Single shared browser instance |
| LRU page cache | Caches 1 page for reuse |
| Health monitoring | Auto-restart on degradation |
| IPv6/IPv4 dual-stack | Supports Chrome v139+ |

### Usage

```python
from utils.browser_manager import BrowserManager

browser_mgr = BrowserManager()

# Get browser instance
browser = await browser_mgr.get_browser()

# Get page for URL (with caching)
page = await browser_mgr.get_page_for_url("https://example.com")

# Health check
is_healthy = browser_mgr.is_healthy()

# Graceful restart
await browser_mgr.restart_browser_gracefully()
```

### CDP Connection
```python
browser = await chromium.connect_over_cdp(
    f"http://[::1]:{port}/devtools/browser/{browser_id}"
)
```

### Health Thresholds
- Memory threshold: 2048 MB
- Restart interval: 2.5 hours
- Max pages: 1 (LRU cache)

---

## Windows Save Guardian

**Location:** `utils/windows_save_guardian.py`

### Purpose
Provides atomic file operations for Windows.

### Strategies

| Strategy | Priority | Description |
|----------|----------|-------------|
| Temp file + replace | 1 | Write to .tmp, then rename |
| Backup + replace | 2 | Backup existing, write new, cleanup |
| Retry with backoff | 3 | Retry on lock conflicts |
| Alt temp dir | 4 | Use different temp directory |
| Direct write | 5 | Last resort (not atomic) |

### Usage

```python
from utils.windows_save_guardian import WindowsSaveGuardian

guardian = WindowsSaveGuardian()

# Atomic save
guardian.save_json(data, "output.json")

# Atomic save with custom strategy
guardian.save_json(
    data, 
    "output.json",
    strategy="backup_then_replace"
)
```

### Telemetry

Logs save attempts for diagnostics:
```python
guardian.log_telemetry(
    operation="save_json",
    file="output.json",
    success=True,
    strategy="temp_replace",
    duration_ms=45
)
```

---

## Fixed Enhanced State Manager

**Location:** `utils/fixed_enhanced_state_manager.py`

### Purpose
Manages resumable processing state for long-running sessions.

### Key Principles

| Principle | Description |
|-----------|-------------|
| Monotonic indices | Never decrease progress |
| Frozen totals | Category counts locked at start |
| Atomic saves | No partial writes |
| Session tracking | UUID per writer session |

### Usage

```python
from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager

state_mgr = FixedEnhancedStateManager(
    supplier_name="poundwholesale.co.uk"
)

# Initialize or resume
if state_mgr.should_resume():
    state_mgr.resume()
else:
    state_mgr.initialize()

# Update progress
state_mgr.set_phase("supplier_extraction")
state_mgr.advance_category()

# Save atomically
state_mgr.save_state_atomic()
```

### State Schema
```python
{
    "schema_version": "1.2_THREAD_SAFE",
    "supplier_name": "poundwholesale.co.uk",
    "system_progression": {
        "current_phase": "amazon_analysis",
        "persistent_category_index": 231,
        "total_categories": 230
    }
}
```

---

## Sentinel Monitor

**Location:** `utils/sentinel_monitor.py`

### Purpose
Monitors system health and detects divergence.

### Checks

| Check | Description |
|-------|-------------|
| Cache divergence | Cached count vs linking map |
| State consistency | Processing state vs files |
| Anomaly detection | Unusual patterns |

### Usage

```python
from utils.sentinel_monitor import SentinelMonitor

monitor = SentinelMonitor()

# Check for divergence
divergence = await monitor.check_linking_map_vs_cache()

if divergence:
    monitor.log_divergence(
        supplier="poundwholesale.co.uk",
        cache_count=1000,
        linking_count=950
    )
```

### Alerting
- Logs divergence to `OUTPUTS/DIAGNOSTICS/sentinels.log`
- Triggers on significant mismatches

---

## Path Manager

**Location:** `utils/path_manager.py`

### Purpose
Centralized path resolution for all system paths.

### Usage

```python
from utils.path_manager import PathManager, path_manager

# Get paths
linking_map = path_manager.get_linking_map_path("poundwholesale.co.uk")
cache = path_manager.get_supplier_cache_path("poundwholesale.co.uk")
state = path_manager.get_processing_state_path("poundwholesale.co.uk")
```

### Path Types

| Path Type | Method |
|-----------|--------|
| Linking map | `get_linking_map_path(supplier)` |
| Supplier cache | `get_supplier_cache_path(supplier)` |
| Processing state | `get_processing_state_path(supplier)` |
| Amazon cache | `get_amazon_cache_path()` |
| Financial reports | `get_financial_reports_path(supplier)` |

---

## Browser Circuit Breaker

**Location:** `utils/browser_circuit_breaker.py`

### Purpose
Prevents cascading failures from browser issues.

### States

| State | Behavior |
|-------|---------|
| CLOSED | Normal operation |
| OPEN | Fail fast, no requests |
| HALF_OPEN | Allow test request |

### Usage

```python
from utils.browser_circuit_breaker import BrowserCircuitBreaker

cb = BrowserCircuitBreaker(
    failure_threshold=5,
    timeout_seconds=30
)

if cb.can_execute():
    try:
        result = await browser_request()
        cb.record_success()
    except Exception:
        cb.record_failure()
else:
    raise CircuitOpenException()
```

---

## Logger

**Location:** `utils/logger.py`

### Purpose
Centralized logging configuration.

### Usage

```python
from utils.logger import setup_logger

logger = setup_logger(
    name="poundwholesale",
    supplier_name="poundwholesale.co.uk"
)

logger.info("Processing category", extra={"category": "toys"})
logger.warning("Fallback to title search", extra={"ean": "..."})
logger.error("Extraction failed", exc_info=True)
```

### Log Files

| Log Type | Location |
|----------|----------|
| Debug | `logs/debug/run_custom_{supplier}_{timestamp}.log` |
| Application | `logs/application/` |
| API calls | `logs/api_calls/` |

---

## URL Cache Filter

**Location:** `utils/url_cache_filter.py`

### Purpose
Deduplicates URLs to avoid redundant processing.

### Usage

```python
from utils.url_cache_filter import URLCacheFilter

filter = URLCacheFilter()

# Check if URL should be processed
if not filter.is_duplicate(url):
    await process_url(url)
    filter.mark_processed(url)
```

---

## Supplier Config Loader

**Location:** `utils/supplier_config_loader.py`

### Purpose
Loads supplier-specific configurations.

### Usage

```python
from utils.supplier_config_loader import SupplierConfigLoader

loader = SupplierConfigLoader()
config = loader.load_config("poundwholesale.co.uk")

selectors = config["selectors"]
base_url = config["base_url"]
```

---

## Memory Managers

### Windows Memory Manager
**Location:** `utils/windows_memory_manager.py`

Monitors real Chrome process memory (not WSL estimates).

### WSL Memory Manager
**Location:** `utils/wsl_memory_manager.py`

Monitors vmmem process memory for WSL setups.

---

## Summary Table

| Utility | Purpose | Key Class/Function |
|---------|---------|-------------------|
| Browser Manager | Chrome lifecycle | `BrowserManager` |
| Save Guardian | Atomic files | `WindowsSaveGuardian` |
| State Manager | Resumable state | `FixedEnhancedStateManager` |
| Sentinel Monitor | Health checks | `SentinelMonitor` |
| Path Manager | Path resolution | `PathManager` |
| Circuit Breaker | Failure protection | `BrowserCircuitBreaker` |
| Logger | Logging | `setup_logger` |
| URL Filter | Deduplication | `URLCacheFilter` |

---

*Document Version: 1.0*
*Last Updated: 2026-04-11*
