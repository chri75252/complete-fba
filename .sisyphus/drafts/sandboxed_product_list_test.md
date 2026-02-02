# Draft: Sandboxed Runs + Product List Refresh

## Requirements (confirmed)
- Explain why run `9a250a20-35a4-4c3b-88b7-203f06175dd8` was not headless (headed browser expectation for Keepa/SellerAmp extensions).
- Plan a change so sandboxed runs write under a per-supplier sandbox container folder.
- Select 6 products from `OUTPUTS/cached_products/angelwholesale-co-uk_products_cache.json` from different categories.
- Confirm whether product list refresh should be provided via chat input or via a file path.

## Technical Decisions (proposed)
- Sandbox outputs: propose adding a per-supplier sandbox root directory (decision pending on exact desired path layout).
- Product list refresh input: current chat tool schema only supports `products_path`; direct chat JSON input would require extending tool schema/LLM prompt.

## Research Findings (evidence)
- Run artifacts exist for `9a250a20...` including job, status, runner logs, and sandbox output directories.

## Open Questions
- Preferred sandbox root layout (examples):
  - A) `OUTPUTS/FBA_ANALYSIS/linking_maps/sandboxes/<supplier>/<run_id>/...`
  - B) `OUTPUTS/SANDBOX/<supplier>/<run_id>/{linking_maps,processing_states,financial_reports,cached_products}/...`
  - C) Keep current flat naming but add a helper “index” folder.
- For product list refresh: do you want to paste a JSON array in chat (requires new parsing) or keep file-based input only?

## Scope Boundaries
- INCLUDE: run artifact analysis, sandbox folder grouping plan, product selection, input method confirmation.
- EXCLUDE (for now): implementing the folder grouping changes (will be in a separate execution phase).
