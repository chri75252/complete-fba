# Naming Conventions

The Amazon FBA Agent System enforces **three distinct naming forms** for supplier identifiers across different contexts. This ensures consistency and prevents confusion between file paths, Python modules, and configuration keys.

---

## The Three Forms

### 1. Dot-Form (Domain)

**Format**: `supplier.co.uk` (with dots and TLD extension)

**Example**: `angelwholesale.co.uk`, `poundwholesale.co.uk`

**Used For**:
- **Selector configuration files**: `config/supplier_configs/angelwholesale.co.uk.json`
- **System config supplier_name**: `"supplier_name": "angelwholesale.co.uk"`
- **Browser authentication URLs**: `https://angelwholesale.co.uk`
- **Linking map directory names** (exception): `OUTPUTS/FBA_ANALYSIS/linking_maps/poundwholesale.co.uk/`

**Why**: Represents actual domain names as they appear in browsers and URLs.

---

### 2. Hyphen-Form (Supplier ID)

**Format**: `supplier-co-uk` (dots and underscores replaced with hyphens)

**Example**: `angelwholesale-co-uk`, `poundwholesale-co-uk`

**Used For**:
- **Runner scripts**: `run_custom_angelwholesale-co-uk.py`
- **Tool directories**: `tools/angelwholesale-co-uk/`
- **Session directories**: `/tmp/onboarding/angelwholesale-co-uk/`
- **Cached product files**: `angelwholesale-co-uk_products_cache.json`

**Why**: Filesystem-safe identifier (no dots that could be confused with file extensions).

**Conversion Rule**:
```
angelwholesale.co.uk → angelwholesale-co-uk
(Replace dots with hyphens)
```

---

### 3. Underscore-Form (Supplier Name)

**Format**: `supplier_co_uk` (dots and hyphens replaced with underscores)

**Example**: `angelwholesale_co_uk`, `poundwholesale_co_uk`

**Used For**:
- **Workflow keys**: `angelwholesale_workflow`, `poundwholesale_workflow`
- **Processing state files**: `angelwholesale_co_uk_processing_state.json`
- **Python module naming**: `import angelwholesale_workflow`
- **Category config files**: `angelwholesale_workflow_categories.json`

**Why**: Python-safe identifier (underscores are the standard for Python module/variable naming).

**Conversion Rule**:
```
angelwholesale.co.uk → angelwholesale_co_uk
(Replace dots with underscores)

Then for workflow keys:
angelwholesale_co_uk → angelwholesale_workflow
(Simplify to just supplier name + _workflow)
```

---

## Quick Reference Table

| Context | Form | Example | Full Path/Usage |
|---------|------|---------|-----------------|
| **Selector Config** | Dot | `angelwholesale.co.uk.json` | `config/supplier_configs/angelwholesale.co.uk.json` |
| **System Config (name)** | Dot | `"angelwholesale.co.uk"` | `config/system_config.json` → `supplier_name` |
| **Runner Script** | Hyphen | `run_custom_angelwholesale-co-uk.py` | Root directory |
| **Tool Directory** | Hyphen | `angelwholesale-co-uk/` | `tools/angelwholesale-co-uk/` |
| **Auth Helper** | Hyphen | `angelwholesale-co-uk/supplier_authentication_service.py` | `tools/angelwholesale-co-uk/` |
| **Workflow Key** | Underscore | `angelwholesale_workflow` | `config/system_config.json` → workflows |
| **Categories Config** | Underscore | `angelwholesale_workflow_categories.json` | `config/` |
| **Processing State** | Underscore | `angelwholesale_co_uk_processing_state.json` | `OUTPUTS/CACHE/processing_states/` |
| **Cached Products** | Hyphen | `angelwholesale-co-uk_products_cache.json` | `OUTPUTS/cached_products/` |
| **Linking Map Dir** | Dot | `poundwholesale.co.uk/` | `OUTPUTS/FBA_ANALYSIS/linking_maps/poundwholesale.co.uk/` |

---

## Validation Checklist

When validating generated files, verify:

### ✅ Correct Usage

- [ ] Config file uses **dot-form**: `angelwholesale.co.uk.json`
- [ ] Runner uses **hyphen-form**: `run_custom_angelwholesale-co-uk.py`
- [ ] Workflow key uses **underscore-form**: `angelwholesale_workflow`
- [ ] Tool directory uses **hyphen-form**: `tools/angelwholesale-co-uk/`
- [ ] State file uses **underscore-form**: `angelwholesale_co_uk_processing_state.json`
- [ ] Categories config uses **underscore-form**: `angelwholesale_workflow_categories.json`

### ❌ Common Mistakes

**Mistake 1**: Dots in filenames (except config)
```
❌ Wrong: run_custom_angelwholesale.co.uk.py
✅ Right: run_custom_angelwholesale-co-uk.py
```

**Mistake 2**: Hyphens in config filenames
```
❌ Wrong: config/supplier_configs/angelwholesale-co-uk.json
✅ Right: config/supplier_configs/angelwholesale.co.uk.json
```

**Mistake 3**: Dots in tool directories
```
❌ Wrong: tools/angelwholesale.co.uk/
✅ Right: tools/angelwholesale-co-uk/
```

**Mistake 4**: Mixed forms in workflow keys
```
❌ Wrong: angelwholesale-co-uk_workflow
❌ Wrong: angelwholesale.co.uk_workflow
✅ Right: angelwholesale_workflow
```

**Mistake 5**: Wrong form in system config
```
❌ Wrong: "supplier_name": "angelwholesale-co-uk"
✅ Right: "supplier_name": "angelwholesale.co.uk"
```

---

## Class Name Conversion (For Authentication Helpers)

Authentication helper class names require special conversion to PascalCase:

**Conversion Rule**:
```
angelwholesale.co.uk → AngelwholesaleCoUkAuthenticationHelper
```

**Steps**:
1. Remove dots: `angelwholesale.co.uk` → `angelwholesale co uk`
2. Split by spaces: `["angelwholesale", "co", "uk"]`
3. Capitalize each word: `["Angelwholesale", "Co", "Uk"]`
4. Join + add suffix: `AngelwholesaleCoUk` + `AuthenticationHelper`

**Examples**:
- `poundwholesale.co.uk` → `PoundwholesaleCoUkAuthenticationHelper`
- `clearance-king.co.uk` → `ClearanceKingCoUkAuthenticationHelper`
- `example.com` → `ExampleComAuthenticationHelper`

---

## Form Selection Logic

**Use this decision tree**:

```
Is it a...

├─ Config file with selectors?
│  └─ Use DOT-FORM: supplier.co.uk.json
│
├─ Python script or executable?
│  └─ Use HYPHEN-FORM: run_custom_supplier-co-uk.py
│
├─ Directory in filesystem?
│  ├─ Is it in tools/?
│  │  └─ Use HYPHEN-FORM: tools/supplier-co-uk/
│  ├─ Is it linking_maps?
│  │  └─ Use DOT-FORM: linking_maps/supplier.co.uk/
│  └─ Is it session dir?
│     └─ Use HYPHEN-FORM: /tmp/onboarding/supplier-co-uk/
│
├─ Workflow key or Python module?
│  └─ Use UNDERSCORE-FORM: supplier_workflow
│
├─ Processing state or cache file?
│  └─ Use UNDERSCORE-FORM: supplier_co_uk_processing_state.json
│
└─ system_config.json supplier_name field?
   └─ Use DOT-FORM: "supplier.co.uk"
```

---

## Examples by Supplier

### angelwholesale.co.uk

| Context | Form | Value |
|---------|------|-------|
| Domain | Dot | `angelwholesale.co.uk` |
| Supplier ID | Hyphen | `angelwholesale-co-uk` |
| Workflow Key | Underscore | `angelwholesale_workflow` |
| Config File | Dot | `config/supplier_configs/angelwholesale.co.uk.json` |
| Runner | Hyphen | `run_custom_angelwholesale-co-uk.py` |
| Tool Dir | Hyphen | `tools/angelwholesale-co-uk/` |
| Auth Class | PascalCase | `AngelwholesaleCoUkAuthenticationHelper` |

### poundwholesale.co.uk

| Context | Form | Value |
|---------|------|-------|
| Domain | Dot | `poundwholesale.co.uk` |
| Supplier ID | Hyphen | `poundwholesale-co-uk` |
| Workflow Key | Underscore | `poundwholesale_workflow` |
| Config File | Dot | `config/supplier_configs/poundwholesale.co.uk.json` |
| Runner | Hyphen | `run_custom_poundwholesale-co-uk.py` |
| Tool Dir | Hyphen | `tools/poundwholesale-co-uk/` |
| Auth Class | PascalCase | `PoundwholesaleCoUkAuthenticationHelper` |

---

## Enforcement During Validation

When validating generated files:

1. **Read each file/directory name**
2. **Determine expected form** based on context (table above)
3. **Verify actual form matches expected**
4. **Report any mismatches** with specific examples

**Validation Template**:
```
Checking: run_custom_angelwholesale-co-uk.py
Expected Form: HYPHEN-FORM (supplier-co-uk)
Actual: angelwholesale-co-uk
Status: ✅ PASS

Checking: config/supplier_configs/angelwholesale-co-uk.json
Expected Form: DOT-FORM (supplier.co.uk)
Actual: angelwholesale-co-uk
Status: ❌ FAIL - Should be angelwholesale.co.uk.json
```

---

## Summary

**Remember**:
- **Dot-form** = Domain/URL contexts
- **Hyphen-form** = Filesystem (scripts, directories)
- **Underscore-form** = Python/config keys

**When in doubt**, refer to existing implementations:
- Check `run_custom_poundwholesale.py` for pattern
- Check `config/supplier_configs/poundwholesale.co.uk.json` for config pattern
- Check `tools/poundwholesale/` (note: older format, use hyphen-form for new suppliers)

---

**End of NAMING_CONVENTIONS.md**
