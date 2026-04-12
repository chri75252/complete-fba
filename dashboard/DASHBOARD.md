# Dashboard V2 Redesign

**Location:** `dashboard_v2_redesign/`

## Overview

The dashboard provides a real-time view of the FBA agent system's processing metrics, job management, and AI-powered analysis. It's the primary interface for monitoring active runs and querying the system.

---

## Directory Structure

```
dashboard_v2_redesign/
├── api.py                          # Backend API server
├── operator_control_plane.html      # Main operator dashboard
├── precision_dashboard.html       # KPI-focused view
├── ai_assistant.html               # AI analysis interface
├── CLAUDE.md                       # Development instructions
├── templates/                      # HTML templates
│   └── ...
└── static/
    ├── js/
    │   └── app.js                 # Frontend JavaScript
    └── css/
        └── styles.css
```

---

## Components

### 1. Operator Control Plane (`operator_control_plane.html`)

**Purpose:** Main dashboard for monitoring active runs

**Features:**
- Real-time processing metrics
- Product count display
- Phase progress (supplier extraction / Amazon analysis)
- Category completion status
- Error alerts
- Run controls (start/stop/monitor)

**Metrics Displayed:**
- Total products processed
- Products matched to Amazon
- Categories completed
- Current phase
- Session runtime

### 2. Precision Dashboard (`precision_dashboard.html`)

**Purpose:** KPI-focused view for quick health checks

**Metrics:**
- Total products extracted
- Match rate (% matched to Amazon)
- Profitable products count
- Average ROI
- Profit margin distribution

### 3. AI Assistant (`ai_assistant.html`)

**Purpose:** Natural language queries against system data

**Capabilities:**
- Query products by criteria
- Ask about profitability
- Find matching opportunities
- Explain metrics
- Generate reports

**Integration:** Uses `control_plane/chat_orchestrator.py` for AI responses

### 4. Backend API (`api.py`)

**Purpose:** Serves data to dashboard frontend

**Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/metrics` | GET | Current processing metrics |
| `/api/products` | GET | Product list with filters |
| `/api/suppliers` | GET | List of suppliers |
| `/api/state/{supplier}` | GET | Processing state for supplier |
| `/api/financial/{supplier}` | GET | Financial report data |
| `/api/chat` | POST | AI chat query |

---

## API Endpoints

### GET /api/metrics

```json
{
  "total_products": 10828,
  "matched_products": 8500,
  "profitable_products": 2340,
  "avg_roi": 45.2,
  "avg_margin": 22.5,
  "active_runs": ["poundwholesale", "clearance-king"],
  "last_updated": "2026-04-11T10:30:00Z"
}
```

### GET /api/state/{supplier}

```json
{
  "supplier": "poundwholesale.co.uk",
  "phase": "amazon_analysis",
  "category_progress": "1/230",
  "total_products": 10828,
  "successful_products": 8500,
  "last_updated": "2026-04-11T10:30:00Z"
}
```

### GET /api/financial/{supplier}

```json
{
  "supplier": "poundwholesale.co.uk",
  "products": [
    {
      "ean": "5050837373018",
      "asin": "B0FPXFMGVT",
      "supplier_price": 4.00,
      "selling_price": 899.99,
      "net_profit": -28.69,
      "roi": -717.25,
      "profit_margin": -3.19
    }
  ],
  "summary": {
    "total_products": 850,
    "profitable_count": 234,
    "avg_roi": 45.2,
    "avg_margin": 22.5
  }
}
```

### POST /api/chat

**Request:**
```json
{
  "query": "Find products with ROI > 100%",
  "supplier": "poundwholesale.co.uk"
}
```

**Response:**
```json
{
  "answer": "Found 234 products with ROI > 100%...",
  "sources": ["fba_financial_report_...csv"],
  "matches": [
    {"ean": "...", "roi": 150.5},
    {"ean": "...", "roi": 142.3}
  ]
}
```

---

## Running the Dashboard

### Start API Server
```bash
cd dashboard_v2_redesign
python api.py
# Runs on http://localhost:8501
```

### Open Dashboard
```bash
# Option 1: Direct file
open operator_control_plane.html

# Option 2: Via API server
# Navigate to http://localhost:8501/operator_control_plane.html
```

---

## Data Sources

The dashboard reads from:

| Source | Location | Data |
|--------|----------|------|
| Processing States | `OUTPUTS/CACHE/processing_states/` | Run progress, phase |
| Supplier Cache | `OUTPUTS/cached_products/` | Product counts |
| Linking Maps | `OUTPUTS/FBA_ANALYSIS/linking_maps/` | Match statistics |
| Financial Reports | `OUTPUTS/FBA_ANALYSIS/financial_reports/` | Profitability |

---

## Control Plane Integration

The dashboard integrates with `control_plane/` for job management:

### Job Types

| Job | Description |
|-----|-------------|
| `category_run` | Standard category-based extraction |
| `product_list_refresh` | Process specific product URLs |
| `ai_chat` | Natural language queries |

### Worker Architecture

```
Dashboard UI
    │
    ▼
api.py (Flask/Streamlit)
    │
    ├──► control_plane/chat_orchestrator.py (AI chat)
    │
    └──► control_plane/worker.py (Job execution)
             │
             ▼
        Job Queue → Worker Process
```

---

## Frontend JavaScript (`static/js/app.js`)

**Key Functions:**

```javascript
// Fetch and display metrics
async function refreshMetrics() {
  const data = await fetch('/api/metrics');
  updateDisplay(data);
}

// Real-time updates
function startPolling(interval = 5000) {
  setInterval(refreshMetrics, interval);
}

// Financial data table
function renderFinancialTable(data) {
  // Sortable, filterable product table
}

// Chart rendering
function renderCharts(metrics) {
  // ROI distribution
  // Margin trends
  // Category completion
}
```

---

## Styling

**Design Philosophy:**
- No generic "AI slop" aesthetics
- Bold, distinctive design
- Production-grade interfaces

**Typography:**
- Display: Sora, Elms Sans, Vend Sans
- Body: Manrope, Figtree, Source Sans 3

**Reference:** See `CLAUDE.md` for full design guidelines

---

## Legacy Dashboard

**Location:** `dashboard_legacy_streamlit/`

Older Streamlit-based dashboard (still functional but superseded by V2 redesign)

---

## Related Components

| Component | Location | Purpose |
|----------|----------|---------|
| Chat Orchestrator | `control_plane/chat_orchestrator.py` | AI chat logic |
| Worker | `control_plane/worker.py` | Job execution |
| RAG Index | `control_plane/rag_index.py` | Context retrieval |
| Financial Query | `control_plane/financial_query.py` | Financial data queries |

---

## Troubleshooting

### Dashboard Not Loading
1. Check API server running: `python api.py`
2. Check port 8501 available
3. Check browser console for errors

### Metrics Not Updating
1. Verify processing state file exists
2. Check file permissions on OUTPUTS
3. Inspect browser network tab for API errors

### AI Chat Not Responding
1. Check `chat_orchestrator.py` logs
2. Verify LLM provider configured
3. Check API keys in environment

---

*Document Version: 1.0*
*Last Updated: 2026-04-11*
