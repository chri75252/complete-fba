# Processing States

**Location:** `OUTPUTS/CACHE/processing_states/`

## Overview

Processing state files track the progress of long-running extraction sessions. They enable the system to resume from where it left off after interruptions (browser crash, session timeout, manual stop).

---

## Directory Structure

```
OUTPUTS/CACHE/
└── processing_states/
    ├── poundwholesale_co_uk_processing_state.json
    ├── clearance_king_co_uk_processing_state.json
    ├── efghousewares_co_uk_processing_state.json
    └── {supplier}_processing_state.json
```

---

## File: `{supplier}_processing_state.json`

### Purpose
Persists session progress to enable resumption without reprocessing completed work.

### Schema

```json
{
  "schema_version": "1.2_THREAD_SAFE",
  "created_at": "2025-11-19T15:55:04.947693+00:00",
  "last_updated": "2026-03-25T05:44:09.933594+00:00",
  "supplier_name": "poundwholesale.co.uk",
  "total_products": 10828,
  "successful_products": 11362,
  "processing_status": "initialized",
  "is_fresh_start": false,
  "category_progress": "1/230",
  "error_log": [],
  "system_progression": {
    "current_phase": "amazon_analysis",
    "persistent_category_index": 231,
    "current_category_index": 1,
    "total_categories": 230,
    "category_freeze_timestamp": "2026-03-23T15:06:24.295547+00:00",
    "supplier_products_needing_extraction": 1,
    "supplier_products_completed": 0,
    "amazon_products_needing_analysis": 1,
    "amazon_products_completed": 1,
    "current_category_url": "https://www.poundwholesale.co.uk/toys/...",
    "frozen_category_denominators": {
      "https://supplier.co.uk/category1": 58,
      "https://supplier.co.uk/category2": 15
    }
  },
  "frozen_totals_committed": true
}
```

---

## Field Reference

### Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | string | Version for compatibility (current: `1.2_THREAD_SAFE`) |
| `created_at` | ISO 8601 | When state file was first created |
| `last_updated` | ISO 8601 | Last modification timestamp |
| `supplier_name` | string | Supplier domain (e.g., `poundwholesale.co.uk`) |
| `total_products` | integer | Total products found in supplier cache |
| `successful_products` | integer | Products successfully matched to Amazon |
| `processing_status` | string | Current status: `initialized`, `running`, `paused`, `completed` |
| `is_fresh_start` | boolean | Whether this is a fresh run vs resume |
| `category_progress` | string | Progress indicator: `"current/total"` (e.g., `"1/230"`) |
| `error_log` | array | List of errors encountered |
| `frozen_totals_committed` | boolean | Whether frozen category totals have been saved |

### system_progression

The `system_progression` object tracks the current position in the workflow:

| Field | Type | Description |
|-------|------|-------------|
| `current_phase` | string | Active phase: `supplier_extraction`, `amazon_analysis` |
| `persistent_category_index` | integer | **Key resume point** - next category to process |
| `current_category_index` | integer | Current position within category |
| `total_categories` | integer | Total number of categories in config |
| `category_freeze_timestamp` | ISO 8601 | When category totals were frozen |
| `supplier_products_needing_extraction` | integer | Products pending supplier extraction |
| `supplier_products_completed` | integer | Products extracted |
| `amazon_products_needing_analysis` | integer | Products pending Amazon matching |
| `amazon_products_completed` | integer | Products matched to Amazon |
| `current_category_url` | string | URL of currently processing category |
| `frozen_category_denominators` | object | Category → product count mapping (frozen at start) |

### frozen_category_denominators

Once frozen, this maps each category URL to its product count:

```json
{
  "https://supplier.co.uk/category1": 58,
  "https://supplier.co.uk/category2": 15,
  "https://supplier.co.uk/category3": 26
}
```

---

## Phase Workflow

```
┌─────────────────────────────────────────────────────┐
│ INITIALIZED → SUPPLIER_EXTRACTION → AMAZON_ANALYSIS │
└─────────────────────────────────────────────────────┘
```

### Phase: `initialized`
- State file created
- Categories loaded
- Ready to start

### Phase: `supplier_extraction`
- Scraping products from supplier categories
- Updates: `supplier_products_completed`
- Advances: `persistent_category_index`

### Phase: `amazon_analysis`
- Matching products to Amazon
- Updates: `amazon_products_completed`
- Creates entries in linking map

---

## Resumption Logic

The system resumes by reading `system_progression`:

```python
# Simplified resume logic
phase = state["system_progression"]["current_phase"]
cat_index = state["system_progression"]["persistent_category_index"]

if phase == "amazon_analysis":
    # Resume Amazon matching from current index
    start_from = cat_index
```

### Key Rules
1. **`persistent_category_index` never decreases** - only advances
2. **Frozen totals don't change** - product counts per category are locked at run start
3. **Atomic saves** - state is written using temp-file-then-replace

---

## Usage

### Read State
```python
import json
from pathlib import Path

state_path = Path("OUTPUTS/CACHE/processing_states/poundwholesale_co_uk_processing_state.json")
with open(state_path) as f:
    state = json.load(f)

print(f"Phase: {state['system_progression']['current_phase']}")
print(f"Progress: {state['category_progress']}")
print(f"Products: {state['total_products']}")
```

### Check if Resume Needed
```python
if state["is_fresh_start"]:
    print("Fresh start required")
elif state["processing_status"] in ["paused", "initialized"]:
    print("Can resume from index:", state["system_progression"]["persistent_category_index"])
```

### Manual Resume Point Adjustment
```python
# WARNING: Only for debugging/recovery
state["system_progression"]["persistent_category_index"] = 100
state["last_updated"] = datetime.now().isoformat()
# Save with atomic write...
```

---

## Related Files

| File | Location | Purpose |
|-------|----------|---------|
| Supplier Cache | `OUTPUTS/cached_products/{supplier}_products_cache.json` | Products extracted |
| Linking Map | `OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier}/linking_map.json` | Amazon matches |
| Windows Save Guardian | `utils/windows_save_guardian.py` | Atomic save logic |

---

## Manager Class

**Location:** `utils/fixed_enhanced_state_manager.py`

**Class:** `FixedEnhancedStateManager`

**Key Methods:**
- `initialize_workflow_session()` - Create new state
- `save_state_atomic()` - Save with atomic write
- `advance_category()` - Move to next category
- `set_phase()` - Update current phase
- `get_current_progress()` - Read progress metrics

---

## Backups

No automatic backups. The `WindowsSaveGuardian` may create temporary `.bak` files during saves.

---

## Common Issues

### State Reset to Zero
- Usually caused by incorrect state file write
- Check logs for save errors
- Verify `schema_version` hasn't been corrupted

### Index Mismatch
- If linking map has more entries than state expects
- May indicate manual edits or parallel processing
- Run `SentinelMonitor` to detect divergence

### Frozen Totals Inconsistent
- Category product counts don't match actual cache
- Run fresh start to recalculate

---

## Maintenance

To force fresh start:
```python
state["is_fresh_start"] = True
state["system_progression"]["persistent_category_index"] = 0
state["system_progression"]["current_phase"] = "initialized"
```

---

*Document Version: 1.0*
*Last Updated: 2026-04-11*
