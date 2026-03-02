# Analysis: LLM Autonomous Tailoring Capabilities

## 1. Diff Analysis: Template vs Final Scripts

I compared the generic `.claude/skills/supplier-onboarding/templates/runner_template.py.txt` to the finalized `run_custom_poundwholesale.py` and `run_custom_clearance_king.py` scripts.

**Findings:**
1.  **Zero Custom Logic in Runners:** The generated `run_custom_*.py` scripts are actually extremely standardized. There are **no custom `time.sleep()` statements**, no custom cookie injections, and no special HTTP headers hardcoded into the `run_custom_*.py` files themselves. 
2.  **Config-Driven Architecture:** All of the complexity (which selectors to use, what URLs to hit, how to paginate) is perfectly abstracted away into the `config/supplier_configs/*.json` files. The runner script simply loads the JSON config and passes it to the `PassiveExtractionWorkflow`.
3.  **Authentication Abstraction:** The only major difference between runners is whether they import and instantiate the `supplier_authentication_service.py` helper. This is handled flawlessly by the `supplier_onboarding_wizard.py` logic based on the `authentication_required` flag in the JSON.

**The Auth Helper Gap:**
I compared the generic `auth_helper_template.py.txt` to the finalized `tools/poundwholesale/supplier_authentication_service.py`. 
*   **This is where tailoring happens.** The template is full of `TODO:` comments. The final Poundwholesale script has hardcoded Magento selectors (`input[name='login[username]']`), specific URL paths (`/customer/account/login/`), and custom error message checking (`.message-error`).

---

## 2. LLM Autonomous Capability

**Can the Chat UI LLM magically know what to inject into the Python files autonomously?**

*   **For `run_custom_{supplier}.py`**: There is almost never anything to tailor here. The wizard handles it.
*   **For `supplier_authentication_service.py`**: **NO**, the LLM cannot autonomously divine the exact Python playwright login logic without external help.

**Why it can't do it autonomously:**
When the wizard generates the `supplier_authentication_service.py` template, it drops `TODO:` blocks for the login selectors. The Chat UI LLM cannot "see" the supplier's live login page. It doesn't know if the email field is `#login_email` or `input[name='login[username]']` unless you explicitly give it the HTML or the CSS selectors.

*Note:* I checked the new JSON schema you provided for `stationerywholesale.co.uk`. You brilliantly included an `"authentication"` block inside the JSON with the `login_selectors` mapped out! But the python wizard template (`auth_helper_template.py.txt`) currently does not automatically read those JSON values; it expects hardcoded python logic.

---

## 3. Conclusion & Answer to Your Question

You asked: *"I should inform it of what kind of changes are needed? Can it not identify it on its own?"*

**Answer:** **Yes, you MUST inform it.** 

The LLM does not have autonomous browser vision to guess the login page structure or know if a popup is blocking the screen. 

If the script requires custom tailoring (like filling out the `supplier_authentication_service.py` logic or adding a custom `time.sleep()`), you must explicitly instruct the LLM via the Chat UI:

> *"Read `tools/supplier/supplier_authentication_service.py`. I need you to implement the login logic. The email selector is `#email`, the password selector is `#pass`, and the button is `#submit`. Add a 5 second sleep after clicking submit."*

Because we are implementing the safe `edit_repo_file` logic (via `write_output_file` with the Prompt Lock), the LLM will then happily take your instructions, write the custom Python code into the file, and save it safely.