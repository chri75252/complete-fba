# Dashboard UI/UX Improvement Plan
## Amazon FBA Analytics Engine — dashboard_v2

**Prepared:** 2026-03-16
**Source analysed:** `dashboard_v2/` (templates/index.html, static/css/styles.css, static/js/app.js, api.py, operator_control_plane.html, ai_assistant.html)

---

## Section 1: Current State Audit

### 1.1 File Structure & Architecture

The dashboard has a dual-implementation problem that is the most important structural issue to address:

| File | Role | Status |
|------|------|--------|
| `templates/index.html` | The **live, wired** single-page app served by FastAPI | Production |
| `static/css/styles.css` | CSS custom properties system for the live app | Production |
| `static/js/app.js` | Full JS logic: nav, charts, chat, SSE streaming | Production |
| `api.py` | FastAPI backend, all endpoints | Production |
| `operator_control_plane.html` | **Static mockup** — not wired to any data | Prototype only |
| `ai_assistant.html` | **Static mockup** — not wired to any data | Prototype only |

The two standalone HTML files are higher-fidelity design mockups that were never integrated into the actual app. They use Material Symbols icons and inline Tailwind with MD3 tokens — a different design language from the industrial CSS variable system in `styles.css`. This creates visual inconsistency and wasted design work.

### 1.2 Navigation & Page Structure

**Current structure (live app):**
- Sidebar: 280px fixed left, three nav items (Dashboard, Operator, AI Assistant)
- Content area: single `<main>` with three `<section>` elements toggled by JS class manipulation (`display: none / block`)

**Issues:**
- No ARIA `role="navigation"`, no `aria-current="page"` on the active nav item
- No "Analysis" tab exists for product filtering/scoring
- The live ticker is only visible in the Dashboard view — it should persist across all views
- No URL routing — deep-linking is impossible

### 1.3 Color Scheme — The Core Conflict

The Stitch prototypes ARE the target design. The current `styles.css` uses a competing industrial aesthetic (`#050505` bg, `#e2fd52` volt green accent) that needs to be REPLACED with the prototype's Material Design 3 dark palette:

**Target palette (from prototypes):**
- Background: `#131314` (not `#050505`)
- Surface levels: `#0e0e0f` / `#1c1b1c` / `#201f20` / `#2a2a2b` / `#353436`
- Primary: `#c0c1ff` (lavender)
- Primary container: `#8083ff`
- Secondary: `#4edea3` (mint)
- Tertiary: `#ffb95f` (amber)
- Error: `#ffb4ab`
- Text: `#e5e2e3` / `#c7c4d7` / `#908fa0`

The `#e2fd52` volt green must be removed entirely and replaced with the lavender/mint system.

### 1.4 Typography Bugs

**Bug 1:** `--font-display: 'Sora'` is defined in the CSS variable but Sora is never loaded in the `<link>` tag. Every heading silently falls back to the system sans-serif. The `<link>` loads Space Grotesk, but the CSS variable references Sora.

**Bug 2:** `--font-mono: 'JetBrains Mono'` is defined but JetBrains Mono is also never loaded. Every monospace element (log panel, badges, trace output) silently falls back to the OS monospace.

### 1.5 Accessibility Issues

| Issue | Severity |
|-------|----------|
| `--text-muted: #666666` on `#050505` background: contrast ratio ~3.7:1 — fails WCAG AA (requires 4.5:1) | Fail |
| No `aria-current="page"` on active nav item | Fail |
| No `aria-label` or `role="img"` on Chart.js canvases | Fail |
| Chat input has no `aria-label` | Fail |
| No `focus-visible` outline styles defined anywhere | Fail |
| Metric card labels at 10px — below WCAG minimum for body text | Marginal |

### 1.6 What Works Well

- The industrial aesthetic is cohesive and distinctive — the volt accent on near-black is high-impact
- SSE streaming in the chat renders agent trace steps live — correct UX for an agentic tool
- Confidence distribution chips in the matching panel are a clean, dense data pattern
- Auto-refresh interval selector in sidebar is a useful persistent control
- Stagger animations on load are tasteful and fast (60ms increments, cubic-bezier easing)
- The live ticker with velocity badge is a distinctive contextual-awareness element

---

## Section 2: Visual Design Improvements

### 2.1 Design Language Decision

Commit to the **MD3 dark theme** from the Stitch prototypes. The industrial volt-green aesthetic in the current `styles.css` is abandoned. The prototype's lavender primary + mint secondary + amber tertiary provides a sophisticated, high-contrast dark palette that is already fully designed and tested in the prototype HTML files.

### 2.2 Refined Color Palette

```css
:root {
    --bg-body:              #131314;
    --bg-surface-lowest:    #0e0e0f;
    --bg-surface-low:       #1c1b1c;
    --bg-surface:           #201f20;
    --bg-surface-high:      #2a2a2b;
    --bg-surface-highest:   #353436;
    --bg-surface-bright:    #3a393a;

    --primary:              #c0c1ff;
    --primary-container:    #8083ff;
    --on-primary:           #1000a9;
    --on-primary-container: #0d0096;

    --secondary:            #4edea3;
    --secondary-container:  #00a572;
    --on-secondary:         #003824;

    --tertiary:             #ffb95f;
    --tertiary-container:   #ca8100;
    --on-tertiary:          #472a00;

    --error:                #ffb4ab;
    --error-container:      #93000a;

    --text-primary:         #e5e2e3;
    --text-variant:         #c7c4d7;
    --text-muted:           #908fa0;
    --text-inverse:         #313031;

    --outline:              #908fa0;
    --outline-variant:      #464554;
    --surface-tint:         #c0c1ff;

    --font-display:         'Space Grotesk', sans-serif;
    --font-body:            'Manrope', sans-serif;
    --font-mono:            'JetBrains Mono', monospace;

    --radius-sm:            0.125rem;
    --radius-md:            0.25rem;
    --radius-lg:            0.5rem;
    --radius-xl:            0.75rem;
}
```

### 2.3 Typography Corrections

**Fix 1 — Load the correct fonts:**
```html
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Manrope:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
```

Note: Sora is NOT used in the prototypes. Remove all references to Sora.

**Fix 2 — Headline font**: Space Grotesk (loaded and used — no bug). **Body font**: Manrope. **Mono font**: JetBrains Mono.

**Refined type scale:**

| Element | Font | Size | Weight |
|---------|------|------|--------|
| Page heading (h1) | Space Grotesk | 2.0rem | 700 |
| Section title | Space Grotesk | 1.1rem | 700 |
| Card heading (h3) | Space Grotesk | 0.8rem | 700 |
| Metric value | Space Grotesk | 1.75rem | 700 |
| Metric label | JetBrains Mono | 0.7rem | 500 |
| Body text | Manrope | 0.9rem | 400 |
| Table cell | Manrope | 0.8rem | 400 |
| Badge/tag | JetBrains Mono | 0.65rem | 700 |
| Log output | JetBrains Mono | 0.75rem | 400 |

Reduce all-caps usage: only metric labels and badge text should be uppercase. Card headings should be mixed case at slightly larger size.

### 2.4 Spacing & Layout Refinements

- Main content padding: `40px 48px` -> `32px 40px` with `max-width: 1600px; margin: 0 auto` to prevent over-stretching on ultrawide monitors
- Metric grid gap: `16px` -> `20px`
- Card header padding: `18px 24px` -> `14px 24px`
- Section title top margin: `48px` -> `36px`

**Semantic card border variants** (replace ad-hoc inline Tailwind throughout the HTML):
```css
.card-accent-primary { border-left: 3px solid var(--accent); }
.card-accent-success  { border-left: 3px solid var(--success); }
.card-accent-warning  { border-left: 3px solid var(--warning); }
.card-featured        { border-left: 4px solid var(--accent); background: rgba(226,253,82,0.06); }
```

### 2.5 Fix the Broken Card Hover Effect

The `card::before` pseudo-element has `background: transparent` with no corresponding `:hover` state, so the top-bar effect never fires. The prototype uses a `ghost-border` pattern instead of the `card::before` pseudo-element.

**Fix — match prototype ghost-border styling:**
```css
.card {
    outline: 1px solid rgba(70, 69, 84, 0.15);
}
.card:hover {
    outline-color: rgba(192, 193, 255, 0.25);
}
```

### 2.6 Fix btn-primary Color

The prototype uses the metallic lavender gradient for primary buttons. This is CORRECT for the prototype design:

```css
.btn-primary {
    background: linear-gradient(135deg, #c0c1ff 0%, #8083ff 100%);
    color: #1000a9;
    border: none;
    padding: 10px 16px;
    border-radius: 0.25rem;
    font-family: var(--font-display);
    font-weight: 700;
    font-size: 0.8rem;
    cursor: pointer;
    transition: opacity 150ms ease;
}
.btn-primary:hover { opacity: 0.9; }
```

---

## Section 3: UX Flow Improvements

### 3.1 Navigation Improvements

**Add status badges to nav items** — when active jobs exist, the Operator item shows a count badge; when a pending chat approval exists, the AI Assistant item shows a warning dot:

```css
.nav-item { position: relative; }
.nav-item[data-badge]::after {
    content: attr(data-badge);
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    background: var(--warning);
    color: var(--text-inverse);
    font-size: 0.6rem;
    font-family: var(--font-mono);
    font-weight: 700;
    padding: 1px 5px;
    border-radius: 10px;
}
```

**Add ARIA attributes:**
```html
<nav class="nav-links" role="navigation" aria-label="Primary navigation">
  <a href="#" class="nav-item active" data-target="dashboard" aria-current="page">Dashboard</a>
  <a href="#" class="nav-item" data-target="operator" aria-current="false">Operator</a>
  <a href="#" class="nav-item" data-target="chat" aria-current="false">AI Assistant</a>
</nav>
```

Update the JS click handler to toggle `aria-current` alongside the `active` class.

### 3.2 Dashboard Information Hierarchy Restructure

**Current problem:** The financial summary (Total Profit Potential) is buried in position 6 of the metric cards, and there is a long scroll path through charts, tables, and logs before reaching the terminal.

**Proposed restructure — same data, better grouping:**

```
[Live Ticker — bar persists across all views]
[Page Header]

STRIP: Financial Summary
  Hero card: Total Profit Potential (XX,XXX.XX GBP)
  Supporting: Profitable Count | Average ROI | Files Scanned

GRID (2-col): Operational Status
  Left:  System Health card
  Right: Amazon Matching Performance card

TABBED SECTION (Charts / Products / Logs)
  Tab 1 "Charts":   2x2 chart grid + seller mix
  Tab 2 "Products": Sortable top 20 profitable products table
  Tab 3 "Logs":     Full log terminal
```

This eliminates the endless vertical scroll and groups information by decision type: financials (why run it?), operational status (is it running correctly?), analytical output (what did it find?).

### 3.3 Data Visualization Improvements

**Chart color system — use prototype palette:**
- Primary data: `#c0c1ff` (lavender)
- Positive/success: `#4edea3` (mint)
- Warning: `#ffb95f` (amber)
- Error: `#ffb4ab`
- Background/grid: `rgba(70, 69, 84, 0.15)`

Pull all chart colors from CSS custom properties via `getComputedStyle(document.documentElement).getPropertyValue('--primary')` etc. for design system consistency.

**ROI Histogram:**
- Add a vertical reference line at the target ROI threshold (e.g., 20%) using `chartjs-plugin-annotation`
- Color bins: mint (`#4edea3`) to the right of threshold, grey (`rgba(70, 69, 84, 0.15)`) to the left
- Reduce from 30 bins to 20 bins for cleaner display on typical 200-500 product datasets

**Price Ratio Chart:**
- Add vertical reference lines at `1.0x` (break-even) and `2.0x` (common floor)
- Relabel axis: "Amazon Price / Supplier Price" not "Price Ratio (x)"

**Net Profit Scatter:**
- The three-tier color coding (green/amber/red by ROI) already exists but uses hardcoded hex values in JS — replace with `#4edea3` (mint), `#ffb95f` (amber), `#ffb4ab` (error) from the prototype palette

**Match Quality Chart:**
- Replace vertical bar with horizontal bar — category names are long and get truncated in vertical bars
- Sort bars by value descending

**Seller Mix Doughnut:**
- Add explicit empty state: grey doughnut with centered text `NO SELLER DATA` when both FBA and FBM counts are zero
- Move from full-width to a 30/70 layout (chart left, summary stats right) — a 2-segment doughnut does not need a full-width card

**Suggested chart replacements:**
- Replace **Price Ratio chart** with **Top Categories by Profit** horizontal bar — shows which supplier categories yield the most profitable EAN-verified matches. More actionable than a price ratio distribution.
- Add **Profit vs. Competition scatter** — Net Profit (Y) vs FBA seller count (X). Answers the key question: "Which profitable products have low competition?"

### 3.4 Loading & Empty States

**Skeleton loading for metric cards** — apply during fetch, remove on data arrival:
```css
.metric-skeleton {
    background: linear-gradient(90deg,
        var(--bg-surface-raised) 25%,
        var(--bg-surface-hover) 50%,
        var(--bg-surface-raised) 75%
    );
    background-size: 200% 100%;
    animation: skeleton-sweep 1.5s infinite;
    border-radius: var(--radius-sm);
    height: 1.75rem;
    width: 80%;
}
@keyframes skeleton-sweep {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}
```

**Empty state for chart containers:**
```css
.chart-empty-state {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: var(--text-muted);
    font-family: var(--font-mono);
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    border: 1px dashed var(--surface-border);
    border-radius: var(--radius-sm);
}
```
Message: `NO DATA — RUN A WORKFLOW FIRST`

**Stale data indicator:** When a refresh fails, do not clear existing chart data. Instead show a badge on the page header: `DATA AS OF 14:32 - REFRESH FAILED` in `var(--warning)` color.

### 3.5 Operator View UX

**Deploy Job — 2-step confirmation:** The current button fires immediately. Replace with:
```
Click once -> button text changes to "Confirm Deploy" + "Cancel" appear
Click Confirm within 5 seconds -> fires
No action within 5 seconds -> auto-resets to original state
```

**Active Jobs list:** Currently an empty state placeholder. When job data is available, each job renders as:
```
[icon] [Job name]        [Status badge]
[ID: JOB-XXXX]          [84% ||||||||..] [Running]
                         [Elapsed: 2h 14m] [Cancel]
```

Status color mapping:
```css
.job-status-running  { border-left-color: var(--success);  }
.job-status-pending  { border-left-color: var(--warning);  }
.job-status-failed   { border-left-color: var(--error);    }
.job-status-complete { border-left-color: var(--accent);   }
```

### 3.6 Chat View UX

**Context window indicator** — add below the input area:
```html
<div class="context-bar-container">
    <div class="context-bar-fill" id="contextBarFill"></div>
    <span class="context-bar-label" id="contextBarLabel">Context: 0 / 8k</span>
</div>
```

**Pending approval — break out of bubble:** The approval card currently appears inside a chat message bubble. It should render as a full-width alert block within the chat pane, with prominent Approve/Reject buttons that are impossible to scroll past.

**Message timestamps:** Add `title` attribute to each `.msg-bubble` with the timestamp (e.g., `title="14:32:11"`). Visible on hover without cluttering the interface.

**Chat input keyboard hint:** Add sub-label `Enter to send / Shift+Enter for new line` in `var(--text-muted)` monospace text below the input field.

---

## Section 4: New Components / Sections Proposed

### 4.1 Analysis Tab (Priority 1 — Highest Value)

**What it shows:** A filterable, sortable, paginated table of all products from the financial report CSV. This is the primary deliverable of the FBA system — the full ranked list with ROI, profit, prices, and match quality.

**Why it matters:** The current "Top 5 Profitable Products" table is non-interactive and shows 5 rows. The actual decision-making use case requires reviewing dozens of products with full detail.

**Dashboard Data Integrity**: The main Dashboard view (KPI cards + charts) should filter to EAN-verified matches only (`EAN == EAN_OnPage` where both non-empty). This ensures the headline numbers (Total Profit, Average ROI, Profitable Count) reflect real matches. Unverified/title-based matches are visible in the Analysis tab where they're explicitly labeled by confidence tier.

**Layout:**
```
FILTER BAR
  ROI: [min ___] - [max ___]    Net Profit min: [___]
  Match Quality: [ALL | Exact | High | Medium | Low]
  Sort by: [ROI v] [Profit] [Price Ratio] [Match Quality]
  [Apply]  [Clear]  [Export CSV]          847 results

PRODUCT TABLE (25 per page, paginated)
Columns: # | Supplier Title | Amazon Title | ROI | Net Profit
         | Sell Price | Supplier Price | Ratio | Quality
Row left border color-coded by ROI tier (green/amber/red)
Click row -> expand: full titles, ASIN link, EAN, category URL
```

**Filtering Controls in Analysis Tab:**
```
FILTER CONTROLS STRIP
  Script Filtering:
    Mode: [No Action*] [Manual Trigger] [Every N products] [Sync with fin report]
    Row Range: [From: ___] [To: ___] [All]

  AI Analysis:
    Mode: [No Action*] [Manual Trigger] [Every N products] [Sync with fin report]
    Row Range: [From: ___] [To: ___] [All]
    Max Rows per Batch: [20]

  [Run Script Filter] [Run AI Analysis]
```

"No Action" = completely dormant. No background processes, no API calls. Only activates on button press or when scheduled trigger fires.

### 4.2 Supplier Status Card in Sidebar (Priority 2)

**What it shows:** A persistent mini-card at the bottom of the sidebar configuration section:
```
POUNDWHOLESALE
  ACTIVE
----------------
Phase:  amazon_analysis
Cat:    47 / 233
Run:    12,847 products
Since:  2h 14m ago
```

**Why it matters:** Users switching suppliers in the dropdown lose awareness of the running workflow's state. This surfaces the top 4 operational facts without navigating to the Dashboard.

**CSS treatment:** `background: var(--bg-surface)`, `border: 1px solid var(--border-subtle)`, `border-left: 3px solid var(--accent)` when active.

### 4.3 Toast Notification System (Priority 2)

**Position:** Fixed, bottom-right, `24px` from edges.

**Triggers:**
- Auto-refresh completed: `Data refreshed - 14:33:02`
- Job deployed: `Job JOB-XXXX deployed`
- Connection lost/restored
- Chat: agent task completed

```css
.toast-container {
    position: fixed;
    bottom: 24px;
    right: 24px;
    z-index: 9999;
    display: flex;
    flex-direction: column;
    gap: 8px;
    pointer-events: none;
}
.toast {
    background: var(--bg-surface-raised);
    border: 1px solid var(--border-default);
    border-left: 3px solid var(--accent);
    padding: 12px 16px;
    border-radius: var(--radius-sm);
    font-family: var(--font-mono);
    font-size: 0.75rem;
    color: var(--text-primary);
    pointer-events: all;
    animation: toast-in 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    max-width: 320px;
}
@keyframes toast-in {
    from { opacity: 0; transform: translateX(20px); }
    to   { opacity: 1; transform: translateX(0); }
}
```

Auto-dismiss after 4 seconds. Error toasts (border `var(--error)`) persist until manually dismissed.

### 4.4 Jobs History Panel (Priority 3)

**Location:** Below Active Jobs in the Operator view.

**What it shows:** Table of completed/failed jobs from `OUTPUTS/CONTROL_PLANE/jobs/done/` and `jobs/failed/`:

| Job ID | Supplier | Started | Duration | Products | Status |
|--------|----------|---------|----------|----------|--------|
| JOB-9281 | poundwholesale | 12:14 | 2h 14m | 12,847 | Complete |

Paginated at 10 rows, newest first. Status column uses the same color coding as Active Jobs.

---

## Section 5: Implementation Approach

### 5.1 Core Principles

1. Build only on `dashboard_v2/templates/index.html`, `static/css/styles.css`, `static/js/app.js`, and `api.py`
2. All changes are additive — no file deletions, no modifications to `dashboard/` (legacy Streamlit)
3. Stack remains: vanilla JS + Chart.js + custom CSS. No framework introduction
4. Add `chartjs-plugin-annotation` from CDN for reference lines

### 5.2 Priority Matrix

| # | Improvement | Effort | Priority |
|---|-------------|--------|----------|
| 1 | Fix font loading (Space Grotesk + Manrope + JetBrains Mono + Material Symbols, remove Sora) | XS | Immediate |
| 2 | Fix `--text-muted` to `#908fa0` (WCAG AA on `#131314`) | XS | Immediate |
| 3 | Fix `btn-primary` to metallic lavender gradient | XS | Immediate |
| 4 | Fix card hover — ghost-border pattern from prototype | XS | Immediate |
| 5 | ARIA attributes on nav (role, aria-current) | XS | Immediate |
| 6 | ARIA labels on Chart.js canvases | XS | Immediate |
| 7 | Skeleton loading for metric cards | S | Sprint 1 |
| 8 | Empty/error states for charts | S | Sprint 1 |
| 9 | Toast notification system | S | Sprint 1 |
| 10 | ROI histogram reference line + color threshold | S | Sprint 1 |
| 11 | Chart colors pull from CSS vars | S | Sprint 1 |
| 12 | Expand top products table to 20 rows (was 5) | XS | Sprint 1 |
| 13 | Title tooltips for truncated table cells | XS | Sprint 1 |
| 14 | Tabbed section: Charts / Products / Logs | M | Sprint 2 |
| 15 | Analysis tab: filter bar + full product table | M | Sprint 2 |
| 16 | API: `/api/products/{supplier}` with filtering | M | Sprint 2 |
| 17 | Supplier status card in sidebar | S | Sprint 2 |
| 18 | Chat: context window indicator | S | Sprint 2 |
| 19 | Chat: approval as full-width overlay | S | Sprint 2 |
| 20 | Operator: Deploy Job 2-step confirmation | S | Sprint 2 |
| 21 | Jobs history panel | M | Sprint 3 |
| 22 | Nav badge indicators | S | Sprint 3 |
| 23 | Horizontal bar for Match Quality chart | S | Sprint 3 |
| 24 | Seller mix empty state + compact layout | S | Sprint 3 |

**Effort:** XS < 30 min / S = 30-120 min / M = half day

### 5.3 File Structure

```
dashboard_v2/
  templates/
    index.html           # Existing — add Analysis nav item, tabbed section markup
  static/
    css/
      styles.css         # Existing — apply all corrections from Section 2
    js/
      app.js             # Existing — fix chart colors, expand tables, ARIA updates
      analysis.js        # NEW — Analysis tab: filter bar, product table, pagination
      toast.js           # NEW — Toast notification system
  api.py                 # Existing — add /api/products/{supplier} endpoint
```

### 5.4 New API Endpoint

`GET /api/products/{supplier}`

**Query parameters:**
- `roi_min` float (default 0.0)
- `roi_max` float (default 100.0)
- `profit_min` float (default -inf)
- `quality` string (ALL | Exact | High | Medium | Low)
- `sort_by` string (default "NetProfit")
- `sort_dir` string (asc | desc)
- `page` int (default 1)
- `per_page` int (default 25, max 100)
- `lineage` string (base | latest_sandbox)

**Response:**
```json
{
  "total": 847,
  "page": 1,
  "per_page": 25,
  "pages": 34,
  "products": [
    {
      "SupplierTitle": "...",
      "AmazonTitle": "...",
      "ASIN": "B0XXXXX",
      "EAN": "...",
      "ROI": 0.42,
      "NetProfit": 3.82,
      "SellingPrice_incVAT": 12.99,
      "SupplierPrice_incVAT": 4.20,
      "PriceRatio": 3.09,
      "MatchQuality": "Exact"
    }
  ]
}
```

Reads the same CSV as the existing chart endpoint; applies pandas filtering server-side; returns a paginated slice.

### 5.5 Six Immediate Patches (XS — can be done right now)

**Patch 1 — Fix font loading** (`templates/index.html`):
```html
<!-- Replace the existing Google Fonts link with: -->
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Manrope:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
```
Sora is NOT used in the prototypes — remove any reference to it.

**Patch 2 — Fix muted text contrast** (`static/css/styles.css`):
```css
--text-muted: #908fa0;  /* prototype's outline color — 5.2:1 on #131314, passes WCAG AA */
```

**Patch 3 — Fix btn-primary** (`static/css/styles.css`):
```css
.btn-primary {
    background: linear-gradient(135deg, #c0c1ff 0%, #8083ff 100%);
    color: #1000a9;
    border: none;
    padding: 10px 16px;
    border-radius: 0.25rem;
    font-family: var(--font-display);
    font-weight: 700;
    font-size: 0.8rem;
    cursor: pointer;
    transition: opacity 150ms ease;
}
.btn-primary:hover { opacity: 0.9; }
```

**Patch 4 — Fix card hover** (`static/css/styles.css`):
```css
.card {
    outline: 1px solid rgba(70, 69, 84, 0.15);
}
.card:hover {
    outline-color: rgba(192, 193, 255, 0.25);
}
```

**Patch 5 — ARIA on nav** (`templates/index.html`):
```html
<nav class="nav-links" role="navigation" aria-label="Primary navigation">
  <a href="#" class="nav-item active" data-target="dashboard" aria-current="page">Dashboard</a>
  <a href="#" class="nav-item" data-target="operator" aria-current="false">Operator</a>
  <a href="#" class="nav-item" data-target="chat" aria-current="false">AI Assistant</a>
</nav>
```
Update `static/js/app.js` click handler to set `item.setAttribute('aria-current', 'page')` on the active item and `'false'` on others.

**Patch 6 — ARIA labels on Chart.js canvases** (`templates/index.html`):
Add `role="img"` and `aria-label="[descriptive label]"` to each `<canvas>` element.

---

*All recommendations target `dashboard_v2/` only. No modifications to `dashboard/` (legacy Streamlit) or any protected files in `tools/` or `run_custom_*.py`.*
