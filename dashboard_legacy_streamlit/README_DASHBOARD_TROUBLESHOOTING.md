# FBA Dashboard Troubleshooting Guide

## 🚨 Issue: Blank Page in Streamlit Dashboard

### **Root Causes Identified**

1. **Path Resolution Failures**: Dashboard couldn't find critical data files
2. **Timeout Issues**: Large JSON files causing infinite loading
3. **Auto-refresh Loops**: Rapid refresh preventing proper rendering
4. **Import Errors**: Module path resolution problems
5. **Missing Error Handling**: Silent failures in data loading

### **✅ Solutions Implemented**

## **Solution 1: Use Fixed Dashboard Files**

Instead of the original `app.py` and `metrics_core.py`, use the fixed versions:

```bash
# Navigate to dashboard directory
cd dashboard

# Run the fixed dashboard
python run_dashboard.py
```

**Key Improvements in Fixed Version:**
- ✅ **Auto-detect base directory** instead of manual input
- ✅ **Improved supplier name resolution** (handles both formats)
- ✅ **Performance limits** for large files (5.9MB+ linking maps)
- ✅ **Better error handling** with user-friendly messages
- ✅ **Disabled auto-refresh by default** (60s interval)
- ✅ **Validation checks** before attempting to load data
- ✅ **Graceful degradation** when files are missing

## **Solution 2: Manual Launch Options**

### **Option A: Direct Streamlit Launch**
```bash
# From project root directory
streamlit run dashboard/app_fixed.py --server.port 8501
```

### **Option B: Python Launcher (Recommended)**
```bash
# From project root directory
cd dashboard
python run_dashboard.py
```

### **Option C: Virtual Environment**
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/WSL
# venv\Scripts\activate   # Windows

# Install requirements
pip install streamlit pandas

# Run dashboard
python run_dashboard.py
```

## **Solution 3: Data Validation**

Before running the dashboard, ensure your data is available:

### **Check Required Files:**
```bash
# From project root
ls -la OUTPUTS/CACHE/processing_states/          # Should contain *processing_state.json
ls -la OUTPUTS/FBA_ANALYSIS/linking_maps/        # Should contain supplier folders
ls -la OUTPUTS/FBA_ANALYSIS/financial_reports/   # Should contain CSV files
ls -la logs/debug/                                # Should contain log files
```

### **Expected File Structure:**
```
OUTPUTS/
├── CACHE/
│   └── processing_states/
│       └── poundwholesale_co_uk_processing_state.json
├── FBA_ANALYSIS/
│   ├── linking_maps/
│   │   ├── poundwholesale.co.uk/
│   │   │   └── linking_map.json
│   └── financial_reports/
│       └── fba_financial_report_*.csv
└── logs/
    └── debug/
        └── run_custom_*.log
```

## **Solution 4: Configuration Options**

### **Supplier Name Matching:**
The fixed dashboard handles multiple supplier name formats:
- `poundwholesale_co_uk` (underscore format)
- `poundwholesale.co.uk` (dot format)
- Custom supplier names

### **Base Directory:**
The dashboard auto-detects the base directory, but you can override:
- Set environment variable: `FBA_BASE_DIR=/path/to/your/project`
- Or use the sidebar input field

### **Auto-refresh:**
- Default: 60 seconds (disabled for debugging)
- Set to 0 to disable completely
- Recommended: Keep disabled while troubleshooting

## **Solution 5: Debug Mode**

### **Enable Debug Logging:**
```bash
# Run with debug logging
streamlit run dashboard/app_fixed.py --logger.level debug
```

### **Check Dashboard Logs:**
```bash
# From project root
logs/debug/
└── dashboard_*.log  # Dashboard-specific logs
```

## **Common Issues & Fixes**

### **Issue 1: "Import Error: metrics_core"**
**Fix**: Ensure you're running from the project root directory, not the dashboard directory.

### **Issue 2: "State file not found"**
**Fix**:
1. Run the FBA system at least once to generate data
2. Check that `OUTPUTS/CACHE/processing_states/*_processing_state.json` exists
3. Verify supplier name matches data directory structure

### **Issue 3: "Linking map file not found"**
**Fix**:
1. Check linking maps directory: `OUTPUTS/FBA_ANALYSIS/linking_maps/`
2. Verify supplier folder format (dotted vs underscore)
3. Ensure linking_map.json exists in supplier folder

### **Issue 4: Dashboard loads but shows no data**
**Fix**:
1. Check file permissions
2. Verify files are not corrupted (try opening JSON files in text editor)
3. Check for large file size warnings in dashboard
4. Review error messages in sidebar

### **Issue 5: Auto-refresh causing infinite loading**
**Fix**:
1. Set auto-refresh to 0 in sidebar
2. Use fixed version (app_fixed.py) which has better refresh handling
3. Clear browser cache and reload

## **Performance Optimization**

### **Large File Handling:**
- Linking maps > 10MB are automatically sampled
- Financial reports > 50MB per file are skipped
- Log files > 10MB show reduced line count

### **Memory Management:**
- JSON files are streamed rather than fully loaded
- Caching prevents repeated file reads
- Sample limits prevent memory exhaustion

## **Testing the Fix**

### **Step 1: Verify Fixed Files Exist**
```bash
ls dashboard/app_fixed.py
ls dashboard/metrics_core_fixed.py
ls dashboard/run_dashboard.py
```

### **Step 2: Test Import Functionality**
```bash
cd dashboard
python -c "from metrics_core_fixed import load_metrics; print('✅ Import successful')"
```

### **Step 3: Run Fixed Dashboard**
```bash
cd dashboard
python run_dashboard.py
```

### **Step 4: Verify Dashboard Functionality**
- Dashboard should load without blank page
- Error messages should appear if data files are missing
- Auto-refresh should work properly (if enabled)
- Performance should be acceptable even with large data files

## **Next Steps**

1. **Run the fixed dashboard**: `cd dashboard && python run_dashboard.py`
2. **Check for data availability**: Look at the error messages in the sidebar
3. **Verify supplier name**: Ensure it matches your data directory structure
4. **Monitor performance**: Large files should be sampled automatically
5. **Contact support**: If issues persist, provide the error messages from the dashboard

## **Developer Notes**

The key changes in the fixed version:

1. **Path Resolution**: Multiple supplier name formats supported
2. **Error Handling**: Graceful degradation with user-friendly messages
3. **Performance**: Sampling and limits for large files
4. **Caching**: Improved cache invalidation
5. **Auto-refresh**: Better control and error handling
6. **Diagnostics**: Comprehensive error reporting and path validation

The fixed version should resolve the blank page issue and provide better visibility into any remaining problems.