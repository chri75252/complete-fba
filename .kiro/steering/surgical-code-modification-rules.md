# Surgical Code Modification Rules - MANDATORY COMPLIANCE
## Critical Guidelines for Code Changes in Amazon FBA Agent System

**VIOLATION OF THESE RULES WILL RESULT IN IMMEDIATE TASK TERMINATION**

---

## 🚨 RULE 1: SURGICAL PRECISION ONLY

### ✅ ALLOWED:
- **Minimal line-by-line changes** to fix specific issues
- **Single-line modifications** when explicitly requested
- **Adding specific methods** when explicitly requested with exact specifications
- **Fixing exact enumeration patterns** (e.g., `enumerate(..., 1)` to `enumerate(..., 0)`)

### ❌ FORBIDDEN:
- **Wholesale method replacements** unless explicitly requested
- **Changing method signatures** without explicit user approval
- **Modifying working code** that wasn't part of the original problem
- **"Improving" code** that wasn't broken
- **Adding features** not specifically requested

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