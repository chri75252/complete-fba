# Project Structure & Organization

## Core Architecture

The system follows a modular architecture with clear separation of concerns:

```
├── tools/                          # Core processing components
│   ├── passive_extraction_workflow_latest.py  # Main orchestrator
│   ├── configurable_supplier_scraper.py       # Supplier data extraction
│   ├── amazon_playwright_extractor.py         # Amazon data extraction
│   ├── FBA_Financial_calculator.py            # Financial analysis
│   └── cache_manager.py                       # Data caching
├── utils/                          # Utility components
│   ├── windows_save_guardian.py               # Atomic file operations
│   ├── browser_manager.py                     # Browser health management
│   ├── sentinel_monitor.py                    # System monitoring
│   └── path_manager.py                        # Path standardization
├── config/                         # Configuration management
│   ├── system_config.json                     # Main system config
│   ├── system_config_loader.py                # Config loading
│   └── supplier_configs/                      # Supplier-specific configs
└── OUTPUTS/                        # Generated outputs
    ├── cached_products/                       # Supplier product cache
    ├── FBA_ANALYSIS/                          # Amazon analysis results
    └── CACHE/                                 # Processing state
```

## Entry Points

- **`run_custom_poundwholesale.py`**: Primary launcher script
- **`run_complete_fba_system.py`**: Alternative system launcher

## Key Directories

### `/tools` - Core Processing
Contains the main workflow engine and processing components. The `passive_extraction_workflow_latest.py` is the central orchestrator that coordinates all other components.

### `/utils` - Utilities
Platform-specific utilities and cross-cutting concerns:
- Memory management (Windows/Linux specific)
- File operations (atomic saves, path handling)
- Browser management and health monitoring
- System monitoring and alerting

### `/config` - Configuration
Centralized configuration management:
- `system_config.json`: Single source of truth for all settings
- Supplier-specific configurations
- Environment-based overrides

### `/OUTPUTS` - Generated Data
Structured output directory:
- `cached_products/`: Supplier product cache files
- `FBA_ANALYSIS/`: Amazon matching and financial reports
- `CACHE/`: Processing state and resume data

## Architectural Patterns

### Configuration-Driven
All behavior controlled via `config/system_config.json` with no hardcoded values in processing logic.

### State Management
Resumable workflows using file-based state persistence with atomic operations.

### Modular Components
Clear separation between scraping, matching, analysis, and persistence layers.

### Platform Abstraction
Windows and Linux-specific implementations abstracted behind common interfaces.

## File Naming Conventions

- **Scripts**: `snake_case.py`
- **Classes**: `PascalCase`
- **Config files**: `snake_case.json`
- **Output files**: `supplier_timestamp.format`
- **Backup files**: `original.backup_YYYYMMDD_HHMMSS`

## Archive Strategy

- `/archive`: Historical versions and deprecated code
- `/backup`: Timestamped backups before major changes
- Root-level test/validation scripts for development only