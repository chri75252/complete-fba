"""
EFG Housewares Authentication Helper

This supplier requires login to view wholesale prices ("LOGIN TO PURCHASE" appears when logged out).
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
from typing import Any

from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

log = logging.getLogger(__name__)


class SupplierAuthenticationService:
    """
    Authentication service for https://www.efghousewares.co.uk

    Compatibility notes:
    - Some call sites instantiate this with a Playwright `Page` (positional).
    - Some call sites instantiate with keyword args: supplier_name/supplier_url/config_path.
    - Some call sites call `ensure_authenticated_session(credentials)` and expect `bool`.
    - Some call sites call `ensure_authenticated_session(page, credentials, force_reauth=...)` and expect a tuple.
    """

    def __init__(
        self,
        page: Page | None = None,
        *,
        supplier_name: str = "efghousewares.co.uk",
        supplier_url: str = "https://www.efghousewares.co.uk",
        config_path: str | None = None,
    ):
        self.page = page
        self.supplier_name = supplier_name
        self.supplier_url = supplier_url
        self.config_path = config_path

        self.login_url = "https://www.efghousewares.co.uk/Login"
        self.my_account_url = "https://www.efghousewares.co.uk/MyAccount"
        self.test_product_url = "https://www.efghousewares.co.uk/baltus-night-lights-8hrs-white-pk50"

        # Login form selectors (verified from HTML)
        self.username_selector = "#UserName"
        self.password_selector = "#Password"
        self.login_button_selector = "#dupbtn"

    async def is_authenticated(self, page: Page | None = None) -> bool:
        target_page = page or self.page
        if not target_page:
            return False

        try:
            await target_page.goto(self.my_account_url, wait_until="domcontentloaded", timeout=20000)

            # If redirected to login page, not authenticated
            if "/Login" in (target_page.url or ""):
                log.info("❌ User is not authenticated (redirected to login)")
                return False

            # Logout form presence is a strong indicator
            try:
                logout_form = target_page.locator("form[action*='Account/LogOff']").first
                if await logout_form.is_visible(timeout=1500):
                    # Verify price access (definitive for this supplier)
                    return await self.verify_price_access(target_page)
            except Exception:
                pass

            # Fallback: verify price access directly
            return await self.verify_price_access(target_page)
        except Exception as e:
            log.warning(f"Authentication check failed: {e}")
            return False

    async def login(self, credentials: dict[str, Any], page: Page | None = None) -> bool:
        target_page = page or self.page
        if not target_page:
            log.error("No page available for login")
            return False

        username = credentials.get("username") or credentials.get("email")
        password = credentials.get("password")
        if not username or not password:
            log.error("Missing username/email or password in credentials")
            return False

        try:
            log.info(f"🔄 Starting login process for {username}...")
            await target_page.goto(self.login_url, wait_until="domcontentloaded", timeout=20000)

            log.info("⏳ Waiting for login form...")
            await target_page.wait_for_selector(self.username_selector, timeout=15000)

            log.info("✏️  Entering username...")
            await target_page.fill(self.username_selector, str(username))

            log.info("✏️  Entering password...")
            await target_page.fill(self.password_selector, str(password))

            log.info("🖱️  Clicking login button...")
            await target_page.click(self.login_button_selector)

            log.info("⏳ Waiting for login response...")
            try:
                await target_page.wait_for_load_state("networkidle", timeout=15000)
            except PlaywrightTimeoutError:
                pass

            await asyncio.sleep(1.5)

            if await self.is_authenticated(target_page):
                log.info("✅ Login successful")
                return True

            log.error("❌ Login failed (authentication check returned False)")
            return False
        except Exception as e:
            log.error(f"Login failed with exception: {e}")
            return False

    async def verify_price_access(self, page: Page | None = None) -> bool:
        target_page = page or self.page
        if not target_page:
            return False

        try:
            log.info(f"🔎 Verifying price access via test product: {self.test_product_url}")
            await target_page.goto(self.test_product_url, wait_until="domcontentloaded", timeout=20000)
            try:
                await target_page.wait_for_load_state("networkidle", timeout=8000)
            except PlaywrightTimeoutError:
                pass

            # Give Cloudfy a moment to render pricing widgets
            await target_page.wait_for_timeout(1500)

            # Logged-out indicator on this site
            try:
                login_to_purchase = target_page.locator("text=LOGIN TO PURCHASE").first
                if await login_to_purchase.is_visible(timeout=1500):
                    log.info("❌ Price access not available (LOGIN TO PURCHASE visible)")
                    return False
            except Exception:
                pass

            # Logged-in wholesale price markers (Cloudfy patterns observed on listing + product pages)
            candidate_selectors = [
                "p.price_text span.excUnitPrice",  # Product page: numeric (e.g., 7.04)
                "span.excUnitPrice",  # Product page: numeric
                "span.Price2",  # strongest signal (usually contains numeric price only)
                "div.newprice",  # contains "Price : Ł 10.54" style text
                "span.rrp_price",  # container with "Price : Ł" and nested value
                "span[class*='AlwaysExPrice_']",  # dynamic class with numeric value
            ]

            # Wait briefly for any known price selector to attach (best-effort)
            for selector in candidate_selectors:
                try:
                    await target_page.wait_for_selector(selector, timeout=2500)
                    break
                except Exception:
                    continue

            for selector in candidate_selectors:
                try:
                    locator = target_page.locator(selector)
                    count = await locator.count()
                    if count == 0:
                        continue

                    # Iterate a few matches; the first one may be hidden (e.g., wasPrice display:none)
                    for i in range(min(count, 5)):
                        el = locator.nth(i)
                        try:
                            if not await el.is_visible():
                                continue
                        except Exception:
                            continue

                        text = (await el.text_content()) or ""
                        text = " ".join(text.split())
                        if re.search(r"\b\d+(?:[.,]\d{1,2})?\b", text):
                            log.info(f"✅ Price access verified ({selector} -> '{text[:60]}')")
                            return True
                except Exception:
                    continue

            # If we got here, we didn't see LOGIN TO PURCHASE or any price selector we recognize.
            log.warning(
                f"❌ Price access not verified (no recognized price selectors found). url={target_page.url}"
            )

            # Persist a screenshot for post-mortem debugging (non-fatal if it fails)
            try:
                os.makedirs("OUTPUTS", exist_ok=True)
                await target_page.screenshot(path="OUTPUTS/efghousewares_price_verification_failed.png", full_page=True)
                log.warning("📸 Saved screenshot: OUTPUTS/efghousewares_price_verification_failed.png")
            except Exception as screenshot_err:
                log.debug(f"Could not save screenshot: {screenshot_err}")
            return False
        except Exception as e:
            log.warning(f"Price verification failed: {e}")
            return False

    async def ensure_authenticated_session(self, *args, **kwargs):
        """
        Ensure authenticated session.

        Supported call patterns:
        - ensure_authenticated_session(credentials) -> bool
        - ensure_authenticated_session(page, credentials, force_reauth=True) -> tuple[bool, str]
        """
        force_reauth = bool(kwargs.get("force_reauth", False))

        # Pattern 1: (credentials) -> bool
        if len(args) == 1 and isinstance(args[0], dict) and not hasattr(args[0], "goto"):
            credentials = args[0]
            if not self.page:
                log.error("No page attached; cannot ensure authenticated session")
                return False
            if not force_reauth and await self.is_authenticated(self.page):
                return True
            return await self.login(credentials, self.page)

        # Pattern 2: (page, credentials, force_reauth=...) -> (bool, method)
        if len(args) >= 2 and hasattr(args[0], "goto") and isinstance(args[1], dict):
            page = args[0]
            credentials = args[1]
            self.page = page

            if not force_reauth and await self.is_authenticated(page):
                return True, "already_authenticated"
            ok = await self.login(credentials, page)
            return ok, "login"

        # Keyword-only fallbacks
        page = kwargs.get("page") or (args[0] if args and hasattr(args[0], "goto") else None)
        credentials = kwargs.get("credentials") or kwargs.get("creds")

        if page and credentials:
            self.page = page
            if not force_reauth and await self.is_authenticated(page):
                return True, "already_authenticated"
            ok = await self.login(credentials, page)
            return ok, "login"

        raise TypeError("Unsupported ensure_authenticated_session call signature")


# Backwards-compatible alias
EfghousewaresAuthenticationHelper = SupplierAuthenticationService
