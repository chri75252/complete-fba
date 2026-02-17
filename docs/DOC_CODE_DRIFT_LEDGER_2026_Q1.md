# Doc/Code Drift Ledger (2026 Q1)

**Generated**: 2026-02-10
**Quarter**: 2026 Q1

This ledger tracks mismatches between the repository's documentation (AGENTS.md, README.md, wiki-dec-3) and the actual implementation observed in code.

---

## 📊 Summary Table: High-Impact Drifts

| Area | Doc Claim | Code Reality | Impact |
| :--- | :--- | :--- | :--- |
| **Dashboard** | "Monitoring dashboard for system health and financial metrics." | `app_fixed.py` includes "Operator" and "Chat" tabs for active control. | Users unaware of integrated command/control and LLM interaction. |
| **Config** | JSON `chrome.debug_port` controls connection. | Port `9222` is largely hard-coded in runners and `PassiveExtractionWorkflow`. | Configuration changes to the port in `system_config.json` are ignored. |
| **Onboarding** | Unified naming for category files. | `supplier_onboarding_wizard.py` switches between domain labels and workflow keys. | Inconsistent file creation leads to "missing config" errors during runs. |
| **Refresh** | Product refresh is a minimal/standalone operation. | Uses `FixedAmazonExtractor`, importing full AI/Extractor dependencies. | Refresh runs crash if `OPENAI_API_KEY` is missing (Extractor hard-exit). |
| **Analysis** | Flexible price range for product sourcing. | Hard £20 upper bound enforced in `system_config.json` and `AGENTS.md`. | High-ticket items are silently excluded despite "exhaustive" mode claims. |
| **Chat** | (Omitted from core workflow documentation) | `chat_panel.py` and `operator_control_plane.py` are first-class citizens. | The "Agentic" core of the system is undocumented for end-users. |
| **State** | Resumption uses simple "last product" pointers. | Uses frozen category manifests and `persistent_category_index` (PCI). | Manual state repairs often break resumption by missing the frozen manifest logic. |

---

## 1. Dashboard & Control Plane
- **Code Reference**: `dashboard/app_fixed.py`, `dashboard/chat_panel.py`, `dashboard/pages/01_Operator_Control_Plane.py`
- **Drift**: README.md and older wiki entries treat the dashboard as a passive visualization tool.
- **Reality**: The dashboard is now the primary GUI for the Control Plane job system. It can spawn jobs, inject override configs, and manage the worker queue via `chat_panel.py`.

## 2. Configuration & CDP Port
- **Code Reference**: `tools/passive_extraction_workflow_latest.py#L225`, `AGENTS.md#L112`
- **Drift**: Documentation implies full configurability of the Chrome debug port.
- **Reality**: While `system_config.json` has a `chrome.debug_port` field, many components default to `9222` or explicitly check `9222` first. `AGENTS.md` explicitly warns about this code-level hard-coding.

## 3. Supplier Onboarding Inconsistency
- **Code Reference**: `utils/supplier_onboarding_wizard.py`
- **Drift**: Onboarding guides suggest `config/{supplier}.json` and `config/{supplier}_categories.json`.
- **Reality**: The wizard sometimes generates `config/{workflow_key}_categories.json` and sometimes `config/{domain_label}_categories.json`. This causes the Workflow Engine (which expects a specific path from the config loader) to fail to find URLs.

## 4. Product Refresh (PRD_04) Gaps
- **Code Reference**: `control_plane/run_product_list_refresh.py`
- **Drift**: Described as a lightweight "refresh" to update prices.
- **Reality**: It instantiates `FixedAmazonExtractor`, which triggers a hard process exit if `OPENAI_API_KEY` is not in the environment. This makes "minimal" refreshes impossible in restricted environments.

## 5. Analysis & Pricing Bounds
- **Code Reference**: `config/system_config.json`, `processing_limits.max_price_gbp`
- **Drift**: System is often marketed as "Exhaustive Mode - Process EVERY product".
- **Reality**: The £20 ceiling is a strict invariant. Products exceeding this price are filtered at the supplier level, never reaching Amazon matching, regardless of "exhaustive" settings.

## 6. Chat & Natural Language Operations
- **Code Reference**: `dashboard/chat_panel.py`, `fba_agent/`
- **Drift**: Not mentioned in the primary `AGENTS.md` architecture overview.
- **Reality**: The system has a robust `fba_agent` subsystem and a chat-based dashboard panel that allows creating runs via natural language (e.g., "Run poundwholesale for all home categories").

---

## 🛡️ Action Plan (2026 Q1)

1. **Update AGENTS.md**: Add sections for the Control Plane, Operator Page, and Chat Panel.
2. **Standardize Onboarding**: Force the wizard to use the `workflow_key` consistently for all file generation.
3. **Fix Port Hard-coding**: Refactor `PassiveExtractionWorkflow` and runners to strictly honor the `SystemConfigLoader` port value.
4. **Extractor Decoupling**: Modify `FixedAmazonExtractor` to allow "non-AI" imports without hard-exiting, facilitating lightweight refreshes.
5. **Transparency**: Explicitly log a warning at startup if products are being filtered by the £20 price cap, even in "Exhaustive" mode.

(End)
