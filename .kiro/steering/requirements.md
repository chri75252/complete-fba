# Requirements - Amazon FBA Agent System v3.8+

## 🚨 CRITICAL SURGICAL IMPLEMENTATION REQUIREMENTS

### **🔒 SECURITY RESTRICTIONS - EXPLICIT USER APPROVAL REQUIRED**

**⚠️ MANDATORY: The following actions are FORBIDDEN unless explicitly requested by user:**

1. **🚫 API Key Modifications**: Never modify, remove, or change existing API keys
2. **🚫 Authentication System Changes**: Never alter authentication logic without explicit approval
3. **🚫 Security Configuration Updates**: Never modify security-related configurations
4. **🚫 Environment Variable Changes**: Never alter .env files or environment settings
5. **🚫 File Permission Modifications**: Never change file access permissions or security settings
6. **🚫 Network Configuration Changes**: Never modify proxy, firewall, or network settings

**✅ SECURITY PROTOCOL**: When security-related changes might be beneficial, ASK USER FIRST:
```
"I notice a potential security improvement: [description]
Should I proceed with this security-related change, or would you prefer to review it first?"
```

---

### **🧪 TESTING RESTRICTIONS - USER INSTRUCTION REQUIRED**

**⚠️ MANDATORY: System execution and testing require explicit user instruction:**

#### **🚫 FORBIDDEN without explicit user request:**
1. **Full System Execution**: Running `python run_custom_poundwholesale.py`
2. **Browser Automation Testing**: Starting Chrome with debug ports
3. **Live Website Interaction**: Accessing poundwholesale.co.uk or Amazon
4. **State File Modifications**: Altering processing state files
5. **Cache System Testing**: Running cache-dependent operations

#### **✅ ALLOWED general testing approaches:**
```bash
# Static code analysis and validation
python -m py_compile target_file.py
python -c "import target_module; print('Import successful')"

# Syntax and structure validation
grep -n "def\|class\|import" target_file.py
python -m ast target_file.py

# Configuration validation (non-destructive)
python -c "import json; json.load(open('config.json')); print('Config valid')"
```

#### **✅ ASK USER for system testing:**
```
"I recommend testing this change by running [specific test]. 
Should I proceed with system testing, or would you prefer to test it yourself?"
```

---

### **🔧 SURGICAL CODE MODIFICATION PROTOCOL (MANDATORY)**

**⚠️ CRITICAL: All code changes MUST follow surgical precision rules from `.kiro/steering/surgical-code-modification-rules.md`**

#### **MANDATORY PRE-IMPLEMENTATION VERIFICATION MATRIX:**

#### **1. Method Existence Verification**
```bash
# REQUIRED: Verify target method exists before ANY modification
grep -n "def target_method\|async def target_method" target_file.py
find . -name "*.py" -exec grep -l "def target_method" {} \;

# Example: Before calling scrape_products_from_url()
grep -n "def scrape_products_from_url" tools/configurable_supplier_scraper.py
```

#### **2. Attribute Existence Verification** 
```bash
# REQUIRED: Verify attribute initialization before accessing
grep -n "self\.target_attribute.*=" target_file.py
grep -A 20 "__init__" target_file.py | grep "self\.target_attribute"

# Example: Verify self.supplier_scraper exists
grep -n "self\.supplier_scraper.*=" tools/passive_extraction_workflow_latest.py
```

#### **3. Method Signature Compatibility Verification**
```bash
# REQUIRED: Check calling code matches method signature
grep -A 5 "def target_method" target_file.py
grep -rn "target_method(" . --include="*.py"

# Example: Verify _extract_supplier_products() signature compatibility
grep -A 3 "def _extract_supplier_products" tools/passive_extraction_workflow_latest.py
grep -rn "_extract_supplier_products(" . --include="*.py"
```

#### **4. Cross-Reference Impact Analysis**
```bash
# REQUIRED: Find ALL occurrences before changing anything
grep -rn "old_element_name" . --include="*.py" --include="*.json" --include="*.md"
grep -rn "\.old_attribute\." . --include="*.py"

# Example: Before changing any scraper references
grep -rn "\.scraper\." . --include="*.py"
grep -rn "self\.scraper" . --include="*.py"
```

---

## 🎯 SYSTEM BUSINESS REQUIREMENTS

### **Core Functionality Requirements**

#### **R1: Supplier Data Extraction**
- **Requirement**: Extract product data from poundwholesale.co.uk with >99% success rate
- **Critical Verification**: Method `scrape_products_from_url()` must exist and be accessible
- **Integration Verification**: Must work with PassiveExtractionWorkflow orchestration
- **Implementation Rule**: NEVER change method signatures without verifying all callers

#### **R2: Amazon Product Matching**
- **Requirement**: Match supplier products to Amazon listings with EAN/title fallback
- **Critical Verification**: AmazonPlaywrightExtractor methods must exist before calling
- **Integration Verification**: Linking map management must remain compatible
- **Implementation Rule**: Verify attribute names before accessing (e.g., self.extractor)

#### **R3: Financial Analysis & ROI Calculation**
- **Requirement**: Calculate profitability with VAT, fees, shipping costs
- **Critical Verification**: FBA_Financial_calculator methods must be verified before calling
- **Integration Verification**: Configuration loading must remain intact
- **Implementation Rule**: Preserve all existing calculation method signatures

#### **R4: State Management & Resume Capability**
- **Requirement**: 100% reliable resume functionality after interruption
- **Critical Verification**: FixedEnhancedStateManager attributes must exist before access
- **Integration Verification**: Atomic file operations must remain functional
- **Implementation Rule**: NEVER modify state management without complete verification

---

## 🛡️ SURGICAL PRECISION IMPLEMENTATION PROTOCOL

### **Mandatory Implementation Safety Checklist**

#### **Before ANY Code Change:**
- [ ] **Read original code first** using file reading tools
- [ ] **Verify problem actually exists** in current code
- [ ] **Check if problem already fixed** in recent changes
- [ ] **Identify exact minimal change required**
- [ ] **Search for attribute initialization**: `grep -n "self\.attribute.*=" file.py`
- [ ] **Verify method existence**: `grep -n "def method_name" file.py`
- [ ] **Check method signatures**: `grep -A 5 "def method_name" file.py`
- [ ] **Find all callers**: `grep -rn "method_name(" . --include="*.py"`
- [ ] **Create backup**: `mkdir backup_$(date +%Y%m%d_%H%M%S); cp files backup/`

#### **Implementation Execution Protocol:**
1. **Single Line Changes Only** - Make minimal surgical modifications
2. **Preserve Method Signatures** - Never change signatures without explicit approval
3. **Verify Each Change Immediately** - Check that change solves specific problem
4. **Test Integration Points** - Verify calling code still works
5. **Document Changes** - Record exact modifications made

#### **Post-Implementation Verification:**
- [ ] **Confirm specific issue resolved** - Target problem eliminated
- [ ] **Verify no new errors introduced** - No AttributeError, TypeError, NameError
- [ ] **Check integration points work** - Calling code functions correctly
- [ ] **Validate method signatures preserved** - All callers still compatible
- [ ] **Test import statements** - All imports work correctly

---

## 🏗️ ARCHITECTURAL INTEGRITY REQUIREMENTS (PRESERVE)

### **Critical System Patterns - DO NOT MODIFY**

#### **AI1: Multi-Tier AI Fallback System**
- **Pattern**: 4-tier temperature progression (0.1 → 0.3 → 0.5 → manual)
- **Verification Required**: All AI client method calls must maintain signature compatibility
- **Integration Points**: Category selection, product matching, error recovery
- **Rule**: Never change AI client instantiation or method calls without verification

#### **AI2: Unified State Management**
- **Pattern**: Single source of truth with atomic operations
- **Verification Required**: All state manager attribute access must be validated
- **Integration Points**: Resume functionality, progress calculation, file operations  
- **Rule**: Never modify state attributes without checking initialization

#### **AI3: Smart Caching System**
- **Pattern**: 240x performance improvement through hash optimization
- **Verification Required**: Cache manager method signatures must remain compatible
- **Integration Points**: Product deduplication, hash lookup, memory management
- **Rule**: Preserve all caching method signatures and calling patterns

#### **AI4: Filter Invariant Enforcement**
- **Pattern**: `skip + needs_amazon + needs_full == total_input`
- **Verification Required**: All filter-related method calls must be validated
- **Integration Points**: URL filtering, reconciliation logic, progress tracking
- **Rule**: Never modify filter logic without complete impact analysis

---

## 📊 PERFORMANCE REQUIREMENTS

### **P1: System Capabilities (Must Preserve)**
- **Processing Capacity**: 1M+ products per run without intervention
- **Session Duration**: 18+ hours continuous operation  
- **Resume Reliability**: 100% success rate maintained
- **Memory Management**: Smart clearing with sliding window approach
- **Browser Stability**: Automatic restart functionality preserved

### **P2: Performance Monitoring (General Approach)**
```bash
# Non-destructive performance validation
python -c "import psutil; print(f'Memory: {psutil.virtual_memory().percent}%')"
python -c "import time; start=time.time(); import target_module; print(f'Import time: {time.time()-start:.2f}s')"

# Configuration validation
python -c "import json; config=json.load(open('config/system_config.json')); print('Config loaded successfully')"
```

### **P3: Error Recovery Verification (Ask User for System Testing)**
- **Pattern**: "Should I test error recovery by running [specific component]?"
- **Approach**: Verify error handling logic exists without triggering it
- **Validation**: Check error handling code structure and imports

---

## 🔐 SECURITY REQUIREMENTS (USER APPROVAL REQUIRED)

### **S1: API Key Management (DO NOT MODIFY)**
- **Requirement**: Never hardcode API keys in source code
- **Current State**: API keys properly stored in environment variables
- **Verification Only**: Check for hardcoded patterns without changing anything
- **Rule**: ASK USER before any API key related modifications

### **S2: Authentication Safety (USER APPROVAL REQUIRED)**
- **Requirement**: Secure browser authentication with session management
- **Current State**: Authentication methods working correctly
- **Verification Only**: Confirm authentication code structure exists
- **Rule**: NEVER modify authentication logic without explicit user request

### **S3: Data Protection (PRESERVE EXISTING)**
- **Requirement**: Atomic file operations prevent data corruption
- **Current State**: Windows Save Guardian provides protection
- **Verification Only**: Confirm atomic write patterns exist
- **Rule**: Preserve all existing file operation patterns

---

## 🧪 TESTING & VERIFICATION APPROACH

### **T1: Static Analysis Testing (Always Allowed)**
```bash
# Code structure validation
python -m py_compile target_file.py
python -c "import ast; ast.parse(open('target_file.py').read())"
python -c "import target_module; print('Import successful')"

# Method and attribute verification
grep -n "def\|class" target_file.py
grep -n "self\." target_file.py | head -10
```

### **T2: Configuration Validation (Non-Destructive)**
```bash
# JSON configuration validation
python -c "import json; json.load(open('config/system_config.json')); print('Valid JSON')"
python -c "from utils.path_manager import *; print('Path manager imports successfully')"

# Module import testing  
python -c "from tools import *; print('Tools import successfully')" 2>/dev/null || echo "Import issues detected"
```

### **T3: System Integration Testing (ASK USER FIRST)**
```
EXAMPLE: "I recommend testing this change by running:
python tests/test_unified_state_manager.py

Should I proceed with this test, or would you prefer to run it yourself?"
```

### **T4: Live System Testing (USER INSTRUCTION REQUIRED)**
- **Full Workflow**: Never run without explicit user instruction
- **Browser Automation**: Never start without user permission  
- **Live Website Access**: Never access external sites without approval
- **State Modification**: Never modify processing state without permission

---

## 🎯 SERENA MCP INTEGRATION REQUIREMENTS

### **Context Switching Protocol**

#### **For Code Analysis Tasks:**
```yaml
Context: ide-assistant
Mode: interactive  
Safety: read-only
Purpose: Understanding code structure and identifying issues
```

#### **For Surgical Code Modifications:**
```yaml
Context: ide-assistant
Mode: editing
Safety: backup_before_changes
Purpose: Making minimal, verified code changes

Pre-Change Requirements:
- Create timestamped backup directory
- Verify target method/attribute exists
- Check all calling code compatibility  
- Confirm minimal change approach
```

#### **For System Analysis:**
```yaml
Context: agent
Mode: interactive
Safety: read-only
Purpose: Comprehensive system understanding and architecture analysis
```

### **Serena Safety Configuration Requirements**

#### **Mandatory Backup Protocol:**
```bash
# REQUIRED: Before ANY code modification via Serena
mkdir -p .serena/backups/$(date +%Y%m%d_%H%M%S)
cp -r affected_files/ .serena/backups/$(date +%Y%m%d_%H%M%S)/
```

#### **Verification Protocol:**
```bash
# REQUIRED: Before accessing any attribute or method via Serena  
# Use Serena's symbol analysis tools:
# - get_symbols_overview for class structure
# - find_symbol for method verification
# - get_code_context for usage patterns
```

#### **Read-Only Mode for Analysis:**
```yaml
# When analyzing system without modifications
serena_config:
  read_only: true
  backup_enabled: false
  analysis_only: true
```

#### **Edit Mode for Verified Changes:**
```yaml  
# Only after complete verification
serena_config:
  read_only: false
  backup_enabled: true
  verification_required: true
  minimal_changes_only: true
```

---

## 🎯 SUCCESS CRITERIA

### **SC1: Zero Regression Policy**
- ✅ All existing functionality must continue working after changes
- ✅ No new AttributeError, TypeError, or NameError exceptions  
- ✅ All method signatures preserved unless explicitly changed
- ✅ All attribute access patterns maintained

### **SC2: Surgical Implementation Verification**
- ✅ Every method existence verified before calling
- ✅ Every attribute existence verified before accessing
- ✅ Every method signature verified before modification
- ✅ All integration points tested after changes

### **SC3: Security and Testing Compliance**
- ✅ No unauthorized security modifications
- ✅ No unauthorized system testing
- ✅ User approval obtained for system-level changes
- ✅ Explicit permission received for live testing

### **SC4: Documentation Accuracy**
- ✅ All changes documented with verification results
- ✅ Surgical modification rules followed completely
- ✅ User informed of all modifications made
- ✅ Backup locations and restoration procedures provided

---

**Document Version**: 1.0  
**Last Updated**: 2025-08-15  
**Critical Dependencies**: `.kiro/steering/surgical-code-modification-rules.md`  
**Enforcement Level**: MANDATORY - Violation results in task termination