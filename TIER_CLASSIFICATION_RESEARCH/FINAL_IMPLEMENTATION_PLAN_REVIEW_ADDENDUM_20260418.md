# Final Implementation Plan — Review Addendum (2026-04-18)

## Scope of this addendum

This file is an implementation review addendum for the copied plan at:

- `.sisyphus/plans/FINAL_IMPLEMENTATION_PLAN.md`

It does **not** replace that plan.

It records the final constraints and clarifications that should govern implementation so the work remains surgical and does not reopen already-settled business decisions.

---

## 1. Confirmed accepted plan decisions

The following points from the copied plan are accepted and should **not** be re-litigated during implementation:

### 1.1 Exact-EAN rows remain Tier 1

This is now a user-level business rule, not an open modeling question.

Evidence in copied plan:
- `.sisyphus/plans/FINAL_IMPLEMENTATION_PLAN.md:37`
- `.sisyphus/plans/FINAL_IMPLEMENTATION_PLAN.md:38`

### 1.2 `SUSPICIOUS_TITLE_MISMATCH` remains non-demoting

This flag is acceptable as an audit signal only. It must not demote exact-EAN rows.

Evidence in copied plan:
- `.sisyphus/plans/FINAL_IMPLEMENTATION_PLAN.md:235`
- `.sisyphus/plans/FINAL_IMPLEMENTATION_PLAN.md:239`

### 1.3 `TIER_1_B_AUDIT_OUT` does not recalculate NetProfit during classify stage

The classify stage only flags these rows for audit. Net profit adjustment is intentionally deferred.

Evidence in copied plan:
- `.sisyphus/plans/FINAL_IMPLEMENTATION_PLAN.md:245`
- `.sisyphus/plans/FINAL_IMPLEMENTATION_PLAN.md:246`
- `.sisyphus/plans/FINAL_IMPLEMENTATION_PLAN.md:535`

### 1.4 Wording fixes already accepted

The shift from “calibrated posterior” to “probability estimate” is correct and sufficient.

Evidence in copied plan:
- `.sisyphus/plans/FINAL_IMPLEMENTATION_PLAN.md:108`

### 1.5 No extra classifier experiment campaign is recommended for points 1 / 5 / 7 / 8

At this stage, no better evidenced alternative was identified that justifies expanding scope into another model-comparison project.

---

## 2. One remaining implementation-area concern: analysis concurrency

## 2.1 What the risk is

The real overlap risk is centered on the analysis classification path, not the whole dashboard.

Only `/api/analysis` classifies rows:
- `dashboard_v2_redesign/api.py:543`
- `dashboard_v2_redesign/api.py:601`

The following routes do **not** classify rows:
- `/api/metrics/{supplier}` → `dashboard_v2_redesign/api.py:239`
- `/api/reports/{supplier}` → `dashboard_v2_redesign/api.py:712`
- `/api/categories/{supplier}`

So the concurrency concern is specifically about overlapping analysis requests touching shared probabilistic matcher state.

---

## 2.2 Why frontend abort alone is not enough

The frontend aborts and restarts analysis requests:
- `dashboard_v2_redesign/static/js/app.js:1077`
- `dashboard_v2_redesign/static/js/app.js:1093`

But that only aborts the browser request. It does not guarantee that a previous server-side request has already stopped classifying rows.

That means a shared mutable matcher could still be overwritten by a second overlapping analysis request.

---

## 2.3 Proof artifact

Generated evidence:
- `TIER_CLASSIFICATION_RESEARCH/concurrency_matcher_demo.py`
- `TIER_CLASSIFICATION_RESEARCH/concurrency_matcher_demo_report.md`

Observed result:

```text
global: expected=report_B got=report_B OK
global: expected=report_A got=report_B CROSS-CONTAMINATED
threadlocal: expected=report_B got=report_B OK
threadlocal: expected=report_A got=report_A OK
explicit: expected=report_B got=report_B OK
explicit: expected=report_A got=report_A OK
```

Interpretation:
- single global matcher is unsafe
- report-keyed + thread-local is acceptable
- explicit request-local matcher passing is also acceptable

---

## 3. Required addendum to implementation

The copied plan’s matcher fix is directionally acceptable, but one more layer should be added to make the implementation safer in actual dashboard use.

## Recommended surgical addition

### Add a single active analysis guard

This should be implemented in:
- `dashboard_v2_redesign/api.py`

Purpose:
- prevent overlapping `/api/analysis` executions
- return a controlled response if a second analysis is triggered while one is still running

Minimal design:

```python
_analysis_state = {
    "active": False,
    "job_id": None,
    "cancel_requested": False,
}
_analysis_state_lock = threading.Lock()
```

Required behavior:
- acquire lock at analysis start
- reject second concurrent analysis with `409`
- release lock in `finally`
- support cancellation flag checks during row loop

This is safer than relying only on client-side watcher/abort behavior.

---

### Add Cancel Analysis support

Backend:
- add a lightweight `/api/analysis/cancel` endpoint

Frontend:
- add `Cancel Analysis` button
- abort current fetch and request server-side cancel

This keeps the UX practical while preserving correctness.

---

### Disable only analysis-affecting controls while analysis is running

Do **not** freeze the entire dashboard unnecessarily.

Disable controls that can retrigger `/api/analysis`, such as:
- Apply button
- supplier selector
- lineage selector
- run selector
- analysis report selector
- analysis filters
- analysis sort inputs

This is a safer and more surgical approach than broad “watcher” logic.

---

## 4. UI changes from the copied plan remain mandatory

These are still required and should not be skipped:

### 4.1 Tier filter update
- current hardcoded legacy filter: `dashboard_v2_redesign/templates/index.html:782`
- copied-plan change: `.sisyphus/plans/FINAL_IMPLEMENTATION_PLAN.md:475`

### 4.2 Tier 1 count aggregation
- current hardcoded count: `dashboard_v2_redesign/static/js/app.js:1105`
- copied-plan change: `.sisyphus/plans/FINAL_IMPLEMENTATION_PLAN.md:491`

### 4.3 Expanded `tiers` dict in `process_report()`
- copied-plan change: `.sisyphus/plans/FINAL_IMPLEMENTATION_PLAN.md:377`

### 4.4 Corrected API matcher preparation placement
- copied-plan corrected section: `.sisyphus/plans/FINAL_IMPLEMENTATION_PLAN.md:423`

---

## 5. Final recommendation

Implementation should proceed using:

1. the copied plan at `.sisyphus/plans/FINAL_IMPLEMENTATION_PLAN.md`
2. plus the concurrency/control addendum in this file

### In plain terms

- Keep the copied classifier plan direction
- Do not reopen exact-EAN demotion debates
- Do not recalc NetProfit in classify stage for T1_B
- Do not use a single global matcher
- Add a single active analysis guard + cancel flow
- Lock only analysis-affecting controls while analysis is in flight

That is the most surgical and safest execution path.
