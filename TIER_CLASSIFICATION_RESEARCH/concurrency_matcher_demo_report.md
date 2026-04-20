# Matcher Concurrency Demo Report

## Purpose
Show, with a minimal reproducible script, why a single mutable global matcher is unsafe when two overlapping requests prepare different report-specific matchers.

## Script
`TIER_CLASSIFICATION_RESEARCH/concurrency_matcher_demo.py`

## Result

```text
global: expected=report_B got=report_B OK
global: expected=report_A got=report_B CROSS-CONTAMINATED
threadlocal: expected=report_B got=report_B OK
threadlocal: expected=report_A got=report_A OK
explicit: expected=report_B got=report_B OK
explicit: expected=report_A got=report_A OK
```

## Interpretation

- **Single global matcher**: unsafe. Request/report A can prepare a matcher, request/report B can overwrite it, and then A classifies with B's matcher.
- **Report-keyed dict + thread-local active report**: safe for overlapping requests in this demo.
- **Explicit matcher passed through call chain**: also safe, and simpler to reason about than shared mutable global state.

## Why this matters to the dashboard/API

The probabilistic prototype currently uses `_GLOBAL_MATCHER` in:
- `FINAL STALE/agent analyses/initial_probabilistic_implementation_package/probabilistic_matcher_prototype.py:346`
- `FINAL STALE/agent analyses/initial_probabilistic_implementation_package/probabilistic_matcher_prototype.py:359`

The dashboard analysis endpoint processes one selected report per request, but overlapping requests can still occur from:
- repeated manual refreshes,
- tab switching,
- auto-refresh / abort-restart behavior,
- two browser tabs hitting different reports.

The current frontend already aborts and restarts requests on analysis reload:
- `dashboard_v2_redesign/static/js/app.js:1077`
- `dashboard_v2_redesign/static/js/app.js:1093`

That does not eliminate overlap risk at the server boundary; it only reduces it on the client side.

## Conclusion

If the probabilistic plan is implemented, a single mutable global matcher should not be used. At minimum, matcher state should be report-keyed. Preferably, the prepared matcher should be request-local / explicitly passed.
