"""
Clearance King Authentication Helper
Provides authentication services specifically for clearance-king.co.uk
"""

import asyncio
import logging
from typing import Dict, Optional
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

class ClearanceKingAuthenticationHelper:
    """
    Authentication helper specifically for Clearance King website
    """

    def __init__(self, page: Page):
        self.page = page
        self.log = logging.getLogger(__name__)

        # Clearance King specific selectors
        self.login_url = "https://www.clearance-king.co.uk/customer/account/login/"
        self.email_selector = "input#email"
        self.password_selector = "input#pass"
        self.login_button_selector = "button#send2.action.login.primary"

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

        Returns:
            bool: True if authenticated, False otherwise
        """
        try:
            # Check for authentication indicators
            for selector in self.auth_check_selectors:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=3000)
                    if element:
                        self.log.info(f"✅ Authentication confirmed via selector: {selector}")
                        return True
                except PlaywrightTimeoutError:
                    continue

            # Check if we're on login page (indicates not authenticated)
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

            # If no clear indicators, assume authenticated
            self.log.info("✅ No clear authentication indicators found - assuming authenticated")
            return True

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

            # Navigate to login page
            self.log.info(f"🌐 Navigating to login page: {self.login_url}")
            await self.page.goto(self.login_url, wait_until="domcontentloaded")

            # Wait for login form to load
            await self.page.wait_for_selector(self.email_selector, timeout=10000)

            # Fill email field
            self.log.info("📧 Filling email field...")
            await self.page.fill(self.email_selector, username)

            # Fill password field
            self.log.info("🔑 Filling password field...")
            await self.page.fill(self.password_selector, password)

            # Click login button
            self.log.info("🚀 Clicking login button...")
            await self.page.click(self.login_button_selector)

            # Wait for navigation or error
            try:
                await self.page.wait_for_load_state("networkidle", timeout=15000)
            except PlaywrightTimeoutError:
                self.log.warning("⚠️ Timeout waiting for network idle after login")

            # Check if login was successful
            await asyncio.sleep(2)  # Brief wait for page to settle

            if await self.is_authenticated():
                self.log.info("✅ Login successful!")
                return True
            else:
                # Check for error messages
                error_selectors = [
                    ".message-error",
                    ".error-message",
                    ".alert-error",
                    "[data-ui-id='message-error']"
                ]

                for error_selector in error_selectors:
                    try:
                        error_element = await self.page.wait_for_selector(error_selector, timeout=2000)
                        if error_element:
                            error_text = await error_element.text_content()
                            self.log.error(f"❌ Login error: {error_text}")
                            break
                    except PlaywrightTimeoutError:
                        continue

                self.log.error("❌ Login failed - authentication check failed")
                return False

        except Exception as e:
            self.log.error(f"❌ Login failed with exception: {str(e)}")
            return False

    async def ensure_authenticated_session(self, credentials: Dict[str, str]) -> bool:
        """
        Ensure user is authenticated, performing login if necessary

        Args:
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