# Hooks - Amazon FBA Agent System v3.8+

## 🚨 CRITICAL SURGICAL IMPLEMENTATION HOOKS FRAMEWORK

### **🔒 SECURITY HOOKS - USER APPROVAL REQUIRED**

**⚠️ MANDATORY: Security-related hooks require explicit user instruction**

#### **Security Modification Hook (USER_APPROVAL_REQUIRED)**
```yaml
hook_trigger: security_change_detected
severity: CRITICAL
action: require_user_approval

conditions:
  - API key modification detected
  - Authentication logic change detected  
  - Environment variable modification detected
  - Security configuration change detected
  - Permission change detected

user_approval_prompt:
  "🚨 SECURITY CHANGE DETECTED 🚨
  
  Change Type: [SECURITY_CHANGE_TYPE]
  File: [AFFECTED_FILE]
  Description: [CHANGE_DESCRIPTION]
  
  This change involves security-sensitive code and requires your explicit approval.
  Should I proceed with this change, or would you prefer to review it first?"

fallback_action: halt_execution
```

---

### **🧪 TESTING HOOKS - USER INSTRUCTION REQUIRED**  

**⚠️ MANDATORY: System testing hooks require explicit user permission**

#### **Live System Testing Hook (USER_INSTRUCTION_REQUIRED)**
```yaml
hook_trigger: system_execution_requested
severity: HIGH
action: require_user_instruction

conditions:
  - Full workflow execution requested (run_custom_poundwholesale.py)
  - Browser automation testing requested
  - Live website access required
  - State file modification required
  - API calls to external services

user_instruction_prompt:
  "🧪 SYSTEM TESTING REQUESTED 🧪
  
  Test Type: [TEST_TYPE]
  Command: [PROPOSED_COMMAND]
  Impact: [SYSTEM_IMPACT_DESCRIPTION]
  
  Should I execute this system test, or would you prefer to run it yourself?"

allowed_static_testing:
  - python -m py_compile [file]
  - python -c "import [module]"
  - grep -n "def\|class" [file]
  - python -m ast [file]

fallback_action: suggest_static_alternative
```

---

### **🔧 SURGICAL CODE MODIFICATION HOOKS**

**⚠️ CRITICAL: All code changes must follow surgical precision rules**

#### **Pre-Modification Verification Hook (MANDATORY)**
```yaml
hook_trigger: code_modification_initiated
severity: CRITICAL
action: enforce_verification_checklist

mandatory_verification_steps:
  1. original_code_analysis:
     - read_current_implementation: true
     - identify_exact_problem: true
     - verify_problem_exists: true
     
  2. method_existence_verification:
     command: "grep -n 'def target_method' target_file.py"
     requirement: method_must_exist_before_calling
     
  3. attribute_existence_verification:
     command: "grep -n 'self\\.target_attribute.*=' target_file.py"
     requirement: attribute_must_exist_before_accessing
     
  4. method_signature_verification:
     command: "grep -A 5 'def target_method' target_file.py"
     requirement: signature_must_match_calling_code
     
  5. cross_reference_analysis:
     command: "grep -rn 'target_element' . --include='*.py'"
     requirement: all_references_must_be_identified

verification_failure_action: halt_modification
verification_success_action: proceed_with_backup_creation
```

#### **Method Signature Preservation Hook (ENFORCE)**
```yaml
hook_trigger: method_signature_change_detected
severity: CRITICAL
action: enforce_signature_preservation

protected_patterns:
  - def scrape_products_from_url(self, url, category_name=None)
  - def update_progress_atomic(self, data)
  - def get_resume_point(self)
  - def validate_invariant_compliance(self)
  - def save_state_atomic(self, data, filepath)

change_policy: forbidden_without_explicit_user_approval
user_approval_required: true

approval_prompt:
  "🚨 METHOD SIGNATURE CHANGE DETECTED 🚨
  
  Method: [METHOD_NAME]
  Current Signature: [CURRENT_SIGNATURE]
  Proposed Signature: [PROPOSED_SIGNATURE]
  
  This change will affect all calling code. Have you verified all callers
  and approved this signature change?"

fallback_action: preserve_original_signature
```

#### **Attribute Name Consistency Hook (ENFORCE)**
```yaml
hook_trigger: attribute_access_detected
severity: HIGH
action: enforce_attribute_verification

critical_attributes:
  PassiveExtractionWorkflow:
    - supplier_scraper  # NOT scraper
    - amazon_extractor  # NOT extractor  
    - state_manager     # NOT state
    - browser_manager   # NOT browser
    
  FixedEnhancedStateManager:
    - supplier_extraction_progress  # NOT progress
    - system_progression           # NOT system_state
    - _state_lock                 # NOT lock

verification_command: "grep -n 'self\\.{attribute}.*=' {class_file}.py"
requirement: attribute_must_exist_in_init

violation_action: 
  - log_error: "ATTRIBUTE_ERROR_PREVENTION: {attribute} not found in {class}"
  - suggest_correction: "Did you mean: {suggested_attribute}?"
  - halt_execution: true
```

---

### **📊 PERFORMANCE MONITORING HOOKS**

#### **Performance Degradation Detection Hook**
```yaml
hook_trigger: performance_change_detected
severity: MEDIUM
action: preserve_optimization_patterns

protected_performance_patterns:
  - cache_optimization: 240x_performance_improvement
  - memory_management: 99percent_reduction_in_clearing
  - resume_success_rate: 100percent_reliability
  - session_duration: 18plus_hours_capability

monitoring_commands:
  - cache_performance: "grep -n 'hash.*lookup' utils/hash_lookup_optimizer.py"
  - memory_clearing: "grep -n 'smart.*clear' utils/enhanced_state_manager.py"
  - resume_validation: "grep -n 'validate_resume_point' utils/fixed_enhanced_state_manager.py"

performance_violation_action:
  - alert_user: "Performance optimization pattern at risk"
  - require_justification: "Explain why this change won't degrade performance"
  - suggest_alternative: "Consider alternative that preserves optimization"
```

---

### **🔄 INTEGRATION POINT VALIDATION HOOKS**

#### **Component Integration Verification Hook (ENFORCE)**
```yaml
hook_trigger: component_integration_change
severity: HIGH
action: enforce_integration_integrity

critical_integration_patterns:
  - workflow_to_scraper: "workflow.supplier_scraper.scrape_products_from_url()"
  - workflow_to_amazon: "workflow.amazon_extractor.extract_product_data()"
  - workflow_to_state: "workflow.state_manager.update_progress_atomic()"
  - state_to_files: "state_manager.save_with_atomic_write()"

validation_steps:
  1. verify_calling_pattern_exists:
     command: "grep -n '{pattern}' tools/passive_extraction_workflow_latest.py"
     
  2. verify_target_method_exists:
     command: "grep -n 'def {method_name}' {target_file}.py"
     
  3. verify_signature_compatibility:
     command: "grep -A 5 'def {method_name}' {target_file}.py"

integration_failure_action:
  - log_critical: "INTEGRATION_POINT_BROKEN: {integration_pattern}"
  - halt_modification: true
  - suggest_fix: "Verify {target_method} exists in {target_class}"
```

---

### **🛡️ ERROR PREVENTION HOOKS**

#### **AttributeError Prevention Hook (ENFORCE)**
```yaml
hook_trigger: attribute_access_attempt
severity: HIGH
action: prevent_attributeerror

prevention_checks:
  1. attribute_initialization_check:
     pattern: "self\\.{attribute_name}"
     verification: "grep -n 'self\\.{attribute_name}.*=' {class_file}.py"
     requirement: "Attribute must be initialized in __init__"
     
  2. attribute_usage_pattern_check:
     pattern: "\\b{object_name}\\.{attribute_name}\\b"
     verification: "grep -A 20 '__init__' {class_file}.py | grep 'self\\.{attribute_name}'"
     requirement: "Attribute must exist before access"

error_prevention_action:
  - pre_access_verification: true
  - suggest_correct_attribute: true
  - halt_if_not_found: true

example_prevention:
  wrong_access: "self.scraper.method()"
  verification_check: "grep -n 'self\\.scraper.*=' PassiveExtractionWorkflow"
  correct_access: "self.supplier_scraper.method()"
```

#### **TypeError Prevention Hook (ENFORCE)**
```yaml
hook_trigger: method_call_attempt
severity: HIGH
action: prevent_typeerror

prevention_checks:
  1. method_existence_check:
     pattern: "{object}\\.{method_name}\\("
     verification: "grep -n 'def {method_name}' {target_class}.py"
     requirement: "Method must exist before calling"
     
  2. signature_compatibility_check:
     command: "grep -A 5 'def {method_name}' {target_class}.py"
     requirement: "Method signature must match calling pattern"

error_prevention_action:
  - verify_method_exists: true
  - check_parameter_count: true
  - validate_parameter_types: true
  - halt_if_incompatible: true

example_prevention:
  wrong_call: "scraper.extract_products_from_category(url)"
  verification_check: "grep -n 'def extract_products_from_category' configurable_supplier_scraper.py"
  correct_call: "scraper.scrape_products_from_url(url)"
```

---

### **📁 FILE CHANGE DETECTION HOOKS**

#### **Cascading Update Hook (AUTO-TRIGGER)**
```yaml
hook_trigger: file_modification_detected
severity: MEDIUM
action: trigger_cascading_updates

monitored_files:
  - tools/passive_extraction_workflow_latest.py
  - utils/fixed_enhanced_state_manager.py
  - tools/configurable_supplier_scraper.py
  - tools/amazon_playwright_extractor.py
  - config/system_config.json

cascading_update_actions:
  1. documentation_sync:
     - update_readme: "Update README.md with new functionality"
     - update_architecture_docs: "Sync architecture diagrams"
     - update_troubleshooting: "Update troubleshooting guides"
     
  2. configuration_sync:
     - validate_config_compatibility: "Check config format compatibility"
     - update_config_examples: "Sync configuration examples"
     - validate_environment_variables: "Check .env.example consistency"
     
  3. integration_validation:
     - verify_import_statements: "Check all imports still valid"
     - validate_component_communication: "Test integration points"
     - check_method_signatures: "Verify calling code compatibility"

cascade_failure_action: alert_user_of_inconsistency
```

#### **Backup Creation Hook (AUTO-TRIGGER)**
```yaml
hook_trigger: code_modification_initiated
severity: HIGH
action: create_backup_automatically

backup_strategy:
  1. pre_modification_backup:
     command: "mkdir -p backup/hook_$(date +%Y%m%d_%H%M%S)"
     action: "cp {affected_files} backup/hook_$(date +%Y%m%d_%H%M%S)/"
     
  2. backup_verification:
     command: "ls -la backup/hook_$(date +%Y%m%d_%H%M%S)/"
     requirement: "Backup must be created successfully"
     
  3. backup_restoration_info:
     log_message: "Backup created at: backup/hook_$(date +%Y%m%d_%H%M%S)/"
     restoration_command: "cp backup/hook_$(date +%Y%m%d_%H%M%S)/* ."

backup_failure_action: halt_modification_immediately
```

---

### **🎯 SERENA MCP INTEGRATION HOOKS**

#### **Context Switching Hook (AUTO-OPTIMIZE)**
```yaml
hook_trigger: task_type_detected
severity: LOW
action: optimize_serena_context

context_optimization_rules:
  analysis_tasks:
    context: ide-assistant
    mode: interactive
    safety: read-only
    triggers:
      - code_structure_analysis_requested
      - method_discovery_needed
      - usage_pattern_investigation
      - dependency_mapping_required
      
  implementation_tasks:
    context: ide-assistant  
    mode: editing
    safety: backup_before_changes
    triggers:
      - code_modification_requested
      - surgical_fix_implementation
      - integration_point_repair
      - method_signature_correction
      
  validation_tasks:
    context: ide-assistant
    mode: interactive
    safety: read-only
    triggers:
      - post_modification_verification
      - integration_point_testing
      - error_detection_scanning
      - performance_validation

context_switch_action: automatic_optimization
user_notification: optional
```

#### **Serena Safety Configuration Hook (ENFORCE)**
```yaml
hook_trigger: serena_operation_initiated
severity: HIGH
action: enforce_safety_configuration

safety_configurations:
  analysis_phase:
    read_only: true
    backup_enabled: false
    modification_allowed: false
    analysis_only: true
    
  implementation_phase:
    read_only: false
    backup_enabled: true
    verification_required: true
    minimal_changes_only: true
    
  verification_phase:
    read_only: true
    backup_enabled: false
    validation_only: true
    error_detection_enabled: true

safety_violation_action:
  - log_violation: "SERENA_SAFETY_VIOLATION: {violation_type}"
  - enforce_correct_configuration: true
  - require_user_confirmation: true
```

---

### **📋 HOOK EXECUTION MONITORING**

#### **Hook Performance Monitoring**
```yaml
hook_monitoring:
  execution_time_limit: 10_seconds
  memory_usage_limit: 100MB
  failure_retry_limit: 3
  
  performance_metrics:
    - hook_execution_time
    - verification_success_rate
    - error_prevention_effectiveness
    - user_approval_response_time
    
  monitoring_actions:
    - log_hook_performance: true
    - alert_on_slow_hooks: true
    - disable_failing_hooks: true
    - report_hook_statistics: true
```

#### **Hook Failure Recovery**
```yaml
hook_failure_recovery:
  critical_hook_failure:
    action: halt_system_immediately
    user_notification: required
    fallback_action: manual_intervention_required
    
  non_critical_hook_failure:
    action: continue_with_warning
    user_notification: optional
    fallback_action: disable_failing_hook
    
  hook_cascade_failure:
    action: rollback_to_safe_state
    user_notification: immediate
    fallback_action: restore_from_backup
```

---

## 🎯 HOOK SUCCESS CRITERIA

### **HSC1: Security Hook Success**
- ✅ No unauthorized security modifications
- ✅ User approval obtained for all security changes
- ✅ API key safety maintained
- ✅ Authentication integrity preserved

### **HSC2: Code Quality Hook Success**  
- ✅ All AttributeError exceptions prevented
- ✅ All TypeError exceptions prevented
- ✅ Method signatures preserved correctly
- ✅ Integration points validated successfully

### **HSC3: Performance Hook Success**
- ✅ 240x cache performance maintained
- ✅ 99% memory clearing reduction preserved
- ✅ 100% resume success rate maintained
- ✅ 18+ hour operation capability intact

### **HSC4: Testing Hook Success**
- ✅ User approval obtained for system testing
- ✅ Static testing executed successfully
- ✅ Integration validation completed
- ✅ No regression detected

---

**Document Version**: 1.0  
**Last Updated**: 2025-08-15  
**Hook Authority**: Surgical Code Modification Rules + Security Protocols  
**Execution Level**: AUTOMATIC with USER_APPROVAL override capabilities