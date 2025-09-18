# Windows Setup Guide - Amazon FBA Agent System

🪟 **Complete guide to run the Amazon FBA Agent System on Windows Command Prompt**

---

## 🚀 Quick Start (5 Minutes)

### **Step 1: Run Windows Setup**
```cmd
setup-windows.bat
```

### **Step 2: Start Chrome with Debug Port**
```cmd
chrome --remote-debugging-port=9222 --user-data-dir=C:\temp\chrome-debug
```

### **Step 3: Set API Key**
```cmd
set OPENAI_API_KEY=your-api-key-here
```

### **Step 4: Run the System**
```cmd
run-windows.bat
```

**That's it!** Your system should now run on Windows without WSL.

---

## 📋 Prerequisites

### **Required Software**
- ✅ **Windows 10/11** (any edition)
- ✅ **Python 3.8+** ([Download here](https://python.org))
- ✅ **Google Chrome** (latest version)
- ✅ **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))

### **Optional but Recommended**
- 🔧 **Windows Terminal** (better than Command Prompt)
- 📊 **Task Manager** (for monitoring memory usage)

---

## 🔧 Detailed Setup Instructions

### **1. Install Python**
1. Download Python from https://python.org
2. ✅ **IMPORTANT**: Check "Add Python to PATH" during installation
3. Verify installation:
   ```cmd
   python --version
   pip --version
   ```

### **2. Download the System**
```cmd
git clone [your-repo-url]
cd Amazon-FBA-Agent-System-v32
```

### **3. Run Automated Setup**
```cmd
setup-windows.bat
```

This will:
- ✅ Install all Python dependencies
- ✅ Install Playwright browsers
- ✅ Create required directories
- ✅ Test Windows memory manager
- ✅ Verify system compatibility

### **4. Test Windows Compatibility**
```cmd
python test_windows_compatibility.py
```

Expected output:
```
🪟 Windows Compatibility Test Suite
==================================================
🧪 Testing Platform Detection...
📊 Detected Platform: Windows
✅ Windows detected - will use Windows-native memory management

🧪 Testing Core Imports...
✅ PassiveExtractionWorkflow imported successfully
✅ BrowserManager imported successfully
✅ WindowsMemoryManager imported successfully

🧪 Testing Memory Management...
✅ Memory usage detected: 8.2GB used
   Chrome processes: 0
   Memory percent: 65.3%
✅ Memory monitoring function working

🏁 Test Results Summary
✅ Tests Passed: 5/5
🎉 ALL TESTS PASSED - System is Windows compatible!
```

---

## 🌐 Chrome Setup (Critical)

The system requires Chrome with debug port enabled:

### **Manual Chrome Start**
```cmd
chrome --remote-debugging-port=9222 --user-data-dir=C:\temp\chrome-debug
```

### **Automatic Chrome Start (Recommended)**
The `run-windows.bat` script will automatically start Chrome if not running.

### **Verify Chrome Debug Port**
1. Open http://localhost:9222 in another browser
2. You should see Chrome DevTools Protocol page
3. If not working, restart Chrome with the command above

---

## 🔑 API Key Configuration

### **Method 1: Environment Variable (Temporary)**
```cmd
set OPENAI_API_KEY=sk-your-api-key-here
python run_custom_poundwholesale.py
```

### **Method 2: .env File (Permanent)**
Create `.env` file in project root:
```
OPENAI_API_KEY=sk-your-api-key-here
```

### **Method 3: System Environment Variable (Global)**
1. Open System Properties → Advanced → Environment Variables
2. Add new variable: `OPENAI_API_KEY` = `sk-your-api-key-here`
3. Restart Command Prompt

---

## 🚀 Running the System

### **Option 1: Automated Script (Recommended)**
```cmd
run-windows.bat
```

This script will:
- ✅ Check Chrome debug port
- ✅ Start Chrome if needed
- ✅ Verify API key
- ✅ Display system info
- ✅ Run the extraction workflow

### **Option 2: Manual Execution**
```cmd
python run_custom_poundwholesale.py
```

---

## 📊 Windows-Specific Features

### **Enhanced Memory Management**
- ✅ **Real Chrome Memory Detection**: Accurate process monitoring
- ✅ **Windows Memory Cleanup**: Native memory management
- ✅ **Process Monitoring**: Direct Chrome process control
- ✅ **No WSL Dependencies**: Pure Windows compatibility

### **Memory Monitoring**
The system now provides accurate Windows memory monitoring:
```
📊 Memory status at product 50: 6.2GB used, Chrome: 1024MB
🪟 Windows: 12 Chrome processes, 1024MB total
✅ Memory monitoring function working
```

### **Automatic Chrome Management**
- 🔄 **Auto-restart**: Chrome restarts when memory exceeds 3GB
- 🧹 **Memory cleanup**: Windows-native memory trimming
- 📊 **Process tracking**: Real-time Chrome process monitoring

---

## 🛠️ Troubleshooting

### **Common Issues & Solutions**

#### **"Chrome debug port not found"**
```cmd
# Kill existing Chrome processes
taskkill /F /IM chrome.exe

# Start Chrome with debug port
chrome --remote-debugging-port=9222 --user-data-dir=C:\temp\chrome-debug
```

#### **"Python not found"**
- Reinstall Python with "Add to PATH" checked
- Or add Python to PATH manually

#### **"Module not found" errors**
```cmd
# Reinstall dependencies
pip install -r requirements.txt
playwright install chromium
```

#### **High memory usage**
- ✅ **Windows handles this automatically** with enhanced memory management
- Monitor with Task Manager
- System will auto-cleanup at 85% memory usage

#### **"Permission denied" errors**
- Run Command Prompt as Administrator
- Check antivirus software blocking Python/Chrome

### **Performance Optimization**

#### **For Long Sessions (8+ hours)**
- ✅ **Automatic**: Windows memory manager handles this
- Monitor Chrome memory in Task Manager
- System will restart Chrome at 3GB usage

#### **For Maximum Performance**
```cmd
# Close unnecessary programs
# Increase virtual memory if needed
# Monitor with Task Manager
```

---

## 📈 Expected Performance Improvements

### **Compared to WSL**
- ✅ **Accurate Memory Monitoring**: Real Chrome usage vs WSL estimates
- ✅ **Stable WebSocket Connections**: No WSL networking layer
- ✅ **Direct Process Control**: Native Chrome management
- ✅ **No VmmemWSL Issues**: Eliminates 13GB WSL memory accumulation
- ✅ **Better Error Handling**: Windows-native error reporting

### **Session Stability**
- 🕐 **8-12+ hour sessions**: Stable long-running operations
- 🔄 **Automatic recovery**: Enhanced restart logic
- 📊 **Real-time monitoring**: Accurate resource tracking

---

## 🔍 Monitoring & Logs

### **Log Files Location**
```
logs/
├── debug/                    # Detailed execution logs
├── application/             # Application-level logs  
├── monitoring/              # Memory and performance logs
└── security/               # Security-related logs
```

### **Real-time Monitoring**
```cmd
# Monitor main log
type logs\debug\run_custom_poundwholesale_*.log

# Monitor memory usage
python -c "from utils.windows_memory_manager import WindowsMemoryManager; import asyncio; print(asyncio.run(WindowsMemoryManager().get_windows_memory_usage()))"
```

### **Task Manager Monitoring**
- 📊 **Chrome processes**: Monitor chrome.exe memory usage
- 🐍 **Python process**: Monitor python.exe memory usage
- 💾 **System memory**: Overall memory usage percentage

---

## 🎯 Success Indicators

### **System Running Correctly**
```
🪟 --- Starting Custom Pound Wholesale Extraction Workflow (Windows Native) ---
✅ Running on Windows - Enhanced memory management enabled
📊 Platform: Windows
🐍 Python: 3.11.0
✅ WindowsMemoryManager created successfully
🌐 Connecting to existing Chrome debug port 9222 for authentication...
✅ Connected to persistent Chrome successfully
```

### **Memory Management Working**
```
📊 Memory status at product 50: 6.2GB used, Chrome: 1024MB
🪟 Windows: 12 Chrome processes, 1024MB total
🧹 Windows garbage collection completed
✅ Memory monitoring function working
```

### **Chrome Integration Working**
```
🔌 Connecting to persistent Chrome on debug port 9222
✅ Connected to persistent Chrome successfully
📄 Using existing context with 1 pages
🪟 Windows Chrome detection: 12 processes, 1024MB total
```

---

## 🆘 Support

### **If You Need Help**
1. **Run the test script**: `python test_windows_compatibility.py`
2. **Check logs**: Look in `logs/debug/` for detailed error messages
3. **Verify Chrome**: Ensure http://localhost:9222 is accessible
4. **Check memory**: Use Task Manager to monitor resource usage

### **Common Success Patterns**
- ✅ All compatibility tests pass
- ✅ Chrome debug port accessible
- ✅ Memory monitoring shows accurate Chrome usage
- ✅ No WSL-related errors in logs
- ✅ System runs for 8+ hours without issues

---

## 🎉 You're Ready!

If you've followed this guide, your Amazon FBA Agent System should now run perfectly on Windows Command Prompt with:

- ✅ **No WSL dependencies**
- ✅ **Enhanced Windows memory management** 
- ✅ **Accurate Chrome process monitoring**
- ✅ **Stable long-running sessions**
- ✅ **Native Windows performance**

**Happy scraping!** 🚀