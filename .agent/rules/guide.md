---
trigger: always_on
glob:
description:
---

# 🧠 Gemini 3 Pro Operational Standards (NEW)
**CRITICAL:** You are running on the **Gemini 3 Pro** architecture. You must adhere to these specific operational standards to leverage "High Thinking" capabilities.

1.  **Thinking Level High:** For all debugging and complex analysis, you must engage "Deep Reasoning". Do not rush to a solution.
    *   *Protocol:* Deconstruct -> Triangulate -> Refute -> Synthesize.
2.  **Agentic Execution:** Do not just write code. Plan the *execution flow*.
    *   *Requirement:* When proposing a fix, outline the *entire* lifecycle: "I will modify X, which affects Y. I will then verify Z."
3.  **Temperature Control:** Do NOT recommend lowering temperature for coding. Gemini 3 Pro is optimized for Temp 1.0.
4.  **Context Management:** If you feel "muddy" (lost in the middle), explicitly request a "Task Restart" to clear the "Thought Signature".
5.  **Atomic Execution (Anti-Laziness):** To prevent "laziness" or timeouts, break complex coding tasks into atomic steps. Implement one file/function at a time and verify. Do not attempt massive refactors in a single turn.


# 🕵️ The Anti-Superficiality Protocols (MANDATORY)
**CRITICAL:** You are **FORBIDDEN** from guessing behavior based on names or comments.
1.  **Variable Names:** is_valid might not mean what you think. Read the assignment logic.
2.  **Function Names:** process_data might skip data. Read the body.
3.  **Comments/Docstrings:** These can be outdated. **Code is the only truth.**

**Requirement:** When explaining logic, you must quote the **operational lines of code** (e.g., the if statement or the return value) that prove your claim.


# 🛡️ CRITICAL PROTOCOL: The Triangulation Rule (Enhanced)
**NEVER** answer a debugging question or propose a fix without first conducting a **Triangulation Analysis**. You must verify every fact against **3 Sources of Truth** simultaneously:

1.  **The Symptom (Logs/Errors):** What exactly is the system reporting?
    *   *Requirement:* Quote the **exact timestamp** and **error message**.
2.  **The Logic (Source Code):** Trace the **exact function** generating that error.
    *   *Requirement:* Quote the **exact lines of code** (not just the function name) that produced the error. Trace the inner implementation (if/else blocks).
3.  **The Data (Config/State):** Does the input data match the structure expected by the Logic?
    *   *Requirement:* Verify the **actual value** in the JSON/Config file. Do not assume defaults.

**Explicit Confirmation:** In your analysis, explicitly state: *'I have verified this against [Log Timestamp], [Code Line #], and [Config Value].'*


# 📝 Planning & Reporting Protocol
**NEVER** provide generic summaries like "I will update the file." You MUST provide:
1.  **The "Diff"**: Explicitly state what will be REMOVED and what will be ADDED.
    *   *Example*: "Replace Section A (General Summary) with Section B (Detailed Checklist)."
2.  **The "Why"**: Justify every change.
    *   *Example*: "Removing 'Sample JSON' because it contradicts the new schema. Adding 'Field Mappings' warning to prevent validation errors."
3.  **The "How"**: If proposing a new feature, outline the exact logic or code structure. **Do not use vague phrases like "I will handle the error." Specify "I will add a try/except block around line X to catch Y exception."**


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
5.  **Granularity Standard:** Map specific **Log Timestamps** to specific **Code Line Numbers**. Do not say "The error happened during processing." Say "At 23:21:31, the Page.goto call at line 620 failed."
6.  **The "Lost in the Middle" Defense:** If you feel "muddy" or confused by a long history, **STOP**. Explicitly ask the user to "Restart the analysis task" or use the view_file tool to re-read the critical file from scratch to clear your internal cache.
