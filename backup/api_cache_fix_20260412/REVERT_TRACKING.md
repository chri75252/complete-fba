# REVERT_TRACKING.md

## Session: API Cache Fix - 20260412

## Problem
- `load_metrics(base_dir, effective_supplier)` (metrics_core.py line 681) creates its own `MetricsLoader(base_dir)` with empty `_cache`
- Every API request re-read all source files from scratch (~13 seconds)
- `_response_cache` in api.py should cache the final response but cache hits also took ~13s (broken cache hit path due to mtime comparison)
- `get_analysis` (line 615) and `run_ai_analysis` (line 794) created their own MetricsLoader instead of using singleton

## Root Causes Found

### RC1: load_metrics creates new MetricsLoader each request
- `metrics_data = load_metrics(base_dir, effective_supplier)` calls module-level function which creates its own loader
- This loader has an empty `_cache` on every request — zero reuse of MetricsLoader's internal mtime-based cache
- **Fix:** Replaced `load_metrics(...)` with direct singleton loader method calls so `_get_loader()` singleton's `_cache` persists

### RC2: Mtime comparison failing for sandbox lineage
- Cache retrieval checked mtimes with `supplier` but cache storage stored with `effective_supplier`
- For `lineage=latest_sandbox`, the resolved sandbox supplier name differs from base supplier name used in cache key
- The mtime dict keys themselves could differ between store/retrieve causing `entry["mtimes"] != current_mtimes`
- **Fix:** Removed mtime comparison entirely — TTL alone is sufficient for dashboard freshness requirements

## Changes

| File | Change | Status |
|------|--------|--------|
| dashboard_v2_redesign/api.py | Replace `load_metrics(base_dir, effective_supplier)` with direct singleton loader method calls (line 271-282) | DONE |
| dashboard_v2_redesign/api.py | Remove mtime check from cache retrieval — use TTL only (line 235-244) | DONE |
| dashboard_v2_redesign/api.py | Remove mtimes from cache storage (line 476-482) | DONE |
| dashboard_v2_redesign/api.py | Remove unused `load_metrics` import (line 95) | DONE |
| dashboard_v2_redesign/api.py | Kill rogue `MetricsLoader(base_dir)` — grep shows none remaining except singleton init | VERIFIED |

## Timing Results (after fix)
- Cold request: ~12,000ms (computation — unavoidable)
- Cached request: ~54ms (240x faster than before 13s)
- Forced refresh: ~12,000ms (correctly bypasses cache)
- Cached request 2: ~45ms (consistent)

## Backup
- Source: dashboard_v2_redesign/api.py
- Backup: backup/api_cache_fix_20260412/api.py

## Restore
```cmd
copy "backup\api_cache_fix_20260412\api.py" "dashboard_v2_redesign\api.py"
```

## Verification
1. python -m py_compile dashboard_v2_redesign/api.py — PASS
2. Server started on port 8001 (fresh PID)
3. Timing test: cold ~12s, cached ~54ms, forced ~12s, cached2 ~45ms — PASS
