# Deep Session Handoff

## Superseding Addendum - 2026-03-12 Post-Plan Implementation

This addendum supersedes any earlier handoff statements that said transcript persistence was optional or that implementation had not started.

Current authoritative state:
- The surgical implementation has now been applied in the allowed file set only.
- Transcript persistence is now treated as a required implemented feature, not an optional enhancement.
- The old statements in this handoff that say transcript persistence is optional are now stale and should be ignored.
- Optional mitigations `H` and `I` remain unimplemented by design.

### What Was Implemented
- `A` implemented in `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md`
  - Added explicit product-list resume routing rules.
  - Added explicit distinction between product-list resume and category sandbox resume.
- `B` implemented in `control_plane/chat_orchestrator.py`
  - Added deterministic wrong-tool rewrite for product-list resume requests inside `agent_plan_step(...)`.
  - If the model chooses `enqueue_run` for a resume-style request with no category URLs but active context has `last_products_path` and `last_supplier_domain`, the backend rewrites to `enqueue_product_list_refresh`.
- `C` implemented in `control_plane/chat_orchestrator.py`
  - `_normalize_sandbox_suffix(...)` now canonicalizes bare 8-char suffixes and full UUID-style values to `sandbox__<id>`.
- `D` implemented in `control_plane/chat_orchestrator.py`
  - Added narrowly scoped legacy sandbox alias recovery for resume lookup only.
  - This is used in contextual candidate scoring and in category subset recovery.
  - It is not propagated into tool or workflow layers.
- `E` implemented in `dashboard/api.py`
  - `/api/chat/reset` now clears `last_run_id`, `last_products_path`, `last_supplier_domain`, and `last_sandbox_supplier`.
  - Reset now starts a new chat session id after persisting the prior one.
- `F` implemented in `control_plane/chat_orchestrator.py`
  - `{sandbox_id}` placeholder substitution now works in expected output previews.
- `G` implemented in `control_plane/worker.py`
  - Exit-code-0 runs that contain known semantic abort markers are now marked `failed` rather than `done`.
- `J` implemented in `dashboard/api.py`, `control_plane/audit.py`, and `control_plane/paths.py`
  - Per-session transcript persistence now writes distinct files under `OUTPUTS/CONTROL_PLANE/transcripts/session_<session_id>.json`.
  - Transcripts are persisted before RAM wipe on `/api/chat/reset`.
  - Transcripts are also persisted on final answer, step-limit final answer, approval rejection, and approval execution.

### Files Edited In This Implementation Pass
- `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md`
- `control_plane/chat_orchestrator.py`
- `dashboard/api.py`
- `control_plane/audit.py`
- `control_plane/paths.py`
- `control_plane/worker.py`
- `backup/chat_resume_surgical_20260312/REVERT_TRACKING.md`

### Backup Set Created Before Editing
- Root backup dir: `backup/chat_resume_surgical_20260312/`
- Backed up files:
  - `backup/chat_resume_surgical_20260312/.sisyphus/notepads/handoff/session_handoff.md`
  - `backup/chat_resume_surgical_20260312/dashboard/api.py`
  - `backup/chat_resume_surgical_20260312/control_plane/chat_orchestrator.py`
  - `backup/chat_resume_surgical_20260312/control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md`
  - `backup/chat_resume_surgical_20260312/control_plane/audit.py`
  - `backup/chat_resume_surgical_20260312/control_plane/paths.py`
  - `backup/chat_resume_surgical_20260312/control_plane/worker.py`

### Prometheus Final Review Outcome
Prometheus / plan-builder review was performed before coding. The actionable final review was:
- edit order:
  1. planner instructions
  2. `chat_orchestrator.py`
  3. `dashboard/api.py`
  4. `control_plane/audit.py`
  5. change-tracking markdown
  6. `control_plane/worker.py` last
- backup set:
  - create full dated backup for all edited files
- validation order:
  - planner routing
  - sandbox normalization
  - reset semantics
  - transcript persistence
  - worker semantic-abort behavior last
- risk note:
  - keep backward-compatibility recovery narrow; do not relax validation broadly

### Verification Performed After Implementation
- `lsp_diagnostics` run on:
  - `dashboard/api.py`
  - `control_plane/chat_orchestrator.py`
  - `control_plane/audit.py`
  - `control_plane/paths.py`
  - `control_plane/worker.py`
- Results:
  - no errors
  - only pre-existing or non-blocking hints remained:
    - unused imports in `dashboard/api.py`
    - unreachable-code hint in `control_plane/chat_orchestrator.py`
    - unused-parameter hint in `control_plane/worker.py`
- `python -m py_compile` passed for:
  - `dashboard/api.py`
  - `control_plane/chat_orchestrator.py`
  - `control_plane/audit.py`
  - `control_plane/paths.py`
  - `control_plane/worker.py`
- runtime sanity check passed:
  - `_normalize_sandbox_suffix('a7ce7aa2', 'ignored-run-id')` -> `sandbox__a7ce7aa2`
  - `_normalize_sandbox_suffix('', '12345678-aaaa-bbbb-cccc-1234567890ab')` -> `sandbox__12345678`
  - `write_session_transcript('sanitycheck', {'ok': True})` created a session transcript successfully, then the disposable file was removed

### Important Behavioral Changes
- FastAPI chat sessions now have explicit `session_id` and `session_started_at` stored in RAM state.
- `chat_state["trace"]` is now populated during the streaming loop so persisted session files can contain meaningful step traces rather than an always-empty trace list.
- Reset now persists the current session file before wiping RAM and then starts a fresh session id.
- Current source still contains New Chat button and SSE trace plumbing. This implementation does not add cache-busting or change visible explanation wording.

### Still Not Implemented
- `H` cache-busting query strings for static assets
- `I` stronger explanation wording for richer visible step rationale

### Current Open Questions After Implementation
- UNKNOWN (not verified): whether the live browser symptom that previously hid New Chat or step trace was caused by stale assets, different deployment, or another runtime issue.
- UNKNOWN (not verified): whether the new transcript persistence should later be mirrored into append-only audit JSONL as well as per-session files. Current implementation only guarantees distinct per-session JSON files.

### Continuation Guidance From This Point
- Do not resume from the earlier "plan-only" state in this handoff.
- The implementation is now in place and the next session should focus on targeted behavioral validation against the known problematic resume scenarios.
- Highest-priority regression checks next session:
  1. product-list resume now routes to `enqueue_product_list_refresh`
  2. malformed bare suffixes are normalized to `sandbox__<id>`
  3. `/api/chat/reset` clears all `last_*` keys
  4. per-session transcript files are written before RAM reset
  5. semantic-abort log markers now land in failed status rather than done

## Phase 1 - Work Type Classification

Primary work type:
- [x] DEBUGGING
- [ ] CODE_IMPLEMENTATION
- [ ] REFACTORING
- [ ] ARCHITECTURE
- [ ] DOCUMENTATION
- [ ] RESEARCH

Secondary work types that materially applied in this session:
- ARCHITECTURE
- RESEARCH
- DOCUMENTATION

Reason for primary classification:
- This session was primarily a read-only debugging / root-cause investigation of FastAPI chat, control-plane resume behavior, planner tool choice, sandbox naming, reset semantics, status reporting, and stale UI hypotheses.
- No production code was edited for the underlying bug set during the investigation phase.
- The user explicitly asked for a comprehensive report and surgical implementation plan for review before any implementation.

---

## Phase 2 - Universal Foundation

### 1. Session Metadata
- Session ID: `ses_325d21b4effeGxyxq3jsXPXr1p`
- Work Type: `DEBUGGING` (primary), `ARCHITECTURE` / `RESEARCH` / `DOCUMENTATION` (secondary)
- Duration: `1 days, 7 hours` according to `session_info`
- Token Utilization: `UNKNOWN (not verified)`
- Context Window Target Mentioned By User: `600K token Gemini 3.1 Pro session`
- Compaction Events: current session metadata shows agent list includes `compaction`; exact count `UNKNOWN (not verified)`
- Models Used:
  - Current agent runtime: `openai/gpt-5.4`
  - User continuity target: `Gemini 3.1 Pro 600K` (from user handoff instruction)
- Start Time: `2026-03-10T23:56:06.795Z`
- End Time for this handoff write: `2026-03-12` current local session time; exact ISO end timestamp `UNKNOWN (not verified at write time)`
- Current repository path: `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-`
- Platform: `Windows`
- Git repository: `No (per environment metadata)`

### 2. Executive Objective
Produce an evidence-backed, read-only investigation of the FastAPI chat / control-plane behavior, correct earlier misinterpretations, verify disputed findings through triangulation, generate an updated comprehensive report plus a surgical fix plan for user review, and then write a continuity-grade handoff for compaction / next-session continuation.

### 3. Session Narrative Arc

#### Where we started
- The session began with a user request to investigate previously observed issues in the FastAPI chat UI / control-plane behavior.
- The user explicitly required a read-only investigation at first: no code edits, no background agents performing edits, and only an extensive detailed report.
- The user wanted triangulation across multiple sources of truth:
  - existing handoff notes
  - current code
  - run artifacts
  - logs
  - job/status files
  - generated outputs
  - expected output predictions
- The user also wanted answers to specific questions:
  - where injected prompt context comes from
  - whether restarting `uvicorn` refreshes that context
  - why the New Chat button "wasn't added"
  - any other issues discovered
- The initial inherited handoff in `.sisyphus/notepads/handoff/session_handoff.md` strongly asserted a Streamlit-vs-FastAPI architecture mismatch and claimed prior fixes were irrelevant to FastAPI.

#### The exploration path
- We first read the existing handoff and compared its claims against the current codebase instead of trusting it.
- We inspected `dashboard/api.py` and `control_plane/chat_orchestrator.py` to verify whether FastAPI actually passed active context into planner hints and prompt construction.
- We then inspected `dashboard/templates/index.html` and `dashboard/static/js/app.js` to verify whether the New Chat button and SSE trace UI existed in current source.
- Next, we investigated resume behavior by reading:
  - `control_plane/tools/product_list_refresh.py`
  - `control_plane/chat_orchestrator.py`
  - `control_plane/worker.py`
  - job/status/log/override files under `OUTPUTS/CONTROL_PLANE/...`
  - processing states under `OUTPUTS/CACHE/processing_states/...`
- We matched code behavior to concrete runs using specific run IDs rather than reasoning from code alone.
- We also inspected `OUTPUTS/CONTROL_PLANE/audit/chat_tool_calls.jsonl` to confirm which planner tool the LLM actually selected in the problematic resume scenarios.
- After establishing a first-pass report, the user supplied a second agent's report extract claiming several missed or understated findings.
- We then re-investigated each disputed point in depth:
  - wrong tool selection vs wrong suffix
  - cache-busting
  - SSE reasoning-step visibility
  - transcript persistence
- We consulted multiple internal agents:
  - explore agents for resume/tool-selection and frontend/transcript/cache issues
  - oracle for correctness / blind-spot validation
  - Momus (Plan Critic) for scope control on the surgical fix plan

#### Key discoveries made along the way
- The old handoff is materially stale for the current codebase.
- Current FastAPI chat **does** use `chat_state` and **does** pass it into `agent_plan_step(...)`.
- Current prompt assembly **does** inject `<active_context>` from FastAPI state; the old handoff’s blanket statement that FastAPI never populated planner hints is false for current code.
- The New Chat button already exists in current source.
- The real New Chat problem is partial reset, not absence of the button in source.
- Product-list refresh jobs themselves are correctly sandboxed.
- The bad non-sandbox lineage is introduced later during resume, not during the original refresh job.
- Product-list resume failures are not caused by only one thing:
  - there is a wrong-tool problem in the planner path for product-list resume
  - there is also a sandbox naming mismatch in `enqueue_run` resume handling
- The category-resume case that looked fixed was actually a false positive caused by reusing a previously created malformed non-sandbox fork.
- Expected output previews are heuristic and can be wrong.
- Worker status can say `done` even when workflow semantics clearly aborted.

#### How direction shifted based on findings
- Early direction: validate whether the stale handoff’s Streamlit-vs-FastAPI explanation was still true.
- First pivot: once we confirmed FastAPI `chat_state` is actually wired into planner hints and `<active_context>`, the session changed from “architecture mismatch” to “current FastAPI state + resume semantics + UI reset correctness”.
- Second pivot: after verifying the New Chat button existed in source, the question changed from “why wasn’t it added?” to “why did the live UI behave as if it wasn’t there?” and “what is reset actually clearing?”
- Third pivot: after comparing initial product-list refresh jobs to later resume jobs, the root cause shifted from “refresh resume broke state” to “resume selected the wrong path and created a new malformed lineage.”
- Fourth pivot: after the second agent’s report extract, we explicitly re-tested whether wrong tool choice was merely a consequence of bad suffix handling or a deeper independent issue.
- Fifth pivot: after Oracle and Momus review, the plan was tightened to distinguish core required fixes from optional mitigations.

#### Side investigations (including dead ends or incomplete branches)
- We explored whether the old handoff’s explanation about missing FastAPI active-context injection was still accurate; it was not.
- We checked whether the current source truly lacked a New Chat button; it did not.
- We explored whether missing visible reasoning steps were caused by stale JS alone; this remained unproven.
- We explored whether transcript persistence should be in the essential fix set; conclusion: no, not for this bug cluster.
- Two late explore agents launched specifically for handoff mining returned stale / mixed conclusions drawn from older memory context and are **not** authoritative for current-session facts; do not rely on them over direct code/artifact evidence.

#### Where we ended and why
- We ended with a verified, evidence-backed report and a surgical implementation plan for user review, not implementation.
- We also ended with reviewer feedback from Oracle and Momus that tightened the wording and scope:
  - treat cache-busting as optional mitigation, not proven root cause
  - keep transcript persistence out of the core fix set
  - distinguish minimum required fixes from recovery / preview / status improvements
- The final continuity need is to preserve this corrected state for compaction and future continuation so the next agent does **not** revert to the stale Streamlit-centered narrative in the previous handoff.

### 4. User Direction Changes & Corrections

#### Initial approach
- Initial approach in this session: perform a read-only investigation and generate a detailed report.

#### Direction Change #1
- What you told me: do not edit any files for now; background agents must also be read-only; generate only an extensive detailed report.
- New approach: fully read-only investigation; no code edits; use background agents only for analysis.
- Files affected: none (read-only phase).

#### Direction Change #2
- What you told me: use triangulation with as many sources of truth as needed; review handoff, pasted chat context, referred files, generated files, whether present or absent.
- New approach: artifact-first investigation across code, logs, status files, job payloads, overrides, processing states, audit JSONL, and prior handoff.
- Files affected: read-only inspection of `dashboard/api.py`, `control_plane/chat_orchestrator.py`, `control_plane/tools/product_list_refresh.py`, `control_plane/worker.py`, run artifacts under `OUTPUTS/CONTROL_PLANE`, processing states under `OUTPUTS/CACHE`, and the old handoff file.

#### Direction Change #3
- What you told me: verify how the chat retrieves injected information and why New Chat wasn’t added.
- New approach: inspect current FastAPI path and frontend source directly rather than inferring from prior docs.
- Files affected: `dashboard/api.py`, `dashboard/templates/index.html`, `dashboard/static/js/app.js`, `control_plane/chat_orchestrator.py`.

#### Direction Change #4
- What you told me: after reading the other agent’s report extract, verify whether those points were correct or misinterpreted and update the report and plan accordingly.
- New approach: re-open investigation and explicitly verify C1-C4 (wrong tool, cache-busting, SSE reasoning visibility, transcript persistence) rather than only defending the prior report.
- Files affected: `OUTPUTS/CONTROL_PLANE/audit/chat_tool_calls.jsonl`, `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md`, `dashboard/api.py`, `dashboard/static/js/app.js`, `control_plane/audit.py`, `control_plane/tools/product_list_refresh.py`, `control_plane/worker.py`.

#### Direction Change #5
- What you told me: once the updated report and plan are complete, run Oracle and Momus to verify correctness and ensure the plan is surgical.
- New approach: consult Oracle and Momus after synthesizing the report / plan, then incorporate their critique before finalizing handoff.
- Files affected: no code edits; analysis and review only.

#### Direction Change #6
- What you told me: generate a full handoff report to be referenced during compaction summary; after handoff, continuation should pick up exactly where it left off until the earlier prompt is fully addressed.
- New approach: write a new exhaustive handoff that supersedes the stale previous one and preserves the fact that the earlier deliverable is a review-ready report + fix plan, not an implementation yet.
- Files affected:
  - `.sisyphus/notepads/handoff/session_handoff.md` (to overwrite with corrected handoff)
  - backup copy required first

### 5. Exact User Requirements (verbatim where possible)
- "MAKE SURE YOU DONT EDIT ANY FILES FOR NOW"
- "MAKE SURE WHENVER ANY AGENTS ARE LAUNCHED YOU INSTUCT THEM NOT TO PERFORM ANY EDITS."
- "YOU WILL ** ONLY GENERATE AN EXTENSIVE A DETAILED REPORT"
- "YOU WILL USE TRIANGULATION APPROACH"
- "I EXPECT YOU TO GO THROUGH EVERY CHAT I PASTED BELOW, ALL THE DIFFERENT FILES REEFERED BELOW AND THE GERNATED FILES"
- "ALSO WHILE YOURRE AT IT, I WANT YOU TO CONFIRM HOW AND FROM WHERE IS THE CHAT RETIEVING THE INFORMATION WHICH IS BEING INJECTED ALONG WITH EVERY PROMPT I NIPUTE"
- "AND OF COURSE WHY 'NEWCHAT BUTTON WASNT ADDED.'"
- "YOU WILL ALSO OF COURSE MENTION ANY OTHER ISSUE ( OR ISSUES YOU COME ACCROSS."
- "once the report and plan are complete you will use @oracle and @Momus (Plan Critic)"
- "** once the report and plan have gon through and includeed all the above ... you will generate i for me to review prior to iiimplementing it. **"
- "generate a hadoff report that you willr efernce during the compaction summary"
- "nce you complete the handoff reprt in full, you will continue as you were from exactly where you left off until youd have completed answered/addressed my earlier pmpt/youd have generated the complete report and plan needed"

### 6. Environment + Constraints
- Current working directory: `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-`
- OS: `Windows`
- Shell environment used for backup copy: `PowerShell via bash tool`
- Git repo present: `No`
- Git operations allowed: `No` (explicitly forbidden by repo instructions and user preference)
- Protected files: do not edit `tools/passive_extraction_workflow_latest.py`, `tools/configurable_supplier_scraper.py`, or `run_custom_*.py`
- User preference: keep fixes surgical and confined to `control_plane/*` and `dashboard/*`
- This investigation phase was intentionally read-only except for writing this handoff and its required backup
- Existing handoff backup created at:
  - `backup/session_handoff_refresh_20260312/session_handoff.md`
- Important caveat:
  - the older handoff content currently in `.sisyphus/notepads/handoff/session_handoff.md` before overwrite was stale and Streamlit-centered; do not continue from it.

### 7. Topic Inventory - Everything Discussed This Session

#### Primary Topics
- FastAPI prompt injection path — confirmed current active-context data flow
- New Chat button / reset semantics — button exists, reset incomplete
- Product-list resume failure — wrong tool + sandbox naming mismatch
- Category resume false-positive — malformed non-sandbox fork reused
- Empty `categories_subset.json` aborts — caused by strict supplier-name equality after malformed resume
- Expected output path prediction — heuristic / preview-only, not authoritative runtime truth
- Worker false `done` state — semantic aborts can still land in `done`

#### Secondary Topics Explored
- Whether old handoff remained accurate — it did not
- Whether stale browser assets plausibly explain missing live button / trace — plausible, not proven
- Whether SSE reasoning-step visibility was broken in current code — not proven; code path exists
- Whether transcript persistence is essential to this fix set — no, observability only
- Whether product-list resume could be handled by `enqueue_product_list_refresh` with the same run ID — yes

#### Investigations (Completed)
- Existing handoff validity → stale / misleading for current code
- FastAPI state injection path → confirmed via `dashboard/api.py` and `control_plane/chat_orchestrator.py`
- New Chat presence in source → confirmed in template + JS + API
- Reset completeness → confirmed incomplete
- Original product-list refresh namespace formation → confirmed correct sandboxing
- Resume path namespace formation → confirmed malformed non-sandbox lineage possible
- Actual tool selection in bad resume cases → confirmed in `chat_tool_calls.jsonl`
- Empty override subset cause → matched to strict supplier equality
- Worker semantic status labeling → confirmed `done` can hide semantic abort
- Oracle / Momus review → completed and incorporated

#### Investigations (Incomplete / Open)
- Exact reason the live browser instance lacked a visible New Chat button despite current source containing it → UNKNOWN (not verified)
- Exact reason some live traces may have shown only "Thinking" instead of step trace → UNKNOWN (not verified)
- Whether future implementation should include transcript persistence → not required for current bug cluster; decision still open if user wants observability improvements

#### External Resources Consulted
- External web documentation: none in this session
- Internal agent consultations:
  - resume tool-selection explore
  - frontend cache / SSE / transcript explore
  - Oracle validation
  - Momus scope critique
- Internal session metadata tools:
  - `session_list`
  - `session_info`

#### Tools / Technologies Discussed
- FastAPI chat path in `dashboard/api.py`
- frontend JS in `dashboard/static/js/app.js`
- prompt/planner construction in `control_plane/chat_orchestrator.py`
- planner instructions in `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md`
- refresh enqueue path in `control_plane/tools/product_list_refresh.py`
- worker terminal state logic in `control_plane/worker.py`
- audit logging in `control_plane/audit.py`
- artifact locations under `OUTPUTS/CONTROL_PLANE/*` and `OUTPUTS/CACHE/*`

#### Key Terms / Concepts Defined This Session
- Product-list resume wrong-tool issue: planner selected `enqueue_run` for a previously cancelled product-list refresh resume
- Resume sandbox naming mismatch: `_normalize_sandbox_suffix` accepts bare run fragments like `a7ce7aa2`, causing `supplier__a7ce7aa2` instead of canonical `supplier__sandbox__a7ce7aa2`
- False-positive resume success: later resume appears correct only because it reuses an already malformed lineage
- Partial reset bug: New Chat clears visible chat but leaves `last_*` context keys in memory
- Preview / expected-output mismatch: predicted paths are heuristic, not authoritative runtime lineage

---

## Phase 3 - Work-Type-Specific Sections (DEBUGGING)

### Error Pattern Analysis

#### Error / Problem Types Encountered
- Wrong active-context assumptions from old handoff
  - Description: prior handoff claimed FastAPI was not populating planner hints / active context
  - Frequency: foundational to earlier misdirection
- Resume tool mis-selection for product-list resume
  - Description: bad resume prompt selected `enqueue_run` instead of `enqueue_product_list_refresh`
  - Frequency: confirmed in audited product-list resume cases
- Resume sandbox naming mismatch
  - Description: `enqueue_run` resume accepted bare suffix fragments and built malformed supplier namespace
  - Frequency: confirmed in pound / clearance and angel resume lineage
- Partial reset state leakage
  - Description: New Chat reset leaves `last_*` values in `chat_state`
  - Frequency: deterministic in current code
- Semantic failure mislabeled as done
  - Description: `worker.py` marks `done` on exit code 0 even when logs show workflow aborted semantically
  - Frequency: confirmed in specific runs
- Live UI stale-asset hypothesis
  - Description: source contains button/trace code, but live UI symptoms suggested old assets or different deployment
  - Frequency: observed symptom, exact cause unverified

#### Conditions Triggering Errors / Misbehavior
- Product-list refresh resumed by vague natural language after cancel:
  - example user text: `i now want you to resume the session you cancelled from where you left off`
  - resulting wrong tool in audit: `enqueue_run`
- Resume logic using bare sandbox suffix such as `a7ce7aa2` or `6c89a211`
- Product-list resume via `enqueue_run` with no category URLs and malformed sandbox supplier name
- FastAPI New Chat reset without clearing `last_run_id`, `last_products_path`, `last_supplier_domain`, `last_sandbox_supplier`
- Worker process exiting 0 despite semantic abort string in logs

#### Concrete Artifact Patterns
- Initial correct product-list refresh job types:
  - `run_product_list_refresh`
- Wrong resumed job types:
  - `run_workflow`
- Empty subset file pattern:
  - `category_urls: []`
- Log pattern proving semantic failure:
  - `CUSTOM MODE FAILED: No URLs found in predefined list. Aborting.`

### Debugging Hypothesis Registry

| Hypothesis | Evidence For | Evidence Against | Status |
|---|---|---|---|
| FastAPI was never injecting active context | old handoff said so | `dashboard/api.py` passes `session_state=chat_state`; `chat_orchestrator.py` consumes planner hints and builds `<active_context>` | RULED OUT |
| New Chat button was never added to current source | live user symptom suggested absence | `dashboard/templates/index.html` and `dashboard/static/js/app.js` show it exists | RULED OUT |
| Product-list refresh job itself creates bad namespace | malformed states appeared after resume | initial refresh enqueue path uses canonical `__sandbox__<id>` | RULED OUT |
| Resume failure is only a naming bug | malformed supplier names confirmed | audit proves wrong tool selection also happened | RULED OUT |
| Resume failure is only a wrong-tool bug | audit proves wrong tool | malformed sandbox suffix also independently corrupts lineage and category recovery | RULED OUT |
| Missing visible trace is definitely stale JS | no cache-busting, plausible | current backend/frontend trace path exists; no direct runtime proof | PENDING / UNPROVEN |
| Transcript persistence is required to fix current bug cluster | can help observability | not part of current FastAPI control path, not needed to fix resume/reset bugs | RULED OUT |
| Worker `done` status is reliable | normal expectation | `worker.py` logic only detects fatal traceback, not semantic abort markers | RULED OUT |

### Failed Approaches (DO NOT RETRY)
1. Trusting the old Streamlit-centered handoff as source of truth -> failed because current FastAPI code contradicts it -> DO NOT RETRY.
2. Treating the absence of the New Chat button in the live UI as proof the current source lacked the feature -> failed because source already contains it -> DO NOT RETRY.
3. Explaining product-list resume failure as only a suffix normalization issue -> incomplete because audit logs prove wrong tool selection also happened -> DO NOT RETRY.
4. Treating cache-busting as a proven root cause -> unsupported by current evidence -> DO NOT RETRY.
5. Elevating transcript persistence into the essential fix set for this bug cluster -> over-scoped for the confirmed issues -> DO NOT RETRY.
6. Using stale handoff-mining explore outputs that reintroduced old `_extract_active_context` / Streamlit narrative -> inconsistent with current direct code/artifact evidence -> DO NOT RETRY.

### Current Debugging Theory
The currently supported theory is a coupled failure chain:
1. In product-list resume conversations, the planner can select `enqueue_run` instead of `enqueue_product_list_refresh`.
2. If `enqueue_run` is selected with a bare suffix like `6c89a211`, `_normalize_sandbox_suffix` accepts it raw.
3. That creates a malformed supplier lineage like `clearance-king.co.uk__6c89a211` instead of `clearance-king.co.uk__sandbox__6c89a211`.
4. Resume fallback then tries to recover categories by strict exact supplier-domain equality and fails to match the canonical prior sandbox context.
5. Empty `category_urls` are written to `categories_subset.json`.
6. The workflow aborts semantically with "CUSTOM MODE FAILED".
7. The worker can still report `done` because process exit code is 0 and log parsing only treats fatal tracebacks as failure.

### Next Debugging Step
If the next session is still in report / plan mode, do this first:
1. Re-read this handoff.
2. Re-read the validated core fix set A+B+C+E and scoped extras D/F/G.
3. Do **not** reopen the old Streamlit-centered theory.
4. If the user asks to implement, implement the approved fix set surgically in `control_plane/*` and `dashboard/*` only.

---

## Architecture / Decision Registry (Secondary but important)

| Decision | Rationale | Alternatives Considered | Status |
|---|---|---|---|
| Treat current FastAPI code and artifacts as authority over old handoff | direct code/artifact evidence outranks stale notes | continue from old handoff | FINAL - DO NOT REVISIT |
| Split findings into CONFIRMED / LIKELY / UNPROVEN | user asked for maximum precision | collapse all into one certainty level | FINAL - DO NOT REVISIT |
| Keep implementation plan surgical and review-only | user explicitly asked for review before implementation | implement immediately | FINAL - DO NOT REVISIT |
| Core required fix set = A+B+C+E | Oracle validated these as minimum necessary for the chat/resume bug cluster | broader implementation immediately | FINAL - DO NOT REVISIT |
| Recovery / correctness extras D/F/G are separate from minimum bug fix set | they address backward recovery, previews, and worker status correctness | lump all as mandatory core | FINAL - DO NOT REVISIT |
| Cache-busting belongs in optional mitigation, not proven RCA | plausible stale asset explanation but not directly proven | classify as confirmed root cause | FINAL - DO NOT REVISIT |
| Transcript persistence excluded from essential fix set | observability improvement, not required to fix current issues | include as required fix | FINAL - DO NOT REVISIT |

### Architecture Relationships
```text
User message
  -> dashboard/api.py
       -> chat_state (messages, scratchpad, last_*)
       -> agent_plan_step(..., session_state=chat_state)
            -> control_plane/chat_orchestrator.py
                 -> _compute_planner_hints(..., session_state)
                 -> build_prompt(..., planner_hints)
                 -> <active_context>
                 -> LLM chooses tool
            -> execute / approval path
       -> SSE trace_update / final_answer / approval_needed

Product-list happy path
  -> enqueue_product_list_refresh
       -> same run_id allowed
       -> canonical supplier__sandbox__<id>
       -> refresh job type

Bad resume path
  -> enqueue_run chosen for product-list resume
       -> bare suffix accepted
       -> supplier__<id>
       -> wrong lineage
       -> strict fallback misses canonical categories
       -> empty subset
       -> semantic abort
       -> worker may still mark done
```

### Open Design Questions
- [ ] Should the backend keep a deterministic resume rewrite guard even after prompt guidance is improved? Current answer: yes, likely minimal and worthwhile.
- [ ] Should existing malformed resume lineages be recoverable? Current answer: likely yes via narrowly scoped recovery lookup.
- [ ] Should cache-busting be implemented now even though it is only a plausible explanation? Current answer: probably yes as optional low-risk mitigation, but do not present it as proven root cause.
- [ ] Should reasoning-step explanations be made richer than “short user-facing prose”? Current answer: optional only if user wants richer visible trace.
- [ ] Should per-session transcript persistence be added later? Current answer: open, but not part of essential fix set.

### Constraints & Non-Negotiables
- No git operations.
- Do not edit protected runner/core workflow files.
- Keep changes confined to `control_plane/*` and `dashboard/*`.
- Do not present optional mitigations as mandatory fixes.
- Do not revert to the stale Streamlit-centered diagnosis.
- Do not implement code until the user reviews / approves the report + plan.

---

## The Verified Updated Findings (for continuation)

### Confirmed findings
1. FastAPI currently injects active context from `dashboard/api.py` `chat_state` into planner hints and `<active_context>`.
2. `/api/chat/reset` is partial because it does not clear the `last_*` context keys.
3. The New Chat button exists in current source.
4. Product-list refresh enqueue path is correctly sandboxed.
5. Bad non-sandbox lineages are introduced later during resume.
6. Actual bad product-list resume tool choice was `enqueue_run`, confirmed in `chat_tool_calls.jsonl`.
7. `enqueue_product_list_refresh` can reuse the same run ID and therefore the same sandbox lineage.
8. `_normalize_sandbox_suffix` currently returns bare suffixes unchanged.
9. Resume category recovery currently depends on exact supplier-domain equality and can therefore fail after malformed resume names.
10. Empty `categories_subset.json` files directly explain the immediate aborts in resumed pound / clearance runs.
11. Worker status can say `done` on semantically failed runs.
12. `{sandbox_id}` placeholder support is missing in actual substitution logic even though the prompt requires it.
13. `append_transcript()` exists, but current FastAPI path does not use it.

### Likely but not proven findings
1. Live missing New Chat button / live missing visible step trace were likely caused by stale cached assets or different deployed version.
2. Sparse visible reasoning may also be influenced by prompt wording that asks only for short user-facing explanation.
3. A deterministic backend guard would likely be safer than relying only on prompt instructions for correct resume tool choice.

### Overstatements to avoid
1. Do not say FastAPI never injected active context.
2. Do not say cache-busting is the confirmed root cause of the live UI mismatch.
3. Do not say transcript persistence is required for the core bug fix.
4. Do not say current reasoning-step visibility pipeline is fully proven end-to-end in live UI; the code path is present, but live rendering root cause remains unverified.

---

## The Surgical Fix Plan Already Prepared For User Review

### Fix Letters
- A = explicit product-list resume guidance in `SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md`
- B = deterministic backend guard in `agent_plan_step` to rewrite wrong-tool product-list resume from `enqueue_run` to `enqueue_product_list_refresh`
- C = canonicalize bare run fragments in `_normalize_sandbox_suffix`
- D = narrowly scoped backward-recovery logic for legacy malformed names when recovering category URLs / resume context
- E = clear all `last_*` keys in `/api/chat/reset`
- F = add `{sandbox_id}` placeholder substitution support
- G = mark semantic-abort log markers as failed in `worker.py` even when exit code is 0
- H = optional cache-busting on CSS/JS references
- I = optional stronger explanation wording for visible trace quality
- J = transcript persistence enhancement (explicitly non-core)

### Minimum necessary set (validated by Oracle)
- A + B + C + E

### Additional recommended-but-separate fixes
- D for backward recovery of already malformed runs
- F for expected-output preview correctness
- G for truthful status reporting

### Optional only
- H cache-busting mitigation
- I richer trace wording
- J transcript persistence enhancement

### Review notes from Oracle
- Oracle agreed the following are confirmed / supported:
  - partial reset
  - bare suffix normalization issue
  - missing `{sandbox_id}` replacement
  - worker can falsely mark `done`
  - planner prompt lacks explicit product-list resume rule from active context
- Oracle recommended wording discipline:
  - call tool mis-selection a primary failure mode rather than the only root cause
  - keep stale-asset theory plausible, not proven
  - describe UI trace pipeline conservatively
- Oracle conclusion on scope:
  - minimum set for chat/resume bug = A+B+C+E
  - D/F/G are valid but separate concerns

### Review notes from Momus
- Momus endorsed A, B, C, E, F, G as keepers.
- Momus agreed cache-busting is not proven root cause and should remain non-mandatory.
- Momus agreed transcript persistence should stay out of the essential fix set.
- Momus’s useful narrowing on D: keep legacy-name compatibility scoped only to resume-recovery lookup paths; do not relax validation broadly.

---

## Phase 4 - Universal Closure

### 7. Completed Worklog (Chronological)
1. Read the existing handoff and identified that it was stale and Streamlit-centered.
2. Verified current FastAPI state flow in `dashboard/api.py` and `control_plane/chat_orchestrator.py`.
3. Verified current source contains New Chat button and reset handler.
4. Verified New Chat reset is incomplete because `last_*` context keys survive.
5. Inspected `control_plane/tools/product_list_refresh.py` and confirmed refresh enqueue path is correctly sandboxed.
6. Inspected concrete run/job/status/log artifacts for pound, angel, and clearance resume cases.
7. Confirmed malformed non-sandbox lineage appears during resume, not initial refresh.
8. Confirmed empty `categories_subset.json` files and semantic abort messages in resumed pound / clearance runs.
9. Confirmed the angel “second resume worked” case was a false positive caused by reusing a malformed non-sandbox fork.
10. Confirmed expected output predictions are heuristic and can diverge from actual runtime lineage.
11. Verified worker status logic can mark semantically failed workflows as `done`.
12. Re-opened investigation after user supplied another agent’s report extract.
13. Verified wrong-tool selection is a real issue in product-list resume, not just naming mismatch.
14. Verified cache-busting absence, SSE trace code presence, and transcript persistence status.
15. Consulted Oracle and Momus; integrated their scope/certainty corrections.
16. Backed up the old handoff file.
17. Began writing this replacement handoff.

### 8. Validation Performed
No build/test/lint cycle was run against application code because this session’s investigation phase was read-only.

Commands / operations with concrete outputs:

```text
session_info(ses_325d21b4effeGxyxq3jsXPXr1p)
- Messages: 85
- Date Range: 2026-03-10T23:56:06.795Z to 2026-03-12T07:08:56.296Z
- Agents Used: Hephaestus (Deep Agent), general, compaction
- Duration: 1 days, 7 hours
```

```text
read(dashboard/api.py)
- Confirmed agent_plan_step(..., session_state=chat_state)
- Confirmed state tracking of last_run_id / last_products_path / last_supplier_domain / last_sandbox_supplier
- Confirmed /api/chat/reset leaves last_* keys untouched
```

```text
read(dashboard/static/js/app.js)
- Confirmed progressive SSE read loop via res.body.getReader()
- Confirmed trace_update rendering path exists
- Confirmed approval buttons are disabled before approve/reject fetch
- Confirmed window.resetChat() exists and only clears UI after POST /api/chat/reset
```

```text
read(OUTPUTS/CONTROL_PLANE/audit/chat_tool_calls.jsonl:248-260)
- Confirmed pound resume after cancel used enqueue_run with sandbox_suffix a7ce7aa2
- Confirmed initial clearance product-list analyze used enqueue_product_list_refresh
- Confirmed clearance resume after cancel used enqueue_run with sandbox_suffix 6c89a211
```

```text
read(control_plane/worker.py:484-517)
- Confirmed worker marks done on returncode == 0 unless fatal traceback detected
```

```text
powershell backup command
- Created backup/session_handoff_refresh_20260312/session_handoff.md
- Verified backup file exists with non-zero length
```

Validation posture summary:
- Evidence type used: direct code reads, grep, audit JSONL, status files, job payloads, logs, processing states, internal agent review
- Evidence type not used: runtime browser execution, live manual UI test in this session, build, pytest, mypy, ruff

### 9. Known Issues / Risks

| Issue | Severity | Impact | Mitigation |
|---|---|---|---|
| Old handoff is stale and misleading | High | Next agent may restart from wrong Streamlit theory | Use this handoff instead; ignore prior conclusions unless re-verified |
| Exact live cause of missing New Chat / missing visible trace remains unproven | Medium | Could misattribute UI symptom | Treat cache-busting as plausible mitigation, not confirmed RCA |
| Handoff-mining explore outputs reintroduced stale memory-based claims | Medium | Could pollute continuation | Prefer direct code/artifact findings and Oracle/Momus over those outputs |
| Worker status false `done` can hide real failure | High | User may think run succeeded when it semantically aborted | Include G in plan if user wants status accuracy improved |
| Transcript persistence still absent in FastAPI path | Low | Harder forensic review later | Keep as optional enhancement only |
| No code implementation done yet | Medium | Next session must avoid assuming fixes are already applied | Treat current state as report+plan only |

### 10. External Resources Referenced
- External documentation consulted this session: none
- GitHub issues referenced: none
- Internal resources / generated evidence:
  - `OUTPUTS/CONTROL_PLANE/audit/chat_tool_calls.jsonl`
  - `OUTPUTS/CONTROL_PLANE/jobs/...`
  - `OUTPUTS/CONTROL_PLANE/status/...`
  - `OUTPUTS/CONTROL_PLANE/logs/...`
  - `OUTPUTS/CONTROL_PLANE/overrides/...`
  - `OUTPUTS/CACHE/processing_states/...`
- Internal reviewers:
  - Oracle (`bg_9ef3bb7b`) for correctness / overstatement review
  - Momus (`bg_61128c74`) for plan scope / surgicality review

### 11. Quick-Reference Index

#### Key file paths
- `dashboard/api.py`
- `dashboard/templates/index.html`
- `dashboard/static/js/app.js`
- `dashboard/static/css/styles.css`
- `control_plane/chat_orchestrator.py`
- `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md`
- `control_plane/tools/product_list_refresh.py`
- `control_plane/worker.py`
- `control_plane/audit.py`
- `OUTPUTS/CONTROL_PLANE/audit/chat_tool_calls.jsonl`

#### Important symbols / functions / areas
- `agent_plan_step` in `control_plane/chat_orchestrator.py`
- `_compute_planner_hints` in `control_plane/chat_orchestrator.py`
- `build_prompt` in `control_plane/chat_orchestrator.py`
- `_normalize_sandbox_suffix` in `control_plane/chat_orchestrator.py`
- `_substitute_expected_output_placeholders` in `control_plane/chat_orchestrator.py`
- resume fallback around supplier-domain equality in `control_plane/chat_orchestrator.py`
- `enqueue_product_list_refresh` in `control_plane/tools/product_list_refresh.py`
- `chat_reset` in `dashboard/api.py`

#### Critical commands / operations
- No git commands allowed
- No protected runner/tool edits
- Backup before modifying handoff or docs

#### Configuration / prompt files
- `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md`

#### Critical run IDs
- `a7ce7aa2-e6df-455a-ac48-4c3867131ce6` - pound product-list refresh lineage key
- `25577d05-9f59-4f55-acd5-f780ae1ecb1d` - bad pound resume run via `enqueue_run`
- `dcd2841b-256f-4ffd-8fb5-9442dc3442b8` - angel initial category run
- `f2f90444-2fb9-46ac-bac2-73ea4735239b` - first angel bad/non-canonical resume fork
- `1477ef96-56c5-4958-972a-958b7a0ab951` - second angel resume that looked like success but reused malformed fork
- `6c89a211-052e-462a-864a-b31980348724` - clearance product-list refresh lineage key
- `8d92f994-eb1c-4049-9401-e6f98a529efc` - bad clearance resume run via `enqueue_run`
- `01c00bf8-a4fa-4a78-b940-40a0f869ec12` - clearance product-list build run immediately preceding refresh

### 12. Recovery Instructions If Context Is Lost
If the next agent has zero context except this section:
1. Ignore the previous handoff’s claim that FastAPI lacks active-context injection; that is outdated.
2. The current state is **report + surgical fix plan complete, not implemented**.
3. The confirmed minimum fix set for the core bug cluster is A+B+C+E.
4. The confirmed supporting-but-separate fixes are D/F/G.
5. H/J are not mandatory; do not over-scope.
6. The most important direct evidence file for wrong-tool selection is `OUTPUTS/CONTROL_PLANE/audit/chat_tool_calls.jsonl:248-260`.
7. The most important direct evidence file for partial reset is `dashboard/api.py:391-401` plus `dashboard/api.py:271-280` and `dashboard/api.py:343-358`.
8. The most important direct evidence for worker false done is `control_plane/worker.py:484-517`.
9. Do not implement anything until the user confirms they want the reviewed plan applied.
10. Continue from the verified report/plan state, not from the stale Streamlit narrative.

### 13. Startup Plan For Next Session (First 10 Actions)
1. Read this handoff fully.
2. Read `dashboard/api.py:230-401`.
3. Read `control_plane/chat_orchestrator.py` sections for `_normalize_sandbox_suffix`, `_compute_planner_hints`, `build_prompt`, placeholder substitution, and resume fallback.
4. Read `control_plane/tools/product_list_refresh.py` to confirm same-run-id resume path.
5. Read `OUTPUTS/CONTROL_PLANE/audit/chat_tool_calls.jsonl:248-260` to re-anchor on actual wrong-tool selections.
6. Re-state the confirmed fix set to the user before editing: A+B+C+E minimum; D/F/G scoped extras; H/I/J optional.
7. If the user still wants review only, do not edit code; only present the final report/plan.
8. If the user approves implementation, back up affected files first under a new dated backup dir.
9. Implement only in `control_plane/*` and `dashboard/*`; do not touch protected files.
10. After implementation, run targeted verification on modified files and compare behavior against the exact artifact-backed failure cases from this handoff.

---

## Phase 5 - Supermemory Persistence Plan
The prompt that triggered this handoff explicitly requires at least 12 distilled Supermemory entries after writing the handoff. These entries should reflect the verified current state, not the stale prior handoff.

Required coverage to persist:
1. Current objective/state
2. Core architecture touched
3. Key bug fixes planned
4. Validation pattern used
5. Critical constraints/policies
6. Open risk
7. Next-step plan
8. User workflow preferences
9. Failed approaches to avoid
10. Key architectural decisions
11. External dependencies/blockers
12. Performance / behavior characteristics discovered

Planned entries are listed after this file write and will be added via `supermemory(mode="add", ...)`.

---

## Appendix A - Files Investigated In This Session
- `.sisyphus/notepads/handoff/session_handoff.md` (old stale handoff)
- `dashboard/api.py`
- `dashboard/templates/index.html`
- `dashboard/static/js/app.js`
- `dashboard/static/css/styles.css`
- `control_plane/chat_orchestrator.py`
- `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md`
- `control_plane/tools/product_list_refresh.py`
- `control_plane/worker.py`
- `control_plane/audit.py`
- `OUTPUTS/CONTROL_PLANE/audit/chat_tool_calls.jsonl`
- `OUTPUTS/CONTROL_PLANE/jobs/failed/job_a7ce7aa2-e6df-455a-ac48-4c3867131ce6.json`
- `OUTPUTS/CONTROL_PLANE/jobs/done/job_25577d05-9f59-4f55-acd5-f780ae1ecb1d.json`
- `OUTPUTS/CONTROL_PLANE/jobs/failed/job_f2f90444-2fb9-46ac-bac2-73ea4735239b.json`
- `OUTPUTS/CONTROL_PLANE/jobs/failed/job_1477ef96-56c5-4958-972a-958b7a0ab951.json`
- `OUTPUTS/CONTROL_PLANE/jobs/failed/job_6c89a211-052e-462a-864a-b31980348724.json`
- `OUTPUTS/CONTROL_PLANE/jobs/done/job_8d92f994-eb1c-4049-9401-e6f98a529efc.json`
- `OUTPUTS/CONTROL_PLANE/status/25577d05-9f59-4f55-acd5-f780ae1ecb1d.json`
- `OUTPUTS/CONTROL_PLANE/status/8d92f994-eb1c-4049-9401-e6f98a529efc.json`
- `OUTPUTS/CONTROL_PLANE/logs/25577d05-9f59-4f55-acd5-f780ae1ecb1d.log`
- `OUTPUTS/CONTROL_PLANE/logs/8d92f994-eb1c-4049-9401-e6f98a529efc.log`
- `OUTPUTS/CONTROL_PLANE/overrides/25577d05-9f59-4f55-acd5-f780ae1ecb1d/categories_subset.json`
- `OUTPUTS/CONTROL_PLANE/overrides/8d92f994-eb1c-4049-9401-e6f98a529efc/categories_subset.json`
- `OUTPUTS/CONTROL_PLANE/overrides/f2f90444-2fb9-46ac-bac2-73ea4735239b/categories_subset.json`
- `OUTPUTS/CONTROL_PLANE/overrides/1477ef96-56c5-4958-972a-958b7a0ab951/categories_subset.json`
- `OUTPUTS/CACHE/processing_states/poundwholesale_co_uk__sandbox__a7ce7aa2_processing_state.json`
- `OUTPUTS/CACHE/processing_states/poundwholesale_co_uk__a7ce7aa2_processing_state.json`
- `OUTPUTS/CACHE/processing_states/angelwholesale_co_uk__sandbox__dcd2841b_processing_state.json`
- `OUTPUTS/CACHE/processing_states/angelwholesale_co_uk__dcd2841b_processing_state.json`
- backup results and internal reviewer outputs

## Appendix B - Background Tasks Used In This Session
- `bg_9c9ff462` / prior explore: inspect resume workflow logic
- `bg_254b025e` / prior explore: inspect dashboard UI missing button
- `bg_ab8d70a7` / prior explore: inspect prompt injection behavior
- `bg_3b0f2fbd` / prior oracle: validate root causes and blind spots
- `bg_698c6bf3` / explore: verify resume tool-selection root cause
- `bg_3460afb8` / explore: verify frontend cache/SSE/transcript claims
- `bg_9ef3bb7b` / oracle: validate report findings and surgical fixes
- `bg_61128c74` / Momus: critique surgical fix plan for scope and risk
- `bg_1e05470c` / explore: mine constraints / risks / next actions for handoff
- `bg_d633b204` / explore: mine session artifacts for handoff

## Appendix C - Notes On Authority Hierarchy
This session explicitly superseded an older authority-hierarchy / Streamlit-centric narrative. The previous handoff focused on older "LLM amnesia" fixes (`_prune_value`, Streamlit assumptions, `_extract_active_context` memory narrative). That older narrative is not the authoritative description of the current FastAPI/control-plane investigation state. The next session must not reopen that branch unless the user explicitly asks to revisit it.

## Appendix D - Stop Condition For Continuation
A new agent can continue seamlessly if it understands:
- this session already produced the review-ready report + plan
- current code/artifact truth overrides the old handoff
- the next likely user action is either:
  - ask for the finalized report/plan again after compaction, or
  - approve implementation of the surgical fixes
- implementation is not yet done
- if implementation is requested, apply only the approved scoped fixes
