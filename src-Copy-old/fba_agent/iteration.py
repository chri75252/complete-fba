"""Iteration loop controller.

This module manages the iterative refinement loop:
1. Run analysis (iteration 1)
2. Check if another iteration is needed
3. If yes: apply adjustments, re-run (iteration 2)
4. Run regression guard
5. Finalize or produce DRAFT

Iteration triggers:
- Gate failure (correctable)
- Critique recommends apply_and_rerun
- Large anomaly signals
- Regression blocked (may need adjustment)

Stop conditions:
- All gates pass
- Critique recommends finalize
- Max iterations reached
- Regression guard passes
"""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pandas as pd

from fba_agent.adjustments import apply_adjustments, count_applied
from fba_agent.anomalies import detect_anomalies
from fba_agent.types import IterationResult, MergedConfig

if TYPE_CHECKING:
    from fba_agent.providers import BaseProvider


def should_run_next_iteration(
    current_iter: int,
    max_iterations: int,
    validation_passed: bool,
    critique_action: str | None,
    anomaly_summary: dict | None,
    adjustments_applied: int = 0,
) -> tuple[bool, str]:
    """
    Decide whether to run another iteration.
    
    Args:
        current_iter: Current iteration number (1-indexed)
        max_iterations: Maximum allowed iterations
        validation_passed: Whether current iteration passed validation
        critique_action: Recommended action from critique ("finalize", "apply_and_rerun", "block")
        anomaly_summary: Anomaly detection results
        adjustments_applied: Number of adjustments applied this iteration
    
    Returns:
        Tuple of (should_run, reason)
    """
    # Already at max
    if current_iter >= max_iterations:
        return False, f"Reached max iterations ({max_iterations})"
    
    # If validation failed and is correctable, run again
    if not validation_passed:
        return True, "Validation failed — attempting correction"
    
    # If critique recommends rerun with changes
    if critique_action == "apply_and_rerun" and adjustments_applied > 0:
        return True, f"Critique recommended rerun with {adjustments_applied} adjustments"
    
    # If critique explicitly blocks
    if critique_action == "block":
        return False, "Critique blocked — manual review required"
    
    # If large anomaly signals
    if anomaly_summary:
        has_significant = anomaly_summary.get("has_significant_anomalies", False)
        if has_significant and current_iter == 1:
            return True, "Significant anomalies detected — running refinement iteration"
    
    # Default: no need for another iteration
    return False, "All conditions satisfied — ready to finalize"


def build_iteration_result(
    iteration_number: int,
    ledger: pd.DataFrame,
    evidence: list[dict],
    validation_passed: bool,
    validation_errors: list[str],
    config: MergedConfig,
    anomaly_summary: dict | None = None,
    critique: Any = None,
    adjudication_results: list = None,
) -> IterationResult:
    """Build an IterationResult from iteration outputs."""
    return IterationResult(
        iteration_number=iteration_number,
        ledger=ledger,
        evidence=evidence,
        validation_passed=validation_passed,
        validation_errors=validation_errors,
        anomaly_summary=anomaly_summary or {},
        critique=critique,
        adjudication_results=adjudication_results or [],
        config_applied={
            "supplier_id": config.supplier_id,
            "fee_rate": config.fee_rate,
            "title_match_threshold": config.title_match_threshold,
            "naming": config.naming.__dict__,
        },
    )


def iteration_result_to_dict(result: IterationResult) -> dict:
    """Convert iteration result to serializable dict."""
    d = {
        "iteration_number": result.iteration_number,
        "validation_passed": result.validation_passed,
        "validation_errors": result.validation_errors,
        "anomaly_summary": result.anomaly_summary,
        "config_applied": result.config_applied,
        "adjudication_count": len(result.adjudication_results),
    }
    
    # Add critique if present
    if result.critique:
        d["critique"] = {
            "recommended_action": result.critique.recommended_action,
            "high_severity_issues_count": len(result.critique.high_severity_issues),
            "proposed_changes_count": len(result.critique.proposed_changes),
        }
    
    return d


def select_best_iteration(iterations: list[IterationResult]) -> IterationResult:
    """
    Select the best iteration to use for final output.
    
    Priority:
    1. Last iteration that passed validation
    2. Last iteration overall (if none passed)
    """
    # Find iterations that passed validation
    passed = [i for i in iterations if i.validation_passed]
    
    if passed:
        return passed[-1]  # Return last passing iteration
    
    return iterations[-1]  # Return last overall


def run_iteration_loop(
    df: pd.DataFrame,
    config: MergedConfig,
    max_iterations: int,
    run_dir: Path,
    memory_dir: Path,
    provider: "BaseProvider | None" = None,
    brand_aliases: dict[str, str] | None = None,
    analyze_fn: Any = None,
    validate_fn: Any = None,
    past_ledger_path: Path | str | None = None,  # NEW: Path to past ledger for AI critique comparison
) -> tuple[IterationResult, bool, list[IterationResult]]:
    """
    Run the iteration loop.
    
    This is the main entry point for iterative analysis.
    
    Args:
        df: Normalized DataFrame with stable_key
        config: Initial merged configuration
        max_iterations: Maximum iterations (default: 2)
        run_dir: Run output directory
        memory_dir: Memory directory
        provider: Optional LLM provider for AI features
        brand_aliases: Brand alias mappings
        analyze_fn: Analysis function (for dependency injection)
        validate_fn: Validation function (for dependency injection)
    
    Returns:
        Tuple of (best_iteration, all_gates_passed, all_iterations)
    """
    # Late imports to avoid circular dependencies
    if analyze_fn is None:
        from fba_agent.analysis import analyze_all_rows
        analyze_fn = analyze_all_rows
    
    if validate_fn is None:
        from fba_agent.validate import validate_coverage, validate_profit
        def validate_fn(ledger, original_df):
            cov = validate_coverage(ledger, original_df)
            prof = validate_profit(ledger)
            return cov.passed and prof.passed, cov.errors + prof.errors
    
    if brand_aliases is None:
        brand_aliases = {}
    
    iterations: list[IterationResult] = []
    current_config = config
    current_brand_aliases = brand_aliases.copy()
    
    for iter_num in range(1, max_iterations + 1):
        # Create iteration directory
        iter_dir = run_dir / f"iter_{iter_num}"
        iter_dir.mkdir(parents=True, exist_ok=True)
        
        # Run analysis
        ledger, evidence = analyze_fn(df, current_config, brand_aliases=current_brand_aliases)
        
        # Run validation
        validation_passed, validation_errors = validate_fn(ledger, df)
        
        # Detect anomalies
        anomaly_summary = detect_anomalies(ledger, evidence).to_dict()
        
        # Run AI features if provider available
        critique = None
        adjudication_results = []
        comprehensive_adj_result = {}
        
        if provider is not None:
            # STEP 1: Run adjudication (separate try/except so failure doesn't kill other AI steps)
            try:
                from fba_agent.adjudication import select_candidates, run_adjudication
                candidate_ids = select_candidates(ledger, evidence, current_config)
                if candidate_ids:
                    # Build candidate data
                    candidates = []
                    for row_id in candidate_ids[:99]:  # Capped at 99 (3 batches of 33 rows)
                        row_match = ledger[ledger["row_id"] == row_id]
                        if len(row_match) > 0:
                            row = row_match.iloc[0].to_dict()
                            candidates.append(row)
                    
                    if candidates:
                        print(f"▶ Running AI adjudication on {len(candidates)} candidates...")
                        adjudication_results = run_adjudication(candidates, provider)
                        print(f"✓ AI adjudication complete: {len(adjudication_results)} results")
                        
                        # APPLY ADJUDICATION RESULTS TO LEDGER
                        if adjudication_results:
                            from fba_agent.adjustments import apply_adjudication_to_ledger
                            ledger, adjudication_applied = apply_adjudication_to_ledger(
                                ledger, 
                                adjudication_results
                            )
                            if adjudication_applied > 0:
                                print(f"✓ Applied {adjudication_applied} adjudication upgrades to ledger")
            except Exception as e:
                print(f"⚠ AI Adjudication failed: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
            
            # STEP 2: Comprehensive adjudication (RUNS BEFORE CRITIQUE so critique can review findings)
            try:
                # Generate iteration report first (needed for comprehensive review)
                from fba_agent.render import render_phasea_report
                report_content = render_phasea_report(
                    ledger,
                    input_file=current_config.supplier_id,
                    supplier=current_config.supplier_id,
                    generated_date=None,
                )
                
                # Write temporary iteration report
                iteration_report_path = run_dir / f"iteration_{iter_num}_report.md"
                iteration_report_path.write_text(report_content, encoding="utf-8")
                print(f"✓ Generated iteration {iter_num} report for comprehensive review")
                
                # Run comprehensive adjudication (reads FULL report)
                print(f"▶ Running comprehensive adjudication on full report...")
                from fba_agent.comprehensive_adjudication import run_comprehensive_adjudication
                from fba_agent.adjudication_apply import (
                    apply_adjudication_recategorizations,
                    log_adjudication_summary,
                )
                
                # Get source excel path from config if available
                source_path = getattr(current_config, 'input_path', '') or ''
                
                comprehensive_adj_result = run_comprehensive_adjudication(
                    report_path=iteration_report_path,
                    ledger=ledger,
                    source_excel_path=source_path,
                    config=current_config,
                    provider=provider,
                )
                
                # Log summary
                log_adjudication_summary(comprehensive_adj_result)
                
                # Apply recategorizations to ledger
                recategorizations = comprehensive_adj_result.get("recategorizations", [])
                if recategorizations:
                    ledger, comp_adj_applied = apply_adjudication_recategorizations(
                        ledger,
                        recategorizations
                    )
                    print(f"✓ Applied {comp_adj_applied} comprehensive adjudication recategorizations")
                    
            except Exception as e:
                print(f"⚠ Comprehensive adjudication failed: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                comprehensive_adj_result = {"error": str(e)}
            
            # STEP 3: Run critique (AFTER comprehensive adjudication, so it can review findings)
            try:
                from fba_agent.critique import build_critique_inputs, run_critique
                print(f"▶ Running AI critique (with comprehensive adjudication findings)...")
                critique_inputs = build_critique_inputs(
                    summary={"input_file": "", "supplier": current_config.supplier_id},
                    ledger=ledger,
                    evidence=evidence,
                    anomaly_summary=anomaly_summary,
                    past_ledger_path=past_ledger_path,
                    comprehensive_adj_findings=comprehensive_adj_result,  # NEW: Pass findings to critique
                )
                critique = run_critique(critique_inputs, provider)
                print(f"✓ AI critique complete: recommended_action={critique.recommended_action}")
            except Exception as e:
                print(f"⚠ AI Critique failed: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
        
        # Build iteration result
        iter_result = build_iteration_result(
            iteration_number=iter_num,
            ledger=ledger,
            evidence=evidence,
            validation_passed=validation_passed,
            validation_errors=validation_errors,
            config=current_config,
            anomaly_summary=anomaly_summary,
            critique=critique,
            adjudication_results=adjudication_results,
        )
        iterations.append(iter_result)
        
        # Decide whether to run another iteration
        critique_action = critique.recommended_action if critique else None
        adjustments_applied = 0
        
        # Apply adjustments if critique recommends
        if critique and critique.proposed_changes:
            current_config, current_brand_aliases, logs = apply_adjustments(
                current_config,
                critique.proposed_changes,
                current_brand_aliases,
            )
            adjustments_applied = count_applied(logs)
        
        should_continue, reason = should_run_next_iteration(
            current_iter=iter_num,
            max_iterations=max_iterations,
            validation_passed=validation_passed,
            critique_action=critique_action,
            anomaly_summary=anomaly_summary,
            adjustments_applied=adjustments_applied,
        )
        
        if not should_continue:
            break
    
    # Select best iteration
    best = select_best_iteration(iterations)
    all_passed = best.validation_passed
    
    return best, all_passed, iterations
