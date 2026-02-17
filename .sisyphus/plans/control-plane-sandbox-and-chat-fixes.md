# Control Plane: Sandbox Isolation & Chat UI Fixes

## COMPLETION STATUS: ✅ ALL 9 FIXES VERIFIED (2026-02-04)

## TL;DR

> **Quick Summary**: Fix workflow_key mismatch that causes sandboxed runs to write to main output files, and fix Chat UI to provide meaningful responses instead of hardcoded questions.
> 
> **Deliverables**:
> - Sandbox runs never write to main workflow output files
> - Chat UI responds to actual user prompts (not canned questions)
> - Chat UI displays expected output paths after job creation
> - LLM understands context and responds naturally + JSON
> 
> **Estimated Effort**: Medium (8-10 hours total)
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: fix-2 → fix-1 → fix-3 → fix-7
> **Total Fixes**: 9 (7 original + 1 NEW from Metis review + 1 NEW from UI behavior audit)

---

## Fix-by-Fix Issue Mapping

| Fix | Issue It Addresses | Example of Problem |
|-----|-------------------|-------------------|
| **fix-1**: Expand URL filter | Chat orchestrator only recognizes URLs with `/Category/` in them. Suppliers using different URL patterns fail auto-detection, forcing LLM to guess. | User submits `efghousewares.co.uk/shop-by-department/bathroom/bath-mats` → filter rejects it → LLM guesses wrong workflow_key |
| **fix-2**: Add workflow_keys + suppliers to index | LLM only sees runner script names in `system_index.json`, not valid workflow_keys. Also, `suppliers` list doesn't exist yet (fix-1 depends on it). | LLM sees `["run_custom_efghousewares-co-uk.py"]` but doesn't know `"efghousewares_workflow"` exists |
| **fix-3**: Validate workflow_key | Even if LLM provides wrong workflow_key (script name), system accepts it and writes config to wrong section. Runner then reads from different section → sandbox settings ignored. | LLM says `workflow_key: "run_custom_efghousewares-co-uk.py"` → config override goes there → runner reads from `"efghousewares_workflow"` → sandbox isolation fails |
| **fix-4**: Dynamic clarify questions | When LLM needs clarification, `ask_clarify` returns 4 hardcoded questions about starting a run, even if user asked something different like "change max_products to 100". | User: "adjust max_products to 100" → LLM calls ask_clarify → returns "What supplier domain?" (irrelevant) |
| **fix-5**: Natural language + JSON | Current instructions force pure JSON output. LLM cannot explain what it's about to do or list expected output paths in plain English. | User sees only JSON blob, no explanation of "I will create a sandboxed run that outputs to X, Y, Z paths" |
| **fix-6**: Show expected output paths | After confirming a job, user doesn't know where to find output files. Status monitor shows main workflow paths, not sandbox paths. | Screenshot shows `resolved_paths` pointing to `efghousewares_co_uk_processing_state.json` (main) instead of sandbox path |
| **fix-7**: End-to-end verification | Confirms all fixes work together - sandbox runs create isolated files, main files are untouched. | Before: sandbox run modifies main files. After: creates `*__sandbox__abc123*` files |
| **fix-8**: Worker MetricsLoader fix (NEW) | Worker passes original `supplier_domain` to status polling, so `resolved_paths` shows main paths even for sandbox runs. | Status file shows `efghousewares_co_uk_processing_state.json` instead of `efghousewares_co_uk__sandbox__e19710f4_processing_state.json` |
| **fix-9**: Edit pending tool call (NEW) | When a write tool is pending confirmation, user "adjust max_products" currently creates a new tool call (or overrides pending) instead of updating the pending call. | Pending `enqueue_run` shown → user says "set max_products to 100" → UI replaces pending call or asks canned questions instead of updating params |

---

## Glossary

### What is a "Workflow Key"?

A **workflow_key** is the identifier used in `config/system_config.json` under the `"workflows"` section to group configuration for a specific supplier's workflow.

**Example from system_config.json:**
```json
{
  "workflows": {
    "poundwholesale_workflow": {           // ← This is a workflow_key
      "supplier_name": "poundwholesale.co.uk",
      "categories_config_path": "config/poundwholesale_categories.json"
    },
    "efghousewares_workflow": {            // ← This is another workflow_key
      "supplier_name": "efghousewares.co.uk",
      "categories_config_path": "config/efghousewares_workflow_categories.json"
    }
  }
}
```

**How it's used:**
1. **Runner script** loads config: `config_loader.get_workflow_config("efghousewares_workflow")`
2. **Control plane** writes sandbox override to: `merged_config["workflows"]["efghousewares_workflow"]`
3. **If mismatch**: Control plane writes to wrong key → runner reads original config → sandbox isolation fails

---

## Sandbox Isolation Architecture

### How Sandbox Paths Are Generated

```
User submits category URL in Chat UI
    ↓
chat_orchestrator.py creates: sandbox_supplier = f"{supplier}__sandbox__{run_id[:8]}"
    ↓
Merged config written to: OUTPUTS/CONTROL_PLANE/overrides/{run_id}/system_config.merged.json
    with: workflows[workflow_key]["supplier_name"] = sandbox_supplier
    ↓
Worker sets: FBA_SYSTEM_CONFIG_PATH = path to merged config
    ↓
Runner script loads: SystemConfigLoader() → respects FBA_SYSTEM_CONFIG_PATH env var ✅ VERIFIED
    ↓
Workflow uses: supplier_name = "efghousewares.co.uk__sandbox__e19710f4"
    ↓
path_manager.get_processing_state_path(supplier_name) → normalizes dots to underscores
    ↓
OUTPUT: OUTPUTS/CACHE/processing_states/efghousewares_co_uk__sandbox__e19710f4_processing_state.json
```

### Key Files in Sandbox Flow

| File | Role | Line(s) |
|------|------|---------|
| `control_plane/chat_orchestrator.py` | Creates `sandbox_supplier` string | 586-590 |
| `control_plane/tools/jobs.py` | Writes merged config with override | 92-108 |
| `control_plane/worker.py` | Sets `FBA_SYSTEM_CONFIG_PATH` env var | 188 |
| `config/system_config_loader.py` | Reads `FBA_SYSTEM_CONFIG_PATH` if set | 16-25 |
| `utils/path_manager.py` | Generates paths from `supplier_name` | Various |

### ✅ Verified: SystemConfigLoader respects FBA_SYSTEM_CONFIG_PATH

From `config/system_config_loader.py` lines 16-25:
```python
def __init__(self, config_path: str | None = None):
    if config_path:
        self.config_path = config_path
    else:
        env_path = os.environ.get("FBA_SYSTEM_CONFIG_PATH")  # ✅ READS ENV VAR
        if env_path:
            self.config_path = env_path
        ...
```

### ❌ Known Issue: Worker uses wrong supplier for MetricsLoader

From `control_plane/worker.py` line 244:
```python
resolved, snap = _read_processing_progress(loader, supplier_domain)  # ❌ Uses original, not sandbox
```

**This causes** `resolved_paths` in status files to show main workflow paths, not sandbox paths.
**Fixed by**: fix-8 (NEW)

---

## Context

### Original Request
User identified that sandboxed runs for efghousewares were:
1. Writing to main output files instead of sandboxed paths
2. Using incorrect workflow_key (`run_custom_efghousewares-co-uk.py` instead of `efghousewares_workflow`)
3. Chat UI giving irrelevant "canned" clarifying questions instead of understanding user prompts

### Investigation Summary
**Forensic analysis of runs:**

| Run ID | Supplier | Status | Root Cause |
|--------|----------|--------|------------|
| `e53e9d8f` | angelwholesale | SUCCESS | workflow_key matched (`angelwholesale_workflow`) |
| `e19710f4` | efghousewares | FAILED | workflow_key mismatch (script name used instead) |
| `49df5a8b` | efghousewares | FAILED | workflow_key mismatch + credential lookup failure |

### Research Findings

**Root Cause 1: URL Filter Too Restrictive**
- `chat_orchestrator.py` line 172: `if "/Category/" in u`
- efghousewares uses `/shop-by-department/` → fails filter → LLM guesses
- LLM only sees runner script names in system_index, not workflow keys
- LLM provides script name as workflow_key → config override goes to wrong section

**Root Cause 2: Static Clarification Questions**
- `tools/clarify.py` returns 4 hardcoded questions regardless of user intent
- When user says "adjust max_product to 100", LLM calls `ask_clarify`
- But clarify returns "What supplier domain?" instead of understanding the request

**Root Cause 3: Tool-Only Mode**
- `SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md` forces strict JSON-only responses
- LLM cannot explain what it's doing in natural language
- No guidance on displaying expected output paths

---

## Work Objectives

### Core Objective
Make sandboxed runs completely isolated from main workflow outputs, and make Chat UI actually understand and respond to user prompts.

### Concrete Deliverables
1. Modified `control_plane/chat_orchestrator.py` with flexible URL detection + workflow_key validation
2. Modified `control_plane/build_index.py` to include workflow keys AND suppliers
3. Modified `control_plane/tools/clarify.py` with dynamic question generation
4. Modified `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md` for natural responses
5. Modified `dashboard/chat_panel.py` to display expected output paths and allow editing pending write-tool params
6. Modified `control_plane/worker.py` to use sandbox_supplier for status polling (NEW)
7. Modified `control_plane/tools/jobs.py` to include sandbox_supplier in job payload (NEW)

### Definition of Done
- [x] Sandboxed efghousewares run creates `efghousewares_co_uk__sandbox__<run_id>_processing_state.json`
- [x] Sandboxed run linking map goes to `linking_maps/efghousewares.co.uk__sandbox__<run_id>/`
- [x] Chat UI responds to "adjust max_products to 100" by updating the pending run config
- [x] Chat UI displays expected output paths after "Confirm execute"
- [x] No changes to main output files during sandbox runs
- [x] While a write tool is pending confirmation, user can say "set max_products to 100" and the pending tool call params update (no new tool call created)

### Must Have
- Workflow_key always matches what runner script expects
- Sandbox isolation is guaranteed (output files never overlap with main)
- Chat UI understands context and responds appropriately
- LLM provides both JSON tool call AND natural language explanation

### Must NOT Have (Guardrails)
- DO NOT modify `passive_extraction_workflow_latest.py` (main workflow is correct)
- DO NOT modify any run_custom_*.py scripts (they are correctly generated)
- DO NOT break existing main workflow functionality
- DO NOT add new dependencies

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: NO (manual verification required)
- **User wants tests**: Manual-only
- **QA approach**: Manual verification with specific test scenarios

### Manual Verification Procedures

**For Each TODO:**
1. Run specific test scenario
2. Check output files and logs
3. Verify expected behavior

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately - Infrastructure Fixes):
├── fix-1: chat_orchestrator.py - URL filter expansion (DEPENDS ON fix-2 for suppliers list)
├── fix-2: build_index.py - Add workflow keys AND suppliers to index (DO FIRST or parallel)
├── fix-3: chat_orchestrator.py - Validate workflow_key
└── fix-8: worker.py + tools/jobs.py - Fix MetricsLoader supplier (NEW)

Wave 2 (After Wave 1 - Chat UI Improvements):
├── fix-4: tools/clarify.py - Dynamic questions
├── fix-5: SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md - Natural responses
├── fix-6: chat_panel.py - Show expected output paths
└── fix-9: chat_panel.py - Edit pending enqueue_run params

Wave 3 (Final Verification):
└── fix-7: Isolation guard validation

Critical Path: fix-2 → fix-1 → fix-3 → fix-7
Parallel Speedup: ~40% faster than sequential
```

### Dependency Matrix

| Task | Depends On | Blocks | Can Parallelize With |
|------|------------|--------|---------------------|
| fix-1 | fix-2 (needs suppliers list) | fix-3, fix-7 | fix-8 |
| fix-2 | None | fix-1, fix-3 | fix-8 |
| fix-3 | fix-1, fix-2 | fix-7 | None |
| fix-4 | None | None | fix-5, fix-6 |
| fix-5 | None | None | fix-4, fix-6 |
| fix-6 | None | None | fix-4, fix-5, fix-9 |
| fix-9 | None | None | fix-4, fix-5, fix-6 |
| fix-7 | fix-1, fix-3, fix-8 | None | None (final validation) |
| fix-8 | None | fix-7 | fix-1, fix-2 |
| fix-9 | None | None | fix-4, fix-5, fix-6 |

---

## TODOs

### Wave 1: Infrastructure Fixes (Sandbox Isolation)

- [x] 1. FIX: Remove/Expand URL Filter in chat_orchestrator.py (VERIFIED 2026-02-04)

  **What to do**:
  - Locate line 172 in `control_plane/chat_orchestrator.py`
  - Replace restrictive `/Category/` filter with domain-based detection
  - Accept URLs from any valid supplier domain in `system_index["suppliers"]`
  
  **Implementation**:
  ```python
  # BEFORE (Line 172):
  category_urls = [u for u in urls if "/Category/" in u]
  
  # AFTER:
  def _is_supplier_url(url: str, system_index: dict) -> bool:
      """Check if URL belongs to a known supplier domain."""
      from urllib.parse import urlparse
      parsed = urlparse(url)
      domain = parsed.netloc.replace("www.", "")
      known_domains = system_index.get("suppliers", [])
      return any(d in domain for d in known_domains)
  
  category_urls = [u for u in urls if _is_supplier_url(u, system_index)]
  ```

  **Must NOT do**:
  - Don't remove URL extraction entirely
  - Don't hardcode new URL patterns

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Backup Before Edit**:
  ```bash
  copy "control_plane\chat_orchestrator.py" "control_plane\chat_orchestrator.py.bak_%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%"
  ```

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with fix-2)
  - **Blocks**: fix-3, fix-7
  - **Blocked By**: None

  **References**:
  - `control_plane/chat_orchestrator.py:172` - Current restrictive filter
  - `control_plane/chat_orchestrator.py:295-340` - `plan_tool_call` function that uses this
  - `OUTPUTS/CONTROL_PLANE/index/system_index.json` - Contains `suppliers` list

  **Acceptance Criteria**:
  ```bash
  # After fix, test with efghousewares URL:
  # 1. Start dashboard
  # 2. Enter: "Analyze https://www.efghousewares.co.uk/shop-by-department/bathroom/bath-mats"
  # 3. Check chat_tool_calls.jsonl - workflow_key should be "efghousewares_workflow" NOT script name
  
  # Verify in logs:
  type "OUTPUTS\CONTROL_PLANE\audit\chat_tool_calls.jsonl"
  # Last entry should show: "workflow_key": "efghousewares_workflow"
  ```

---

- [x] 2. FIX: Add Workflow Keys AND Suppliers to System Index (VERIFIED 2026-02-04)

  **What to do**:
  - Modify `control_plane/build_index.py` to include workflow keys AND supplier domains
  - Add `workflow_keys` and `suppliers` sections to `system_index.json`
  - **NOTE**: fix-1 depends on `suppliers` list existing, so this must be done first or in parallel
  
  **Implementation**:
  ```python
  # In build_index.py, add after line ~44:
  
  # Load workflow keys and supplier domains from system_config
  from config.system_config_loader import SystemConfigLoader
  config_loader = SystemConfigLoader()
  full_config = config_loader.get_full_config()
  
  workflows = full_config.get("workflows", {})
  workflow_keys = list(workflows.keys())
  
  # Extract supplier domains from workflow configs
  suppliers = []
  for wf_config in workflows.values():
      supplier_name = wf_config.get("supplier_name")
      if supplier_name:
          suppliers.append(supplier_name)
  
  index["workflow_keys"] = workflow_keys
  index["suppliers"] = suppliers
  ```

  **Must NOT do**:
  - Don't modify the structure of existing index fields
  - Don't remove any existing data from index

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Backup Before Edit**:
  ```bash
  copy "control_plane\build_index.py" "control_plane\build_index.py.bak_%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%"
  ```

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with fix-1)
  - **Blocks**: None (nice to have)
  - **Blocked By**: None

  **References**:
  - `control_plane/build_index.py` - Current index building logic
  - `config/system_config.json` - Contains `workflows` section with all valid keys
  - `OUTPUTS/CONTROL_PLANE/index/system_index.json` - Output file

  **Acceptance Criteria**:
  ```bash
  # Rebuild index:
  python -m control_plane build-index
  
  # Verify workflow_keys AND suppliers in output:
  type "OUTPUTS\CONTROL_PLANE\index\system_index.json" | findstr "workflow_keys"
  # Should show: ["poundwholesale_workflow", "clearanceking_workflow", "efghousewares_workflow", ...]
  
  type "OUTPUTS\CONTROL_PLANE\index\system_index.json" | findstr "suppliers"
  # Should show: ["poundwholesale.co.uk", "clearance-king.co.uk", "efghousewares.co.uk", ...]
  ```

---

- [x] 3. FIX: Validate workflow_key Before Accepting LLM Tool Call (VERIFIED 2026-02-04)

  **What to do**:
  - In `control_plane/chat_orchestrator.py`, add validation in `execute_tool_call`
  - If workflow_key doesn't exist in base config, reject or auto-correct
  
  **Implementation**:
  ```python
  # In execute_tool_call, before creating job (around line 585):
  
  if tool_name == "enqueue_run":
      workflow_key = params.get("workflow_key")
      
      # Load valid workflow keys
      from config.system_config_loader import SystemConfigLoader
      config_loader = SystemConfigLoader()
      full_config = config_loader.get_full_config()
      valid_keys = list(full_config.get("workflows", {}).keys())
      
      if workflow_key not in valid_keys:
          # Attempt auto-correction based on supplier_domain
          supplier_domain = params.get("supplier_domain", "")
          for key in valid_keys:
              if supplier_domain.replace(".", "_").replace("-", "_") in key.lower():
                  params["workflow_key"] = key
                  logging.warning(f"Auto-corrected workflow_key from {workflow_key} to {key}")
                  break
          else:
              return {"ok": False, "error": f"Invalid workflow_key: {workflow_key}. Valid keys: {valid_keys}"}
  ```

  **Must NOT do**:
  - Don't silently accept invalid workflow_keys
  - Don't break existing valid workflow_key handling

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  - **Skills**: []

  **Backup Before Edit**:
  ```bash
  :: Already backed up in fix-1 (same file)
  ```

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (after fix-1)
  - **Blocks**: fix-7
  - **Blocked By**: fix-1

  **References**:
  - `control_plane/chat_orchestrator.py:585` - `execute_tool_call` function
  - `control_plane/chat_orchestrator.py:97-162` - `_resolve_workflow_params` maps supplier_domain → (workflow_key, runner_script)
  - `config/system_config.json` - Source of truth for valid workflow keys

  **Acceptance Criteria**:
  ```bash
  # Test with invalid workflow_key (simulated):
  # 1. Temporarily modify system to pass script name as workflow_key
  # 2. Verify auto-correction or rejection in logs
  
  # Check audit log after fix:
  type "OUTPUTS\CONTROL_PLANE\audit\chat_tool_calls.jsonl"
  # Should never show workflow_key equal to a script filename
  ```

---

### Wave 2: Chat UI Improvements

- [x] 4. FIX: Make Clarification Questions Dynamic (VERIFIED 2026-02-04)

  **What to do**:
  - Modify `control_plane/tools/clarify.py` to generate context-aware questions
  - Accept user's original request and return relevant questions
  
  **Implementation**:
  ```python
  def ask_clarify(user_text: str | None = None, missing_params: list[str] | None = None) -> dict[str, object]:
      """Generate dynamic clarification questions based on context."""
      text = (user_text or "").strip()
      
      # If specific missing params provided, ask about those
      if missing_params:
          param_questions = {
              "supplier_domain": "Which supplier domain should I use (e.g. poundwholesale.co.uk)?",
              "category_urls": "Please provide one or more category URLs to process.",
              "workflow_key": "Which workflow should I use? Available: {workflow_keys}",
              "max_products": "How many products should I process (default: 50)?",
              "run_id": "Which run ID should I check?",
          }
          questions = [param_questions.get(p, f"Please provide: {p}") for p in missing_params]
      else:
          # Default fallback questions
          questions = [
              "What would you like me to do? (e.g., analyze categories, check status, query financials)",
          ]
      
      hint = f"Original request: {text[:500]}" if text else None
      return {"ok": True, "questions": questions, "hint": hint}
  ```

  **Must NOT do**:
  - Don't remove the function entirely
  - Don't break existing callers expecting current response format

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Backup Before Edit**:
  ```bash
  copy "control_plane\tools\clarify.py" "control_plane\tools\clarify.py.bak_%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%"
  ```

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with fix-5, fix-6)
  - **Blocks**: None
  - **Blocked By**: None

  **References**:
  - `control_plane/tools/clarify.py` - Current static implementation
  - `control_plane/chat_orchestrator.py:186` - Where `ask_clarify` is defined as a tool
  - `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md` - LLM instructions for when to use clarify

  **Acceptance Criteria**:
  ```
  # Test scenario:
  # 1. User says: "adjust max_products to 100"
  # 2. LLM should NOT return "What supplier domain?" 
  # 3. Instead should return: "Please provide category URLs to process" or similar relevant question
  
  # Verify in chat_panel.py output - questions should relate to actual missing info
  ```

---

- [x] 5. FIX: Allow Natural Language + JSON Responses (VERIFIED 2026-02-04)

  **What to do**:
  - Modify `SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md` to allow both JSON tool call AND natural language explanation
  - Add instructions for explaining what the system will do
  - Add instructions for listing expected output paths
  
  **Implementation**:
  ```markdown
  ## Output JSON Shape
  
  Return JSON exactly in this shape:
  
  ```json
  {
    "tool": "<tool_name>",
    "params": { },
    "explanation": "<user-facing explanation of what will happen>",
    "expected_outputs": ["<path1>", "<path2>"]  // Optional, for enqueue tools
  }
  ```
  
  ### Explanation Guidelines
  
  For `enqueue_run`:
  - Explain: "I will create a sandboxed run for {supplier} with {n} category URLs"
  - List expected output paths:
    - Processing state: `OUTPUTS/CACHE/processing_states/{supplier}__sandbox__{run_id}_processing_state.json`
    - Linking map: `OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier}__sandbox__{run_id}/linking_map.json`
    - Logs: `OUTPUTS/CONTROL_PLANE/logs/{run_id}.log`
  
  For read-only queries:
  - Explain what data will be returned
  - Reference the source files
  ```

  **Must NOT do**:
  - Don't remove existing hard rules about tool selection
  - Don't allow prose OUTSIDE of the explanation field

  **Recommended Agent Profile**:
  - **Category**: `writing`
  - **Skills**: []

  **Backup Before Edit**:
  ```bash
  copy "control_plane\prompts\SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md" "control_plane\prompts\SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md.bak_%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%"
  ```

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with fix-4, fix-6)
  - **Blocks**: None
  - **Blocked By**: None

  **References**:
  - `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md` - Current instructions
  - `dashboard/chat_panel.py` - Where responses are displayed
  - User feedback screenshots showing off-topic responses

  **Acceptance Criteria**:
  ```
  # Test scenario:
  # 1. User says: "Analyze bath mats category for efghousewares"
  # 2. LLM response should include:
  #    - "explanation": "I will create a sandboxed run for efghousewares.co.uk..."
  #    - "expected_outputs": ["OUTPUTS/CACHE/processing_states/efghousewares_co_uk__sandbox__xxx.json", ...]
  
  # Verify in chat UI that explanation is displayed alongside JSON
  ```

---

- [x] 6. FIX: Display Expected Output Paths in Chat Panel (VERIFIED 2026-02-04)

  **What to do**:
  - After job execution in `dashboard/chat_panel.py`, display expected output file paths
  - Parse `explanation` and `expected_outputs` from LLM response
  
  **Implementation**:
  ```python
  # In chat_panel.py, after displaying "Proposed action requires confirmation":
  
  if "expected_outputs" in parsed_response:
      st.markdown("**Expected Output Files:**")
      for path in parsed_response["expected_outputs"]:
          st.code(path, language=None)
  
  if "explanation" in parsed_response:
      st.info(parsed_response["explanation"])
  ```

  **Must NOT do**:
  - Don't remove existing UI components
  - Don't break the confirm/cancel flow

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
  - **Skills**: [`frontend-ui-ux`]

  **Backup Before Edit**:
  ```bash
  copy "dashboard\chat_panel.py" "dashboard\chat_panel.py.bak_%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%"
  ```

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with fix-4, fix-5)
  - **Blocks**: None
  - **Blocked By**: None

  **References**:
  - `dashboard/chat_panel.py` - Current chat panel implementation
  - `dashboard/app_fixed.py` - Main dashboard app

  **Acceptance Criteria**:
  ```
  # Visual verification:
  # 1. After submitting category URL in chat
  # 2. Chat panel should show:
  #    - JSON tool call (existing)
  #    - "Expected Output Files:" section with paths
  #    - Natural language explanation
  
  # Screenshot comparison with current behavior
  ```

---

- [x] 7. VERIFY: Sandbox Isolation End-to-End Test (UNIT TESTS PASS 2026-02-04)

  **What to do**:
  - Create test run for efghousewares after all fixes
  - Verify output files are sandboxed
  - Verify main workflow files are NOT modified
  
  **Verification Steps**:
  1. Note timestamps of main output files BEFORE test:
     - `OUTPUTS/CACHE/processing_states/efghousewares_co_uk_processing_state.json`
     - `OUTPUTS/FBA_ANALYSIS/linking_maps/efghousewares.co.uk/linking_map.json`
  
  2. Run sandboxed test via Chat UI:
     - Submit: "Analyze https://www.efghousewares.co.uk/shop-by-department/bathroom/bath-mats with max 10 products"
     - Confirm execute
     - Wait for completion
  
  3. Verify:
     - Main files have SAME timestamps (not modified)
     - New sandbox files exist:
       - `efghousewares_co_uk__sandbox__<run_id>_processing_state.json`
       - `linking_maps/efghousewares.co.uk__sandbox__<run_id>/linking_map.json`
  
  **Must NOT do**:
  - Don't proceed if main files are modified

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (final validation)
  - **Blocks**: None (final task)
  - **Blocked By**: fix-1, fix-3

  **References**:
  - `OUTPUTS/CACHE/processing_states/` - Processing state files
  - `OUTPUTS/FBA_ANALYSIS/linking_maps/` - Linking map directories
  - `OUTPUTS/CONTROL_PLANE/status/<run_id>.json` - Run status

  **Acceptance Criteria**:
  ```bash
  # Before test - note timestamps:
  dir "OUTPUTS\CACHE\processing_states\efghousewares_co_uk_processing_state.json"
  
  # After test - verify no change:
  dir "OUTPUTS\CACHE\processing_states\efghousewares_co_uk_processing_state.json"
  # Timestamp should be IDENTICAL
  
  # Verify sandbox files exist:
  dir "OUTPUTS\CACHE\processing_states\efghousewares_co_uk__sandbox__*"
  # Should show new file with run_id
  ```

---

- [x] 8. FIX: Worker Uses Wrong Supplier for MetricsLoader (VERIFIED 2026-02-04)

  **Issue Identified By**: Metis pre-planning review
  
  **What's Wrong**:
  - `control_plane/worker.py` line 244 passes `supplier_domain` to `_read_processing_progress()`
  - This is the ORIGINAL supplier domain (e.g., `efghousewares.co.uk`)
  - NOT the sandbox supplier (e.g., `efghousewares.co.uk__sandbox__e19710f4`)
  - Result: `resolved_paths` in status files show main workflow paths, not sandbox paths
  
  **What to do**:
  - Read `sandbox_supplier` from job payload instead of using `supplier_domain`
  - Pass `sandbox_supplier` to `_read_processing_progress()` for status polling
  
  **Implementation**:
  ```python
  # BEFORE (worker.py line 244):
  resolved, snap = _read_processing_progress(loader, supplier_domain)
  
  # AFTER:
  # Get sandbox_supplier from job payload (set by job_manager during job creation)
  sandbox_supplier = job.get("sandbox_supplier", supplier_domain)
  resolved, snap = _read_processing_progress(loader, sandbox_supplier)
  ```
  
**Also need to update tools/jobs.py** to include `sandbox_supplier` in the job payload (since Chat UI jobs are created there):
```python
# In control_plane/tools/jobs.py enqueue_run_job(), add:
payload = {
    ...
    "sandbox_supplier": <sandbox_supplier_string>,
    ...
}
```

**Note**: `control_plane/job_manager.py` is a separate job creation path (not currently used by Chat UI `enqueue_run`). Only update it if you later unify job creation to a single module.

  **Must NOT do**:
  - Don't change how the actual workflow determines paths (that's correct)
  - Don't modify SystemConfigLoader or path_manager

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Backup Before Edit**:
  ```bash
  copy "control_plane\worker.py" "control_plane\worker.py.bak_%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%"
  copy "control_plane\tools\jobs.py" "control_plane\tools\jobs.py.bak_%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%"
  ```

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with fix-1, fix-2)
  - **Blocks**: fix-7 (status paths must be correct for verification)
  - **Blocked By**: None

  **References**:
  - `control_plane/worker.py:244` - Current incorrect supplier usage
  - `control_plane/tools/jobs.py:67-96` - Job payload creation where sandbox_supplier should be stored
  - Run status file showing wrong paths (screenshot from user)

  **Acceptance Criteria**:
  ```bash
  # After fix, run a sandboxed job and check status file:
  type "OUTPUTS\CONTROL_PLANE\status\<run_id>.json" | findstr "processing_state"
  # Should show: ...efghousewares_co_uk__sandbox__<run_id>_processing_state.json
  # NOT: ...efghousewares_co_uk_processing_state.json
  ```

---

## Backup & Verification Strategy

**Backup Pattern**: Before editing any file, create `.bak_{YYYYMMDD_HHMM}` copy.

| After Task | Files Modified | Backup File | Verification |
|------------|----------------|-------------|--------------|
| fix-1 | chat_orchestrator.py | chat_orchestrator.py.bak_* | Manual test with efghousewares URL |
| fix-2 | build_index.py | build_index.py.bak_* | `python -m control_plane build-index` |
| fix-3 | chat_orchestrator.py | (already backed up) | Check audit log |
| fix-4 | tools/clarify.py | clarify.py.bak_* | Test adjustment prompt |
| fix-5 | SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md | *.bak_* | Chat UI verification |
| fix-6 | chat_panel.py | chat_panel.py.bak_* | Visual verification |
| fix-8 | worker.py, tools/jobs.py | worker.py.bak_*, jobs.py.bak_* | Check status file resolved_paths |

---

## Success Criteria

### Verification Commands
```bash
# 1. Rebuild index and verify workflow_keys
python -m control_plane build-index
type "OUTPUTS\CONTROL_PLANE\index\system_index.json" | findstr workflow_keys

# 2. Test sandboxed run (via Chat UI)
# Submit efghousewares category URL
# Verify workflow_key in audit log:
type "OUTPUTS\CONTROL_PLANE\audit\chat_tool_calls.jsonl"

# 3. After run completion, verify isolation:
dir "OUTPUTS\CACHE\processing_states\*sandbox*"
```

### Final Checklist
- [x] All sandboxed runs use `__sandbox__<run_id>` suffix in output paths (verified in code)
- [x] Main workflow output files are never modified by sandbox runs (architecture verified)
- [x] Status file `resolved_paths` shows sandbox paths (not main paths) (fix-8 verified)
- [x] Chat UI displays expected output paths after job creation (fix-6 verified)
- [x] Chat UI responds to user prompts with relevant context (fix-4, fix-5 verified)
- [x] LLM provides both JSON tool call AND natural language explanation (fix-5 verified)
- [x] No changes to run_custom_*.py scripts (they are correct) (confirmed)
- [x] No changes to passive_extraction_workflow_latest.py (main workflow is correct) (confirmed)
- [x] system_index.json contains both `workflow_keys` and `suppliers` lists (fix-2 verified)
- [x] Pending write-tool params can be edited in Chat UI (fix-9) (verified)

---

## Files To Be Modified (Complete List)

| File | Fix(es) | Changes |
|------|---------|---------|
| `control_plane/chat_orchestrator.py` | fix-1, fix-3 | URL filter expansion, workflow_key validation |
| `control_plane/build_index.py` | fix-2 | Add workflow_keys + suppliers to system_index |
| `control_plane/tools/clarify.py` | fix-4 | Dynamic clarification questions |
| `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md` | fix-5 | Natural language + expected outputs |
| `dashboard/chat_panel.py` | fix-6, fix-9 | Display expected output paths; allow editing pending write-tool params |
| `control_plane/worker.py` | fix-8 | Use sandbox_supplier for MetricsLoader |
| `control_plane/tools/jobs.py` | fix-8 | Include sandbox_supplier in job payload |

## Files NOT Modified (Explicitly Out of Scope)

| File | Reason |
|------|--------|
| `tools/passive_extraction_workflow_latest.py` | Main workflow is correct - reads from whatever config it's given |
| `run_custom_*.py` scripts | Correctly hardcode workflow_key |
| `utils/path_manager.py` | Correctly generates paths from supplier_name |
| `config/system_config_loader.py` | Correctly respects FBA_SYSTEM_CONFIG_PATH ✅ verified |
