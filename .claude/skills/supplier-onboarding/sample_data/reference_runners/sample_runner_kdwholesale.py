import asyncio
import logging
import sys
import os
from playwright.async_api import async_playwright

# Add project root to path to ensure imports work correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.system_config_loader import SystemConfigLoader
from tools.passive_extraction_workflow_latest import PassiveExtractionWorkflow
from utils.browser_manager import BrowserManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("kdwholesale_runner.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """
    Main entry point for the KD Wholesale scraper runner.
    This script initializes the workflow and executes the scraping process.
    """
    logger.info("Starting KD Wholesale extraction workflow...")
    
    # Initialize system configuration loader
    config_loader = SystemConfigLoader()
    
    # Load the specific workflow configuration for KD Wholesale
    # The key 'kdwholesale_workflow' must exist in system_config.json
    workflow_config = config_loader.get_workflow_config('kdwholesale_workflow')
    
    if not workflow_config:
        logger.error("Workflow configuration 'kdwholesale_workflow' not found!")
        return

    # Initialize the browser manager
    # We use a context manager to ensure the browser is properly closed
    async with async_playwright() as p:
        browser_manager = BrowserManager(p)
        
        try:
            # Launch the browser instance
            # Headless mode is typically preferred for production runs
            browser = await browser_manager.launch_browser(headless=True)
            page = await browser_manager.create_page(browser)
            
            logger.info("Browser launched successfully.")

            # Initialize the Passive Extraction Workflow
            # This is the core component that handles the scraping logic
            workflow = PassiveExtractionWorkflow(
                page=page,
                config=workflow_config,
                workflow_id='kdwholesale_workflow'
            )
            
            # --- Authentication Section (Optional) ---
            # If authentication is required, the auth helper would be initialized here.
            # For KD Wholesale, we are assuming no authentication is required for this sample.
            # 
            # Example of what auth code would look like:
            # from tools.kdwholesale.supplier_authentication_service import KdwholesaleAuthenticationHelper
            # auth_helper = KdwholesaleAuthenticationHelper(page)
            # if not await auth_helper.is_authenticated():
            #     await auth_helper.login(config_loader.get_credentials('kdwholesale'))
            # -----------------------------------------

            logger.info("Workflow initialized. Starting execution...")

            # Execute the workflow
            # This will process categories, extract products, and save results
            await workflow.run()
            
            logger.info("Workflow execution completed successfully.")

        except Exception as e:
            logger.error(f"An error occurred during workflow execution: {str(e)}")
            import traceback
            traceback.print_exc()
            
        finally:
            # Ensure browser resources are released
            logger.info("Closing browser resources...")
            await browser_manager.close()

def validate_environment():
    """
    Performs a quick check of the environment before running.
    """
    # Check if output directories exist
    os.makedirs("OUTPUTS", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Check if config files exist
    if not os.path.exists("config/system_config.json"):
        logger.warning("config/system_config.json not found!")

if __name__ == "__main__":
    # Set up Windows-specific event loop policy if needed
    # Windows-specific event loop configuration for Python 3.13+
    if sys.platform == "win32":
        import platform
        # Parse python version
        python_version = tuple(map(int, platform.python_version().split('.')))
        
        if python_version >= (3, 13):
            # Python 3.13+ requires ProactorEventLoop for subprocess support on Windows
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            # print("Using Windows ProactorEventLoop for Python 3.13+ compatibility")
        else:
            # Python 3.12 and below use SelectorEventLoop
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            # print("Using Windows SelectorEventLoop for Python 3.12 compatibility")
    
    # Validate environment
    validate_environment()
    
    # Run the main async function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Workflow interrupted by user.")
    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}")
        sys.exit(1)

# End of runner script
# This script is designed to be a robust entry point for the supplier scraping process.
# It handles configuration loading, browser management, and workflow execution.
# 
# Key responsibilities:
# 1. Load configuration
# 2. Initialize browser
# 3. Instantiate workflow
# 4. Handle authentication (if needed)
# 5. Execute workflow
# 6. Clean up resources
