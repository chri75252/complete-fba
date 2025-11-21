# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 🚨 CRITICAL CLAUDE CODE DIRECTIVES - EXECUTE IMMEDIATELY

### **🚨 MANDATORY TESTING & VERIFICATION STANDARDS**

- **🚨 MANDATORY_FIX_TESTING**: WHENEVER A FIX IS IMPLEMENTED YOU MUST THOROUGHLY TEST YOUR FIXES
- **🚨 NO_CLAIMS_WITHOUT_VERIFICATION**: Tasks cannot be marked complete without actual verification
- **🚨 MANDATORY_FILE_VERIFICATION_PROTOCOL**: For any response referencing files (outputs, scripts, folders, etc.) you MUST:
  1. ✅ **VERIFY_EXISTENCE**: Check file/directory actually exists at specified path
  2. ✅ **CHECK_TIMESTAMP**: Verify file creation/modification timestamp is recent/relevant
  3. ✅ **VERIFY_CONTENT**: Read and analyze actual file content before making claims
  4. ✅ **CONFIRM_SUPPLIER**: Ensure correct supplier reference (poundwholesale.co.uk is default)
  5. ✅ **PROVIDE_FULL_PATHS**: Always use complete absolute directory paths
  6. ✅ **NO_ASSUMPTIONS**: Never reference files without first reading and verifying

### **🚨 MANDATORY BACKUP PROTOCOL**

Before testing any script, parameter, toggle, or making major edits:
  1. ✅ **CREATE_BACKUP_DIRECTORY**: Create "backup" folder if doesn't exist
  2. ✅ **DATED_SUBFOLDER**: Create subfolder with brief reason + date (e.g., "test_change_20251119")
  3. ✅ **BACKUP_ALL_AFFECTED**: Copy ALL files/folders/scripts that might be affected
  4. ✅ **VERIFY_BACKUP**: Confirm backup created successfully before proceeding

### **🚨 TASK SUCCESS CRITERIA**

For any testing task to be considered successfully completed:
  1. ✅ **CORRECT_TIMESTAMP**: Every file must have accurate timestamp matching the test/workflow
  2. ✅ **CORRECT_FILE_PATH**: Exact absolute path verified and accessible
  3. ✅ **CORRECT_SCRIPT_EXECUTION**: All expected scripts ran in correct order
  4. ✅ **CONTENT_VERIFICATION**: File content analyzed and verified against expectations

### **⚠️ UPDATE PROTOCOL - CRITICAL COMPLIANCE**

When updating ANY file, script, output, or folder:
  1. **⚠️ CASCADING UPDATES**: Check ALL related files that reference the changed item
  2. ⚠️ **DOCUMENTATION_SYNC**: Update ALL relevant documentation with new paths/procedures
  3. **⚠️ PATH_CONSISTENCY**: Verify path_manager.py and system_config.json reflect changes
  4. **⚠️ DASHBOARD INTEGRATION**: Update dashboard if workflow/output structure changes

### **🔒 SERENA MCP - READ-ONLY USAGE**

**Purpose**: Discovery & verification only - NEVER write/mutate with Serena
**Order**: Investigate → hypothesize minimal change → use Serena to validate coverage → manual edits
**Proof**: Provide pre-edit match count & file list; post-edit count (expect 0 or documented keeps)
**Ban**: Any Serena or shell command that edits files

### **FORBIDDEN OPERATIONS**

- No command-line in-place editors (`sed -i`, `perl -pi`, `ed`)
- No "auto-fix" Python/Node scripts that reorder or rewrite large file sections
- No mass search-and-replace across repo without Serena manifest + manual snippet patches

---

## 🚨 CRITICAL API KEY PRESERVATION POLICY

**🚨 MANDATORY DIRECTIVE: NEVER REMOVE OR MODIFY EXISTING API KEYS**
- ✅ **PRESERVE ALL EXISTING API KEYS** in scripts and environment files (comment out if needed)
- ✅ **ADD KEYS WHEN NEEDED** but never remove working configurations
- ✅ **MAINTAIN FUNCTIONALITY** - Keep all working API integrations intact

**Current Working API Keys (USE WHEN NEEDED/REQUESTED):**
- OpenAI API Key: `sk-ZVcoRkU6brREgixWUDk7lTq_aBNRZwdh_PWwOZuJwKT3BlbkFJvOyKLWAM8OhjyHN0b8e66E1O2G7N2Ew_g3SngsDToA`
- GitHub Token: `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`

---

## 💼 MULTI-SUPPLIER ARCHITECTURE

### **System is Designed for ANY Wholesale Supplier**

The Amazon FBA Agent System is **supplier-agnostic** and can be configured for any wholesale supplier website through a deterministic onboarding process.

### **Supplier Onboarding via Skill**

**Location**: `.claude/skills/supplier-onboarding/`

**Purpose**: Automated supplier integration using guided workflow
**When to Use**: Adding new wholesale suppliers to the FBA analysis system

**Skill Workflow (7 Steps):**
1. **Data Preprocessing** - LLM manual validation of categories and selectors
2. **Gather Information** - Progressive discovery of supplier details
3. **Prepare Configurations** - Create JSON files for categories and selectors
4. **Invoke Wizard** - Generate runner script and authentication helper
5. **Validate Files** - Comprehensive file and content verification
6. **Report Results** - Detailed success/failure summary
7. **User Decision** - Test run, main run, or fix issues

**Key Features:**
- **Deterministic file generation** with atomic operations
- **Three naming conventions**: dot-form (config files), hyphen-form (scripts), underscore-form (workflow keys)
- **Comprehensive validation** prevents wrong supplier URLs and broken configurations
- **Authentication support** for suppliers requiring login
- **Template-based generation** ensures consistency across suppliers

**Reference Documentation:**
- `.claude/skills/supplier-onboarding/SKILL.md` - Complete onboarding guide
- `.claude/skills/supplier-onboarding/docs/NAMING_CONVENTIONS.md` - Naming standards
- `.claude/skills/supplier-onboarding/docs/FILE_SPECIFICATIONS.md` - File structure requirements
- `.claude/skills/supplier-onboarding/docs/TROUBLESHOOTING.md` - Common issues and fixes

**Example Suppliers Currently Configured:**
- `poundwholesale.co.uk` - With authentication (143-line runner)
- `clearance-king.co.uk` - Without authentication (117-line runner)
- `angelwholesale.co.uk` - With authentication and category processing

**Invoking the Skill:**
```
User: "Onboard new supplier example-wholesale.com with categories from setup/categories.txt"

Claude: Activates supplier-onboarding skill
↓
Step 0: LLM validates categories file and creates JSON configurations
Step 1: Gathers authentication requirements
Step 2: Creates config files in correct locations
Step 3: Invokes wizard to generate runner and auth helper
Step 4: Validates all generated files thoroughly
Step 5: Reports comprehensive results
Step 6: Performs pre-run verification
Step 7: Presents user with test/main run options
```

---

## Project Overview

The Amazon FBA Agent System is a production-ready automation platform for FBA product sourcing from supplier websites to Amazon marketplace. It features file-grounded state management, Chrome v139+ compatibility, Streamlit dashboard monitoring, and resumable processing workflows using Playwright browser automation.

### **🎯 System Characteristics**

- **Configurable Entry Point**: Launched via `run_custom_poundwholesale.py` with settings from `config/system_config.json`
- **No AI Logic**: All AI features **disabled** - uses deterministic, selector-based scraping and matching
- **Single-Phase Price Scraping**: Processes full price range (`min_price_gbp` to `max_price_gbp` from config)
- **Complete Resumable Processing**: Full workflow implementation with state persistence after every operation
- **Chrome v139+ Compatible**: IPv6/IPv4 dual-stack implementation with automatic endpoint detection
- **File-Grounded State**: All state calculations based on actual files, not memory variables
- **Real-Time Monitoring**: Streamlit dashboard for system health, matching performance, and financial analytics
- **Multi-Supplier Support**: Can be configured for any wholesale supplier through guided onboarding skill

---

## Commands

### **🚀 Running the System**

**Main Entry Point:**
```bash
python run_custom_poundwholesale.py
```

**Prerequisites:**
1. **Start Chrome with debug port** (REQUIRED):
   - Windows: `chrome --remote-debugging-port=9222 --user-data-dir=C:\temp\chrome-debug`
   - Linux: `google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug &`
2. **Verify Chrome connection**: `curl http://localhost:9222/json/version`
3. **Install dependencies**: `pip install -r requirements.txt`
4. **Install Playwright browsers**: `playwright install chromium`

**Dashboard Monitoring:**
```bash
# Start the Streamlit dashboard
streamlit run dashboard/app.py

# Or using the launcher script
python dashboard/run_dashboard.py

# Dashboard opens at http://localhost:8501
```

**Alternative Entry Point:**
```bash
python run_complete_fba_system.py
```

### **🧪 Testing**

**Environment Setup:**
```bash
# Create isolated environment (REQUIRED)
python -m venv .venv
.venv\Scripts\activate     # Windows
source .venv/bin/activate  # Linux/Mac

# Install test dependencies
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-mock pytest-cov
```

**Test Execution:**
```bash
# Run all tests
pytest

# Specific test categories
pytest tests/unit/                    # Unit tests only
pytest -m integration                  # Integration tests
pytest -m e2e                         # End-to-end tests
pytest tests/performance/ --benchmark-only  # Performance tests

# Code quality checks
tox -e lint                          # Linting and formatting
tox -e format                        # Auto-format code
tox -e type-check                    # Type checking with mypy
tox -e security                      # Security vulnerability scanning

# Coverage reporting
tox -e coverage-report
```

### **🔧 Development Tools**

**System Diagnostics:**
```bash
# Chrome v139+ compatibility verification
python utils/browser_manager.py --health-check --auto-restart

# Memory management validation
python test_memory_leak_fixes.py

# State file validation
python utils/fixed_enhanced_state_manager.py --validate-state --supplier=poundwholesale-co-uk

# Comprehensive system audit
python run_system_audit.py
```

---

## Architecture

### **🏗️ Complete Workflow Architecture**

The system follows a **Freeze-Mark-Resume** sequence with file-grounded state management:

```
[run_custom_poundwholesale.py] (Entry Point)
     │
     ▼
[PassiveExtractionWorkflow::run] (Core Orchestrator - 413 KB implementation)
     │
     ├─> 1. 🎯 System Initialization
     │    ├─> Chrome CDP connection (IPv6/IPv4 auto-detection)
     │    ├─> Authentication verification
     │    ├─> Configuration loading (system_config.json)
     │    └─> Startup state analysis (file-grounded calculations)
     │
     ├─> 2. 📂 Category Processing Sequence
     │    └─> For each category in config/poundwholesale_categories.json:
     │        ├─> a. URL Discovery & Manifest Generation (BEFORE initialization)
     │        │   ├─> Scrape category page for all product URLs
     │        │   ├─> Save complete URL list atomically to manifest
     │        │   └─> Freeze denominator (write-once, never changes)
     │        ├─> b. Category Initialization (AFTER freezing)
     │        │   ├─> Initialize category processing with frozen denominators
     │        │   ├─> Setup progress tracking with access to frozen totals
     │        │   └─> Handle empty categories (denominator=0, mark complete)
     │        └─> c. Product Processing Loop
     │            ├─> Resume pointer validation using frozen denominators
     │            ├─> Supplier data extraction
     │            ├─> Amazon analysis (EAN-first, title fallback)
     │            ├─> Financial calculations (UK marketplace, 20% VAT)
     │            └─> Atomic state commits
     │
     ├─> 3. 🔄 Interruption & Resume Behavior
     │    ├─> Atomic state persistence using WindowsSaveGuardian
     │    ├─> Resume pointer storage as {phase, cat_idx, prod_idx}
     │    ├─> Phase-aware resumption (supplier or amazon_analysis)
     │    └─> Monotonic validation (pointers only advance, never regress)
     │
     ├─> 4. 📊 Output Generation
     │    ├─> Financial reports (CSV with ROI analysis)
     │    ├─> Linking maps (EAN-to-ASIN mappings)
     │    └─> Amazon cache (individual product data)
     │
     └─> 5. 📺 Real-Time Monitoring
          └─> Streamlit dashboard reads outputs for live metrics
```

### **🔧 Core Components & Dependencies**

**Entry Points:**
- `run_custom_poundwholesale.py` - Primary launcher with authentication and browser setup
- `run_complete_fba_system.py` - Alternative system launcher
- `dashboard/run_dashboard.py` - Streamlit dashboard launcher

**Core Workflow Engine:**
- `tools/passive_extraction_workflow_latest.py` - Main orchestrator (413 KB, PassiveExtractionWorkflow class)

**Direct Dependencies (Core Workflow Tools):**
- `tools/configurable_supplier_scraper.py` - Supplier data extraction with URL filtering
- `tools/amazon_playwright_extractor.py` - Amazon product extraction via Playwright
- `tools/FBA_Financial_calculator.py` - Financial analysis and ROI calculations
- `tools/supplier_authentication_service.py` - Session management and login automation

**Essential Utilities:**
- `utils/fixed_enhanced_state_manager.py` - **CRITICAL**: File-grounded state management with freeze-mark-resume
- `utils/browser_manager.py` - Chrome CDP connection management with IPv6/IPv4 dual-stack
- `utils/windows_save_guardian.py` - Atomic file operations for Windows compatibility
- `utils/path_manager.py` - Cross-platform path management
- `utils/sentinel_monitor.py` - System monitoring and divergence detection

**Configuration System:**
- `config/system_config_loader.py` - System configuration loading
- `config/system_config.json` - Main configuration (processing limits, performance, browser settings)
- `config/poundwholesale_categories.json` - Predefined category URLs
- `config/supplier_configs/` - Supplier-specific configurations

**Dashboard Components:**
- `dashboard/app.py` / `dashboard/app_fixed.py` - Streamlit web interface
- `dashboard/metrics_core.py` / `dashboard/metrics_core_fixed.py` - Data processing engine
- `dashboard/samples/` - Test data files for validation

### **📁 Output Structure**

```
OUTPUTS/
├── cached_products/                              # Supplier product cache
│   └── poundwholesale-co-uk_products_cache.json
├── FBA_ANALYSIS/
│   ├── amazon_cache/                             # Individual Amazon product data
│   │   └── amazon_{ASIN}_{EAN_or_title}.json
│   ├── linking_maps/                             # EAN→ASIN mappings
│   │   └── poundwholesale.co.uk/                 # Dotted folder format
│   │       └── linking_map.json
│   └── financial_reports/                        # Profitability analysis
│       └── fba_financial_report_{timestamp}.csv
├── CACHE/
│   └── processing_states/                        # State management for resumability
│       └── poundwholesale-co-uk_processing_state.json
├── DIAGNOSTICS/                                  # System diagnostics
│   ├── save_telemetry.log
│   ├── sentinels.log
│   └── monitor_trace.log
└── logs/
    ├── debug/                                    # Detailed execution logs
    │   └── run_custom_poundwholesale_{timestamp}.log
    └── health/                                   # System health monitoring
```

---

## Development Notes

### **🪟 Windows Compatibility**

- Full Windows 10/11 support with native memory management
- Atomic file operations to prevent permission issues
- Windows Memory Manager with accurate process monitoring
- PowerShell and Command Prompt compatibility

### **⚡ Performance Optimizations**

- O(1) hash-based duplicate prevention (20-40% improvement)
- Smart memory clearing (99% reduction in operations)
- URL pre-filtering eliminates duplicate processing
- Configurable batch processing for different system capabilities
- Dashboard with chunked data loading for large datasets

### **📊 Monitoring and Debugging**

- Multi-level logging system (debug, health, application logs)
- Real-time performance monitoring via Streamlit dashboard
- Comprehensive error reporting with stack traces
- System diagnostics and validation tools
- Sentinel monitoring for divergence detection
- WindowsSaveGuardian telemetry tracking

---

## Environment Variables

### **Required Variables**

```bash
# Browser Automation
CHROME_REMOTE_PORT=9222
PLAYWRIGHT_BROWSERS_PATH=/opt/playwright

# Output Management
OUTPUTS_BASE_PATH=./OUTPUTS
output_root=./OUTPUTS

# Dashboard Configuration
FBA_BASE_DIR=/path/to/project  # Auto-detected if not set

# Supplier Configuration
SUPPLIER_SESSION_TIMEOUT=3600
AUTHENTICATION_RETRY_ATTEMPTS=3

# Amazon API Configuration
AMAZON_REQUEST_DELAY_MS=1000
AMAZON_CACHE_TTL_HOURS=24

# Financial Analysis (UK Marketplace)
DEFAULT_FBA_FEE_PERCENTAGE=15
VAT_RATE_UK=20
PROFIT_MARGIN_TARGET=25

# System Optimization
MAX_CONCURRENT_EXTRACTIONS=3
CACHE_RETENTION_DAYS=30
```

---

## Troubleshooting

### **🔧 Common Issues**

**Chrome Connection Issues:**
```bash
# Check Chrome v139+ IPv6/IPv4 connectivity
netstat -tuln | grep 9222
curl -6 http://localhost:9222/json/version  # IPv6
curl -4 http://localhost:9222/json/version  # IPv4

# Auto-recovery with dynamic endpoint detection
python utils/browser_manager.py --health-check --auto-restart --ipv6-first
```

**Authentication Failures:**
```bash
# Reset Chrome session and restart browser
pkill -f chrome && sleep 2
python utils/browser_manager.py --health-check --auto-restart

# Clear authentication cache
rm -rf OUTPUTS/CACHE/auth_sessions/*.json
python tools/supplier_authentication_service.py --reset-auth
```

**State Corruption Recovery:**
```bash
# Validate and rebuild state from files
python utils/fixed_enhanced_state_manager.py --validate-state --supplier=poundwholesale-co-uk
python utils/fixed_enhanced_state_manager.py --rebuild-from-cache --file-grounded
```

**Dashboard Issues:**
```bash
# Dashboard shows "—" for missing data
# 1. Verify FBA_BASE_DIR environment variable
echo $FBA_BASE_DIR  # Linux/Mac
echo %FBA_BASE_DIR%  # Windows

# 2. Check file structure
ls -la OUTPUTS/CACHE/processing_states/
ls -la OUTPUTS/FBA_ANALYSIS/linking_maps/

# 3. Verify files exist with correct supplier naming
# Supports both: poundwholesale.co.uk and poundwholesale_co_uk
```

---

## Documentation References

**Complete Technical Documentation:**
- `docs/README.md` - Comprehensive technical documentation
- `config/system-config-toggle-v2.md` - System settings and toggles
- `docs/PULL_REQUEST_CHECKLIST.md` - Development and security standards
- `latest_workflow.md` - Detailed workflow behavior and sequence
- `AGENTS.md` - Multi-agent orchestration and deployment guide
- `dashboard/README.md` - Dashboard setup and usage guide
- `dashboard/README_DASHBOARD_TROUBLESHOOTING.md` - Dashboard troubleshooting
- `.claude/skills/supplier-onboarding/` - Complete supplier onboarding documentation

**System Status**: ✅ Production Ready
**Chrome Compatibility**: ✅ v139+ with IPv6/IPv4 dual-stack
**Dashboard**: ✅ Real-time monitoring with Streamlit
**Multi-Supplier**: ✅ Configurable for any wholesale supplier
**Last Updated**: November 19, 2025
**Platform Support**: Windows 10/11, Linux, WSL2
**Python Compatibility**: 3.8+

---

## Critical Behavioral Rules

### **🚨 DUAL TRACKING STATE ARCHITECTURE**

- `system_progression` section = CANONICAL source for resumption logic
- `supplier_extraction_progress` section = legacy compatibility only
- **ONLY CORRECT METHOD**: `update_progression_unified()` for atomic updates to both sections
- **ARCHITECTURAL VIOLATION**: Direct calls to `update_supplier_extraction_progress()`

### **🚨 STATE CORRUPTION INDICATORS**

- `total_categories` MUST equal 233 (from poundwholesale_categories.json)
- If `total_categories` ≠ 233, state corruption has occurred
- Dashboard Health Panel validates this automatically

### **🚨 NEVER DELETE CACHE FILES**

- System uses "reverse gap processing" - acts as if cache clear, starts from first URL, uses cache for skip logic
- Cache files are ESSENTIAL for gap processing and resume functionality
- Deleting cache breaks the entire system architecture

### **🚨 FILE-GROUNDED OPERATIONS**

- All state calculations based on actual files (linking_map.json, processing_state.json, cache files)
- Never rely on in-memory variables for progress tracking
- Dashboard reads directly from output files without database
- Resume data reconstructed from linking_map.json on startup

---

## Dashboard-Specific Instructions

### **Launch Dashboard**

```bash
# Method 1: Using launcher script
python dashboard/run_dashboard.py

# Method 2: Direct Streamlit invocation
streamlit run dashboard/app.py --server.port 8501

# Method 3: With explicit base directory
FBA_BASE_DIR=/path/to/project streamlit run dashboard/app.py
```



## 🧩 MCP SERVER INTEGRATIONS - AVAILABLE TOOLS

### **Zen MCP - Multi-Model Reasoning & Analysis**

When user explicitly requests ZEN MCP tools or when complex reasoning is needed:

**Available Tools:**
- **chat**: General collaborative thinking and brainstorming (models: gpt-5, gemini-2.5-flash)
- **thinkdeep**: Multi-stage comprehensive investigation and reasoning
- **planner**: Interactive sequential planning with step-by-step breakdown
- **consensus**: Multi-model consensus workflow for decision making
- **codereview**: Step-by-step code review with expert analysis
- **debug**: Root cause analysis and systematic debugging
- **analyze**: Comprehensive code analysis and architectural assessment
- **refactor**: Refactoring analysis with code smell detection
- **tracer**: Code tracing workflow for execution flow analysis
- **docgen**: Documentation generation with complexity analysis

**Usage Pattern:**
```
Complex debugging → Use zen::debug for systematic root cause analysis
Architecture decisions → Use zen::consensus for multi-model decision making
Code quality → Use zen::codereview for expert analysis
Planning → Use zen::planner for structured breakdown
```

### **Serena MCP - Semantic Code Operations (READ-ONLY)**

**Purpose**: Symbol-based code navigation and discovery
**Capabilities**:
- `find_symbol` - Locate classes, methods, functions by name
- `find_referencing_symbols` - Discover where code is used
- `search_for_pattern` - Flexible pattern matching
- `get_symbols_overview` - File structure understanding

**CRITICAL**: Serena is READ-ONLY. Never use for mutations. Only for discovery and verification.

### **Context7 MCP - Library Documentation**

**Purpose**: Up-to-date documentation for libraries and frameworks
**Usage**:
1. `resolve-library-id` - Find Context7 library ID
2. `get-library-docs` - Retrieve focused documentation

**Example Libraries Available:**
- `/anthropics/courses` - Anthropic Claude SDK and prompt engineering
- `/anthropics/anthropic-cookbook` - Code snippets for Claude integrations
- `/websites/docs_anthropic_com-en-home` - Official Anthropic API docs

### **Chrome DevTools (CDP) MCP - Browser Automation**

**Purpose**: Browser interaction and testing
**Key Tools**:
- `navigate_page` - Navigate to URLs
- `click` - Interact with elements
- `fill` - Fill form fields
- `take_screenshot` - Visual validation
- `evaluate_script` - Execute JavaScript

**Use Case**: Browser testing, E2E validation, visual regression testing

### **Sequential Thinking MCP - Structured Reasoning**

**Purpose**: Multi-step problem solving with thought chains
**Use When**:
- Breaking down complex problems
- Planning with room for revision
- Analysis needing course correction
- Hypothesis generation and verification

---


## 🤖 SUB-AGENT ORCHESTRATION - MANDATORY PROTOCOL

### **CRITICAL ORCHESTRATION RULES**

**FOR ALL MULTI-STEP OR FEATURE DEVELOPMENT TASKS:**
1. **ALWAYS START** by invoking the `tech-lead-orchestrator` agent
2. **WAIT** for its structured routing map (named agents, specified order)
3. **USE ONLY** the agents listed in the routing map, in the sequence provided
4. **NEVER** improvise agent selection or skip the orchestrator step
5. **ALL HANDOFFS** managed by main agent, not sub-agent-to-sub-agent calls

### **When to Use Tech Lead Orchestrator**

- Multi-step development tasks (>3 steps)
- Feature implementations requiring multiple agents
- Architectural decisions needing strategic planning
- Complex debugging requiring systematic approach
- Any task where optimal agent coordination matters

### **Available Specialized Agents**

**Orchestrators & Planning:**
- `tech-lead-orchestrator` - Strategic planning and agent coordination (REQUIRED for multi-step tasks)
- `project-analyst` - Deep project understanding and stack detection
- `team-configurator` - AI team configuration based on tech stack

**Core Development:**
- `code-archaeologist` - Codebase exploration and discovery
- `code-reviewer` - Quality assurance and code review
- `performance-optimizer` - Speed and efficiency improvements
- `documentation-specialist` - Technical documentation creation

**Framework Specialists:**
- `django-backend-expert` - Django models, views, services
- `django-api-developer` - Django REST Framework, GraphQL
- `django-orm-expert` - ActiveRecord optimization, queries
- `rails-backend-expert` - Rails complete backend development
- `rails-api-developer` - Rails API design and implementation
- `react-component-architect` - React components and patterns
- `react-state-manager` - Redux, Zustand, Context API
- `vue-component-architect` - Vue 3 Composition API
- `nextjs-pro` - Next.js SSR, SSG, ISR

**Universal Agents (Use when no specialist available):**
- `backend-developer` - Generic backend implementation
- `frontend-developer` - Generic frontend implementation
- `api-architect` - Framework-agnostic API design
- `full-stack-developer` - End-to-end development

**Quality & Testing:**
- `test-automator` - Automated testing strategies
- `qa-expert` - Comprehensive quality assurance
- `debugger` - Error diagnosis and resolution
- `security-auditor` - Security vulnerability analysis

**Infrastructure & DevOps:**
- `cloud-architect` - AWS, Azure, GCP infrastructure
- `deployment-engineer` - CI/CD pipelines and deployment
- `devops-incident-responder` - Production incident response

**Data & AI:**
- `database-optimizer` - Query optimization and schema design
- `ai-engineer` - LLM-powered applications and RAG systems
- `ml-engineer` - Machine learning model lifecycle

### **Orchestration Example**

```
User Request: "Build a product API with authentication"

Step 1: Invoke tech-lead-orchestrator
↓
Tech Lead Returns:
- Task 1: Analyze codebase → AGENT: code-archaeologist
- Task 2: Design data models → AGENT: django-backend-expert
- Task 3: Implement auth → AGENT: backend-developer
- Task 4: Create API endpoints → AGENT: django-api-developer
- Task 5: Write tests → AGENT: test-automator
- Task 6: Review code → AGENT: code-reviewer

Step 2: Main Agent Delegates
- Execute Task 1 with code-archaeologist
- After Task 1 completes, execute Task 2 with django-backend-expert
- Continue sequentially through all tasks
```

---

This comprehensive guide enables effective development, debugging, and monitoring of the Amazon FBA Agent System. All major components, workflows, multi-supplier support, agent orchestration, MCP integrations, and the Streamlit dashboard are documented for future reference.
