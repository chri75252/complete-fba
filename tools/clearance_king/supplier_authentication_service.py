"""
Clearance King Authentication Helper
Provides authentication services specifically for clearance-king.co.uk
"""

import asyncio
import logging
import os
from typing import Dict, Optional
from urllib.parse import urlparse
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError
from tools.standalone_playwright_login import StandalonePlaywrightLogin
from config.system_config_loader import SystemConfigLoader

def _normalize_domain(url_or_host: str) -> str:
    """Normalize domain for consistent credential lookup"""
    host = url_or_host
    if "://" in url_or_host:
        host = urlparse(url_or_host).netloc
    host = host.lower()
    if host.startswith("www."):
        host = host[4:]
    return host

class ClearanceKingAuthenticationHelper:
    """
    Authentication helper specifically for Clearance King website
    """

    def __init__(self, page: Page):
        # ✅ Type guard: Fail fast with clear message if wrong type passed
        assert hasattr(page, "goto"), (
            "ClearanceKingAuthenticationHelper expects a Playwright Page object, "
            "not BrowserManager. Please pass: page = await browser_manager.get_page(...)"
        )
        self.page = page
        self.log = logging.getLogger(__name__)

        # Clearance King specific configuration
        self.login_url = "https://www.clearance-king.co.uk/customer/account/login/"

        # Authentication check selectors
        self.auth_check_selectors = [
            ".customer-welcome",
            ".logged-in",
            ".customer-name",
            ".customer-menu"
        ]

    async def is_authenticated(self) -> bool:
        """
        Check if user is currently authenticated on Clearance King
        Uses price verification as the definitive authentication check

        Returns:
            bool: True if authenticated, False otherwise
        """
        try:
            # 1) Price visibility (strongest signal) - check price access first
            try:
                # Load clearance-king supplier config directly from file
                import json
                supplier_config_path = os.path.join("config", "supplier_configs", "clearance-king.co.uk.json")
                
                with open(supplier_config_path, 'r', encoding='utf-8') as f:
                    supplier_config = json.load(f)
                
                # Extract required configuration values
                test_product_url = supplier_config.get('login_config', {}).get('test_product_url')
                if not test_product_url:
                    self.log.error("❌ test_product_url not found in clearance-king config")
                    return False
                
                login_handler = StandalonePlaywrightLogin(
                    supplier_url="https://www.clearance-king.co.uk",
                    test_product_url=test_product_url,
                    supplier_config=supplier_config
                )
                login_handler.page = self.page  # Use existing page
                
                # Use existing page for price verification
                if await login_handler.verify_price_access(page=self.page):
                    self.log.info("✅ Price visible on test product — authenticated")
                    return True
            except Exception as e:
                self.log.debug(f"Price verification failed: {e}")

            # 2) Explicit "logout / account" indicators
            try:
                logout_selectors = [
                    "a[href*='logout']",
                    "a:has-text('My Account')",
                    "a:has-text('Account')",
                    ".customer-welcome",
                    ".customer-name"
                ]
                for selector in logout_selectors:
                    try:
                        element = await self.page.locator(selector).first
                        if await element.is_visible(timeout=1000):
                            self.log.info(f"✅ Logout/Account indicator found ({selector}) — authenticated")
                            return True
                    except Exception:
                        continue
            except Exception:
                pass

            # 3) As a weak negative, a visible login link
            try:
                login_link = await self.page.locator("a[href*='login']").first
                if await login_link.is_visible(timeout=1000):
                    self.log.info("❌ Login link visible — likely not authenticated")
                    return False
            except Exception:
                pass

            # Default conservative answer
            self.log.info("❌ No clear authentication indicators found")
            return False

        except Exception as e:
            self.log.error(f"Error checking authentication status: {str(e)}")
            return False

    async def login(self, credentials: Dict[str, str]) -> bool:
        """
        Perform login to Clearance King

        Args:
            credentials: Dictionary with 'username' and 'password' keys

        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            username = credentials.get('username')
            password = credentials.get('password')

            if not username or not password:
                self.log.error("❌ Missing username or password in credentials")
                return False

            self.log.info(f"🔐 Starting login process for Clearance King...")

            # Use StandalonePlaywrightLogin for comprehensive login
            try:
                # Load clearance-king supplier config directly from file
                import json
                supplier_config_path = os.path.join("config", "supplier_configs", "clearance-king.co.uk.json")
                
                with open(supplier_config_path, 'r', encoding='utf-8') as f:
                    supplier_config = json.load(f)
                
                # Extract required configuration values
                test_product_url = supplier_config.get('login_config', {}).get('test_product_url')
                if not test_product_url:
                    self.log.error("❌ test_product_url not found in clearance-king config")
                    return False
                
                login_handler = StandalonePlaywrightLogin(
                    email=username,
                    password=password,
                    supplier_url="https://www.clearance-king.co.uk",
                    test_product_url=test_product_url,
                    supplier_config=supplier_config
                )
                login_handler.page = self.page  # Use existing page
                
                # Perform login using StandalonePlaywrightLogin (uses login_workflow for skip-if-authenticated)
                self.log.info("🚀 Performing login via StandalonePlaywrightLogin...")
                login_result = await login_handler.login_workflow()
                
                if login_result.success:
                    self.log.info("✅ Login successful via StandalonePlaywrightLogin!")
                    return True
                else:
                    self.log.error(f"❌ Login failed: {login_result.error_message}")
                    return False
                    
            except Exception as e:
                self.log.error(f"❌ StandalonePlaywrightLogin failed: {str(e)}")
                return False

        except Exception as e:
            self.log.error(f"❌ Login failed with exception: {str(e)}")
            return False

    async def ensure_authenticated_session(self, credentials: Dict[str, str] | None = None) -> bool:
        """
        Ensure user is authenticated, performing login if necessary

        Args:
            credentials: Dictionary with 'username' and 'password' keys (optional, will load from config if not provided)

        Returns:
            bool: True if authenticated session is established, False otherwise

        Note:
            This helper is page-based; it uses self.page set in __init__
        """
        try:
            self.log.info("🔍 Checking current authentication status...")

            # First check if already authenticated
            if await self.is_authenticated():
                self.log.info("✅ Already authenticated - no login required")
                return True

            # Not authenticated, attempt login with robust credentials resolution
            self.log.info("🔐 Not authenticated - attempting login...")

            # Always resolve credentials robustly
            if not credentials or not credentials.get("username") or not credentials.get("password"):
                self.log.warning("⚠️ Credentials missing or incomplete - loading from config")
                loader = SystemConfigLoader()
                # Normalize domain from login URL for consistent credential lookup
                credential_key = _normalize_domain(self.login_url)  # Will be "clearance-king.co.uk"
                resolved_creds = loader.get_credentials(credential_key)

                if not resolved_creds or not resolved_creds.get("username") or not resolved_creds.get("password"):
                    self.log.error(f"❌ Missing credentials for {credential_key}")
                    return False
                credentials = resolved_creds
                self.log.info(f"✅ Loaded credentials from config for {credential_key}")

            return await self.login(credentials)

        except Exception as e:
            self.log.error(f"❌ Error ensuring authenticated session: {str(e)}")
            return False

# Alias for compatibility with existing imports
SupplierAuthenticationService = ClearanceKingAuthenticationHelper