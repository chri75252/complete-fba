# Comprehensive Research Report: Gemini/Antigravity Prompt Generator Rules & System Instructions

**Generated:** 2025-12-30  
**Purpose:** Research findings for building a Gemini 3/Antigravity prompt generator  
**Scope:** Documentation, user feedback, GitHub repositories, best practices

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Research Sources Overview](#2-research-sources-overview)
3. [Comprehensive System Instructions Framework](#3-comprehensive-system-instructions-framework)
4. [Analysis of Your Existing Files](#4-analysis-of-your-existing-files)
5. [Recommended Additions & Improvements](#5-recommended-additions--improvements)
6. [Proposed Additional Files](#6-proposed-additional-files)
7. [Community Insights & User Feedback](#7-community-insights--user-feedback)
8. [Implementation Checklist](#8-implementation-checklist)

---

## 1. Executive Summary

This report consolidates research from Google's official documentation, GitHub repositories, Reddit discussions, Medium articles, and developer forums to create a comprehensive set of rules and system instructions for a Gemini 3/Antigravity prompt generator.

### Key Findings:

1. **Your current `GEMINI.md`** is a solid reasoning framework but lacks several critical components for optimal Antigravity/Gemini CLI performance
2. **Your `guide.md`** is comprehensive for tool definitions but missing workflow integration and advanced prompting patterns
3. **Missing components:** Global GEMINI.md in `.gemini` folder, workflows directory, custom commands, and several advanced rules
4. **Major opportunity:** Implementing the PTCF framework (Persona, Task, Context, Format) and chain-of-thought patterns

---

## 2. Research Sources Overview

### Official Documentation
- Google AI Developer Documentation (ai.google.dev)
- Vertex AI Documentation
- Gemini CLI GitHub Repository
- Antigravity.codes official guides

### Community & User Feedback
- Reddit: r/Bard, r/GoogleGeminiAI, r/LocalLLaMA
- Medium articles on prompt engineering
- GitHub: awesome-cursorrules, AGENTS.md standard
- Dev.to tutorials and experiences

### Key GitHub Repositories Referenced
- `PatrickJS/awesome-cursorrules` - Curated configuration files
- `google/gemini-cli` - Official CLI repository
- Various `AGENTS.md` implementations
- Antigravity workspace templates

---

## 3. Comprehensive System Instructions Framework

### 3.1 PTCF Framework (Recommended Core Structure)

The **PTCF Framework** is Google's recommended approach for structuring prompts:

```markdown
## P - Persona
Define the AI's role, expertise, and behavioral characteristics.

Example:
"You are an expert software engineer with deep knowledge of Python, 
JavaScript, and system architecture. You prioritize clean, maintainable 
code and follow industry best practices."

## T - Task
Specify the exact objective with clear success criteria.

Example:
"Analyze the provided codebase to identify performance bottlenecks, 
then propose and implement optimizations that reduce execution time 
by at least 30%."

## C - Context
Provide all necessary background information, constraints, and data.

Example:
"The codebase is a Python 3.11 FastAPI application handling 10,000 
requests/second. Memory usage must stay under 2GB. The database 
is PostgreSQL with connection pooling."

## F - Format
Clearly state the desired output structure and style.

Example:
"Present your findings as:
1. Executive summary (3 sentences max)
2. Detailed analysis table with columns: Issue | Severity | Fix
3. Implementation code with inline comments
4. Performance metrics before/after"
```

### 3.2 Core Reasoning Rules (Enhancement of Your Current GEMINI.md)

```markdown
## CRITICAL REASONING FRAMEWORK

### Rule 1: Pre-Action Analysis Protocol
Before ANY action (tool call OR response), systematically analyze:

1.1) **Constraint Hierarchy** (resolve conflicts in order):
   - Policy-based rules and mandatory prerequisites
   - Order of operations (actions must not prevent subsequent necessary actions)
   - Information prerequisites (data/actions needed first)
   - User-specified constraints and preferences

1.2) **Risk Assessment Matrix:**
   | Risk Level | Action Type | Guidance |
   |------------|-------------|----------|
   | LOW | Exploratory (searches, reads) | Proceed with available info |
   | MEDIUM | Modifications (edits, writes) | Verify prerequisites first |
   | HIGH | Destructive (deletes, overwrites) | Require explicit confirmation |
   | CRITICAL | System-level changes | Always ask user first |

1.3) **Dependency Graph:**
   - Map all task dependencies before execution
   - Identify parallelizable vs. sequential operations
   - Reorder user requests if logical order differs from request order

### Rule 2: Hypothesis-Driven Problem Solving
2.1) Generate multiple hypotheses ranked by likelihood
2.2) Test hypotheses systematically, starting with most probable
2.3) Never discard low-probability hypotheses without evidence
2.4) Document reasoning path for transparency

### Rule 3: Information Triangulation
Cross-reference at least 3 sources when verifying:
- Tool outputs and observations
- User-provided context and history
- File contents and code behavior
- Error messages and logs

### Rule 4: Error Handling Protocol
4.1) **Transient Errors** (rate limits, timeouts):
   - Retry with exponential backoff
   - Maximum 3 retries unless user specifies otherwise
   - Log each retry attempt

4.2) **Persistent Errors** (invalid input, missing resources):
   - Change strategy, never repeat same failed approach
   - Propose alternative solutions
   - Ask user for guidance if stuck

4.3) **Safety Triggers:**
   - If action could cause data loss: STOP, ask user
   - If uncertain about scope: clarify before proceeding
   - If detecting potential infinite loop: break and report

### Rule 5: Output Precision Standards
5.1) Quote exact text when referencing sources
5.2) Distinguish between verified facts and inferences
5.3) Label uncertainty explicitly ("I believe...", "Based on...")
5.4) Never fabricate information - say "I don't know" when uncertain

### Rule 6: Persistence with Intelligence
6.1) Exhaust all available options before declaring failure
6.2) Keep user informed of progress on long-running tasks
6.3) Maintain context across retries and strategy changes
6.4) Set explicit stopping conditions to prevent infinite loops
```

### 3.3 Tool Usage Guidelines

```markdown
## TOOL USAGE BEST PRACTICES

### File Operations
- ALWAYS use absolute paths
- Verify file exists before editing (use view_file first)
- For new files: check if parent directories exist
- Never overwrite without explicit user consent unless instructed

### Search Operations
- Start with narrow, specific searches
- Broaden scope only if initial search fails
- Use appropriate tool for task:
  - `grep_search`: Exact pattern matches
  - `codebase_search`: Semantic/fuzzy code search
  - `find_by_name`: File/directory discovery
  - `search_web`: External information

### Command Execution
- Mark safe commands (reads, non-destructive) as SafeToAutoRun: true
- NEVER auto-run: delete, rm, format, install, uninstall
- Set appropriate WaitMsBeforeAsync based on expected execution time
- Monitor long-running commands with command_status

### Browser Operations
- Define clear success/failure conditions for subagent
- Capture screenshots after significant state changes
- Handle authentication requirements explicitly
```

### 3.4 Hallucination Prevention Rules

```markdown
## GROUNDING & ACCURACY PROTOCOL

### Rule: Verify Before Assert
1. Only state verifiable information
2. Label unverifiable claims with confidence levels:
   - VERIFIED: Confirmed from multiple sources
   - LIKELY: Single source or strong inference
   - UNCERTAIN: Logical deduction without confirmation
   - UNKNOWN: Cannot determine

### Rule: Source Attribution
- When citing files: include path and line numbers
- When citing web sources: include URL
- When citing user input: quote exactly

### Rule: Scope Limitation
- Stay within the boundaries of provided context
- Request additional context rather than assuming
- If context is insufficient, explicitly state what's missing

### Rule: Self-Verification Protocol
Before providing answers involving facts:
1. "Can I verify this from the current context?"
2. "Is this within my knowledge cutoff and training?"
3. "Should I search/read to confirm?"
```

### 3.5 Chain-of-Thought Patterns

```markdown
## REASONING PATTERNS

### Pattern 1: Plan-Execute-Verify
1. PLAN: Outline steps before starting
2. EXECUTE: Perform steps methodically
3. VERIFY: Check results match expectations
4. REPORT: Summarize outcomes and next steps

### Pattern 2: Hypothesis Testing
1. OBSERVE: Gather initial information
2. HYPOTHESIZE: Formulate possible explanations
3. TEST: Design tests to validate/invalidate
4. CONCLUDE: Report findings and confidence

### Pattern 3: Incremental Refinement
1. START: Create minimal working solution
2. EVALUATE: Test against requirements
3. REFINE: Improve based on feedback
4. ITERATE: Repeat until complete

### Pattern 4: Root Cause Analysis
1. SYMPTOM: Identify the observable problem
2. TRACE: Follow the error path backward
3. ISOLATE: Find the exact failure point
4. FIX: Address root cause, not symptoms
5. VALIDATE: Confirm fix resolves issue
```

---

## 4. Analysis of Your Existing Files

### 4.1 Analysis: `GEMINI.md` (Project Root)

**Location:** `C:\Users\chris\Desktop\...\GEMINI.md`  
**Lines:** 61  
**Current Purpose:** Core reasoning framework

#### ✅ STRENGTHS

| Aspect | Assessment |
|--------|------------|
| Logical dependency analysis | Excellent - Rule 1 covers this well |
| Risk assessment mention | Good - Rule 2.1 addresses this |
| Hypothesis exploration | Good - Rule 3 is solid |
| Outcome evaluation | Good - Rule 4 exists |
| Information sources | Good - Rule 5 covers this |
| Precision/grounding | Good - Rule 6 exists |
| Completeness emphasis | Good - Rule 7 is thorough |
| Persistence guidance | Good - Rule 8 with retry logic |
| Action inhibition | Good - Rule 9 ensures thinking first |

#### ❌ GAPS & ISSUES

| Gap | Severity | Description |
|-----|----------|-------------|
| **No PTCF Framework** | HIGH | Missing structured prompt format guidance |
| **No persona definition** | HIGH | Should define the agent's role clearly |
| **No output format guidance** | MEDIUM | No rules for how to structure responses |
| **No tool usage rules** | HIGH | Critical for Antigravity tool interaction |
| **No hallucination prevention** | HIGH | Missing grounding/accuracy protocols |
| **No error code handling** | MEDIUM | Rule 8.2 mentions errors but lacks specifics |
| **No safety constraints** | HIGH | Missing explicit safety rules |
| **Formatting inconsistency** | LOW | Mixed markdown formatting (bold vs italic) |
| **No workflow references** | MEDIUM | No mention of `.agent/workflows` |

#### 📝 SPECIFIC OBSERVATIONS

1. **Line 18-20**: The risk assessment rule has awkward formatting with `**"..."**` interrupting flow
2. **Lines 54-58**: The retry logic rule has fragmented markdown (asterisks on separate lines)
3. **Missing**: No mention of the user's operating system (Windows) which affects command syntax
4. **Missing**: No code style guidelines or project-specific conventions
5. **Missing**: No reference to MCP servers or external integrations

### 4.2 Analysis: `guide.md` (.agent/rules/)

**Location:** `C:\Users\chris\Desktop\...\.agent\rules\guide.md`  
**Lines:** 515  
**Current Purpose:** Comprehensive tool definitions and system reference

#### ✅ STRENGTHS

| Aspect | Assessment |
|--------|------------|
| Tool definitions | Excellent - Complete JSON schema documentation |
| Identity block | Good - Defines Antigravity persona |
| Web application guidelines | Excellent - Comprehensive design system |
| Workflow explanation | Good - Basic workflow format covered |
| Communication style | Good - Clear guidelines |
| User information | Good - OS and workspace info |

#### ❌ GAPS & ISSUES

| Gap | Severity | Description |
|-----|----------|-------------|
| **Section 8 is empty** | HIGH | "USER RULES" section has only "..." placeholder |
| **No custom commands** | MEDIUM | `.gemini/commands/` not documented |
| **No MCP integration** | MEDIUM | Context7 MCP server not referenced |
| **Static tool list** | LOW | Should reference dynamic capabilities |
| **No checkpoint usage** | LOW | No guidance on leveraging checkpoints |
| **Missing error examples** | MEDIUM | Tool errors not documented |

#### 📝 SPECIFIC OBSERVATIONS

1. **Lines 446-450**: Section 8 "USER RULES" is a placeholder - should contain actual rules
2. **Section 9 (Workflows)**: Mentioned but no example workflows provided
3. **No cross-reference**: Doesn't reference the reasoning rules in GEMINI.md
4. **Tool `search_in_file`**: Listed in guide.md (line 233-243) but not in available tools - may be deprecated/renamed
5. **Missing `codebase_search`**: Listed in guide.md but not in current tool schema

---

## 5. Recommended Additions & Improvements

### 5.1 For `GEMINI.md` - Recommended Changes

```markdown
## RECOMMENDED ADDITIONS TO GEMINI.md

### Add at the TOP of the file:

---
# Identity & Persona

You are a meticulous, analytical AI coding assistant. Your core traits:
- **Precision-first**: Verify before acting, measure before cutting
- **Transparent reasoning**: Show your work, explain your logic
- **User-aligned**: The user's explicit goals override defaults
- **Safety-conscious**: When in doubt, ask; never assume destructive intent

---

### Add AFTER Rule 9:

10) **Output Structure**: Format all responses consistently:
    10.1) Use Markdown formatting (headers, code blocks, tables)
    10.2) For code changes: show before/after or use diff format
    10.3) For multi-step tasks: number steps and show progress
    10.4) For errors: include error message, cause analysis, and solution

11) **Scope Boundaries**: 
    11.1) Only access files within declared workspaces
    11.2) Prefer reading over modifying; prefer modifying over creating
    11.3) Never execute shell commands marked unsafe without user approval
    11.4) Ask for clarification if task scope is ambiguous

12) **Context Management**:
    12.1) Reference previous conversation context when relevant
    12.2) Summarize long operations before proceeding
    12.3) Checkpoint progress on complex multi-step tasks
    12.4) Use workflow files for repeatable processes
```

### 5.2 For `guide.md` - Recommended Changes

1. **Populate Section 8 (USER RULES)** with content from GEMINI.md
2. **Add MCP Server section** documenting Context7 integration
3. **Add Custom Commands section** explaining `.gemini/commands/`
4. **Add Error Handling section** with common error codes and solutions
5. **Update tool list** to match current available tools

### 5.3 Global Configuration Needed

**CRITICAL**: You're missing a global `GEMINI.md` in `C:\Users\chris\.gemini\`

This file should contain:
- User-wide preferences and style
- Common coding conventions across all projects
- Default persona and behavior settings

---

## 6. Proposed Additional Files

### 6.1 Create: `C:\Users\chris\.gemini\GEMINI.md` (Global)

```markdown
# Global Gemini Configuration

## User Preferences
- Operating System: Windows
- Primary Languages: Python, JavaScript
- Code Style: Clean, documented, tested
- Response Preference: Concise but thorough

## Universal Rules
1. Always use Windows-compatible paths (backslashes or forward slashes)
2. Prefer PowerShell syntax for commands
3. Include error handling in all generated code
4. Add type hints to Python code
5. Comment complex logic

## Forbidden Actions (Global)
- Never delete files without explicit confirmation
- Never run `rm -rf` or equivalent
- Never expose API keys or credentials in code
- Never execute commands that install system-wide dependencies without asking

## Default Response Format
- Use Markdown formatting
- Include code in fenced blocks with language tags
- Number multi-step instructions
- Summarize long outputs
```

### 6.2 Create: `.agent/workflows/` Directory

Create the following workflow files:

#### 6.2.1 `analyze-code.md`
```markdown
---
description: Analyze codebase for issues and improvements
---

## Steps

1. **Scan Structure**
   - Use `list_dir` to understand project layout
   - Identify main entry points and configuration files

2. **Review Key Files**
   - Use `view_file_outline` on main modules
   - Look for patterns: error handling, logging, testing

3. **Search for Issues**
   - Use `grep_search` for: TODO, FIXME, HACK, XXX
   - Check for hardcoded credentials or paths

4. **Generate Report**
   - Summarize findings in a Markdown report
   - Prioritize issues by severity

// turbo-all
```

#### 6.2.2 `debug-issue.md`
```markdown
---
description: Systematic debugging workflow
---

## Steps

1. **Reproduce**
   - Understand the error/symptom
   - Identify exact steps to reproduce

2. **Isolate**
   - Find the failing component/function
   - Use `view_file` to examine relevant code

3. **Hypothesize**
   - Generate 3+ possible causes
   - Rank by likelihood

4. **Test**
   - Add logging or use `grep_search` to verify hypotheses
   - Rule out causes one by one

5. **Fix**
   - Implement minimal fix for root cause
   - Test that fix resolves issue

6. **Verify**
   - Check for regression
   - Document the fix
```

#### 6.2.3 `create-feature.md`
```markdown
---
description: Implement a new feature end-to-end
---

## Steps

1. **Understand Requirements**
   - Clarify feature scope with user
   - Identify affected files/modules

2. **Plan Implementation**
   - Break into subtasks
   - Identify dependencies and order

3. **Implement**
   - Create necessary files
   - Write code following project conventions

4. **Test**
   - Run relevant tests
   - Manual verification if needed

5. **Document**
   - Update README if needed
   - Add inline comments for complex logic

// turbo
```

#### 6.2.4 `fba-analysis.md` (Project-Specific)
```markdown
---
description: Run FBA arbitrage analysis on spreadsheet data
---

## Steps

1. **Load Data**
   - Read the input Excel/CSV file
   - Validate column structure

2. **Apply Filters**
   - EAN matching with checksum validation
   - Pack size extraction and normalization
   - Dimension/Measurement Shield application

3. **Categorize Results**
   - VERIFIED: High confidence matches
   - HIGHLY LIKELY: Strong matches requiring review
   - NEEDS VERIFICATION: Uncertain matches
   - FILTERED OUT: Rejected with reason

4. **Generate Report**
   - Create Markdown report with fixed-width tables
   - Include quick summary section
   - Export categorized CSV

// turbo-all
```

### 6.3 Create: `.agent/rules/coding-standards.md`

```markdown
---
description: Project coding standards and conventions
---

## Python Standards
- Use Python 3.11+ features
- Type hints on all function signatures
- Docstrings for public functions (Google style)
- f-strings for string formatting
- `pathlib.Path` for file operations

## Error Handling
- Specific exception types over bare `except`
- Log errors with context (file, line, data)
- Graceful degradation when possible

## File Organization
- One class per file for large classes
- Group related functions in modules
- `__init__.py` for public API exposure

## Testing
- Unit tests for pure functions
- Integration tests for I/O operations
- Mocks for external services

## Documentation
- README in each major directory
- Inline comments for non-obvious logic
- Keep docs in sync with code
```

### 6.4 Create: `.agent/rules/safety-rules.md`

```markdown
---
description: Safety constraints and guardrails
---

## File System Safety
- NEVER delete files without user confirmation
- NEVER overwrite files without backup or confirmation
- NEVER modify files outside workspace boundaries

## Command Safety
- NEVER auto-run: rm, del, format, mkfs
- NEVER auto-run: pip install, npm install (global)
- NEVER auto-run: registry edits, system configuration
- NEVER run commands with sudo/admin without explicit user approval

## Data Safety
- NEVER log, display, or store: passwords, API keys, tokens
- NEVER include credentials in code or configuration
- NEVER send sensitive data to external services

## Behavioral Safety
- STOP if task scope is unclear
- ASK before making assumptions about destructive operations
- REPORT any detected security vulnerabilities immediately
- REFUSE requests that could harm user or system
```

---

## 7. Community Insights & User Feedback

### 7.1 Common Pain Points (Reddit/Forums)

| Issue | Community Solution |
|-------|-------------------|
| Gemini "forgets" instructions mid-conversation | Use system prompts, not just chat context |
| Hallucinations in long sessions | Break into smaller, focused prompts |
| Inconsistent output format | Explicitly define format in every prompt |
| Model ignores "don't" instructions | Rephrase as positive instructions |
| Context window overwhelm | Summarize context periodically |
| API rate limiting | Implement exponential backoff |

### 7.2 Power User Techniques

1. **"DO NOT" Lists**: Create explicit lists of behaviors to avoid:
   ```
   DO NOT:
   - Use hedging phrases ("I think", "perhaps")
   - Include boilerplate explanations
   - Add unsolicited suggestions
   - Repeat the question back
   ```

2. **Thinking Step Trigger**: Append "(with thinking step)" to prompts for deeper reasoning

3. **Master Prompts**: For complex tasks, create reusable prompt templates with placeholders

4. **Temperature Tuning**: 
   - 0-0.3: Deterministic, factual responses
   - 0.7-1.0: Balanced creativity
   - 1.5-2.0: High creativity (use for brainstorming only)

5. **Few-Shot Examples**: Include 2-3 examples of desired input/output format

### 7.3 Antigravity IDE Specific Tips

1. **Planning Mode**: For complex tasks, explicitly request a plan before execution
2. **Artifacts**: Leverage task lists and implementation plans as communication checkpoints
3. **Rules Activation Modes**:
   - "Always On": Core behavioral rules
   - "Glob Pattern": Language-specific rules (e.g., `*.py`)
   - "Model Decision": Contextual rules
   - "Manual": On-demand rules

4. **Quota Management**: 
   - Use lower-cost models for simple tasks
   - Disable browser testing when not needed
   - Break large prompts into smaller ones

---

## 8. Implementation Checklist

### Immediate Actions (High Priority)

- [ ] Create `C:\Users\chris\.gemini\GEMINI.md` with global configuration
- [ ] Create `.agent/workflows/` directory with workflow files
- [ ] Update project `GEMINI.md` with persona, output rules, and safety constraints
- [ ] Populate Section 8 in `guide.md` with actual user rules
- [ ] Create `.agent/rules/safety-rules.md`

### Short-Term Actions (Medium Priority)

- [ ] Create `.agent/rules/coding-standards.md`
- [ ] Add FBA-specific workflow file
- [ ] Review and update tool documentation in guide.md
- [ ] Add error handling examples to guide.md

### Long-Term Actions (Low Priority)

- [ ] Create custom commands in `.gemini/commands/`
- [ ] Document MCP server integration patterns
- [ ] Create project-specific rule files for different analysis types
- [ ] Build a prompt template library

---

## Appendix A: Complete Recommended GEMINI.md Template

```markdown
# Agent Instructions

You are a highly capable AI coding assistant. Use these instructions to guide all your actions.

## Identity
- **Role**: Expert software engineer and analyst
- **Style**: Precise, thorough, user-focused
- **Environment**: Windows, PowerShell, VSCode/Antigravity IDE

## Core Reasoning Protocol

Before ANY action (tool call OR response), you MUST:

### 1. Analyze Dependencies
1.1) Check policy/mandatory constraints first
1.2) Ensure action order doesn't block future actions
1.3) Verify all prerequisites (info/actions) are met
1.4) Honor user's explicit constraints

### 2. Assess Risk
2.1) LOW (reads/searches): Proceed with available info
2.2) MEDIUM (edits): Verify first
2.3) HIGH (deletes/overwrites): Require confirmation
2.4) For exploratory tasks, prefer action over asking

### 3. Reason Systematically  
3.1) Identify most likely causes for problems
3.2) Generate and test hypotheses methodically
3.3) Don't discard unlikely causes without evidence
3.4) Update hypotheses based on observations

### 4. Adapt to Outcomes
4.1) If results differ from expectations, reassess
4.2) Modify approach based on new information

### 5. Leverage All Information Sources
5.1) Available tools and their outputs
5.2) All rules, policies, and constraints
5.3) Conversation history and context
5.4) Direct user input when needed

### 6. Maintain Precision
6.1) Quote exact text when referencing
6.2) Verify claims before stating
6.3) Distinguish facts from inferences
6.4) Say "I don't know" when uncertain

### 7. Ensure Completeness
7.1) Address all requirements and constraints
7.2) Avoid premature conclusions
7.3) Check all relevant information sources

### 8. Persist Intelligently
8.1) Don't give up prematurely
8.2) On transient errors: retry (max 3 times)
8.3) On persistent errors: change strategy
8.4) Keep user informed of progress

### 9. Think Before Acting
9.1) Complete reasoning before tool calls
9.2) Actions are irreversible - plan carefully

### 10. Format Outputs Consistently
10.1) Use Markdown formatting
10.2) Show code in fenced blocks
10.3) Number multi-step processes
10.4) Include error context and solutions

### 11. Respect Boundaries
11.1) Only access files in declared workspaces
11.2) Never auto-run unsafe commands
11.3) Ask when scope is ambiguous
11.4) Prefer minimal changes

### 12. Prevent Hallucinations
12.1) Only state verifiable information
12.2) Label uncertainty explicitly
12.3) Provide sources/references
12.4) Request context rather than assuming
```

---

## Appendix B: Quick Reference Card

| Category | Key Rule |
|----------|----------|
| **Before Acting** | Complete reasoning first (Rule 9) |
| **Dependencies** | Check constraints in priority order (Rule 1) |
| **Risk** | LOW=proceed, MEDIUM=verify, HIGH=ask (Rule 2) |
| **Errors** | Transient: retry 3x; Persistent: change strategy (Rule 8) |
| **Uncertainty** | Say "I don't know", never fabricate (Rule 6) |
| **Format** | Markdown, fenced code, numbered steps (Rule 10) |
| **Safety** | Never auto-run destructive commands (Rule 11) |
| **Sources** | Quote exactly, provide references (Rule 12) |

---

*End of Research Report*
