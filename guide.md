---
trigger: always_on
glob:
description:
---


# 🛡️ CRITICAL PROTOCOL: The Triangulation Rule
**NEVER** answer a debugging question or propose a fix without first conducting a **Triangulation Analysis**. You must verify every fact against **3 Sources of Truth** simultaneously:

1.  **The Symptom (Logs/Errors):** What exactly is the system reporting? (e.g., 'No products found').
2.  **The Logic (Source Code):** Trace the **exact function** generating that error. *How* does it decide to report that error? (e.g., 'It returns empty list IF selectors.get('field_mappings') is missing').
3.  **The Data (Config/State):** Does the input data (JSON/Variables) match the **structure** expected by the Logic? (e.g., 'Does the JSON file actually HAVE a field_mappings key?').

**MANDATORY BEHAVIOR:**
*   **Trace Before Fixing:** Do not propose a fix until you have quoted the line of code responsible for the error.
*   **Distrust Assumptions:** Never assume a file structure is correct just because it 'looks right'. Verify it against the code's schema expectations.
*   **Explicit Confirmation:** In your analysis, explicitly state: *'I have verified this against [Log], [Code Line #], and [Config File].'*

# 📝 Planning & Reporting Protocol
**NEVER** provide generic summaries like "I will update the file." You MUST provide:
1.  **The "Diff"**: Explicitly state what will be REMOVED and what will be ADDED.
    *   *Example*: "Replace Section A (General Summary) with Section B (Detailed Checklist)."
2.  **The "Why"**: Justify every change.
    *   *Example*: "Removing 'Sample JSON' because it contradicts the new schema. Adding 'Field Mappings' warning to prevent validation errors."
3.  **The "How"**: If proposing a new feature, outline the exact logic or code structure.

# 📚 Documentation Standards (Instructional Density)
**NEVER** over-summarize instructions for the agent. "High Instructional Density" is required.
1.  **Explicit Checklists**: Do not say "Validate URLs." Say "Check for http/https, domain match, and valid syntax."
2.  **Positive & Negative Examples**: Always provide "✅ Valid" AND "❌ Invalid" examples.
    *   *Critical*: Show *why* something is invalid (e.g., "❌ Invalid: :text() (Playwright extension)").
3.  **Code Snippets**: When asking an agent to verify code, provide the **exact snippet** to look for (imports, class names, function signatures).

# 📂 System Architecture & Key Files
*   **Workflow Logic:** tools/passive_extraction_workflow_latest.py (The 'Brain' - orchestrates phases).
*   **Scraper Logic:** tools/configurable_supplier_scraper.py (The 'Hands' - does the actual work).
*   **State Management:** utils/fixed_enhanced_state_manager.py (The 'Memory' - tracks progress).
*   **Configuration:** config/supplier_configs/*.json (The 'Instructions' - defines *how* to scrape).

**⚠️ Configuration Rule:** The scraper code (configurable_supplier_scraper.py) is **strict**. It expects selectors to be nested inside field_mappings. Flat JSON files will fail silently. ALWAYS check the JSON structure against the code's extract_product_elements function.

# 🚫 Operational Rules
1.  **No Unauthorized Edits:** NEVER edit a file unless explicitly requested. If a fix is needed, **propose** it first with a diff or explanation.
2.  **Evidence-Based Answers:** Every claim must be backed by a file path, line number, or log entry. Do not generalize.
3.  **Contextual Awareness:** Before answering, check processing_state.json (if relevant) to understand *where* the user is in the workflow.
4.  **Front-Loaded Interaction:** For complex tasks (like onboarding), **STOP** and gather ALL necessary information (Auth, Configs, URLs) *before* generating any code. Do not rely on iterative "fix-it-later" loops.
