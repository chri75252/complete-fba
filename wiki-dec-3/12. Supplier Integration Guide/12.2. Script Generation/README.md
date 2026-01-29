# 12.2. Script Generation

This section contains documentation for Script Generation.

## Automated Script Generation

The preferred method for generating supplier scripts is using the **Supplier Onboarding Wizard**:

```bash
python utils/supplier_onboarding_wizard.py \
  --domain "supplier.com" \
  --categories-source "config/supplier_categories.json" \
  --selectors-source "config/supplier_configs/supplier.com.json" \
  --workflow-key "supplier_workflow" \
  --mode generate \
  --authentication-required false
```

The wizard generates:
- Runner script: `run_custom_{supplier-id}.py`
- Categories config: `config/{workflow_key}_categories.json`
- Workflow registration in `config/system_config.json`
- Authentication helper (if required): `tools/{supplier-id}/supplier_authentication_service.py`

For the full guided workflow, use the **supplier-onboarding** skill at `.claude/skills/supplier-onboarding/SKILL.md`.

## Contents

- [12.2.1. Ai Powered Discovery](./12.2.1. Ai Powered Discovery/README.md)
- [12.2.2. Template Generation](./12.2.2. Template Generation/README.md)
- [12.2.3. Validation Testing](./12.2.3. Validation Testing/README.md)

*Generated on 2025-12-03T04:40:00.488Z*
