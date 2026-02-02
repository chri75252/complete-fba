# Draft: Category Analyze → Linking Map Rows (Follow-up)

## Requirements / Goal (user)
- User expects **sandboxed category analysis** when providing a supplier category URL.
- User expects **sandboxed product list refresh/analysis** only when a product list is provided.
- User tried: "analyze this category: https://angelwholesale.co.uk/Category/Baby-Clothing/Baby-Clothing-Sets"
- System responded with ~50 rows from existing linking map, path:
  - `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\FBA_ANALYSIS\linking_maps\angelwholesale.co.uk\linking_map.json`

## Observed Behavior (grounded)
- Chat likely selected a READ tool (`find_linking_entries`) rather than running a new extraction job (`enqueue_run`).
- Returned fields included `created_at`, suggesting the "production" linking map schema includes more fields than the product-list refresh runner’s linking rows.

## Hypotheses to Validate
- The planner prompt may be biased toward read tools when it sees a supplier domain.
- The executor may infer `supplier_domain` from URL and then query linking map without using the category URL.

## Clarifications (confirmed)
- User can input **one or multiple categories** in a single request.
- The system must run **sandboxed sessions** for category analysis and product-list analysis.
  - Sandbox outputs: new `linking_map`, `processing_state`, `financial_report` under sandbox supplier name.
- Existing production `linking_map` must not be treated as the result of “analyze category”.
- The only production artifact that may be reused is the supplier cached products file (prices likely unchanged), unless running the full workflow is simpler.
- For category analysis, acceptable behavior:
  - Scrape category → extract product URLs (and count)
  - Optionally compare to existing cached products for that category
  - Then execute Amazon extraction steps (to produce sandbox outputs)

## Open Questions
- Should sandboxed category analysis default to **cache-first** (reuse existing cached products if present) or default to **full supplier workflow** (scrape supplier product info fresh)?

## Scope Boundaries
- INCLUDE: investigate tool selection behavior + recommend prompt/heuristic changes; update markdown docs.
- EXCLUDE: implementing code changes in `control_plane/` / `tools/` for now.
