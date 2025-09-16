#!/usr/bin/env python3
"""
Chrome CDP Final Fix - Resolves IPv4/IPv6 binding issues in Chrome v139
Provides comprehensive solution for CDP connectivity problems
"""

import subprocess
import time
import json
import asyncio
from pathlib import Path

def kill_all_browsers():
    """Kill all Chromium-based browsers including Chrome and Comet"""
    browsers = ['chrome.exe', 'msedge.exe', 'comet.exe', 'chromium.exe']
    
    for browser in browsers:
        try:
            subprocess.run(['taskkill', '/f', '/im', browser], 
                         capture_output=True, check=False)
            print(f"  🔄 Stopped {browser}")
        except Exception:
            pass
    
    print("  ⏳ Waiting 5 seconds for process cleanup...")
    time.sleep(5)

def start_chrome_ipv4_forced():
    """Start Chrome with forced IPv4 binding"""
    print("🚀 Starting Chrome with forced IPv4 binding...")
    
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    profile_path = r"C:\ChromeDebugProfile"
    
    cmd = [
        chrome_path,
        '--remote-debugging-port=9222',
        '--remote-debugging-address=127.0.0.1',  # Force IPv4
        f'--user-data-dir={profile_path}',
        '--disable-web-security',
        '--disable-features=VizDisplayCompositor,TranslateUI',
        '--no-first-run',
        '--no-default-browser-check',
        '--disable-background-mode',
        '--disable-background-timer-throttling',
        '--process-per-site'
    ]
    
    try:
        subprocess.Popen(cmd, shell=False)
        print("  ✅ Chrome started with IPv4 forced binding")
        return True
    except Exception as e:
        print(f"  ❌ Failed to start Chrome: {e}")
        return False

def test_debug_interface():
    """Test both IPv4 and IPv6 debug interfaces"""
    import urllib.request
    import urllib.error
    
    print("🌐 Testing debug interfaces...")
    
    # Test IPv4
    try:
        url = "http://127.0.0.1:9222/json/version"
        req = urllib.request.Request(url)
        response = urllib.request.urlopen(req, timeout=5)
        data = json.loads(response.read().decode())
        print(f"  ✅ IPv4 Success: {data.get('Browser', 'Unknown')}")
        return 'ipv4', url
    except Exception as e:
        print(f"  ❌ IPv4 failed: {e}")
    
    # Test IPv6
    try:
        url = "http://[::1]:9222/json/version"
        req = urllib.request.Request(url)
        response = urllib.request.urlopen(req, timeout=5)
        data = json.loads(response.read().decode())
        print(f"  ✅ IPv6 Success: {data.get('Browser', 'Unknown')}")
        return 'ipv6', url
    except Exception as e:
        print(f"  ❌ IPv6 failed: {e}")
    
    return None, None

async def test_playwright_connection(url):
    """Test Playwright CDP connection"""
    from playwright.async_api import async_playwright
    
    print(f"🎭 Testing Playwright connection to {url}...")
    
    playwright = await async_playwright().start()
    try:
        browser = await playwright.chromium.connect_over_cdp(
            url.replace('json/version', ''),
            timeout=10000
        )
        print("  ✅ Playwright CDP connection successful!")
        
        # Test basic functionality
        contexts = browser.contexts
        print(f"  📊 Active contexts: {len(contexts)}")
        
        if contexts:
            pages = contexts[0].pages
            print(f"  📄 Active pages: {len(pages)}")
        
        await browser.close()
        return True
        
    except Exception as e:
        print(f"  ❌ Playwright connection failed: {e}")
        return False
    finally:
        await playwright.stop()

def update_system_config_for_fix():
    """Update system config if needed"""
    config_path = Path("config/system_config.json")
    
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Ensure Chrome config exists
            if 'chrome' not in config:
                config['chrome'] = {}
            
            # Note the IPv4 requirement
            config['chrome']['debug_port'] = 9222
            config['chrome']['binding'] = 'ipv4_forced'
            config['chrome']['startup_flags'] = [
                '--remote-debugging-address=127.0.0.1',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
            
            # Backup and save
            backup_path = config_path.with_suffix('.json.backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            print(f"  ✅ Updated {config_path} with IPv4 binding configuration")
            return True
            
        except Exception as e:
            print(f"  ❌ Failed to update config: {e}")
    
    return False

def main():
    print("🎯 CHROME CDP FINAL FIX")
    print("=" * 50)
    print("🎨 Comet Browser aware solution")
    print("🌐 IPv4/IPv6 binding resolution")
    print("📋 Chrome v139 compatibility")
    print()
    
    # Step 1: Clean browser shutdown
    print("📋 Step 1: Stopping all Chromium browsers...")
    kill_all_browsers()
    
    # Step 2: Start Chrome with IPv4 forced
    print("📋 Step 2: Starting Chrome with IPv4 binding...")
    if not start_chrome_ipv4_forced():
        print("❌ Failed to start Chrome")
        return False
    
    # Step 3: Wait and test
    print("📋 Step 3: Waiting for initialization...")
    time.sleep(8)
    
    interface_type, interface_url = test_debug_interface()
    
    if not interface_type:
        print("❌ No debug interface responding")
        return False
    
    # Step 4: Test Playwright connection
    print("📋 Step 4: Testing Playwright CDP connection...")
    playwright_success = asyncio.run(test_playwright_connection(interface_url))
    
    if playwright_success:
        print("\n🎉 SUCCESS: Chrome CDP connectivity restored!")
        print(f"  🌐 Interface: {interface_type.upper()}")
        print(f"  📡 URL: {interface_url}")
        print("\n🔧 Next Steps:")
        print("  1. Run: python test_cdp_fix.py")
        print("  2. Test: python run_custom_poundwholesale.py")
        
        # Update config
        print("\n📋 Updating system configuration...")
        update_system_config_for_fix()
        
        return True
    else:
        print("\n❌ Playwright connection still failing")
        print("🔍 Manual investigation required")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Chrome CDP Final Fix Complete!")
        else:
            print("\n❌ Fix incomplete - manual intervention needed")
    except KeyboardInterrupt:
        print("\n🛑 Fix interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
