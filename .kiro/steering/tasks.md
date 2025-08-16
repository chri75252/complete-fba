# Tasks - Amazon FBA Agent System v3.8+

## 🚨 CRITICAL IMPLEMENTATION TASK PROTOCOLS

### **🔒 SECURITY TASK RESTRICTIONS - USER APPROVAL MANDATORY**

**⚠️ FORBIDDEN TASKS without explicit user instruction:**

#### **Security-Related Tasks (ASK USER FIRST):**
- [ ] **API Key Modifications**: Any changes to existing API key configurations
- [ ] **Authentication Updates**: Modifications to authentication logic or session management
- [ ] **Security Configuration Changes**: Updates to security-related settings or protocols
- [ ] **Environment Variable Modifications**: Changes to .env files or environment settings
- [ ] **Permission Adjustments**: File access or security permission modifications
- [ ] **Network Configuration Tasks**: Proxy, firewall, or network setting changes

#### **Required User Approval Protocol:**
```
EXAMPLE: "I've identified a potential security improvement in API key handling:
[Description of proposed change]

This involves modifying security-related code. Should I proceed with this change, 
or would you prefer to review and implement it yourself?"
```

---

### **🧪 SYSTEM TESTING TASK RESTRICTIONS - USER INSTRUCTION REQUIRED**

**⚠️ FORBIDDEN TASKS without explicit user permission:**

#### **Live System Execution Tasks (ASK USER FIRST):**
- [ ] **Full Workflow Execution**: Running `python run_custom_poundwholesale.py`
- [ ] **Browser Automation Testing**: Starting Chrome with debug ports or live testing
- [ ] **External Website Access**: Connecting to poundwholesale.co.uk or Amazon.co.uk
- [ ] **State File Modifications**: Altering processing state or cache files
- [ ] **Live API Testing**: Making actual API calls to OpenAI or other services

#### **Required Testing Approval Protocol:**
```
EXAMPLE: "To verify this fix works correctly, I recommend running:
python tests/test_unified_state_manager.py

Should I execute this test, or would you prefer to run it yourself?"
```

#### **Allowed Static Testing Tasks:**
```bash
# Always allowed - static validation
python -m py_compile target_file.py
python -c "import target_module; print('Import successful')"
grep -n "def\|class" target_file.py
python -m ast target_file.py  # Syntax validation
```

---

### **🔧 SURGICAL CODE MODIFICATION TASK PROTOCOL**

**⚠️ CRITICAL: All code modification tasks MUST follow surgical precision rules**

#### **MANDATORY Pre-Implementation Task Checklist:**

##### **T1: Code Analysis Tasks (ALWAYS REQUIRED)**
- [ ] **Read Original Code**: Use file reading tools to examine current implementation
- [ ] **Identify Exact Problem**: Pinpoint specific issue location and root cause
- [ ] **Verify Problem Exists**: Confirm issue is present and not already fixed
- [ ] **Understand Current Behavior**: Analyze what code currently does

##### **T2: Verification Tasks (MANDATORY BEFORE ANY CHANGE)**
- [ ] **Method Existence Verification**:
  ```bash
  grep -n "def target_method" target_file.py
  find . -name "*.py" -exec grep -l "def target_method" {} \;
  ```

- [ ] **Attribute Existence Verification**:
  ```bash
  grep -n "self\.target_attribute.*=" target_file.py
  grep -A 20 "__init__" target_file.py | grep "self\.target_attribute"
  ```

- [ ] **Method Signature Verification**:
  ```bash
  grep -A 5 "def target_method" target_file.py
  grep -rn "target_method(" . --include="*.py"
  ```

- [ ] **Cross-Reference Analysis**:
  ```bash
  grep -rn "target_element" . --include="*.py" --include="*.json"
  grep -rn "\.target_attribute\." . --include="*.py"
  ```

##### **T3: Impact Assessment Tasks (CRITICAL)**
- [ ] **Find All Callers**: Identify every location that calls the method/uses the attribute
- [ ] **Check Integration Points**: Verify how change affects component interactions
- [ ] **Assess Dependency Chain**: Understand downstream effects of modification
- [ ] **Identify Minimal Change**: Determine smallest possible fix that solves problem

---

## 🎯 CORE DEVELOPMENT TASKS

### **TD1: Supplier Data Extraction Tasks**

#### **Priority: HIGH - Core System Functionality**

##### **Task: Fix Supplier Scraper Integration Issues**
- **Problem Pattern**: AttributeError when accessing `self.scraper` vs `self.supplier_scraper`
- **Pre-Implementation Checklist**:
  - [ ] Verify attribute name in `PassiveExtractionWorkflow.__init__`
  - [ ] Check all references to scraper attribute throughout workflow
  - [ ] Confirm `ConfigurableSupplierScraper` method names
  - [ ] Test integration between workflow and scraper components

##### **Task: Resolve Method Name Mismatches**
- **Problem Pattern**: Calling `extract_products_from_category()` when method is `scrape_products_from_url()`
- **Pre-Implementation Checklist**:
  - [ ] Read `ConfigurableSupplierScraper` class to identify actual method names
  - [ ] Find all callers of scraper methods in workflow
  - [ ] Verify method signatures match calling patterns
  - [ ] Update calling code with correct method names

##### **Task: Validate Supplier URL Processing**
- **Pre-Implementation Checklist**:
  - [ ] Verify supplier URL handling in scraper
  - [ ] Check category processing logic
  - [ ] Validate product data extraction patterns
  - [ ] Test error handling for malformed URLs

---

### **TD2: Amazon Integration Tasks**

#### **Priority: HIGH - Core Matching Functionality**

##### **Task: Fix Amazon Extractor Integration**
- **Problem Pattern**: Method signature mismatches in Amazon data extraction
- **Pre-Implementation Checklist**:
  - [ ] Verify `AmazonPlaywrightExtractor` method signatures
  - [ ] Check workflow integration with Amazon extractor
  - [ ] Validate EAN/title fallback logic
  - [ ] Test linking map generation and updates

##### **Task: Resolve Product Matching Issues**
- **Pre-Implementation Checklist**:
  - [ ] Verify product matching algorithm accuracy
  - [ ] Check EAN-to-ASIN mapping consistency
  - [ ] Validate title-based fallback mechanism
  - [ ] Test duplicate product handling

---

### **TD3: State Management Tasks**

#### **Priority: CRITICAL - System Resume Functionality**

##### **Task: Fix State Manager Attribute Access**
- **Problem Pattern**: Accessing non-existent attributes in state manager
- **Pre-Implementation Checklist**:
  - [ ] Read `FixedEnhancedStateManager.__init__` to verify all attributes
  - [ ] Check attribute usage patterns in workflow
  - [ ] Verify atomic operation implementations
  - [ ] Test resume functionality end-to-end

##### **Task: Resolve Progress Tracking Inconsistencies**
- **Pre-Implementation Checklist**:
  - [ ] Verify progress calculation methods exist
  - [ ] Check counter synchronization between components
  - [ ] Validate file-based state persistence
  - [ ] Test state corruption detection and repair

##### **Task: Fix Filter Invariant Violations**
- **Problem Pattern**: `skip + needs_amazon + needs_full != total_input`
- **Pre-Implementation Checklist**:
  - [ ] Verify filter counting logic accuracy
  - [ ] Check reconciliation mechanism implementation
  - [ ] Validate invariant enforcement at all stages
  - [ ] Test automatic repair functionality

---

### **TD4: Performance Optimization Tasks**

#### **Priority: MEDIUM - System Efficiency**

##### **Task: Validate Memory Management Performance**
- **Pre-Implementation Checklist**:
  - [ ] Verify smart memory clearing implementation
  - [ ] Check sliding window mechanism accuracy
  - [ ] Validate memory threshold configurations
  - [ ] Test garbage collection triggers

##### **Task: Optimize Cache System Performance**
- **Pre-Implementation Checklist**:
  - [ ] Verify hash-based deduplication logic
  - [ ] Check cache hit/miss ratio calculations
  - [ ] Validate cache eviction policies
  - [ ] Test cache integrity after clearing operations

---

## 🛡️ IMPLEMENTATION TASK EXECUTION PROTOCOL

### **Phase 1: Preparation Tasks (MANDATORY)**

#### **P1.1: Environment Preparation**
```bash
# REQUIRED: Create backup before ANY modification
mkdir -p backup/task_$(date +%Y%m%d_%H%M%S)
cp -r target_files/ backup/task_$(date +%Y%m%d_%H%M%S)/
```

#### **P1.2: Code Analysis Tasks**
```bash
# REQUIRED: Understand current implementation
# Read target files to understand current behavior
# Identify exact problem location and cause
# Verify problem exists and hasn't been fixed already
```

#### **P1.3: Verification Tasks**
```bash
# REQUIRED: Verify all elements before modification
grep -n "def target_method\|async def target_method" target_file.py
grep -n "self\.target_attribute.*=" target_file.py
grep -A 5 "def target_method" target_file.py
grep -rn "target_method(" . --include="*.py"
```

### **Phase 2: Implementation Tasks (SURGICAL PRECISION)**

#### **P2.1: Minimal Change Application**
- [ ] **Apply Single Line Changes Only**: Make minimal surgical modifications
- [ ] **Preserve Method Signatures**: Never change signatures without explicit verification
- [ ] **Maintain Attribute Names**: Use exact attribute names that exist in classes
- [ ] **Fix Specific Issue Only**: Address only the identified problem, nothing else

#### **P2.2: Immediate Verification**
- [ ] **Test Specific Fix**: Verify the specific issue is resolved
- [ ] **Check Integration Points**: Ensure calling code still works correctly
- [ ] **Validate Method Calls**: Confirm all method calls use correct signatures
- [ ] **Test Import Statements**: Verify all imports work without errors

### **Phase 3: Validation Tasks (COMPREHENSIVE)**

#### **P3.1: Static Validation Tasks (ALWAYS ALLOWED)**
```bash
# Code structure validation
python -m py_compile modified_file.py
python -c "import modified_module; print('Import successful')"
python -m ast modified_file.py
```

#### **P3.2: Integration Validation Tasks (ASK USER FOR SYSTEM TESTS)**
```
EXAMPLE: "I've completed the fix. To verify it works end-to-end, 
I recommend running: python tests/test_integration.py

Should I execute this test, or would you prefer to run it yourself?"
```

#### **P3.3: Error Monitoring Tasks**
```bash
# Check for new errors (static analysis)
grep -E "AttributeError|TypeError|NameError" logs/debug/*.log 2>/dev/null || echo "No recent error logs found"
```

---

## 🎯 SERENA MCP TASK INTEGRATION

### **SM1: Analysis Phase Tasks**

#### **Context Configuration for Analysis:**
```yaml
serena_analysis_tasks:
  context: ide-assistant
  mode: interactive
  safety: read-only
  
  required_analysis_tasks:
    - get_symbols_overview: Understand class structure and available methods
    - find_symbol: Locate specific method or attribute definitions
    - get_code_context: Analyze usage patterns and integration points
    - analyze_dependencies: Map component relationships
```

#### **Analysis Task Checklist:**
- [ ] **Symbol Overview**: Use Serena to map class structure before making changes
- [ ] **Method Discovery**: Use find_symbol to verify method existence
- [ ] **Usage Pattern Analysis**: Understand how methods/attributes are used
- [ ] **Dependency Mapping**: Identify all integration points that might be affected

### **SM2: Implementation Phase Tasks**

#### **Context Configuration for Implementation:**
```yaml
serena_implementation_tasks:
  context: ide-assistant
  mode: editing
  safety: backup_before_changes
  
  pre_implementation_requirements:
    - backup_creation: Create timestamped backup directory
    - symbol_verification: Confirm target symbols exist
    - integration_check: Verify all calling code compatibility
    - minimal_change_plan: Define exact surgical modification needed
```

#### **Implementation Task Protocol:**
- [ ] **Create Backup**: `mkdir .serena/backups/$(date +%Y%m%d_%H%M%S)`
- [ ] **Verify Symbols**: Use Serena's symbol analysis to confirm method/attribute existence
- [ ] **Apply Surgical Fix**: Make minimal change addressing specific issue only
- [ ] **Immediate Validation**: Use Serena to verify fix doesn't break integration points

### **SM3: Verification Phase Tasks**

#### **Context Configuration for Verification:**
```yaml
serena_verification_tasks:
  context: ide-assistant
  mode: interactive
  safety: read-only
  
  verification_capabilities:
    - symbol_integrity: Verify all symbols still accessible
    - usage_validation: Check usage patterns remain valid
    - integration_testing: Validate component interactions
    - error_detection: Identify potential issues introduced
```

#### **Verification Task Checklist:**
- [ ] **Symbol Integrity**: Confirm all modified symbols are accessible
- [ ] **Usage Validation**: Verify all usage patterns remain valid
- [ ] **Integration Testing**: Check component interactions work correctly
- [ ] **Error Prevention**: Ensure no AttributeError, TypeError, NameError introduced

---

## 🧪 TESTING TASK FRAMEWORK

### **TF1: Static Testing Tasks (ALWAYS ALLOWED)**

#### **Code Structure Testing:**
```bash
# Syntax and import validation
python -m py_compile target_file.py
python -c "import target_module; print('Module imports successfully')"
python -m ast target_file.py

# Method and attribute discovery
grep -n "def\|class" target_file.py
grep -n "self\." target_file.py | head -10

# Configuration validation
python -c "import json; json.load(open('config/system_config.json')); print('Config valid')"
```

### **TF2: Integration Testing Tasks (USER APPROVAL REQUIRED)**

#### **Component Integration Tests:**
```
USER APPROVAL REQUIRED: "Should I run integration tests to verify the fix?"

# If approved:
python tests/test_workflow_integration.py
python tests/test_state_manager_integration.py  
python tests/test_supplier_scraper_integration.py
```

#### **System-Level Tests (USER INSTRUCTION REQUIRED):**
```
USER INSTRUCTION REQUIRED: "Should I run full system tests?"

# If instructed:
python tests/validate_comprehensive_state_fixes.py
python tests/integration/test_resume_functionality.py
python tests/integration/test_data_integrity.py
```

### **TF3: Live System Testing Tasks (EXPLICIT USER PERMISSION)**

#### **Browser Automation Tests:**
```
EXPLICIT PERMISSION REQUIRED: "Should I test browser automation?"

# Only if user approves:
# Start Chrome with debug port
# Test supplier authentication
# Validate scraping functionality
```

#### **Full Workflow Tests:**
```
EXPLICIT PERMISSION REQUIRED: "Should I run the complete workflow?"

# Only if user instructs:
python run_custom_poundwholesale.py
```

---

## 🎯 TASK SUCCESS CRITERIA

### **TSC1: Code Modification Task Success**
- ✅ **Specific Problem Resolved**: The exact issue identified has been fixed
- ✅ **No New Errors Introduced**: No AttributeError, TypeError, NameError exceptions
- ✅ **Integration Points Intact**: All component interactions continue working
- ✅ **Method Signatures Preserved**: All calling code remains compatible
- ✅ **Surgical Precision Applied**: Only minimal necessary changes made

### **TSC2: System Integrity Task Success**  
- ✅ **Performance Maintained**: 240x cache performance and other optimizations preserved
- ✅ **Resume Functionality Intact**: 100% resume success rate maintained
- ✅ **State Consistency Preserved**: Unified state management working correctly
- ✅ **Filter Invariants Maintained**: Mathematical relationships preserved

### **TSC3: Security Task Success**
- ✅ **No Unauthorized Changes**: No security modifications without user approval
- ✅ **API Key Safety**: No hardcoded secrets or compromised key management
- ✅ **Authentication Integrity**: Session management and auth logic preserved
- ✅ **Data Protection Maintained**: Atomic file operations and corruption prevention intact

### **TSC4: Testing Task Success**
- ✅ **Static Tests Pass**: All code compiles and imports successfully
- ✅ **Integration Verified**: Component interactions validated (if user approves testing)
- ✅ **No Regression Detected**: All existing functionality continues working
- ✅ **Documentation Updated**: Changes documented with verification results

---

## 📋 TASK PRIORITY MATRIX

### **Priority 1: CRITICAL (Immediate Action Required)**
- **State Manager Attribute Errors**: Fix AttributeError exceptions in state management
- **Method Name Mismatches**: Resolve incorrect method calls causing NameError
- **Signature Incompatibilities**: Fix TypeError from method signature mismatches
- **Resume Functionality Failures**: Address state corruption preventing system resume

### **Priority 2: HIGH (Required for System Operation)**  
- **Integration Point Failures**: Fix component communication breakdowns
- **Configuration Loading Issues**: Resolve config parsing and validation problems
- **Error Recovery Failures**: Fix automatic error handling and recovery mechanisms
- **Performance Degradation**: Address issues affecting system efficiency

### **Priority 3: MEDIUM (System Optimization)**
- **Memory Management Optimization**: Improve memory usage patterns
- **Cache Performance Enhancement**: Optimize caching mechanisms
- **Browser Stability Improvement**: Enhance browser restart and management
- **Logging and Monitoring Enhancement**: Improve system observability

### **Priority 4: LOW (Nice to Have)**
- **Code Documentation**: Update code comments and documentation
- **Code Cleanup**: Remove unused code and optimize structure
- **Test Coverage Expansion**: Add additional test cases
- **Configuration Simplification**: Streamline configuration options

---

**Document Version**: 1.0  
**Last Updated**: 2025-08-15  
**Task Authority**: Surgical Code Modification Rules + User Approval Protocol  
**Enforcement Level**: MANDATORY - Task violations require immediate cessation