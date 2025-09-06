# Surgical Code Modification Rules - MANDATORY COMPLIANCE
## Critical Guidelines for Code Changes in Amazon FBA Agent System

**VIOLATION OF THESE RULES WILL RESULT IN IMMEDIATE TASK TERMINATION**

---

## 🚨 RULE 0: LOGIC-FIRST DEBUGGING MANDATE (ANTI-TESTING-THEATER)

### **🚨 FUNDAMENTAL ASSUMPTION:**
- **Existing architecture likely has necessary data and components**
- **Focus on logic interpretation gaps, NOT missing implementations**
- **Evidence requirement: Architectural changes must be justified by proof that logic fixes won't work**

### **⚠️ MANDATORY INVESTIGATION SEQUENCE - EXECUTE IN ORDER:**

1. **📊 DATA FLOW TRACE**: What data exists and flows correctly?
   - ✅ Read logs to identify where system shows success (data populated, operations completed)
   - ✅ Follow successful data through the system step-by-step
   - ✅ Document what data is available at each stage

2. **🔍 DECISION POINT ANALYSIS**: Where does correct data get ignored/misclassified?
   - ✅ Find the exact transition from "data exists" to "system fails"
   - ✅ Identify the specific conditional logic or workflow routing
   - ✅ Focus on if/else branches, classification rules, workflow decisions

3. **🎯 LOGIC BRANCH REVIEW**: What conditions cause wrong paths?
   - ✅ Examine the logic that determines system behavior
   - ✅ Look for classification errors, misinterpretation of data
   - ✅ Check workflow routing logic and decision trees

4. **🔧 MINIMAL FIX IDENTIFICATION**: What's the smallest logic change that fixes the flow?
   - ✅ Prefer single-line conditional changes
   - ✅ Focus on interpretation logic, not data generation
   - ✅ Use existing data structures and workflows

5. **🏗️ ARCHITECTURE CHANGES**: Only if steps 1-4 prove insufficient
   - ✅ Must provide concrete evidence that logic fixes are impossible
   - ✅ Document why existing architecture cannot support the fix

### **🚨 INVESTIGATION RED FLAGS - STOP AND RECONSIDER:**
- ❌ **Proposing callback systems** → Check if existing communication just needs logic fixes
- ❌ **Suggesting new components** → Verify existing components don't already have the data
- ❌ **Building integration layers** → Confirm the integration isn't just a conditional logic error
- ❌ **Tests pass but production fails** → Look for logic interpretation, not implementation gaps
- ❌ **"Missing implementation" conclusions** → Verify implementation doesn't exist but is bypassed

### **🎯 EVIDENCE-BASED DEBUGGING:**
- ✅ "The system generates correct data but makes wrong decisions - trace the decision logic"
- ✅ "Assume all components work, find where good data gets misclassified"
- ✅ "Focus on workflow routing and conditional logic, not component integration"
- ✅ "Look for single-line logic errors before proposing architectural changes"

## 🚨 RULE 1: SURGICAL PRECISION ONLY

### ✅ ALLOWED:
- **Minimal line-by-line changes** to fix specific issues
- **Single-line conditional logic fixes** when data exists but is misinterpreted
- **Classification logic corrections** when existing data gets dropped
- **Workflow routing fixes** when system takes wrong path with correct data
- **Single-line modifications** when explicitly requested
- **Adding specific methods** when explicitly requested with exact specifications
- **Fixing exact enumeration patterns** (e.g., `enumerate(..., 1)` to `enumerate(..., 0)`)

### ❌ FORBIDDEN:
- **Wholesale method replacements** unless explicitly requested
- **Adding callback systems** without proving existing communication is broken
- **Creating new components** without verifying existing ones don't have the data
- **Changing method signatures** without explicit user approval
- **Modifying working code** that wasn't part of the original problem
- **"Improving" code** that wasn't broken
- **Adding features** not specifically requested
- **Building integration layers** for problems that are actually logic interpretation errors

---

## 🚨 RULE 2: MANDATORY PRE-CHANGE ANALYSIS

### BEFORE MAKING ANY CODE CHANGE:

1. **READ THE ORIGINAL CODE FIRST**
   ```
   - Use readFile to examine the current implementation
   - Understand what the code currently does
   - Identify the EXACT problem location
   ```

2. **VERIFY THE PROBLEM EXISTS**
   ```
   - Confirm the issue is actually present in the code
   - Check if the problem has already been fixed
   - Ensure you understand the root cause
   ```

3. **IDENTIFY MINIMAL CHANGE REQUIRED**
   ```
   - Determine the smallest possible fix
   - Avoid changing anything beyond the specific issue
   - Preserve all existing functionality
   ```

4. **CHECK FOR DEPENDENCIES**
   ```
   - Search for all callers of the method/function
   - Verify attribute names and method signatures
   - Ensure changes won't break existing integrations
   ```

---

## 🚨 RULE 3: ATTRIBUTE AND METHOD NAME VERIFICATION

### MANDATORY CHECKS BEFORE USING ANY ATTRIBUTE:

1. **Search for attribute initialization**
   ```python
   # REQUIRED: Search for patterns like:
   self.scraper = 
   self.supplier_scraper = 
   self.web_scraper =
   ```

2. **Verify attribute usage patterns**
   ```python
   # REQUIRED: Search for existing usage:
   self.scraper.method_name
   self.supplier_scraper.method_name
   ```

3. **Check method availability**
   ```python
   # REQUIRED: Use get_symbols_overview or find_symbol to verify:
   - Method exists in the target class
   - Method signature matches expected parameters
   - Method name is spelled correctly
   ```

### ❌ NEVER ASSUME:
- Attribute names without verification
- Method names without checking the actual class
- Method signatures without reading the implementation

---

## 🚨 RULE 4: METHOD SIGNATURE PRESERVATION

### ✅ WHEN MODIFYING EXISTING METHODS:

1. **PRESERVE ORIGINAL SIGNATURE**
   ```python
   # If original method has:
   def method(self, param1, param2, param3):
   
   # Your modification MUST maintain:
   def method(self, param1, param2, param3):
   ```

2. **CHECK ALL CALLERS FIRST**
   ```python
   # REQUIRED: Search for all calls to the method:
   method_name(arg1, arg2, arg3)
   # Ensure your changes won't break these calls
   ```

3. **ONLY CHANGE SIGNATURE IF EXPLICITLY REQUESTED**
   ```
   - User must specifically request signature changes
   - All callers must be identified and updated
   - Changes must be approved before implementation
   ```

---

## 🚨 RULE 5: ENUMERATION AND INDEX FIXES

### ✅ CORRECT APPROACH FOR ENUMERATION FIXES:

1. **IDENTIFY EXACT PATTERNS**
   ```python
   # Search for specific patterns:
   enumerate(items, 1)  # Should be enumerate(items, 0)
   ```

2. **MAKE MINIMAL CHANGES**
   ```python
   # ONLY change the enumeration start value:
   # BEFORE:
   for i, item in enumerate(items, 1):
   
   # AFTER:
   for i, item in enumerate(items, 0):
   ```

3. **UPDATE RELATED CALCULATIONS**
   ```python
   # If enumeration changes, update dependent calculations:
   # BEFORE:
   index = (batch_num - 1) * size + item_index
   
   # AFTER (if enumerate starts from 0):
   index = batch_num * size + item_index
   ```

### ❌ FORBIDDEN:
- Rewriting entire methods for enumeration fixes
- Changing unrelated code in the same method
- Modifying method signatures during enumeration fixes

---

## 🚨 RULE 6: ERROR HANDLING PROTOCOL

### WHEN ENCOUNTERING ERRORS:

1. **ANALYZE THE ERROR MESSAGE**
   ```
   - Read the exact error message
   - Identify the specific line causing the issue
   - Understand the root cause before fixing
   ```

2. **MAKE TARGETED FIXES**
   ```
   - Fix ONLY the specific issue mentioned in the error
   - Do not "improve" surrounding code
   - Preserve all existing functionality
   ```

3. **VERIFY THE FIX**
   ```
   - Ensure the fix addresses the exact error
   - Check that no new issues are introduced
   - Confirm all existing functionality remains intact
   ```

### ❌ NEVER:
- Make multiple unrelated changes when fixing one error
- Assume what other improvements might be needed
- Change working code while fixing broken code

---

## 🚨 RULE 7: MANDATORY VERIFICATION STEPS

### BEFORE SUBMITTING ANY CODE CHANGE:

1. **VERIFY ATTRIBUTE NAMES**
   ```bash
   # REQUIRED: Search for attribute initialization
   grep -n "self\..*scraper.*=" file.py
   ```

2. **VERIFY METHOD NAMES**
   ```bash
   # REQUIRED: Check method exists in target class
   grep -n "def method_name" target_class.py
   ```

3. **VERIFY METHOD CALLS**
   ```bash
   # REQUIRED: Find all existing calls to modified methods
   grep -n "method_name(" *.py
   ```

4. **CHECK IMPORT STATEMENTS**
   ```python
   # REQUIRED: Verify all imports are correct
   # Check that classes and methods are imported properly
   ```

---

## 🚨 RULE 8: FORBIDDEN MODIFICATIONS

### ❌ ABSOLUTELY NEVER CHANGE:

1. **Working method signatures** without explicit user request
2. **Attribute names** that are already correctly used elsewhere
3. **Import statements** unless specifically broken
4. **Class initialization** unless specifically requested
5. **Error handling logic** unless it's the specific problem
6. **Configuration loading** unless it's the specific problem
7. **File paths and naming** unless specifically requested

---

## 🚨 RULE 9: COMMUNICATION REQUIREMENTS

### BEFORE MAKING CHANGES:

1. **EXPLAIN WHAT YOU FOUND**
   ```
   "I found the issue at line X in file Y"
   "The problem is: [specific issue]"
   "The minimal fix required is: [exact change]"
   ```

2. **CONFIRM THE APPROACH**
   ```
   "I will change only line X from A to B"
   "This will preserve all existing functionality"
   "No other changes are needed"
   ```

3. **AFTER MAKING CHANGES**
   ```
   "I made the following specific change: [exact change]"
   "All other functionality remains unchanged"
   "The fix addresses: [specific error/issue]"
   ```

---

## 🚨 RULE 10: VALIDATION CHECKLIST

### MANDATORY CHECKS BEFORE ANY CODE MODIFICATION:

- [ ] **Read the original code** to understand current implementation
- [ ] **Identify the exact problem** location and cause
- [ ] **Verify attribute names** by searching for their initialization
- [ ] **Verify method names** by checking the target class
- [ ] **Check method signatures** match expected parameters
- [ ] **Search for all callers** of methods being modified
- [ ] **Confirm minimal change** approach will solve the problem
- [ ] **Ensure no breaking changes** to existing functionality

### IF ANY CHECKBOX IS UNCHECKED: DO NOT PROCEED WITH CHANGES

---

## 🚨 RULE 11: ESCALATION PROTOCOL

### WHEN IN DOUBT:

1. **STOP IMMEDIATELY**
2. **ASK THE USER FOR CLARIFICATION**
   ```
   "I found the issue but need clarification on the approach"
   "Should I change X or Y to fix this?"
   "I want to confirm this change won't break Z"
   ```
3. **WAIT FOR EXPLICIT APPROVAL** before proceeding

### ❌ NEVER:
- Guess what the user wants
- Make assumptions about the "best" approach
- Implement changes without understanding the full impact

---

## 🚨 ENFORCEMENT

**VIOLATION OF THESE RULES WILL RESULT IN:**
1. Immediate task termination
2. Requirement to revert all changes
3. Mandatory re-analysis of the problem
4. User approval required for any further modifications

**THESE RULES ARE NON-NEGOTIABLE AND MUST BE FOLLOWED WITHOUT EXCEPTION**

---

## ✅ SUMMARY OF CORRECT APPROACH

1. **READ** the existing code first
2. **UNDERSTAND** the exact problem
3. **VERIFY** all attribute and method names
4. **MAKE MINIMAL** surgical changes only
5. **PRESERVE** all existing functionality
6. **TEST** that the specific issue is resolved
7. **COMMUNICATE** clearly about what was changed and why

**REMEMBER: THE GOAL IS TO FIX SPECIFIC ISSUES, NOT TO REWRITE OR IMPROVE CODE**