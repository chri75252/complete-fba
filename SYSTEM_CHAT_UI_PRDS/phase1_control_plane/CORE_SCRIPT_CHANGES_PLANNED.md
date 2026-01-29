# Planned Core Script Changes (Phase 1)

This document lists **every planned edit** to existing scripts for Phase 1, with:
- file path
- exact line numbers (based on current repo snapshot)
- diff-style planned patch (approximate)
- expected behavioral impact
- what to test after Phase 1

Backups for these files are stored under:
- `SYSTEM_CHAT_UI_PRDS/backups/phase1_planned_changes_20260125/`

## Change A — `FBA_SYSTEM_CONFIG_PATH` env override
**File**: `config/system_config_loader.py`

**Current location**: `config/system_config_loader.py:16-23`

### Planned Diff (approx)
```diff
 class SystemConfigLoader:
@@
-    def __init__(self, config_path: str | None = None):
-        if config_path:
-            self.config_path = config_path
-        else:
-            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
-            self.config_path = os.path.join(base_dir, "config", "system_config.json")
+    def __init__(self, config_path: str | None = None):
+        if config_path:
+            self.config_path = config_path
+        else:
+            env_path = os.environ.get("FBA_SYSTEM_CONFIG_PATH")
+            if env_path:
+                self.config_path = env_path
+            else:
+                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
+                self.config_path = os.path.join(base_dir, "config", "system_config.json")
```

### Effect on Workflow
- **Default behavior unchanged** unless `FBA_SYSTEM_CONFIG_PATH` is set.
- Enables running with per-run merged config without editing canonical config.

### What to Test
1. Normal runs with env var unset (should behave identically).
2. Instantiate `SystemConfigLoader()` with env var set to a valid config path.
3. Instantiate with env var set to missing file (should log error, behave safely).

## Change B — Categories config path respected when loading categories list
**File**: `tools/passive_extraction_workflow_latest.py`

**Current location**: `_get_predefined_categories` at `tools/passive_extraction_workflow_latest.py:3893-3924`

### Planned Diff (approx)
```diff
 def _get_predefined_categories(self, supplier_name: str) -> list:
@@
-        try:
-            # Robust path construction using pathlib
-            base_name = supplier_name.split('.')[0]
-            config_path = (
-                Path(__file__).parent.parent
-                / "config"
-                / f"{base_name}_categories.json"
-            )
+        try:
+            categories_config_path = None
+            try:
+                categories_config_path = (self.workflow_config or {}).get("categories_config_path")
+            except Exception:
+                categories_config_path = None
+
+            if categories_config_path:
+                config_path = Path(categories_config_path)
+            else:
+                # Backwards compatible convention
+                base_name = supplier_name.split('.')[0]
+                config_path = (
+                    Path(__file__).parent.parent
+                    / "config"
+                    / f"{base_name}_categories.json"
+                )
```

### Effect on Workflow
- Default behavior unchanged when `categories_config_path` is not present.
- When workflow config includes `categories_config_path`, category loading uses that.
- This enables per-run category subset files without editing conventional config files.

### What to Test
1. Run with existing suppliers (no `categories_config_path` changes) — must load same categories.
2. Set `categories_config_path` to a subset JSON — must load subset.
3. Confirm `_get_authoritative_category_count` and `_get_predefined_categories` agree (count matches list).

## Note on Diagnostics
This environment does not have Python LSP (`basedpyright`) installed, so line-level diagnostics tooling is not available via `lsp_diagnostics`. Use:
- `python -m py_compile <file>`
- `pytest` where applicable

