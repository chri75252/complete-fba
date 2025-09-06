# Chrome CDP Debugging - Controlled Experiment Matrix

## Root Cause Analysis Summary
- **Primary Issue**: `svchost.exe` process 2452 hijacking port 9222 on IPv4
- **Secondary Issue**: Chrome 139.x preferring IPv6 binding for debug interfaces
- **Tertiary Issue**: System service intercepting HTTP requests meant for Chrome

## Experiment Environment
- **System**: Windows 11 22H2 build 22621
- **Chrome Version**: 139.0.7258.155
- **Current State**: 42 Chrome processes running
- **Profile Path**: C:\ChromeDebugProfile
- **Target Port**: 9222 (hijacked by svchost.exe PID 2452)

---

## PHASE 1: PORT CONFLICT RESOLUTION (15 minutes)

### Experiment 1.1: Service Process Identification
**Objective**: Identify exact service hijacking port 9222
**Duration**: 3 minutes
**Risk Level**: LOW

**Pre-Flight Checklist:**
```bash
# Backup current Chrome profile
robocopy "C:\ChromeDebugProfile" "C:\ChromeDebugProfile_BACKUP_$(Get-Date -Format 'yyyyMMdd_HHmmss')" /E /R:1 /W:1

# Document baseline
netstat -ano | findstr :9222 > baseline_port_9222.txt
tasklist /FI "PID eq 2452" /FO CSV > baseline_svchost_2452.txt
```

**Experiment Steps:**
1. **Service Deep Analysis**:
   ```bash
   # Identify service details
   tasklist /SVC /FI "PID eq 2452"
   sc query type= service state= all | findstr /C:"svchost"
   Get-Process -Id 2452 | Select-Object ProcessName, Id, StartTime, Path
   ```

2. **Network Stack Analysis**:
   ```bash
   # Check IPv4/IPv6 binding patterns
   netstat -ano -p TCP | findstr :9222
   netstat -ano -p TCP6 | findstr :9222
   netsh interface portproxy show all
   ```

**Success Criteria:**
- Service name and owner identified
- IPv4/IPv6 binding pattern documented
- No system disruption

**Rollback Procedure:**
- No changes made - observation only
- Restore from backup if Chrome profile affected

---

### Experiment 1.2: Alternative Port Testing
**Objective**: Test Chrome CDP on alternative ports
**Duration**: 5 minutes
**Risk Level**: LOW

**Port Candidates**: 9223, 9224, 9225, 9333

**Experiment Steps:**
1. **Port Availability Check**:
   ```bash
   # Test each candidate port
   foreach ($port in @(9223,9224,9225,9333)) {
       $result = Test-NetConnection -ComputerName localhost -Port $port
       Write-Output "Port $port : $($result.TcpTestSucceeded)"
   }
   ```

2. **Chrome Startup with Alternative Port**:
   ```bash
   # Test each port systematically
   "C:\Program Files\Google\Chrome\Application\chrome.exe" `
   --remote-debugging-port=9223 `
   --user-data-dir="C:\ChromeDebugProfile_TEST" `
   --no-first-run --no-default-browser-check
   ```

3. **CDP Connectivity Validation**:
   ```bash
   # Test each alternative port
   foreach ($port in @(9223,9224,9225,9333)) {
       curl -s "http://localhost:$port/json/version"
   }
   ```

**Success Criteria:**
- At least one alternative port accepts CDP connections
- Chrome starts successfully with new port
- `curl` test returns valid JSON response

**Rollback Procedure:**
```bash
# Kill test Chrome instances
Get-Process chrome | Where-Object {$_.Path -like "*Chrome*"} | Stop-Process -Force
# Remove test profile
Remove-Item "C:\ChromeDebugProfile_TEST" -Recurse -Force -ErrorAction SilentlyContinue
```

---

### Experiment 1.3: IPv6 Binding Enforcement
**Objective**: Force Chrome to bind CDP on IPv4
**Duration**: 4 minutes
**Risk Level**: MEDIUM

**Experiment Steps:**
1. **IPv4 Binding Test**:
   ```bash
   # Force IPv4 binding with explicit flags
   "C:\Program Files\Google\Chrome\Application\chrome.exe" `
   --remote-debugging-port=9223 `
   --remote-debugging-address=127.0.0.1 `
   --disable-ipv6 `
   --user-data-dir="C:\ChromeDebugProfile_IPV4TEST" `
   --no-first-run --no-default-browser-check
   ```

2. **Binding Verification**:
   ```bash
   # Verify IPv4-only binding
   netstat -ano | findstr :9223
   curl -s "http://127.0.0.1:9223/json/version"
   curl -s "http://[::1]:9223/json/version" # Should fail
   ```

**Success Criteria:**
- Chrome binds only to IPv4 (127.0.0.1:9223)
- IPv6 binding test fails as expected
- CDP responds correctly on IPv4

**Rollback Procedure:**
```bash
Get-Process chrome | Where-Object {$_.CommandLine -like "*IPV4TEST*"} | Stop-Process -Force
Remove-Item "C:\ChromeDebugProfile_IPV4TEST" -Recurse -Force -ErrorAction SilentlyContinue
```

---

### Experiment 1.4: Service Conflict Resolution
**Objective**: Test if stopping conflicting service resolves issue
**Duration**: 3 minutes
**Risk Level**: HIGH (Service modification)

**⚠️ WARNING**: Only proceed if service is non-critical

**Experiment Steps:**
1. **Service Safety Check**:
   ```bash
   # Identify service critically BEFORE stopping
   Get-Service | Where-Object {$_.Status -eq "Running"} | 
   ForEach-Object {
       $svcProcess = Get-Process -Id (Get-WmiObject -Query "SELECT ProcessId FROM Win32_Service WHERE Name='$($_.Name)'").ProcessId -ErrorAction SilentlyContinue
       if ($svcProcess.Id -eq 2452) {
           Write-Output "Service: $($_.Name) - Critical: $($_.StartType)"
       }
   }
   ```

2. **Controlled Service Stop** (ONLY if non-critical):
   ```bash
   # EMERGENCY ROLLBACK READY
   # Stop service temporarily
   Stop-Service -Name [SERVICE_NAME] -Force
   
   # Immediate test
   "C:\Program Files\Google\Chrome\Application\chrome.exe" `
   --remote-debugging-port=9222 `
   --user-data-dir="C:\ChromeDebugProfile" `
   --no-first-run --no-default-browser-check
   
   curl -s "http://localhost:9222/json/version"
   ```

**Success Criteria:**
- Port 9222 becomes available
- Chrome successfully binds to port 9222
- CDP connectivity restored

**IMMEDIATE Rollback Procedure:**
```bash
# RESTART SERVICE IMMEDIATELY
Start-Service -Name [SERVICE_NAME]
# Verify service restoration
Get-Service -Name [SERVICE_NAME]
```

---

## PHASE 2: CHROME STARTUP OPTIMIZATION (20 minutes)

### Experiment 2.1: Performance Flags Testing
**Objective**: Test performance-optimized Chrome startup flags
**Duration**: 8 minutes
**Risk Level**: LOW

**Flag Combinations to Test**:
1. **Minimal Flags**: Basic CDP only
2. **Performance Optimized**: Speed-focused flags
3. **Stability Optimized**: Reliability-focused flags

**Experiment Steps:**
1. **Minimal Configuration**:
   ```bash
   # Test 1: Minimal flags
   "C:\Program Files\Google\Chrome\Application\chrome.exe" `
   --remote-debugging-port=9223 `
   --user-data-dir="C:\ChromeDebugProfile_MINIMAL" `
   --no-first-run
   ```

2. **Performance Configuration**:
   ```bash
   # Test 2: Performance flags
   "C:\Program Files\Google\Chrome\Application\chrome.exe" `
   --remote-debugging-port=9223 `
   --user-data-dir="C:\ChromeDebugProfile_PERF" `
   --no-first-run --no-default-browser-check --no-sandbox `
   --disable-gpu --disable-dev-shm-usage --disable-extensions `
   --disable-plugins --disable-images --disable-javascript `
   --disable-background-timer-throttling --disable-renderer-backgrounding
   ```

3. **Stability Configuration**:
   ```bash
   # Test 3: Stability flags  
   "C:\Program Files\Google\Chrome\Application\chrome.exe" `
   --remote-debugging-port=9223 `
   --user-data-dir="C:\ChromeDebugProfile_STABLE" `
   --no-first-run --no-default-browser-check `
   --disable-backgrounding-occluded-windows `
   --disable-background-timer-throttling `
   --disable-renderer-backgrounding --disable-features=TranslateUI
   ```

**Success Criteria for Each Test**:
- Chrome starts within 10 seconds
- CDP responds within 5 seconds of startup
- `test_cdp_fix.py` executes successfully
- Memory usage < 500MB baseline

**Measurement Protocol**:
```bash
# Startup time measurement
$startTime = Get-Date
# [START CHROME COMMAND]
# Wait for CDP availability
do {
    $response = curl -s "http://localhost:9223/json/version" 2>$null
    Start-Sleep 1
} while ([string]::IsNullOrEmpty($response))
$endTime = Get-Date
$startupTime = ($endTime - $startTime).TotalSeconds
Write-Output "Startup time: $startupTime seconds"
```

**Rollback Procedure**:
```bash
# Clean up test profiles
Get-Process chrome | Where-Object {$_.CommandLine -like "*ChromeDebugProfile_*"} | Stop-Process -Force
Remove-Item "C:\ChromeDebugProfile_MINIMAL" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "C:\ChromeDebugProfile_PERF" -Recurse -Force -ErrorAction SilentlyContinue  
Remove-Item "C:\ChromeDebugProfile_STABLE" -Recurse -Force -ErrorAction SilentlyContinue
```

---

### Experiment 2.2: Startup Timing Optimization
**Objective**: Optimize Chrome startup sequence and warmup
**Duration**: 6 minutes
**Risk Level**: LOW

**Experiment Steps:**
1. **Cold Start Baseline**:
   ```bash
   # Measure cold start performance
   Get-Process chrome | Stop-Process -Force
   Start-Sleep 3
   
   $coldStart = Measure-Command {
       "C:\Program Files\Google\Chrome\Application\chrome.exe" `
       --remote-debugging-port=9223 `
       --user-data-dir="C:\ChromeDebugProfile_TIMING" `
       --no-first-run --no-default-browser-check
       
       # Wait for CDP availability
       do {
           $response = curl -s "http://localhost:9223/json/version" 2>$null
           Start-Sleep 0.5
       } while ([string]::IsNullOrEmpty($response))
   }
   ```

2. **Warm Start Optimization**:
   ```bash
   # Pre-warm system components
   # Keep one Chrome process running as warmup
   Start-Process "chrome.exe" -ArgumentList "--no-first-run","--no-default-browser-check"
   
   # Test warm start performance
   $warmStart = Measure-Command {
       "C:\Program Files\Google\Chrome\Application\chrome.exe" `
       --remote-debugging-port=9224 `
       --user-data-dir="C:\ChromeDebugProfile_WARM" `
       --no-first-run --no-default-browser-check
       
       do {
           $response = curl -s "http://localhost:9224/json/version" 2>$null
           Start-Sleep 0.5
       } while ([string]::IsNullOrEmpty($response))
   }
   ```

3. **Performance Analysis**:
   ```bash
   Write-Output "Cold start time: $($coldStart.TotalSeconds) seconds"
   Write-Output "Warm start time: $($warmStart.TotalSeconds) seconds"
   Write-Output "Improvement: $(($coldStart.TotalSeconds - $warmStart.TotalSeconds)) seconds"
   ```

**Success Criteria**:
- Warm start < 5 seconds
- Cold start < 15 seconds  
- No memory leaks after multiple restarts
- CDP remains stable throughout timing tests

**Rollback Procedure**:
```bash
Get-Process chrome | Where-Object {$_.CommandLine -like "*TIMING*" -or $_.CommandLine -like "*WARM*"} | Stop-Process -Force
Remove-Item "C:\ChromeDebugProfile_TIMING" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "C:\ChromeDebugProfile_WARM" -Recurse -Force -ErrorAction SilentlyContinue
```

---

### Experiment 2.3: Network Stack Optimization
**Objective**: Optimize network bindings and connection handling
**Duration**: 6 minutes  
**Risk Level**: MEDIUM

**Experiment Steps:**
1. **Network Interface Binding Test**:
   ```bash
   # Test different interface bindings
   "C:\Program Files\Google\Chrome\Application\chrome.exe" `
   --remote-debugging-port=9223 `
   --remote-debugging-address=0.0.0.0 `
   --user-data-dir="C:\ChromeDebugProfile_NETTEST" `
   --no-first-run --no-default-browser-check
   ```

2. **Connection Pool Optimization**:
   ```bash
   # Test with connection pooling flags
   "C:\Program Files\Google\Chrome\Application\chrome.exe" `
   --remote-debugging-port=9224 `
   --remote-debugging-address=127.0.0.1 `
   --max-connections-per-host=10 `
   --aggressive-cache-discard `
   --user-data-dir="C:\ChromeDebugProfile_POOL" `
   --no-first-run --no-default-browser-check
   ```

3. **Network Validation**:
   ```bash
   # Test accessibility from different interfaces
   curl -s "http://127.0.0.1:9223/json/version"
   curl -s "http://localhost:9223/json/version"  
   curl -s "http://127.0.0.1:9224/json/version"
   
   # Test concurrent connections
   1..5 | ForEach-Object -Parallel {
       curl -s "http://127.0.0.1:9223/json/version"
   }
   ```

**Success Criteria**:
- All interface bindings successful
- Concurrent connections handled properly
- No connection timeouts under load
- Network overhead minimal

**Rollback Procedure**:
```bash
Get-Process chrome | Where-Object {$_.CommandLine -like "*NETTEST*" -or $_.CommandLine -like "*POOL*"} | Stop-Process -Force
Remove-Item "C:\ChromeDebugProfile_NETTEST" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "C:\ChromeDebugProfile_POOL" -Recurse -Force -ErrorAction SilentlyContinue
```

---

## PHASE 3: INTEGRATION TESTING (15 minutes)

### Experiment 3.1: browser_manager.py Integration
**Objective**: Test optimal configuration with existing browser_manager.py
**Duration**: 8 minutes
**Risk Level**: MEDIUM

**⚠️ CONSTRAINT**: NO modifications to browser_manager.py code

**Experiment Steps:**
1. **Configuration Discovery**:
   ```bash
   # Analyze current browser_manager.py configuration
   python -c "
   import sys
   sys.path.append('.')
   from utils.browser_manager import BrowserManager
   bm = BrowserManager()
   print('Current debug port:', getattr(bm, 'debug_port', 'Not found'))
   print('Current flags:', getattr(bm, 'chrome_flags', 'Not found'))
   "
   ```

2. **Environment Variable Override**:
   ```bash
   # Test environment-based configuration override
   $env:CHROME_DEBUG_PORT = "9223"
   $env:CHROME_DEBUG_ADDRESS = "127.0.0.1"
   
   # Test browser_manager with new environment
   python test_cdp_fix.py
   ```

3. **Profile Directory Override**:
   ```bash
   # Test with optimized profile directory
   $env:CHROME_PROFILE_DIR = "C:\ChromeDebugProfile_OPTIMIZED"
   
   # Create optimized profile
   mkdir "C:\ChromeDebugProfile_OPTIMIZED" -ErrorAction SilentlyContinue
   
   python -c "
   from utils.browser_manager import BrowserManager
   bm = BrowserManager()
   # Test initialization with environment overrides
   print('Browser manager initialized successfully')
   "
   ```

**Success Criteria**:
- browser_manager.py accepts environment variable overrides
- test_cdp_fix.py executes without errors
- Chrome profile remains functional
- No regression in browser automation functionality

**Rollback Procedure**:
```bash
# Reset environment variables
Remove-Item Env:CHROME_DEBUG_PORT -ErrorAction SilentlyContinue
Remove-Item Env:CHROME_DEBUG_ADDRESS -ErrorAction SilentlyContinue
Remove-Item Env:CHROME_PROFILE_DIR -ErrorAction SilentlyContinue

# Clean up test profile
Remove-Item "C:\ChromeDebugProfile_OPTIMIZED" -Recurse -Force -ErrorAction SilentlyContinue
```

---

### Experiment 3.2: End-to-End Workflow Validation  
**Objective**: Validate full system functionality with optimal configuration
**Duration**: 7 minutes
**Risk Level**: LOW

**Experiment Steps:**
1. **Optimal Configuration Application**:
   ```bash
   # Apply best configuration from previous experiments
   # (Use results from Phase 1 & 2)
   $OPTIMAL_PORT = 9223  # From Phase 1 results
   $OPTIMAL_FLAGS = "--no-first-run --no-default-browser-check --disable-backgrounding-occluded-windows"
   
   # Set environment for system test
   $env:CHROME_DEBUG_PORT = $OPTIMAL_PORT
   $env:CHROME_DEBUG_ADDRESS = "127.0.0.1"
   ```

2. **System Integration Test**:
   ```bash
   # Test full workflow components
   python -c "
   import sys, time
   sys.path.append('.')
   
   # Test 1: Browser manager initialization
   print('Testing browser_manager...')
   from utils.browser_manager import BrowserManager
   bm = BrowserManager()
   print('✓ BrowserManager initialized')
   
   # Test 2: CDP connectivity
   print('Testing CDP connectivity...')
   import subprocess
   result = subprocess.run(['curl', '-s', f'http://127.0.0.1:{$OPTIMAL_PORT}/json/version'], 
                          capture_output=True, text=True)
   if result.returncode == 0:
       print('✓ CDP connection successful')
   else:
       print('✗ CDP connection failed')
   
   print('Integration test completed')
   "
   ```

3. **Performance Validation**:
   ```bash
   # Measure end-to-end performance
   python test_cdp_fix.py --performance-test
   ```

**Success Criteria**:
- All system components initialize successfully
- CDP connectivity stable throughout test
- Performance metrics within acceptable ranges
- No errors in system logs
- User Chrome profile remains intact

**Final System State Verification**:
```bash
# Document final state
Write-Output "=== FINAL SYSTEM STATE ===" > experiment_results.txt
Write-Output "Date: $(Get-Date)" >> experiment_results.txt
Write-Output "Optimal Port: $env:CHROME_DEBUG_PORT" >> experiment_results.txt
Write-Output "Debug Address: $env:CHROME_DEBUG_ADDRESS" >> experiment_results.txt

# Test final configuration
curl -s "http://$env:CHROME_DEBUG_ADDRESS:$env:CHROME_DEBUG_PORT/json/version" >> experiment_results.txt
python test_cdp_fix.py >> experiment_results.txt 2>&1

Write-Output "Experiment matrix completed. Results in experiment_results.txt"
```

---

## EMERGENCY PROCEDURES

### Complete System Rollback
**Execute if any experiment causes system instability**:

```bash
# EMERGENCY ROLLBACK SCRIPT
Write-Output "EXECUTING EMERGENCY ROLLBACK"

# 1. Kill all test Chrome processes
Get-Process chrome | Where-Object {
    $_.CommandLine -like "*ChromeDebugProfile_*" -or
    $_.CommandLine -like "*TEST*" -or  
    $_.CommandLine -like "*PERF*" -or
    $_.CommandLine -like "*STABLE*"
} | Stop-Process -Force

# 2. Restore original Chrome profile
if (Test-Path "C:\ChromeDebugProfile_BACKUP_*") {
    $backup = Get-ChildItem "C:\ChromeDebugProfile_BACKUP_*" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    Remove-Item "C:\ChromeDebugProfile" -Recurse -Force -ErrorAction SilentlyContinue
    robocopy $backup.FullName "C:\ChromeDebugProfile" /E /R:1 /W:1
}

# 3. Reset environment variables
Remove-Item Env:CHROME_* -ErrorAction SilentlyContinue

# 4. Clean up test directories
Get-ChildItem "C:\" | Where-Object {$_.Name -like "ChromeDebugProfile_*" -and $_.Name -notlike "*BACKUP*"} | Remove-Item -Recurse -Force

# 5. Restart any services stopped during testing
# (Service restart commands would be added here based on Phase 1 results)

Write-Output "Emergency rollback completed"
```

### Service Recovery Protocol
**If Windows services were affected**:

```bash
# SERVICE RECOVERY
$criticalServices = @("Themes", "AudioSrv", "BITS", "Winmgmt")
foreach ($service in $criticalServices) {
    $svc = Get-Service $service -ErrorAction SilentlyContinue
    if ($svc.Status -ne "Running") {
        Start-Service $service
        Write-Output "Restarted service: $service"
    }
}
```

---

## EXPERIMENT SUCCESS METRICS

### Quantitative Success Criteria
- **CDP Connectivity**: `curl` response time < 1000ms
- **Chrome Startup**: < 10 seconds cold start, < 5 seconds warm start
- **Memory Usage**: < 500MB baseline for debug instance
- **CPU Usage**: < 10% sustained during idle
- **Network Latency**: < 50ms localhost response time

### Qualitative Success Indicators
- **System Stability**: No crashes or hanging processes
- **User Experience**: Chrome profile functionality preserved
- **Integration Health**: browser_manager.py operates without modification
- **Reproducibility**: Results consistent across multiple test runs

### Documentation Requirements
Each experiment must produce:
- Command-line execution log
- Performance measurement data
- Error/warning messages captured
- Before/after system state comparison
- Rollback procedure validation

---

**EXPERIMENT MATRIX STATUS**: Ready for execution  
**ESTIMATED TOTAL TIME**: 50 minutes  
**RISK LEVEL**: LOW to MEDIUM (with proper rollback procedures)  
**PREREQUISITES**: Chrome debug profile backup, administrative privileges for service analysis