# Supplier Onboarding Skill - Setup and Usage Guide

Complete guide for using the supplier-onboarding skill following Anthropic best practices.

---

## 📦 What Was Created

The supplier-onboarding skill has been restructured following official Claude Code skill patterns:

```
.claude/skills/supplier-onboarding/
├── SKILL.md                          # ⭐ Main skill file (YAML + Markdown)
│                                     # - Complete workflow instructions
│                                     # - Progressive information gathering
│                                     # - Wizard invocation
│                                     # - Comprehensive file validation
│                                     # - Result reporting
│
├── docs/                             # Supporting documentation
│   ├── NAMING_CONVENTIONS.md        # Three naming forms (dot/hyphen/underscore)
│   ├── FILE_SPECIFICATIONS.md       # Expected file formats and structures
│   └── TROUBLESHOOTING.md           # Common issues and solutions
│
├── sample_data/                      # Reference implementations
│   ├── reference_runners/
│   │   ├── run_custom_poundwholesale.py       # 143-line runner (with auth)
│   │   └── run_custom_clearance_king.py       # 117-line runner (no auth)
│   └── reference_auth/
│       └── poundwholesale_auth.py  # Complete auth helper example
│
└── templates/                        # Templates used by wizard
    ├── runner_template.py.txt       # Base runner template
    └── auth_helper_template.py.txt  # Base auth helper template
```

---

## 🎯 Key Improvements

### Before (Old Structure)
```
skills/supplier-onboarding/          # ❌ Wrong location (root, not .claude/)
├── skill.yaml                       # ❌ Wrong format (should be SKILL.md)
├── main.py                          # ❌ Executable orchestrator (not instructions)
└── README.md                        # Documentation
```

**Problems**:
- Not recognized by Claude Code's skill system
- Contains executable code instead of instructions
- Hidden logic in Python subprocess calls
- No validation instructions for LLM

### After (New Structure)
```
.claude/skills/supplier-onboarding/  # ✅ Correct location
├── SKILL.md                         # ✅ Correct format (YAML frontmatter + MD)
├── docs/                            # ✅ Supporting documentation
├── sample_data/                     # ✅ Reference implementations
└── templates/                       # ✅ Templates for wizard
```

**Benefits**:
- ✅ Proper Claude Code integration
- ✅ All logic visible to Claude
- ✅ Transparent workflow execution
- ✅ Comprehensive validation instructions
- ✅ Reference implementations for comparison
- ✅ Following Anthropic best practices

---

## 🚀 How to Use

### Method 1: Front-Loaded Interaction (Standard)

Simply mention the skill in your message. The skill is designed to stop and ask for all necessary information **UPFRONT** before doing any work.

```
You: "Use supplier-onboarding skill to add angelwholesale.co.uk"
```

Claude will follow this **Strict Protocol**:
1.  **Analyze Request**: Read SKILL.md and identify what you provided.
2.  **Initial Handshake**: Immediately ask for the 5 critical data points (Auth, Categories, Test Product, Selectors, Pagination).
3.  **Manual Validation**: Read and verify your provided files (categories/selectors) *before* running any scripts.
4.  **File Generation**: Invoke the wizard only after data is validated.
5.  **Strict Verification**: Manually check every generated file.

**The Initial Handshake covers**:
1.  **Authentication**: Login URL, Username, Password (if needed)
2.  **Category List**: List of URLs or file path
3.  **Test Product URL**: ONE valid product URL for verification
4.  **Selectors**: CSS selectors (if you have them)
5.  **Pagination**: How the site handles multiple pages

### Method 2: Provide All Information Upfront (Power User)

To skip the handshake, provide EVERYTHING in your first message. This allows Claude to proceed directly to validation and generation.

**Template**:
```
You: "Use supplier-onboarding skill to add [supplier_domain]

Categories: [list of URLs or file path]
Test Product: [one valid product URL]
Selectors:
- Product Item: [selector]
- Title: [selector]
- Price: [selector]
- URL: [selector]
Pagination: [details]
Authentication: [Yes/No]"
```

**Example**:
```
You: "Use supplier-onboarding skill to add angelwholesale.co.uk

Categories: setup/categories_angel.txt
Test Product: https://angelwholesale.co.uk/example-product
Selectors:
- Product Item: .product-item
- Title: .product-title
- Price: .price
- URL: .product-link
Pagination: ?page=N
Authentication: No"
```

### Method 3: Inline Information (Quick Start)

For simple sites, you can paste everything directly in the chat:

```
You: "Use supplier-onboarding skill to add example.co.uk
Categories: https://example.co.uk/cat1, https://example.co.uk/cat2
Authentication: No
Selectors:
- Product card: .product-item
- Title: h3.product-title
- Price: .price"
```

---

## 🤖 What Claude Will Do (Internal Workflow)

Claude follows a strict 5-phase process to ensure quality:

### Phase 1: Analysis & Handshake
1.  **Read SKILL.md**: Loads the core logic.
2.  **Analyze Request**: Checks if you provided Auth, Categories, Selectors, etc.
3.  **Ask Missing Info**: If anything is missing, it asks specific questions (The "Handshake").

### Phase 2: Manual Validation (The "Human" Check)
1.  **Read Files**: Reads your category/selector files line-by-line.
2.  **Verify Content**: Checks for valid URLs, correct domains, and standard CSS.
3.  **Create JSON**: Manually writes `setup/{supplier}_categories.json` and `setup/{supplier}_selectors.json`.

### Phase 3: Configuration & Generation
1.  **Create Wizard Input**: Prepares the JSON payload for the automation script.
2.  **Invoke Wizard**: Runs `utils/supplier_onboarding_wizard.py`.
3.  **Generate Files**: The script creates the Runner, Configs, and Auth Helper.

### Phase 4: Strict Verification (Critical)
1.  **Read Generated Files**: Claude reads the actual code generated.
2.  **Verify Logic**: Checks imports, line counts, and workflow keys.
3.  **Fix Issues**: If the script made a mistake (e.g., wrong path), Claude fixes it MANUALLY.

### Phase 5: Reporting
1.  **Summary**: Presents a detailed table of what was built.
2.  **Next Steps**: Guides you to the Pre-Run Verification.

---

## 📋 What Information You Need

Before invoking the skill, gather:

### 1. Supplier Domain ✅
- Example: `angelwholesale.co.uk`
- Can be any form: URL, dot-form, hyphen-form

### 2. Category URLs 📂
- List of product category pages to scrape
- Can provide as:
  - File path: `setup/categories.txt`
  - Inline list: Paste URLs directly
  - JSON file: `config/categories.json`

### 3. CSS Selectors 🎯
- Product scraping selectors
- Can provide as:
  - File path: `setup/selectors.txt`
  - Inline JSON: Paste selector object
  - JSON file: `config/selectors.json`

**Required selectors**:
- `product_card_selector` - Container for each product
- `title_selector` - Product title
- `price_selector` - Product price
- `url_selector` - Product page URL
- `ean_selector` - EAN/barcode
- `next_page_selector` - Pagination link
- `image_selector` - Product image
- `out_of_stock_selector` - Stock status

### 4. Authentication Requirement 🔐
- Does supplier require login to view prices?
- If YES: Provide username + password
- If NO: Mention "no authentication required"

### 5. Pagination Details 📄
- **CRITICAL**: The scraper defaults to `?page=N` style pagination.
- **Warning**: If the supplier uses a different format (e.g., `/page/2/`, `p=2`, or "Load More" buttons), you MUST mention this.
- The scraper script (`tools/configurable_supplier_scraper.py`) may require manual editing for non-standard pagination.

---

## 🔍 What Claude Will Do (Detailed Workflow)

### Phase 1: Information Gathering
Claude reads your message and identifies:
- ✅ What you've already provided
- ❓ What's still missing

Then asks **ONLY** for missing information.

**Example**:
```
I have the following:
✅ Domain: angelwholesale.co.uk
✅ Categories: Found 328 URLs in setup/categories angel.txt
✅ Selectors: Found in setup/selectors angel.txt

I still need:
❓ Authentication Requirement: Does this site require login?
```

### Phase 2: File Preparation
Claude creates two JSON configuration files:
1. **Categories**: `config/angelwholesale_workflow_categories.json`
2. **Selectors**: `config/supplier_configs/angelwholesale.co.uk.json`

### Phase 3: Wizard Invocation
Claude constructs and executes wizard command:
```bash
python utils/supplier_onboarding_wizard.py \
  --domain "angelwholesale.co.uk" \
  --categories-source "config/angelwholesale_categories.json" \
  --selectors-source "config/supplier_configs/angelwholesale.co.uk.json" \
  --workflow-key "angelwholesale_workflow" \
  --mode generate \
  --authentication-required false
```

Wizard generates:
- Full runner script (117-143 lines)
- System config registration
- [If auth] Authentication helper template

### Phase 4: Comprehensive Validation ⚠️ CRITICAL
Claude **reads and analyzes** generated files (not just checks existence):

**Runner Script Validation**:
- [ ] File is 117-143 lines (NOT 26-line shim)
- [ ] Correct workflow_key referenced
- [ ] Authentication integration matches requirement
- [ ] Naming conventions followed (hyphen-form)
- [ ] Compares with reference implementations

**Configuration Validation**:
- [ ] Categories JSON structure correct
- [ ] All required selectors present
- [ ] System config updated correctly
- [ ] Naming conventions followed (dot-form for configs)

**Authentication Helper** (if applicable):
- [ ] Directory created with correct name (hyphen-form)
- [ ] Class name follows PascalCase convention
- [ ] Required methods present
- [ ] TODO comments present (expected for template)

### Phase 5: Result Reporting
Claude provides comprehensive summary:
```
✅ Supplier Onboarding Complete: angelwholesale.co.uk

📋 FILES GENERATED:
- Runner: run_custom_angelwholesale-co-uk.py (143 lines) ✅
- Categories: config/angelwholesale_workflow_categories.json (328 URLs) ✅
- Selectors: config/supplier_configs/angelwholesale.co.uk.json ✅
- System Config: Updated with angelwholesale_workflow ✅

🔍 VALIDATION RESULTS:
Structure Checks:           ✅ PASSED
Workflow Integration:       ✅ PASSED
Naming Conventions:         ✅ PASSED
Configuration Files:        ✅ PASSED

📊 SANITY CHECK: 6/6 Criteria Passed

🚀 NEXT STEPS:
1. Review runner for supplier-specific optimizations
2. Test: python run_custom_angelwholesale-co-uk.py
```

---

## ✅ Success Criteria

Onboarding is successful when:

1. **All Files Generated**:
   - ✅ Runner script exists and is correct length (117-143 lines, NOT 26)
   - ✅ Categories config exists with all URLs
   - ✅ Selector config exists with all required fields
   - ✅ System config updated with new workflow
   - ✅ [If auth] Auth helper generated as template

2. **Validation Passes**:
   - ✅ Runner references correct workflow_key (NOT poundwholesale or other supplier)
   - ✅ All naming conventions followed correctly
   - ✅ All configuration files valid JSON
   - ✅ Authentication integration matches requirement

3. **Sanity Check Passes**:
   - ✅ Products successfully scraped
   - ✅ Amazon cache files created
   - ✅ Linking maps generated
   - ✅ Financial CSV created
   - ✅ Processing state saved
   - ✅ No critical errors in logs

---

## 🚫 What NOT to Do

### ❌ Don't Edit Old Skill Files
The old `skills/supplier-onboarding/` directory (in root) is now deprecated.
- Don't edit `skill.yaml`
- Don't edit `main.py`
- All changes should be in `.claude/skills/supplier-onboarding/SKILL.md`

### ❌ Don't Manually Generate Scripts
Let the wizard generate runner and auth helper scripts.
- Don't create `run_custom_*.py` manually
- Don't create auth helpers manually
- Wizard uses templates for consistency

### ❌ Don't Skip Validation
Claude MUST read and analyze generated files, not just check existence.
- Always verify workflow_key is correct
- Always check file lengths (117-143 lines, NOT 26)
- Always validate naming conventions

---

## 🔧 Customization

### Customizing the Workflow

Edit `.claude/skills/supplier-onboarding/SKILL.md` to:
- Add additional validation checks
- Modify information gathering approach
- Update wizard command parameters
- Change success criteria

### Customizing Templates

Edit templates in `.claude/skills/supplier-onboarding/templates/`:
- `runner_template.py.txt` - Modify runner structure
- `auth_helper_template.py.txt` - Modify auth helper structure

**⚠️ Important**: After editing templates, regenerate suppliers to apply changes.

### Adding Reference Implementations

Add new reference scripts to `sample_data/`:
- Place runners in `reference_runners/`
- Place auth helpers in `reference_auth/`

These will be available for Claude to compare during validation.

---

## 📚 Documentation References

- **Main Workflow**: `.claude/skills/supplier-onboarding/SKILL.md`
- **Naming Rules**: `.claude/skills/supplier-onboarding/docs/NAMING_CONVENTIONS.md`
- **File Specs**: `.claude/skills/supplier-onboarding/docs/FILE_SPECIFICATIONS.md`
- **Troubleshooting**: `.claude/skills/supplier-onboarding/docs/TROUBLESHOOTING.md`

---

## 🎯 Example Session

```
You: "Use supplier-onboarding skill to add angelwholesale.co.uk

Categories in: setup/categories angel.txt
Selectors in: setup/selectors angel.txt
No login needed"

Claude: "I'm reading the provided files...

✅ Found 328 category URLs in setup/categories angel.txt
✅ Found detailed selectors in setup/selectors angel.txt
✅ Authentication not required

Creating configuration files...
✅ Created config/angelwholesale_workflow_categories.json
✅ Created config/supplier_configs/angelwholesale.co.uk.json

Invoking wizard...
[Wizard executes for ~7 minutes]
✅ Generated run_custom_angelwholesale-co-uk.py

Validating generated files...

Runner Script Validation:
✅ File is 143 lines (full implementation, NOT shim)
✅ Workflow key: 'angelwholesale_workflow' (correct)
✅ No authentication imports (correct for no-auth supplier)
✅ Naming convention: hyphen-form (correct)

Configuration Validation:
✅ Categories: 328 URLs, all valid
✅ Selectors: All 9 required fields present
✅ System config: angelwholesale_workflow registered

Sanity Check Results:
✅ Scraping Rate: PASS (20 products found)
✅ Amazon Cache: PASS
✅ Linking Map: PASS
✅ Financial CSV: PASS
✅ Processing State: PASS
✅ No Critical Errors: PASS

🎉 Supplier Onboarding Complete!

Next steps:
1. Test: python run_custom_angelwholesale-co-uk.py
2. Review financial reports in OUTPUTS/FBA_ANALYSIS/
"
```

---

## 🐛 Common Issues

See `.claude/skills/supplier-onboarding/docs/TROUBLESHOOTING.md` for detailed solutions.

**Quick Fixes**:
- **26-line shim generated**: Wizard needs update, delete and regenerate
- **Wrong workflow executed**: Edit runner, change workflow_key
- **Auth helper missing**: Re-run with --authentication-required true
- **Naming violations**: Rename files to correct form (see NAMING_CONVENTIONS.md)

---

## ✨ Benefits of New Structure

1. **Transparent**: All logic visible to Claude in SKILL.md
2. **Validated**: Claude reads and analyzes files, not just checks existence
3. **Flexible**: Claude can adapt based on context and error messages
4. **Documented**: Comprehensive docs, examples, and references
5. **Standard**: Follows official Anthropic skill patterns
6. **Maintainable**: Easy to update instructions in SKILL.md

---

**Ready to onboard your first supplier?**

Just say: **"Use supplier-onboarding skill to add [domain]"**

Claude will guide you through the rest!
