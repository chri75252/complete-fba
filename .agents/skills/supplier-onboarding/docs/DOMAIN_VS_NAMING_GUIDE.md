# Domain vs Naming Consistency Guide

## 🚨 CRITICAL CONCEPT: Domain ≠ File Naming

**This is the #1 source of configuration errors in supplier onboarding.**

Many suppliers have `.com` websites but use `.co.uk` in their operational file names. This is **INTENTIONAL** and **CORRECT**. The system separates:

1. **Actual Domain** (from supplier URL) - Used for web scraping
2. **Operational Naming** - Uses `.co.uk` suffix for consistency

---

## The Two Domain Concepts

### 1. **Actual Domain** (From Supplier URL)
- **Source**: Extracted from supplier's website URL
- **Usage**: Configuration files, supplier_id, system_config
- **Example**: `wholesaletradingsupplies.com` (from https://wholesaletradingsupplies.com)
- **Must Match**: The actual website domain

### 2. **Operational Naming** (File/Script Names)
- **Source**: Historical convention (`.co.uk` suffix)
- **Usage**: Runner scripts, cache files, linking maps, state files
- **Example**: `wholesaletradingsupplies-co-uk` (in file names)
- **Purpose**: Consistency across all suppliers

---

## 📋 What Changes vs What Stays the Same

### ✅ **MUST Change** (Match Actual Domain)
| Item | Current | Must Match | Example |
|------|---------|------------|---------|
| **Config Filename** | `supplier.co.uk.json` | **Actual domain** | `wholesaletradingsupplies.com.json` |
| **Config supplier_id** | `supplier.co.uk` | **Actual domain** | `wholesaletradingsupplies.com` |
| **System Config supplier_name** | `supplier.co.uk` | **Actual domain** | `wholesaletradingsupplies.com` |
| **Config supplier_url** | `https://supplier.co.uk` | **Actual URL** | `https://wholesaletradingsupplies.com` |

### ✅ **Stays Same** (Uses .co.uk for Consistency)
| Item | Current | Stays As | Example |
|------|---------|----------|---------|
| **Runner Script** | `run_custom_supplier-co-uk.py` | **Hyphen-form** | `run_custom_wholesaletradingsupplies-co-uk.py` |
| **Tool Directory** | `tools/supplier-co-uk/` | **Hyphen-form** | `tools/wholesaletradingsupplies-co-uk/` |
| **Cached Products** | `supplier-co-uk_products_cache.json` | **Hyphen-form** | `wholesaletradingsupplies-co-uk_products_cache.json` |
| **Linking Map Dir** | `supplier.co.uk/` | **Dot-form** | `wholesaletradingsupplies.co.uk/` |
| **State File** | `supplier_co_uk_processing_state.json` | **Underscore-form** | `wholesaletradingsupplies_co_uk_processing_state.json` |
| **Workflow Key** | `supplier_workflow` | **Underscore-form** | `wholesaletradingsupplies_workflow` |

---

## 🧪 Real-World Examples

### Example 1: wholesaletradingsupplies.com (Current Issue)
```
Website: https://wholesaletradingsupplies.com
Actual Domain: wholesaletradingsupplies.com

✅ CORRECT Configuration:
  Config File: wholesaletradingsupplies.com.json
  Config supplier_id: wholesaletradingsupplies.com
  System Config: wholesaletradingsupplies.com
  Config supplier_url: https://wholesaletradingsupplies.com

✅ CORRECT Operational Names (Stay .co.uk):
  Runner: run_custom_wholesaletradingsupplies-co-uk.py
  Cache File: wholesaletradingsupplies-co-uk_products_cache.json
  Linking Map: wholesaletradingsupplies.co.uk/linking_map.json
  State File: wholesaletradingsupplies_co_uk_processing_state.json
```

### Example 2: kdwholesale.co.uk (Already Correct)
```
Website: https://kdwholesale.co.uk
Actual Domain: kdwholesale.co.uk

✅ CORRECT Configuration:
  Config File: kdwholesale.co.uk.json
  Config supplier_id: kdwholesale.co.uk
  System Config: kdwholesale.co.uk
  Config supplier_url: https://kdwholesale.co.uk

✅ CORRECT Operational Names (Stay .co.uk):
  Runner: run_custom_kdwholesale-co-uk.py
  Cache File: kdwholesale-co-uk_products_cache.json
  Linking Map: kdwholesale.co.uk/linking_map.json
  State File: kdwholesale_co_uk_processing_state.json
```

---

## 🔍 Validation Decision Tree

When validating files, use this logic:

```
Is this a configuration file that affects web scraping?
├─ YES (config file, supplier_id, supplier_name, supplier_url)
│  └─ MUST match actual domain from supplier URL
│
├─ NO (operational files - runners, caches, states)
│  └─ Use historical .co.uk naming convention
│    ├─ Runner scripts: hyphen-form (supplier-co-uk)
│    ├─ Cache/state files: underscore-form (supplier_co_uk)
│    └─ Linking maps: dot-form (supplier.co.uk)
```

---

## 🚨 Common Confusion Scenarios

### Scenario 1: "I see .co.uk in file names but website is .com - is this wrong?"
**Answer**: NO, this is **CORRECT**. The operational files use `.co.uk` for consistency across all suppliers, regardless of actual website domain.

### Scenario 2: "Should I change all .co.uk to .com in file names?"
**Answer**: NO, only change the **configuration domain** fields. Keep operational file names as `.co.uk`.

### Scenario 3: "The runner expects .co.uk config but website is .com - what should I do?"
**Answer**: Update the **config file name** to match the actual domain (.com), but keep the **runner name** as .co.uk.

---

## 🎯 Critical Thinking Protocol

When onboarding a supplier:

1. **Extract actual domain** from supplier URL
2. **Create two lists**:
   - **Config items** (MUST match actual domain)
   - **Operational items** (MUST use .co.uk convention)
3. **Validate each file** against its respective list
4. **Report mismatches** with specific fix instructions

### Example Validation Report
```
Validating wholesaletradingsupplies.com onboarding:

✅ Config Domain Consistency:
  Config file: wholesaletradingsupplies.com.json ✓ matches URL
  Config supplier_id: wholesaletradingsupplies.com ✓ matches URL
  System Config: wholesaletradingsupplies.com ✓ matches URL

✅ Operational Naming Consistency:
  Runner: run_custom_wholesaletradingsupplies-co-uk.py ✓ uses hyphen-form
  Cache: wholesaletradingsupplies-co-uk_products_cache.json ✓ uses hyphen-form
  Linking Map: wholesaletradingsupplies.co.uk/ ✓ uses dot-form
  State: wholesaletradingsupplies_co_uk_processing_state.json ✓ uses underscore-form

Status: ✅ ALL CHECKS PASS - Ready for execution
```

---

## 🛠️ Fix Templates

### Template: Domain Mismatch Error
```
❌ CRITICAL: Domain mismatch detected
   Supplier URL: https://wholesaletradingsupplies.com
   Expected domain: wholesaletradingsupplies.com
   Found in config file: wholesaletradingsupplies.co.uk

🔧 SURGICAL FIX:
1. Update config/supplier_configs/wholesaletradingsupplies.com.json:
   - Change "supplier_id": "wholesaletradingsupplies.co.uk"
   - To: "supplier_id": "wholesaletradingsupplies.com"

2. Update config/system_config.json:
   - Change "supplier_name": "wholesaletradingsupplies.co.uk"
   - To: "supplier_name": "wholesaletradingsupplies.com"

⚠️ DO NOT change: runner name, cache files, or linking map names
   Keep as: wholesaletradingsupplies-co-uk (operational consistency)
```

### Template: Operational Naming Error
```
❌ INCORRECT: Operational file using wrong form
   File: run_custom_wholesaletradingsupplies.com.py
   Expected: run_custom_wholesaletradingsupplies-co-uk.py

🔧 FIX: Rename to use hyphen-form (not dot-form)
   Correct: run_custom_wholesaletradingsupplies-co-uk.py
```

---

## 📚 Quick Reference

### Domain vs Naming Summary
| Context | Must Match Actual Domain? | Uses .co.uk Convention? | Example |
|--------|---------------------------|------------------------|---------|
| Config filename | ✅ YES | ❌ NO | `supplier.com.json` |
| Config supplier_id | ✅ YES | ❌ NO | `supplier.com` |
| System Config name | ✅ YES | ❌ NO | `supplier.com` |
| Config supplier_url | ✅ YES | ❌ NO | `https://supplier.com` |
| Runner script | ❌ NO | ✅ YES | `supplier-co-uk.py` |
| Tool directory | ❌ NO | ✅ YES | `supplier-co-uk/` |
| Cache files | ❌ NO | ✅ YES | `supplier-co-uk_products_cache.json` |
| Linking maps | ❌ NO | ✅ YES | `supplier.co.uk/` |
| State files | ❌ NO | ✅ YES | `supplier_co_uk_processing_state.json` |

### Validation Commands
```bash
# Extract domain from config file
grep '