# AI-Enhanced FBA Setup System

Conversational interface for configuring new Amazon FBA suppliers with guided setup.

## Features

- **Natural Language Setup**: Configure suppliers through conversation with Claude Sonnet 3.5
- **Guided CSS Selector Extraction**: Step-by-step instructions for obtaining product selectors
- **Automated Config Generation**: Creates validated JSON configurations
- **Sanity Batch Validation**: Tests configuration with 25 products before full run
- **Non-Destructive Integration**: Zero modifications to existing workflow code
- **Resume Capability**: Interrupt and resume conversations without data loss
- **Cost Transparency**: Clear cost tracking ($0.10-$0.20 per conversation typically)

## Quick Start

### Prerequisites

1. **Python 3.8+**
2. **Anthropic API Key** - Get from [console.anthropic.com](https://console.anthropic.com/)
3. **Existing FBA System** - This integrates with Amazon-FBA-Agent-System-v32

### Installation

```bash
# Install Anthropic SDK
pip install anthropic

# Set API key
export ANTHROPIC_API_KEY='sk-ant-...'

# Run setup
python run_ai_setup.py
```

### Basic Usage

```bash
python run_ai_setup.py
```

Follow the conversational prompts to:
1. Provide supplier domain (e.g., poundwholesale.co.uk)
2. Specify categories to scan
3. Obtain and provide CSS selectors for product data
4. Set price range and target ROI
5. Confirm configuration
6. Run sanity batch (25 products)
7. Optionally run full analysis

## Module Overview

### `ai_enhanced_setup/`

- **conversation_orchestrator.py** - Claude-based conversational interface
- **conversation_state_manager.py** - Session persistence and resume
- **config_generator.py** - JSON configuration generation with validation
- **config_validator.py** - Schema validation against system requirements
- **workflow_executor.py** - Subprocess invocation of existing workflow
- **result_summarizer.py** - File-grounded metrics and reporting
- **dashboard_verifier.py** - Optional dashboard metrics cross-check

### Entry Point

- **run_ai_setup.py** - Main script integrating all components

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Conversational Layer (NEW - ai_enhanced_setup/)       │
│  ┌───────────────────────────────────────────────────┐ │
│  │ conversation_orchestrator.py                      │ │
│  │  • Natural language intent parsing                │ │
│  │  • Slot collection (domain, categories, selectors)│ │
│  │  • State persistence (resume capability)          │ │
│  │  • Cost tracking (display only)                   │ │
│  └───────────────────────────────────────────────────┘ │
│                        ↓                                │
│  ┌───────────────────────────────────────────────────┐ │
│  │ config_generator.py                               │ │
│  │  • Direct Python dict → JSON (no templates)       │ │
│  │  • Schema validation against SystemConfigLoader   │ │
│  │  • Atomic writes (WindowsSaveGuardian pattern)    │ │
│  │  • Additive system_config.json merging            │ │
│  └───────────────────────────────────────────────────┘ │
│                        ↓                                │
│  ┌───────────────────────────────────────────────────┐ │
│  │ workflow_executor.py                              │ │
│  │  • Subprocess invocation of existing runners      │ │
│  │  • Stream stdout/stderr to console                │ │
│  │  • Return code + timestamps                       │ │
│  │  • Sanity batch validation (6 criteria)           │ │
│  └───────────────────────────────────────────────────┘ │
│                        ↓                                │
│  ┌───────────────────────────────────────────────────┐ │
│  │ result_summarizer.py                              │ │
│  │  • Read OUTPUTS artifacts (file-grounded)         │ │
│  │  • Counts, top-N by ROI/margin                    │ │
│  │  • Anomaly detection (missing EANs, low matches)  │ │
│  │  • Generate summary.md + curated.csv              │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                        ↓ subprocess.run()
┌─────────────────────────────────────────────────────────┐
│  Existing System (ZERO MODIFICATIONS)                  │
│  • run_custom_poundwholesale.py                        │
│  • tools/passive_extraction_workflow_latest.py (413KB) │
│  • tools/configurable_supplier_scraper.py              │
│  • tools/amazon_playwright_extractor.py                │
│  • tools/FBA_Financial_calculator.py                   │
└─────────────────────────────────────────────────────────┘
```

## File Structure

```
ai_enhanced_setup/
├── __init__.py
├── README.md
├── conversation_orchestrator.py       # Claude integration
├── conversation_state_manager.py      # State persistence
├── config_generator.py                 # Config generation
├── config_validator.py                 # Validation (in config_generator.py)
├── workflow_executor.py               # Subprocess execution
├── result_summarizer.py               # Metrics & reports
└── dashboard_verifier.py              # Optional verification

run_ai_setup.py                        # Main entry point

OUTPUTS/
├── AI_SETUP_RESULTS/                  # Generated summaries
│   └── {supplier_id}/
│       ├── summary_*.md
│       ├── curated_*.csv
│       └── dashboard_verification_*.json
└── CACHE/
    └── conversation_states/           # Session persistence
        └── session_*_state.json
```

## Cost Information

### Typical Costs

- **Conversation Only**: $0.10-$0.20 per supplier setup
- **With Optional Features**: $2-$4 (selector suggestions, result analysis)

### Cost Control

- Budget limit configurable (default: $0.10 conversation)
- Real-time cost tracking displayed after each exchange
- Graceful degradation on budget exceeded
- Optional hard cap available (set via environment variable)

### Environment Variables

```bash
# Required
export ANTHROPIC_API_KEY="sk-ant-..."

# Optional (defaults shown)
export AI_HARD_CAP_ENABLED="false"           # Set to "true" to enforce hard cap
export AI_HARD_CAP_AMOUNT="4.00"             # Hard cap amount (if enabled)
export AI_CONVERSATION_BUDGET="0.10"          # Conversation guideline
export AI_SETUP_LOG_LEVEL="INFO"             # DEBUG | INFO | WARNING | ERROR
export AI_SETUP_SESSION_TIMEOUT="86400"      # 24 hours
```

## Sanity Batch Validation

Before full run, sanity batch (25 products) validates configuration against 6 criteria:

| Criterion | Pass Threshold | Purpose |
|-----------|----------------|---------|
| Product Scraping | ≥20/25 (80%) | Verify selectors work |
| Amazon Cache | ≥1 file | Verify Amazon connection |
| Linking Map | ≥1 entry | Verify matching logic |
| Financial CSV | ≥1 row | Verify profitability calc |
| Processing State | Updated | Verify state manager |
| Critical Errors | 0 | Verify no crashes |

## Resume Capability

Conversations are automatically saved after each exchange. On restart:

```
📂 Found incomplete session
   Last updated: 2025-01-15 14:30:22
   Cost so far: $0.085

Resume this session? (y/n):
```

Choose 'y' to continue where you left off with all collected data intact.

## Non-Destructive Guarantee

This system makes **ZERO modifications** to existing workflow code:

- ✅ All integration via subprocess invocation
- ✅ Configs written to separate directories
- ✅ Existing `run_custom_poundwholesale.py` unchanged
- ✅ No imports from core workflow modules
- ✅ File-based state management only

## Output Files

### Summary Report (`summary_YYYYMMDD_HHMMSS.md`)

Markdown report with:
- Key metrics (processed, matched, profitable)
- Top 20 opportunities by profit/ROI
- Anomalies detected (missing EANs, price mismatches)

### Curated CSV (`curated_YYYYMMDD_HHMMSS.csv`)

Filtered CSV containing only profitable products (profit ≥ £2, ROI ≥ 30%, margin ≥ 25%), sorted by profit descending.

### Dashboard Verification (Optional)

Cross-checks dashboard metrics against file sources with discrepancy detection.

## Troubleshooting

### "ANTHROPIC_API_KEY not found"

```bash
export ANTHROPIC_API_KEY='sk-ant-...'
```

### "Anthropic library not installed"

```bash
pip install anthropic
```

### Sanity Batch Failures

- **Product scraping < 80%**: Check CSS selectors (right-click → Inspect → Copy selector)
- **Amazon cache empty**: Verify Chrome running with CDP on port 9222
- **Linking map empty**: Ensure products have EAN/barcode data
- **Financial CSV empty**: Check price data quality

### Session Resume Not Working

Check `OUTPUTS/CACHE/conversation_states/` for session files. Sessions expire after 24 hours by default.

## Development

### Testing Individual Modules

```bash
# Config generator
python ai_enhanced_setup/config_generator.py

# Workflow executor
python ai_enhanced_setup/workflow_executor.py

# Result summarizer
python ai_enhanced_setup/result_summarizer.py

# State manager
python ai_enhanced_setup/conversation_state_manager.py
```

### Adding New Suppliers

The system handles any e-commerce supplier. Provide:
1. Domain (e.g., newsupplier.com)
2. Category URLs to scan
3. CSS selectors for: title, price, EAN, product URL, image
4. Price range (min/max in GBP)
5. Target ROI percentage

## Version History

- **v1.0.0** (2025-01-15) - Initial release
  - Full 9-session implementation complete
  - Claude Sonnet 3.5 integration
  - Non-destructive workflow integration
  - State persistence and resume
  - Sanity batch validation
  - Cost tracking and transparency

## License

Part of Amazon FBA Agent System v3.2+

## Support

For issues or questions:
1. Check `OUTPUTS/CACHE/ai_enhanced_setup_logs/` for error context
2. Review conversation state in `OUTPUTS/CACHE/conversation_states/`
3. Verify API key is valid and has credits
4. Check existing workflow is functional independently

---

**Generated by:** AI-Enhanced FBA Setup System  
**Implementation:** Sessions 1-9 Complete  
**Status:** Production Ready
