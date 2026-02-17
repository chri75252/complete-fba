## Dashboard & Chat UI
- UI is structured into 3 tabs: Dashboard, Operator, Chat in app_fixed.py.
- Chat UI uses session state for messages and implements confirmation gating for write tools.
- Operator tab handles job orchestration via JobManager and provides run monitoring.
- Validation helpers (validate_supplier_data) are key for debugging data loading issues.
