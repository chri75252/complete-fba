# KNOWN SHARP EDGES

This document tracks known architectural quirks, potential failure points, and technical debt that requires careful handling.

## 1. OpenAI Key Hard-Exit
- **Location**: `tools/amazon_playwright_extractor.py#L39`
- **Behavior**: The script performs a `sys.exit(1)` if `OPENAI_API_KEY` is missing from the environment.
- **Impact**: Cascading workflow failure if keys aren't pre-validated.

## 2. Onboarding Wizard Category Paths Inconsistency
- **Context**: `utils/supplier_onboarding_wizard.py`
- **Issue**: Inconsistency in how category sources are resolved (relative vs absolute) across different onboarding modes, which can lead to "File Not Found" errors during automated validation.

## 3. Chrome Port 9222 Collision
- **Context**: `utils/browser_manager.py` and `config/system_config.json`
- **Issue**: The system defaults to port `9222`. If another Chrome instance or a zombie process is holding this port, the `BrowserManager` fails to attach without a clear error message in some runner environments.

## 4. IPv6 vs IPv4 CDP Binding
- **Context**: Browser Automation
- **Issue**: Playwright sometimes attempts to connect to `[::1]` (IPv6) while Chrome is bound to `127.0.0.1` (IPv4), or vice versa. This causes connection timeouts despite the port being open.

## 5. Windows Path Length Limits
- **Reference**: `AGENTS.md` Section 5 (State Management)
- **Issue**: Deep directory structures for `OUTPUTS\FBA_ANALYSIS\amazon_cache\...` can exceed the MAX_PATH (260 chars) limit on Windows systems where Long Paths are not enabled, causing atomic save failures in `WindowsSaveGuardian`.
