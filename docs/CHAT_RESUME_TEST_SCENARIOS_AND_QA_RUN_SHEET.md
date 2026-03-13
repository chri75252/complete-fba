# Chat Resume Test Scenarios + Manual QA Run Sheet

This document includes two versions in one file:
1) Expanded scenario definitions with expected prompts/responses, file outputs, and reuse rules.
2) Manual QA run sheet (checkbox format) for live execution.

---

## Version 1: Expanded Scenarios (Expected Prompt/Response + File Reuse Matrix)

Placeholders used during live testing:
- `<RUN_A>` = run id from Scenario 1 refresh
- `<SID_A>` = first 8 chars of `<RUN_A>`
- `<RUN_B1>` = first category sandbox run id
- `<SID_B>` = first 8 chars of `<RUN_B1>`
- `<RUN_B2>` = resumed category run id (may be same or new)
- `<SESSION_ID>` = current FastAPI chat session id

### Scenario 1: Product List "Amnesia" Test (Build -> Analyze)

Goal:
- Prove the planner does not ask "Which file?" after generating a product list.

Preconditions:
- Worker running: `python -m control_plane worker`
- FastAPI dashboard running
- Supplier cache exists for `poundwholesale.co.uk`

Step 1
- Prompt:
  - `Generate a new product list containing 5 items from 2 categories for poundwholesale.co.uk.`
- Expected planner tool response:
  - Tool: `build_product_list_from_cached`
  - Params include:
    - `supplier_domain: "poundwholesale.co.uk"`
    - `sample_size: 5`
    - `category_count: 2`
  - Must not ask for path.

Expected runtime result:
- Success with generated file path, usually:
  - `OUTPUTS/PRODUCTS_LISTS/product_list_poundwholesale.co.uk_<DDMMYY>.json`

Expected files touched:
- Created:
  - `OUTPUTS/PRODUCTS_LISTS/product_list_poundwholesale.co.uk_<DDMMYY>.json`
- Read:
  - `OUTPUTS/cached_products/poundwholesale-co-uk_products_cache.json`
- Session transcript updated:
  - `OUTPUTS/CONTROL_PLANE/transcripts/session_<SESSION_ID>.json`

Step 2
- Action:
  - Click `Confirm execute`.
- Expected:
  - Success message with generated product list path.
  - Active context now tracks generated path and supplier.

Step 3
- Prompt:
  - `analyze the json product list you generated`
- Expected planner behavior (fix validation):
  - Tool must be `enqueue_product_list_refresh`
  - Params must include exact `products_path` from Step 1
  - Must not ask: "please provide full path"
  - Must not route to `enqueue_run`

Step 4
- Action:
  - Click `Confirm execute`.

Expected outputs (new run-scoped artifacts):
- New run id returned: `<RUN_A>`
- Job + status + log:
  - `OUTPUTS/CONTROL_PLANE/jobs/pending/job_<RUN_A>.json`
  - `OUTPUTS/CONTROL_PLANE/status/<RUN_A>.json`
  - `OUTPUTS/CONTROL_PLANE/logs/<RUN_A>.log`
- Run-scoped state/linking/report:
  - `OUTPUTS/CACHE/processing_states/poundwholesale_co_uk__sandbox__<SID_A>_processing_state.json`
  - `OUTPUTS/FBA_ANALYSIS/linking_maps/poundwholesale.co.uk__sandbox__<SID_A>/linking_map.json`
  - `OUTPUTS/FBA_ANALYSIS/financial_reports/poundwholesale-co-uk__sandbox__<SID_A>/...`
- Reused input file (should be read, not recreated):
  - `OUTPUTS/PRODUCTS_LISTS/product_list_poundwholesale.co.uk_<DDMMYY>.json`

Pass criteria:
- No path clarification prompt
- Correct tool (`enqueue_product_list_refresh`)
- Correct exact `products_path`

---

### Scenario 1-B: Cancellation & "The Run" Recall Test

Goal:
- Prove the planner/backend can cancel without asking for explicit run id.

Step 1
- Wait about 15 seconds for Scenario 1 analysis to be running.

Step 2
- Prompt:
  - `cancel the run`
- Expected planner behavior:
  - Tool: `cancel_run`
  - Must not ask "which run?"
  - Param style can be either:
    - `run_id: ""` (backend resolves from active context), or
    - explicit `run_id: "<RUN_A>"`

Step 3
- Action:
  - Click `Confirm execute`.

Expected outputs:
- Cancel markers:
  - `OUTPUTS/CONTROL_PLANE/status/<RUN_A>.cancelled`
  - `OUTPUTS/CONTROL_PLANE/lock/cancel_<RUN_A>.flag`
- Status eventually terminal:
  - `OUTPUTS/CONTROL_PLANE/status/<RUN_A>.json`
- Session transcript updated:
  - `OUTPUTS/CONTROL_PLANE/transcripts/session_<SESSION_ID>.json`

Reuse semantics:
- Cancel does not create a new processing-state lineage.
- Existing run-scoped files from Scenario 1 remain the continuity basis.

---

### Scenario 2: Categories Sandboxed Workflow (Run -> Cancel -> Resume)

Goal:
- Prove category sandbox resume continues the same sandbox lineage after interruption.

Prompt 1:
- `i want you to analyze 10 products from each of the following categroies : "https://angelwholesale.co.uk/Category/All-Roleplay-toys",  "https://angelwholesale.co.uk/Category/All-School-bags"`

Expected planner response:
- Tool: `enqueue_run`
- Params should include:
  - `supplier_domain: "angelwholesale.co.uk"`
  - `category_urls`: both URLs
  - `max_products_per_category: 10`
  - `max_products: 20` (2 categories x 10 each)

Execute and run ~1 minute:
- Click `Confirm execute`.

Expected outputs (first category run):
- `<RUN_B1>` created
- Job/status/log:
  - `OUTPUTS/CONTROL_PLANE/jobs/pending/job_<RUN_B1>.json`
  - `OUTPUTS/CONTROL_PLANE/status/<RUN_B1>.json`
  - `OUTPUTS/CONTROL_PLANE/logs/<RUN_B1>.log`
- Overrides:
  - `OUTPUTS/CONTROL_PLANE/overrides/<RUN_B1>/system_config.merged.json`
  - `OUTPUTS/CONTROL_PLANE/overrides/<RUN_B1>/categories_subset.json`
- Run-scoped state/linking/cache/report:
  - `OUTPUTS/CACHE/processing_states/angelwholesale_co_uk__sandbox__<SID_B>_processing_state.json`
  - `OUTPUTS/FBA_ANALYSIS/linking_maps/angelwholesale.co.uk__sandbox__<SID_B>/linking_map.json`
  - `OUTPUTS/cached_products/angelwholesale-co-uk__sandbox__<SID_B>_products_cache.json`
  - `OUTPUTS/FBA_ANALYSIS/financial_reports/angelwholesale-co-uk__sandbox__<SID_B>/...`
- Session transcript updated:
  - `OUTPUTS/CONTROL_PLANE/transcripts/session_<SESSION_ID>.json`

Cancel phase:
- Prompt: `cancel the run`
- Expected: `cancel_run` without requiring manual run id

Resume phase:
- Prompt: `resume the run from where it left off`

Expected planner behavior:
- Tool: `enqueue_run` (category workflow)
- Must resume the same sandbox lineage context
- Must not ask category URLs again if recoverable from context/overrides
- Must not fork into non-sandbox namespace

Expected outputs on resumed enqueue:
- New control-plane job/status/log may be created (`<RUN_B2>`), this is acceptable:
  - `OUTPUTS/CONTROL_PLANE/jobs/pending/job_<RUN_B2>.json`
  - `OUTPUTS/CONTROL_PLANE/status/<RUN_B2>.json`
  - `OUTPUTS/CONTROL_PLANE/logs/<RUN_B2>.log`
  - `OUTPUTS/CONTROL_PLANE/overrides/<RUN_B2>/system_config.merged.json`
  - `OUTPUTS/CONTROL_PLANE/overrides/<RUN_B2>/categories_subset.json`

Must be reused (same sandbox lineage):
- `OUTPUTS/CACHE/processing_states/angelwholesale_co_uk__sandbox__<SID_B>_processing_state.json`
- `OUTPUTS/FBA_ANALYSIS/linking_maps/angelwholesale.co.uk__sandbox__<SID_B>/linking_map.json`
- `OUTPUTS/cached_products/angelwholesale-co-uk__sandbox__<SID_B>_products_cache.json`
- `OUTPUTS/FBA_ANALYSIS/financial_reports/angelwholesale-co-uk__sandbox__<SID_B>/...`

Must NOT happen:
- Non-canonical lineage creation like `angelwholesale.co.uk__<SID_B>` (without `sandbox__`)
- Empty resumed category subset (`category_urls: []`) when context is recoverable

---

## Version 2: Manual QA Run Sheet (Checkbox Format)

Use this as a live run checklist.

### Global Setup
- [ ] Start worker: `python -m control_plane worker`
- [ ] Confirm FastAPI dashboard is running
- [ ] Confirm supplier caches exist for tested domains
- [ ] Open these folders in parallel for live monitoring:
  - [ ] `OUTPUTS/CONTROL_PLANE/jobs/pending/`
  - [ ] `OUTPUTS/CONTROL_PLANE/status/`
  - [ ] `OUTPUTS/CONTROL_PLANE/logs/`
  - [ ] `OUTPUTS/CACHE/processing_states/`
  - [ ] `OUTPUTS/FBA_ANALYSIS/linking_maps/`
  - [ ] `OUTPUTS/CONTROL_PLANE/transcripts/`

### Scenario 1 QA

#### 1A Build List
- [ ] Prompt entered: `Generate a new product list containing 5 items from 2 categories for poundwholesale.co.uk.`
- [ ] Proposed tool is `build_product_list_from_cached`
- [ ] Tool params include `sample_size=5`, `category_count=2`
- [ ] No path clarification requested
- [ ] Clicked `Confirm execute`
- [ ] Success result contains generated `products_path`
- [ ] File exists: `OUTPUTS/PRODUCTS_LISTS/product_list_poundwholesale.co.uk_<DDMMYY>.json`

#### 1A Analyze Generated File (Amnesia check)
- [ ] Prompt entered: `analyze the json product list you generated`
- [ ] Proposed tool is `enqueue_product_list_refresh`
- [ ] `products_path` exactly matches generated file from previous step
- [ ] No "please provide full path" question
- [ ] Clicked `Confirm execute`
- [ ] Captured `<RUN_A>`
- [ ] File exists: `OUTPUTS/CONTROL_PLANE/jobs/pending/job_<RUN_A>.json`
- [ ] File exists: `OUTPUTS/CONTROL_PLANE/status/<RUN_A>.json`
- [ ] File exists: `OUTPUTS/CONTROL_PLANE/logs/<RUN_A>.log`
- [ ] File exists: `OUTPUTS/CACHE/processing_states/poundwholesale_co_uk__sandbox__<SID_A>_processing_state.json`
- [ ] File exists: `OUTPUTS/FBA_ANALYSIS/linking_maps/poundwholesale.co.uk__sandbox__<SID_A>/linking_map.json`

#### 1B Cancel & Run Recall
- [ ] Waited ~15 seconds (run active)
- [ ] Prompt entered: `cancel the run`
- [ ] Proposed tool is `cancel_run`
- [ ] No "which run" clarification
- [ ] Clicked `Confirm execute`
- [ ] File exists: `OUTPUTS/CONTROL_PLANE/status/<RUN_A>.cancelled`
- [ ] File exists: `OUTPUTS/CONTROL_PLANE/lock/cancel_<RUN_A>.flag`

### Scenario 2 QA

#### 2A Initial Category Run
- [ ] Prompt entered with two angel category URLs and 10-per-category request
- [ ] Proposed tool is `enqueue_run`
- [ ] Params include both category URLs
- [ ] Params include `max_products_per_category=10`
- [ ] Params include `max_products=20`
- [ ] Clicked `Confirm execute`
- [ ] Captured `<RUN_B1>`
- [ ] Waited ~1 minute
- [ ] File exists: `OUTPUTS/CONTROL_PLANE/overrides/<RUN_B1>/categories_subset.json`
- [ ] File exists: `OUTPUTS/CACHE/processing_states/angelwholesale_co_uk__sandbox__<SID_B>_processing_state.json`
- [ ] File exists: `OUTPUTS/FBA_ANALYSIS/linking_maps/angelwholesale.co.uk__sandbox__<SID_B>/linking_map.json`

#### 2B Cancel
- [ ] Prompt entered: `cancel the run`
- [ ] Proposed tool is `cancel_run`
- [ ] No run-id clarification
- [ ] Clicked `Confirm execute`

#### 2C Resume
- [ ] Prompt entered: `resume the run from where it left off`
- [ ] Proposed tool is `enqueue_run`
- [ ] Resume does not ask again for category URLs
- [ ] No non-sandbox forked namespace appears
- [ ] If new run id `<RUN_B2>` is created, only control-plane enqueue artifacts are new

### Reuse/Non-Reuse Assertions

Must be reused after resume (Scenario 2):
- [ ] `OUTPUTS/CACHE/processing_states/angelwholesale_co_uk__sandbox__<SID_B>_processing_state.json`
- [ ] `OUTPUTS/FBA_ANALYSIS/linking_maps/angelwholesale.co.uk__sandbox__<SID_B>/linking_map.json`
- [ ] `OUTPUTS/cached_products/angelwholesale-co-uk__sandbox__<SID_B>_products_cache.json`

Expected new files on resumed enqueue:
- [ ] `OUTPUTS/CONTROL_PLANE/jobs/pending/job_<RUN_B2>.json`
- [ ] `OUTPUTS/CONTROL_PLANE/status/<RUN_B2>.json`
- [ ] `OUTPUTS/CONTROL_PLANE/logs/<RUN_B2>.log`
- [ ] `OUTPUTS/CONTROL_PLANE/overrides/<RUN_B2>/system_config.merged.json`
- [ ] `OUTPUTS/CONTROL_PLANE/overrides/<RUN_B2>/categories_subset.json`

Must not happen:
- [ ] No `supplier__<id>` lineage without `sandbox__`
- [ ] No resumed `categories_subset.json` with `category_urls: []` (when recoverable context exists)

### Transcript Assertions (new mandatory behavior)
- [ ] Session transcript file exists:
  - `OUTPUTS/CONTROL_PLANE/transcripts/session_<SESSION_ID>.json`
- [ ] Transcript updates after final-answer events
- [ ] Transcript updates after approval rejection/execution
- [ ] Transcript is written before `/api/chat/reset` clears RAM state

### Final Pass/Fail
- [ ] Scenario 1 passed (no product-list amnesia)
- [ ] Scenario 1-B passed (implicit run recall on cancel)
- [ ] Scenario 2 passed (category sandbox resume continuity)
- [ ] Transcript persistence passed (distinct per-session file updated correctly)
