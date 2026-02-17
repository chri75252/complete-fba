# Draft: Control Plane Chat + Scraper Issues

## Requirements (confirmed)
- User wants to continue ULW (ultra thorough) debugging/fixes for Control Plane chat UI failures after user testing.
- Fix chat-run failures when URL contains `www.` (e.g. `www.efghousewares.co.uk`).
- Ensure natural language limits like "first 12 products" are respected.
- Fix follow-up chat questions that lose context (LLM responds generically).
- Investigate category scrape producing 0 product URLs (angelwholesale example).

## Technical Decisions (proposed)
- Canonicalize supplier domains by stripping `www.` at every URL→domain inference point.
- Expand runtime constraint parsing to support natural language limits ("first N products", "only N products", etc.).
- Pass recent chat history into the LLM planner prompt (bounded to avoid prompt bloat).
- Improve `ask_clarify` so it uses error context and asks specific questions instead of generic prompts.

## Research Findings (file-grounded)
- Domain inference currently keeps `www.` in `_infer_supplier_domain_from_url()` in `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\control_plane\chat_orchestrator.py`.
- `_extract_category_urls()` strips `www.` only for *filtering known domains*, not for the supplier used in job creation.
- Runtime constraint parsing only matched explicit `max_products` tokens; natural language phrases like "first 12 products" were not captured → ends up as `0` (infinite mode).
- `ask_clarify()` currently returns a generic question when `missing_params` is empty: `"What would you like me to do?..."` in `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\control_plane\tools\clarify.py`.
- Chat UI calls `plan_tool_call(user_input, Path(base_dir))` with only the current message; no conversation history is provided in `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\dashboard\chat_panel.py`.
- System planner instructions explicitly say: "Never guess file paths" in `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\control_plane\prompts\SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md`.

## Open Questions
- Scope: include scraper 0-products fix in the same work plan, or focus only on chat/control-plane?
- Verification: do you want automated tests added (pytest) or manual verification only?
- Chat history: how much history should be injected into the planner prompt (e.g., last 12 messages vs last 25)?

## Scope Boundaries
- INCLUDE: control-plane chat planning + clarification improvements; domain normalization; runtime constraint parsing; (optionally) angelwholesale 0-products scrape.
- EXCLUDE: large refactors of the workflow engine unrelated to chat/control-plane; unrelated supplier onboarding.
