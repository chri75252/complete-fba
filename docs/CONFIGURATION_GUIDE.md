# Configuration Guide - Amazon FBA Agent System v3.7+

**Last Updated:** August 6, 2025  
**Version:** v3.7+  
**Status:** ✅ Production Ready with Hash Optimization  

---

## 🎯 **OVERVIEW**

This guide provides comprehensive documentation for configuring the Amazon FBA Agent System v3.7+. The system uses a centralized configuration approach with `config/system_config.json` as the primary configuration file, supplemented by environment variables. Recent enhancements include hash-based optimization settings and enhanced memory management configurations.

---

## 📁 **CONFIGURATION FILES**

### **Primary Configuration**
- **`config/system_config.json`** - Main system configuration
- **`.env`** - Environment variables and API keys
- **`config/supplier_configs/`** - Supplier-specific configurations
- **`requirements.txt`** - Python dependencies

### **Configuration Hierarchy**
1. **Environment Variables** (highest priority)
2. **System Config JSON** (primary configuration)
3. **Default Values** (fallback)

---

## ⚙️ **SYSTEM CONFIGURATION (`config/system_config.json`)**

### **System Settings**

```json
{
  "system": {
    "name": "Amazon FBA Agent System",
    "version": "3.5.0",
    "environment": "production",
    "test_mode": false,
    "max_products": 1000000,
    "max_analyzed_products": 1000000,
    "max_products_per_category": 1000,
    "max_products_per_cycle": 20,
    "supplier_extraction_batch_size": 100,
    "linking_map_batch_size": 50,
    "financial_report_batch_size": 100,
    "output_root": "OUTPUTS",
    "reuse_browser": true,
    "max_tabs": 2
  }
}
```

#### **Key System Settings**

| Setting | Default | Description |
|---------|---------|-------------|
| `max_products` | `1000000` | Maximum products to process (0 = unlimited) |
| `max_products_per_category` | `1000` | Maximum products per category |
| `supplier_extraction_batch_size` | `100` | Products processed in each batch |
| `linking_map_batch_size` | `50` | Batch size for Amazon linking |
| `output_root` | `"OUTPUTS"` | Base directory for all outputs |
| `reuse_browser` | `true` | Reuse browser instances for efficiency |

### **Processing Limits**

```json
{
  "processing_limits": {
    "max_products_per_category": 1000,
    "max_products_per_run": 1000000,
    "min_price_gbp": 0.01,
    "max_price_gbp": 20.0,
    "price_midpoint_gbp": 20.0,
    "min_products_per_category": 1,
    "category_validation": {
      "enabled": true,
      "min_products_per_category": 1,
      "timeout_seconds": 15
    }
  }
}
```

#### **Price Filtering**

| Setting | Default | Description |
|---------|---------|-------------|
| `min_price_gbp` | `0.01` | Minimum product price in GBP |
| `max_price_gbp` | `20.0` | Maximum product price in GBP |
| `price_midpoint_gbp` | `20.0` | Price midpoint for analysis |

### **Performance Configuration**

```json
{
  "performance": {
    "max_concurrent_requests": 8,
    "request_timeout_seconds": 45,
    "retry_attempts": 5,
    "retry_delay_seconds": 3,
    "batch_size": 100,
    "rate_limiting": {
      "rate_limit_delay": 1.5,
      "batch_delay": 8.0,
      "ai_batch_size": 10
    },
    "timeouts": {
      "navigation_timeout_ms": 90000,
      "search_input_timeout_ms": 10000,
      "results_wait_timeout_ms": 30000,
      "selector_wait_timeout_ms": 45000,
      "page_load_timeout_ms": 20000,
      "http_request_timeout_seconds": 30
    }
  }
}
```

#### **Performance Tuning**

| Setting | Default | Description |
|---------|---------|-------------|
| `max_concurrent_requests` | `8` | Maximum concurrent HTTP requests |
| `request_timeout_seconds` | `45` | HTTP request timeout |
| `retry_attempts` | `5` | Number of retry attempts |
| `rate_limit_delay` | `1.5` | Delay between requests (seconds) |

### **Chrome Browser Configuration**

```json
{
  "chrome": {
    "debug_port": 9222,
    "headless": false,
    "extensions": [
      "Keepa",
      "SellerAmp"
    ]
  }
}
```

#### **Browser Settings**

| Setting | Default | Description |
|---------|---------|-------------|
| `debug_port` | `9222` | Chrome debug port for automation |
| `headless` | `false` | Run Chrome in headless mode |
| `extensions` | `["Keepa", "SellerAmp"]` | Required Chrome extensions |

### **Authentication Configuration**

```json
{
  "authentication": {
    "enabled": true,
    "startup_verification": true,
    "consecutive_failure_threshold": 5,
    "primary_periodic_interval": 300,
    "secondary_periodic_interval": 450,
    "max_consecutive_auth_failures": 10,
    "auth_failure_delay_seconds": 60,
    "min_products_between_logins": 50,
    "adaptive_threshold_enabled": true,
    "circuit_breaker": {
      "enabled": true,
      "failure_threshold": 5,
      "recovery_timeout_seconds": 120
    }
  }
}
```

#### **Authentication Settings**

| Setting | Default | Description |
|---------|---------|-------------|
| `enabled` | `true` | Enable authentication system |
| `consecutive_failure_threshold` | `5` | Failures before circuit breaker |
| `primary_periodic_interval` | `300` | Primary auth check interval (seconds) |
| `circuit_breaker.enabled` | `true` | Enable circuit breaker protection |

### **Analysis Configuration**

```json
{
  "analysis": {
    "min_roi_percent": 15.0,
    "min_profit_per_unit": 0.25,
    "min_rating": 3.0,
    "min_reviews": 5,
    "max_sales_rank": 500000,
    "min_monthly_sales": 1,
    "max_competition_level": 20,
    "excluded_categories": [],
    "target_categories": [
      "Home & Kitchen",
      "Pet Supplies",
      "Toys",
      "Health & Personal Care",
      "Office Products",
      "Sports & Outdoors",
      "Baby Products",
      "Beauty & Personal Care",
      "Automotive",
      "Garden & Outdoor",
      "Tools & Home Improvement"
    ]
  }
}
```

#### **Profitability Criteria**

| Setting | Default | Description |
|---------|---------|-------------|
| `min_roi_percent` | `15.0` | Minimum ROI percentage |
| `min_profit_per_unit` | `0.25` | Minimum profit per unit (GBP) |
| `min_rating` | `3.0` | Minimum Amazon product rating |
| `min_reviews` | `5` | Minimum number of reviews |
| `max_sales_rank` | `500000` | Maximum Amazon sales rank |

### **Supplier Credentials**

```json
{
  "credentials": {
    "poundwholesale.co.uk": {
      "username": "your-username",
      "password": "your-password"
    }
  }
}
```

**⚠️ Security Note**: Store sensitive credentials in environment variables instead of the config file for production use.

---

## 🌍 **ENVIRONMENT VARIABLES (`.env`)**

### **API Keys**

```bash
# OpenAI API (optional - AI features disabled by default)
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini

# Keepa API (optional - for enhanced Amazon data)
KEEPA_API_KEY=your-keepa-api-key-here
```

### **Browser Configuration**

```bash
# Chrome Debug Port
CHROME_DEBUG_PORT=9222

# Browser Timeouts
NAVIGATION_TIMEOUT=60000
PAGE_LOAD_TIMEOUT=20000
```

### **Memory Management**

```bash
# Browser Memory Management
BROWSER_MEMORY_THRESHOLD_MB=2048
CIRCUIT_BREAKER_FAILURE_THRESHOLD=3
CIRCUIT_BREAKER_TIMEOUT_SECONDS=300

# Windows Memory Management
WINDOWS_MEMORY_WARNING_GB=4
WINDOWS_MEMORY_CRITICAL_GB=6
WINDOWS_MEMORY_EMERGENCY_GB=8

# WSL Memory Management (Linux/WSL)
WSL_MEMORY_WARNING_GB=4
WSL_MEMORY_CRITICAL_GB=6
WSL_MEMORY_EMERGENCY_GB=8
```

### **Performance Tuning**

```bash
# Request Configuration
MAX_CONCURRENT_REQUESTS=8
REQUEST_TIMEOUT_SECONDS=45
RETRY_ATTEMPTS=5
RETRY_DELAY_SECONDS=3

# Rate Limiting
RATE_LIMIT_DELAY=1.5
BATCH_DELAY=8.0

# Processing Limits
MAX_PRODUCTS_PER_CATEGORY=1000
SUPPLIER_EXTRACTION_BATCH_SIZE=100
```

### **Supplier Authentication**

```bash
# Pound Wholesale Credentials
POUNDWHOLESALE_USERNAME=your-username
POUNDWHOLESALE_PASSWORD=your-password

# Authentication Settings
AUTH_CONSECUTIVE_FAILURE_THRESHOLD=5
AUTH_FAILURE_DELAY_SECONDS=60
MIN_PRODUCTS_BETWEEN_LOGINS=50
```

---

## 🔧 **ADVANCED CONFIGURATION**

### **Hybrid Processing Mode**

```json
{
  "hybrid_processing": {
    "enabled": true,
    "switch_to_amazon_after_categories": 1,
    "processing_modes": {
      "chunked": {
        "description": "Alternate between supplier extraction and Amazon analysis",
        "enabled": true,
        "chunk_size_categories": 1
      }
    },
    "memory_management": {
      "clear_cache_between_phases": false,
      "max_memory_threshold_mb": 16384,
      "file_based_counting": {
        "enabled": true,
        "safe_clear_frequency": 100,
        "preserve_critical_counters": true,
        "fallback_to_memory": false
      }
    }
  }
}
```

### **Smart Memory Management with Hash Optimization**

```json
{
  "memory_management": {
    "smart_clearing": {
      "enabled": true,
      "accumulation_threshold": 500,
      "continuity_window": 100,
      "force_gc_on_clear": true
    },
    "file_based_counting": {
      "enabled": true,
      "safe_clear_frequency": 100,
      "preserve_critical_counters": true
    },
    "hash_optimization": {
      "enabled": true,
      "cache_indexing": true,
      "dual_index_mode": true,
      "performance_logging": true
    }
  }
}
```

### **Hash-Based Duplicate Prevention**

```json
{
  "duplicate_prevention": {
    "product_cache_lookup": {
      "enabled": true,
      "index_by_ean": true,
      "index_by_url": true,
      "rebuild_on_cache_change": true
    },
    "linking_map_lookup": {
      "enabled": true,
      "hash_based": true,
      "performance_tracking": true
    },
    "multi_category_deduplication": {
      "enabled": true,
      "cross_category_tracking": true,
      "efficiency_reporting": true
    }
  }
}
```

### **Cache Configuration**

```json
{
  "cache": {
    "enabled": true,
    "ttl_hours": 10000,
    "max_size_mb": 2048,
    "selective_clear_config": {
      "preserve_analyzed_products": true,
      "preserve_ai_categories": true,
      "preserve_linking_map": true,
      "clear_unanalyzed_only": false,
      "clear_failed_extractions": false
    }
  }
}
```

### **Monitoring Configuration**

```json
{
  "monitoring": {
    "enabled": true,
    "metrics_interval": 300,
    "health_check_interval": 600,
    "log_level": "INFO",
    "alert_thresholds": {
      "cpu_percent": 90,
      "memory_percent": 90,
      "error_rate_per_hour": 50
    }
  }
}
```

---

## 🎛️ **CONFIGURATION PROFILES**

### **Development Profile**

```json
{
  "system": {
    "environment": "development",
    "test_mode": true,
    "max_products": 100,
    "max_products_per_category": 10
  },
  "chrome": {
    "headless": false
  },
  "monitoring": {
    "log_level": "DEBUG"
  }
}
```

### **Production Profile**

```json
{
  "system": {
    "environment": "production",
    "test_mode": false,
    "max_products": 1000000,
    "max_products_per_category": 1000
  },
  "chrome": {
    "headless": false
  },
  "monitoring": {
    "log_level": "INFO"
  }
}
```

### **Testing Profile**

```json
{
  "system": {
    "environment": "testing",
    "test_mode": true,
    "max_products": 50,
    "max_products_per_category": 5
  },
  "chrome": {
    "headless": true
  },
  "monitoring": {
    "log_level": "DEBUG"
  }
}
```

---

## 🔍 **CONFIGURATION VALIDATION**

### **Validation Script**

```python
# validate_config.py
import json
import os
from pathlib import Path

def validate_system_config():
    """Validate system configuration file"""
    config_path = Path("config/system_config.json")
    
    if not config_path.exists():
        print("❌ config/system_config.json not found")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Validate required sections
        required_sections = ['system', 'processing_limits', 'performance', 'chrome']
        for section in required_sections:
            if section not in config:
                print(f"❌ Missing required section: {section}")
                return False
        
        # Validate critical settings
        if config['chrome']['debug_port'] != 9222:
            print("⚠️ Chrome debug port should be 9222")
        
        if config['system']['max_products'] <= 0:
            print("⚠️ max_products should be > 0 (or use 1000000 for unlimited)")
        
        print("✅ Configuration validation passed")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in config file: {e}")
        return False

if __name__ == "__main__":
    validate_system_config()
```

### **Environment Validation**

```bash
# validate_env.sh
#!/bin/bash

echo "🔍 Validating Environment Configuration..."

# Check Chrome debug port
if curl -s http://localhost:9222/json/version > /dev/null; then
    echo "✅ Chrome debug port accessible"
else
    echo "❌ Chrome debug port not accessible"
    echo "   Start Chrome with: chrome --remote-debugging-port=9222"
fi

# Check Python dependencies
if python -c "import playwright, aiohttp, beautifulsoup4" 2>/dev/null; then
    echo "✅ Python dependencies installed"
else
    echo "❌ Missing Python dependencies"
    echo "   Run: pip install -r requirements.txt"
fi

# Check output directories
if [ -d "OUTPUTS" ]; then
    echo "✅ Output directory exists"
else
    echo "⚠️ Creating output directory"
    mkdir -p OUTPUTS
fi

echo "🎯 Environment validation complete"
```

---

## 🛠️ **CONFIGURATION TROUBLESHOOTING**

### **Common Issues**

#### **Chrome Debug Port Issues**

```bash
# Check if port is in use
netstat -an | grep 9222

# Kill existing Chrome processes
# Windows:
taskkill /F /IM chrome.exe

# Linux:
pkill chrome

# Restart Chrome with debug port
chrome --remote-debugging-port=9222 --user-data-dir=C:\temp\chrome-debug
```

#### **Configuration File Errors**

```bash
# Validate JSON syntax
python -m json.tool config/system_config.json

# Check for common issues
grep -n "," config/system_config.json | tail -5  # Trailing commas
grep -n '"' config/system_config.json | grep -v ':'  # Unmatched quotes
```

#### **Memory Configuration Issues**

```bash
# Check system memory
# Windows:
wmic OS get TotalVisibleMemorySize,FreePhysicalMemory

# Linux:
free -h

# Adjust memory thresholds based on available memory
# For 8GB systems: warning=4GB, critical=6GB
# For 16GB systems: warning=8GB, critical=12GB
```

### **Performance Optimization**

#### **For High-Volume Processing**

```json
{
  "performance": {
    "max_concurrent_requests": 12,
    "batch_size": 200,
    "rate_limiting": {
      "rate_limit_delay": 1.0,
      "batch_delay": 5.0
    }
  },
  "system": {
    "supplier_extraction_batch_size": 200,
    "max_products_per_cycle": 50
  }
}
```

#### **For Memory-Constrained Systems**

```json
{
  "performance": {
    "max_concurrent_requests": 4,
    "batch_size": 50
  },
  "system": {
    "supplier_extraction_batch_size": 50,
    "max_products_per_cycle": 10
  },
  "memory_management": {
    "smart_clearing": {
      "accumulation_threshold": 200,
      "continuity_window": 50
    }
  }
}
```

---

## 📊 **CONFIGURATION MONITORING**

### **Real-time Configuration Status**

```bash
# Monitor configuration usage
tail -f logs/debug/*.log | grep -E "(config|setting|threshold)"

# Check memory thresholds
grep "Memory threshold" logs/health/*.log | tail -10

# Monitor batch processing
grep "batch.*size" logs/debug/*.log | tail -10
```

### **Configuration Metrics**

```python
# config_metrics.py
import json
from pathlib import Path

def get_config_metrics():
    """Get configuration metrics"""
    with open("config/system_config.json", 'r') as f:
        config = json.load(f)
    
    metrics = {
        "max_products": config["system"]["max_products"],
        "batch_size": config["system"]["supplier_extraction_batch_size"],
        "price_range": f"£{config['processing_limits']['min_price_gbp']}-£{config['processing_limits']['max_price_gbp']}",
        "concurrent_requests": config["performance"]["max_concurrent_requests"],
        "chrome_debug_port": config["chrome"]["debug_port"],
        "authentication_enabled": config["authentication"]["enabled"]
    }
    
    return metrics

if __name__ == "__main__":
    metrics = get_config_metrics()
    for key, value in metrics.items():
        print(f"{key}: {value}")
```

---

## 🎯 **BEST PRACTICES**

### **Configuration Management**

1. **Version Control**: Keep configuration files in version control
2. **Environment Separation**: Use different configs for dev/test/prod
3. **Sensitive Data**: Store credentials in environment variables
4. **Validation**: Validate configuration before deployment
5. **Documentation**: Document all configuration changes

### **Security Considerations**

1. **Credential Storage**: Never commit credentials to version control
2. **API Keys**: Use environment variables for API keys
3. **File Permissions**: Restrict access to configuration files
4. **Encryption**: Consider encrypting sensitive configuration data

### **Performance Tuning**

1. **Memory Monitoring**: Adjust memory thresholds based on system capacity
2. **Batch Sizing**: Optimize batch sizes for your hardware
3. **Concurrency**: Balance concurrent requests with system resources
4. **Rate Limiting**: Respect supplier rate limits

---

**Configuration Status:** ✅ Complete  
**Validation:** ✅ Tested  
**Production Ready:** ✅ Yes  
**Last Updated:** July 25, 2025