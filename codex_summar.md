# Hybrid Workflow Audit Report (Latest Two Runs)

## Scope

- Inputs reviewed:
    - Log output 1: fba_extraction_20250904.log (most recent)
    - Log output 2: fba_extraction_20250902.log (previous)
    - Processing state snapshots:
    - OUTPUTS/CACHE/processing_states/at-the-startoffirstrun.json
    - OUTPUTS/CACHE/processing_states/1strun.json
    - OUTPUTS/CACHE/processing_states/poundwholesale_co_uk_processing_state.json (latest)
-
Reference: COMPLETE_WORKFLOW.md (frozen denominators, chronology)
-
Method: Cross-validate logs, processing state, linking map, supplier cache, and Amazon cache. Treat logs as non-authoritative unless corroborated.

## Implementation Status

- Denominator Freeze: Partial
    - Evidence 1
    OUTPUTS/CACHE/processing_states/poundwholesale_co_uk_processing_state.json L1-L16
    {
      "schema_version": "1.1_FIXED",
      ...
      "supplier_extraction_progress": { "current_category_index": 92, "total_categories": 231, ... },
      ...
      "system_progression": { "current_phase": "supplier", "current_category_index": 1, "total_categories": 1, ... }
    }
- Evidence 2
    COMPLETE_WORKFLOW.md L348-L355
    OUTPUT: Frozen denominator used for category progress %; never changed
    Policy & Rationale: ... record the denominator the first time ... and freeze it. ... do not mutate the frozen denominator.
-
Finding: Drift persists (231 vs 1). Frozen denominator not reflected in system_progression; partial.
-
Single Writer Enforcement: Partial
    - Evidence 1
    OUTPUTS/CACHE/processing_states/poundwholesale_co_uk_processing_state.json ["supplier_extraction_progress"], ["system_progression"]
    "supplier_extraction_progress": { "current_category_index": 92, "total_categories": 231, ... }
    "system_progression": { "current_phase": "supplier", "current_category_index": 1, "total_categories": 1, ... }
- Evidence 2
    OUTPUTS/CACHE/processing_states/poundwholesale_co_uk_processing_state.json ["runtime_settings"]["current_phase"], ["system_progression"]["current_phase"]
    "runtime_settings": { "current_phase": "FRESH_CATEGORIES", ... }
    "system_progression": { "current_phase": "supplier", ... }
-
Finding: Both legacy and unified fields persist with mismatched values; partial single-writer migration.
-
Resume Fidelity & Banners: Partial
    - Evidence 1
    OUTPUTS/CACHE/processing_states/poundwholesale_co_uk_processing_state.json ["resumption_index"], ["last_processed_index"]
    "resumption_index": 0,
    "last_processed_index": 22,
    "resume_reason": "reverse_gap_restart_preserved"
- Evidence 2
    OUTPUTS/CACHE/processing_states/at-the-startoffirstrun.json L1-L12, L1298-L1312
    "resumption_index": 0, "progress_index": 10386, ...
    "system_progression": { "current_category_index": 1, "total_categories": 1, "current_product_index_in_category": 10386, ... }
-
Finding: Resume pointer not aligned to known progress; resume banner not observed in latest logs; partial.
-
Per-Category Filter Invariant: Failed
    - Evidence 1
    fba_extraction_20250904.log L1-L1
    [empty file]
- Evidence 2
    fba_extraction_20250902.log L1-L1
    [empty file]
-
Finding: Canonical invariant line “🧮 Filter Invariant: …” not present in either recent log.
-
Dedupe Gating (0 new → single summary): Failed
    - Evidence 1
    fba_extraction_20250904.log L1-L1
    [empty file]
- Evidence 2
    fba_extraction_20250902.log L1-L1
    [empty file]
-
Finding: No “🔍 DEDUP SUMMARY: 0 new; skipped re-scan” in latest logs; unconfirmed → fail.
-
Per-Product Callback (prefiltered) + Cadence Saves: Partial
    - Evidence 1 (supplier cache entries persisted)
    OUTPUTS/cached_products/poundwholesale-co-uk_products_cache.json L1-L22
    [
      { "title": "'Welcome' Wellies Door Mat", ..., "scraped_at": "2025-07-29T04:35:25.293789" },
      { "title": "\"Congratulations\" Assorted Colours Balloons 12 Pack", ..., "scraped_at": "2025-08-12T15:56:05.845654" }
    ]
- Evidence 2 (progress moved)
    OUTPUTS/CACHE/processing_states/1strun.json ["last_processed_index"], ["progress_index"]
    "last_processed_index": 3,
    "progress_index": 3
-
Finding: Persisting and progress occur; cadence save logs not visible in latest logs; partial.
-
Atomic State Saves: Successful
    - Evidence 1 (telemetry)
    OUTPUTS/DIAGNOSTICS/save_telemetry.log L1-L6
    {"strategy": "temp_then_replace", "status": "SUCCESS", ...}
    {"strategy": "backup_then_replace", "status": "SUCCESS", ...}
- Evidence 2 (large linking map saved atomically with fallback)
    OUTPUTS/DIAGNOSTICS/save_telemetry.log L15-L24
    {"strategy": "temp_then_replace", "status": "FAILED", "error_type": "PermissionError", ...}
    {"strategy": "alternative_temp_dir", "status": "SUCCESS", "details": {"path": ".../linking_map.json", "file_size_bytes": 1712476}}
-
Finding: Atomic persistence achieved with fallbacks; success.
-
Disallowed Sources for Resume (user progress tracking): Successful
    - Evidence 1 (file-grounded counts present)
    OUTPUTS/CACHE/processing_states/poundwholesale_co_uk_processing_state.json ["runtime_settings"]
    "runtime_settings": { "supplier_cache_count": 10386, "linking_map_count": 10515, ... }
- Evidence 2 (canonical caches present)
    OUTPUTS/COMBINED OJUTPUTS/LINKING MAP/linking_map.json L1-L18
    [ { "supplier_ean": "...", "amazon_asin": "...", "match_method": "...", ... }, ... ]
    OUTPUTS/FBA_ANALYSIS/amazon_cache/
    amazon_0007261632_9780007261635.json, amazon_0008472785_5060082934230.json, ...
- Finding: Resume logic appears grounded to cache+map; no evidence of “user progress tracking” driving resume.

## Discrepancies

- High — Denominator drift (Supplier vs system_progression)
    - Supplier shows total_categories=231 vs system_progression=1. This undermines progress/banners and violates frozen denominator spec.
    - Likely Cause: Legacy write vs normalized single-writer, or denominator freeze not persisted to system_progression.
    - Likely Cause: Legacy write vs normalized single-writer, or denominator freeze not persisted to system_progression.
-
Medium — Resume pointer inconsistency
    - resumption_index remains 0 while progress indices advance, causing start-at-0 symptoms or clamping reliance.
    - Likely Cause: Reverse-gap preserve coupled with missing banner/log confirmation and late clamping.
-
Medium — Missing runtime logs (auditability)
    - Latest two logs are empty; invariant/banners/dedupe summary not verifiable.
    - Likely Cause: Output redirection or disabled logging for runs.
-
Low/Medium — Phase field disagreement
    - runtime_settings.current_phase vs system_progression.current_phase mismatch; indicates vestigial write paths.

## Workflow Integrity

    - Authentication, supplier scraping, linking-map and Amazon cache appear intact from prior run artifacts:
    OUTPUTS/EXPERIMENTS/.../run_custom_poundwholesale_20250715_181810.log L1-L24
    ... 🔧 Logging initialised ... ✅ Connected to Chrome ... 🎉 Playwright login successful! ...
- Latest caches/maps present and populated:
    - Supplier cache JSON entries with realistic timestamps.
    - Amazon cache files exist and include EAN/title variants.
    - Linking map JSON populated with plausible entries (EAN/title matches).
- New integrations did not obviously break persistence; issues are primarily state consistency (denominator) and missing runtime log outputs.

## Conclusion

- Overall: Partially Compliant
    - Strong: Atomic saves, persistence health (supplier cache, linking map, amazon cache), avoidance of disallowed sources.
    - Weak/Partial: Frozen denominator not propagated to system_progression; resume pointer not confirmed via logs; no invariant/dedupe summary/banners visible in recent logs.
    - Weak/Partial: Frozen denominator not propagated to system_progression; resume pointer not confirmed via logs; no invariant/dedupe summary/banners visible in recent logs.
-
Recommendations (non-executable):
    - Ensure next run emits invariant, dedupe summary, and resume banner lines; confirm logging path.
    - Verify that system_progression.total_categories is set to the frozen denominator and remains stable.
    - Confirm single-writer shim normalizes all supplier progress writes; legacy indices should not drift.

## Summary Table

| Implementation                         | Status     | Evidence 1                                           | Evidence 2                                           |
|----------------------------------------|------------|------------------------------------------------------|------------------------------------------------------|
| Denominator Freeze                     | Partial    | processing_state.json: 231 vs 1 totals              | COMPLETE_WORKFLOW.md frozen denominator policy       |
| Single Writer Enforcement              | Partial    | supplier_extraction_progress vs system_progression   | runtime_settings.phase vs system_progression.phase   |
| Resume Fidelity & Banner               | Partial    | resumption_index=0 with progress>0                   | at-the-startoffirstrun.json high progress values     |
| Per-Category Filter Invariant          | Failed     | fba_extraction_20250904.log empty                    | fba_extraction_20250902.log empty                    |
| Dedupe Gating (0 new summary)          | Failed     | fba_extraction_20250904.log empty                    | fba_extraction_20250902.log empty                    |
| Prefiltered Callback + Cadence Saves   | Partial    | Supplier cache persisted entries                     | 1strun.json progress indices advanced                |
| Atomic State Saves                     | Successful | save_telemetry.log SUCCESS (fallbacks)               | Large linking map atomic save (alternative temp dir) |
| Disallowed Sources Avoidance           | Successful | runtime_settings: file-grounded counts               | Linking map + Amazon cache present                   |
OUTPUTS/CACHE/processing_states/poundwholesale_co_uk_processing_state.json ["system_progression"]["total_categories"]
"total_categories": 1
OUTPUTS/CACHE/processing_states/poundwholesale_co_uk_processing_state.json ["supplier_extraction_progress"]["total_categories"]
"total_categories": 231
OUTPUTS/COMBINED OJUTPUTS/LINKING MAP/linking_map.json L1-L18
[ { "supplier_ean": "5053249250236", "amazon_asin": "B00128V0NA", ... }, ... ]
OUTPUTS/FBA_ANALYSIS/amazon_cache/
amazon_0007261632_9780007261635.json
OUTPUTS/cached_products/poundwholesale-co-uk_products_cache.json L1-L22
[ { "title": "'Welcome' Wellies Door Mat", ..., "scraped_at": "2025-07-29T04:35:25.293789" }, ... ]