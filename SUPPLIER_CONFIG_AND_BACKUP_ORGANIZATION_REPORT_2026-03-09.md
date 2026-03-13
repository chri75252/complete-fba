# Amazon FBA Agent System v32 - Supplier Config and Backup Organization Report

Date: 2026-03-09 (UTC+4)  
Short Project Name: Amazon FBA Agent System v32 (PostLongRunPreKiro2)  
Canonical Repo Path: `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-`

## Why this report file exists
The UI renders long URL-encoded project paths poorly. This report uses a short readable project name and plain Windows paths.

## Supplier Config Decisions (Evidence-Backed)

### 1) PoundWholesale
- Keep: `config\supplier_configs\poundwholesale.co.uk.json`
- Review/remove candidate: `config\supplier_configs\poundwholesale-co-uk.json`
- Review/remove candidate: `config\supplier_configs\www.poundwholesale.co.uk.json`
- Evidence:
  - `config\system_config.json:267` uses `supplier_name = "poundwholesale.co.uk"`.
  - `run_custom_poundwholesale.py:82` builds config path as `f"{supplier_name}.json"`.
  - `tools\poundwholesale\supplier_authentication_service.py:81` directly loads `poundwholesale.co.uk.json`.
  - `config\supplier_config_loader.py:31-35` strips `www.` before filename resolution.

### 2) Clearance King
- Keep: `config\supplier_configs\clearance-king.co.uk.json`
- Review/remove candidate: `config\supplier_configs\clearance-king.json`
- Review/remove candidate: `config\supplier_configs\clearance-king - Copy.json`
- Evidence:
  - `config\system_config.json:275` uses `supplier_name = "clearance-king.co.uk"`.
  - `run_custom_clearance_king.py:82` builds config path as `f"{supplier_name}.json"`.
  - `tools\clearance_king\supplier_authentication_service.py:63` and `:149` directly load `clearance-king.co.uk.json`.
  - GitNexus HTTP query confirms these files exist in the indexed repo.

### 3) Wholesale Trading Supplies
- Keep (current runtime): `config\supplier_configs\wholesaletradingsupplies.com.json`
- Review needed: workflow uses `supplier_name = wholesaletradingsupplies.co.uk` but `supplier_url = https://wholesaletradingsupplies.com`.
- Evidence:
  - `config\system_config.json:312-313` shows `.co.uk` supplier name and `.com` supplier URL.
  - `run_custom_wholesaletradingsupplies-co-uk.py:82` builds `f"{supplier_name}.json`.
  - `tools\configurable_supplier_scraper.py:1897+` resolves selector config by domain from URL.
  - Existing file present: `config\supplier_configs\wholesaletradingsupplies.com.json`.

## Backup/Copy Script Organization Completed

Moved backup/copy/old Python script variants into per-folder backup containers:

- `tools\backup_organized_20260309` -> 46 files
- `utils\backup_organized_20260309` -> 31 files
- `control_plane\backup_organized_20260309` -> 12 files
- `dashboard\backup_organized_20260309` -> 4 files
- `config\backup_organized_20260309` -> 1 file

Total moved: 94 files.

Post-check result:
- Remaining matching backup/copy/old Python script variants in these folders (outside organized backup folders): 0

## Scope Restrictions Respected
- No changes made in `OUTPUTS\` or `OUTPUTS - Copy\`.
- No changes made to root copy-version folders (kept for later review).

## Intentionally Untouched (For Later Review)

Root folders:
- `archive`
- `archive_new`
- `backup`
- `codex_sgent-Copy`
- `codex_sgent-old`
- `codex_sgent-old-Copy`
- `src-Copy_(2)`
- `src-Copy-old`
- `src-Copy-old-copy`
- `OUTPUTS - Copy`
- `supplier-onboarding - backup`

Root-level script files (examples):
- `run_custom_clearance_king - Copy.py`
- `run_custom_clearance_king.py.bak_09-02-26`
- `run_custom_dkwholesale-com.py.bak_09-02-26`
- `run_custom_efghousewares-co-uk.py.bak_0-02-261`
- `run_custom_poundwholesale.py.bak_09-02-26`
- `run_custom_stationerywholesale-co-uk.py.bak`

## GitNexus MCP Status Note
- Codex native GitNexus MCP tool transport is failing in this session (`Transport closed`), so graph evidence was collected through the running GitNexus HTTP server endpoints (`/api/repos`, `/api/query`, `/api/search`, `/api/graph`).
