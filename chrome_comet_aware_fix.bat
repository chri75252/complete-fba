@echo off
echo ======================================
echo Chrome CDP Fix with Comet Browser Awareness
echo ======================================

echo Stopping ALL Chromium-based browsers...
taskkill /f /im chrome.exe >nul 2>&1
taskkill /f /im msedge.exe >nul 2>&1
taskkill /f /im comet.exe >nul 2>&1

echo Waiting 5 seconds for process cleanup...
timeout /t 5 >nul

echo Starting Chrome with debug port 9222...
start "Chrome Debug" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --remote-debugging-address=127.0.0.1 --user-data-dir="C:\ChromeDebugProfile" --no-first-run --no-default-browser-check

echo Waiting 8 seconds for initialization...
timeout /t 8 >nul

echo Testing debug interface...
curl -m 5 -s http://127.0.0.1:9222/json/version
if %errorlevel% equ 0 (
    echo SUCCESS: Chrome debug interface is responding
) else (
    echo Trying IPv6...
    curl -m 5 -s http://[::1]:9222/json/version
    if %errorlevel% equ 0 (
        echo SUCCESS: Chrome debug interface responding on IPv6
    ) else (
        echo FAILED: Debug interface not responding
    )
)

echo.
echo Chrome CDP Fix Complete
pause
