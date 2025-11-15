# Supplier Onboarding Skill - Complete Restructure Following Anthropic Best Practices (January 2025)

## Session Context

**User Request**: Restructure the supplier-onboarding skill to follow official Claude Code skill best practices, based on:
1. Latest memory file about angelwholesale.co.uk onboarding issues
2. Anthropic's official skill patterns (claude-cookbooks/skills)
3. Context7 documentation on Claude Code skills
4. Efficient, clear, least error-prone approach

**Key User Insight**: Suggested slash command should contain validation instructions, OR include all validation logic directly in SKILL.md. User wanted most efficient approach.

---

## Critical Clarification: Generation vs Validation

**WIZARD GENERATES (Automated, Template-Based)**:
- Loads templates from `.claude/skills/supplier-onboarding/templates/`
- Replaces variables: `{{WORKFLOW_KEY}}`, `{{SUPPLIER_NAME}}`, `{{SUPPLIER_DOMAIN}}`, etc.
- Writes full 117-143 line runner scripts
- Generates authentication helpers (if auth_required=true)
- Fast, deterministic, consistent

**CLAUDE VALIDATES (Post-Generation, Intelligent)**:
- **READS** generated files (not just checks existence)
- **ANALYZES** structure, content, and correctness
- **COMPARES** with reference implementations in sample_data/
- **VERIFIES** naming conventions (dot/hyphen/underscore forms)
- **CHECKS** workflow_key correctness (must match supplier, not reference other suppliers)
- **REPORTS** specific findings with remediation steps
- Adaptive, intelligent, context-aware

**This is the "Hybrid Approach"**: Speed of automation + intelligence of validation

---

## Complete File Structure Created

```
.claude/skills/supplier-onboarding/
├── SKILL.md (23.8 KB)                    # ⭐ SINGLE SOURCE OF TRUTH
│   ├── YAML frontmatter (name, description)
│   ├── Step 1: Progressive Information Gathering
│   │   └── Ask ONLY for missing information
│   ├── Step 2: Prepare Configuration Files
│   │   ├── Categories JSON
│   │   └── Selectors JSON
│   ├── Step 3: Invoke Wizard
│   │   └── Construct and execute wizard command
│   ├── Step 4: Validate Generated Files ⚠️ CRITICAL
│   │   ├── 4.1. Runner Script Validation
│   │   │   ├── Structure checks (117-143 lines, NOT 26)
│   │   │   ├── Workflow integration checks
│   │   │   ├── Authentication integration checks
│   │   │   ├── Naming convention checks
│   │   │   └── Compare with reference implementations
│   │   ├── 4.2. Configuration Files Validation
│   │   │   ├── Categories JSON
│   │   │   ├── Selector JSON
│   │   │   └── System config update
│   │   ├── 4.3. Authentication Helper Validation (if applicable)
│   │   └── 4.4. Naming Convention Compliance Summary
│   └── Step 5: Report Results
│       ├── Success summary (comprehensive)
│       └── Failure summary (with remediation)
│
├── SETUP_AND_USAGE.md (13.5 KB)          # Complete user guide
│   ├── What was created
│   ├── Key improvements (before/after)
│   ├── How to use (3 methods)
│   ├── What information needed
│   ├── Detailed workflow explanation
│   ├── Success criteria
│   ├── Common issues
│   └── Example session
│
├── docs/
│   ├── NAMING_CONVENTIONS.md (9.2 KB)
│   │   ├── Three naming forms explained
│   │   │   ├── Dot-form (domain): supplier.co.uk
│   │   │   ├── Hyphen-form (supplier_id): supplier-co-uk
│   │   │   └── Underscore-form (workflow): supplier_workflow
│   │   ├── Quick reference table
│   │   ├── Validation checklist
│   │   ├── Common mistakes
│   │   └── Class name conversion (PascalCase)
│   │
│   ├── FILE_SPECIFICATIONS.md (11.7 KB)
│   │   ├── Runner script specification
│   │   │   ├── Required imports
│   │   │   ├── Main function structure
│   │   │   ├── Critical lines to verify
│   │   │   └── Entry point requirements
│   │   ├── Categories configuration spec
│   │   ├── Selector configuration spec
│   │   ├── System config update spec
│   │   └── Authentication helper spec
│   │
│   └── TROUBLESHOOTING.md (13.8 KB)
│       ├── Issue 1: 26-line shim generated (CRITICAL)
│       ├── Issue 2: Wrong workflow executed
│       ├── Issue 3: Auth helper not generated
│       ├── Issue 4: Naming convention violations
│       ├── Issue 5: Sanity check failures
│       ├── Issue 6: Template placeholders not replaced
│       ├── Issue 7: Permission denied (Windows)
│       ├── Issue 8: Module import errors
│       └── Quick diagnostic commands
│
├── sample_data/
│   ├── reference_runners/
│   │   ├── poundwholesale.py            # 143 lines with authentication
│   │   └── clearance_king.py            # 117 lines without authentication
│   │
│   └── reference_auth/
│       └── poundwholesale_auth.py       # Complete auth helper example
│
└── templates/
    ├── runner_template.py.txt           # Base runner template (117 lines)
    └── auth_helper_template.py.txt      # Base auth helper template (95 lines)
```

**Total Files**: 10 files created

---

## Key Design Decisions

### Decision 1: Single SKILL.md (No Slash Command)

**Reasoning**: 
- All logic in one place (single source of truth)
- Slash command would just be "use the skill" (redundant)
- Validation instructions belong in skill workflow
- Follows Anthropic pattern (SKILL.md with YAML frontmatter)

**Result**: SKILL.md contains complete workflow from gathering info to reporting results

### Decision 2: Progressive Information Gathering

**Pattern**:
```markdown
1. Check what user has provided
2. Identify missing information  
3. Ask ONLY for missing information (don't repeat what they said)
```

**Benefits**:
- Efficient (no redundant questions)
- Smart (adapts to what user already provided)
- User-friendly (respects their input)

### Decision 3: Comprehensive Validation Instructions

**CRITICAL**: Claude must READ and ANALYZE files, not just check existence

**Validation Checklist in SKILL.md**:
- [ ] Runner is 117-143 lines (if 26 lines → CRITICAL ERROR: shim detected)
- [ ] Workflow_key correct (search for get_workflow_config() calls)
- [ ] Authentication integration matches requirement
- [ ] Naming conventions followed (dot/hyphen/underscore forms)
- [ ] Compare structure with reference implementations
- [ ] All configuration files valid JSON with required fields

### Decision 4: Reference Implementations

**Purpose**: Claude can read and compare generated files against working examples

**Included**:
- `poundwholesale.py` - 143-line runner with auth
- `clearance_king.py` - 117-line runner without auth  
- `poundwholesale_auth.py` - Complete auth helper

### Decision 5: Templates in Skill Directory

**Pattern**: Following Anthropic's skill structure
```
skill/
├── SKILL.md
├── docs/
├── sample_data/
└── templates/        # Resources used by skill
```

**Wizard Updated**: Now loads templates from `.claude/skills/supplier-onboarding/templates/`

---

## What Changed from Old to New

### Old Structure (Deprecated)
```
skills/supplier-onboarding/           # ❌ Wrong location (root, not .claude/)
├── skill.yaml                        # ❌ Wrong format (separate YAML)
├── main.py                           # ❌ Executable orchestrator
└── README.md
```

**Problems**:
- Not recognized by Claude Code skill system
- Contains executable code instead of instructions
- Hidden logic in Python subprocess calls
- No validation instructions for Claude
- Session file complexity (input.json → output.json)

### New Structure (Current)
```
.claude/skills/supplier-onboarding/   # ✅ Correct location
├── SKILL.md                          # ✅ YAML frontmatter + Markdown
├── docs/                             # ✅ Supporting documentation
├── sample_data/                      # ✅ Reference implementations
└── templates/                        # ✅ Wizard resources
```

**Benefits**:
- ✅ Proper Claude Code integration
- ✅ All logic visible to Claude
- ✅ Transparent workflow execution
- ✅ Comprehensive validation instructions
- ✅ Reference implementations for comparison
- ✅ Following Anthropic best practices

---

## How to Use the New Skill

### Method 1: Direct Invocation (Recommended)
```
User: "Use supplier-onboarding skill to add angelwholesale.co.uk"
```

**Claude's Workflow**:
1. Reads SKILL.md
2. Checks what user provided
3. Asks for missing info (categories, selectors, auth)
4. Creates config files
5. Invokes wizard: `python utils/supplier_onboarding_wizard.py ...`
6. **VALIDATES generated files** (reads and analyzes)
7. Reports comprehensive results

### Method 2: With All Information
```
User: "Use supplier-onboarding skill to add angelwholesale.co.uk

Categories in: setup/categories angel.txt
Selectors in: setup/selectors angel.txt  
No authentication required"
```

Claude skips asking and proceeds directly.

### Method 3: Inline Data
```
User: "Use supplier-onboarding skill to add example.co.uk

Categories: https://example.co.uk/cat1, https://example.co.uk/cat2

Selectors:
- Product card: .product-item
- Title: h3.title
- Price: .price

Authentication: yes
Username: user@example.com
Password: SecurePass123"
```

---

## Validation Behavior (CRITICAL)

**What Claude Does During Step 4 (Validation)**:

### 4.1. Runner Script Validation

**Read the file**:
```bash
Read: run_custom_angelwholesale-co-uk.py
```

**Check line count**:
```
Lines: 143 → ✅ PASS (full implementation)
Lines: 26 → ❌ FAIL: CRITICAL ERROR - This is a shim!
```

**Verify workflow_key** (CRITICAL):
```python
# Claude searches for this line in runner:
workflow_config = config_loader.get_workflow_config('angelwholesale_workflow')

✅ PASS: 'angelwholesale_workflow' (correct)
❌ FAIL: 'poundwholesale_workflow' (WRONG SUPPLIER!)
```

**Compare with references**:
```bash
Read: sample_data/reference_runners/poundwholesale.py
Compare structure: imports, main function, entry point
Verify pattern matches
```

**Check naming conventions**:
```
File name: run_custom_angelwholesale-co-uk.py
Expected form: HYPHEN-FORM (supplier-co-uk)
Actual: angelwholesale-co-uk
Result: ✅ PASS
```

### 4.2. Configuration Validation

**Categories JSON**:
```bash
Read: config/angelwholesale_workflow_categories.json
Check: {"category_urls": [...]} structure
Verify: All URLs complete and valid
Count: 328 URLs
```

**Selectors JSON**:
```bash
Read: config/supplier_configs/angelwholesale.co.uk.json
Check: File name uses DOT-FORM (not hyphen-form)
Verify: All 10 required selectors present
Check: authentication_required boolean correct
```

**System Config**:
```bash
Read: config/system_config.json workflows section
Check: angelwholesale_workflow entry exists
Verify: supplier_name uses DOT-FORM
Verify: All required fields present
```

### 4.3. Authentication Helper (If Applicable)

**Directory structure**:
```bash
Check: tools/angelwholesale-co-uk/ exists (hyphen-form)
Check: __init__.py exists
Check: supplier_authentication_service.py exists
```

**Read and verify**:
```bash
Read: tools/angelwholesale-co-uk/supplier_authentication_service.py
Check: Class name is AngelwholesaleCoUkAuthenticationHelper (PascalCase)
Check: is_authenticated() method present
Check: login() method present
Check: TODO comments present (EXPECTED for template)
```

---

## Critical Lines in SKILL.md

**Line ~200-300**: Runner Script Validation
- Detailed checks for structure, workflow_key, auth, naming
- Instructions to READ file and COMPARE with references
- Specific error messages for each failure type

**Line ~301-380**: Configuration Files Validation  
- JSON structure verification
- Required fields checking
- Naming form validation

**Line ~381-420**: Naming Convention Compliance
- Three-form table with examples
- Validation checklist
- Common mistakes to avoid

**Line ~421-500**: Result Reporting
- Success summary template
- Failure summary template with remediation
- Next steps guidance

---

## Wizard Integration Changes

**Updated Template Paths** (utils/supplier_onboarding_wizard.py):

**Line 308** (create_full_runner):
```python
# OLD:
template_path = repo_root / "utils/runner_template.py.txt"

# NEW:
template_path = repo_root / ".claude/skills/supplier-onboarding/templates/runner_template.py.txt"
```

**Line 391** (create_auth_helper):
```python
# OLD:
template_path = repo_root / "utils/auth_helper_template.py.txt"

# NEW:
template_path = repo_root / ".claude/skills/supplier-onboarding/templates/auth_helper_template.py.txt"
```

**Why**: Following Anthropic pattern - templates are part of skill resources, not system utils

---

## Testing the New Skill

### Test Case 1: Basic Invocation
```
User: "Use supplier-onboarding skill to add angelwholesale.co.uk"

Expected:
1. Claude reads SKILL.md
2. Checks what's provided (just domain)
3. Asks for categories, selectors, auth requirement
4. User provides information
5. Claude creates config files
6. Claude invokes wizard
7. Claude READS generated runner (not just checks existence)
8. Claude VERIFIES workflow_key is 'angelwholesale_workflow' (not 'poundwholesale_workflow')
9. Claude COMPARES with reference implementations
10. Claude reports comprehensive results
```

### Test Case 2: With All Information
```
User: "Use supplier-onboarding skill to add angelwholesale.co.uk

Categories in: setup/categories angel.txt
Selectors in: setup/selectors angel.txt
No authentication required"

Expected:
1. Claude reads SKILL.md
2. Checks what's provided (all info present)
3. Skips asking questions
4. Creates config files immediately
5. Invokes wizard
6. Validates generated files
7. Reports results
```

### Validation Test: 26-Line Shim Detection
```
If wizard generates 26-line shim:

Claude should:
1. Read the file
2. Count lines: 26
3. Report: "❌ CRITICAL ERROR: Generated runner is only 26 lines - this is a shim!"
4. Identify: "Found BASE_RUNNER = 'run_custom_poundwholesale.py'"
5. Explain: "This will execute wrong supplier workflow"
6. Provide remediation: Delete file, verify wizard has create_full_runner(), regenerate
```

### Validation Test: Wrong Workflow Key
```
If workflow_key is wrong:

Claude should:
1. Read runner file
2. Search for: config_loader.get_workflow_config(...)
3. Find: 'poundwholesale_workflow'
4. Report: "❌ CRITICAL ERROR: Wrong workflow_key"
5. Show: Found 'poundwholesale_workflow', Expected 'angelwholesale_workflow'
6. Explain: "Sanity check will scrape wrong supplier"
7. Provide fix: Edit line X, change workflow_key
```

---

## Success Criteria

Skill is working correctly when:

1. **Location**: Skill is in `.claude/skills/supplier-onboarding/` (not `skills/`)
2. **Format**: SKILL.md has YAML frontmatter + Markdown content
3. **Invocation**: User can say "Use supplier-onboarding skill" and it works
4. **Progressive**: Claude asks ONLY for missing information
5. **Validation**: Claude READS generated files and ANALYZES content
6. **Comparison**: Claude compares with reference implementations
7. **Detection**: Claude detects 26-line shims and reports CRITICAL ERROR
8. **Verification**: Claude verifies workflow_key correctness
9. **Naming**: Claude validates all three naming forms
10. **Reporting**: Claude provides comprehensive results with specific findings

---

## Files Generated by Skill Workflow

When user invokes skill for `angelwholesale.co.uk`:

**Before Wizard** (Claude creates):
1. `config/angelwholesale_workflow_categories.json` - Categories from user-provided file/data
2. `config/supplier_configs/angelwholesale.co.uk.json` - Selectors from user-provided file/data

**Wizard Generates**:
3. `run_custom_angelwholesale-co-uk.py` - Full 117-143 line runner
4. `config/system_config.json` - Updated with angelwholesale_workflow entry
5. [If auth] `tools/angelwholesale-co-uk/supplier_authentication_service.py` - Auth helper template

**Claude Validates**:
- Reads all 5 files
- Analyzes structure and content
- Compares with references
- Verifies correctness
- Reports findings

---

## Documentation Guide

**For Next Session**:
1. **Start with**: `.claude/skills/supplier-onboarding/SETUP_AND_USAGE.md`
2. **Workflow details**: `.claude/skills/supplier-onboarding/SKILL.md`
3. **Naming rules**: `.claude/skills/supplier-onboarding/docs/NAMING_CONVENTIONS.md`
4. **File specs**: `.claude/skills/supplier-onboarding/docs/FILE_SPECIFICATIONS.md`
5. **If issues**: `.claude/skills/supplier-onboarding/docs/TROUBLESHOOTING.md`

**For Users**:
- Quick start: SETUP_AND_USAGE.md
- Just say: "Use supplier-onboarding skill to add [domain]"

**For Developers**:
- Templates: `.claude/skills/supplier-onboarding/templates/*.txt`
- References: `.claude/skills/supplier-onboarding/sample_data/`
- Wizard code: `utils/supplier_onboarding_wizard.py` (lines 308, 391 updated)

---

## Key Lessons Learned

### Lesson 1: Single Source of Truth
**Don't split logic** across SKILL.md + slash command. Put everything in SKILL.md.

### Lesson 2: Validation is Critical
**Reading files matters**. Checking existence is not enough. Claude must analyze content.

### Lesson 3: Reference Implementations
**Real examples beat descriptions**. Claude can compare generated files with working references.

### Lesson 4: Progressive Discovery
**Ask only for missing info**. Don't repeat what user already provided.

### Lesson 5: Templates as Resources
**Following Anthropic pattern**: Templates belong in skill directory, not system utils.

---

## Next Steps for User

### Immediate Actions:
1. **Test the skill**: "Use supplier-onboarding skill to add angelwholesale.co.uk"
2. **Verify validation**: Check that Claude reads files and reports specific findings
3. **Test detection**: Verify Claude detects 26-line shims if they occur

### Optional Actions:
1. **Clean old skill**: Can delete `skills/supplier-onboarding/` (root location) once new skill verified working
2. **Update README**: Update main project README to reference new skill location
3. **Add more references**: Add more reference runners to sample_data/ if available

---

## Implementation Status

✅ **COMPLETE**: All files created, wizard updated, skill restructured

**Files Created**: 10
- SKILL.md (23.8 KB)
- SETUP_AND_USAGE.md (13.5 KB)
- NAMING_CONVENTIONS.md (9.2 KB)
- FILE_SPECIFICATIONS.md (11.7 KB)
- TROUBLESHOOTING.md (13.8 KB)
- runner_template.py.txt (117 lines)
- auth_helper_template.py.txt (95 lines)
- poundwholesale.py (reference)
- clearance_king.py (reference)
- poundwholesale_auth.py (reference)

**Files Updated**: 1
- utils/supplier_onboarding_wizard.py (template paths updated)

**Result**: Production-ready supplier-onboarding skill following Anthropic best practices

---

## Final Architecture Summary

```
USER INVOCATION
     │
     ▼
CLAUDE reads .claude/skills/supplier-onboarding/SKILL.md
     │
     ├─> Step 1: Check what user provided
     │            Ask ONLY for missing info
     │
     ├─> Step 2: Create config files
     │            - categories JSON
     │            - selectors JSON
     │
     ├─> Step 3: Invoke wizard
     │            python utils/supplier_onboarding_wizard.py ...
     │            │
     │            ├─> Wizard loads templates from skill directory
     │            ├─> Wizard replaces variables
     │            └─> Wizard writes full runner (117-143 lines)
     │
     ├─> Step 4: VALIDATE generated files ⚠️ CRITICAL
     │            │
     │            ├─> READ runner (not just check existence)
     │            ├─> CHECK line count (26 = shim = ERROR)
     │            ├─> VERIFY workflow_key correctness
     │            ├─> COMPARE with reference implementations
     │            └─> VALIDATE naming conventions
     │
     └─> Step 5: Report comprehensive results
                  - Success summary OR
                  - Failure summary with remediation
```

**This architecture is**: Efficient, transparent, validated, and following official Anthropic patterns.

---

**End of Memory File**
