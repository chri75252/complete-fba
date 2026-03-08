# Re-Audit Triangulation Table

| Run ID | Type | Status JSON | Log File | Output Artifacts | Final Reconciled Verdict |
|--------|------|-------------|----------|------------------|--------------------------|
| `0695` (Angel) | Sandbox Category Resume | `state: done` | `IndexError` / `Traceback` present | `categories_subset.json` exists (1 URL) | **FAILED**. Worker incorrectly trusted exit code 0 despite a fatal Python crash. |
| `d8f5` (EFG) | Product List Refresh | `state: done` | `Event loop is closed` traceback at shutdown | `linking_map.json` exists (6 entries) | **DONE**. Traceback is purely a shutdown artifact. The job completed its work. |
