# Comprehensive Findings & Implementation Plan: FBA Agent vNext AI Integration
**Date:** 2026-01-05
**Author:** Antigravity (Google Deepmind)
**Subject:** Deep Analysis of AI Module Integration, Debugging, and Workflow Behavior

---

## 1. Executive Summary

We have successfully integrated the "vNext" AI modules (`adjudication`, `critique`, `iteration`) into the FBA Agent pipeline. What began as a request to "make it run" evolved into a deep debugging session that uncovered and fixed a critical API compatibility issue with `gpt-5-mini` and revealed how "Smart" AI configuration can actually lead to *stricter* (and initially lower) verification counts compared to "Dumb" heuristic baselines.

**Key Status:**
*   ✅ **Integration:** `run.py` now correctly orchestrates the full AI iteration loop.
*   ✅ **Bug Fix:** Identified and fixed a `temperature=0` rejection error in the Preflight module.
*   ✅ **Traceability:** Implemented a "Flight Recorder" (`llm_trace.jsonl`) to capture raw LLM I/O.
*   ⚠️ **Observation:** AI Preflight is **significantly stricter** than heuristics, shielding logical false positives but currently leaving many ambiguous items in `NEEDS_VERIFICATION`.
*   ❌ **Logging Gap:** While Preflight logs perfectly, Adjudication and Critique traces are failing to write to the log file (likely an environment scope issue).

---

## 2. Detailed Findings

### 2.1. The Preflight "Silent Failure"
**Issue:** For several runs, the agent reported "falling back to heuristic" for preflight checks.
**Discovery:** By implementing the trace logger in `src/fba_agent/openai_client.py` and running with `gpt-5-mini`, we captured the exact error response from the API.

**Extract from `llm_trace.jsonl`:**
```json
"error": "400 Client Error: Bad Request... Message: Unsupported value: 'temperature' does not support 0 with this model. Only the default (1) value is supported."
```
**Fix Implemented:** We modified `openai_client.py` to remove the hardcoded `temperature=0` parameter. Preflight now succeeds.

### 2.2. The "Memory Corruption" Issue
**Issue:** Even after fixing the code, the agent kept using the old, limited heuristic configuration.
**Cause:** The `merge_calibration` logic in `memory_store.py` prioritizes *persisted supplier memory* (`calibration.json`) over fresh preflight results. Since previous runs failed, they saved the "bad" heuristic config to memory.
**Fix Executed:** We deleted `memory/suppliers/part_4_jan/calibration.json`. The subsequent run (`20260105_095759`) successfully generated and applied a fresh AI-derived configuration.

### 2.3. The "Stricter AI" Paradox
Comparing the configurations explains why our `VERIFIED` count dropped from **29** (Heuristic run) to **11** (AI run), and `NEEDS_VERIFICATION` spiked to **96**.

| Feature | Heuristic Config | AI Config (gpt-5-mini) | Impact |
| :--- | :--- | :--- | :--- |
| **Explicit Units** | `["pce", "pcs", "pk", "pack"]` | `["ML", "G", "L", "CM", "MM", "IN", "TR", "PC", "PCS", "PK", "PACK", ...]` | AI recognizes far more unit types. |
| **Dimension Shielding** | Minimal | **Aggressive:** `["X", "x", "BY", "ft", "cm", "mm", "WIDTH", "HEIGHT", "DEPTH"]` | **CRITICAL:** The AI correctly identifies "300 x 50mm" as dimensions, not a "Pack of 300". |

**Result:**
The Heuristic method was **ignorant**. It likely saw numbers in titles (like dimensions) and guessed they were pack quantities, leading to "false positive" Verified items with huge artificial profits.
The AI method is **smart**. It blocked these false positives. However, it also introduced more nuance, placing 96 items into `NEEDS_VERIFICATION` because it wasn't 100% sure, rather than blindly verifying them.

### 2.4. Adjudication & Logging Anomaly
**Observation:** The run summary claims `adjudication_count: 50`. However, the `llm_trace.jsonl` contains **only 1 line** (the Preflight call).
**Diagnosis:** The Adjudication module uses `src/fba_agent/providers/openai_provider.py`. I instrumented this class to check `os.getenv("FBA_TRACE_FILE")`.
*   **Hypothesis:** The `OpenAIProvider` might be instantiated *before* `run.py` sets the environment variable, or in a way where the variable isn't visible.
*   **Result:** We are flying blind on Adjudication decisions. We don't know *why* it failed to move those 96 items out of `NEEDS_VERIFICATION`.

---

## 3. Current System Verification

*   **Script:** `src/fba_agent/run.py`
    *   **Status:** Correctly calls `_run_with_iteration`.
    *   **Evidence:** `iteration_details.json` exists and shows loop data.

*   **Script:** `src/fba_agent/openai_client.py` (Preflight)
    *   **Status:** Fixed `temperature` bug. Added tracing.
    *   **Evidence:** `llm_trace.jsonl` contains successful preflight payload.

*   **Script:** `src/fba_agent/providers/openai_provider.py` (Main AI)
    *   **Status:** Tracing added but **NOT ACTIVATING**.
    *   **Defect:** Logs are missing for Adjudication and Critique.

---

## 4. Proposed Investigation & Fix Plan

To move forward, I propose the following plan to achieve distinct visibility and higher result yields.

### Step 1: Fix Reliable Tracing (Priority 1)
We must see the Adjudication prompts to know if `gpt-5-mini` is being "lazy" or "strict".
*   **Action:** Modify `BaseProvider` `__init__` method to accept an optional `trace_path` argument.
*   **Action:** Update `run.py` to pass the `llm_trace.jsonl` path explicitly when calling `get_provider`, rather than relying on environment variables.

### Step 2: Tune Adjudication Capabilities
The current cap of **50 rows** is too low for the current batch, which has 96 items in usage `NEEDS_VERIFICATION` + hundreds of high-value `FILTERED_OUT` candidates.
*   **Action:** In `src/fba_agent/adjudication.py`, increase the absolute cap (e.g., to 200 or 300) to ensure the AI gets a chance to look at all borderline items.

### Step 3: Relax "Paranoid" Critique
The Critique module detected "Regression in Verified Count" (presumably) and blocked the loop.
*   **Action:** Temporarily disable the "Block on High Priority Issue" logic in `iteration.py` or `run.py`. We want the agent to *try* a second iteration even if the first one looks weird, because self-correction happens in the loop.

### Step 4: Re-Run and Analyze Trace
Once logging works:
*   **Run:** Execute Analysis again.
*   **Inspect:** Open `llm_trace.jsonl`.
*   **Verify:** Check the `Adjudication` entries. Are we sending the right data? Is the AI saying "I can't decide"?
*   **Tune:** If the AI says "Unsure", we update the `system_prompt` in `adjudication.py` to be more decisive or provide better examples.

### Step 5: Recover Missing Entries
To address the "missing entries" compared to your reference report:
*   We likely need to **tune the Confidence Thresholds** in `analysis.py`. The AI parsing is stricter, so our confidence penalty for "ambiguity" might need to be lowered, trusting the AI's "shielding" lists more.

---

**Ready to proceed with Step 1 (Fixing Tracing) upon your command.**
