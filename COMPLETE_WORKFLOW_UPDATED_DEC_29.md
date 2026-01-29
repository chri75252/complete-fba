# Amazon FBA Agent System - Master Behavior Specification

**Document Type**: Complete System Behavior Guide
**Version**: v4.0 (December 2025 Update)
**Date**: December 29, 2025
**Status**: Production Ready - Master Reference (Updated)
**Purpose**: Definitive guide for system behavior, processing flow, data management, and operational guarantees.

**🚨 DECEMBER 2025 UPDATE**: This document has been comprehensively updated to reflect the current production codebase. Key changes since August 2025 include the finalized `FixedEnhancedStateManager`, the "Freeze-Mark-Resume" architecture, `persistent_category_index` as the primary resume pointer, and consolidated phase management.

---

## 🎯 **EXECUTIVE SUMMARY**

The Amazon FBA Agent System v4.0 is a production-ready automation platform that processes supplier websites to identify profitable Amazon FBA opportunities.

**🚨 CRITICAL ARCHITECTURE NOTE**: The system contains **TWO DISTINCT WORKFLOWS** in `passive_extraction_workflow_latest.py`:

1. **🔄 Hybrid Processing Mode** (Primary/Recommended): `_run_hybrid_processing_mode()`
   - Completes both supplier extraction AND Amazon analysis for one category before proceeding to the next.
   - Supports chunked, sequential, and balanced processing sub-modes.
   - **This specification primarily documents the HYBRID mode workflow.**
   - **Controlled by:** `config.hybrid_processing.enabled == true`

2. **📋 Regular/Legacy Workflow Mode**: Standard sequential processing
   - Extracts ALL supplier products first, then analyzes ALL products.
   - Older implementation maintained for compatibility.
   - **❌ Not covered by this specification.**

**⚠️ IMPORTANT**: When testing, implementing, or debugging, ensure you are working with the **HYBRID PROCESSING MODE** by verifying `hybrid_processing.enabled = true` in `system_config.json`.

**Core Architectural Pillars**:
- **Freeze-Mark-Resume**: A deterministic, crash-safe resumption protocol. State is frozen at discovery, marked after each successful write, and resumed without data loss or duplication.
- **Single Source of Truth**: `system_progression` (within `processing_state.json`) is the exclusive owner of resume-critical pointers. `linking_map.json` is the exclusive owner of historical/completion data.
- **O(1) Hash-Based Filtering**: All skip decisions (Linking Map check, Cache check) use in-memory hash sets for constant-time lookups.
- **Atomic Persistence**: All critical file I/O is protected by `WindowsSaveGuardian` (Write -> Flush -> Rename) to prevent data corruption.

---

## 📊 **IMPLEMENTATION STATUS & ANALYSIS SUMMARY**

### **🔄 DUAL WORKFLOW ARCHITECTURE**

| Mode | Entry Method | `system_config.json` | Processing Pattern | Covered Here? |
|---|---|---|---|---|
| **Hybrid** (Primary) | `_run_hybrid_processing_mode()` | `hybrid_processing.enabled = true` | Category-by-category (Supplier→Amazon→Next) | ✅ **YES** |
| **Legacy** | Standard methods | `hybrid_processing.enabled = false` | All Supplier, then All Amazon | ❌ No |

**🚨 TESTING & IMPLEMENTATION NOTE**:
- When testing resumption, manifests, filtering, or any feature described in this document:
- **ALWAYS ensure `hybrid_processing.enabled = true`** in your system configuration.
- **ALWAYS verify you're working with `_run_hybrid_processing_mode()`**.

---

### **✅ VERIFIED CORRECT IMPLEMENTATIONS (December 2025)**

| Component | Status | Details & Location |
|-----------|--------|------------|
| **State Manager** | ✅ **STABLE** | `utils/fixed_enhanced_state_manager.py`. `FixedEnhancedStateManager` is the canonical class. Uses `system_progression` as the single source of truth for resumption. |
| **Freeze-Mark-Resume** | ✅ **IMPLEMENTED** | Category denominators are frozen on first discovery (`category_denominator_frozen`). Product index is "marked" immediately after each LM write. Resume reads from frozen state. |
| **Atomic Persistence** | ✅ **WORKING** | `WindowsSaveGuardian` used for `processing_state.json`, `linking_map.json`, manifests, and caches. |
| **Hash Optimization** | ✅ **WORKING** | O(1) lookups via `HashLookupOptimizer` and in-memory sets (`lm_url_set`, `cache_url_set`). Rebuild triggers after every LM write. |
| **Filter Order** | ✅ **CORRECT** | LM → Cache → Extract sequence implemented in `utils/url_filter.py`. |
| **Filter Transparency Logging** | ✅ **IMPLEMENTED** | Enhanced format: `🧮 Filter Invariant: in=N == skip+amz_only+full=N`. |
| **Dashboard** | ✅ **WORKING** | `dashboard/app_fixed.py` (Streamlit). Reads from `processing_state.json`, `linking_map.json`, and financial reports. |

---

### **🟡 AREAS WITH KNOWN CONSIDERATIONS**

| Component | Status | Notes |
|-----------|--------|-------|
| **Resumption Logic Consistency** | 🟡 **95%** | Primary resume path (`_run_hybrid_processing_mode`) uses `system_progression.persistent_category_index`. Some legacy helper functions may still reference older fields; these are being deprecated. |
| **Financial Report Triggering** | 🟡 **PARTIAL** | Logic exists but threshold monitoring (`financial_report_batch_size`) is not consistently called in all sub-modes of hybrid processing. Manual report generation is always available. |
| **Manifest Generation Point** | 🟡 **PARTIAL** | Manifests are generated by the scraper but the call sequence (`_generate_and_save_manifest -> filter`) is not explicitly enforced in all code paths. |

---

### **📋 KEY STATE FILE FIELDS (December 2025)**

The `processing_state.json` file (located at `OUTPUTS/CACHE/processing_states/{supplier}_processing_state.json`) is the authoritative resume state. The key fields are nested under `system_progression`:

```json
{
  "schema_version": "1.2_THREAD_SAFE",
  "supplier_name": "poundwholesale_co_uk",
  "is_fresh_start": false,
  "system_progression": {
    "current_phase": "amazon_analysis",          // "supplier" or "amazon_analysis"
    "persistent_category_index": 5,              // 1-BASED! The current/resume category index.
    "current_category_url": "https://...",       // The URL of the category being processed.
    "total_categories": 119,                     // Frozen total, set at startup.
    "category_denominator_frozen": true,         // Once true, total_products_in_category never changes.
    "supplier_products_needing_extraction": 60,  // How many URLs were discovered for this category.
    "supplier_products_completed": 60,           // How many have been scraped (supplier phase).
    "amazon_products_needing_analysis": 13,      // Size of the Amazon queue for this category.
    "amazon_products_completed": 8               // How many have been analyzed (amazon phase).
  },
  "gap_processing": {
    "startup_analysis_completed": true,
    "reverse_gap_detected": false
  }
}
```

**⚠️ CRITICAL POINTER: `persistent_category_index`**
- This is the **1-based** index of the current category.
- It is the **ONLY** field used to determine which category to start/resume from.
- `current_category_index` (0-based) is a legacy mirror field and should NOT be used for new logic.

---

## 🏗️ **SYSTEM ARCHITECTURE OVERVIEW**

### **Processing Philosophy**
- **Deterministic Resumption**: The system resumes from interruptions with 100% accuracy using the `system_progression` object. There are no heuristics.
- **Stable Denominators (Write-Once)**: Product counts for progress calculation are frozen at discovery and are immune to later changes. This ensures stable user-facing metrics.
- **Freeze-Mark-Resume**: A three-stage state machine ensures data integrity. State is frozen before work begins, marked after each atomic write, and resumed from the mark.
- **Atomic Persistence**: All critical data files are written atomically via Windows Save Guardian (WSG).
- **Transparent Observability**: Key operational metrics are logged to provide immediate insight into system health.

### **Data Flow Architecture**
```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         MASTER DATA FLOW ARCHITECTURE (v4.0)                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  🚀 LAUNCHER (run_custom_{supplier}.py)                                         │
│  └── Initializes BrowserManager (Port 9222) → Triggers PassiveExtractionWorkflow│
│                         │                                                       │
│                         ▼                                                       │
│  ⚙️ WORKFLOW ENGINE (PassiveExtractionWorkflow)                                 │
│  └── Loads Config → Loads/Creates State → Enters _run_hybrid_processing_mode() │
│                         │                                                       │
│                         ▼                                                       │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │ FOR EACH CATEGORY (from persistent_category_index to total_categories):  │  │
│  ├───────────────────────────────────────────────────────────────────────────┤  │
│  │                                                                           │  │
│  │  1️⃣ PHASE: CATEGORY INIT (FREEZE)                                        │  │
│  │  ├── Load Category URL from Manifest                                     │  │
│  │  ├── Scrape all Product URLs from Category Pages                         │  │
│  │  ├── 🔒 FREEZE Denominator: total_products_in_category = N               │  │
│  │  └── Save State (Atomic)                                                  │  │
│  │                         │                                                 │  │
│  │                         ▼                                                 │  │
│  │  2️⃣ PHASE: INTELLIGENT FILTERING (O(1) Hash Lookups)                     │  │
│  │  ├── 🔗 Linking Map Check → skip_entirely[] (Products with LM entry)      │  │
│  │  ├── 💾 Product Cache Check → needs_amazon_only[] (Has supplier data)     │  │
│  │  ├──❓ Remaining → needs_full_extraction[] (New products)                │  │
│  │  └── 🧮 Log Invariant: in == skip + amazon_only + full                    │  │
│  │                         │                                                 │  │
│  │                         ▼                                                 │  │
│  │  3️⃣ PHASE: SUPPLIER EXTRACTION (current_phase = "supplier")              │  │
│  │  ├── For each URL in needs_full_extraction[]:                             │  │
│  │  │   ├── Navigate → Parse (Title, Price, EAN, Imgs)                      │  │
│  │  │   ├── Add to Product Cache → Save Cache (Batched, Atomic)              │  │
│  │  │   └── Increment supplier_products_completed → Save State (Atomic)      │  │
│  │  └── Log: "SUPPLIER DONE: newly_extracted=R"                              │  │
│  │                         │                                                 │  │
│  │                         ▼                                                 │  │
│  │  4️⃣ PHASE: AMAZON ANALYSIS (current_phase = "amazon_analysis")           │  │
│  │  ├── Build amazon_queue = needs_amazon_only + newly_extracted             │  │
│  │  ├── For each URL in amazon_queue:                                        │  │
│  │  │   ├── 🔎 Lookup: EAN Search (High Conf) || Title Search (Med Conf)    │  │
│  │  │   ├── Harvest: ASIN, Price, BSR, Seller Count, Fees                   │  │
│  │  │   ├── 💰 Calculate Financials (ROI, Net Profit)                       │  │
│  │  │   ├── 🔗 MARK: Upsert Linking Map Entry → Save LM (Atomic)             │  │
│  │  │   ├── 🔥 Rebuild Hash Indexes (lm_url_set, etc.)                       │  │
│  │  │   └── Increment amazon_products_completed → Save State (Atomic)        │  │
│  │  └── Log: "AMAZON DONE: analyzed=T"                                       │  │
│  │                         │                                                 │  │
│  │                         ▼                                                 │  │
│  │  5️⃣ PHASE: CATEGORY COMPLETE                                             │  │
│  │  ├── Log: "✅ CATEGORY COMPLETE[C{idx}]"                                  │  │
│  │  ├── Increment persistent_category_index                                  │  │
│  │  ├── Reset phase to "supplier", reset product indices to 0                │  │
│  │  └── Save State (Atomic) → Loop to next category                          │  │
│  │                                                                           │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                         │                                                       │
│                         ▼                                                       │
│  📊 FINALIZATION                                                                │
│  ├── Generate Final Financial Report (if enabled)                              │
│  └── Log: "🏁 WORKFLOW COMPLETE"                                               │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 **DETAILED PROCESSING WORKFLOW**

**🚨 WORKFLOW MODE CLARIFICATION**: This detailed workflow describes the **HYBRID PROCESSING MODE** implementation (`_run_hybrid_processing_mode()`) which is the primary and recommended workflow.

**Configuration Requirement**: Ensure `hybrid_processing.enabled = true` in `system_config.json` for this workflow to be active.

---

### **PHASE 1: STARTUP & INITIALIZATION**

#### **Step 1.1 — State Manager Initialization**
```
INPUT: supplier_name (from run_custom_*.py)
ACTION: Instantiate FixedEnhancedStateManager, load state from disk.
OUTPUT: Populated self.state_data, is_fresh_start flag set.
```
**Entry Point**: `EnhancedStateManager.initialize_workflow_session()`
This method is the single authoritative entry for starting or resuming a workflow. It:
1.  Calls `load_state()` which reads the JSON from disk and sets `is_fresh_start = True` if file is missing, `False` otherwise.
2.  Calls `perform_startup_analysis()` which reconciles counters and sets the `session_resume_cursor`.

**Code Path (`utils/fixed_enhanced_state_manager.py`, Lines 247-283)**:
```python
def initialize_workflow_session(self) -> int:
    log.info("⚡ INITIALIZING WORKFLOW SESSION...")
    self.state_data["startup_completed"] = False
    self.load_state()
    log.info("📁 State loaded from disk.")
    self.perform_startup_analysis()
    log.info("🧪 Startup analysis complete.")

    sp = self.state_data.get("system_progression", {})
    start_category_index = int(sp.get("persistent_category_index", 1) or 1)
    current_phase = sp.get("current_phase", "supplier")

    log.info(f"🚀 AUTHORITATIVE START POSITION: Category {start_category_index} in phase '{current_phase}'")
    return start_category_index
```

**Fresh Start State Seeding**:
If no state file exists, default values are set:
```json
{
  "system_progression": {
    "persistent_category_index": 1,
    "current_phase": "supplier",
    "total_categories": 0, // Will be set by config loader
    "supplier_products_completed": 0,
    "amazon_products_completed": 0
  }
}
```

---

#### **Step 1.2 — Category Manifest Loading**
```
INPUT: Category list from config/poundwholesale_categories.json or .txt
ACTION: Load list, set total_categories in state.
OUTPUT: Ordered list of category URLs, frozen denominator.
```
The manifest of category URLs is loaded from a pre-defined configuration file. This list is the **frozen authority** for which categories exist. The system does NOT dynamically discover categories on every run; it trusts the manifest.

**Log**:
```
🚀 STARTUP: total_categories=119, resume_index=5, phase=amazon_analysis, url=<...>
```

---

#### **Step 1.3 — Perform Startup Analysis (Reconciliation)**
**Purpose**: To ensure counters in `processing_state.json` are consistent with the ground truth stored in `linking_map.json`. This handles the "Reverse Gap" scenario where the state file was reset but the linking map retained data.

**Code Path (`utils/fixed_enhanced_state_manager.py`, Lines 469-645)**:
```python
def perform_startup_analysis(self) -> Dict[str, Any]:
    # ...
    file_grounded_data = self._calculate_file_grounded_totals()
    linking_map_count = file_grounded_data.get("linking_map_count", 0)

    # Reconcile counters to linking_map as source of truth
    self.state_data["successful_products"] = linking_map_count
    # ...
```
**Key Invariant**: After `perform_startup_analysis()`, `successful_products` and other aggregate counters **MUST** match the count of entries in `linking_map.json`. If they don't, the linking map count wins.

---

### **PHASE 2: INTELLIGENT URL FILTERING (Per Category)**

Before processing any URLs, the system must determine which have already been handled. This is a strict 3-stage filter.

#### **Step 2.1 — Primary Skip: Linking Map Check (O(1))**
```
INPUT: product_urls[] (from category page scrape)
ACTION: Build normalized hash set of linking_map supplier URLs; compare.
OUTPUT: skip_entirely[] (URLs already in LM), remaining[]
```
**Rule**: The "already processed" decision uses **ONLY** the `linking_map.json`. It does **NOT** consult `processing_state.json` counters.

**Code Path (`utils/url_filter.py`)**:
```python
lm_url_set = { normalize_url(e.get("supplier_url","")) for e in linking_map if e.get("supplier_url") }
skip_entirely = [url for url in product_urls if normalize_url(url) in lm_url_set]
remaining = [url for url in product_urls if normalize_url(url) not in lm_url_set]
```
**Log**: `🔗 Linking-map check: <N> complete (skipped)`

---

#### **Step 2.2 — Secondary Split: Product Cache Check (O(1))**
```
INPUT: remaining[] from Step 2.1
ACTION: Build normalized hash set of cached product URLs; compare.
OUTPUT: needs_amazon_only[] (have supplier data), needs_full_extraction[] (new)
```
**Code Path (`utils/url_filter.py`)**:
```python
cache_url_set = { normalize_url(p.get("url","")) for p in cached_products if p.get("url") }
needs_amazon_only = [url for url in remaining if normalize_url(url) in cache_url_set]
needs_full_extraction = [url for url in remaining if normalize_url(url) not in cache_url_set]
```
**Log**: `💾 Product-cache check: <N> have supplier data; <M> need supplier extraction`

---

#### **Step 2.3 — Filter Invariant Validation**
A critical invariant is logged to make routing bugs immediately visible.
```
🧮 Filter Invariant: in=<N> == skip+amz_only+full=<Total>
```
If the equality fails, an **ERROR** level log is emitted. The process does not halt, but this indicates a bug in the filtering logic.

---

### **PHASE 3: SUPPLIER DATA EXTRACTION**

This phase only runs for URLs in `needs_full_extraction[]`.

#### **Step 3.1 — Browser Extraction & Cache Persistence**
```
INPUT: needs_full_extraction[]
ACTION: Navigate → parse → validate → persist. Per-product state updates.
OUTPUT: Updated cached_products file; progress persisted atomically.
```
**Extraction targets**: Title, price (wholesale), EAN/Barcode, images, description, brand.

**State Update (Per Product)**:
After each successful extraction, `supplier_products_completed` is incremented.
```python
self.state_manager.update_progression_unified(
    supplier_products_completed=current_count + 1
)
self.state_manager.save_state_atomic()
```
**Cache Save Frequency**: To prevent data loss, the product cache is saved atomically at a configurable frequency (e.g., every 5 products), controlled by `system_config.supplier_cache_control.update_frequency_products`.

**Log**: `📦 EXTRACTED: <product_title> | EAN=<ean> | Price=£<price>`

---

#### **Step 3.2 — Post-Extraction Summary**
A summary log confirms the work done.
```
SUPPLIER DONE[C{idx} <slug>]: newly_extracted=15, cache_total=1200
```

---

### **PHASE 4: AMAZON ANALYSIS QUEUE COMPILATION**

#### **Step 4.1 — Build the Amazon Queue**
```
INPUT:
  - needs_amazon_only[]           # From Step 2.2
  - newly_extracted_success_urls  # From Step 3.1
ACTION: Combine, normalize, and sort for deterministic order.
OUTPUT: amazon_queue[] for Phase 5
```
**Why a separate dispatcher**: This strict separation prevents items that only need Amazon analysis from ever entering the supplier extraction loop.

**State Transition**:
```python
self.state_manager.update_progression_unified(
    current_phase="amazon_analysis",
    amazon_products_needing_analysis=len(amazon_queue),
    amazon_products_completed=0
)
```
**Log**: `➡️ AMAZON QUEUE[C{idx}]: total=25, from_cache=12, newly_extracted=13`

---

### **PHASE 5: AMAZON PRODUCT ANALYSIS (Queue-Driven)**

This phase iterates through the `amazon_queue`, performing lookups and financial calculations.

#### **Step 5.1 — EAN-First, Title-Fallback Lookup**
The system attempts to find the product on Amazon.
1.  **EAN Search (Preferred)**: Query Amazon by the supplier-provided EAN. High confidence.
2.  **Title Fallback**: If EAN fails, query by cleaned product title. Uses `difflib.SequenceMatcher` for title similarity scoring; requires > 30-50% match to accept. Medium/Low confidence.

**Log**:
```
🔎 AMAZON LOOKUP (EAN): 5033849048631 → ASIN=B07D3GVZZL (conf=high)
🔎 AMAZON LOOKUP (TITLE): "tiara necklace beauty set" → ASIN=B0... (conf=medium)
❌ AMAZON NO-MATCH: url=<...>, reason="Title similarity below threshold (0.22)"
```

---

#### **Step 5.2 — Data Harvest & Financial Calculation**
Once an ASIN is resolved, data is extracted: Amazon Price, Referral Fee, FBA Fee, BSR (from Keepa extension), Seller Count.

**Financial Calculation (`FBA_Financial_calculator.py`)**:
```
Net Profit = (Amazon Price - VAT) - Referral Fee - FBA Fee - Supplier Cost
ROI = (Net Profit / Supplier Cost) * 100
```

---

#### **Step 5.3 — Linking Map Entry Creation (The "Mark")**
A canonical entry is created or updated in `linking_map.json`. This is the **MARK** step of the Freeze-Mark-Resume protocol.
**Merge Policy (Upsert)**: The `supplier_url` (normalized) is the primary key. If an entry exists, it is updated; new entries are appended. This prevents duplicates.

**Code Path**:
```python
self._add_or_update_linking_map_entry(entry)
WindowsSaveGuardian.save_json_atomic(self.linking_map_path, self.linking_map)
```

**Log**: `🔗 LM UPSERT: url=<...>, asin=B07D..., method=ean, conf=high (new)`

---

#### **Step 5.4 — Hash Index Rebuild & Progress Update**
After every Linking Map save, the in-memory hash sets are rebuilt. This ensures the skip logic in Phase 2 always has current data.
```
🔥 HASH INDEX BUILT: 8619 EANs, 8879 URLs, 5945 ASINs in 0.21s
```
The state is then updated:
```python
self.state_manager.update_progression_unified(
    amazon_products_completed=current_count + 1
)
self.state_manager.save_state_atomic()
```

---

### **PHASE 6: CATEGORY COMPLETION & TRANSITION**

#### **Step 6.1 — Completion Criteria**
A category is complete when:
- Supplier phase work is done (`supplier_products_completed >= supplier_products_needing_extraction`).
- Amazon phase work is done (`amazon_products_completed >= amazon_products_needing_analysis`).

**Log**: `✅ CATEGORY COMPLETE[C{idx}]: <category_slug>`

---

#### **Step 6.2 — Transition to Next Category**
The state is advanced. This is also atomic.
```python
self.state_manager.update_progression_unified(
    persistent_category_index=current_idx + 1,          # Advance to next category (1-based)
    current_phase="supplier",                           # Reset phase
    supplier_products_completed=0,                      # Reset supplier counter
    amazon_products_completed=0,                        # Reset amazon counter
    current_category_url=get_next_url(current_idx + 1)  # Set next URL
)
self.state_manager.save_state_atomic()
```
**Log**: `➡️ NEXT CATEGORY: index={idx+1}/{total} url=<next_url or END>`

---

## 🔄 **SYSTEM RESUMPTION MECHANISM**

The system is designed for 100% deterministic resumption with no data loss or duplication.

### **Resume Decision Matrix**
| Condition | Action |
|---|---|
| State file is missing or unreadable. | **Fresh Start**. `is_fresh_start = True`. |
| State file exists and is valid. | **Resume**. `is_fresh_start = False`. |
| `force_fresh_start = true` in config. | **Fresh Start** (Override). |

### **Resume Logic**
The `initialize_workflow_session()` method handles all resumption logic. It returns the `persistent_category_index` which the main workflow loop uses as its starting point.

**Phase-Aware Resume**:
- **If `current_phase == "supplier"`**: The loop will enter the supplier extraction phase for the `persistent_category_index` category, starting from `supplier_products_completed`.
- **If `current_phase == "amazon_analysis"`**: The loop will rebuild the `amazon_queue` for that category and seek to `amazon_products_completed` to continue work.

### **The "Reverse Gap" Protocol**
**Scenario**: User accidentally deletes `processing_state.json` but keeps `linking_map.json`.
**Detection**: `perform_startup_analysis()` counts `linking_map` entries. If this count is greater than the state's counters, a "reverse gap" is detected.
**Action**: The state counters are reconciled to match the linking map. **Data is never lost.**
```
⚠️ REVERSE GAP DETECTED: LM count (1500) > state.successful_products (0). Aligning state to LM.
```

---

## 📊 **PROGRESS TRACKING & DASHBOARD**

### **Dashboard (`dashboard/app_fixed.py`)**
The Streamlit dashboard provides real-time visibility into the system.
*   **Launch**: `streamlit run dashboard/app_fixed.py`

**Key Panels & Data Sources**:
| Panel | Data Source Field |
|---|---|
| **System Progression** (Phase, Category X/Y) | `processing_state.json` → `system_progression.persistent_category_index`, `total_categories`, `current_phase` |
| **Category Progress** (Supplier X/Y, Amazon X/Y) | `processing_state.json` → `system_progression.supplier_products_completed`, `amazon_products_completed` |
| **Total Matches** | `linking_map.json` → `len(entries)` |
| **Financial Performance** | `OUTPUTS/FBA_ANALYSIS/financial_reports/*.csv` |

### **Progress Calculation (Derived on Demand)**
Progress percentages are always calculated on-demand from the canonical state and frozen denominators. They are NOT stored, which prevents state drift.
```python
overall_pct = sp["persistent_category_index"] / sp["total_categories"]
category_pct = sp["amazon_products_completed"] / max(1, sp["amazon_products_needing_analysis"])
```

---

## 🔧 **DATA MANAGEMENT & PERSISTENCE**

### **Windows Save Guardian (WSG) Usage**
All critical saves use **WSG** with an **anti-truncation guard**. The pattern is: Write to a temporary file (`*.tmp`) → `os.fsync()` → Atomic rename to target.

**Files Protected by WSG**:
- `OUTPUTS/CACHE/processing_states/{supplier}_processing_state.json`
- `OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier}/linking_map.json`
- `OUTPUTS/CACHE/manifests/{supplier}_{category_slug}.json`
- `OUTPUTS/cached_products/{supplier}_products_cache.json`

### **Save Cadence (Discipline)**
State is saved immediately after:
- Every `update_progression_unified(...)` call where a counter changes.
- After each `linking_map.json` write (upsert).
- After each batch of supplier cache writes.
- At category completion before transitioning.

---

## 🧩 **SYSTEM CONFIGURATION (`config/system_config.json`)**

This is the "God Config" for the system.

```json
{
  "hybrid_processing": {
    "enabled": true,
    "chunk_size_categories": 1
  },
  "processing_limits": {
    "min_price_gbp": 0.5,
    "max_price_gbp": 25.0,
    "max_products_per_category": 2000
  },
  "supplier_cache_control": {
    "update_frequency_products": 5
  },
  "financial_configuration": {
    "financial_report_batch_size": 50
  },
  "performance": {
    "timeouts": {
      "page_load_timeout_ms": 30000,
      "navigation_timeout_ms": 45000
    }
  }
}
```

---

## 🔐 **CROSS-PHASE GUARANTEES & RULES (Do-Not-Do List)**

*   ❌ **Do not** compute "already processed" from `processing_state.json` counters. Use `linking_map.json` only.
*   ❌ **Do not** re-seed or mutate the `supplier_products_needing_extraction` denominator after the category's first discovery pass.
*   ❌ **Do not** infer resume points from completion flags or file scans. Use `system_progression.persistent_category_index` only.
*   ❌ **Do not** intermingle Amazon-only items in the supplier extraction loop.
*   ❌ **Do not** write state files using standard `open(f, 'w')`. Always use `WindowsSaveGuardian`.

---

## 🧪 **VALIDATION & TESTING**

### **Critical Test Cases**

1.  **Resumption Accuracy**:
    - [ ] Stop the system mid-category. Restart. Verify it resumes from the exact product index, not the start of the category.
    - [ ] Stop the system mid-amazon phase. Restart. Verify it rebuilds the correct `amazon_queue` and seeks to the correct product.
2.  **Reverse Gap Handling**:
    - [ ] Delete `processing_state.json`. Keep `linking_map.json`. Restart. Verify linking map data is NOT re-processed.
3.  **Filter Invariant**:
    - [ ] Check logs for `🧮 Filter Invariant`. The equation must always balance.
4.  **Atomic Persistence**:
    - [ ] Force-kill the process (`CTRL+C` or `taskkill`) multiple times during a run. Verify no JSON files are truncated or corrupted on restart.

### **Compliance Check Commands**
```bash
# Verify no legacy resume logic is used
grep -r "supplier_extraction_progress" tools/
# Should return 0 results in new code paths.

# Verify all saves are atomic
grep -r "WindowsSaveGuardian" tools/ utils/
# Should show usage in save paths.
```

---

## 🏁 **CONCLUSION**

This specification defines the **Amazon FBA Agent System v4.0**, a production-ready, deterministic, and crash-safe platform. The architecture is built on the **Freeze-Mark-Resume** principle, with `system_progression` as the single source of truth for resumption and `linking_map.json` as the single source of truth for completion.

**Document Status**: Authoritative Reference
**Last Updated**: December 29, 2025
**Next Review**: After next major system change.

---
