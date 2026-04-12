# Sandbox Workflows

## Overview

Sandbox workflows run isolated from production processing, using separate output directories. They enable testing, experimentation, and product list refresh without affecting main processing state.

---

## Sandbox vs Main Workflows

| Aspect | Main Workflow | Sandbox Workflow |
|--------|--------------|------------------|
| **Purpose** | Production runs | Testing, experiments |
| **Output Dir** | `OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier}/` | `OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier}__sandbox__{run_id}/` |
| **Processing State** | Single persistent state | Isolated per-run state |
| **Supplier Cache** | Single persistent cache | Sandbox-specific cache |
| **Resumable** | Yes, across sessions | Run-specific |
| **Use Cases** | Full extraction | Testing, product refresh |

---

## Sandbox Directory Naming

### Pattern
```
{supplier}.{tld}__sandbox__{run_id}
```

### Components

| Component | Format | Example |
|-----------|--------|---------|
| Supplier | Dot-form | `poundwholesale.co.uk` |
| Separator | `__sandbox__` | Literal |
| Run ID | UUID or identifier | `44b12007`, `cea25747`, `aebdad60` |

### Examples

```
poundwholesale.co.uk__sandbox__44b12007
efghousewares.co.uk__sandbox__cea25747
angelwholesale.co.uk__sandbox__008fb410
clearance-king.co.uk__sandbox__ad76adf1
```

---

## Directory Structure

### Main Workflow

```
OUTPUTS/FBA_ANALYSIS/linking_maps/
└── poundwholesale.co.uk/
    └── linking_map.json
```

### Sandbox Workflow

```
OUTPUTS/FBA_ANALYSIS/linking_maps/
├── poundwholesale.co.uk/                    # Main
│   └── linking_map.json
└── poundwholesale.co.uk__sandbox__44b12007/  # Sandbox
    ├── linking_map.json
    └── amazon_cache/
        └── amazon_{ASIN}_{EAN}.json
```

---

## File Contents

### Sandbox linking_map.json

Identical structure to main linking map:

```json
[
  {
    "supplier_ean": "5060071385975",
    "amazon_asin": "B0FM84PBBM",
    "supplier_title": "Adhesive House And Gate Number Black With Gold Number 7",
    "amazon_title": "Contemporary Matte Black House Number 7...",
    "supplier_price": 0.33,
    "amazon_price": 3.99,
    "match_method": "EAN",
    "confidence": 1,
    "created_at": "2026-03-12T23:56:41Z",
    "supplier_url": "https://www.poundwholesale.co.uk/..."
  }
]
```

---

## Identifying Sandbox Runs

### Run ID Sources

| Source | Pattern | Example |
|--------|---------|---------|
| UUID v4 | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` | `44b12007-8abc-4def-9876-543210abcdef` |
| Short ID | 8 hex chars | `44b12007` |
| Custom name | `sandbox__name` | `sandbox__test_par` |

### Naming Patterns

**Category Sandbox (Full extraction):**
```
poundwholesale.co.uk__sandbox__44b12007
```
- Contains full category URL set
- Can match all products

**Product List Sandbox (Refresh):**
```
poundwholesale.co.uk__sandbox__008fb410
```
- Contains specific product URLs
- Used for targeted refresh

**Named Sandbox:**
```
angelwholesale.co.uk__sandbox__angelwho
angelwholesale.co.uk__sandbox__run_ange
```
- Custom named runs
- Often for specific testing purposes

---

## Sandbox Output Files

Each sandbox directory may contain:

| File/Directory | Description |
|----------------|-------------|
| `linking_map.json` | EAN → ASIN mappings |
| `amazon_cache/` | Amazon product data |
| `processing_state.json` | Run-specific state |
| `cached_products.json` | Sandbox supplier cache |

---

## Product List Refresh

The product list refresh workflow uses sandbox isolation:

```python
async def refresh_product_list(product_urls: list[str], supplier: str, run_id: str):
    # Create sandbox directory
    sandbox_dir = f"OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier}__sandbox__{run_id}"
    
    # Process in isolation
    await process_products(product_urls, sandbox_dir)
    
    # Return results from sandbox
    return load_results(sandbox_dir)
```

### Key Characteristics
- **Specific URLs** - Only listed products processed
- **Isolated state** - Doesn't affect main linking map
- **Quick iteration** - Fast test cycles
- **Results merge** - Can merge back to main if desired

---

## Common Use Cases

### 1. Testing New Selectors
```
supplier.com__sandbox__test_selectors
```
- Test new CSS selectors
- Validate extraction accuracy
- No impact on production

### 2. Category Experiments
```
supplier.com__sandbox__experiment_catA
```
- Try different category sets
- Compare results
- Isolated analysis

### 3. Product Refresh
```
supplier.com__sandbox__refresh_20260411
```
- Update specific products
- Fresh Amazon data
- Merge or discard results

### 4. Resumable Testing
```
supplier.com__sandbox__long_test
```
- Long-running test extraction
- Interruptible
- State persists in sandbox

---

## Listing All Sandboxes

```python
from pathlib import Path

linking_maps = Path("OUTPUTS/FBA_ANALYSIS/linking_maps")

sandboxes = []
for d in linking_maps.iterdir():
    if "__sandbox__" in d.name:
        sandboxes.append(d.name)

print(f"Found {len(sandboxes)} sandbox directories")
for s in sorted(sandboxes):
    print(f"  - {s}")
```

---

## Cleanup

### Remove Old Sandboxes
```python
from pathlib import Path
from datetime import datetime, timedelta

base = Path("OUTPUTS/FBA_ANALYSIS/linking_maps")
threshold = datetime.now() - timedelta(days=30)

for d in base.iterdir():
    if "__sandbox__" in d.name:
        mtime = datetime.fromtimestamp(d.stat().st_mtime)
        if mtime < threshold:
            print(f"Removing {d.name}...")
            # import shutil; shutil.rmtree(d)
```

### Archive Instead of Delete
```python
from pathlib import Path
from datetime import datetime

def archive_sandbox(sandbox_path: Path):
    archive_name = f"archived_{sandbox_path.name}_{datetime.now().strftime('%Y%m%d')}"
    archive_dir = sandbox_path.parent / "archived"
    archive_dir.mkdir(exist_ok=True)
    sandbox_path.rename(archive_dir / archive_name)
```

---

## Related Files

| File | Location | Purpose |
|------|----------|---------|
| Main Linking Map | `OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier}/linking_map.json` | Production mappings |
| Product List Refresh | `control_plane/run_product_list_refresh.py` | Refresh workflow |
| State Manager | `utils/fixed_enhanced_state_manager.py` | State isolation |

---

## Workflows That Use Sandboxes

| Workflow | Sandboxing Method |
|----------|------------------|
| Product List Refresh | Always sandboxed |
| Category Testing | Optional sandboxing |
| Full Extraction | Main (non-sandboxed) |
| AI-Generated Categories | Often sandboxed |

---

*Document Version: 1.0*
*Last Updated: 2026-04-11*
