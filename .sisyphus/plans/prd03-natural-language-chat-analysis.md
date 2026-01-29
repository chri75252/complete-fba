# PRD 03 Natural Language Chat: Analysis, Reconciliation & Update Plan

## TL;DR

> **Quick Summary**: Comprehensive analysis of PRD_03_NATURAL_LANGUAGE_CHAT.md, reconciliation with architectural constraints (sandbox runs, no core script edits, category vs product-list flows), research into Qwen3-8B/Ollama best practices, and production of an updated PRD plus detailed report.
> 
> **Deliverables**:
> - Updated PRD document with risk mitigations and architectural alignment
> - Comprehensive analysis report with research findings
> - Test plan validation document
> 
> **Estimated Effort**: Medium (4-6 hours analysis + documentation)
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: Task 1 (PRD Analysis) -> Task 5 (Reconciliation) -> Task 8 (Updated PRD)

---

## Context

### Original Request
Produce a detailed, step-by-step plan to:
1. Analyze `SYSTEM_CHAT_UI_PRDS/PRD_03_NATURAL_LANGUAGE_CHAT.md`
2. Reconcile with critique/observations and architectural decisions (sandbox runs, category vs product-list flows, no core script edits)
3. Research Qwen3-8B + Ollama/local LLM best practices (tool calling/JSON/thinking)
4. Draft an updated PRD and comprehensive report

### Interview Summary
**Key Discussions**:
- Read-only planning only - NO code edits
- Must address risk management: zero interference with workflow, deterministic execution, confirmation gating, schema drift prevention, local LLM reliability
- Search tools (glob/grep) unreliable due to rg.exe PATH issues - use fallbacks (PowerShell Select-String, direct file reads, explore agents)

**Research Findings**:
- PRD_03 proposes natural language chat using Qwen3-8B's triple-output (content, thinking, tool_calls)
- Current `providers.py` ALREADY has `generate_with_tools()` and `generate_text()` implemented
- Current `chat_orchestrator.py` still uses old `plan_tool_call()` with JSON-only output
- Ollama supports streaming tool calls with `think=True` parameter
- Best practice: Temperature 0.3, two-phase (tool selection + post-execution summarization)

### Gap Analysis (Self-Review)
**Auto-Resolved (Minor)**:
- Provider methods already exist - PRD code samples need updating to reflect current state
- Model default is `llama3.1` not `qwen3` - can be changed via environment variable

**Defaults Applied (Ambiguous)**:
- Non-streaming mode for initial implementation (PRD Section 2.2 NG5 confirms this)
- Thinking mode display as optional expander (follows PRD Section 3.2.1)

**No Critical Gaps** - All requirements are clear.

---

## Work Objectives

### Core Objective
Analyze, reconcile, and update PRD_03 to align with current implementation state and architectural constraints, incorporating Qwen3-8B/Ollama best practices and comprehensive risk management.

### Concrete Deliverables
1. `SYSTEM_CHAT_UI_PRDS/PRD_03_NATURAL_LANGUAGE_CHAT_v2.md` - Updated PRD
2. `SYSTEM_CHAT_UI_PRDS/PRD_03_ANALYSIS_REPORT.md` - Comprehensive analysis report
3. `SYSTEM_CHAT_UI_PRDS/PRD_03_TEST_PLAN.md` - Validated test plan for chat UX

### Definition of Done
- [ ] All architectural constraints documented and addressed
- [ ] Risk management section complete with mitigations
- [ ] Qwen3-8B/Ollama best practices incorporated
- [ ] Test plan includes success criteria and verification commands
- [ ] No implementation code in outputs (planning/analysis only)

### Must Have
- Complete analysis of current vs proposed implementation state
- Risk mitigation strategies for all 5 identified risks
- Ollama API usage patterns validated against official docs
- Category vs product-list flow integration documented
- Sandbox isolation pattern documented

### Must NOT Have (Guardrails)
- NO code edits to any `.py` files
- NO modifications to `tools/` or `utils/` directories
- NO implementation artifacts (only documentation)
- NO changes to main OUTPUTS directory structure
- NO assumptions about business logic without evidence from codebase

---

## Verification Strategy (MANDATORY)

### Test Decision
- **Infrastructure exists**: N/A (documentation task)
- **User wants tests**: Manual verification procedures
- **Framework**: None (read-only analysis)

### Manual Verification Procedures

Each TODO includes verification that:
1. Output file exists and is valid markdown
2. Content addresses all required sections
3. References to codebase are accurate
4. No implementation code is present

---

## Task Dependency Graph

| Task | Depends On | Reason | Blocks |
|------|------------|--------|--------|
| Task 1 | None | Starting point - PRD analysis | 2, 3, 5, 6 |
| Task 2 | Task 1 | Needs PRD understanding to analyze current impl | 5, 6 |
| Task 3 | Task 1 | Needs PRD context for research direction | 5, 6 |
| Task 4 | None | Independent research on local LLM constraints | 5, 6 |
| Task 5 | Tasks 1, 2, 3, 4 | Synthesis requires all prior work | 8 |
| Task 6 | Tasks 1, 2, 3, 4 | Risk analysis needs full context | 8 |
| Task 7 | Task 1 | Test plan based on PRD requirements | 8 |
| Task 8 | Tasks 5, 6, 7 | Final deliverable integrates all work | None |

---

## Parallel Execution Graph

```
Wave 1 (Start immediately):
├── Task 1: Deep PRD 03 Analysis (no dependencies)
├── Task 4: Local LLM Reliability Research (no dependencies)

Wave 2 (After Wave 1 completes):
├── Task 2: Current Implementation Gap Analysis (depends: Task 1)
├── Task 3: Qwen3-8B/Ollama Best Practices Research (depends: Task 1)
├── Task 7: Test Plan Validation (depends: Task 1)

Wave 3 (After Wave 2 completes):
├── Task 5: Architectural Reconciliation (depends: Tasks 1, 2, 3, 4)
├── Task 6: Risk Management Analysis (depends: Tasks 1, 2, 3, 4)

Wave 4 (Final - After Wave 3 completes):
└── Task 8: Updated PRD + Report Generation (depends: Tasks 5, 6, 7)

Critical Path: Task 1 → Task 2 → Task 5 → Task 8
Estimated Parallel Speedup: ~35% faster than sequential
```

---

## TODOs

### Task 1: Deep PRD 03 Analysis

**What to do**:
- Read and analyze `SYSTEM_CHAT_UI_PRDS/PRD_03_NATURAL_LANGUAGE_CHAT.md` in full
- Document section-by-section summary of proposed changes
- Identify all assumptions made in PRD
- Map proposed changes to specific files and line numbers
- Note any inconsistencies with PRD_01 and PRD_02

**Must NOT do**:
- Make any code changes
- Assume implementation details not in PRD

**Recommended Agent Profile**:
- **Category**: `writing` - Documentation-focused analysis task
  - Reason: Task is analysis and documentation, not implementation
- **Skills**: None required - pure documentation task
- **Skills Evaluated but Omitted**:
  - `python-programmer`: No Python code involved
  - `frontend-ui-ux`: No UI implementation

**Parallelization**:
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 1 (with Task 4)
- **Blocks**: Tasks 2, 3, 5, 6, 7
- **Blocked By**: None (can start immediately)

**References** (CRITICAL - Be Exhaustive):

**Pattern References**:
- `SYSTEM_CHAT_UI_PRDS/PRD_03_NATURAL_LANGUAGE_CHAT.md` - Primary analysis target (full 824 lines)
- `SYSTEM_CHAT_UI_PRDS/phase1_control_plane/PRD_01_CONTROL_PLANE_EXECUTION_READY.md` - Phase 1 context
- `SYSTEM_CHAT_UI_PRDS/phase2_chat_ui/PRD_02_CHAT_UI_EXECUTION_READY.md` - Phase 2 context

**API/Type References**:
- `control_plane/chat_orchestrator.py:59-63` - Current ToolCall dataclass (compare to PRD proposal)
- `control_plane/llm/providers.py:48-102` - Existing `generate_with_tools()` method (PRD assumes this needs to be added)

**Documentation References**:
- `AGENTS.md:Section 1.1` - Mandatory verification protocols (apply to analysis)

**WHY Each Reference Matters**:
- PRD_03 must be analyzed against PRD_01/02 for consistency
- Current ToolCall dataclass shows what PRD proposes vs what exists
- AGENTS.md ensures analysis follows verification protocols

**Acceptance Criteria**:

- [ ] Using direct file read:
  - Read: `SYSTEM_CHAT_UI_PRDS/PRD_03_NATURAL_LANGUAGE_CHAT.md`
  - Verify: File content matches expected PRD structure
- [ ] Analysis document created with:
  - Section-by-section summary
  - Assumptions identified
  - File mapping table
  - Inconsistencies noted
- [ ] Output saved to working document (not final deliverable)

**Commit**: NO (documentation task, no code changes)

---

### Task 2: Current Implementation Gap Analysis

**What to do**:
- Compare PRD_03 proposals against actual current implementation
- Document which proposed features ALREADY exist (discovered: `generate_with_tools`, `generate_text`)
- Document which features are MISSING
- Identify any conflicts between PRD assumptions and current code
- Create gap matrix: PRD Proposal vs Current State vs Recommendation

**Must NOT do**:
- Modify any code files
- Make assumptions about code behavior without reading files
- Use glob/grep tools (unreliable) - use direct file reads

**Recommended Agent Profile**:
- **Category**: `unspecified-low` - Moderate analysis effort
  - Reason: Requires careful code reading but not complex reasoning
- **Skills**: [`python-programmer`]
  - `python-programmer`: Understanding Python code structure for accurate gap analysis
- **Skills Evaluated but Omitted**:
  - `git-master`: No git operations needed

**Parallelization**:
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 2 (with Tasks 3, 7)
- **Blocks**: Tasks 5, 6
- **Blocked By**: Task 1

**References** (CRITICAL - Be Exhaustive):

**Pattern References**:
- `control_plane/llm/providers.py:48-131` - `generate_with_tools()` and `generate_text()` methods (ALREADY EXIST)
- `control_plane/chat_orchestrator.py:59-63` - Current ToolCall dataclass
- `control_plane/chat_orchestrator.py:175-228` - Current `plan_tool_call()` function
- `dashboard/chat_panel.py:127-133` - Current message rendering with JSON expander

**API/Type References**:
- `control_plane/chat_orchestrator.py:39-56` - READ_TOOLS and WRITE_TOOLS dictionaries (tool classification)
- `control_plane/tools/__init__.py` - All available tools

**Documentation References**:
- `control_plane/README.md` - Phase 1 architecture overview
- `dashboard/README.md` - Dashboard architecture

**WHY Each Reference Matters**:
- `providers.py` shows PRD's T1/T2 tasks are already done - major gap finding
- `chat_orchestrator.py` shows current vs proposed ToolCall structure
- `chat_panel.py` shows current UI rendering pattern

**Acceptance Criteria**:

- [ ] Gap matrix document created with columns:
  - PRD Task ID | PRD Proposal | Current State | Gap Type | Recommendation
- [ ] All 10 PRD tasks (T1-T10) mapped to current implementation state
- [ ] Each "ALREADY EXISTS" finding has file:line citation
- [ ] Each "MISSING" finding has clear specification
- [ ] Output saved to working document

**Commit**: NO (documentation task, no code changes)

---

### Task 3: Qwen3-8B/Ollama Best Practices Research

**What to do**:
- Research Ollama tool calling API format
- Document Qwen3-8B specific capabilities and limitations
- Research `think=True` parameter behavior and output format
- Document streaming vs non-streaming trade-offs
- Create best practices checklist for tool calling with local LLMs
- Validate PRD's API usage against official Ollama documentation

**Must NOT do**:
- Test Ollama locally (planning only)
- Make assumptions about undocumented API behavior

**Recommended Agent Profile**:
- **Category**: `writing` - Research documentation task
  - Reason: External research and documentation synthesis
- **Skills**: None required
- **Skills Evaluated but Omitted**:
  - `python-programmer`: No code implementation

**Parallelization**:
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 2 (with Tasks 2, 7)
- **Blocks**: Tasks 5, 6
- **Blocked By**: Task 1

**References** (CRITICAL - Be Exhaustive):

**External References** (libraries and frameworks):
- Official docs: `https://docs.ollama.com/capabilities/tool-calling` - Ollama tool calling API
- Official docs: `https://docs.ollama.com/capabilities/thinking` - Thinking mode documentation
- Official docs: `https://qwen.readthedocs.io/en/latest/framework/function_call.html` - Qwen function calling
- Hugging Face: `https://huggingface.co/Qwen/Qwen3-8B` - Model capabilities and limitations

**Pattern References** (from Context7 research):
- Ollama Python streaming with tool calls pattern (from research)
- TypeScript Ollama chat with functions pattern (from research)
- Pydantic structured output pattern (from research)

**API/Type References**:
- `control_plane/llm/providers.py:48-102` - Current implementation to validate against docs

**WHY Each Reference Matters**:
- Ollama docs are authoritative source for API behavior
- Qwen docs explain model-specific capabilities
- Current implementation should be validated against official patterns

**Acceptance Criteria**:

- [ ] Research document includes:
  - Ollama `/api/chat` endpoint specification
  - Tool schema format (type: function, function: {name, description, parameters})
  - Response format (message.content, message.thinking, message.tool_calls)
  - `think=True` parameter behavior
  - Streaming considerations
- [ ] Best practices checklist created (10+ items)
- [ ] PRD API usage validated against official docs
- [ ] Any PRD inaccuracies documented

**Commit**: NO (documentation task, no code changes)

---

### Task 4: Local LLM Reliability Constraints Research

**What to do**:
- Research common failure modes of local LLMs with tool calling
- Document rate limiting and request throttling best practices
- Research context window management for Qwen3-8B (8K default, 32K with RoPE)
- Document fallback strategies when tool calling fails
- Create reliability checklist for production use

**Must NOT do**:
- Test any LLM locally
- Make assumptions about reliability without research basis

**Recommended Agent Profile**:
- **Category**: `writing` - Research documentation task
  - Reason: External research focus
- **Skills**: None required
- **Skills Evaluated but Omitted**:
  - `python-programmer`: No code implementation

**Parallelization**:
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 1 (with Task 1)
- **Blocks**: Tasks 5, 6
- **Blocked By**: None (can start immediately)

**References** (CRITICAL - Be Exhaustive):

**External References**:
- Ollama docs: Troubleshooting section for common issues
- Community forums: CrewAI/Ollama tool calling issues
- Hugging Face Qwen3-8B model card: Context length and limitations

**Documentation References**:
- `config/system_config.json` - Review `performance.request_timeout_seconds` and related settings

**WHY Each Reference Matters**:
- Understanding failure modes enables robust mitigation strategies
- Context window limits affect prompt engineering
- Timeout settings must align with LLM response times

**Acceptance Criteria**:

- [ ] Research document includes:
  - Common failure modes list (5+ items)
  - Rate limiting recommendations
  - Context window management strategies
  - Fallback strategy flowchart
- [ ] Reliability checklist created (10+ items)
- [ ] Recommendations mapped to PRD risk management section

**Commit**: NO (documentation task, no code changes)

---

### Task 5: Architectural Reconciliation

**What to do**:
- Reconcile PRD_03 with sandbox run architecture
- Document how category vs product-list flows affect tool schema
- Verify "no core script edits" constraint is maintained
- Map PRD changes to allowed edit locations (`control_plane/`, `dashboard/`)
- Document sandbox isolation pattern: `supplier_domain__sandbox__{run_id}`
- Ensure existing control_plane + dashboard chat compatibility

**Must NOT do**:
- Propose changes to `tools/` or `utils/`
- Suggest modifications to core workflow scripts

**Recommended Agent Profile**:
- **Category**: `ultrabrain` - Complex architectural reasoning
  - Reason: Requires synthesis of multiple constraints and systems
- **Skills**: [`python-programmer`]
  - `python-programmer`: Understanding code architecture for reconciliation
- **Skills Evaluated but Omitted**:
  - `frontend-ui-ux`: No UI design decisions

**Parallelization**:
- **Can Run In Parallel**: NO
- **Parallel Group**: Wave 3 (with Task 6)
- **Blocks**: Task 8
- **Blocked By**: Tasks 1, 2, 3, 4

**References** (CRITICAL - Be Exhaustive):

**Pattern References**:
- `control_plane/chat_orchestrator.py:363-412` - Sandbox pattern implementation (`enqueue_run` tool)
- `control_plane/tools/jobs.py` - Job creation patterns

**API/Type References**:
- `control_plane/job_types.py` - RunRequest and OnboardingWizardRequest schemas
- `control_plane/paths.py` - Path resolution for sandbox outputs

**Documentation References**:
- `AGENTS.md:Section 2.1` - Primary entry points and allowed edit locations
- `SYSTEM_CHAT_UI_PRDS/phase2_chat_ui/PRD_02_CHAT_UI_EXECUTION_READY.md:Section 5` - LLM integration constraints

**WHY Each Reference Matters**:
- Sandbox pattern in `chat_orchestrator.py` shows how isolation is implemented
- AGENTS.md defines what CAN and CANNOT be edited
- PRD_02 established existing constraints that PRD_03 must respect

**Acceptance Criteria**:

- [ ] Reconciliation document includes:
  - Sandbox architecture diagram
  - Category vs product-list flow comparison
  - Allowed vs forbidden edit locations table
  - Compatibility matrix with existing chat
- [ ] All PRD_03 proposed changes mapped to allowed edit locations
- [ ] Any violations of "no core script edits" identified and resolved
- [ ] Output saved to working document

**Commit**: NO (documentation task, no code changes)

---

### Task 6: Risk Management Analysis

**What to do**:
- Address all 5 risk areas from user requirements:
  1. Zero interference with existing workflow
  2. Strict deterministic tool execution
  3. Confirmation gating
  4. Schema drift prevention
  5. Local LLM reliability constraints
- Document mitigation strategies for each risk
- Create risk matrix with severity, likelihood, mitigation
- Validate existing mitigations in current codebase

**Must NOT do**:
- Propose mitigations that require core script edits
- Underestimate risks without evidence

**Recommended Agent Profile**:
- **Category**: `ultrabrain` - Complex risk analysis
  - Reason: Requires systematic risk assessment and mitigation design
- **Skills**: None required
- **Skills Evaluated but Omitted**:
  - `python-programmer`: Analysis focus, not implementation

**Parallelization**:
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 3 (with Task 5)
- **Blocks**: Task 8
- **Blocked By**: Tasks 1, 2, 3, 4

**References** (CRITICAL - Be Exhaustive):

**Pattern References**:
- `dashboard/chat_panel.py:135-169` - Confirmation gating implementation (existing mitigation)
- `control_plane/chat_orchestrator.py:231-232` - `is_write_tool()` function (tool classification)
- `control_plane/chat_orchestrator.py:215-219` - Fallback to `ask_clarify` pattern

**Documentation References**:
- `AGENTS.md:Section 1.2` - Backup protocol (existing safety pattern)
- `SYSTEM_CHAT_UI_PRDS/phase2_chat_ui/PRD_02_CHAT_UI_EXECUTION_READY.md:Section 9` - Safety & Permissions

**WHY Each Reference Matters**:
- Confirmation gating already exists - document and extend
- `is_write_tool()` classification prevents accidental writes
- Backup protocol shows existing safety culture

**Acceptance Criteria**:

- [ ] Risk matrix document includes:
  - 5x risk areas with descriptions
  - Severity rating (Critical/High/Medium/Low)
  - Likelihood rating (Certain/Likely/Possible/Unlikely)
  - Existing mitigations (cite code)
  - Proposed additional mitigations
- [ ] All mitigations respect "no core script edits" constraint
- [ ] Fallback chain documented for LLM failures
- [ ] Output saved to working document

**Commit**: NO (documentation task, no code changes)

---

### Task 7: Test Plan Validation

**What to do**:
- Review PRD_03 Section 5 (Test Plan)
- Validate unit test specifications are testable
- Validate integration test scenarios are complete
- Add missing test cases based on risk analysis
- Create verification commands for each test
- Ensure manual verification checklist is actionable

**Must NOT do**:
- Write actual test code
- Remove existing test cases without justification

**Recommended Agent Profile**:
- **Category**: `writing` - Test documentation task
  - Reason: Validation and documentation of test plan
- **Skills**: None required
- **Skills Evaluated but Omitted**:
  - `python-programmer`: No test code implementation

**Parallelization**:
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 2 (with Tasks 2, 3)
- **Blocks**: Task 8
- **Blocked By**: Task 1

**References** (CRITICAL - Be Exhaustive):

**Pattern References**:
- `SYSTEM_CHAT_UI_PRDS/PRD_03_NATURAL_LANGUAGE_CHAT.md:659-687` - Current test plan section
- `SYSTEM_CHAT_UI_PRDS/phase1_control_plane/TEST_PLAN_PHASE1.md` - Phase 1 test patterns

**Documentation References**:
- `SYSTEM_CHAT_UI_PRDS/phase1_control_plane/PHASE1_TEST_EVIDENCE.md` - Test evidence format
- `SYSTEM_CHAT_UI_PRDS/phase2_chat_ui/PRD_02_CHAT_UI_EXECUTION_READY.md:Section 10` - Phase 2 test plan

**WHY Each Reference Matters**:
- Current test plan needs validation against implementation gaps
- Phase 1/2 test patterns establish expected format
- Test evidence format shows what verification looks like

**Acceptance Criteria**:

- [ ] Test plan validation document includes:
  - Review of each UT1-UT5 unit test
  - Review of each IT1-IT4 integration test
  - Added test cases from risk analysis
  - Verification commands for each test
  - Updated manual verification checklist
- [ ] All tests are actionable and verifiable
- [ ] Output saved to working document

**Commit**: NO (documentation task, no code changes)

---

### Task 8: Updated PRD + Report Generation

**What to do**:
- Synthesize all prior task outputs into final deliverables
- Create `PRD_03_NATURAL_LANGUAGE_CHAT_v2.md` with:
  - Updated implementation status (what exists vs what's needed)
  - Architectural reconciliation section
  - Risk management section
  - Updated test plan
  - Qwen3-8B/Ollama best practices integration
- Create `PRD_03_ANALYSIS_REPORT.md` with:
  - Executive summary
  - Gap analysis findings
  - Research findings
  - Recommendations
- Create `PRD_03_TEST_PLAN.md` with:
  - Complete test specification
  - Verification commands
  - Success criteria

**Must NOT do**:
- Include any implementation code
- Change deliverable format without justification

**Recommended Agent Profile**:
- **Category**: `writing` - Final documentation synthesis
  - Reason: Primary task is document generation
- **Skills**: None required
- **Skills Evaluated but Omitted**:
  - All technical skills: No code involved

**Parallelization**:
- **Can Run In Parallel**: NO
- **Parallel Group**: Wave 4 (final, sequential)
- **Blocks**: None (final task)
- **Blocked By**: Tasks 5, 6, 7

**References** (CRITICAL - Be Exhaustive):

**Pattern References**:
- All Task 1-7 working documents (synthesis inputs)
- `SYSTEM_CHAT_UI_PRDS/PRD_03_NATURAL_LANGUAGE_CHAT.md` - Original PRD for structure
- `SYSTEM_CHAT_UI_PRDS/phase1_control_plane/PRD_01_CONTROL_PLANE_EXECUTION_READY.md` - PRD format reference

**Documentation References**:
- `.sisyphus/drafts/prd03-natural-language-chat-analysis.md` - Interview notes and decisions

**WHY Each Reference Matters**:
- All prior tasks feed into final synthesis
- Original PRD provides structure template
- Draft captures key decisions made during planning

**Acceptance Criteria**:

- [ ] `PRD_03_NATURAL_LANGUAGE_CHAT_v2.md` created with:
  - All sections from original PRD
  - Updated implementation status per Task 2 findings
  - Architectural reconciliation section from Task 5
  - Risk management section from Task 6
  - Updated test plan from Task 7
  - Qwen3-8B best practices from Task 3
- [ ] `PRD_03_ANALYSIS_REPORT.md` created with:
  - Executive summary (1 page)
  - Gap analysis (from Task 2)
  - Research findings (from Tasks 3, 4)
  - Recommendations (prioritized list)
- [ ] `PRD_03_TEST_PLAN.md` created with:
  - Complete test cases
  - Verification procedures
  - Success criteria matrix
- [ ] All files are valid markdown
- [ ] No implementation code in any file

**Commit**: YES (documentation deliverables)
- Message: `docs(prd): update PRD_03 with analysis, reconciliation, and risk management`
- Files: 
  - `SYSTEM_CHAT_UI_PRDS/PRD_03_NATURAL_LANGUAGE_CHAT_v2.md`
  - `SYSTEM_CHAT_UI_PRDS/PRD_03_ANALYSIS_REPORT.md`
  - `SYSTEM_CHAT_UI_PRDS/PRD_03_TEST_PLAN.md`
- Pre-commit: N/A (documentation only)

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 8 | `docs(prd): update PRD_03 with analysis, reconciliation, and risk management` | `SYSTEM_CHAT_UI_PRDS/PRD_03_*.md` | Visual inspection of markdown |

---

## Success Criteria

### Verification Commands
```bash
# Verify deliverable files exist
ls -la SYSTEM_CHAT_UI_PRDS/PRD_03_NATURAL_LANGUAGE_CHAT_v2.md
ls -la SYSTEM_CHAT_UI_PRDS/PRD_03_ANALYSIS_REPORT.md
ls -la SYSTEM_CHAT_UI_PRDS/PRD_03_TEST_PLAN.md

# Verify no .py files were modified
git status --porcelain | grep -E "\.py$" | wc -l  # Expected: 0

# Verify markdown validity (basic check)
head -20 SYSTEM_CHAT_UI_PRDS/PRD_03_NATURAL_LANGUAGE_CHAT_v2.md
```

### Final Checklist
- [ ] All 3 deliverable documents created
- [ ] No code files modified
- [ ] Risk management section addresses all 5 required areas
- [ ] Qwen3-8B/Ollama best practices documented
- [ ] Test plan includes success criteria
- [ ] Architectural constraints documented and respected
- [ ] All references are accurate file:line citations

---

## Agent Dispatch Summary

| Wave | Tasks | Recommended Dispatch |
|------|-------|---------------------|
| 1 | 1, 4 | `delegate_task(category="writing", run_in_background=true)` x2 |
| 2 | 2, 3, 7 | `delegate_task(category="unspecified-low", skills=["python-programmer"])` for Task 2; `delegate_task(category="writing")` for Tasks 3, 7 |
| 3 | 5, 6 | `delegate_task(category="ultrabrain", skills=["python-programmer"])` for Task 5; `delegate_task(category="ultrabrain")` for Task 6 |
| 4 | 8 | `delegate_task(category="writing")` - sequential after Wave 3 |

---

## Appendix: File Reference Matrix

| File Path | Read/Write | Used In Tasks |
|-----------|------------|---------------|
| `SYSTEM_CHAT_UI_PRDS/PRD_03_NATURAL_LANGUAGE_CHAT.md` | READ | 1, 2, 7, 8 |
| `control_plane/llm/providers.py` | READ | 2, 3 |
| `control_plane/chat_orchestrator.py` | READ | 2, 5, 6 |
| `dashboard/chat_panel.py` | READ | 2, 6 |
| `AGENTS.md` | READ | 1, 5 |
| `SYSTEM_CHAT_UI_PRDS/PRD_03_NATURAL_LANGUAGE_CHAT_v2.md` | WRITE | 8 |
| `SYSTEM_CHAT_UI_PRDS/PRD_03_ANALYSIS_REPORT.md` | WRITE | 8 |
| `SYSTEM_CHAT_UI_PRDS/PRD_03_TEST_PLAN.md` | WRITE | 8 |
