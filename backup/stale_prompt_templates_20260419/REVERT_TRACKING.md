# REVERT TRACKING — stale_prompt_templates_20260419

Date: 2026-04-19
Reason: Add stale-data prompt templates for product-list and category-list execution, and make minor strictness improvements to stale-data workflow instructions for exclusion handling, explicit sales-column treatment, and stronger tool-usage enforcement.

## Planned Edit Scope

| # | Target File | Intended Scope | Backup Source Path | Planned Validation | Status |
|---|---|---|---|---|---|
| 1 | `workflows/stale-data-workflow/SKILL.md` | Minor wording updates for exclusions, explicit use of both sales columns, and mandatory template usage references | `backup/stale_prompt_templates_20260419/workflows/stale-data-workflow/SKILL.md` | File readback, targeted diff review, parity after sync | Pending |
| 2 | `workflows/stale-data-workflow/references/EXECUTION_ENFORCEMENT.md` | Minor enforcement updates for exclusion-list handling and sales-column evidence | `backup/stale_prompt_templates_20260419/workflows/stale-data-workflow/references/EXECUTION_ENFORCEMENT.md` | File readback, targeted diff review, parity after sync | Pending |
| 3 | `workflows/stale_product_list_prompt_template.md` | New template for product-list stale-data runs | N/A (new file) | File exists, placeholders correct, prompt completeness | Pending |
| 4 | `workflows/stale_category_list_prompt_template.md` | New template for category-list stale-data runs | N/A (new file) | File exists, placeholders correct, prompt completeness | Pending |

## Restore Instructions

If rollback is required:
1. Restore stale-data workflow files from `backup/stale_prompt_templates_20260419/workflows/stale-data-workflow/...`.
2. Remove newly created prompt templates:
   - `workflows/stale_product_list_prompt_template.md`
   - `workflows/stale_category_list_prompt_template.md`

## Notes

- This pass is prompt/skill-instruction work only.
- If stale-data workflow files are updated, mirrored native skill copies must be re-synced afterward.
