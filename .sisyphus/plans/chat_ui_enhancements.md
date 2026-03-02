# Chat UI Enhancements Plan

## 1. Post-Run Validation Tool (`validate_run_integrity`)
**Goal:** Create a fast, deterministic python tool that validates a run without forcing the LLM to hallucinate over massive JSON files.

**Implementation (`control_plane/tools/run_validation.py`):**
- Checks `job_type`. If it is `run_onboarding_wizard`, it validates the onboarding files (`run_custom_*.py`, configs, and `system_config.json` injection).
- If it is a standard workflow, it locates `cached_products.json` and `linking_map.json`.
- It counts the entries.
- It randomly samples 3 distinct product dictionaries and strictly verifies the types (`url` starts with `http`, `price` is numeric).
- If the outputs are empty, it scans the run `.log` for `EMPTY CATEGORY`, `404`, or exceptions.
- Returns a highly structured JSON summary.

## 2. Fix the Expected Outputs Hallucination
**Goal:** Stop the LLM from outputting incorrect paths when asked "What files will this run produce?"

**Implementation (`control_plane/chat_orchestrator.py` & `SYSTEM_INSTRUCTIONS`):**
- Rewrite `_fallback_expected_outputs_for_enqueue_tool` to perfectly replicate the worker's `sandbox_suffix` logic.
- Instruct the LLM in the system prompt to explicitly use the literal `{sandbox_id}` placeholder when predicting paths, allowing the orchestrator to inject the true UUID later.

---

### Tasks
- [x] Task 1: Create Plan File
- [ ] Task 2: Create `control_plane/tools/run_validation.py`
- [ ] Task 3: Update `control_plane/chat_orchestrator.py` (Expected Outputs & Tool Registration)
- [ ] Task 4: Update `control_plane/tools/__init__.py`
- [ ] Task 5: Update `SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md`
- [ ] Task 6: Add "Validate Last Run" button to `dashboard/chat_panel.py` and implement Thought Trace UI.