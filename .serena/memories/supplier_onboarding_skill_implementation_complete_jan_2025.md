# Supplier Onboarding Skill Implementation - Complete

## Summary

Successfully implemented a complete **Agent Skill + Python Wizard** architecture for guided supplier onboarding in the Amazon FBA Agent System. This replaces the attempted `ai_enhanced_setup/` implementation that faced architectural restrictions.

## Implementation Complete

### Components Created

1. **Agent Skill (Orchestrator)**
   - Location: `skills/supplier-onboarding/`
   - Files:
     - `skill.yaml` - Interface definition with all parameters
     - `main.py` - Orchestration logic (file-based communication only)
     - `README.md` - Complete documentation

2. **Python Wizard (Executor)**
   - Location: `utils/supplier_onboarding_wizard.py`
   - Size: ~650 lines
   - Features: All critical adjustments implemented

3. **Documentation**
   - `ONBOARDING_WORKFLOW_EXAMPLES.md` - 3 complete real-world scenarios
   - Step-by-step user guides
   - Troubleshooting section

## Critical Adjustments Implemented

### 1. Runner Selection (HIGHEST PRIORITY)
- 4-tier fallback hierarchy:
  1. Supplier-specific: `run_custom_{supplier-id}.py`
  2. Workflow-mapped: From `system_config.json`
  3. General runner: `run_complete_fba_system.py`
  4. Auto-generate shim as fallback
- Function: `determine_runner()` in wizard

### 2. Absolute Path Discipline
- All file operations use absolute paths
- Windows/WSL/Linux aware session directories
- Function: `resolve_repo_root()` and `_create_session_dir()`

### 3. Robust Domain Normalization
- Handles: URL, hyphen-form, dot-form
- UK TLD support (`.co.uk`, `.org.uk`, etc.)
- Function: `normalize_domain()` and `generate_supplier_forms()`

### 4. Accurate Sanity Check
- 6 criteria with exact field names:
  1. `scraping_rate`: `supplier_products_completed >= 20`
  2. `amazon_cache`: ≥1 recent file
  3. `linking_map`: Updated + >100 bytes (hyphen-form dir)
  4. `financial_csv`: Present + >1KB
  5. `processing_state`: Updated (underscore-form file)
  6. `no_critical_errors`: Scan `logs/debug/*`
- Function: `verify_sanity_outputs()`

### 5. Naming Conventions Enforcement
- **Dot-form** (domain): `poundwholesale.co.uk` → selector configs
- **Hyphen-form** (supplier_id): `poundwholesale-co-uk` → linking maps
- **Underscore-form** (supplier_name): `poundwholesale_co_uk` → state files
- Class: `NamingConventions` with static methods

## Architecture Design

```
Agent Skill (skills/supplier-onboarding/main.py)
├─> Input validation
├─> Session file creation (input.json)
├─> Wizard invocation via subprocess
└─> Result presentation (read output.json)

Python Wizard (utils/supplier_onboarding_wizard.py)
├─> Domain normalization
├─> File generation to staging/
├─> Atomic move to final locations
├─> Runner selection with fallback
├─> Sanity check (FBA_TEST_MODE=true)
├─> 6-criterion verification
└─> Remediation generation
```

**File-Based Interface (CRITICAL):**
- Skill writes: `input.json` (all parameters + repo_root)
- Wizard reads: `input.json`
- Wizard executes: All file operations
- Wizard writes: `output.json` (results + sanity checks)
- Skill reads: `output.json`
- **NO direct imports between layers**

## Usage Examples

### New Supplier (Clearance King)

```bash
# Via Claude Code
"Use supplier-onboarding skill to add clearance-king.co.uk"

# Via Python (testing)
cd skills/supplier-onboarding
python main.py \
  --domain "clearance-king.co.uk" \
  --categories-source "config/clearance_king_categories.json" \
  --selectors-source "config/supplier_configs/clearance-king.co.uk.json" \
  --workflow-key "clearance_king_workflow" \
  --scaffolds supplier-package runner-shim
```

### Existing Supplier Update

```bash
python main.py \
  --domain "poundwholesale.co.uk" \
  --categories-source "config/poundwholesale_categories.json" \
  --selectors-source "config/supplier_configs/poundwholesale.co.uk.json" \
  --workflow-key "poundwholesale_workflow"
  # No scaffolds = update only
```

### Validation Only (Reference Mode)

```bash
python main.py \
  --domain "poundwholesale.co.uk" \
  --categories-source "config/poundwholesale_categories.json" \
  --selectors-source "config/supplier_configs/poundwholesale.co.uk.json" \
  --workflow-key "poundwholesale_workflow" \
  --mode reference
```

## Real-World Workflow

1. **Prerequisites** (~2 min):
   - Start Chrome: `chrome --remote-debugging-port=9222`
   - Navigate to repo root
   - Prepare selectors (DevTools copy)

2. **Configuration** (~5 min):
   - Create selectors JSON
   - Create categories JSON
   - OR use inline JSON

3. **Skill Execution** (~7-10 min):
   - Invoke skill
   - Wizard generates files
   - Sanity check runs
   - Results returned

4. **Verification** (~1 min):
   - Review 6-criterion results
   - Check files generated
   - Follow remediation if needed

5. **Full Run**:
   - `python run_custom_{supplier-id}.py`

## Files Generated

For new supplier `clearance-king.co.uk`:

1. `config/supplier_configs/clearance-king.co.uk.json` (dot-form)
2. `config/clearance_king_categories.json`
3. `suppliers/clearance-king-co-uk/config/product_selectors.json` (hyphen-form)
4. `suppliers/clearance-king-co-uk/.supplier_ready`
5. `run_custom_clearance-king-co-uk.py` (auto-generated shim)

## Session Files (Debugging)

Location varies by OS:
- Windows: `C:/temp/onboarding/<session_id>/`
- WSL: `/mnt/c/temp/onboarding/<session_id>/`
- Linux: `/tmp/onboarding/<session_id>/`

Contains:
- `input.json` - All parameters passed to wizard
- `output.json` - Wizard results
- `staging/` - Temporary files before atomic move

## Success Output Example

```json
{
  "success": true,
  "files_generated": [
    "C:\\...\\config\\supplier_configs\\clearance-king.co.uk.json",
    "C:\\...\\config\\clearance_king_categories.json"
  ],
  "sanity_results": {
    "scraping_rate": true,
    "amazon_cache": true,
    "linking_map": true,
    "financial_csv": true,
    "processing_state": true,
    "no_critical_errors": true
  }
}
```

## Remediation Example

If sanity checks fail:

```json
{
  "success": false,
  "sanity_results": {
    "scraping_rate": false,
    "amazon_cache": true,
    ...
  },
  "remediation": {
    "scraping_rate": {
      "issue": "Less than 20 products scraped",
      "actions": [
        "Verify selectors are correct",
        "Check config/supplier_configs/{domain}.json",
        "Use DevTools to verify CSS selectors",
        "Ensure no login required"
      ]
    }
  }
}
```

## Testing Status

- ✅ Architecture validated via sequential thinking (5 steps)
- ✅ All components implemented
- ✅ Documentation complete
- ⏳ Pending: Manual testing with mock supplier
- ⏳ Pending: Production testing with real supplier

## Next Steps for Implementation

1. **Test Standalone Python**:
   ```bash
   cd skills/supplier-onboarding
   python main.py --domain "test-supplier.com" \
     --categories-source '{"category_urls": ["http://test.com"]}' \
     --selectors-source '{"field_mappings": {...}}' \
     --workflow-key "test_workflow"
   ```

2. **Test via Claude Code Skills**:
   - Ensure skill is recognized by Claude Code
   - Invoke via natural language
   - Verify results

3. **Production Rollout**:
   - Use with clearance-king.co.uk
   - Monitor session files for debugging
   - Verify all 6 criteria pass

4. **Iterate Based on Feedback**:
   - Adjust selectors if needed
   - Refine remediation guidance
   - Add auth helper generation (Phase 2)

## Key Design Decisions

1. **Skill + Wizard over Pure Skill**: Needed separation for atomic file operations
2. **File-Based Interface**: Maintains strict separation, enables debugging
3. **Session Files Preserved**: Kept for debugging (cleanup commented out)
4. **Staging Pattern**: Generate → Validate → Atomic Move
5. **4-Tier Runner Selection**: Flexibility with automatic fallback

## Why Previous Attempt Failed

The `ai_enhanced_setup/` implementation likely failed due to:
- ❌ Direct file writes via Claude (violates Serena read-only)
- ❌ Mixed AI + deterministic logic (architectural violation)
- ❌ No atomic operations (WindowsSaveGuardian missing)
- ❌ Insufficient file verification

The new architecture solves all of these by:
- ✅ Skill doesn't write files directly (delegates to wizard)
- ✅ No AI in pipeline (onboarding separate from execution)
- ✅ Wizard uses WindowsSaveGuardian for all writes
- ✅ Both layers verify files

## Documentation Locations

1. `skills/supplier-onboarding/README.md` - Skill documentation
2. `skills/supplier-onboarding/skill.yaml` - Interface definition
3. `ONBOARDING_WORKFLOW_EXAMPLES.md` - Complete workflows
4. `utils/supplier_onboarding_wizard.py` - Inline code comments

## Estimated Time to Production

- **Already Complete**: Architecture + Implementation (~4 hours)
- **Testing**: 2-3 hours
- **Production Validation**: 1 hour
- **Total**: 7-8 hours to fully production-ready

## Contact Points for Continuation

If continuing this work:
1. Read: `ONBOARDING_WORKFLOW_EXAMPLES.md` for usage
2. Test: Run standalone Python first
3. Debug: Check session files in temp directories
4. Extend: Add auth helper generation in Phase 2
