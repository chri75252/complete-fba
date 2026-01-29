#!/usr/bin/env python3
"""
Standalone test for dkwholesale authentication fix
Tests the corrected selectors: #CustomerEmail and button:text("Sign in")
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from playwright.async_api import async_playwright
from tools.dkwholesale.supplier_authentication_service import DkwholesaleAuthenticationHelper
from config.system_config_loader import SystemConfigLoader

async def test_authentication():
    """Test authentication with corrected selectors"""
    print("🧪 Testing dkwholesale authentication fix...")
    print("=" * 60)

    config_loader = SystemConfigLoader()
    credentials = config_loader.get_credentials('dkwholesale.com')

    if not credentials:
        print("❌ No credentials found for dkwholesale.com")
        return False

    print(f"✅ Using credentials: {credentials['username']}")

    async with async_playwright() as p:
        print("🌐 Connecting to Chrome...")
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = await context.new_page()

        try:
            print("\n🔐 Initializing authentication helper...")
            auth_helper = DkwholesaleAuthenticationHelper(page)

            # Test 1: Check if already authenticated
            print("\n1️⃣  Checking authentication status...")
            is_auth = await auth_helper.is_authenticated()

            if is_auth:
                print("✅ Already authenticated!")
                return True
            else:
                print("🔐 Not authenticated, proceeding with login...")

            # Test 2: Attempt login
            print("\n2️⃣  Testing login with corrected selectors...")
            print("   → Using selector: #CustomerEmail (visible field)")
            print("   → Using selector: button:text('Sign in') (login button)")

            login_result = await auth_helper.login(credentials)

            if login_result:
                print("\n✅ Login successful!")

                # Test 3: Verify price access
                print("\n3️⃣  Verifying price access...")
                price_verified = await auth_helper.verify_price_access()

                if price_verified:
                    print("✅ Price access verified - authentication complete!")
                    return True
                else:
                    print("⚠️  Authenticated but price verification failed")
                    print("   Possible causes:")
                    print("   - Session not fully established")
                    print("   - Test product URL changed")
                    return False
            else:
                print("\n❌ Login failed!")
                print("   Screenshot saved to: OUTPUTS/dkwholesale_login_failed.png")
                return False

        except Exception as e:
            print(f"\n❌ Authentication test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            await browser.close()

async def test_selectors():
    """Test selectors directly without authentication"""
    print("\n🔍 Testing selectors directly...")
    print("=" * 60)

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = await context.new_page()

        try:
            # Navigate to login page
            print("🌐 Navigating to login page...")
            await page.goto("https://dkwholesale.com/account/login", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)

            # Test email field visibility
            print("\n1️⃣  Testing #CustomerEmail field...")
            customer_email = await page.query_selector('#CustomerEmail')
            if customer_email:
                is_visible = await customer_email.is_visible()
                bounding_box = await customer_email.bounding_box()
                print(f"   ✅ Found #CustomerEmail")
                print(f"   📏 Visible: {is_visible}")
                print(f"   📐 Bounding box: {bounding_box}")

                if is_visible:
                    print("   ✨ Field is visible - can be used for login")
                else:
                    print("   ⚠️  Field is not visible - may cause issues")
            else:
                print("   ❌ #CustomerEmail not found!")

            # Test recover email (should be invisible)
            print("\n2️⃣  Testing #RecoverEmail field...")
            recover_email = await page.query_selector('#RecoverEmail')
            if recover_email:
                is_visible = await recover_email.is_visible()
                bounding_box = await recover_email.bounding_box()
                print(f"   ✅ Found #RecoverEmail")
                print(f"   📏 Visible: {is_visible}")
                print(f"   📐 Bounding box: {bounding_box}")

                if not is_visible:
                    print("   ✨ Field is invisible - correctly NOT used for login")
                else:
                    print("   ⚠️  Field is visible - may conflict with #CustomerEmail")
            else:
                print("   ❌ #RecoverEmail not found!")

            # Test login button
            print("\n3️⃣  Testing login button selectors...")

            # Test generic submit button
            submit_buttons = await page.query_selector_all('button[type="submit"]')
            print(f"   Found {len(submit_buttons)} button[type=\"submit\"]")

            for i, btn in enumerate(submit_buttons):
                text = await btn.text_content()
                print(f"   Button {i}: text=\"{text.strip()}\"")

            # Test text-based selector
            signin_button = await page.query_selector('button:text("Sign in")')
            if signin_button:
                print(f"   ✅ button:text(\"Sign in\") - Found specific login button")
                is_visible = await signin_button.is_visible()
                print(f"   📏 Visible: {is_visible}")
            else:
                print(f"   ❌ button:text(\"Sign in\") - Not found")

            return True

        except Exception as e:
            print(f"❌ Selector test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            await browser.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Dkwholesale Authentication Fix Test")
    print("=" * 60)
    print()

    # Run selector tests first
    success1 = asyncio.run(test_selectors())

    # Run full authentication test
    print("\n" + "=" * 60)
    success2 = asyncio.run(test_authentication())

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Selector Tests: {'✅ PASSED' if success1 else '❌ FAILED'}")
    print(f"Auth Tests: {'✅ PASSED' if success2 else '❌ FAILED'}")

    if success1 and success2:
        print("\n🎉 All tests passed! Authentication fix is working.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Review output above.")
        sys.exit(1)
