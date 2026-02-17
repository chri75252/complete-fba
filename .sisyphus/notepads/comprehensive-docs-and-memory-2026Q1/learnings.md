## Memory Sentinel Implementation (2026-02-10)
- Implemented  to detect drift between code and Supermemory.
- Scans , , , and  for changes using SHA256.
- Baseline stored in .
- Supports  (default) and  flags.
- Exit code 1 on drift, 0 on no drift.
- Successfully verified drift detection by modifying .
## Supermemory Granularization Learnings - 2026-02-10
- Successfully transformed 28 coarse memories into 90 granular memories across project-config, architecture, learned-pattern, and error-solution categories.
- Pattern identified: Use specific file and line number anchors (e.g., utils/fixed_enhanced_state_manager.py#L264) for high-precision retrieval.
- Lesson: Parallel supermemory(add) calls require strict parameter checking to avoid syntax errors in batches.
- Retrievability confirmed for key concepts: control plane jobs, configuration paths, and chat safety patterns.
## Memory Sentinel Implementation (2026-02-10)
- Implemented `utils/memory_sentinel.py` to detect drift between code and Supermemory.
- Scans `config/`, `tools/`, `control_plane/`, and `utils/` for changes using SHA256.
- Baseline stored in `OUTPUTS/DIAGNOSTICS/memory_baseline.json`.
- Supports `--check` (default) and `--update` flags.
- Exit code 1 on drift, 0 on no drift.
- Successfully verified drift detection by modifying `config/system_config.json`.

## 2026-02-10: Comprehensive Workflow Documentation
- **Architecture**: Confirmed the Three Surface Model (Classic, Dashboard, Control Plane).
- **Config Precedence**: Validated that  prioritizes  env var over .
- **Data Flow**: Verified the standardized structure of  for cached products, Amazon data, linking maps, and financial reports.
- **Workflow Interleaving**: Hybrid mode is the default, allowing for immediate financial feedback during extraction.

## 2026-02-10: Comprehensive Workflow Documentation
- **Architecture**: Confirmed the Three Surface Model (Classic, Dashboard, Control Plane).
- **Config Precedence**: Validated that `SystemConfigLoader` prioritizes `FBA_SYSTEM_CONFIG_PATH` env var over `system_config.json`.
- **Data Flow**: Verified the standardized structure of `OUTPUTS/` for cached products, Amazon data, linking maps, and financial reports.
- **Workflow Interleaving**: Hybrid mode is the default, allowing for immediate financial feedback during extraction.

- **Doc/Code Drift Patterns**:
    - Configuration fields in JSON (like CDP port) are often shadowed by hard-coded defaults in code or runner scripts.
    - Dashboard documentation lags behind feature development (e.g., Operator/Chat tabs).
    - Supplier onboarding automation (Wizard) is prone to naming inconsistencies that ripple into workflow execution errors.
    - AI-gated modules (Amazon Extractor) can cause unexpected crashes in supposedly "minimal" scripts (Product Refresh) if the environment is not fully configured.
