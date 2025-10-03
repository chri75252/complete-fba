"""
Clearance King Authentication Helper
Provides authentication services specifically for clearance-king.co.uk
"""

import asyncio
import logging
import os
from typing import Dict, Optional
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError
from tools.standalone_playwright_login import StandalonePlaywrightLogin

class ClearanceKingAuthenticationHelper:
    """
    Authentication helper specifically for Clearance King website
    """

    def __init__(self, page: Page):
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
            # Quick check - if we're on login page, definitely not authenticated
            current_url = self.page.url
            if "/customer/account/login" in current_url:
                self.log.info("❌ Currently on login page - not authenticated")
                return False

            # Check for login button on page (indicates not authenticated)
            try:
                login_link = await self.page.wait_for_selector("a[href*='login']", timeout=3000)
                if login_link:
                    self.log.info("❌ Login link found - not authenticated")
                    return False
            except PlaywrightTimeoutError:
                pass

            # Use StandalonePlaywrightLogin for price verification (most reliable check)
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
                
                # Verify price access for complete authentication confirmation
                self.log.info("🔍 Verifying price access to confirm authentication...")
                price_access = await login_handler.verify_price_access(self.page)
                if price_access:
                    self.log.info(f"✅ Authentication confirmed via price access verification")
                    return True
                else:
                    self.log.info("❌ Price access verification failed - not authenticated")
                    return False
                    
            except Exception as e:
                self.log.debug(f"Could not verify price access: {e}")
                # Fall back to basic DOM checks if price verification fails
                pass

            # Fallback: Check for basic authentication indicators
            for selector in self.auth_check_selectors:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=3000)
                    if element:
                        self.log.info(f"✅ Basic authentication indicator found: {selector}")
                        return True
                except PlaywrightTimeoutError:
                    continue

            # If no clear indicators, assume not authenticated
            self.log.info("❌ No authentication indicators found - not authenticated")
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
                
                # Perform login using StandalonePlaywrightLogin
                self.log.info("🚀 Performing login via StandalonePlaywrightLogin...")
                login_result = await login_handler.perform_login()
                
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

    async def ensure_authenticated_session(self, page: Page, credentials: Dict[str, str]) -> bool:
        """
        Ensure user is authenticated, performing login if necessary

        Args:
            page: Playwright page object (for compatibility, but self.page is used)
            credentials: Dictionary with 'username' and 'password' keys

        Returns:
            bool: True if authenticated session is established, False otherwise
        """
        try:
            self.log.info("🔍 Checking current authentication status...")

            # First check if already authenticated
            if await self.is_authenticated():
                self.log.info("✅ Already authenticated - no login required")
                return True

            # Not authenticated, attempt login
            self.log.info("🔐 Not authenticated - attempting login...")
            return await self.login(credentials)

        except Exception as e:
            self.log.error(f"❌ Error ensuring authenticated session: {str(e)}")
            return False

# Alias for compatibility with existing imports
SupplierAuthenticationService = ClearanceKingAuthenticationHelper