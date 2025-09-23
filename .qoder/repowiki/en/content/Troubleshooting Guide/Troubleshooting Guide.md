# Troubleshooting Guide

<cite>
**Referenced Files in This Document**   
- [CHROME_CDP_CONNECTIVITY_TROUBLESHOOTING_REPORT.md](file://CHROME_CDP_CONNECTIVITY_TROUBLESHOOTING_REPORT.md)
- [MEMORY_MANAGEMENT_ANALYSIS.md](file://MEMORY_MANAGEMENT_ANALYSIS.md)
- [comprehensive_state_corruption_analysis.md](file://memories/comprehensive_state_corruption_analysis.md)
- [critical_resume_logic_bug_location_found.md](file://memories/critical_resume_logic_bug_location_found.md)
- [chrome_cdp_diagnostic.py](file://chrome_cdp_diagnostic.py)
- [fixed_enhanced_state_manager.py](file://utils/fixed_enhanced_state_manager.py)
- [system_monitor.py](file://tools/system_monitor.py)
- [supplier_authentication_service.py](file://tools/supplier_authentication_service.py)
- [state_validation.md](file://OUTPUTS/DIAGNOSTICS/state_validation.md)
- [run_custom_poundwholesale.py](file://run_custom_poundwholesale.py)
- [logs/debug/run_custom_poundwholesale_20250904_223041.txt](file://logs/debug/run_custom_poundwholesale_20250904_223041.txt)
- [processing_states/poundwholesale_co_uk_processing_state.json](file://processing_states/poundwholesale_co_uk_processing_state.json)
- [diagnostics/state_events/state_1757010996.json](file://diagnostics/state_events/state_1757010996.json)
- [diagnostics/state_timeline_analysis.txt](file://diagnostics/state_timeline_analysis.txt)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Chrome Debug Port Conflicts](#chrome-debug-port-conflicts)
3. [Memory Management Issues](#memory-management-issues)
4. [Authentication Failures](#authentication-failures)
5. [State Management Problems](#state-management-problems)
6. [Debug Log and Diagnostic Report Interpretation](#debug-log-and-diagnostic-report-interpretation)
7. [Performance Optimization for Long-Running Sessions](#performance-optimization-for-long-running-sessions)
8. [Recovery from System Crashes](#recovery-from-system-crashes)
9. [Conclusion](#conclusion)

## Introduction
This guide provides comprehensive troubleshooting procedures for the Amazon FBA Agent System, focusing on diagnosing and resolving common operational issues. It covers critical areas including Chrome CDP connectivity, memory pressure, authentication failures, and state management integrity. The documentation leverages system terminology such as 'processing state corruption', 'browser health monitoring', and 'state validation' to ensure alignment with the codebase's conceptual framework. Practical diagnostic commands and log analysis techniques are included to enable rapid root cause identification and resolution.

## Chrome Debug Port Conflicts

Chrome Debug Protocol (CDP) port conflicts occur when multiple instances attempt to bind to the same debugging port, typically 9222. This prevents browser initialization and halts agent execution. The system uses `chrome_cdp_diagnostic.py` for connectivity validation and `chrome_quick_fix.py` for automated resolution.

To diagnose port conflicts, execute:
```bash
netstat -ano | findstr :9222
```

If a process is occupying the port, identify it using:
```bash
tasklist | findstr <PID>
```

Terminate the conflicting process with:
```bash
taskkill /PID <PID> /F
```

Alternatively, reconfigure the debug port in `system_config.json` by modifying the `chrome_debug_port` parameter. The `run_custom_poundwholesale.py` script accepts a `--debug-port` argument to override defaults dynamically.

Persistent port conflicts may indicate improper browser shutdowns. Review `logs/debug/run_custom_poundwholesale_20250904_223041.txt` for ungraceful exit patterns and verify `browser_circuit_breaker.py` is active to enforce cleanup.

**Section sources**
- [CHROME_CDP_CONNECTIVITY_TROUBLESHOOTING_REPORT.md](file://CHROME_CDP_CONNECTIVITY_TROUBLESHOOTING_REPORT.md)
- [chrome_cdp_diagnostic.py](file://chrome_cdp_diagnostic.py)
- [run_custom_poundwholesale.py](file://run_custom_poundwholesale.py)

## Memory Management Issues

Memory pressure issues arise during long-running extractions, particularly with large product catalogs. The system employs `system_monitor.py` for real-time memory tracking and triggers warnings via `MEMORY_MANAGEMENT_ANALYSIS.md` when thresholds are exceeded.

Key indicators in logs include:
- `MemoryPressureWarning: usage > 85%`
- `GCEvent: forced collection due to allocation failure`
- `BrowserHealthMonitor: tab crash detected`

Interpret memory monitoring logs by correlating timestamps with processing state transitions in `diagnostics/state_events/`. Sudden memory spikes often coincide with category transitions or manifest loading.

To mitigate memory issues:
1. Adjust `memory_cleanup_interval` in `system_config.json`
2. Enable `aggressive_cache_cleanup` in high-memory-pressure environments
3. Reduce `concurrent_page_loads` to limit browser tab accumulation

The `data_integrity_guardian.py` module enforces memory-safe state serialization, preventing corruption during high-load scenarios. Validate memory behavior using `run_system_audit_simple.py --memory-profile`.

**Section sources**
- [MEMORY_MANAGEMENT_ANALYSIS.md](file://MEMORY_MANAGEMENT_ANALYSIS.md)
- [system_monitor.py](file://tools/system_monitor.py)
- [data_integrity_guardian.py](file://utils/data_integrity_guardian.py)

## Authentication Failures

Authentication failures occur when the `supplier_authentication_service.py` cannot validate credentials or establish browser session trust. Common causes include invalid credentials, browser fingerprint mismatches, or network-level blocking.

To troubleshoot:
1. Verify credentials in `config/supplier_configs/www.poundwholesale.co.uk.json`
2. Check browser accessibility by launching Chrome manually with `--remote-debugging-port=9222`
3. Inspect `logs/debug/run_custom_poundwholesale_20250904_223041.txt` for `AuthFailedEvent` entries

The system performs automated credential validation through `security_checks.py`. If authentication succeeds in isolation but fails in the agent context, investigate proxy or user-agent spoofing configurations.

Browser health monitoring detects authentication-related tab crashes and triggers automatic retries with `browser_circuit_breaker.py`. Persistent failures should prompt a review of `CHROME_CDP_CONNECTIVITY_TROUBLESHOOTING_REPORT.md` for underlying connectivity issues.

**Section sources**
- [supplier_authentication_service.py](file://tools/supplier_authentication_service.py)
- [security_checks.py](file://tools/security_checks.py)
- [logs/debug/run_custom_poundwholesale_20250904_223041.txt](file://logs/debug/run_custom_poundwholesale_20250904_223041.txt)

## State Management Problems

State management issues manifest as inaccurate progress tracking or resumption failures, often due to processing state corruption. The system uses `fixed_enhanced_state_manager.py` to serialize state to `processing_states/poundwholesale_co_uk_processing_state.json`.

Common symptoms:
- Resumption from incorrect category
- Duplicate processing of completed categories
- Missing progress in `enhanced_category_tracking.json`

Diagnose using `state_validation.md`, which details the state validation protocol. Compare `processing_states/latest/11strun.json` with archived states in `processing_states/ARCHIVED/` to detect divergence.

The root cause of resumption failures was identified in `critical_resume_logic_bug_location_found.md` as improper pointer serialization. The fix ensures atomic writes via `atomic_file_operations.py` and validates state integrity before resumption.

To resolve state corruption:
1. Restore from a known-good state in `diagnostics/baseline_20250905_110101/`
2. Run `python critical_fixes_implementation.py --repair-state`
3. Validate with `python config_usage_analyzer.py --validate-state`

**Section sources**
- [fixed_enhanced_state_manager.py](file://utils/fixed_enhanced_state_manager.py)
- [comprehensive_state_corruption_analysis.md](file://memories/comprehensive_state_corruption_analysis.md)
- [critical_resume_logic_bug_location_found.md](file://memories/critical_resume_logic_bug_location_found.md)
- [processing_states/poundwholesale_co_uk_processing_state.json](file://processing_states/poundwholesale_co_uk_processing_state.json)

## Debug Log and Diagnostic Report Interpretation

Effective troubleshooting requires interpreting debug logs and diagnostic reports. The system generates structured logs in `logs/debug/` and diagnostic bundles in `diagnostics/`.

Key log patterns:
- `StateTransitionEvent: from=CategoryA to=CategoryB` – Normal progression
- `ProcessingStateCorruptionDetected` – Critical state error
- `BrowserHealthMonitor: restart initiated` – Recovery action

Diagnostic reports in `OUTPUTS/DIAGNOSTICS/` provide system snapshots:
- `state_validation.json` – Current state integrity assessment
- `workflow_diff.json` – Deviation from expected execution path
- `code_map.json` – Dynamic configuration analysis

Use `diagnostics/state_timeline_analysis.txt` to reconstruct execution sequences. Each entry in `diagnostics/state_events/` represents a state checkpoint, enabling timeline-based forensics.

For example, to trace a resumption failure:
```bash
grep "resumption_pointer" diagnostics/state_events/state_*.json
```

Correlate findings with `capture_resume_logs.py` output for comprehensive analysis.

**Section sources**
- [state_validation.md](file://OUTPUTS/DIAGNOSTICS/state_validation.md)
- [diagnostics/state_timeline_analysis.txt](file://diagnostics/state_timeline_analysis.txt)
- [diagnostics/state_events/state_1757010996.json](file://diagnostics/state_events/state_1757010996.json)

## Performance Optimization for Long-Running Sessions

Long-running sessions require careful resource management to prevent degradation. The system implements several optimization strategies documented in `SMART_MEMORY_MANAGEMENT_UPDATE_SUMMARY.md`.

Key optimization levers:
- `chunking_execution_tracer.py` – Splits large categories into manageable chunks
- `url_cache_filter.py` – Reduces redundant URL processing
- `data_store.py` – Optimizes in-memory data structures

To optimize performance:
1. Adjust `chunk_size` in `system_config.json` for balanced processing
2. Enable `incremental_save` to reduce memory pressure
3. Monitor `CATEGORY_TRACKING_ISSUE_ANALYSIS.md` for inefficient navigation patterns

The `comprehensive_execution_trace.py` tool provides performance profiling. Run:
```bash
python comprehensive_execution_trace.py --target poundwholesale_co_uk
```

This generates timing metrics for each processing phase, highlighting bottlenecks.

For extended runs, use `temp_integrated_workflow_runner.py` with `--checkpoint-interval` to ensure recoverability without sacrificing throughput.

**Section sources**
- [chunking_execution_tracer.py](file://tools/chunking_execution_tracer.py)
- [url_cache_filter.py](file://utils/url_cache_filter.py)
- [comprehensive_execution_trace.py](file://tools/comprehensive_execution_trace.py)

## Recovery from System Crashes

System crashes require structured recovery to maintain data integrity. The system implements crash resilience through atomic state updates and diagnostic snapshots.

Recovery procedure:
1. Identify crash point from `logs/debug/run_custom_poundwholesale_*.txt`
2. Validate state file integrity using `python data_integrity_guardian.py --verify`
3. Resume with `python run_custom_poundwholesale.py --resume-from-last`

The `git_checkpoint.py` tool provides versioned state backups. In cases of irrecoverable corruption, restore from the latest checkpoint in `diagnostics/session_*/backups/`.

Post-crash analysis should examine:
- `diagnostics/run_repro_20250904_223030/` – Reproduction environment
- `diagnostics/final_proof_20250904_231938/logs/stdout.txt` – Final execution trace
- `AUDIT_RUN1_FINAL_STATE.json` – Pre-crash state snapshot

The `COMPREHENSIVE_SYSTEM_FIXES.py` script includes a recovery mode that auto-detects and repairs common post-crash issues.

**Section sources**
- [data_integrity_guardian.py](file://utils/data_integrity_guardian.py)
- [git_checkpoint.py](file://tools/git_checkpoint.py)
- [COMPREHENSIVE_SYSTEM_FIXES.py](file://COMPREHENSIVE_SYSTEM_FIXES.py)

## Conclusion
This troubleshooting guide provides a systematic approach to diagnosing and resolving common issues in the Amazon FBA Agent System. By leveraging built-in diagnostic tools, understanding log patterns, and applying targeted fixes, operators can maintain system reliability and data integrity. Key focus areas include Chrome CDP connectivity, memory management, authentication stability, and state validation. The documented procedures enable rapid recovery from failures and optimization of long-running operations, ensuring robust performance in production environments.