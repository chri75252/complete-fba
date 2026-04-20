<!-- DASHBOARD METRICS API REFERENCE - Generated 2026-04-12 -->

# Dashboard Metrics API — How It Works

## What Files The Dashboard Reads

| Dashboard Section | Source File |
|---|---|
| Total Extracted (product count) | `OUTPUTS/cached_products/{supplier}_products_cache.json` |
| Total Processed / Match Stats / Confidence % | `OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier}/linking_map.json` |
| Profitable count / Avg ROI / Total Profit / Charts | `OUTPUTS/FBA_ANALYSIS/financial_reports/{supplier}/fba_financial_report_*.csv` |
| Phase / Category Index / Fresh Starts / Progress | `OUTPUTS/CACHE/processing_states/{supplier}_processing_state.json` |
| Terminal Logs | `logs/debug/run_custom_{supplier}_*.log` |

## How The Auto-Refresh Works

- **Endpoint:** `GET /api/metrics/{supplier}`
- **Called by:** Browser auto-refresh timer (default: every 60 seconds)
- **Query params:** `lineage=base` (main) or `latest_sandbox`, `report=` (specific CSV), `sales_field=`, `force_refresh=`

## Two Cache Layers

### 1. Response Cache (30 second TTL)

- Stored in `_response_cache` dict (dashboard_v2_redesign/api.py module-level)
- Returns entire JSON response in ~50ms if called within 30 seconds of last call
- Invalidated after 30 seconds (time-based only)
- Bypassed when `force_refresh=1` is passed (Refresh Now button)

### 2. MetricsLoader Internal Cache (mtime-based)

- Each `load_state_metrics`, `load_linking_map_metrics`, `load_financial_metrics` method checks file modification time
- If file hasn't changed since last read, returns cached result without disk I/O
- This is why after 30s TTL expiry, requests take ~200ms instead of ~12s (files checked but not re-read)

## What Happens On Each Refresh Call

| Scenario | Time | What Happens |
|---|---|---|
| First request after server starts | ~12s | Reads all 5 files from disk, parses JSON/CSV, computes metrics, caches result |
| Request within 30 seconds | ~50ms | Returns cached JSON response from memory |
| Request after 30 seconds, files unchanged | ~200ms | Loader methods check mtime, no files changed, return cached per-file results |
| Request after 30 seconds, files changed | ~12s | Only changed file(s) re-read and re-parsed |
| "Refresh Now" button (force_refresh=1) | ~12s | Ignores all caches, re-reads everything |

## Logs Are Never Cached

- Terminal logs are read fresh every request (`tail_logs()`)
- This is intentional because logs are continuously written during active workflow runs

## When Files Change (Triggers Re-Read After TTL Expiry)

| File | Written By |
|---|---|
| `products_cache.json` | Supplier scraper (every batch) |
| `linking_map.json` | Amazon matching step (every batch) |
| `financial_reports/*.csv` | Financial calculator (after N linking map entries) |
| `processing_state.json` | Workflow engine (after category batch) |
| `run_custom_*.log` | Any runner script (continuous during runs) |

## Recommendation

Set Auto Refresh to **Disabled** when analyzing completed runs (no active workflow). The data is static — polling generates identical results. Use "Refresh Now" for manual updates.

## Related Files

- `dashboard_v2_redesign/api.py` — FastAPI app, endpoints, caching logic
- `dashboard_legacy_streamlit/metrics_core.py` — MetricsLoader class with mtime-based per-file cache
- `dashboard_v2_redesign/static/js/app.js` — `fetchMetrics()` function, auto-refresh timer
- `dashboard_v2_redesign/templates/index.html` — Dashboard UI, Data Sources panel at bottom
- `wiki-dec-3/10. Api Reference/10.5. Dashboard Api.md` — Full prose documentation

---

*Document Version: 1.0*  
*Last Updated: 2026-04-12*