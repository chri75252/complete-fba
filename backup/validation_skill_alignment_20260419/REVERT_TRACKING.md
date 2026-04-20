# REVERT TRACKING — validation_skill_alignment_20260419

Date: 2026-04-19
Reason: Align validation prompt/skill with stale-data workflow standards, fix API-key/tool reference discipline, and synchronize native skill locations (.gemini and OpenCode skill paths).

## Planned Edit Scope

| # | Target File | Intended Scope | Backup Source Path | Planned Validation | Status |
|---|---|---|---|---|---|
| 1 | `workflows/fba_product_validation_prompt.md` | Add Phase 0 preflight, deterministic API key order, stronger matching rules, output structure, anti-pattern checklist | `backup/validation_skill_alignment_20260419/workflows/fba_product_validation_prompt.md` | File readback, lsp_diagnostics, manual section checks | Completed |
| 2 | `workflows/fba-validation-workflow/SKILL.md` | New canonical validation skill | N/A (new file) | File exists, section completeness, lsp_diagnostics | Completed |
| 3 | `workflows/fba-validation-workflow/references/EXECUTION_ENFORCEMENT.md` | New enforcement reference with phase gates and anti-evasion checks | N/A (new file) | File exists, checklist integrity, lsp_diagnostics | Completed |
| 4 | `.opencode/skills/fba-validation-workflow/SKILL.md` | Native project skill mirror of canonical validation skill | N/A (new file) | Byte/line parity check vs workflows copy | Completed |
| 5 | `.opencode/skills/fba-validation-workflow/references/EXECUTION_ENFORCEMENT.md` | Native project enforcement mirror | N/A (new file) | Byte/line parity check vs workflows copy | Completed |
| 6 | `C:/Users/chris/.gemini/antigravity/skills/stale-data-workflow/SKILL.md` | Replace outdated copy with latest canonical workflow version | `backup/validation_skill_alignment_20260419/global_gemini/stale-data-workflow/SKILL.md` | `fc` comparison with canonical file | Completed |
| 7 | `C:/Users/chris/.gemini/antigravity/skills/stale-data-workflow/references/EXECUTION_ENFORCEMENT.md` | Replace outdated copy with latest canonical workflow reference | `backup/validation_skill_alignment_20260419/global_gemini/stale-data-workflow/references/EXECUTION_ENFORCEMENT.md` | `fc` comparison with canonical file | Completed |
| 8 | `C:/Users/chris/.gemini/antigravity/skills/fba-validation-workflow/SKILL.md` | Add global Gemini-native validation skill | N/A (new file) | File exists and matches canonical content | Completed |
| 9 | `C:/Users/chris/.gemini/antigravity/skills/fba-validation-workflow/references/EXECUTION_ENFORCEMENT.md` | Add global Gemini-native enforcement reference | N/A (new file) | File exists and matches canonical content | Completed |
| 10 | `C:/Users/chris/.config/opencode/skills/fba-validation-workflow/SKILL.md` | Add global OpenCode-native validation skill | N/A (new file) | File exists and matches canonical content | Completed |
| 11 | `C:/Users/chris/.config/opencode/skills/fba-validation-workflow/references/EXECUTION_ENFORCEMENT.md` | Add global OpenCode-native enforcement reference | N/A (new file) | File exists and matches canonical content | Completed |

## Restore Instructions

If rollback is required:
1. Restore repo files from `backup/validation_skill_alignment_20260419/workflows/...`.
2. Restore global Gemini stale-data files from `backup/validation_skill_alignment_20260419/global_gemini/stale-data-workflow/...`.
3. Remove newly created validation skill folders if needed:
   - `workflows/fba-validation-workflow/`
   - `.opencode/skills/fba-validation-workflow/`
   - `C:/Users/chris/.gemini/antigravity/skills/fba-validation-workflow/`
   - `C:/Users/chris/.config/opencode/skills/fba-validation-workflow/`

## Notes

- This pass is documentation/skill-alignment only; no runtime Python code paths are modified.
- Validation-first discipline follows: file evidence -> deterministic tool references -> post-save verification.
- Note: `lsp_diagnostics` for `.md` files is not supported in current environment (no Markdown LSP server configured). Verification used file existence + readback + `fc` parity checks.
