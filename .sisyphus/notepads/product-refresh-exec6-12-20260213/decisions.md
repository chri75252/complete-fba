# Decisions

## 2026-02-17
- Use deterministic runtime monkeypatch validation for `control_plane.run_product_list_refresh.main()` to prove Issue #6 completion-state behavior without touching protected workflow files or requiring live browser dependencies.
- Validate Issue #7 using worker-level terminal recompute helper on disk artifacts for both object-shaped and list-shaped products payloads to directly test the fixed counting logic.
