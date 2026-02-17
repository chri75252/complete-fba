# State Management and Resumption Guide

This document outlines the architecture and procedures for state management, atomic persistence, and interruption recovery in the Amazon FBA Agent System.

---

## 1. The Golden Rule

> **NEVER manually edit state files.**

The system's integrity depends on a strict single-writer model and authoritative, file-grounded verification. Manual intervention in `OUTPUTS/CACHE/processing_states/*.json` or linking maps can lead to:
- **Manifest Drift**: Disalignment between frozen category lists and live URLs.
- **Pointer Corruption**: PCI (Persistent Category Index) misalignment causing the system to skip categories or loop infinitely.
- **Data Loss**: Overwriting valid progress with incorrect manual indices.

If state repair is absolutely necessary, follow the [Resetting State](#4-resetting-state-procedure) procedure.

---

## 2. How Resumption Works

The system is designed to be "marathon-ready," supporting 18+ hour sessions with reliable recovery from crashes, reboots, or network failures.

### 2.1 Authoritative Pointers
- **PCI (Persistent Category Index)**: The 1-based authoritative pointer for the category manifest. It only advances after a category is marked as fully completed.
- **Resumption Index**: Tracks product-level progress within the current phase (Supplier Extraction or Amazon Analysis).
- **Session Cursor**: A runtime-only calculation that determines the first incomplete URL by checking its status in the linking map/cache.

### 2.2 Startup Analysis
On every launch, the `FixedEnhancedStateManager` performs a comprehensive startup analysis:
1. **File-Grounded Verification**: Counts actual entries in linking maps and product caches.
2. **ISS-007 Reconciliation**: If a mismatch is detected between state counters and file counts, the system authoritatively aligns counters to the **Linking Map** (Single Source of Truth).
3. **PCI Hardening**: Ensures the category pointer is preserved across runs and never defaults to 1 unless it is a fresh start.

### 2.3 Deterministic vs. Heuristic Resume
- **Deterministic**: Resumes exactly from the last saved product index based on file counts.
- **Heuristic (Reverse Gap)**: Triggered if the Linking Map contains more entries than the Product Cache. This indicates that products were matched but their supplier data is missing or corrupted, allowing the system to force a targeted re-extraction.

---

## 3. Atomic Writes (WindowsSaveGuardian)

To prevent file corruption and "WinError 5: Access Denied" errors common on Windows (often caused by indexing services or antivirus locking files), the system uses the `WindowsSaveGuardian`.

### 3.1 Persistence Strategies
The guardian attempts the following strategies in order:
1. **Alternative Temp Directory**: Writes to a system temp folder and then copies to the target. This bypasses local directory locks.
2. **Temp Then Replace**: The classic atomic pattern (write `.tmp`, then `os.replace`).
3. **Backup Then Replace**: Creates a `.bak` file before attempting a write.
4. **Direct Write**: A non-atomic last resort if all other methods fail.

### 3.2 Anti-Truncation Guard
The guardian includes a safety check that prevents "empty state" writes. If the new data is significantly smaller than the existing file (e.g., saving 1 product index over a file with 10,000 entries), the guard will trigger a merge or block the write to prevent progress loss.

---

## 4. Resetting State Procedure

If you must reset or modify state, follow these steps to ensure safety:

1. **Backup**: Copy the current state file to `backup/manual_repair_<YYYYMMDD>/`.
2. **Clean Reset**:
   - To restart a specific supplier from scratch, delete its state file in `OUTPUTS/CACHE/processing_states/` and its linking map in `OUTPUTS/FBA_ANALYSIS/linking_maps/`.
3. **Soft Reset (Targeted)**:
   - To re-run a specific category, you can use the `force_cache_rebuild()` method via a runner script, which resets the resumption index to 0 while preserving the PCI.
4. **Verify**: Run the dashboard (`python dashboard/run_dashboard.py`) to confirm the state is recognized correctly before starting a new run.

---

## 5. Reference Implementation
- **State Logic**: `utils/fixed_enhanced_state_manager.py`
- **Atomic Persistence**: `utils/windows_save_guardian.py`
- **Path Resolution**: `utils/path_manager.py`
