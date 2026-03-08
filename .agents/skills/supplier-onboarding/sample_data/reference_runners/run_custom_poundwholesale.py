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
from tools.poundwholesale.supplier_authentication_service import PoundwholesaleAuthenticationHelper
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
    """Main function to run the custom extraction workflow."""
    # Detect platform and display compatibility info
    import platform
    system_platform = platform.system()
    
    if system_platform == "Windows":
        print("🪟 --- Starting Custom Pound Wholesale Extraction Workflow (Windows Native) ---")
        print("✅ Running on Windows - Enhanced memory management enabled")
    else:
        print("--- Starting Custom Pound Wholesale Extraction Workflow (Linux/WSL) ---")
        print("Running on Linux/WSL - Standard memory management")
    
    print(f"Platform: {system_platform}")
    print(f"Python: {platform.python_version()}")
    print("--- Starting Custom Pound Wholesale Extraction Workflow ---")
    
    # Setup logging
    debug_log_file = setup_logger()
    log = logging.getLogger(__name__)
    log.info(f"📋 Debug log file: {debug_log_file}")
    log.debug("Debug logging initialized - full system execution details will be captured")

    config_loader = SystemConfigLoader()
    workflow_config = config_loader.get_workflow_config('poundwholesale_workflow')
    supplier_name = workflow_config.get('supplier_name', 'poundwholesale.co.uk')
    credentials = config_loader.get_credentials(supplier_name)
    
    chrome_debug_port = config_loader.get_system_config().get('chrome_debug_port', 9222)

    browser_manager = None
    try:
        browser_manager = BrowserManager.get_instance()
        await browser_manager.launch_browser(cdp_port=chrome_debug_port)
        page = await browser_manager.get_page()

        supplier_url = workflow_config.get('supplier_url', f"https://{supplier_name}")
        supplier_config_path = os.path.join("config", "supplier_configs", f"{supplier_name}.json")

        log.info(f"🔐 Initializing Poundwholesale authentication helper...")
        auth_helper = PoundwholesaleAuthenticationHelper(page)

        if not credentials:
            log.error(f"🚨 Credentials for {supplier_name} not found in config. Exiting.")
            return

        log.info(f"✅ Using hardcoded credentials for {supplier_name}")
        
        log.info(f"🌐 Connecting to existing Chrome debug port {chrome_debug_port} for authentication...")

        # Check if already authenticated
        is_authenticated = await auth_helper.is_authenticated()
        if not is_authenticated:
            log.info("🔐 Not authenticated, initiating login...")
            authenticated = await auth_helper.login(credentials)
            if not authenticated:
                log.error("❌ Authentication failed. Exiting workflow.")
                return
        else:
            log.info("✅ Already authenticated!")

        # Pass the single browser manager instance to the workflow
        workflow = PassiveExtractionWorkflow(
            config_loader=config_loader,
            workflow_config=workflow_config,
            browser_manager=browser_manager
        )
        await workflow.run()

    except Exception as e:
        log.critical(f"💥 A critical error occurred in the main workflow: {e}", exc_info=True)
    finally:
        if browser_manager:
            # Keep browser persistent - only close pages, not the browser itself
            log.info("🌐 Keeping browser persistent for next run - not closing browser")
            # No browser cleanup to maintain persistence
        print("--- Custom Pound Wholesale Extraction Workflow Finished ---")

if __name__ == "__main__":
    # Windows-specific event loop configuration for Python 3.13+
    if sys.platform == "win32":
        # Fix for Python 3.13+ on Windows with Playwright
        import platform
        python_version = tuple(map(int, platform.python_version().split('.')))
        
        if python_version >= (3, 13):
            # Python 3.13+ requires ProactorEventLoop for subprocess support on Windows
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            print("Using Windows ProactorEventLoop for Python 3.13+ compatibility")
        else:
            # Python 3.12 and below use SelectorEventLoop
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            print("Using Windows SelectorEventLoop for Python 3.12 compatibility")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Shutting down gracefully.")
    except NotImplementedError as e:
        print(f"\nWindows event loop error: {e}")
        print("Try installing the latest version of Playwright:")
        print("   pip install --upgrade playwright")
        print("   playwright install chromium")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
