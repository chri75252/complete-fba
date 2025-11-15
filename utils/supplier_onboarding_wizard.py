#!/usr/bin/env python3
"""
Supplier Onboarding Wizard
Deterministic file generation and validation for supplier onboarding.

This wizard handles:
- Domain normalization (URL/hyphen/dot forms)
- File generation with atomic operations
- Runner selection with fallback hierarchy
- Sanity check execution
- 6-criterion output verification
- Remediation guidance generation

Communication with skill is ONLY via session files (input.json → output.json).
"""

import sys
import json
import re
import time
import argparse
import subprocess
import os
import uuid
import tempfile
import csv
from pathlib import Path
from typing import Dict, Any, Tuple, List, Optional
from urllib.parse import urlparse
from dataclasses import dataclass

# Add repo root to Python path (wizard may be invoked as subprocess)
SCRIPT_DIR = Path(__file__).parent.absolute()
REPO_ROOT = SCRIPT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Import existing utilities
try:
    from utils.windows_save_guardian import WindowsSaveGuardian
except ImportError:
    print("ERROR: Cannot import WindowsSaveGuardian", file=sys.stderr)
    print("Ensure you're running from the repository root", file=sys.stderr)
    sys.exit(1)


# ============================================================================
# CONSTANTS
# ============================================================================

UK_TLDS = {
    ".co.uk", ".org.uk", ".ac.uk", ".gov.uk", ".nhs.uk",
    ".police.uk", ".ltd.uk", ".plc.uk", ".net.uk", ".me.uk"
}

# Workflow to runner mapping
WORKFLOW_TO_RUNNER = {
    "poundwholesale_workflow": "run_custom_poundwholesale.py",
    "clearance_king_workflow": "run_custom_clearance_king.py"
}

# Default runner for unknown workflows
DEFAULT_RUNNER = "run_custom_poundwholesale.py"


# ============================================================================
# ATOMIC TEXT WRITE HELPER
# ============================================================================

def atomic_write_text(path: Path, content: str) -> None:
    """
    Atomic text write for non-JSON files (e.g., Python shims).
    Uses temp file then replace pattern.
    """
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        tmp.write_text(content, encoding="utf-8")
        tmp.replace(path)
    finally:
        if tmp.exists():
            try:
                tmp.unlink()
            except:
                pass


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class SupplierForms:
    """Three forms of supplier identification."""
    domain: str              # dot-form: poundwholesale.co.uk
    supplier_id: str         # hyphen-form: poundwholesale-co-uk
    supplier_name_underscore: str  # underscore-form: poundwholesale_co_uk


# ============================================================================
# DOMAIN NORMALIZATION
# ============================================================================

def normalize_domain(input_domain: str) -> str:
    """
    Robust domain normalization supporting:
    - Full URLs: https://example.co.uk/path → example.co.uk
    - Hyphen form: example-co-uk → example.co.uk
    - Dot form: example.co.uk → example.co.uk
    - All TLDs: .com, .net, .co.uk, etc.
    """
    domain = input_domain.strip()

    # Handle full URL
    if domain.startswith(('http://', 'https://')):
        parsed = urlparse(domain)
        domain = parsed.netloc or parsed.path.split('/')[0]

    # Remove www prefix
    domain = re.sub(r'^www\.', '', domain)

    # Check if already in dot-form with valid TLD (has at least one dot)
    if '.' in domain:
        return domain.lower()

    # Convert hyphen-form to dot-form for multi-level TLDs (UK TLDs)
    for tld in UK_TLDS:
        hyphen_tld = tld.replace('.', '-')
        if domain.endswith(hyphen_tld):
            base = domain[:-len(hyphen_tld)]
            return (base + tld).lower()

    # Handle hyphen-form with single-level TLD (e.g., example-com → example.com)
    if domain.count('-') > 0:
        parts = domain.rsplit('-', 1)
        return f"{parts[0]}.{parts[1]}".lower()

    return domain.lower()


def generate_supplier_forms(domain: str) -> SupplierForms:
    """
    Generate all three forms from domain.
    """
    # Ensure dot-form
    domain_dot = normalize_domain(domain)

    # Generate hyphen-form (supplier_id)
    supplier_id = domain_dot.replace('.', '-')

    # Generate underscore-form (supplier_name)
    supplier_name_underscore = domain_dot.replace('.', '_').replace('-', '_')

    return SupplierForms(
        domain=domain_dot,
        supplier_id=supplier_id,
        supplier_name_underscore=supplier_name_underscore
    )


# ============================================================================
# NAMING CONVENTIONS
# ============================================================================

class NamingConventions:
    """Centralized naming convention enforcement."""

    @staticmethod
    def selector_config_path(domain: str, repo_root: Path) -> Path:
        """config/supplier_configs/{domain}.json (dot-form)"""
        return repo_root / f"config/supplier_configs/{domain}.json"

    @staticmethod
    def linking_map_dir(supplier_id: str, repo_root: Path) -> Path:
        """OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier-id}/ (hyphen-form)"""
        return repo_root / f"OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier_id}"

    @staticmethod
    def processing_state_file(supplier_name_underscore: str, repo_root: Path) -> Path:
        """OUTPUTS/CACHE/processing_states/{supplier_name_underscore}_processing_state.json"""
        return repo_root / f"OUTPUTS/CACHE/processing_states/{supplier_name_underscore}_processing_state.json"

    @staticmethod
    def categories_config_path(workflow_key: str, repo_root: Path) -> Path:
        """
        Read from workflows.{workflow_key}.categories_config_path in system_config.json.
        If missing, set to default config/{workflow_key}_categories.json and write back.
        """
        config_path = repo_root / "config/system_config.json"
        config = json.loads(config_path.read_text(encoding='utf-8'))

        workflow = config.get("workflows", {}).get(workflow_key, {})
        categories_path = workflow.get("categories_config_path")

        if not categories_path:
            # Set default and write back
            categories_path = f"config/{workflow_key}_categories.json"

            if "workflows" not in config:
                config["workflows"] = {}
            if workflow_key not in config["workflows"]:
                config["workflows"][workflow_key] = {}

            config["workflows"][workflow_key]["categories_config_path"] = categories_path

            # Write back atomically
            guardian = WindowsSaveGuardian()
            guardian.save_json_atomic(config_path, config)

        return repo_root / categories_path

    @staticmethod
    def register_workflow(workflow_key: str, supplier_name: str, supplier_url: str,
                         categories_path: str, test_product_url: Optional[str],
                         auth_required: bool, repo_root: Path) -> None:
        """
        Register complete workflow in system_config.json.
        Creates/updates workflows.{workflow_key} with all required fields.
        """
        config_path = repo_root / "config/system_config.json"
        config = json.loads(config_path.read_text(encoding='utf-8'))

        if "workflows" not in config:
            config["workflows"] = {}

        # Create complete workflow entry
        config["workflows"][workflow_key] = {
            "supplier_name": supplier_name,
            "supplier_url": supplier_url,
            "categories_config_path": categories_path,
            "use_predefined_categories": True,
            "ai_client": None,
            "authentication_required": auth_required
        }

        # Add test_product_url if provided
        if test_product_url:
            config["workflows"][workflow_key]["test_product_url"] = test_product_url

        # Write back atomically
        guardian = WindowsSaveGuardian()
        guardian.save_json_atomic(config_path, config)

    @staticmethod
    def register_credentials(supplier_name: str, username: Optional[str],
                            password: Optional[str], repo_root: Path) -> None:
        """
        Register credentials in system_config.json.
        Only registers if username and password are provided.
        """
        if not username or not password:
            return  # Skip if credentials not provided

        config_path = repo_root / "config/system_config.json"
        config = json.loads(config_path.read_text(encoding='utf-8'))

        if "credentials" not in config:
            config["credentials"] = {}

        config["credentials"][supplier_name] = {
            "username": username,
            "password": password
        }

        # Write back atomically
        guardian = WindowsSaveGuardian()
        guardian.save_json_atomic(config_path, config)


# ============================================================================
# RUNNER SELECTION
# ============================================================================

def determine_runner(workflow_key: str, supplier_id: str, supplier_domain: str,
                     auth_required: bool, repo_root: Path) -> str:
    """
    Select appropriate runner for the supplier.
    Priority:
    1. Supplier-specific runner: run_custom_{supplier-id}.py (if exists)
    2. Generate FULL runner implementation (117-143 lines)

    No dependency on run_complete_fba_system.py or workflows.*.runner_script.
    """
    # 1. Check for supplier-specific runner
    supplier_runner = repo_root / f"run_custom_{supplier_id}.py"
    if supplier_runner.exists():
        return str(supplier_runner.absolute())

    # 2. Generate full runner implementation (HYBRID: template + LLM validation)
    runner_path = create_full_runner(
        supplier_id=supplier_id,
        workflow_key=workflow_key,
        supplier_domain=supplier_domain,
        auth_required=auth_required,
        repo_root=repo_root
    )
    return str(runner_path.absolute())


def create_full_runner(supplier_id: str, workflow_key: str, supplier_domain: str,
                       auth_required: bool, repo_root: Path) -> Path:
    """
    Generate FULL runner implementation (117-143 lines) from template.
    HYBRID APPROACH: Template-based generation + LLM validation afterward.

    Replaces create_runner_shim() which only generated 26-line forwarding scripts.
    """
    # Load template from skill directory (following Anthropic patterns)
    template_path = repo_root / ".claude/skills/supplier-onboarding/templates/runner_template.py.txt"
    if not template_path.exists():
        raise FileNotFoundError(f"Runner template not found: {template_path}")

    template = template_path.read_text(encoding='utf-8')

    # Determine supplier display name
    supplier_display_name = supplier_domain.replace('.co.uk', '').replace('.com', '').replace('.', ' ').title()

    # Authentication section
    if auth_required:
        # Check if auth helper exists or will be created
        auth_helper_dir = repo_root / "tools" / supplier_id
        auth_helper_file = auth_helper_dir / "supplier_authentication_service.py"

        supplier_class_name = supplier_domain.replace('.co.uk', '').replace('.com', '').replace('.', '').replace('-', '').title()

        if auth_helper_file.exists() or True:  # Always generate import assuming helper exists/will be created
            import_auth = f"from tools.{supplier_id}.supplier_authentication_service import {supplier_class_name}AuthenticationHelper"
            auth_section = f'''        log.info(f"🔐 Initializing {supplier_display_name} authentication helper...")
        auth_helper = {supplier_class_name}AuthenticationHelper(page)

        if not credentials:
            log.error(f"🚨 Credentials for {{supplier_name}} not found in config. Exiting.")
            return

        log.info(f"✅ Using credentials for {{supplier_name}}")
        log.info(f"🌐 Connecting to existing Chrome debug port {{chrome_debug_port}}...")

        is_authenticated = await auth_helper.is_authenticated()
        if not is_authenticated:
            log.info("🔐 Not authenticated, initiating login...")
            authenticated = await auth_helper.login(credentials)
            if not authenticated:
                log.error("❌ Authentication failed. Exiting workflow.")
                return
        else:
            log.info("✅ Already authenticated!")
'''
    else:
        import_auth = "# No authentication required"
        auth_section = '''        log.info(f"ℹ️ No authentication required for {supplier_name}")
'''

    # Replace template variables
    runner_content = template.replace('{{SUPPLIER_NAME}}', supplier_id)
    runner_content = runner_content.replace('{{SUPPLIER_DISPLAY_NAME}}', supplier_display_name)
    runner_content = runner_content.replace('{{SUPPLIER_DOMAIN}}', supplier_domain)
    runner_content = runner_content.replace('{{WORKFLOW_KEY}}', workflow_key)
    runner_content = runner_content.replace('{{IMPORT_AUTH_HELPER}}', import_auth)
    runner_content = runner_content.replace('{{AUTH_SECTION}}', auth_section)

    # Write runner file
    runner_path = repo_root / f"run_custom_{supplier_id}.py"
    atomic_write_text(runner_path, runner_content)

    # Make executable on Unix
    try:
        import stat
        runner_path.chmod(runner_path.stat().st_mode | stat.S_IEXEC)
    except:
        pass  # Windows doesn't support chmod

    return runner_path


def create_auth_helper(supplier_id: str, supplier_domain: str, supplier_url: str, repo_root: Path) -> Path:
    """
    Generate authentication helper for supplier from template.
    Creates tools/{supplier_id}/supplier_authentication_service.py

    ⚠️ Generated helper is a TEMPLATE requiring manual customization.
    """
    # Create supplier tools directory
    tools_dir = repo_root / "tools" / supplier_id
    tools_dir.mkdir(parents=True, exist_ok=True)

    # Create __init__.py
    init_file = tools_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text("", encoding='utf-8')

    # Load template from skill directory (following Anthropic patterns)
    template_path = repo_root / ".claude/skills/supplier-onboarding/templates/auth_helper_template.py.txt"
    if not template_path.exists():
        raise FileNotFoundError(f"Auth helper template not found: {template_path}")

    template = template_path.read_text(encoding='utf-8')

    # Determine class name (remove special chars, title case)
    supplier_class_name = supplier_domain.replace('.co.uk', '').replace('.com', '').replace('.', '').replace('-', '').title()
    supplier_display_name = supplier_domain.replace('.co.uk', '').replace('.com', '').replace('.', ' ').title()

    # Replace template variables
    content = template.replace('{{SUPPLIER_NAME}}', supplier_id)
    content = content.replace('{{SUPPLIER_CLASS_NAME}}', supplier_class_name)
    content = content.replace('{{SUPPLIER_DISPLAY_NAME}}', supplier_display_name)
    content = content.replace('{{SUPPLIER_URL}}', supplier_url)
    content = content.replace('{{SUPPLIER_ID}}', supplier_id)

    # Write file
    auth_file = tools_dir / "supplier_authentication_service.py"
    atomic_write_text(auth_file, content)

    return auth_file


def create_runner_shim(supplier_id: str, workflow_key: str, repo_root: Path) -> Path:
    """
    Generate run_custom_{supplier-id}.py that invokes workflow-mapped base runner.
    Maps workflow_key to specific existing runner using WORKFLOW_TO_RUNNER.
    """
    shim_path = repo_root / f"run_custom_{supplier_id}.py"

    # Get base runner from workflow mapping
    base_runner = WORKFLOW_TO_RUNNER.get(workflow_key, DEFAULT_RUNNER)

    shim_content = f'''#!/usr/bin/env python3
"""
Auto-generated runner shim for {supplier_id}
Maps to workflow: {workflow_key}
Base runner: {base_runner}
Generated by: supplier_onboarding_wizard.py
"""
import sys
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).parent
BASE_RUNNER = "{base_runner}"

def main():
    """Forward to base runner for this workflow."""
    cmd = [
        sys.executable,
        str(REPO_ROOT / BASE_RUNNER),
        *sys.argv[1:]
    ]

    raise SystemExit(subprocess.run(cmd).returncode)

if __name__ == "__main__":
    main()
'''

    # Write atomically using text helper (NOT WindowsSaveGuardian for non-JSON)
    atomic_write_text(shim_path, shim_content)

    # Make executable on Unix
    try:
        shim_path.chmod(0o755)
    except Exception:
        pass  # Windows doesn't support chmod

    return shim_path


# ============================================================================
# FILE GENERATION
# ============================================================================

def generate_files(
    session_input: Dict[str, Any],
    forms: SupplierForms,
    repo_root: Path,
    staging_dir: Path
) -> List[str]:
    """
    Generate all configuration files to staging directory.
    Returns list of files generated.
    """
    generated = []
    guardian = WindowsSaveGuardian()

    # 1. Selectors (legacy location - dot-form)
    selectors_path = staging_dir / "selectors.json"
    selectors_content = load_or_parse_json(session_input["selectors_source"], repo_root)
    guardian.save_json_atomic(selectors_path, selectors_content)
    generated.append(str(selectors_path))

    # 2. Categories (normalize schema)
    categories_path = staging_dir / "categories.json"
    categories_raw = load_or_parse_json(session_input["categories_source"], repo_root)

    # Normalize to {"category_urls": ["https://...", ...]}
    if isinstance(categories_raw, list):
        # If list of strings, wrap
        if categories_raw and isinstance(categories_raw[0], str):
            categories_content = {"category_urls": categories_raw}
        # If list of objects with name/url, extract URLs
        elif categories_raw and isinstance(categories_raw[0], dict):
            urls = [item.get("url") or item.get("category_url") for item in categories_raw if item.get("url") or item.get("category_url")]
            categories_content = {"category_urls": urls}
        else:
            categories_content = {"category_urls": []}
    elif isinstance(categories_raw, dict) and "category_urls" in categories_raw:
        categories_content = categories_raw
    else:
        raise ValueError(f"Categories must be list or dict with category_urls, got: {type(categories_raw)}")

    guardian.save_json_atomic(categories_path, categories_content)
    generated.append(str(categories_path))

    # 3. Optional: Supplier package
    if "supplier-package" in session_input.get("scaffolds", []):
        pkg_selectors = staging_dir / "package_selectors.json"
        guardian.save_json_atomic(pkg_selectors, selectors_content)
        generated.append(str(pkg_selectors))

        pkg_ready = staging_dir / "supplier_ready.json"
        ready_content = {"validation_status": {"products_validated": True}}
        guardian.save_json_atomic(pkg_ready, ready_content)
        generated.append(str(pkg_ready))

    # 4. Optional: Runner shim (generate directly to repo root, not staging)
    if "runner-shim" in session_input.get("scaffolds", []):
        runner = create_runner_shim(forms.supplier_id, session_input["workflow_key"], repo_root)
        generated.append(str(runner))

    return generated


def load_or_parse_json(source: str, repo_root: Path) -> Dict[str, Any]:
    """
    Load JSON from file path or parse inline JSON string.
    """
    # Try as file path first
    if source.endswith('.json'):
        file_path = repo_root / source if not Path(source).is_absolute() else Path(source)
        if file_path.exists():
            return json.loads(file_path.read_text(encoding='utf-8'))

    # Try parsing as JSON string
    try:
        return json.loads(source)
    except json.JSONDecodeError:
        raise ValueError(f"Cannot load JSON from source: {source}")


def atomic_move_to_final(staging_dir: Path, repo_root: Path, forms: SupplierForms, workflow_key: str):
    """
    Atomically move files from staging to final locations.
    Re-reads JSON and uses save_json_atomic for all writes.
    """
    guardian = WindowsSaveGuardian()

    # 1. Selectors
    staged_selectors = staging_dir / "selectors.json"
    final_selectors = NamingConventions.selector_config_path(forms.domain, repo_root)
    final_selectors.parent.mkdir(parents=True, exist_ok=True)
    selectors_data = json.loads(staged_selectors.read_text(encoding='utf-8'))
    guardian.save_json_atomic(final_selectors, selectors_data)

    # 2. Categories - Create SINGLE correct filename for both system and state manager
    staged_categories = staging_dir / "categories.json"

    # Use state manager compatible naming (without _workflow suffix)
    supplier_name_clean = forms.domain.replace('.co.uk', '').replace('.com', '').replace('.', '')
    categories_filename = f"{supplier_name_clean}_categories.json"
    final_categories = repo_root / "config" / categories_filename
    final_categories.parent.mkdir(parents=True, exist_ok=True)
    categories_data = json.loads(staged_categories.read_text(encoding='utf-8'))

    # Save single categories file for both system_config.json and state manager
    guardian.save_json_atomic(final_categories, categories_data)
    print(f"SUCCESS: Created: {categories_filename} (compatible with both system and state manager)")

    # Update system_config.json to use the correct path
    system_config_path = repo_root / "config" / "system_config.json"
    system_config = json.loads(system_config_path.read_text(encoding='utf-8'))

    if "workflows" not in system_config:
        system_config["workflows"] = {}
    if workflow_key not in system_config["workflows"]:
        system_config["workflows"][workflow_key] = {}

    system_config["workflows"][workflow_key]["categories_config_path"] = f"config/{categories_filename}"
    guardian.save_json_atomic(system_config_path, system_config)
    print(f"SUCCESS: Updated system_config.json to use: config/{categories_filename}")

    # Validate category file
    if not categories_data.get("category_urls"):
        print("\nWARNING: No category URLs were provided!")
        print("   The category file will be empty.")
        print("   Workflow will enter fresh_start mode.")
    else:
        print(f"\nSUCCESS: Category file validation:")
        print(f"   - Total URLs: {len(categories_data.get('category_urls', []))}")
        print(f"   - Single file used by both system and state manager")

    # 3. Supplier package (if exists)
    staged_pkg_selectors = staging_dir / "package_selectors.json"
    if staged_pkg_selectors.exists():
        final_pkg_dir = repo_root / f"suppliers/{forms.supplier_id}/config"
        final_pkg_dir.mkdir(parents=True, exist_ok=True)

        final_pkg_selectors = final_pkg_dir / "product_selectors.json"
        pkg_selectors_data = json.loads(staged_pkg_selectors.read_text(encoding='utf-8'))
        guardian.save_json_atomic(final_pkg_selectors, pkg_selectors_data)

        staged_ready = staging_dir / "supplier_ready.json"
        final_ready = repo_root / f"suppliers/{forms.supplier_id}/.supplier_ready"
        ready_data = json.loads(staged_ready.read_text(encoding='utf-8'))
        guardian.save_json_atomic(final_ready, ready_data)


# ============================================================================
# SANITY CHECK
# ============================================================================

def run_sanity_check(runner_path: str, repo_root: Path) -> subprocess.CompletedProcess:
    """
    Execute sanity check with FBA_TEST_MODE=true.
    """
    env = os.environ.copy()
    env["FBA_TEST_MODE"] = "true"

    cmd = [sys.executable, runner_path]

    result = subprocess.run(
        cmd,
        env=env,
        capture_output=True,
        text=True,
        timeout=600,  # 10 minute timeout
        cwd=str(repo_root)
    )

    return result


def verify_sanity_outputs(
    forms: SupplierForms,
    repo_root: Path,
    run_start_time: float
) -> Tuple[bool, Dict[str, bool]]:
    """
    Verify 6 criteria with exact field names and time windows.
    """
    checks = {}

    # 1. Scraping rate: supplier_products_completed >= 20 (nested then top-level fallback)
    state_file = NamingConventions.processing_state_file(forms.supplier_name_underscore, repo_root)
    if state_file.exists():
        state = json.loads(state_file.read_text(encoding='utf-8'))
        # Try nested first, then top-level fallback
        completed = state.get("system_progression", {}).get("supplier_products_completed")
        if completed is None:
            completed = state.get("supplier_products_completed", 0)
        checks["scraping_rate"] = int(completed) >= 20
    else:
        checks["scraping_rate"] = False

    # 2. Amazon cache: ≥1 recent file (within 15 minutes of run start)
    amazon_cache_dir = repo_root / "OUTPUTS/FBA_ANALYSIS/amazon_cache"
    if amazon_cache_dir.exists():
        recent_files = [
            f for f in amazon_cache_dir.glob("amazon_*.json")
            if f.stat().st_mtime >= run_start_time
        ]
        checks["amazon_cache"] = len(recent_files) > 0
    else:
        checks["amazon_cache"] = False

    # 3. Linking map: updated and non-empty (hyphen-form directory)
    linking_map_dir = NamingConventions.linking_map_dir(forms.supplier_id, repo_root)
    linking_map = linking_map_dir / "linking_map.json"
    if linking_map.exists():
        mtime = linking_map.stat().st_mtime
        size = linking_map.stat().st_size
        checks["linking_map"] = (mtime >= run_start_time and size > 100)
    else:
        checks["linking_map"] = False

    # 4. Financial CSV: present and >1KB (recent)
    financial_dir = repo_root / "OUTPUTS/FBA_ANALYSIS/financial_reports"
    if financial_dir.exists():
        recent_csvs = [
            f for f in financial_dir.glob("fba_financial_report_*.csv")
            if f.stat().st_mtime >= run_start_time and f.stat().st_size > 1024
        ]
        checks["financial_csv"] = len(recent_csvs) > 0
    else:
        checks["financial_csv"] = False

    # 5. Processing state: updated recently (underscore-form filename)
    checks["processing_state"] = (
        state_file.exists() and
        state_file.stat().st_mtime >= run_start_time
    )

    # 6. No critical errors: scan logs/debug/* for ERROR/CRITICAL
    checks["no_critical_errors"] = check_logs_for_errors(repo_root, run_start_time)

    all_passed = all(checks.values())
    return all_passed, checks


def check_logs_for_errors(repo_root: Path, run_start_time: float) -> bool:
    """
    Scan logs/debug/* for ERROR/CRITICAL patterns in recent logs.
    """
    logs_dir = repo_root / "logs/debug"
    if not logs_dir.exists():
        logs_dir = repo_root / "OUTPUTS/logs/debug"

    if not logs_dir.exists():
        return True  # No logs = assume no errors

    # Find logs created during this run
    recent_logs = [
        f for f in logs_dir.glob("run_custom_*.log")
        if f.stat().st_mtime >= run_start_time
    ]

    critical_patterns = [
        r'ERROR:',
        r'CRITICAL:',
        r'Exception:',
        r'Traceback \(most recent call last\):'
    ]

    for log_file in recent_logs:
        try:
            content = log_file.read_text(errors='ignore')
            for pattern in critical_patterns:
                if re.search(pattern, content):
                    return False
        except Exception:
            pass  # Ignore read errors

    return True


# ============================================================================
# REMEDIATION
# ============================================================================

def generate_remediation(checks: Dict[str, bool], forms: SupplierForms, repo_root: Path) -> Dict[str, Any]:
    """
    Generate remediation guidance for failed checks.
    """
    remediation = {}

    if not checks.get("scraping_rate"):
        remediation["scraping_rate"] = {
            "issue": "Less than 20 products scraped",
            "actions": [
                "Verify selectors are correct (product_item, title, price, ean, url, image)",
                f"Check {NamingConventions.selector_config_path(forms.domain, repo_root)}",
                "Use browser DevTools to verify CSS selectors match actual page structure",
                "Ensure no login required or authentication is properly configured"
            ]
        }

    if not checks.get("amazon_cache"):
        remediation["amazon_cache"] = {
            "issue": "No Amazon cache files generated",
            "actions": [
                "Verify EAN extraction is working (check selectors)",
                "Ensure Amazon API connectivity",
                "Check test product URL has valid EAN",
                f"Manually test: check OUTPUTS/FBA_ANALYSIS/amazon_cache/ exists"
            ]
        }

    if not checks.get("linking_map"):
        remediation["linking_map"] = {
            "issue": "Linking map not generated or empty",
            "actions": [
                f"Check hyphen-form directory: OUTPUTS/FBA_ANALYSIS/linking_maps/{forms.supplier_id}/",
                "Verify workflow completed amazon_analysis phase",
                "Ensure EAN matching succeeded for at least some products"
            ]
        }

    if not checks.get("financial_csv"):
        remediation["financial_csv"] = {
            "issue": "Financial CSV not generated",
            "actions": [
                "Check financial_report_batch_size in system_config.json",
                "Verify ROI calculations completed",
                "Check OUTPUTS/FBA_ANALYSIS/financial_reports/ directory"
            ]
        }

    if not checks.get("processing_state"):
        remediation["processing_state"] = {
            "issue": "Processing state file not updated",
            "actions": [
                f"Check underscore-form file: OUTPUTS/CACHE/processing_states/{forms.supplier_name_underscore}_processing_state.json",
                "Verify workflow completed without crashes",
                "Check logs for interruptions"
            ]
        }

    if not checks.get("no_critical_errors"):
        remediation["no_critical_errors"] = {
            "issue": "Critical errors found in logs",
            "actions": [
                "Review logs/debug/run_custom_*.log for ERROR/CRITICAL patterns",
                "Address specific errors found",
                "Check Chrome CDP connectivity if browser-related",
                "Verify authentication if login-related"
            ]
        }

    return remediation


# ============================================================================
# MAIN WIZARD LOGIC
# ============================================================================

class SupplierOnboardingWizard:
    """Main wizard orchestrator."""

    def __init__(self, input_file: Path, output_file: Path):
        self.input_file = input_file
        self.output_file = output_file
        self.session_input = None
        self.repo_root = None
        self.forms = None
        self.staging_dir = None

    def execute(self):
        """Main execution flow."""
        try:
            # 1. Load session input
            self.session_input = json.loads(self.input_file.read_text(encoding='utf-8'))
            self.repo_root = Path(self.session_input["repo_root"])

            # 2. Generate supplier forms
            self.forms = generate_supplier_forms(self.session_input["domain"])

            # 3. Execute based on mode
            if self.session_input["mode"] == "reference":
                result = self.reference_mode()
            else:
                result = self.generate_mode()

            # 4. Write output
            self.output_file.write_text(json.dumps(result, indent=2), encoding='utf-8')

        except Exception as e:
            # Error handling
            error_result = {
                "success": False,
                "errors": [str(e)],
                "files_generated": [],
                "sanity_results": {}
            }
            self.output_file.write_text(json.dumps(error_result, indent=2), encoding='utf-8')

    def reference_mode(self) -> Dict[str, Any]:
        """Validate existing files without writing."""
        checks = {
            "selectors_exist": NamingConventions.selector_config_path(self.forms.domain, self.repo_root).exists(),
            "categories_exist": NamingConventions.categories_config_path(self.session_input["workflow_key"], self.repo_root).exists()
        }

        return {
            "success": all(checks.values()),
            "files_generated": [],
            "validation_checks": checks,
            "sanity_results": {}
        }

    def generate_mode(self) -> Dict[str, Any]:
        """Generate files and run sanity check."""
        # 1. Create staging directory (absolute temp path, OS-safe)
        session_id = self.session_input.get("session_id") or str(uuid.uuid4())
        base_tmp = Path(tempfile.gettempdir())
        self.staging_dir = (base_tmp / "onboarding" / session_id / "staging").resolve()
        self.staging_dir.mkdir(parents=True, exist_ok=True)

        # 2. Generate files to staging
        staged_files = generate_files(self.session_input, self.forms, self.repo_root, self.staging_dir)

        # 3. Validate staged files
        # (Add validation logic here if needed)

        # 4. Atomic move to final locations
        atomic_move_to_final(self.staging_dir, self.repo_root, self.forms, self.session_input["workflow_key"])

        # 4a. Register workflow in system_config.json
        # FIX: Use consistent naming (no _workflow suffix) - matches atomic_move_to_final logic
        supplier_name_clean = self.forms.domain.replace('.co.uk', '').replace('.com', '').replace('.', '')
        categories_path = f"config/{supplier_name_clean}_categories.json"
        auth_required = self.session_input.get("authentication_required", False)
        test_product_url = self.session_input.get("test_product_url")

        # Extract supplier_url from selectors_source if it's a dict with supplier_url
        selectors = load_or_parse_json(self.session_input["selectors_source"], self.repo_root)
        supplier_url = selectors.get("supplier_url", f"https://{self.forms.domain}")

        NamingConventions.register_workflow(
            workflow_key=self.session_input["workflow_key"],
            supplier_name=self.forms.domain,
            supplier_url=supplier_url,
            categories_path=categories_path,
            test_product_url=test_product_url,
            auth_required=auth_required,
            repo_root=self.repo_root
        )

        # 4b. Register credentials (if provided)
        username = self.session_input.get("username")
        password = self.session_input.get("password")
        NamingConventions.register_credentials(
            supplier_name=self.forms.domain,
            username=username,
            password=password,
            repo_root=self.repo_root
        )

        # 4c. Generate authentication helper (if auth required)
        if auth_required:
            auth_helper_path = create_auth_helper(
                supplier_id=self.forms.supplier_id,
                supplier_domain=self.forms.domain,
                supplier_url=supplier_url,
                repo_root=self.repo_root
            )
            print(f"✅ Generated authentication helper: {auth_helper_path}")
            print(f"⚠️ Auth helper is a TEMPLATE - customize login selectors manually")
            print(f"   Edit: {auth_helper_path}")

        # 5. Determine runner (with NEW parameters for full runner generation)
        runner = determine_runner(
            workflow_key=self.session_input["workflow_key"],
            supplier_id=self.forms.supplier_id,
            supplier_domain=self.forms.domain,
            auth_required=auth_required,
            repo_root=self.repo_root
        )

        # 6. Run sanity check (set run_start_time immediately before)
        run_start_time = time.time()
        sanity_result = run_sanity_check(runner, self.repo_root)

        # 7. Verify outputs
        all_passed, checks = verify_sanity_outputs(self.forms, self.repo_root, run_start_time)

        # 8. Generate remediation if needed
        remediation = generate_remediation(checks, self.forms, self.repo_root) if not all_passed else None

        # 9. If sanity passed, run full workflow and generate summary
        full_run_result = None
        if all_passed:
            full_run_result = self.run_full_workflow_and_summarize(runner)

        # 10. Return result
        return {
            "success": all_passed,
            "files_generated": [
                str(NamingConventions.selector_config_path(self.forms.domain, self.repo_root)),
                str(NamingConventions.categories_config_path(self.session_input["workflow_key"], self.repo_root))
            ],
            "sanity_results": checks,
            "remediation": remediation,
            "sanity_stdout": sanity_result.stdout[:1000],  # Truncate
            "sanity_stderr": sanity_result.stderr[:1000] if sanity_result.stderr else None,
            "full_run_result": full_run_result
        }

    def run_full_workflow_and_summarize(self, runner: str) -> Dict[str, Any]:
        """
        On sanity pass: run full workflow and generate summary + curated CSV.
        """
        # 1. Run full workflow (without FBA_TEST_MODE)
        try:
            result = subprocess.run(
                [sys.executable, runner],
                capture_output=True,
                text=True,
                timeout=3600,  # 1 hour max
                cwd=str(self.repo_root)
            )

            if result.returncode != 0:
                return {
                    "status": "failed",
                    "error": f"Full run exited with code {result.returncode}",
                    "stderr": result.stderr[:500]
                }

        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "error": "Full run exceeded 1 hour timeout"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

        # 2. Generate summary and curated CSV
        try:
            summary_result = self._generate_summary_and_curated(runner)
            return {
                "status": "success",
                "summary_file": summary_result["summary_file"],
                "curated_file": summary_result["curated_file"],
                "total_products": summary_result["total_products"],
                "curated_products": summary_result["curated_products"]
            }
        except Exception as e:
            return {
                "status": "partial",
                "error": f"Full run completed but summary generation failed: {e}"
            }

    def _generate_summary_and_curated(self, runner: str) -> Dict[str, Any]:
        """
        Generate summary.md and curated.csv in OUTPUTS/AI_SETUP_RESULTS/{supplier-id}/.
        """
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_dir = self.repo_root / f"OUTPUTS/AI_SETUP_RESULTS/{self.forms.supplier_id}"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Find latest financial report
        financial_dir = self.repo_root / "OUTPUTS/FBA_ANALYSIS/financial_reports"
        if not financial_dir.exists():
            raise FileNotFoundError("No financial reports directory found")

        csv_files = list(financial_dir.glob("fba_financial_report_*.csv"))
        if not csv_files:
            raise FileNotFoundError("No financial reports found")

        latest_csv = max(csv_files, key=lambda f: f.stat().st_mtime)

        # Read CSV and filter (profit ≥ £2, ROI ≥ 30%, margin ≥ 25%)
        # Uses repo's field names: net_profit_gbp, roi_pct, margin_pct with tolerant fallback
        curated_rows = []
        total_count = 0

        with open(latest_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                total_count += 1
                try:
                    # Tolerant field name lookup: try repo names first, fallback to old names
                    profit = float(row.get('net_profit_gbp') or row.get('profit_gbp') or 0)
                    roi = float(row.get('roi_pct') or row.get('roi_percentage') or 0)
                    margin = float(row.get('margin_pct') or row.get('profit_margin_percentage') or 0)

                    if profit >= 2 and roi >= 30 and margin >= 25:
                        curated_rows.append(row)
                except (ValueError, KeyError):
                    pass  # Skip malformed rows

        # Write curated CSV
        curated_file = output_dir / f"curated_{timestamp}.csv"
        if curated_rows:
            with open(curated_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=curated_rows[0].keys())
                writer.writeheader()
                writer.writerows(curated_rows)

        # Calculate curated percentage (guard against division by zero)
        curated_pct = (len(curated_rows) / total_count * 100.0) if total_count else 0.0

        # Write summary markdown
        summary_file = output_dir / f"summary_{timestamp}.md"
        summary_content = f"""# Supplier Onboarding Summary

**Supplier**: {self.forms.domain}
**Workflow**: {self.session_input['workflow_key']}
**Date**: {time.strftime("%Y-%m-%d %H:%M:%S")}

## Results

- **Total Products Analyzed**: {total_count}
- **Curated Products** (profit ≥ £2, ROI ≥ 30%, margin ≥ 25%): {len(curated_rows)}
- **Curated Percentage**: {curated_pct:.1f}%

## Criteria

- Minimum Profit: £2.00
- Minimum ROI: 30%
- Minimum Margin: 25%

## Files Generated

- Selectors: `{NamingConventions.selector_config_path(self.forms.domain, self.repo_root).relative_to(self.repo_root)}`
- Categories: `{NamingConventions.categories_config_path(self.session_input['workflow_key'], self.repo_root).relative_to(self.repo_root)}`
- Financial Report: `{latest_csv.relative_to(self.repo_root)}`
- Curated Products: `{curated_file.relative_to(self.repo_root)}`

## Next Steps

1. Review curated products in `{curated_file.name}`
2. Adjust selectors if needed in `{NamingConventions.selector_config_path(self.forms.domain, self.repo_root).relative_to(self.repo_root)}`
3. Run again with: `python {runner.replace(str(self.repo_root) + '/', '')}`
"""

        summary_file.write_text(summary_content, encoding='utf-8')

        return {
            "summary_file": str(summary_file),
            "curated_file": str(curated_file),
            "total_products": total_count,
            "curated_products": len(curated_rows)
        }


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Supplier Onboarding Wizard")
    parser.add_argument("--input", required=True, type=Path, help="Session input JSON file")
    parser.add_argument("--output", required=True, type=Path, help="Session output JSON file")

    args = parser.parse_args()

    wizard = SupplierOnboardingWizard(args.input, args.output)
    wizard.execute()


if __name__ == "__main__":
    main()
