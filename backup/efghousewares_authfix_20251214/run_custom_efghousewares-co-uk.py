#!/usr/bin/env python3
"""
Custom runner for efghousewares-co-uk
"""

import asyncio
import logging
import os
import sys

# Add project root to Python path to resolve module imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Ensure Windows consoles can render Unicode log output
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from config.system_config_loader import SystemConfigLoader
from tools.passive_extraction_workflow_latest import PassiveExtractionWorkflow
from tools.efghousewares.supplier_authentication_service import SupplierAuthenticationService
from utils.browser_manager import BrowserManager
from utils.logger import setup_logger

# ✅ IMPORT HYGIENE: Validate correct shared workflow module is imported
import inspect

workflow_module_path = inspect.getfile(PassiveExtractionWorkflow)
expected_path_suffix = os.path.join("tools", "passive_extraction_workflow_latest.py")
if not workflow_module_path.endswith(expected_path_suffix.replace(os.sep, "/")):
    print(f"WARNING: PassiveExtractionWorkflow imported from unexpected path: {workflow_module_path}")
    print(f"Expected path to end with: {expected_path_suffix}")
else:
    print(f"IMPORT HYGIENE: PassiveExtractionWorkflow imported from correct path: {workflow_module_path}")


async def main() -> None:
    debug_log_file = setup_logger()
    log = logging.getLogger(__name__)
    log.info(f"📄 Debug log file: {debug_log_file}")

    config_loader = SystemConfigLoader()
    workflow_config = config_loader.get_workflow_config("efghousewares_workflow")
    supplier_name = workflow_config.get("supplier_name", "efghousewares.co.uk")
    credentials = config_loader.get_credentials(supplier_name)

    chrome_debug_port = config_loader.get_system_config().get("chrome_debug_port", 9222)

    browser_manager = None
    try:
        browser_manager = BrowserManager.get_instance()
        await browser_manager.launch_browser(cdp_port=chrome_debug_port)
        page = await browser_manager.get_page()

        if not page:
            log.error("❌ Could not acquire a browser page")
            return

        log.info("🔐 Checking supplier authentication status...")
        auth_helper = SupplierAuthenticationService(page)
        if not await auth_helper.is_authenticated(page):
            if not credentials:
                log.error(f"❌ Credentials for {supplier_name} not found in config; cannot login.")
                return
            log.info(f"✅ Using credentials for {supplier_name}")
            ok = await auth_helper.login(credentials, page=page)
            if not ok:
                log.error("❌ Authentication failed. Exiting workflow.")
                return
        else:
            log.info("✅ Already authenticated")

        workflow = PassiveExtractionWorkflow(
            config_loader=config_loader,
            workflow_config=workflow_config,
            browser_manager=browser_manager,
        )

        log.info(f"🚀 Starting workflow for {supplier_name}...")
        await workflow.run()
        log.info("✅ Workflow completed successfully")

    except KeyboardInterrupt:
        log.warning("⚠️ Workflow interrupted by user")
    except Exception as e:
        log.error(f"❌ Workflow failed: {e}", exc_info=True)
        raise
    finally:
        if browser_manager:
            log.info("🧠 Keeping browser persistent for next run - not calling cleanup()")


if __name__ == "__main__":
    # Windows-specific event loop configuration for Python 3.13+
    if sys.platform == "win32":
        import platform

        python_version = tuple(map(int, platform.python_version().split(".")))
        if python_version >= (3, 13):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        else:
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())

