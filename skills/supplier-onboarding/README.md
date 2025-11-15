# Supplier Onboarding Skill

Guided supplier onboarding for Amazon FBA Agent System with deterministic file generation, atomic operations, and comprehensive validation.

## Features

- ✅ **Deterministic File Generation**: Atomic writes with WindowsSaveGuardian (JSON-only)
- ✅ **Smart Runner Selection**: Workflow-mapped runners with automatic shim generation
- ✅ **Automatic Workflow Registration**: Auto-registers workflow in system_config.json
- ✅ **Automatic Credentials Registration**: Auto-registers credentials in system_config.json (if provided)
- ✅ **Robust Domain Normalization**: Handles URLs, hyphen-form, dot-form (all TLDs)
- ✅ **6-Criterion Sanity Check**: Validates scraping, Amazon cache, linking map, financial CSV, state, logs
- ✅ **Comprehensive Remediation**: Actionable guidance for failed checks
- ✅ **Session Management**: Persistent session files for debugging
- ✅ **Post-Sanity Full Run**: Automatic full workflow execution on sanity pass
- ✅ **Summary Generation**: Auto-generates summary.md and curated.csv (profit ≥ £2, ROI ≥ 30%, margin ≥ 25%)

## Quick Start

### Prerequisites

1. **Start Chrome with debug port:**
   ```bash
   chrome --remote-debugging-port=9222 --user-data-dir=C:\temp\chrome-debug
   ```

2. **Navigate to repository root:**
   ```bash
   cd "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32..."
   ```

3. **Prepare selectors** (use browser DevTools to copy CSS selectors)

### Usage

#### Via Claude Code (Recommended)

```
Use supplier-onboarding skill to add clearance-king.co.uk
```

#### Via Python (Testing)

```bash
cd skills/supplier-onboarding

python main.py \
  --domain "clearance-king.co.uk" \
  --categories-source "config/clearance_king_categories.json" \
  --selectors-source "config/supplier_configs/clearance-king.co.uk.json" \
  --workflow-key "clearance_king_workflow" \
  --mode generate \
  --scaffolds supplier-package runner-shim
```

## Architecture

```
Agent Skill (Orchestrator)
├─> Input validation
├─> Session file creation
├─> Wizard invocation
└─> Result presentation

Python Wizard (Executor)
├─> Domain normalization (all TLDs)
├─> Categories schema normalization
├─> File generation (staging) → save_json_atomic
├─> Atomic move to final → save_json_atomic
├─> Workflow registration → system_config.json (automatic)
├─> Credentials registration → system_config.json (if provided)
├─> Runner selection (workflow-mapped)
├─> Sanity check execution (FBA_TEST_MODE)
├─> Output verification (6 criteria)
├─> Full workflow execution (on pass)
├─> Summary + curated CSV generation
└─> Remediation generation (on fail)
```

## Parameters

### Required

- **domain**: Supplier domain (any form: URL, dot-form, hyphen-form)
- **categories_source**: Path to categories JSON or inline JSON string
- **selectors_source**: Path to selectors JSON or inline JSON object
- **workflow_key**: Workflow key in system_config.json

### Optional

- **mode**: `generate` (default) or `reference` (validate only)
- **scaffolds**: Array of `["supplier-package", "auth-helper", "runner-shim"]`
- **test_product_url**: URL for validation
- **username**: Supplier login username (required if authentication_required is true)
- **password**: Supplier login password (required if authentication_required is true)
- **authentication_required**: Boolean, set to true if supplier requires login to view prices/products

## Output

### Success Response (All Checks Passed)

```json
{
  "success": true,
  "files_generated": [
    "C:\\...\\config\\supplier_configs\\clearance-king.co.uk.json",
    "C:\\...\\config\\clearance_king_categories.json"
  ],
  "sanity_results": {
    "scraping_rate": true,
    "amazon_cache": true,
    "linking_map": true,
    "financial_csv": true,
    "processing_state": true,
    "no_critical_errors": true
  },
  "full_run_result": {
    "status": "success",
    "summary_file": "OUTPUTS/AI_SETUP_RESULTS/clearance-king-co-uk/summary_20250110_143022.md",
    "curated_file": "OUTPUTS/AI_SETUP_RESULTS/clearance-king-co-uk/curated_20250110_143022.csv",
    "total_products": 247,
    "curated_products": 83
  }
}
```

### Curated CSV Filters

Generated curated CSV applies these criteria:
- **Profit**: ≥ £2.00 (field: `net_profit_gbp`, fallback: `profit_gbp`)
- **ROI**: ≥ 30% (field: `roi_pct`, fallback: `roi_percentage`)
- **Profit Margin**: ≥ 25% (field: `margin_pct`, fallback: `profit_margin_percentage`)

**Field Name Tolerance**: The wizard tries repo-standard field names first, then falls back to alternative names if not found. This ensures compatibility across different financial CSV versions.

**Division Safety**: Curated percentage calculation is guarded against division by zero (returns 0.0% when total_count = 0).

### Summary Markdown

Contains:
- Total products analyzed
- Curated products count and percentage
- File locations (selectors, categories, financial reports)
- Next steps guidance

## Naming Conventions

The system enforces three naming forms:

1. **Dot-form** (domain): `poundwholesale.co.uk`
   - Used for: Selector config files
   - Location: `config/supplier_configs/poundwholesale.co.uk.json`

2. **Hyphen-form** (supplier_id): `poundwholesale-co-uk`
   - Used for: Linking map directories, runner shims
   - Location: `OUTPUTS/FBA_ANALYSIS/linking_maps/poundwholesale-co-uk/`

3. **Underscore-form** (supplier_name): `poundwholesale_co_uk`
   - Used for: Processing state files
   - Location: `OUTPUTS/CACHE/processing_states/poundwholesale_co_uk_processing_state.json`

## Categories Schema

The wizard normalizes categories to the standard schema:

**Standard Format**:
```json
{
  "category_urls": [
    "https://www.example.com/category1",
    "https://www.example.com/category2"
  ]
}
```

**Supported Input Formats**:

1. **List of URLs** (converted automatically):
   ```json
   ["https://example.com/cat1", "https://example.com/cat2"]
   ```

2. **List of objects** (extracts URLs):
   ```json
   [
     {"name": "Category 1", "url": "https://example.com/cat1"},
     {"name": "Category 2", "category_url": "https://example.com/cat2"}
   ]
   ```

3. **Standard format** (used as-is):
   ```json
   {"category_urls": ["https://example.com/cat1"]}
   ```

The wizard automatically:
- Normalizes any format to standard schema
- Writes to `config/{workflow_key}_categories.json`
- Updates `system_config.json` if `categories_config_path` missing

## Sanity Check Criteria

1. **Scraping Rate**: ≥20 products scraped
   - Checks: `state.system_progression.supplier_products_completed >= 20`
   - Fallback: `state.supplier_products_completed >= 20` (top-level)
2. **Amazon Cache**: ≥1 recent Amazon cache file (mtime ≥ run_start_time)
3. **Linking Map**: Updated and non-empty (>100 bytes, mtime ≥ run_start_time)
   - Location: `OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier-id}/linking_map.json`
4. **Financial CSV**: Present and >1KB (mtime ≥ run_start_time)
   - Location: `OUTPUTS/FBA_ANALYSIS/financial_reports/fba_financial_report_*.csv`
5. **Processing State**: Updated recently (mtime ≥ run_start_time)
   - Location: `OUTPUTS/CACHE/processing_states/{supplier_name_underscore}_processing_state.json`
6. **No Critical Errors**: No ERROR/CRITICAL in logs since run start
   - Scans: `logs/debug/run_custom_*.log` or `OUTPUTS/logs/debug/*`

## Troubleshooting

### Selectors Invalid

```
Issue: scraping_rate failed (< 20 products)
Fix:
  1. Use DevTools to verify CSS selectors
  2. Check config/supplier_configs/{domain}.json
  3. Verify no login required
```

### Amazon Cache Empty

```
Issue: amazon_cache failed
Fix:
  1. Verify EAN extraction working
  2. Check test product has valid EAN
  3. Ensure Amazon API connectivity
```

### Runner Not Found

```
Issue: No runner found for supplier
Fix:
  Wizard auto-generates shim at run_custom_{supplier-id}.py
  Shim maps workflow_key to base runner:
    - poundwholesale_workflow → run_custom_poundwholesale.py
    - clearance_king_workflow → run_custom_clearance_king.py
    - unknown_workflow → run_custom_poundwholesale.py (default)
```

## Runner Selection Policy

The wizard generates **FULL supplier-specific runner implementations** (117-143 lines):

1. **Check for existing runner**: `run_custom_{supplier-id}.py`
   - If exists → use it (no regeneration)
   - If not → generate full implementation from template

2. **Generate full runner implementation**:
   - Creates complete 117-143 line Python script
   - Includes authentication integration (if auth_required=true)
   - Imports supplier-specific tools from `tools/{supplier-id}/`
   - Follows poundwholesale/clearance_king pattern
   - Uses `utils/runner_template.py.txt` as base template

**HYBRID APPROACH**:
- **Wizard**: Automated template-based generation (fast, deterministic)
- **LLM**: Post-generation validation and enhancement (adaptive, flexible)

**No dependency on**:
- `run_complete_fba_system.py` (removed)
- `workflows.*.runner_script` in system_config.json (not used)
- **NO shims or forwarding scripts** - each supplier gets full implementation

**Example generated runner** (117-143 lines):
```python
#!/usr/bin/env python3
"""Custom runner for angelwholesale-co-uk"""
import asyncio, logging, sys, os
from config.system_config_loader import SystemConfigLoader
from tools.passive_extraction_workflow_latest import PassiveExtractionWorkflow
from tools.angelwholesale.supplier_authentication_service import AngelwholesaleAuthenticationHelper
from utils.browser_manager import BrowserManager

async def main():
    """Main function to run the custom extraction workflow."""
    config_loader = SystemConfigLoader()
    workflow_config = config_loader.get_workflow_config('angelwholesale_workflow')
    supplier_name = workflow_config.get('supplier_name', 'angelwholesale.co.uk')
    credentials = config_loader.get_credentials(supplier_name)

    browser_manager = BrowserManager.get_instance()
    await browser_manager.launch_browser(cdp_port=9222)
    page = await browser_manager.get_page()

    # Authentication (if required)
    auth_helper = AngelwholesaleAuthenticationHelper(page)
    is_authenticated = await auth_helper.is_authenticated()
    if not is_authenticated:
        await auth_helper.login(credentials)

    # Run workflow
    workflow = PassiveExtractionWorkflow(
        config_loader=config_loader,
        workflow_key='angelwholesale_workflow',
        workflow_config=workflow_config,
        browser_manager=browser_manager
    )
    await workflow.run()

if __name__ == "__main__":
    asyncio.run(main())
```

## Session Files

Debug files located at OS-specific temp directory (absolute paths):
- **Windows**: `%TEMP%\onboarding\<session_id>\` (e.g., `C:\Users\...\AppData\Local\Temp\onboarding\...`)
- **WSL**: `/tmp/onboarding/<session_id>/` (or `/mnt/c/Users/.../Temp/onboarding/...`)
- **Linux**: `/tmp/onboarding/<session_id>/`

**Path Resolution**: Uses `tempfile.gettempdir()` for OS-safe absolute paths, ensuring Windows/WSL/Linux compatibility.

Contains:
- `input.json`: All parameters passed to wizard
- `output.json`: Wizard execution results
- `staging/`: Temporary files before atomic move (absolute temp path)

## Development

### Testing

```bash
# Test domain normalization
python -c "from utils.supplier_onboarding_wizard import normalize_domain; \
  print(normalize_domain('https://clearance-king.co.uk/products'))"

# Test runner selection
python -c "from utils.supplier_onboarding_wizard import determine_runner; \
  from pathlib import Path; \
  print(determine_runner('test_workflow', 'test-supplier', Path('.')))"
```

### Adding New Scaffolds

Edit `utils/supplier_onboarding_wizard.py` in `generate_files()` function.

## License

Internal use only - Amazon FBA Agent System
