# 12. Supplier Integration Guide

This section contains documentation for Supplier Integration Guide.

## Contents

- [12.1. Supplier Configuration](./12.1. Supplier Configuration/README.md)
- [12.2. Script Generation](./12.2. Script Generation/README.md)
- [12.3. Integration Testing](./12.3. Integration Testing/README.md)

## Automated Onboarding

For automated supplier onboarding, use the **supplier-onboarding** skill located at `.claude/skills/supplier-onboarding/SKILL.md`. This skill provides a 7-step guided workflow that includes:

1. Data preprocessing and validation
2. Information gathering
3. Configuration file preparation
4. Wizard invocation (`utils/supplier_onboarding_wizard.py`)
5. File validation
6. Pre-run verification
7. Test/Main run decision

## Naming Conventions

The system uses three distinct naming forms depending on context:

| Context | Form | Example |
|---------|------|---------|
| Config files | Dot-form | `supplier.com.json` |
| System config supplier_name | Dot-form | `"supplier_name": "supplier.com"` |
| Runner scripts | Hyphen-form | `run_custom_supplier-com.py` |
| Tool directories | Hyphen-form | `tools/supplier-com/` |
| Workflow keys | Underscore-form | `supplier_workflow` |
| State files | Underscore-form | `supplier_com_processing_state.json` |

*Generated on 2025-12-03T04:40:00.457Z*
