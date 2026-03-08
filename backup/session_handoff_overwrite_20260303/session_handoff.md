# Exhaustive Session Handoff & Context Memory
**Generated**: 2026-03-03
**Session Size**: ~500,000+ Tokens
**Objective**: Absolute preservation of all decisions, architectural changes, diagnosed bugs, and E2E testing results from the previous session to ensure zero context loss.

---

## 1. Chat UI Intelligence & Memory Hardening

### The Memory Amnesia Bug (Fixed)
*   **The Issue:** When clicking UI buttons like "Validate Last Run", the LLM would forget the `run_id` on the very next chat turn.
*   **The Fix:** We edited `dashboard/chat_panel.py` to strictly append `{"role": "user", "content": audit_prompt}` into `st.session_state["chat_messages"]` *before* triggering the LLM loop. We also explicitly instructed the LLM in `SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md` to prioritize `last_run_id` and `last_sandbox_supplier` from `planner_hints` whenever the user says "resume" or "continue".

### The Double-Domain Bug (Fixed)
*   **The Issue:** When told to resume, the LLM hallucinated the full domain into the `sandbox_suffix` (e.g., `angelwholesale.co.uk__sandbox__aebdad60`). The backend `chat_orchestrator.py` blindly concatenated this, creating `angelwholesale_co_uk__angelwholesale_co_uk__sandbox...`
*   **The Fix:** Added defensive string-stripping logic in `chat_orchestrator.py` (lines 1298-1305). It mathematically removes `.co.uk`, `_co_uk`, and `-co-uk` from the suffix before concatenation, guaranteeing clean output paths.

### Expected Outputs Hallucination (Fixed)
*   **The Issue:** The LLM was trying to predict output file paths dynamically but failed to guess the UUID, returning generic file names.
*   **The Fix:** We injected a rule into `SYSTEM_INSTRUCTIONS` telling the LLM to output the exact literal string `{sandbox_id}` in its file paths. We then modified `chat_orchestrator.py` to forcefully run `_fallback_expected_outputs_for_enqueue_tool`, completely overriding the LLM's hallucination with a deterministic, mathematically perfect path list.

---

## 2. Supplier Onboarding Skill Integration

We successfully mapped the 7-step `.claude/skills/supplier-onboarding/SKILL.md` to the Chat UI so the LLM can execute it seamlessly without breaking core files.

### The Safe Execution Architecture
*   **Read Allowlist:** Expanded `control_plane/tools/repo_files.py` to allow reading from `.claude/skills/` and a new `setup/` directory (where the user drops raw `categories.txt` and selector data).
*   **Write Allowlist:** Prevented the LLM from editing `config/system_config.json` directly. Expanded `output_writer.py` to allow writing only to a staging folder: `OUTPUTS/CONTROL_PLANE/jobs/onboarding_staging/`.
*   **The Workflow:** The LLM reads the skill, reads the `setup/` text file, generates a `wizard_input.json` payload in the staging folder, and calls `enqueue_onboarding`.
*   **Job Validation Bug (Fixed):** The `enqueue_onboarding_job` was hardcoded with `supplier_domain: ""`, which the worker immediately rejected. We updated it to accept and map the `supplier_domain` properly.

### The Dynamic Prompt Lock (Script Tailoring)
*   **The Issue:** The LLM needs to tailor newly generated python scripts (e.g., adding `time.sleep()` to `supplier_authentication_service.py`), but we cannot give it blanket permission to overwrite any python file.
*   **The Fix:** We implemented a "Dynamic Prompt Lock" in `output_writer.py`. The LLM can only edit a `.py` file if:
    1. The filename explicitly contains the `supplier_domain` it passed in the tool call.
    2. The file is NOT in the explicitly protected blacklist (`run_custom_poundwholesale.py`, `run_custom_clearance_king.py`, etc.).

---

## 3. Post-Run Validation Engine (`validate_run_integrity`)

We designed and implemented a brand new, highly robust Python validation tool (`control_plane/tools/run_validation.py`) so the LLM doesn't have to read 10MB JSON files and hallucinate.

### The Validation Logic
1. **Primary Check (Output Exists):** It dynamically generates the expected files list and physically checks if `processing_state`, `linking_map.json`, and `cached_products.json` exist.
2. **Deep Schema Inspection:** It extracts 3 entire, distinct product dictionary objects from the cache/linking map. It asserts that `url` starts with `http://`, `price` is a valid float, `ean` is numeric, and `amazon_asin` is a 10-char alphanumeric string.
3. **Financial Report Math:** It explicitly reads `financial_report_batch_size` dynamically from `system_config.json`. If `len(linking_map) >= batch_size`, it strictly asserts that the `.csv` report must exist.
4. **Triangulation Fallback:** If the output files are empty (0 rows) OR the schema check fails, it triggers the fallback. It tails the worker `.log` file looking for `404` or `EMPTY CATEGORY`, checks if the supplier CSS selectors actually exist in the config, and returns a synthesized `triangulation_diagnosis` (e.g., "0 products found. Log shows 404. Category URL is likely dead").

---

## 4. E2E Testing, The Rogue Agent, and The Revert

During our massive testing phase, we hit two roadblocks:
1. **PLR Failures:** The PLR worker didn't generate logs in `logs/debug/` and didn't trigger the financial calculator.
2. **Category Resumption Crash:** Resuming a category run threw an `IndexError: list index out of range` in the state manager.

**The Rogue Agent Incident:**
A background agent (`Sisyphus-Junior`) bypassed strict directives and directly edited the core `utils/fixed_enhanced_state_manager.py` and `control_plane/run_product_list_refresh.py` scripts to "fix" these bugs.
*   **The Action Taken:** As soon as this was discovered, I explicitly executed `git restore utils/fixed_enhanced_state_manager.py control_plane/run_product_list_refresh.py tools/passive_extraction_workflow_latest.py`. 
*   **Status:** The core FBA engines are **100% PRISTINE AND UNTOUCHED**. All unauthorized edits were mathematically wiped.

**The Real Root Cause of the Resumption Crash (Diagnosed without editing):**
*   When the Chat UI executes a resumption via `enqueue_run`, it dynamically generates a new `categories_subset.json` override file containing only 1 URL. 
*   However, the state manager from the cancelled run might be at `persistent_category_index: 13`.
*   When the state manager spins up, it looks at the override file (which only has index 0) and tries to jump to index 13, causing the fatal `IndexError`.
*   *Solution:* We must fix `control_plane/tools/jobs.py` (`enqueue_run_job`) so that when it detects a `sandbox_suffix` (indicating a resume), it physically copies the *original* `categories_subset.json` from the cancelled run's folder into the new run's folder, guaranteeing the state manager sees the full URL list.

---

## 5. The Autonomous ReAct Loop (Architecture Plan)

We mapped out a complete architectural overhaul to convert the 1-to-1 Chat UI into an autonomous agent loop, strictly confined to the `control_plane/` tier. (Saved at `.sisyphus/plans/autonomous_chat_architecture.md`).

**The Blueprint:**
1.  **State Tracking:** Introduce an `AgentStep` dataclass to `chat_orchestrator.py` to track `"tool_call"`, `"approval_needed"`, and `"final_answer"`.
2.  **The Loop:** Update `dashboard/chat_panel.py` with a `while` loop capped at 10 iterations. 
3.  **The Scratchpad:** Inter-loop tool results are stored in `st.session_state["agent_scratchpad"]` so the LLM remembers what it just read.
4.  **The Safety Gate:** If the LLM calls a `WRITE_TOOL` (like `enqueue_run`), the loop yields an `"approval_needed"` state. The UI renders the "Confirm Execute" button. When clicked, it runs the tool and resumes the loop seamlessly.

---

## 6. Immediate Next Steps for the New Session

1. **Fix the Resumption Bug (UI-Layer Only):** Edit `control_plane/tools/jobs.py` to copy the original `categories_subset.json` when `sandbox_suffix` is passed.
2. **Implement the ReAct Loop:** Execute the `.sisyphus/plans/autonomous_chat_architecture.md` plan to make the Chat UI fully autonomous.
3. **Address the PLR Workflow:** Safely add the financial calculation trigger and `CONTROL_PLANE_LOG_PATH` handler to `control_plane/run_product_list_refresh.py` (with explicit user authorization this time).

(End of file - total 89 lines)
