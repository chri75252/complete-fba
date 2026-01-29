# FBA Agent v4.3.0 - Root Cause Analysis & Suggested Fixes

**Date:** 2026-01-08 21:01 UTC+4  
**Status:** Issues Identified, Fixes Provided (NO EDITS MADE)

---

## EXPECTED MD REPORT SECTIONS

The MD report MUST contain these sections:

| Section | Definition |
|---------|------------|
| **VERIFIED - RECOMMENDED** | track=VERIFIED AND bucket=VERIFIED |
| **VERIFIED - AUDITED OUT** | track=VERIFIED AND bucket=FILTERED_OUT (excluded due to profitability) |
| **HIGHLY LIKELY - RECOMMENDED** | track=HIGHLY_LIKELY AND bucket=HIGHLY_LIKELY |
| **HIGHLY LIKELY - AUDITED OUT** | track=HIGHLY_LIKELY AND bucket=FILTERED_OUT (excluded due to profitability) |
| **NEEDS VERIFICATION** | bucket=NEEDS_VERIFICATION |
| **UNRELATED / NOT INCLUDED** | include_in_tables=False |

**Note:** "FILTERED_OUT" is the internal bucket name for products filtered by deterministic analysis.
"AUDITED OUT" is the display name for products that matched but were excluded due to profitability.

---

## ISSUE #1: render.py NaN Handling Bug

### Symptom
```
ValueError: cannot convert float NaN to integer
File: render.py, line 41, in _fmt_int
    return str(int(round(f)))
```

### Root Cause
The `_fmt_int()` function on line 32-41 doesn't check for NaN values before converting to int. When a row has NaN in the `sales` column, `float(value)` succeeds but `int(round(f))` fails because NaN cannot be converted to int.

### Location
`src/fba_agent/render.py` lines 32-41

### Suggested Fix (Diff Format)
```diff
 def _fmt_int(value: object) -> str:
     if value is None:
         return "-"
     try:
         f = float(value)
     except (TypeError, ValueError):
         return "-"
+    # Check for NaN - cannot convert to int
+    import math
+    if math.isnan(f):
+        return "-"
     if f.is_integer():
         return str(int(f))
     return str(int(round(f)))
```

---

## ISSUE #2: Providers Missing trace_path Parameter

### Symptom
```
GeminiProvider.__init__() got an unexpected keyword argument 'trace_path'
```

### Root Cause
In `providers/__init__.py` lines 166 and 179, `trace_path` is passed to GeminiProvider and MoonshotProvider constructors, but their `__init__` methods don't accept this parameter.

OpenAIProvider correctly accepts `trace_path`:
```python
def __init__(self, config: ProviderConfig, trace_path: str | None = None):
```

But GeminiProvider and MoonshotProvider only accept `config`:
```python
def __init__(self, config: ProviderConfig):  # Missing trace_path!
```

### Location
- `src/fba_agent/providers/gemini_provider.py` line 13
- `src/fba_agent/providers/moonshot_provider.py` line 13

### Suggested Fix (Diff Format)

**gemini_provider.py:**
```diff
 class GeminiProvider(BaseProvider):
     """Gemini LLM provider using OpenAI-compatible API."""

-    def __init__(self, config: ProviderConfig):
+    def __init__(self, config: ProviderConfig, trace_path: str | None = None):
         super().__init__(config)
+        self.set_trace_path(trace_path)
         self._client = None
```

**moonshot_provider.py:**
```diff
 class MoonshotProvider(BaseProvider):
     """Moonshot LLM provider."""

-    def __init__(self, config: ProviderConfig):
+    def __init__(self, config: ProviderConfig, trace_path: str | None = None):
         super().__init__(config)
+        self.set_trace_path(trace_path)
         self._client = None
```

---

## ISSUE #3: Incorrect Section Names in render.py

### Symptom
The MD report displays "FILTERED OUT / EXCLUDED" but should display "AUDITED OUT"

### Root Cause
In `render.py` lines 125-127 and 148-150, the section titles use "FILTERED OUT / EXCLUDED" terminology but the CORRECT terminology is "AUDITED OUT" for products that matched (VERIFIED/HIGHLY LIKELY) but were excluded due to profitability.

**Terminology clarification:**
- **FILTERED_OUT** = Internal bucket name for products filtered by deterministic analysis
- **AUDITED OUT** = Display name for matched products excluded due to profitability

### Location
`src/fba_agent/render.py` lines 125-127 and 148-150

### Suggested Fix (Diff Format)
```diff
     lines.append("## Summary Counts")
     lines.append("")
     lines.append(f"- VERIFIED - RECOMMENDED: {len(verified_rec)}")
-    lines.append(f"- VERIFIED - FILTERED OUT / EXCLUDED: {len(verified_fo)}")
+    lines.append(f"- VERIFIED - AUDITED OUT: {len(verified_fo)}")
     lines.append(f"- HIGHLY LIKELY - RECOMMENDED: {len(hl_rec)}")
-    lines.append(f"- HIGHLY LIKELY - FILTERED OUT / EXCLUDED: {len(hl_fo)}")
+    lines.append(f"- HIGHLY LIKELY - AUDITED OUT: {len(hl_fo)}")
     lines.append(f"- NEEDS VERIFICATION: {len(needs_ver)}")
     lines.append(f"- UNRELATED / NOT INCLUDED: {unrelated_count}")
     lines.append(f"- **TOTAL ANALYZED: {total}**")
```

```diff
     section("VERIFIED - RECOMMENDED", verified_rec)
-    section("VERIFIED - FILTERED OUT / EXCLUDED", verified_fo)
+    section("VERIFIED - AUDITED OUT", verified_fo)
     section("HIGHLY LIKELY - RECOMMENDED", hl_rec)
-    section("HIGHLY LIKELY - FILTERED OUT / EXCLUDED", hl_fo)
+    section("HIGHLY LIKELY - AUDITED OUT", hl_fo)
     section("NEEDS VERIFICATION", needs_ver)
```

---

## ISSUE #4: LLM Trace Logging Missing in Gemini/Moonshot Providers

### Symptom
Even if `trace_path` parameter is added, Gemini and Moonshot providers don't actually log to the trace file.

### Root Cause
OpenAIProvider has explicit trace logging code (lines 74-115):
```python
if self._trace_path:
    with open(self._trace_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(trace_entry) + "\n")
```

But GeminiProvider and MoonshotProvider have no such code.

### Location
- `src/fba_agent/providers/gemini_provider.py` - missing trace logging
- `src/fba_agent/providers/moonshot_provider.py` - missing trace logging

### Suggested Fix (Diff Format)

**gemini_provider.py - add after line 63:**
```diff
             content = response.choices[0].message.content
+            
+            # Log trace if enabled
+            if self._trace_path:
+                import json
+                from datetime import datetime
+                trace_entry = {
+                    "timestamp": datetime.now().isoformat(),
+                    "provider": "gemini",
+                    "model": self.current_model,
+                    "input": {"system": json_system[:500], "user": user[:500]},
+                    "output": {"content": content[:1000]},
+                }
+                with open(self._trace_path, "a", encoding="utf-8") as f:
+                    f.write(json.dumps(trace_entry) + "\n")
+            
             return self._parse_json(content)
```

---

## ISSUE #5: MD Report Not Generated Before AI Steps

### Symptom
We modified `iteration.py` to generate MD report before Step 1, but if the render fails (Issue #1), the entire AI pipeline breaks.

### Root Cause
In the new v4.3.0 code in `iteration.py` lines 225-285, the MD report generation is done BEFORE the try/except block for AI steps. If render fails, the exception propagates up and kills the run.

### Location
`src/fba_agent/iteration.py` lines 225-240

### Suggested Fix (Diff Format)
```diff
         if provider is not None:
             # ═══════════════════════════════════════════════════════════════
             # GENERATE MD REPORT FIRST (needed for AI steps to analyze)
             # ═══════════════════════════════════════════════════════════════
-            from fba_agent.render import render_phasea_report
-            report_content = render_phasea_report(
-                ledger,
-                input_file=current_config.supplier_id,
-                supplier=current_config.supplier_id,
-                generated_date=None,
-            )
-            
-            # Write iteration report
-            iteration_report_path = run_dir / f"iteration_{iter_num}_report.md"
-            iteration_report_path.write_text(report_content, encoding="utf-8")
-            print(f"✓ Generated iteration {iter_num} report for AI review")
+            try:
+                from fba_agent.render import render_phasea_report
+                report_content = render_phasea_report(
+                    ledger,
+                    input_file=current_config.supplier_id,
+                    supplier=current_config.supplier_id,
+                    generated_date=None,
+                )
+                
+                # Write iteration report
+                iteration_report_path = run_dir / f"iteration_{iter_num}_report.md"
+                iteration_report_path.write_text(report_content, encoding="utf-8")
+                print(f"✓ Generated iteration {iter_num} report for AI review")
+            except Exception as e:
+                print(f"⚠ MD report generation failed: {type(e).__name__}: {e}")
+                import traceback
+                traceback.print_exc()
+                report_content = None
+                iteration_report_path = None
```

---

## ISSUE #6: v4.3.0 Broke MD Report Generation Order (CRITICAL!)

### Symptom
My v4.3.0 changes moved MD report generation BEFORE Step 1, but it should be AFTER.

### Root Cause
The CORRECT original flow was:
```
1. Deterministic Analysis → LEDGER
2. Step 1 (Per-Row Adj) → Updates LEDGER with corrections
3. ▶▶ MD REPORT GENERATED ◀◀ (uses updated LEDGER from Step 1)
4. Step 2 (Comprehensive Adj) → Reads MD REPORT
5. Step 3 (Critique) → Reviews findings
```

My v4.3.0 changes INCORRECTLY changed this to:
```
1. Deterministic Analysis → LEDGER
2. ▶▶ MD REPORT GENERATED ◀◀ (WRONG! Before Step 1!)
3. Step 1 (Per-Row Adj) → Analyzes MD report
4. Step 2 (Comprehensive Adj) → Reads same MD REPORT
5. Step 3 (Critique)
```

This is WRONG because:
- Step 1 adjudication should update the LEDGER first
- MD report should reflect those updates
- Comprehensive adj reads the UPDATED report

### Location
`src/fba_agent/iteration.py` lines 225-288

### Suggested Fix (Diff Format)
Revert to original order - Step 1 BEFORE MD report generation:
```diff
         if provider is not None:
-            # ════════════════════════════════════════════════════════════════════════
-            # GENERATE MD REPORT FIRST (needed for AI steps to analyze)
-            # Per AI_LOGIC_PROPOSED_PLAN: Generate report BEFORE adjudication
-            # ════════════════════════════════════════════════════════════════════════
-            from fba_agent.render import render_phasea_report
-            report_content = render_phasea_report(...)
-            iteration_report_path.write_text(report_content)
-            
             # ════════════════════════════════════════════════════════════════════════
-            # STEP 1: Per-Row Adjudication FROM MD REPORT
+            # STEP 1: Per-Row Adjudication FROM LEDGER (ORIGINAL FLOW)
             # ════════════════════════════════════════════════════════════════════════
             try:
-                # Process MD report batches
-                batches = create_md_report_batches(report_content, batch_size=70)
+                # Process LEDGER candidates (original behavior)
+                from fba_agent.adjudication import select_candidates, run_adjudication
+                candidate_ids = select_candidates(ledger, evidence, current_config)
+                if candidate_ids:
+                    # ... original adjudication from ledger
                     
+            # ════════════════════════════════════════════════════════════════════════
+            # GENERATE MD REPORT AFTER STEP 1 (uses updated ledger)
+            # ════════════════════════════════════════════════════════════════════════
+            from fba_agent.render import render_phasea_report
+            report_content = render_phasea_report(ledger, ...)  # Uses UPDATED ledger
+            iteration_report_path.write_text(report_content)
+            
             # ════════════════════════════════════════════════════════════════════════
             # STEP 2: Comprehensive Adjudication
+            # Reads the MD REPORT (which now reflects Step 1 changes)
             # ════════════════════════════════════════════════════════════════════════
```

---

## ISSUE #7: Test Script Used Wrong Provider

### Symptom
Test script used `provider_name="gemini"` but .env has OPENAI_API_KEY configured.

### Root Cause
In `run_test.py`, I set:
```python
provider_name="gemini"  # WRONG!
```

But the .env file has:
```
OPENAI_API_KEY=sk-proj-...
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-5-mini
```

### Location
`run_test.py` line 36

### Suggested Fix
Use OpenAI or auto-detect from env:
```diff
         result = run_analysis(
             ...
-            provider_name="gemini",
+            provider_name="openai",  # Use OpenAI (configured in .env)
         )
```

---

## SUMMARY OF ALL ISSUES

| # | Issue | Severity | File | Root Cause |
|---|-------|----------|------|------------|
| 1 | NaN handling in _fmt_int() | **CRITICAL** | render.py:32-41 | Missing NaN check before int conversion |
| 2 | trace_path not accepted by providers | **HIGH** | gemini_provider.py:13, moonshot_provider.py:13 | Missing parameter in __init__ |
| 3 | Section names use wrong terminology | **MEDIUM** | render.py:125-127,148-150 | Should be "AUDITED OUT" not "FILTERED OUT / EXCLUDED" |
| 4 | Missing trace logging in providers | **LOW** | gemini_provider.py, moonshot_provider.py | No trace write code |
| 5 | MD report error kills AI pipeline | **MEDIUM** | iteration.py:225-240 | Missing try/except wrapper |
| **6** | **v4.3.0 broke MD report order** | **CRITICAL** | iteration.py:225-288 | **MD report generated BEFORE Step 1 (should be AFTER)** |
| 7 | Test script used wrong provider | **MEDIUM** | run_test.py:36 | Used "gemini" instead of "openai" |

---

## FIX ORDER (Recommended)

1. **Issue #6** (MD report order) - MUST REVERT - I broke the original flow
2. **Issue #1** (render.py NaN) - CRITICAL blocking bug
3. **Issue #2** (provider trace_path) - Required for AI features
4. **Issue #7** (test script provider) - Use OpenAI
5. **Issue #3** (AUDITED OUT terminology) - Display correctness
6. **Issue #5** (try/except wrapper) - Prevents cascading failures
7. **Issue #4** (trace logging) - Nice to have

---

**END OF ROOT CAUSE ANALYSIS**

*No edits were made per user instruction. Waiting for approval to apply fixes.*

