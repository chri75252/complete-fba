---
trigger: model_decision
description: "Read this rule when the user is working on anything code-related in this project: Python scripts, supplier scrapers, passive extraction workflows, Amazon data extractors, financial calculators, state management, browser automation, linking maps, cached products, cross-file refactoring, debugging, running the system, adding suppliers, editing configs, or any task that involves files in this repository. Do NOT read for conversational messages (greetings, general questions unrelated to this codebase, or questions about other projects)."
---

Read the full project architecture and contributor rules from the `AGENTS.md` file in the
project root before proceeding. It contains absolute constraints, backup protocols, path
conventions, state management rules, and engineering heuristics that must be followed.

Key areas covered in AGENTS.md:
- Section 0: Absolute rules (no proactive edits, verification protocols)
- Section 2: Architecture (entry points, workflow engine, browser management)
- Section 4: Data processing workflow (supplier → Amazon → financials)
- Section 5: State management (FixedEnhancedStateManager, atomic writes)
- Section 8: Coding standards and engineering heuristics
- Section 17: Critical behavioral rules (state tracking, cache preservation)
- Section 24-25: MCP integrations and sub-agent orchestration
