# Troubleshooting Guide - Amazon FBA Agent System v3.7+

**Last Updated:** August 6, 2025  
**Version:** v3.7+  
**Platform Support:** Windows 10/11, Linux, WSL2  

---

## 🎯 **OVERVIEW**

This comprehensive troubleshooting guide covers common issues, solutions, and diagnostic procedures for the Amazon FBA Agent System v3.7+. The guide is organized by problem category with step-by-step resolution procedures.

---

## 🚨 **QUICK DIAGNOSTIC CHECKLIST**

Before diving into specific issues, run this quick diagnostic:

```bash
# 1. Test system compatibility
python test_windows_compatibility.py

# 2. Check Chrome debug port
curl http://localhost:9222/json/version

# 3. Verify Python dependencies
python -c "import playwright, aiohttp, beautifulsoup4, psutil; print('✅ Dependencies OK')"

# 4. Check configuration
python -c "import json; json.load(open('config/system_config.json')); print('✅ Config OK')"

# 5. Test memory management
python -c "from utils.windows_memory_manager import WindowsMemoryManager; print('✅ Memory Manager OK')"
```

**Expected Output:**
```
✅ Dependencies OK
✅ Config OK
✅ Memory Manager OK
🎉 ALL TESTS PASSED - System is ready!
```

---

## 🌐 **BROWSER & CHROME ISSUES**

### **Issue: Chrome Debug Port Not Accessible**

**Symptoms:**
- Error: "Failed to connect to Chrome on port 9222"
- Browser automation fails to start
- Connection timeout errors

**Diagnosis:**
```bash
# Check if Chrome is running with debug port
curl http://localhost:9222/json/version

# Check if port is in use
netstat -an | grep 9222  # Linux
netstat -an | findstr 9222  # Windows
```

**Solutions:**

#### **Windows Solution:**
```cmd
# 1. Kill existing Chrome processes
taskkill /F /IM chrome.exe

# 2. Start Chrome with debug port
chrome --remote-debugging-port=9222 --user-data-dir=C:\temp\chrome-debug

# 3. Verify connection
curl http://localhost:9222/json/version
```

#### **Linux/WSL Solution:**
```bash
# 1. Kill existing Chrome processes
pkill chrome

# 2. Start Chrome with debug port
google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug --no-sandbox &

# 3. Verify connection
curl http://localhost:9222/json/version
```

### **Issue: Browser Memory Issues**

**Symptoms:**
- Chrome consuming excessive memory (>3GB)
- System becomes unresponsive
- Browser restart failures

**Diagnosis:**
```bash
# Check Chrome memory usage
# Windows:
tasklist /FI "IMAGENAME eq chrome.exe" /FO TABLE

# Linux:
ps aux | grep chrome | awk '{sum+=$6} END {print "Chrome Memory: " sum/1024 " MB"}'
```

**Solutions:**

1. **Automatic Memory Management (Built-in):**
   - System automatically restarts Chrome at 3GB usage
   - Monitor logs: `tail -f logs/health/memory_monitoring_*.log`

2. **Manual Memory Cleanup:**
   ```bash
   # Force browser restart
   python -c "
   import asyncio
   from utils.browser_manager import BrowserManager
   async def restart():
       bm = BrowserManager.get_instance()
       await bm.restart_browser_gracefully()
   asyncio.run(restart())
   "
   ```

### **Issue: Browser Circuit Breaker Activation**

**Symptoms:**
- "Circuit breaker OPENED" messages in logs
- Browser operations suspended
- Automatic recovery attempts

**Diagnosis:**
```bash
# Check circuit breaker status
grep "Circuit Breaker" logs/health/browser_health_*.log | tail -10
```

**Solutions:**

1. **Wait for Automatic Recovery:**
   - Circuit breaker opens after 3 failures
   - Automatically recovers after 5 minutes
   - Monitor: `tail -f logs/health/circuit_breaker_*.log`

2. **Manual Reset:**
   ```python
   # Reset circuit breaker
   from utils.browser_circuit_breaker import BrowserCircuitBreaker
   breaker = BrowserCircuitBreaker()
   breaker.reset()
   print("Circuit breaker reset")
   ```

---

## 💾 **MEMORY MANAGEMENT ISSUES**

### **Issue: High Memory Usage**

**Symptoms:**
- System memory >85%
- Python process consuming >3GB
- Smart memory clearing not working

**Diagnosis:**
```bash
# Check system memory
# Windows:
wmic OS get TotalVisibleMemorySize,FreePhysicalMemory

# Linux:
free -h

# Check Python memory
python -c "
import psutil
proc = psutil.Process()
print(f'Python Memory: {proc.memory_info().rss / 1024 / 1024:.1f} MB')
"
```

**Solutions:**

1. **Verify Smart Memory Management:**
   ```bash
   # Check if smart clearing is working
   grep "SMART MEMORY CLEARED" logs/debug/*.log | tail -5
   
   # Expected: Clearing every ~500 products, keeping 100 recent
   ```

2. **Manual Memory Cleanup:**
   ```python
   # Force memory cleanup
   from tools.passive_extraction_workflow_latest import PassiveExtractionWorkflow
   workflow = PassiveExtractionWorkflow()
   workflow.safe_memory_clear_with_file_fallback()
   print("Memory cleared safely")
   ```

3. **Adjust Memory Thresholds:**
   ```bash
   # Edit .env file
   echo "WINDOWS_MEMORY_WARNING_GB=3" >> .env
   echo "WINDOWS_MEMORY_CRITICAL_GB=4" >> .env
   echo "WINDOWS_MEMORY_EMERGENCY_GB=6" >> .env
   ```

### **Issue: WSL Memory Leak (Linux/WSL)**

**Symptoms:**
- VmmemWSL process consuming 13GB+
- System becomes unresponsive
- WSL memory not releasing

**Diagnosis:**
```bash
# Check WSL memory usage
wsl --list --verbose
wsl --shutdown  # Test if this helps

# Check VmmemWSL in Task Manager (Windows)
```

**Solutions:**

1. **Automatic WSL Management (Built-in):**
   - System monitors WSL memory automatically
   - Triggers cleanup at 4GB/6GB/8GB thresholds
   - Monitor: `tail -f logs/health/wsl_memory_*.log`

2. **Manual WSL Memory Cleanup:**
   ```bash
   # Force WSL memory cleanup
   python -c "
   import asyncio
   from utils.wsl_memory_manager import get_wsl_memory_manager
   async def cleanup():
       manager = get_wsl_memory_manager()
       await manager.emergency_memory_cleanup()
   asyncio.run(cleanup())
   "
   ```

3. **WSL Configuration:**
   ```bash
   # Create/edit ~/.wslconfig
   echo '[wsl2]
   memory=8GB
   processors=4
   swap=2GB' > ~/.wslconfig
   
   # Restart WSL
   wsl --shutdown
   ```

---

## 🔐 **AUTHENTICATION ISSUES**

### **Issue: Supplier Login Failures**

**Symptoms:**
- "Authentication failed" messages
- Products processed without pricing data
- Repeated login attempts

**Diagnosis:**
```bash
# Check authentication logs
grep -i "auth" logs/debug/*.log | tail -10

# Check authentication fallback count
python -c "
from tools.passive_extraction_workflow_latest import PassiveExtractionWorkflow
workflow = PassiveExtractionWorkflow()
count = workflow.get_authentication_fallback_count_from_state()
print(f'Auth fallback count: {count}')
"
```

**Solutions:**

1. **Verify Credentials:**
   ```json
   // Check config/system_config.json
   {
     "credentials": {
       "poundwholesale.co.uk": {
         "username": "your-correct-username",
         "password": "your-correct-password"
       }
     }
   }
   ```

2. **Test Manual Login:**
   ```bash
   # Test authentication manually
   python -c "
   import asyncio
   from tools.supplier_authentication_service import SupplierAuthenticationService
   from utils.browser_manager import BrowserManager
   
   async def test_auth():
       bm = BrowserManager.get_instance()
       await bm.launch_browser(9222)
       page = await bm.get_page('https://www.poundwholesale.co.uk/login')
       
       auth_service = SupplierAuthenticationService(bm)
       credentials = {'username': 'your-username', 'password': 'your-password'}
       
       result = await auth_service.ensure_authenticated_session(page, credentials)
       print(f'Authentication result: {result}')
   
   asyncio.run(test_auth())
   "
   ```

3. **Reset Authentication State:**
   ```bash
   # Clear authentication cache
   rm -f OUTPUTS/CACHE/processing_states/*_auth_state.json
   
   # Restart browser
   python -c "
   import asyncio
   from utils.browser_manager import BrowserManager
   async def restart():
       bm = BrowserManager.get_instance()
       await bm.restart_browser_gracefully()
   asyncio.run(restart())
   "
   ```

### **Issue: Authentication Circuit Breaker**

**Symptoms:**
- "Authentication circuit breaker OPENED"
- Authentication attempts suspended
- Fallback to no-price processing

**Solutions:**

1. **Wait for Recovery:**
   - Circuit breaker opens after 5 consecutive failures
   - Automatically recovers after 2 minutes
   - Monitor: `grep "auth.*circuit" logs/debug/*.log`

2. **Manual Reset:**
   ```python
   # Reset authentication circuit breaker
   from tools.supplier_authentication_service import SupplierAuthenticationService
   auth_service = SupplierAuthenticationService(None)
   auth_service.circuit_breaker.reset()
   print("Authentication circuit breaker reset")
   ```

---

## 📁 **FILE & DATA ISSUES**

### **Issue: Missing Output Files**

**Symptoms:**
- Expected output files not created
- Empty directories in OUTPUTS/
- File permission errors

**Diagnosis:**
```bash
# Check output directory structure
ls -la OUTPUTS/
ls -la OUTPUTS/cached_products/
ls -la OUTPUTS/FBA_ANALYSIS/

# Check file permissions
ls -la config/system_config.json
```

**Solutions:**

1. **Create Missing Directories:**
   ```bash
   # Create required directories
   mkdir -p OUTPUTS/{cached_products,FBA_ANALYSIS/{amazon_cache,linking_maps,financial_reports},CACHE/processing_states,logs/{debug,health,application}}
   ```

2. **Fix File Permissions:**
   ```bash
   # Linux/WSL:
   chmod -R 755 OUTPUTS/
   chmod 644 config/system_config.json
   
   # Windows: Run as Administrator if needed
   ```

3. **Verify File Creation:**
   ```python
   # Test file creation
   import os
   import json
   
   test_file = "OUTPUTS/test_write.json"
   try:
       with open(test_file, 'w') as f:
           json.dump({"test": "success"}, f)
       os.remove(test_file)
       print("✅ File write permissions OK")
   except Exception as e:
       print(f"❌ File write error: {e}")
   ```

### **Issue: Corrupted Configuration Files**

**Symptoms:**
- JSON decode errors
- "Invalid configuration" messages
- System fails to start

**Diagnosis:**
```bash
# Validate JSON syntax
python -m json.tool config/system_config.json

# Check for common issues
grep -n "," config/system_config.json | tail -5  # Trailing commas
```

**Solutions:**

1. **Restore from Backup:**
   ```bash
   # Check for backup files
   ls -la config/system_config.json.bak*
   
   # Restore from backup
   cp config/system_config.json.bak1 config/system_config.json
   ```

2. **Reset to Default Configuration:**
   ```bash
   # Create minimal working configuration
   cat > config/system_config.json << 'EOF'
   {
     "system": {
       "max_products": 1000000,
       "max_products_per_category": 1000,
       "supplier_extraction_batch_size": 100
     },
     "processing_limits": {
       "min_price_gbp": 0.01,
       "max_price_gbp": 20.0
     },
     "chrome": {
       "debug_port": 9222,
       "headless": false
     },
     "authentication": {
       "enabled": true
     }
   }
   EOF
   ```

---

## 🐍 **PYTHON & DEPENDENCY ISSUES**

### **Issue: Import Errors**

**Symptoms:**
- "ModuleNotFoundError" messages
- "No module named 'playwright'" errors
- Import failures on startup

**Diagnosis:**
```bash
# Check Python version
python --version

# Check installed packages
pip list | grep -E "(playwright|aiohttp|beautifulsoup4|psutil)"

# Test critical imports
python -c "import playwright, aiohttp, beautifulsoup4, psutil, openai"
```

**Solutions:**

1. **Reinstall Dependencies:**
   ```bash
   # Reinstall all dependencies
   pip install -r requirements.txt --force-reinstall
   
   # Install Playwright browsers
   playwright install chromium
   playwright install-deps  # Linux only
   ```

2. **Virtual Environment Issues:**
   ```bash
   # Create new virtual environment
   python -m venv venv_new
   
   # Windows:
   venv_new\Scripts\activate
   
   # Linux:
   source venv_new/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Path Issues:**
   ```python
   # Check Python path
   import sys
   print("Python path:")
   for path in sys.path:
       print(f"  {path}")
   
   # Add current directory to path
   import os
   sys.path.insert(0, os.getcwd())
   ```

### **Issue: Playwright Browser Issues**

**Symptoms:**
- "Browser not found" errors
- Playwright installation failures
- Browser launch failures

**Solutions:**

1. **Reinstall Playwright:**
   ```bash
   # Uninstall and reinstall
   pip uninstall playwright
   pip install playwright==1.40.0
   playwright install chromium
   ```

2. **Manual Browser Installation:**
   ```bash
   # Linux: Install system dependencies
   sudo apt update
   sudo apt install -y libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libxss1 libasound2
   
   # Install browsers
   playwright install chromium
   playwright install-deps
   ```

---

## ⚡ **PERFORMANCE ISSUES**

### **Issue: Slow Processing Speed**

**Symptoms:**
- Processing <10 products/hour
- Long delays between operations
- Timeout errors

**Diagnosis:**
```bash
# Check processing rate
grep "products.*hour" logs/debug/*.log | tail -5

# Check for bottlenecks
grep -E "(timeout|slow|delay)" logs/debug/*.log | tail -10
```

**Solutions:**

1. **Optimize Configuration:**
   ```json
   // Increase concurrency in config/system_config.json
   {
     "performance": {
       "max_concurrent_requests": 12,
       "request_timeout_seconds": 30,
       "retry_attempts": 3,
       "rate_limiting": {
         "rate_limit_delay": 1.0,
         "batch_delay": 5.0
       }
     }
   }
   ```

2. **Check Network Issues:**
   ```bash
   # Test network connectivity
   curl -w "@curl-format.txt" -o /dev/null -s "https://www.poundwholesale.co.uk"
   
   # Check DNS resolution
   nslookup www.poundwholesale.co.uk
   ```

3. **System Resource Check:**
   ```bash
   # Check CPU usage
   # Windows: Task Manager
   # Linux: htop or top
   
   # Check disk I/O
   # Windows: Resource Monitor
   # Linux: iotop
   ```

### **Issue: Hash Optimization Not Working**

**Symptoms:**
- Processing already-cached products
- No efficiency gains reported in logs
- Missing "Cache hit" messages

**Diagnosis:**
```bash
# Check hash optimization logs
grep "HASH OPTIMIZATION\|Cache hit" logs/debug/*.log | tail -10

# Check cache file and hash indexes
ls -la OUTPUTS/cached_products/*.json
python -c "
from tools.passive_extraction_workflow_latest import PassiveExtractionWorkflow
workflow = PassiveExtractionWorkflow('poundwholesale.co.uk')
print('Hash optimizer available:', hasattr(workflow, 'hash_optimizer'))
"
```

**Solutions:**

1. **Verify Hash Optimization Status:**
   ```python
   # Check hash optimization functionality
   import json
   
   # Check cache file
   cache_file = "OUTPUTS/cached_products/poundwholesale-co-uk_products_cache.json"
   try:
       with open(cache_file, 'r') as f:
           data = json.load(f)
       print(f"✅ Cache file: {len(data)} products available for indexing")
       
       # Check for EAN and URL fields
       sample = data[0] if data else {}
       print(f"✅ Sample product has EAN: {'ean' in sample}")
       print(f"✅ Sample product has URL: {'url' in sample}")
   except Exception as e:
       print(f"❌ Cache file error: {e}")
   ```

2. **Monitor Hash Performance:**
   ```bash
   # Watch for hash optimization messages during processing
   tail -f logs/debug/*.log | grep -E "(ENHANCED FILTERING|Cache hit|efficiency gain)"
   
   # Expected output:
   # 🔄 Cache hit (EAN): [Product Name] - skipping extraction
   # 📈 Efficiency gain: X/Y = Z% reduction
   # ⚡ Cache optimization saved ~X seconds
   ```

3. **Reset Hash Indexes:**
   ```python
   # Force hash index rebuild
   from tools.passive_extraction_workflow_latest import PassiveExtractionWorkflow
   workflow = PassiveExtractionWorkflow('poundwholesale.co.uk')
   
   # Clear existing indexes to force rebuild
   if hasattr(workflow, 'product_cache_ean_index'):
       delattr(workflow, 'product_cache_ean_index')
   if hasattr(workflow, 'product_cache_url_index'):
       delattr(workflow, 'product_cache_url_index')
   
   print("Hash indexes cleared - will rebuild on next run")
   ```

---

## 📊 **MONITORING & LOGGING ISSUES**

### **Issue: Missing Log Files**

**Symptoms:**
- Empty logs/ directory
- No debug information available
- Monitoring commands fail

**Solutions:**

1. **Create Log Directories:**
   ```bash
   mkdir -p logs/{debug,health,application,system}
   chmod 755 logs/
   ```

2. **Check Logging Configuration:**
   ```python
   # Test logging
   import logging
   
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
       handlers=[
           logging.StreamHandler(),
           logging.FileHandler("logs/debug/test.log")
       ]
   )
   
   logger = logging.getLogger(__name__)
   logger.info("Test log message")
   print("Check logs/debug/test.log for output")
   ```

### **Issue: Log Files Too Large**

**Symptoms:**
- Log files >1GB
- Disk space issues
- Slow log processing

**Solutions:**

1. **Log Rotation:**
   ```bash
   # Archive old logs
   cd logs/debug/
   gzip *.log.$(date -d "7 days ago" +%Y%m%d) 2>/dev/null
   
   # Clean old archives
   find . -name "*.gz" -mtime +30 -delete
   ```

2. **Reduce Log Level:**
   ```json
   // In config/system_config.json
   {
     "monitoring": {
       "log_level": "WARNING"  // Change from INFO to WARNING
     }
   }
   ```

---

## 🔧 **SYSTEM-SPECIFIC ISSUES**

### **Windows-Specific Issues**

#### **Issue: Windows Defender Blocking**

**Symptoms:**
- Files disappearing after creation
- "Access denied" errors
- Antivirus warnings

**Solutions:**

1. **Add Exclusions:**
   - Open Windows Defender
   - Add folder exclusion for project directory
   - Add process exclusion for python.exe and chrome.exe

2. **Run as Administrator:**
   ```cmd
   # Run Command Prompt as Administrator
   # Navigate to project directory
   # Run system normally
   ```

#### **Issue: Windows Path Issues**

**Symptoms:**
- "File not found" errors
- Path separator issues
- Long path problems

**Solutions:**

1. **Enable Long Paths:**
   ```cmd
   # Run as Administrator
   reg add "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 1
   ```

2. **Use Short Paths:**
   ```cmd
   # Move project to shorter path
   # Example: C:\FBA\ instead of C:\Users\username\Desktop\Amazon-FBA-Agent-System-v32
   ```

### **Linux/WSL-Specific Issues**

#### **Issue: Permission Denied**

**Symptoms:**
- Cannot create files
- Cannot execute scripts
- Permission errors

**Solutions:**

1. **Fix Permissions:**
   ```bash
   # Fix file permissions
   chmod +x *.py
   chmod -R 755 .
   
   # Fix ownership
   sudo chown -R $USER:$USER .
   ```

2. **WSL Permissions:**
   ```bash
   # Add to ~/.bashrc
   echo 'umask 022' >> ~/.bashrc
   source ~/.bashrc
   ```

---

## 🆘 **EMERGENCY PROCEDURES**

### **Complete System Reset**

If all else fails, perform a complete system reset:

```bash
# 1. Stop all processes
pkill python  # Linux
taskkill /F /IM python.exe  # Windows

pkill chrome  # Linux
taskkill /F /IM chrome.exe  # Windows

# 2. Clear all caches
rm -rf OUTPUTS/CACHE/*
rm -rf logs/*
rm -rf __pycache__/
rm -rf */__pycache__/

# 3. Reset configuration
cp config/system_config.json.bak config/system_config.json

# 4. Reinstall dependencies
pip install -r requirements.txt --force-reinstall
playwright install chromium

# 5. Test system
python test_windows_compatibility.py

# 6. Restart system
python run_custom_poundwholesale.py
```

### **Data Recovery**

If data appears lost:

```bash
# Check for backup files
find . -name "*.backup" -o -name "*.bak*"

# Check for temporary files
find OUTPUTS/ -name "*.tmp" -o -name "*.temp"

# Restore from most recent backup
ls -la OUTPUTS/cached_products/*.backup
cp OUTPUTS/cached_products/latest.backup OUTPUTS/cached_products/poundwholesale-co-uk_products_cache.json
```

---

## 📞 **GETTING HELP**

### **Diagnostic Information to Collect**

When seeking help, collect this information:

```bash
# System information
echo "=== SYSTEM INFORMATION ==="
python --version
pip --version
uname -a  # Linux
systeminfo  # Windows

# Configuration status
echo "=== CONFIGURATION STATUS ==="
python -c "import json; print('Config OK' if json.load(open('config/system_config.json')) else 'Config Error')"

# Recent logs
echo "=== RECENT ERRORS ==="
grep -i error logs/debug/*.log | tail -10

# Memory status
echo "=== MEMORY STATUS ==="
python -c "
import psutil
mem = psutil.virtual_memory()
print(f'Memory: {mem.percent}% used, {mem.available/1024/1024/1024:.1f}GB available')
"

# Chrome status
echo "=== CHROME STATUS ==="
curl -s http://localhost:9222/json/version || echo "Chrome debug port not accessible"
```

### **Support Checklist**

Before reporting issues:

- ✅ Run diagnostic checklist
- ✅ Check recent logs for errors
- ✅ Verify Chrome debug port accessibility
- ✅ Test with minimal configuration
- ✅ Try system reset if appropriate
- ✅ Collect diagnostic information

---

**Troubleshooting Status:** ✅ Comprehensive with Hash Optimization  
**Last Updated:** August 6, 2025  
**Coverage:** Windows, Linux, WSL2  
**Support Level:** Production Ready