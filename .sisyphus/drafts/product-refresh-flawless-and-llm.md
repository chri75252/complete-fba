# Draft: Product Refresh Flawless + LLM Behavior

## Requirements (confirmed)
- Product list refresh must be **flawless**: correct sandbox outputs, no leakage into main workflow files.
- Input product list must resolve to an **absolute OS path under** `OUTPUTS/PRODUCTS_LISTS/` regardless of filename supplied.
- **No cached_products write** during product refresh (input list is treated as the supplier cache for now).
- Linking map must be written **every N products**, where **N comes from** `config/system_config.json` (same as main workflow linking map batch size, currently `system.linking_map_batch_size`).
- Add a **grouping step**: group products by category key (use `source_url`) so categories process sequentially.
- Generate a **SANDBOXED processing state file** compatible with the main workflow / category analysis runs (EnhancedStateManager semantics), without affecting main run resume pointers.
- Hard guardrail: **never overwrite or modify main workflow outputs** (processing states, linking maps, cached products, amazon cache, financial reports).
- After product refresh is fixed, remove URL fast-path and make the LLM actually process prompts and produce correct tool outputs + correct expected output paths.

## Evidence / Observations (file-grounded)
- Sandbox overwrite bug exists in `control_plane/run_product_list_refresh.py` (input file can override job sandbox supplier).
- Run `303ca1b8-eb5a-4aa9-9de2-5fc5b8e6593f` was cancelled; wrote main cached_products due to sandbox collapse.
- Run `2003c1b4-99f6-4caf-8257-efa851a9923b` completed and wrote `linking_map.json` — but to **main** path, not sandbox.
- Runner currently writes to global `OUTPUTS/FBA_ANALYSIS/amazon_cache` (not sandboxed) and also triggers financial calculator.
- Worker status uses MetricsLoader-based heuristics; it reports sandbox artifacts missing when outputs were written to base paths.

## Existing Changes Already Made (Feb 12, 2026)
- `control_plane/run_product_list_refresh.py`: accepts both dict-wrapped and list-only products JSON.
- `control_plane/tools/product_list_refresh.py`: resolves relative `products_path` against control plane root; may be incorrect for `OUTPUTS/...` repo-relative paths.

## Scope Boundaries
- INCLUDE: `control_plane/*`, `dashboard/*`, `config/system_config.json` (read-only usage), state/output path logic.
- EXCLUDE: Any edits to protected `tools/*` or `run_custom_*.py` files; any credential changes.

## Open Questions (to resolve during plan execution if needed)
- How to sandbox Amazon cache for refresh runs (per-run overrides dir vs other namespacing).
- Whether to disable financial calculator during refresh runs (to avoid reading/writing global caches) or sandbox it.
