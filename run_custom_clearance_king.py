import asyncio
import logging
import sys
import os

# Add project root to Python path to resolve module imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Ensure Windows consoles can render Unicode log output
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass


from playwright.async_api import async_playwright
from config.system_config_loader import SystemConfigLoader
from tools.standalone_playwright_login import StandalonePlaywrightLogin
from tools.passive_extraction_workflow_latest import PassiveExtractionWorkflow
from tools.supplier_authentication_service import SupplierAuthenticationService
from utils.logger import setup_logger
from utils.browser_manager import BrowserManager

# 🚨 IMPORT HYGIENE: Validate correct module is imported
import inspect
workflow_module_path = inspect.getfile(PassiveExtractionWorkflow)
expected_path_suffix = os.path.join("tools", "passive_extraction_workflow_latest.py")
if not workflow_module_path.endswith(expected_path_suffix.replace(os.sep, "/")):
    print(f"WARNING: PassiveExtractionWorkflow imported from unexpected path: {workflow_module_path}")
    print(f"Expected path to end with: {expected_path_suffix}")
else:
    print(f"IMPORT HYGIENE: PassiveExtractionWorkflow imported from correct path: {workflow_module_path}")

async def main():
    """Main function to run the custom Clearance King extraction workflow."""
    # Detect platform and display compatibility info
    import platform
    system_platform = platform.system()

    if system_platform == "Windows":
        print("🪟 --- Starting Custom Clearance King Extraction Workflow (Windows Native) ---")
        print("✅ Running on Windows - Enhanced memory management enabled")
    else:
        print("--- Starting Custom Clearance King Extraction Workflow (Linux/WSL) ---")
        print("Running on Linux/WSL - Standard memory management")

    print(f"Platform: {system_platform}")
    print(f"Python: {platform.python_version()}")
    print("--- Starting Custom Clearance King Extraction Workflow ---")

    # Setup logging
    debug_log_file = setup_logger()
    log = logging.getLogger(__name__)
    log.info(f"📋 Debug log file: {debug_log_file}")
    log.debug("Debug logging initialized - full system execution details will be captured")

    config_loader = SystemConfigLoader()
    workflow_config = config_loader.get_workflow_config('clearance_king_workflow')
    supplier_name = workflow_config.get('supplier_name', 'clearance-king.co.uk')
    credentials = config_loader.get_credentials(supplier_name)

    chrome_debug_port = config_loader.get_system_config().get('chrome_debug_port', 9222)

    browser_manager = None
    try:
        browser_manager = BrowserManager.get_instance()
        await browser_manager.launch_browser(cdp_port=chrome_debug_port)
        page = await browser_manager.get_page()

        supplier_url = workflow_config.get('supplier_url', f"https://{supplier_name}")
        supplier_config_path = os.path.join("config", "supplier_configs", f"{supplier_name}.json")

        log.info(f"🔐 Initializing authentication service for logout detection...")
        auth_service = SupplierAuthenticationService(browser_manager)

        if not credentials:
            log.error(f"🚨 Credentials for {supplier_name} not found in config. Exiting.")
            return

        log.info(f"✅ Using configured credentials for {supplier_name}")

        log.info(f"🌐 Connecting to existing Chrome debug port {chrome_debug_port} for authentication...")

        authenticated = await auth_service.ensure_authenticated_session(page, credentials)
        if not authenticated:
            log.error("Authentication failed. Exiting workflow.")
            return

        # Pass the single browser manager instance to the workflow
        workflow = PassiveExtractionWorkflow(
            config_loader=config_loader,
            workflow_config=workflow_config,
            browser_manager=browser_manager
        )
        await workflow.run()

    except Exception as e:
        log.error(f"Unexpected error in main workflow: {str(e)}", exc_info=True)
        raise
    finally:
        if browser_manager:
            try:
                await browser_manager.cleanup()
                log.info("🧹 Browser cleanup completed")
            except Exception as cleanup_error:
                log.warning(f"⚠️ Browser cleanup warning: {str(cleanup_error)}")

if __name__ == "__main__":
    asyncio.run(main())