# Selector Validation Implementation Guide for Supplier Onboarding Skill
**Date**: 2025-11-14  
**Purpose**: Add BeautifulSoup vs Playwright selector compatibility validation to skill workflow  
**Target**: LLM detects incompatible selectors BEFORE running wizard script

---

## 📋 SUMMARY

**What**: Add validation to detect jQuery/Playwright pseudo-selectors that don't work with BeautifulSoup  
**Where**: `.claude/skills/supplier-onboarding/SKILL.md` - Section 0.3 (Validate Selectors Content)  
**When**: During Step 0 preprocessing, BEFORE invoking wizard script  
**Why**: Prevent angelwholesale-type issues where selectors use `:has()`, `:contains()`, etc. that BeautifulSoup cannot parse

---

## 🎯 ROOT CAUSE REMINDER

**The Problem**:
- **Supplier scraping** uses BeautifulSoup (Python) - supports ONLY standard CSS
- **Amazon scraping** uses Playwright - supports extended CSS + jQuery-like pseudo-selectors
- Users often provide selectors in jQuery/Cheerio syntax (`:has()`, `:contains()`) which work in Playwright but FAIL in BeautifulSoup

**What Happened with AngelWholesale**:
```json
"ean": [
  ".specs-row:has(.specs-data:contains('Barcode')) .specs-data:nth-child(2)"
]
```
- `:has()` = jQuery pseudo-selector ❌ BeautifulSoup cannot parse
- `:contains()` = jQuery pseudo-selector ❌ BeautifulSoup cannot parse
- Selector failed → fell back to pattern matching → extracted wrong EAN from category ID → all products marked as duplicates

---

## 📍 EXACT LOCATION FOR CHANGES

**File**: `.claude/skills/supplier-onboarding/SKILL.md`

**Section**: `### 0.3. Validate Selectors Content (LLM Manual Inspection)`

**Current Lines**: 101-146

**Current Content** (PROBLEMATIC):
```markdown
### 0.3. Validate Selectors Content (LLM Manual Inspection)

**CSS Syntax Validation** (check manually):
```css
✅ Valid: .product-card h3 a
✅ Valid: span.price
✅ Valid: button:contains('Next Page')  ← ❌ WRONG! This is invalid for BeautifulSoup
✅ Valid: [data-product-id]

❌ Invalid: .product[data-id  (missing closing bracket)
❌ Invalid: span(price  (unbalanced parentheses)
❌ Invalid: :contains('Next'  (missing closing parentheses)
```
```

**Problem**: Currently marks `:contains()` as "Valid" but it's NOT valid for BeautifulSoup!

---

## 🔧 REQUIRED CHANGES

### Change 1: Update Section 0.3 - Add Library Compatibility Check

**Location**: `.claude/skills/supplier-onboarding/SKILL.md` lines 129-146

**Replace**:
```markdown
**CSS Syntax Validation** (check manually):
```css
✅ Valid: .product-card h3 a
✅ Valid: span.price
✅ Valid: button:contains('Next Page')
✅ Valid: [data-product-id]

❌ Invalid: .product[data-id  (missing closing bracket)
❌ Invalid: span(price  (unbalanced parentheses)
❌ Invalid: :contains('Next'  (missing closing parentheses)
```

**Checklist**:
- [ ] Extracted all selectors from source file
- [ ] Verified required keys present
- [ ] Checked CSS syntax (balanced brackets/parentheses)
- [ ] No empty values
```

**With**:
```markdown
**CSS Syntax Validation** (check manually):

#### A. Basic Syntax Check
```css
✅ Valid: .product-card h3 a
✅ Valid: span.price
✅ Valid: [data-product-id]
✅ Valid: element > child
✅ Valid: :nth-child(2)
✅ Valid: :first-child
✅ Valid: :last-child

❌ Invalid: .product[data-id  (missing closing bracket)
❌ Invalid: span(price  (unbalanced parentheses)
```

#### B. **🚨 CRITICAL: BeautifulSoup Compatibility Check**

**Library Context**: Supplier scraping uses **BeautifulSoup (Python)**, which supports ONLY standard CSS selectors.

**Scan ALL selectors for these INCOMPATIBLE pseudo-selectors**:

❌ **jQuery/Cheerio Pseudo-Selectors** (DO NOT WORK in BeautifulSoup):
```css
:has(...)         ← jQuery only
:contains('...')  ← jQuery only  
:has-text('...')  ← Playwright only
:text('...')      ← Playwright only
:text-matches()   ← Playwright only
```

**Example Validation**:
```
Selector 1: ".product-card h3 a"
  ✅ PASS: Standard CSS only

Selector 2: ".specs-row:has(.specs-data:contains('Barcode')) .specs-data:nth-child(2)"
  ❌ FAIL: Contains :has() and :contains() pseudo-selectors
  ⚠️ LIBRARY INCOMPATIBILITY: These work in Playwright but NOT in BeautifulSoup
  
Selector 3: "button:contains('Next Page')"
  ❌ FAIL: Contains :contains() pseudo-selector
  ⚠️ LIBRARY INCOMPATIBILITY: Works in jQuery but NOT in BeautifulSoup

Selector 4: "span.price.price--withoutTax"
  ✅ PASS: Standard CSS only
```

**If incompatible selectors found, INFORM USER**:
```
⚠️ SELECTOR COMPATIBILITY ISSUES DETECTED
════════════════════════════════════════════════════════════════

🚨 CRITICAL: The following selectors use jQuery/Playwright pseudo-selectors
that are NOT supported by BeautifulSoup (supplier scraping library):

❌ FIELD: ean
   SELECTOR: ".specs-row:has(.specs-data:contains('Barcode')) .specs-data:nth-child(2)"
   ISSUES:
     - :has() - jQuery pseudo-selector
     - :contains() - jQuery pseudo-selector
   
   ✅ ALTERNATIVE APPROACHES:
     a) Use simpler selector + manual iteration in code:
        ".specs-row" (then iterate to find 'Barcode' label in Python)
     
     b) Use standard CSS only:
        ".specs-data" (get all, filter by text in Python)

❌ FIELD: next_page_button
   SELECTOR: "button:contains('Next Page')"
   ISSUES:
     - :contains() - jQuery pseudo-selector
   
   ✅ ALTERNATIVE APPROACHES:
     a) Use class or attribute selector:
        "button.btn-load-more"
     
     b) Use data attribute:
        "button[data-action='load-more']"

════════════════════════════════════════════════════════════════

📚 REFERENCE: Why This Matters

  - Supplier scraping uses: BeautifulSoup (Python library)
  - BeautifulSoup supports: Standard CSS selectors ONLY
  - NOT supported: jQuery pseudo-selectors (:has, :contains, etc.)
  
  - Amazon scraping uses: Playwright (supports extended selectors)
  - This is why Amazon config can use :has-text(), :text-matches()
  
  - If you provide jQuery selectors for suppliers:
    ✅ They WILL work in browser (jQuery available)
    ❌ They will FAIL in BeautifulSoup
    ⚠️ System falls back to pattern matching
    🚨 Pattern matching may extract WRONG values
    💥 Result: Deduplication issues, missing data

════════════════════════════════════════════════════════════════

🔧 ACTION REQUIRED:

Please provide alternative selectors using ONLY standard CSS:
  ✅ Allowed: .class, #id, [attr], :nth-child(), :first-child, :last-child, element > child
  ❌ NOT allowed: :has(), :contains(), :text(), :text-matches(), :has-text()

Would you like me to help convert these selectors to BeautifulSoup-compatible alternatives?
```

**Checklist** (UPDATED):
- [ ] Extracted all selectors from source file
- [ ] Verified required keys present
- [ ] Checked basic CSS syntax (balanced brackets/parentheses)
- [ ] **🚨 NEW: Scanned for jQuery/Playwright pseudo-selectors**
- [ ] **🚨 NEW: If found incompatible selectors, informed user with alternatives**
- [ ] **🚨 NEW: Confirmed all selectors are BeautifulSoup-compatible**
- [ ] No empty values
```

---

### Change 2: Add Validation Patterns Reference

**Location**: `.claude/skills/supplier-onboarding/SKILL.md` - Add new section after 0.3

**Insert After Line 146**:

```markdown
---

### 0.3.1. Selector Compatibility Validation Patterns (Reference)

**For LLM use during Step 0.3 validation**:

#### Incompatible Patterns to Detect:

**Regex Patterns**:
```
:has\(        ← Detects :has(...) pseudo-selector
:contains\(   ← Detects :contains(...) pseudo-selector
:has-text\(   ← Detects :has-text(...) Playwright selector
:text\(       ← Detects :text(...) Playwright selector
:text-matches ← Detects :text-matches() Playwright selector
```

**Detection Algorithm** (for LLM to apply):
```
For each selector value in selectors JSON:
  1. Check if contains ":has(" substring
     → IF YES: Mark as incompatible, suggest alternative
  
  2. Check if contains ":contains(" substring
     → IF YES: Mark as incompatible, suggest alternative
  
  3. Check if contains ":has-text(" substring
     → IF YES: Mark as incompatible, suggest alternative
  
  4. Check if contains ":text(" or ":text-matches" substring
     → IF YES: Mark as incompatible, suggest alternative
  
  5. If ANY incompatible patterns found:
     → Display warning message from section 0.3
     → Ask user for BeautifulSoup-compatible alternatives
     → DO NOT proceed to Step 0.4 until resolved
```

#### Common Conversion Patterns:

| jQuery/Cheerio Selector | BeautifulSoup Alternative |
|------------------------|---------------------------|
| `.row:has(.cell:contains('Price'))` | `.row` (iterate in code, check text) |
| `button:contains('Next')` | `button.btn-next` or `button[aria-label='Next']` |
| `span:has-text('Stock')` | `span.stock-label` or `span[data-field='stock']` |
| `.specs:has(.label)` | `.specs` (check children in code) |

#### Manual Iteration Pattern (for reference):

**When user needs to iterate manually** (e.g., for EAN in specs table):

**Original** (jQuery - doesn't work):
```json
"ean": [".specs-row:has(.specs-data:contains('Barcode')) .specs-data:nth-child(2)"]
```

**BeautifulSoup Compatible**:
```json
"_comment_ean": "MANUAL_ITERATION_REQUIRED: Use .specs-row selector, iterate to find 'Barcode' label",
"ean": [".specs-row"]
```

**Code Implementation** (in `configurable_supplier_scraper.py`):
```python
# Manual iteration for .specs-row
specs_rows = soup.select('.specs-row')
for row in specs_rows:
    cells = row.select('.specs-data')
    if len(cells) >= 2:
        label = cells[0].get_text(strip=True).lower()
        if 'barcode' in label or 'ean' in label:
            return cells[1].get_text(strip=True)
```

This approach has been implemented for angelwholesale.co.uk as reference.

---
```

---

### Change 3: Add to Success Criteria

**Location**: `.claude/skills/supplier-onboarding/SKILL.md` lines 1208-1224

**Add to checklist**:
```markdown
✅ All files generated in correct locations
✅ Runner is 117-143 lines (full implementation, NOT 26-line shim)
✅ Workflow_key correct throughout all files
✅ All three naming forms used correctly (dot, hyphen, underscore)
✅ All configuration files valid and complete
✅ System config updated with new workflow
✅ Sanity check passes all 6 criteria
✅ [If auth] Auth helper generated as template with TODO comments
✅ Pre-run verification passes all checks
✅ Content accuracy verified (no wrong supplier URLs)
✅ System readiness confirmed
✅ **🚨 NEW: All selectors validated for BeautifulSoup compatibility** ← ADD THIS
✅ **🚨 NEW: No jQuery/Playwright pseudo-selectors in supplier configs** ← ADD THIS
```

---

## 📝 IMPLEMENTATION CHECKLIST

**To implement this validation in the skill**:

- [ ] **Step 1**: Update `.claude/skills/supplier-onboarding/SKILL.md` section 0.3
  - Replace lines 129-146 with new validation content
  - Add BeautifulSoup compatibility check section
  - Add user warning template

- [ ] **Step 2**: Add new section 0.3.1 after line 146
  - Include regex patterns for detection
  - Include conversion patterns reference
  - Include manual iteration pattern example

- [ ] **Step 3**: Update success criteria (lines 1208-1224)
  - Add selector compatibility checkboxes

- [ ] **Step 4**: Test with angelwholesale scenario
  - Provide selectors with `:has()` and `:contains()`
  - Verify LLM detects incompatibility
  - Verify LLM displays warning with alternatives
  - Verify LLM asks for BeautifulSoup-compatible selectors

---

## 🎯 EXPECTED BEHAVIOR AFTER IMPLEMENTATION

### Scenario 1: User Provides jQuery Selectors

**User Input** (setup/angelwholesale_selectors.txt):
```markdown
### EAN
```css
.specs-row:has(.specs-data:contains('Barcode')) .specs-data:nth-child(2)
```
```

**LLM Behavior** (Step 0.3):
```
🔍 Validating Selectors Content...

✅ Basic Syntax: Valid (balanced brackets/parentheses)

🚨 BeautifulSoup Compatibility Check:

❌ FIELD: ean
   SELECTOR: ".specs-row:has(.specs-data:contains('Barcode')) .specs-data:nth-child(2)"
   ISSUES:
     - :has() - jQuery pseudo-selector
     - :contains() - jQuery pseudo-selector
   
   ⚠️ LIBRARY INCOMPATIBILITY: These work in Playwright/jQuery but NOT in BeautifulSoup

════════════════════════════════════════════════════════════════

🔧 ACTION REQUIRED:

The supplier scraping system uses BeautifulSoup which does NOT support jQuery pseudo-selectors.

Please provide alternative selector using ONLY standard CSS, or indicate if manual iteration is acceptable:

Option A: Use simpler selector + manual iteration
  "ean": [".specs-row"]
  (System will iterate rows to find 'Barcode' label)

Option B: Provide different selector
  Example: ".product-specs .barcode-value"

Which approach would you prefer?
```

**Result**: User provides BeautifulSoup-compatible alternative BEFORE wizard runs, preventing the angelwholesale issue.

---

### Scenario 2: User Provides Standard CSS

**User Input**:
```markdown
### Price
```css
span.price.price--withoutTax
```
```

**LLM Behavior** (Step 0.3):
```
✅ Basic Syntax: Valid
✅ BeautifulSoup Compatibility: PASS (standard CSS only)

Proceeding to Step 0.4...
```

**Result**: No issues, workflow continues normally.

---

## 🔬 VALIDATION ALGORITHM (Detailed)

**For LLM to implement during Step 0.3**:

```python
def validate_selector_compatibility(selector: str, field_name: str) -> dict:
    """
    Check if selector contains BeautifulSoup-incompatible pseudo-selectors.
    Returns: {
        "is_compatible": bool,
        "issues": list of detected issues,
        "suggestions": list of alternatives
    }
    """
    issues = []
    suggestions = []
    
    # Check for jQuery pseudo-selectors
    if ":has(" in selector:
        issues.append(":has() - jQuery pseudo-selector")
        suggestions.append("Use simpler selector + manual iteration in code")
    
    if ":contains(" in selector:
        issues.append(":contains() - jQuery pseudo-selector")
        suggestions.append("Use class/attribute selector or check text in code")
    
    # Check for Playwright pseudo-selectors
    if ":has-text(" in selector:
        issues.append(":has-text() - Playwright pseudo-selector")
        suggestions.append("Use standard CSS selector")
    
    if ":text(" in selector:
        issues.append(":text() - Playwright pseudo-selector")
        suggestions.append("Use standard CSS selector")
    
    if ":text-matches" in selector:
        issues.append(":text-matches() - Playwright pseudo-selector")
        suggestions.append("Use standard CSS selector + regex in code")
    
    is_compatible = len(issues) == 0
    
    return {
        "is_compatible": is_compatible,
        "issues": issues,
        "suggestions": suggestions,
        "field_name": field_name,
        "selector": selector
    }

# Usage during Step 0.3:
for field_name, selector_value in selectors.items():
    result = validate_selector_compatibility(selector_value, field_name)
    
    if not result["is_compatible"]:
        # Display warning to user
        # Ask for BeautifulSoup-compatible alternative
        # DO NOT proceed to Step 0.4
```

---

## 📚 REFERENCE: Library Comparison

| Feature | BeautifulSoup (Supplier) | Playwright (Amazon) |
|---------|--------------------------|---------------------|
| **Library** | bs4 (Python) | playwright.async_api (Python/Node.js) |
| **Parser** | html.parser / lxml | Chrome/Chromium browser engine |
| **Standard CSS** | ✅ Yes | ✅ Yes |
| **`:has()`** | ❌ No | ✅ Yes |
| **`:contains()`** | ❌ No | ❌ No (has `:has-text()` instead) |
| **`:has-text()`** | ❌ No | ✅ Yes |
| **`:text()`** | ❌ No | ✅ Yes |
| **`:text-matches()`** | ❌ No | ✅ Yes |
| **`:nth-child()`** | ✅ Yes | ✅ Yes |
| **`.class`** | ✅ Yes | ✅ Yes |
| **`[attr]`** | ✅ Yes | ✅ Yes |

**Key Takeaway**: If selector works in Playwright, it might NOT work in BeautifulSoup. Always validate for BeautifulSoup compatibility when onboarding suppliers.

---

## ✅ TESTING PLAN

**Test Case 1**: Incompatible Selectors Detection
- Provide selectors with `:has()`, `:contains()`
- Verify LLM detects issues during Step 0.3
- Verify LLM displays detailed warning
- Verify LLM does NOT proceed to Step 0.4

**Test Case 2**: Compatible Selectors Pass-Through
- Provide standard CSS selectors only
- Verify LLM validates successfully
- Verify workflow continues to Step 0.4

**Test Case 3**: Mixed Selectors
- Provide mix of compatible and incompatible
- Verify LLM identifies ONLY the incompatible ones
- Verify user receives specific feedback per selector

**Test Case 4**: Manual Iteration Pattern
- Provide `.specs-row` with manual iteration comment
- Verify LLM accepts as valid pattern
- Verify LLM documents manual iteration requirement

---

## 🎓 SKILL LEARNING OBJECTIVES

After implementing this validation:

1. **LLM learns** to distinguish BeautifulSoup vs Playwright selector compatibility
2. **LLM prevents** jQuery selector bugs before they cause runtime issues
3. **LLM educates** users on library-specific selector limitations
4. **LLM provides** actionable alternatives when incompatible selectors detected

**Result**: Zero selector compatibility issues during supplier onboarding, preventing angelwholesale-type deduplication bugs.

---

**END OF IMPLEMENTATION GUIDE**
