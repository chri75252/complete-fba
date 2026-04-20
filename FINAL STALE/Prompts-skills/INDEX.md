# FBA Workflows & Prompts Repository

This directory consolidates the verified prompts, skill analysis, and operational workflows required to enforce rigorous FBA product validation and stale data cleansing.

## 📁 Directory Index

### 1. `fba_product_validation_prompt.md`
**Type:** Core Execution Prompt
**Purpose:** The master prompt to be copy-pasted (or injected via automation) into the agent when you want it to cleanse, classify, and validate an FBA Analysis Export CSV.
**Key Features:**
- Executes an 8-phase analysis pipeline.
- Enforces unit-quantity mismatch detection using comprehensive regex targeting UK multipack patterns (`N x`, `Pack of N`).
- Mandates cross-referencing against the original Financial Report to catch fee discrepancies.
- Strictly defines buckets (A, B, C) and prevents T3 matches from contaminating high-confidence lists.
- Instructs the agent on exactly which external skills to employ (e.g., `@firecrawl-scraper`, `@deep-research`) and when.

### 2. `skill_reference_analysis.md`
**Type:** Diagnostic & Architectural Reasoning
**Purpose:** The reasoning document that dictates *why* certain skills are used in the workflow and why others were explicitly rejected.
**Key Features:**
- Maps 5 specific agent failure modes (e.g., Tool Avoidance, T3 Contamination) to concrete solutions.
- Explains the proper use case for `@deep-research` (category-level trends) vs. `@playwright-skill` (surgical price checks).
- Documents why generic skills like `@pricing-strategy` and `@systematic-debugging` were excluded to save token context and prevent task drift.

### 3. `stale-data-workflow/` (Folder)
**Type:** Antigravity Skill Bundle
**Purpose:** Contains the rule sets and execution enforcements for dealing with Amazon FBA data older than 14 days. 
**Key Files Inside:**
- `SKILL.md`: The main agent instruction file laying out the 6-phase triage process (triage > system scrape > validate).
- `references/EXECUTION_ENFORCEMENT.md`: The mandatory protocol that forces the agent to stop, provide file-based evidence, and seek user approval before moving to the next phase, preventing runaway AI hallucinations.

---

### How to use this folder:
When you have a new supplier CSV to analyze (e.g., from PoundWholesale), you do not need to rewrite your instructions. 
Simply provide the agent with:
1. The **Analysis CSV path**
2. The **Financial Report path**
3. The content of `fba_product_validation_prompt.md`

The prompt itself will dynamically load the related skills from the `.gemini/antigravity/skills` directory to complete the task accurately.
