# GitNexus Guide

GitNexus is installed for this repo, and this project now uses a curated runtime-context workflow so selected `OUTPUTS` and `logs` artifacts appear in the knowledge graph without indexing everything.

## Important Behavior

GitNexus does **not** natively support "latest N files" filters by folder. It also ignores many data formats by default (`.json`, `.csv`, `.log`, etc.).

To solve this, we generate Python mirror files under `gitnexus_runtime_context/`. Those mirror files contain metadata and previews of the selected runtime artifacts, so GitNexus can index them.

## Installation and Integration Configuration

This is the exact setup used to make GitNexus work reliably in this project.

### Installed CLI Locations

- Global launcher (what `gitnexus ...` uses in terminal): `C:\Users\chris\AppData\Roaming\npm\gitnexus.cmd`
- Project-local CLI (useful for deterministic project runs): `node_modules/.bin/gitnexus.cmd`

### Core Project Config Files

- `.gitnexusignore`:
  - hard excludes for raw generated/runtime/noisy folders
  - preserves the curated `gitnexus_runtime_context/` mirror plus the live workflow code/config/docs layer
- `config/gitnexus_scope_rules.json`:
  - selective mirror rules (latest per live supplier, sandbox quotas, financial/report logic)
- `scripts/generate_gitnexus_filtered_context.py`:
  - generates mirror files from selected `OUTPUTS/...` and `logs/debug/...`
  - preserves path hierarchy under `gitnexus_runtime_context/OUTPUTS/...` and `gitnexus_runtime_context/logs/...`
- `gitnexus_runtime_context/_manifest.json`:
  - generated snapshot of exactly what was selected for indexing

### Runtime Compatibility Patches Applied

- Local GitNexus patch: `node_modules/gitnexus/dist/config/ignore-service.js`
  - patched to read `.gitnexus/config.json` ignore patterns
- Local GitNexus patch: `node_modules/gitnexus/dist/server/api.js`
  - patched to cap graph payload size so frontend render/serialization remains stable
- Global GitNexus mirrors of the same patches:
  - `C:\Users\chris\AppData\Roaming\npm\node_modules\gitnexus\dist\config\ignore-service.js`
  - `C:\Users\chris\AppData\Roaming\npm\node_modules\gitnexus\dist\server\api.js`

### Kuzu Native Module Fixes Applied (Local + Global)

- Local files:
  - `node_modules/kuzu/index.mjs`
  - `node_modules/kuzu/index.js`
  - `node_modules/kuzu/kuzujs.node`
- Global files:
  - `C:\Users\chris\AppData\Roaming\npm\node_modules\gitnexus\node_modules\kuzu/index.mjs`
  - `C:\Users\chris\AppData\Roaming\npm\node_modules\gitnexus\node_modules\kuzu/index.js`
  - `C:\Users\chris\AppData\Roaming\npm\node_modules\gitnexus\node_modules\kuzu/kuzujs.node`

Note: `node_modules` patches can be overwritten by reinstalling/updating packages. If that happens, reapply this guide's integration steps.

## Launch Workflow

1. Generate curated runtime context:

```bash
python scripts/generate_gitnexus_filtered_context.py
```

2. Build or refresh GitNexus index:

```bash
npx gitnexus analyze . --force
```

3. Start the local server:

```bash
gitnexus serve --port 3333
```

4. Open the visual UI:

Navigate to **[https://gitnexus.vercel.app](https://gitnexus.vercel.app)** in your browser, click `Server`, and enter:

```text
http://127.0.0.1:3333
```

*(Note: `http://127.0.0.1:3333` is the backend API only. If you open that URL directly in the browser address bar, you will see `Cannot GET /`, which is normal.)*

## What Gets Reflected (Current Rules)

Rules file: `config/gitnexus_scope_rules.json`

Selected runtime files are mirrored into `gitnexus_runtime_context/OUTPUTS/...` and `gitnexus_runtime_context/logs/...` so the graph preserves the original folder shape instead of flattening everything into category buckets.

- `OUTPUTS/CACHE/processing_states`: latest main file per live supplier + latest 1 sandbox file
- `OUTPUTS/cached_products`: latest main file per live supplier + latest 1 sandbox file
- `OUTPUTS/FBA_ANALYSIS/linking_maps`: latest main linking map per live supplier + latest 1 sandbox file
- `OUTPUTS/FBA_ANALYSIS/amazon_cache`: latest 1 file
- `OUTPUTS/manifests`: all main folders + latest 1 sandbox folder
- `OUTPUTS/PRODUCTS_LISTS`: latest main product list per live supplier + latest 1 sandbox file
- `config/*categories*.json`: latest main category file per live supplier + latest 1 sandbox file
- `logs/debug`: latest main log per live supplier + latest 1 sandbox file
- `OUTPUTS/FBA_ANALYSIS/financial_reports`: latest main report per live supplier + latest 1 sandbox file

The large orchestration file `tools/passive_extraction_workflow_latest.py` remains explicitly included in the GitNexus scope, and its supporting configuration layer is preserved via `config/system_config.json`, `config/system_config_loader.py`, `config/supplier_configs/`, and the curated category files.

Sandbox detection is based on path/name containing `sandbox` or `run_id`.

## Where To Adjust Inclusion/Exclusion

Edit `config/gitnexus_scope_rules.json`.

Edit `.gitnexusignore` for hard exclusions. Current exclusions include raw `OUTPUTS`, raw `logs`, `OUTPUTS - Copy`, `backup`, `archive`, `archive_new`, legacy copy trees, and vendor/tool caches.

Key knobs:

- `sandbox_latest` / `latest`: quota per folder
- `global.preview_lines`: how much file content preview is mirrored
- `global.sandbox_min_unique_suppliers`:
  - `0` = strict newest files regardless of supplier (current behavior)
  - `>0` = enforce minimum supplier diversity before filling remaining newest slots

After changing rules, rerun:

```bash
python scripts/generate_gitnexus_filtered_context.py
npx gitnexus analyze . --force
```

## Refresh Workflow

Use this when files are added, removed, or updated.

1. If you changed normal source code only:

```bash
gitnexus analyze . --force
```

2. If you changed anything in the selectively mirrored runtime areas (`OUTPUTS/...` or `logs/debug/...`):

```bash
python scripts/generate_gitnexus_filtered_context.py
gitnexus analyze . --force
```

3. Restart the local server if it is already running:

```bash
gitnexus serve --port 3333
```

4. Hard refresh the browser page (`Ctrl+Shift+R`) and reconnect if needed.

## Suggested Setting For Better Architecture Coverage

If newest sandbox files are often from one supplier, set:

```json
"global": {
  "sandbox_min_unique_suppliers": 3
}
```

This keeps your "latest-first" behavior while guaranteeing at least 3 supplier perspectives in sandbox snapshots.

## Practical FBA Use Cases

1. Validate resumption behavior by tracing `processing_states` mirrors alongside workflow code.
2. Audit mapping drift by correlating mirrored `linking_maps` and `amazon_cache` snapshots with extractor logic.
3. Investigate runtime failures by querying latest `logs/debug` mirrors together with `browser_manager.py` and orchestration paths.
4. Compare financial regressions by using per-supplier largest main report mirrors plus latest sandbox report mirrors.
