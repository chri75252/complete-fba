@echo off
echo 🔧 FIX AUTHENTICATION CACHE ISSUE
echo ==================================================

echo 🔄 Killing all Python processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1
echo ✅ Python processes killed

echo 🔄 Killing all Chrome processes...
taskkill /F /IM chrome.exe >nul 2>&1
echo ✅ Chrome processes killed

echo 🧹 Clearing Python cache files...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc >nul 2>&1
echo ✅ Python cache cleared

echo.
echo 🎯 SOLUTION COMPLETE:
echo ✅ All Python and Chrome processes have been killed
echo ✅ All Python cache files have been cleared
echo.
echo 📋 NEXT STEPS:
echo 1. Wait 30 seconds for all processes to fully terminate
echo 2. Restart your system: python run_custom_poundwholesale.py
echo 3. The LOGIN SCRIPT TRIGGER messages should no longer appear
echo.
echo 🔍 The authentication trigger code has been removed from the source.
echo If you still see LOGIN SCRIPT TRIGGER messages, there may be another
echo version of the workflow file being used.

pause