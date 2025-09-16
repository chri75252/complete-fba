#!/usr/bin/env python3
"""
Chrome CDP Diagnostic and Fix Script
Comprehensive solution for Chrome Debug Protocol connection issues
"""

import asyncio
import subprocess
import time
import json
import aiohttp
import sys
import os
from pathlib import Path
from playwright.async_api import async_playwright

class ChromeCDPDiagnostic:
    def __init__(self):
        self.chrome_paths = [
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
            "chrome.exe"  # If in PATH
        ]
        self.debug_port = 9222
        self.user_data_dir = "C:\\ChromeDebugProfile"
        
    def print_status(self, message, status="INFO"):
        """Print formatted status message"""
        symbols = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️", "FIX": "🔧"}
        print(f"{symbols.get(status, 'ℹ️')} {message}")
        
    def run_command(self, command, timeout=10):
        """Run command and return result"""
        try:
            result = subprocess.run(
                command, capture_output=True, text=True, 
                timeout=timeout, shell=True
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
            
    def find_chrome_executable(self):
        """Find Chrome executable path"""
        for path in self.chrome_paths:
            if os.path.exists(path):
                self.print_status(f"Found Chrome at: {path}", "SUCCESS")
                return path
        
        # Try to find in PATH
        success, stdout, stderr = self.run_command("where chrome.exe")
        if success and stdout.strip():
            path = stdout.strip().split('\n')[0]
            self.print_status(f"Found Chrome in PATH: {path}", "SUCCESS")
            return path
            
        self.print_status("Chrome executable not found", "ERROR")
        return None
        
    def check_chrome_processes(self):
        """Check current Chrome processes"""
        success, stdout, stderr = self.run_command('tasklist /fi "imagename eq chrome.exe" /fo csv')
        
        if not success:
            self.print_status("Could not check Chrome processes", "ERROR")
            return []
            
        lines = stdout.strip().split('\n')[1:]  # Skip header
        processes = []
        
        for line in lines:
            if line.strip() and "chrome.exe" in line:
                # Parse CSV format: "Image Name","PID","Session Name","Session#","Mem Usage"
                parts = [part.strip('"') for part in line.split('","')]
                if len(parts) >= 2:
                    processes.append({
                        'name': parts[0],
                        'pid': parts[1],
                        'memory': parts[4] if len(parts) > 4 else 'Unknown'
                    })
        
        self.print_status(f"Found {len(processes)} Chrome processes", "INFO")
        return processes
        
    def kill_all_chrome(self):
        """Forcefully kill all Chrome processes"""
        self.print_status("Killing all Chrome processes...", "FIX")
        
        commands = [
            "taskkill /f /im chrome.exe",
            "taskkill /f /im chromedriver.exe",
            "wmic process where \"name='chrome.exe'\" delete"
        ]
        
        for cmd in commands:
            success, stdout, stderr = self.run_command(cmd)
            if success:
                self.print_status(f"Executed: {cmd}", "SUCCESS")
            else:
                self.print_status(f"Failed: {cmd} - {stderr}", "WARNING")
                
        # Wait for processes to terminate
        time.sleep(3)
        
        # Verify all Chrome processes are gone
        remaining = self.check_chrome_processes()
        if remaining:
            self.print_status(f"Warning: {len(remaining)} Chrome processes still running", "WARNING")
            return False
        else:
            self.print_status("All Chrome processes terminated", "SUCCESS")
            return True
            
    def check_port_availability(self, port):
        """Check if port is available or in use"""
        success, stdout, stderr = self.run_command(f'netstat -an | findstr :{port}')
        
        if success and stdout.strip():
            self.print_status(f"Port {port} is in use:", "WARNING")
            for line in stdout.strip().split('\n'):
                self.print_status(f"  {line.strip()}", "INFO")
            return False
        else:
            self.print_status(f"Port {port} is available", "SUCCESS")
            return True
            
    async def test_debug_endpoint(self, port):
        """Test Chrome debug endpoint accessibility"""
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                
                # Test version endpoint
                async with session.get(f"http://localhost:{port}/json/version") as response:
                    if response.status == 200:
                        version_data = await response.json()
                        browser_version = version_data.get('Browser', 'Unknown')
                        ws_endpoint = version_data.get('webSocketDebuggerUrl', 'Not available')
                        
                        self.print_status(f"Chrome debug endpoint accessible!", "SUCCESS")
                        self.print_status(f"Browser: {browser_version}", "INFO")
                        self.print_status(f"WebSocket: {ws_endpoint}", "INFO")
                        
                        # Test tabs/pages endpoint
                        async with session.get(f"http://localhost:{port}/json") as tabs_response:
                            if tabs_response.status == 200:
                                tabs = await tabs_response.json()
                                self.print_status(f"Found {len(tabs)} tabs/pages", "INFO")
                                return True, version_data
                            else:
                                self.print_status(f"Tabs endpoint failed: {tabs_response.status}", "WARNING")
                                return True, version_data  # Version worked, that's enough
                    else:
                        self.print_status(f"Debug endpoint returned status {response.status}", "ERROR")
                        return False, None
                        
        except aiohttp.ClientConnectorError as e:
            self.print_status(f"Cannot connect to debug endpoint: {e}", "ERROR")
            return False, None
        except asyncio.TimeoutError:
            self.print_status(f"Debug endpoint timed out", "ERROR")
            return False, None
        except Exception as e:
            self.print_status(f"Debug endpoint test failed: {e}", "ERROR")
            return False, None
            
    def start_chrome_debug(self, chrome_path):
        """Start Chrome with debug flags"""
        
        # Ensure user data directory exists
        os.makedirs(self.user_data_dir, exist_ok=True)
        
        # Construct Chrome command with debug flags
        cmd = [
            chrome_path,
            f"--remote-debugging-port={self.debug_port}",
            f"--user-data-dir={self.user_data_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-features=TranslateUI",
            "--disable-ipc-flooding-protection"
        ]
        
        self.print_status(f"Starting Chrome with debug flags...", "FIX")
        self.print_status(f"Command: {' '.join(cmd)}", "INFO")
        
        try:
            # Start Chrome process
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            self.print_status(f"Chrome process started with PID: {process.pid}", "SUCCESS")
            
            # Wait for Chrome to start up
            self.print_status("Waiting for Chrome to initialize...", "INFO")
            time.sleep(5)
            
            return True, process
            
        except Exception as e:
            self.print_status(f"Failed to start Chrome: {e}", "ERROR")
            return False, None
            
    async def test_playwright_connection(self, port):
        """Test Playwright CDP connection"""
        try:
            self.print_status("Testing Playwright CDP connection...", "FIX")
            
            playwright = await async_playwright().start()
            
            # Try to connect to Chrome
            browser = await playwright.chromium.connect_over_cdp(
                f"http://localhost:{port}",
                timeout=30000
            )
            
            if browser and browser.is_connected():
                self.print_status("Playwright CDP connection successful!", "SUCCESS")
                
                # Test creating a page
                if browser.contexts:
                    context = browser.contexts[0]
                else:
                    context = await browser.new_context()
                    
                page = await context.new_page()
                await page.goto("about:blank")
                self.print_status("Successfully created and navigated page", "SUCCESS")
                
                await browser.close()
                await playwright.stop()
                return True
            else:
                self.print_status("Playwright connection failed - browser not responsive", "ERROR")
                await playwright.stop()
                return False
                
        except Exception as e:
            self.print_status(f"Playwright connection failed: {e}", "ERROR")
            try:
                await playwright.stop()
            except:
                pass
            return False
            
    async def comprehensive_diagnostic(self):
        """Run comprehensive Chrome CDP diagnostic"""
        self.print_status("=== Chrome CDP Comprehensive Diagnostic ===", "INFO")
        print()
        
        # Step 1: Find Chrome executable
        self.print_status("Step 1: Locating Chrome executable", "INFO")
        chrome_path = self.find_chrome_executable()
        if not chrome_path:
            self.print_status("Cannot proceed without Chrome executable", "ERROR")
            return False
        print()
        
        # Step 2: Check existing Chrome processes
        self.print_status("Step 2: Checking existing Chrome processes", "INFO")
        existing_processes = self.check_chrome_processes()
        print()
        
        # Step 3: Check port availability
        self.print_status("Step 3: Checking debug port availability", "INFO")
        port_available = self.check_port_availability(self.debug_port)
        print()
        
        # Step 4: Test current debug endpoint (if any)
        self.print_status("Step 4: Testing current debug endpoint", "INFO")
        endpoint_working, version_data = await self.test_debug_endpoint(self.debug_port)
        
        if endpoint_working:
            self.print_status("Debug endpoint already working! Testing Playwright...", "SUCCESS")
            playwright_working = await self.test_playwright_connection(self.debug_port)
            if playwright_working:
                self.print_status("All systems working! No fix needed.", "SUCCESS")
                return True
            else:
                self.print_status("Debug endpoint works but Playwright fails", "WARNING")
        print()
        
        # Step 5: Kill all Chrome processes for clean start
        self.print_status("Step 5: Terminating existing Chrome processes", "FIX")
        if existing_processes:
            chrome_killed = self.kill_all_chrome()
            if not chrome_killed:
                self.print_status("Warning: Some Chrome processes may still be running", "WARNING")
        print()
        
        # Step 6: Verify port is now free
        self.print_status("Step 6: Verifying port is free after cleanup", "INFO")
        port_free = self.check_port_availability(self.debug_port)
        if not port_free:
            self.print_status(f"Port {self.debug_port} still in use after cleanup", "ERROR")
            self.print_status("Try rebooting system or use different port", "ERROR")
            return False
        print()
        
        # Step 7: Start Chrome with debug flags
        self.print_status("Step 7: Starting Chrome with debug flags", "FIX")
        chrome_started, chrome_process = self.start_chrome_debug(chrome_path)
        if not chrome_started:
            return False
        print()
        
        # Step 8: Wait and test debug endpoint
        self.print_status("Step 8: Testing new debug endpoint", "INFO")
        
        for attempt in range(6):  # Try for up to 30 seconds
            self.print_status(f"Attempt {attempt + 1}/6 - Testing debug endpoint...", "INFO")
            endpoint_working, version_data = await self.test_debug_endpoint(self.debug_port)
            
            if endpoint_working:
                break
            else:
                if attempt < 5:
                    self.print_status("Debug endpoint not ready yet, waiting...", "WARNING")
                    time.sleep(5)
                else:
                    self.print_status("Debug endpoint never became available", "ERROR")
     