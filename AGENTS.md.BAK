# AGENTS.md

## ?? AGENT DIRECTIVES - EXECUTE IMMEDIATELY

### **?? Foundational & Project-Specific Standards:**
- ?? **ADHERE_TO_GEMINI_MD**: All actions must comply with the core principles outlined in `GEMINI.md`. This file provides project-specific context that builds upon that foundation.
- ?? **MANDATORY_FIX_TESTING**: Whenever a fix is implemented, you must thoroughly test it to ensure correctness and prevent regressions.
- ?? **NO_CLAIMS_WITHOUT_VERIFICATION**: Tasks cannot be marked complete without actual, verifiable proof of success (e.g., passing tests, verified file outputs).
- ?? **MANDATORY_FILE_VERIFICATION_PROTOCOL**: When referencing files (outputs, scripts, etc.), you MUST follow this protocol:
  1.  ? **VERIFY_ACTUAL_EXISTENCE**: Check if the file/directory actually exists at the specified path using `ls` or `find`.
  2.  ? **CHECK_TIMESTAMP**: Verify the file's creation/modification timestamp to confirm it's recent and relevant to the current task.
  3.  ? **VERIFY_CONTENT**: Read and analyze the actual file content (`cat`, `grep`) before making any claims about what it contains.
  4.  ? **CONFIRM_CORRECT_SUPPLIER**: For this project, ensure files reference the correct supplier (`poundwholesale.co.uk`, NOT `clearance-king.co.uk`).
  5.  ? **PROVIDE_FULL_PATHS**: Always use complete, absolute directory paths in diffs and explanations to avoid ambiguity.
  6.  ? **NO_ASSUMPTIONS**: Never reference files without first reading and verifying their actual content and relevance.

---

## Project Overview

**Complete FBA System** - Amazon FBA automation platform designed for product sourcing, competitive analysis, and financial optimization for UK marketplace operations. The system orchestrates multiple specialized agents to extract supplier data, match Amazon products, and generate comprehensive financial reports.

### Core System Characteristics
- **Configurable Entry Point**: System launched via `run_custom_poundwholesale.py` with all operational toggles, batch sizes, and output directories loaded from `config/system_config.json`
- **No AI Logic**: All AI-driven features (category selection, data extraction, diagnostics) are **disabled** - system uses only deterministic, selector-based scraping and matching
- **Single-Phase Price Scraping**: Workflow scrapes full price range as defined in config (`min_price_gbp` to `max_price_gbp`)
- **Complete Resumable Processing**: Main workflow (`PassiveExtractionWorkflow`) includes supplier scraping, Amazon extraction, financial analysis, and profitability checking with state persistence
- **Robust Output Directory Handling**: All output, cache, and report files written to directories defined by `output_root` in config or default to `OUTPUTS/`

### Agent Ecosystem & Hierarchy
- **Primary Agent**: Claude Code (optimized for this system)
- **Compatible Agents**: Cursor, GitHub Copilot, Gemini CLI, OpenAI Codex [89][90][92][95][97]
- **Multi-Agent Orchestration**: System designed for tech-lead-orchestrator coordination [91][94][96]
- **Agent Limitations**: Browser-dependent operations require Chrome v139+ with remote debugging; network-intensive workflows may timeout in sandboxed environments

### ?? Chrome v139+ Compatibility Notice
**? SYSTEM FULLY COMPATIBLE** - Chrome v139.0.7258.155+ IPv6/IPv4 dual-stack implementation active
- **Chrome CDP Connectivity**: Production validated with automatic IPv6/IPv4 endpoint detection
- **Browser Manager**: Handles Chrome v139+ IPv6-first binding automatically  
- **Legacy Scripts Warning**: 46+ non-workflow scripts contain hardcoded `localhost:9222` - be diligent when updating/generating new Chrome-related scripts to use dynamic endpoint detection

---

## Project Structure & Module Organization

### Complete Workflow Architecture
```
[run_custom_poundwholesale.py] (Entry Point)
     �
     ?
[PassiveExtractionWorkflow::run] (use_predefined_categories=True, ai_client=None)
     �
     +-> 1. Load Predefined Categories from `config/poundwholesale_categories.json`
     �
     +-> 2. [ConfigurableSupplierScraper] -> Scrape Supplier Product Data
     �   +-> Saves to: {output_root}/cached_products/poundwholesale-co-uk_products_cache.json
     �
     +-> 3. [COMPLETE PROCESSING LOOP]
     �   +-> For each supplier product:
     �         +-> a. [AmazonExtractor] -> Search Amazon by EAN (or Title fallback)
     �         �     +-> Saves to: {output_root}/FBA_ANALYSIS/amazon_cache/amazon_{ASIN}_{EAN or title}.json
     �         +-> b. [Linking Map] -> Update EAN-to-ASIN mapping
     �         �     +-> Saves to: {output_root}/FBA_ANALYSIS/linking_maps/poundwholesale-co-uk/linking_map.json
     �         +-> c. [FBA_Financial_calculator] -> Calculate Profitability
     �         �     +-> Saves to: {output_root}/FBA_ANALYSIS/financial_reports/fba_financial_report_{timestamp}.csv
     �         +-> d. [EnhancedStateManager] -> Mark Product as Processed
     �               +-> Saves to: {output_root}/CACHE/processing_states/poundwholesale-co-uk_processing_state.json
```

### Directory Structure
```
+-- tools/                          # Core automation agents (MAIN WORKFLOW)
�   +-- supplier_authentication_service.py    # Session management & login automation
�   +-- configurable_supplier_scraper.py      # Multi-site product extraction
�   +-- amazon_playwright_extractor.py        # Amazon data matching & caching
�   +-- FBA_Financial_calculator.py           # ROI & profitability analysis
�   +-- passive_extraction_workflow_latest.py # Orchestration coordinator (413 KB version)
�   +-- category_completion_tracker.py        # Utility & optimizer
+-- utils/                          # Shared infrastructure & utilities
�   +-- enhanced_state_manager.py             # Persistent state & resumption
�   +-- browser_manager.py                    # Playwright session handling
�   +-- path_manager.py                       # Cross-platform file operations
�   +-- logger.py                             # Centralized logging
�   +-- file_manager.py                       # File operations
�   +-- windows_save_guardian.py              # Utility & optimizer
�   +-- hash_lookup_optimizer.py              # Utility & optimizer
�   +-- sentinel_monitor.py                   # Utility & optimizer
�   +-- url_cache_filter.py                   # Utility & optimizer
�   +-- browser_circuit_breaker.py            # Utility & optimizer
+-- config/                         # System configuration
�   +-- system_config.json                    # Main environment & API settings
�   +-- poundwholesale_categories.json        # Supplier-specific category mappings
�   +-- SystemConfigLoader.py                 # Configuration loader
+-- OUTPUTS/                        # Data persistence & reports
�   +-- cached_products/                      # Supplier product cache
�   +-- FBA_ANALYSIS/                         # Financial reports & analysis
�   �   +-- amazon_cache/                     # Amazon product data cache
�   �   +-- linking_maps/                     # EAN-to-ASIN mappings
�   �   +-- financial_reports/                # CSV outputs & summaries
�   +-- CACHE/                                # Processing states & resumption data
�   +-- logs/                                 # Debug and execution logs
+-- run_custom_poundwholesale.py    # ENTRY POINT
```

---

## Build, Test, and Development Commands

### ?? MANDATORY PROTOCOLS
```bash
# ?? MANDATORY_BACKUP_PROTOCOL: Before testing any script or making major edits:
# 1. Create "backup" folder in same directory if doesn't exist
# 2. Create dated subfolder (e.g., "test_change_20250916") 
# 3. Backup ALL affected files/folders/scripts
# 4. Verify backup created successfully before proceeding
```

### Environment Setup
```bash
# Create isolated environment (REQUIRED)
python -m venv .venv
source .venv/bin/activate  # Linux/WSL
# .venv\Scripts\activate   # Windows

# Install all dependencies
pip install -r requirements.txt

# ?? CRITICAL: Pre-launch Chrome for browser automation (REQUIRED)
google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome_debug &

# Verify Chrome connection (IPv6/IPv4 dual-stack)
curl http://localhost:9222/json/version
netstat -tuln | grep 9222
```

### Core Workflow Execution
```bash
# Main FBA analysis workflow (ENTRY POINT)
python run_custom_poundwholesale.py

# Debug mode with verbose logging
python run_custom_poundwholesale.py --debug --log-level=DEBUG

# Configuration check
python -c "from config.SystemConfigLoader import SystemConfigLoader; print(SystemConfigLoader().load_config())"
```

### Testing & Quality Assurance
```bash
# ?? TASK_SUCCESS_CRITERIA: For task testing to be considered successful:
# 1. ? CORRECT_TIMESTAMP: Every file must have accurate creation/modification timestamp
# 2. ? CORRECT_FILE_PATH: Exact absolute path verified and accessible
# 3. ? CORRECT_SCRIPT_EXECUTION: Check all expected scripts ran in correct order
# 4. ? CONTENT_VERIFICATION: File content analyzed and verified against expectations

# Fast development tests
pytest -q

# Browser-dependent tests (requires active Chrome session)
pytest -m "requires_browser" --chrome-port=9222

# Full workflow validation
python run_custom_poundwholesale.py --test-mode --max-products=5
```

---

## Environment Variables & Runtime Context

### Required Environment Variables
```bash
# Browser Automation
CHROME_REMOTE_PORT=9222                    # Chrome debugging port (IPv6/IPv4 auto-detect)
PLAYWRIGHT_BROWSERS_PATH=/opt/playwright   # Browser installation path

# Output Management (matches config/system_config.json)
OUTPUTS_BASE_PATH=./OUTPUTS                # Data persistence location
output_root=./OUTPUTS                      # Main output directory

# Supplier Configuration
SUPPLIER_SESSION_TIMEOUT=3600              # Session expiry (seconds)
AUTHENTICATION_RETRY_ATTEMPTS=3           # Login retry limit
SESSION_VALIDATION_INTERVAL=300           # Session health check

# Amazon API Configuration  
AMAZON_REQUEST_DELAY_MS=1000               # Rate limiting
AMAZON_CACHE_TTL_HOURS=24                  # Cache validity
EAN_MATCHING_CONFIDENCE_THRESHOLD=0.85     # Product matching accuracy

# Financial Analysis (UK marketplace)
DEFAULT_FBA_FEE_PERCENTAGE=15              # Amazon FBA fee
VAT_RATE_UK=20                             # UK VAT calculation
PROFIT_MARGIN_TARGET=25                    # Target profit margin %

# System Optimization
MAX_CONCURRENT_EXTRACTIONS=3               # Resource limiting
CACHE_RETENTION_DAYS=30                    # Cache cleanup interval
```

### Runtime Context Management
```python
# Access configuration in agents
from config.SystemConfigLoader import SystemConfigLoader
from utils.path_manager import PathManager

config_loader = SystemConfigLoader()
config = config_loader.load_config()
path_manager = PathManager(config.get('output_root', './OUTPUTS'))
```

### Configuration Loading Priority
1. **system_config.json** (primary configuration source)
2. **Environment variables** (override config file values)
3. **Default values** (fallback when neither available)

---

## Advanced Agent Troubleshooting & Self-Help

### ?? Critical Authentication Failures
```bash
# Symptom: "Login failed" or "Session expired" errors
# Solution 1: Reset Chrome session with IPv6/IPv4 detection
pkill -f chrome && sleep 2
python utils/browser_manager.py --health-check --auto-restart

# Solution 2: Clear authentication cache  
rm -rf OUTPUTS/CACHE/auth_sessions/*.json
python tools/supplier_authentication_service.py --reset-auth

# Solution 3: Manual login verification
python tools/standalone_playwright_login.py --verify-only
```

### Browser Connection Issues (Chrome v139+ Compatibility)
```bash
# Check Chrome v139+ IPv6/IPv4 dual-stack connectivity
netstat -tuln | grep 9222
curl -6 http://localhost:9222/json/version  # IPv6
curl -4 http://localhost:9222/json/version  # IPv4

# Auto-recovery with dynamic endpoint detection
python utils/browser_manager.py --health-check --auto-restart --ipv6-first
```

### State Corruption & Recovery
```bash
# ?? FILE-GROUNDED STATE VERIFICATION
# Validate processing state integrity
python utils/enhanced_state_manager.py --validate-state --supplier=poundwholesale-co-uk

# Rebuild state from actual files (not memory)
python utils/enhanced_state_manager.py --rebuild-from-cache --file-grounded

# Reset processing state (nuclear option)
python -c "
from utils.enhanced_state_manager import EnhancedStateManager
from config.SystemConfigLoader import SystemConfigLoader
config = SystemConfigLoader().load_config()
manager = EnhancedStateManager(config)
manager.reset_processing_state('poundwholesale-co-uk')
"
```

### Memory & Performance Issues
```bash
# ?? SMART MEMORY MANAGEMENT SYSTEM
# Monitor resource usage (triggers automatic cleanup at >500 products)
python -m memory_profiler run_custom_poundwholesale.py

# Manual memory optimization
python -c "
from tools.passive_extraction_workflow_latest import PassiveExtractionWorkflow
workflow = PassiveExtractionWorkflow()
workflow.safe_memory_clear_with_file_fallback()
"

# Browser restart system (every 2.5 hours)
python utils/browser_manager.py --restart-schedule --interval=9000
```

### Agent Strategy Guidelines

#### When Agents Should Use Browser vs HTTP [103][104]
- **Browser Required**: Dynamic content, JavaScript rendering, authentication flows, supplier sites
- **HTTP Preferred**: Amazon API endpoints, static data feeds, configuration loading
- **Hybrid Approach**: Auth via browser, data extraction via HTTP where possible (current system design)

#### Agent Escalation Criteria 
```python
# Auto-retry scenarios (agent continues)
- Network timeouts (<30s)
- Chrome connection drops (auto-restart available)
- Rate limiting (429 responses) 
- Partial data extraction (gap processing enabled)

# Human escalation scenarios (agent should stop and alert)
- Structural website changes (CSS selectors broken)
- New CAPTCHA implementations
- Authentication consistently failing (>3 attempts)
- Data quality issues (>20% failure rate across products)
- File system errors (permissions, disk space)
```

#### Multi-Agent Orchestration Protocol [91][94][96]
```bash
# For multi-step or feature development, START with tech-lead-orchestrator
# 1. Invoke tech-lead-orchestrator for routing map
# 2. Wait for structured agent sequence
# 3. Use ONLY listed agents in specified order
# 4. All information handoff managed by main agent
# Never improvise agent selection or skip orchestrator step
```

---

## Testing Guidelines & Advanced Verification

### Testing Architecture & Markers
```python
# Test categories aligned with system architecture
@pytest.mark.unit
def test_price_calculation():
    """Fast, isolated component testing"""

@pytest.mark.integration  
def test_supplier_authentication_flow():
    """Component interaction testing"""

@pytest.mark.requires_browser
def test_amazon_extraction_workflow():
    """Browser-dependent testing (Chrome v139+)"""

@pytest.mark.file_grounded_state
def test_state_persistence_from_files():
    """File-based state verification testing"""

@pytest.mark.workflow_complete
def test_end_to_end_fba_workflow():
    """Complete workflow validation"""
```

### ?? Mandatory Testing Protocols
```bash
# Before any code changes (MANDATORY_BACKUP_PROTOCOL)
# 1. Create backup directory with dated subfolder
mkdir -p backup/pre_test_$(date +%Y%m%d_%H%M%S)
cp -r tools/ utils/ config/ backup/pre_test_$(date +%Y%m%d_%H%M%S)/

# Test execution with verification
pytest -v --tb=long tests/
python run_custom_poundwholesale.py --test-mode --max-products=3 --verify-outputs

# Post-test verification (MANDATORY_FILE_VERIFICATION_PROTOCOL)
# 1. Check file timestamps match test execution
# 2. Verify correct file paths and content
# 3. Confirm supplier references are correct (poundwholesale.co.uk)
ls -la OUTPUTS/FBA_ANALYSIS/financial_reports/ --time-style=full-iso
```

### Snapshot Testing & Output Validation
```bash
# Generate/update snapshots for output consistency
pytest --snapshot-update tests/snapshots/ -v

# Validate workflow output format
python -c "
import json
from pathlib import Path
# Verify linking map schema consistency
linking_map_path = Path('OUTPUTS/FBA_ANALYSIS/linking_maps/poundwholesale-co-uk/linking_map.json')
if linking_map_path.exists():
    with open(linking_map_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(f'Linking map entries: {len(data)}')
        # Check for complete schema coverage (match_method, confidence fields)
        sample = next(iter(data.values())) if data else {}
        print(f'Schema fields: {list(sample.keys())}')
"
```

---

## Data Handling & Performance Optimization

### File-Grounded State Management [Critical Lesson Learned]
```python
# All state calculations based on actual files, not memory variables
def get_current_progress_from_files():
    """Calculate progress from persistent files only"""
    # Method 1: Count processed products from state file
    # Method 2: Count Amazon cache files by timestamp
    # Method 3: Count financial report entries
    # Method 4: Analyze linking map completeness
    # Method 5: Check supplier cache vs processed ratio
    # Method 6: Validate output directory consistency
```

### Smart Memory Management System (Verified Working)
```python
# Sliding window memory management (triggers at >500 products)
def safe_memory_clear_with_file_fallback():
    """
    Smart memory clearing with preservation:
    - Write current state to disk
    - Clear large data structures (keep recent 100 for continuity)
    - Preserve critical counters and progress tracking
    - Maintain authentication sessions
    - Never clear files, only in-memory variables
    """
```

### Performance Monitoring & Optimization
```bash
# Browser restart system (automatic every 2.5 hours)
# - Prevents authentication connection degradation
# - ~2.7 second restart time with immediate recovery
# - Memory-based restart on high Python/Node.js usage
# - Zero downtime with connection recovery

# Resource thresholds (triggers automatic optimization)
PYTHON_MEMORY_LIMIT=3GB        # Triggers garbage collection
NODEJS_MEMORY_LIMIT=2GB        # Triggers browser restart
PRODUCT_ACCUMULATION_LIMIT=500 # Triggers smart memory clear
```

---

## Security & Configuration Management

### ?? CRITICAL API KEY PRESERVATION POLICY
**?? MANDATORY DIRECTIVE: NEVER REMOVE OR MODIFY EXISTING API KEYS**
- ? **PRESERVE ALL EXISTING API KEYS** in scripts and environment files
- ? **ADD KEYS WHEN NEEDED** but never remove working configurations  
- ? **MAINTAIN FUNCTIONALITY** - Keep all working API integrations intact

```bash
# Current Working API Keys (USE WHEN NEEDED/REQUESTED)
OPENAI_API_KEY="sk-ZVcoRkU6brREgixWUDk7lTq_aBNRZwdh_PWwOZuJwKT3BlbkFJvOyKLWAM8OhjyHN0b8e66E1O2G7N2Ew_g3SngsDToA"
GITHUB_TOKEN="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"
```

### Authentication Security & Session Management
```python
# Session isolation and security
- Each supplier uses isolated browser contexts
- Auto-expire sessions after 1 hour inactivity  
- All auth attempts logged to OUTPUTS/logs/auth.log
- Max 3 login attempts per supplier per 15 minutes
- Credentials encrypted using system keyring where possible
```

### Configuration Security
```bash
# Secure file handling (UTF-8 encoding resolution)
# All file operations explicitly specify encoding='utf-8'
# Centralized path management prevents systematic failures
# Configuration loading with validation and fallbacks

# Never commit sensitive files
echo "*.env*" >> .gitignore
echo "config/credentials.json" >> .gitignore  
echo "OUTPUTS/CACHE/auth_sessions/" >> .gitignore
```

---

## Agent-Specific Configuration & Behavior

### Supplier Authentication Agent
```python
# tools/supplier_authentication_service.py
class AuthenticationConfig:
    max_retry_attempts: int = 3
    session_timeout_seconds: int = 3600
    validation_interval_seconds: int = 300
    
    # Chrome v139+ compatibility settings
    ipv6_first: bool = True
    dynamic_endpoint_detection: bool = True
    
    # Agent escalation behavior
    failure_escalation_threshold: int = 5
    human_intervention_triggers: List[str] = [
        "CAPTCHA_UNSOLVABLE",
        "ACCOUNT_LOCKED", 
        "STRUCTURAL_WEBSITE_CHANGES",
        "CHROME_VERSION_INCOMPATIBLE"
    ]
```

### ConfigurableSupplierScraper Agent
```python
# tools/configurable_supplier_scraper.py
class ScrapingConfig:
    # Deterministic scraping (NO AI)
    ai_features_enabled: bool = False
    selector_based_extraction: bool = True
    
    # Performance settings
    concurrent_requests: int = 3
    request_delay_seconds: float = 1.0
    page_load_timeout: int = 30
    
    # Data quality (file-grounded validation)
    min_required_fields: int = 5
    cache_validation_from_files: bool = True
    utf8_encoding_enforced: bool = True
```

### Amazon Extractor Agent  
```python
# tools/amazon_playwright_extractor.py
class AmazonExtractionConfig:
    # Matching strategy (EAN-first, title fallback)
    matching_strategy: str = "ean_first_title_fallback"
    confidence_threshold: float = 0.85
    
    # No AI fallbacks (deterministic only)
    ai_enhanced_matching: bool = False
    
    # Cache management 
    cache_file_grounded: bool = True
    linking_map_schema_complete: bool = True  # Every outcome recorded
```

### Financial Calculator Agent
```python
# tools/FBA_Financial_calculator.py  
class FinancialAnalysisConfig:
    # UK marketplace settings
    default_fba_fee_percentage: float = 15.0
    uk_vat_rate: float = 20.0
    target_profit_margin: float = 25.0
    
    # Output format
    currency: str = "GBP"
    csv_output_utf8: bool = True
    timestamp_in_filename: bool = True
```

---

## Commit & Pull Request Guidelines

### Commit Message Format (Conventional Commits)
```bash
# Aligned with project standards from docs/PULL_REQUEST_CHECKLIST.md
feat(scraper): add gap processing for unprocessed products
fix(auth): resolve Chrome v139+ IPv6 connection issue
docs(agents): update troubleshooting for file-grounded state  
perf(memory): implement smart sliding window cleanup
refactor(state): extract file-based progress calculation
test(workflow): add end-to-end verification protocol
```

### ?? UPDATE PROTOCOL - CRITICAL COMPLIANCE
**?? MANDATORY EXECUTION - Whenever updating ANY file, script, output, or folder:**

1. **?? CASCADING UPDATES** (All complexity levels)
   - ? Check ALL related files that reference the changed item
   - ? Update ALL scripts that use modified paths/functions
   - ? Update ALL documentation mentioning the changed item
   - ? Update path_manager.py if paths changed
   - ? Update system_config.json if configuration affected

2. **?? DOCUMENTATION SYNC** (Medium+ complexity)
   - ? Update docs/README.md with new paths/procedures
   - ? Update config/system-config-toggle-v2.md if applicable
   - ? Update architecture diagrams if workflow affected
   - ? Update troubleshooting guides with new references

---

## Output Tracker & Verification

| Output Type             | File Path (relative to output_root)                                        | Verification Method | Agent Access Pattern |
|-------------------------|-----------------------------------------------------------------------------|--------------------|--------------------|
| **Category Config**     | `config/poundwholesale_categories.json`                                   | ? **Input**       | Read-only by workflow |
| **Supplier Cache**      | `cached_products/poundwholesale-co-uk_products_cache.json`                | ? **UTF-8 Verified** | Generated by scraper |
| **Amazon Data Cache**   | `FBA_ANALYSIS/amazon_cache/amazon_{ASIN}_{EAN or title}.json`             | ? **File-Grounded** | Per-product generation |
| **Linking Map**         | `FBA_ANALYSIS/linking_maps/poundwholesale-co-uk/linking_map.json`         | ? **Schema Complete** | EAN-to-ASIN mapping |
| **Financial Report**    | `FBA_ANALYSIS/financial_reports/fba_financial_report_{timestamp}.csv`     | ? **CSV UTF-8** | Profitable products only |
| **Processing State**    | `CACHE/processing_states/poundwholesale-co-uk_processing_state.json`      | ? **Recovery Ready** | State persistence |
| **Debug Logs**          | `logs/debug/run_custom_poundwholesale_{timestamp}.log`                    | ? **Timestamped** | Full execution trace |

---

## Documentation & Help Resources

### Primary Documentation
- **Complete System Details**: `docs/README.md` [comprehensive technical documentation]
- **Configuration Guide**: `config/system-config-toggle-v2.md` [system settings and toggles] 
- **Pull Request Guidelines**: `docs/PULL_REQUEST_CHECKLIST.md` [development and security standards]
- **Architecture Notes**: This AGENTS.md file (current document)

### Agent-Specific Help
```python
# Built-in help system for agents
def get_context_aware_help(context: str) -> str:
    """Retrieve contextual help based on current operation"""
    help_mapping = {
        'authentication': 'Chrome v139+ compatibility and session management',
        'scraping': 'Deterministic extraction without AI dependencies', 
        'amazon_matching': 'EAN-first matching with file-grounded caching',
        'financial_analysis': 'UK marketplace calculations and CSV output',
        'state_management': 'File-based progress tracking and recovery',
        'memory_optimization': 'Smart sliding window and cleanup strategies'
    }
    return help_mapping.get(context, 'General guidance in docs/README.md')
```

---

## Critical Lessons Learned & Best Practices

### ?? Non-Obvious Technical Discoveries

#### 1. File-Grounded State as Recovery Foundation
- **Discovery**: Memory-based state becomes unreliable in long-running systems
- **Implementation**: Calculate state from persistent files, not variables
- **Agent Benefit**: Reliable recovery and progress tracking across sessions

#### 2. Complete Schema Coverage Principle  
- **Discovery**: Every processing outcome must be explicitly handled
- **Implementation**: Standardized linking map with `match_method: "none"`, `confidence: 0` for no-match cases
- **Agent Benefit**: Predictable data structures and error handling

#### 3. UTF-8 Encoding as First-Class Concern
- **Discovery**: Character encoding issues indicate architectural problems  
- **Implementation**: Explicit `encoding='utf-8'` at every file boundary
- **Agent Benefit**: Cross-platform compatibility and data integrity

#### 4. Smart Memory Management Strategy
- **Discovery**: Large-scale processing requires intelligent resource management
- **Implementation**: Sliding window approach with file-based checkpointing
- **Agent Benefit**: Continuous operation without memory leaks or crashes

---

## Advanced Multi-Agent Orchestration

### Agent Communication Patterns [91][94][96]
```python
# Multi-agent coordination for complex workflows
class AgentOrchestrator:
    def __init__(self):
        self.tech_lead_orchestrator = TechLeadOrchestrator()
        self.agent_registry = {
            'authentication_specialist': SupplierAuthenticationService(),
            'data_extraction_specialist': ConfigurableSupplierScraper(),
            'amazon_matching_specialist': AmazonPlaywrightExtractor(), 
            'financial_analysis_specialist': FBAFinancialCalculator(),
            'state_management_specialist': EnhancedStateManager()
        }
    
    async def execute_coordinated_workflow(self, workflow_request):
        # 1. Get routing map from tech-lead-orchestrator
        routing_map = await self.tech_lead_orchestrator.plan_workflow(workflow_request)
        
        # 2. Execute in specified sequence
        results = []
        for agent_name, task_spec in routing_map.agent_sequence:
            agent = self.agent_registry[agent_name]
            result = await agent.execute_task(task_spec)
            results.append(result)
            
            # 3. Validate progress at each stage
            if not self.validate_stage_completion(result):
                return self.escalate_to_human(agent_name, task_spec, result)
        
        return self.consolidate_results(results)
```

### Sub-Agent Deployment Strategy [97]
```python
# Specialized sub-agents for complex operations
class SpecializedAgents:
    """
    Sub-agent architecture for advanced workflows:
    
    Main Claude (coordinator)
    +-- Authentication Specialist (login/session management)
    +-- Data Quality Reviewer (validation specialist) 
    +-- Performance Monitor (resource optimization)
    +-- Error Recovery Agent (failure handling)
    """
    
    def deploy_sub_agent(self, agent_type: str, context: Dict) -> SubAgent:
        agent_configs = {
            'data_quality_reviewer': {
                'focus': 'UTF-8 validation, schema completeness, file verification',
                'tools': ['read', 'grep', 'diff', 'json_validator'],
                'escalation_threshold': 'data_integrity_violations'
            },
            'performance_monitor': {
                'focus': 'memory usage, file I/O, browser resource monitoring',
                'tools': ['memory_profiler', 'browser_restart', 'cache_optimizer'],
                'escalation_threshold': 'resource_exhaustion'  
            }
        }
        return SubAgent(agent_configs[agent_type], context)
```

---

**Last Updated**: 2025-09-17
**Version**: 4.1 (Aligned with GEMINI.md v1.0)
**Maintained By**: Complete FBA System Team  
**Status**: ACTIVE STANDARD - All agent development must comply

**?? NOTICE**: This file provides project-specific context. It must be used in conjunction with the master directives in `GEMINI.md`. For complete development guidance, reference both this file and `docs/README.md`.