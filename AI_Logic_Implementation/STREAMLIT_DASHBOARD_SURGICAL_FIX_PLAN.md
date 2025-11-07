# Streamlit Dashboard Surgical Fix Plan (Combined + Grounded)

Sources used (verified):
- C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\dashboard\app.py
- C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\dashboard\metrics_core.py
- C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\dashboard\streamlit_fba_dashboard.py
- C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\CACHE\processing_states\poundwholesale_co_uk_processing_state.json
- C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\FBA_ANALYSIS\financial_reports\fba_financial_report_*.csv
- C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\FBA_ANALYSIS\linking_maps\poundwholesale.co.uk\linking_map.json

This plan combines your “Master/Complete Streamlit Dashboard Plan” with additional evidence-based analysis and concrete patch guidance to surgically correct the dashboard, without changing upstream code (Phase 1). Upstream matching improvements are listed as Phase 2 for later.


## Executive Summary

- Primary issue is upstream match quality (absurd price mismatches leading to unrealistic ROI), but the dashboard must remain truthful and diagnosable regardless.
- Secondary issues in Streamlit: magic constants (233 categories), brittle path resolution, missing run picker, strict ASIN requirement for KPIs, schema drift handling, and weak diagnostics.
- Phase 1 makes the dashboard correct, transparent, and resilient. Phase 2 (optional) proposes matcher improvements for permanent ROI sanity.


## Current State (Grounded Evidence)

- State file exists with underscores: C:\...\OUTPUTS\CACHE\processing_states\poundwholesale_co_uk_processing_state.json
- Linking map exists under dotted supplier folder: C:\...\OUTPUTS\FBA_ANALYSIS\linking_maps\poundwholesale.co.uk\linking_map.json
- Financial CSVs found under flat directory: C:\...\OUTPUTS\FBA_ANALYSIS\financial_reports\fba_financial_report_*.csv
- ROI extremes confirmed in a recent CSV: ROI > 1000% in 129 / 6137 rows (indicative of mismatches).
- metrics_core.py currently uses a magic “233 categories” check and lacks a run picker.
- streamlit_fba_dashboard.py enforces dropna(['EAN','ASIN']) for KPIs, hiding supplier-only rows that should be counted.


## Phase 1 — Dashboard-Only Surgical Fixes (60–120 minutes)

Goal: Correctness and clarity now, without modifying upstream matching.

### 1) Contract & Path Correctness

- Supplier normalization (authoritative forms):
  - dotted = poundwholesale.co.uk (linking map dir)
  - underscored = poundwholesale_co_uk (processing state filename)
  - hyphenated = poundwholesale-co-uk (preferred subfolder for financial reports; fallback to parent dir)

- Replace magic “233” category logic with observed vs configured counts:
  - observed = len(state.category_performance.keys()) when present (fallback to 0)
  - configured = len(config/poundwholesale_categories.json.category_urls)
  - display tile: “Categories (observed/configured): X / Y” (color-coded, green if close, warn if far apart)

- Prefer supplier subfolder for financial reports if it exists: OUTPUTS\FBA_ANALYSIS\financial_reports\poundwholesale-co-uk\; fallback to parent.

Code patch guidance (metrics_core.py — resolve_paths):
```python
# BEFORE (simplified excerpt)
financial_dir = os.path.join(self.base_dir, "OUTPUTS", "FBA_ANALYSIS", "financial_reports")
return {
    "state_file": state_file,
    "linking_file": linking_file,
    "financial_dir": financial_dir if os.path.exists(financial_dir) else None,
    ...
}

# AFTER
financial_root = os.path.join(self.base_dir, "OUTPUTS", "FBA_ANALYSIS", "financial_reports")
hyphen = supplier_hint.replace('.', '-').lower()
preferred_dir = os.path.join(financial_root, hyphen)
financial_dir = preferred_dir if os.path.exists(preferred_dir) else (
    financial_root if os.path.exists(financial_root) else None
)
return {
    "state_file": state_file,
    "linking_file": linking_file,
    "financial_dir": financial_dir,
    ...
}
```

Code patch guidance (app.py — categories tile):
```python
# BEFORE: relies on is_valid_total_categories_233 + total_categories
is_valid = state_metrics.get("is_valid_total_categories_233")
...
<h4>Total Categories</h4>
<h2>{format_number(total_cats)}</h2>
<p>✅ Valid" if is_valid else f"❌ Invalid (should be 233)

# AFTER: observed/configured tile
obs = state_metrics.get("observed_categories")
cfg = state_metrics.get("configured_categories")
color = "health-ok" if (obs is not None and cfg is not None and abs(obs - cfg) <= max(1, int(0.15*cfg))) else "health-warning"
st.markdown(f"""
<div class="metric-container {color}">
  <h4>Categories (observed/configured)</h4>
  <h2>{format_number(obs)} / {format_number(cfg)}</h2>
  <p>derived from state.category_performance vs config/poundwholesale_categories.json</p>
</div>
""", unsafe_allow_html=True)
```

### 2) Run Picker (per-run control)

- List recent `fba_financial_report_*.csv` in the supplier subfolder; exclude 0-byte and experimental files.
- Verify header includes at least EAN and NetProfit; otherwise mark as invalid.
- Sidebar selectbox to choose one; default newest. Display full path and mtime.

Code patch guidance (app.py or streamlit_fba_dashboard.py — sidebar):
```python
from pathlib import Path
fin_root = Path(paths["financial_dir"]) if paths.get("financial_dir") else None
candidates = []
if fin_root and fin_root.exists():
    for p in sorted(fin_root.glob("fba_financial_report_*.csv"), key=lambda x: x.stat().st_mtime, reverse=True):
        if p.stat().st_size == 0:
            continue
        # header check (cheap)
        try:
            header = p.open("r", encoding="utf-8").readline().strip().split(',')
            if "EAN" in header and ("NetProfit" in header or "ROI" in header):
                candidates.append(p)
        except Exception:
            pass

selected = st.sidebar.selectbox("Select financial report run", candidates, format_func=lambda p: f"{p.name} ({datetime.fromtimestamp(p.stat().st_mtime)})")
st.write("Selected run:", str(selected))
```

### 3) Data-Quality Triage (alert + badges + defaults)

- Red banner if any ROI > 1000% (count and %): “DATA QUALITY ALERT: likely wrong Amazon matches.”
- MatchQuality badges by ROI band:
  - <200% = " Good"
  - 200–1000% = " Review"
  - >1000% = " Suspicious"
- Default filters: ROI slider max=1000; MatchQuality defaults to Good + Review.

Code patch guidance (streamlit_fba_dashboard.py):
```python
def show_data_quality_alert(df):
    if 'ROI' in df.columns:
        suspicious = (pd.to_numeric(df['ROI'], errors='coerce') > 1000).sum()
        total = len(df)
        if suspicious > 0:
            st.error(f"DATA QUALITY ALERT: {suspicious}/{total} ({suspicious/total*100:.1f}%) ROI>1000% — likely wrong Amazon matches.")

df['MatchQuality'] = pd.to_numeric(df['ROI'], errors='coerce').apply(
    lambda r: ' Good' if (pd.notna(r) and r < 200) else (' Review' if (pd.notna(r) and r < 1000) else ' Suspicious')
)
```

### 4) Flexible Schema & Numeric Coercion

- Alias map after read_csv (standardize columns):
  - SupplierPrice_incVAT ← [supplier_price_gbp, price_gbp, supplier_price, cost]
  - SellingPrice_incVAT ← [amazon_price_gbp, amazon_price, selling_price, list_price]
  - NetProfit ← [net_profit, profit, profit_gbp, estimated_profit]
  - ROI ← [roi_pct, roi, return_on_investment, roi_percentage]
  - ProfitMargin ← [profit_margin_pct, profit_margin, margin]
  - EAN, ASIN, SupplierTitle, AmazonTitle
- Coerce numerics with errors='coerce' and report coercion counts.

Code patch guidance:
```python
aliases = {
  'SupplierPrice_incVAT': ['supplier_price_gbp','price_gbp','supplier_price','cost'],
  'SellingPrice_incVAT': ['amazon_price_gbp','amazon_price','selling_price','list_price'],
  'NetProfit': ['net_profit','profit','profit_gbp','estimated_profit'],
  'ROI': ['roi_pct','roi','return_on_investment','roi_percentage'],
  'ProfitMargin': ['profit_margin_pct','profit_margin','margin'],
  'EAN': ['ean','barcode'],
  'ASIN': ['asin','amazon_asin'],
  'SupplierTitle': ['supplier_title','title'],
  'AmazonTitle': ['amazon_title']
}
for std, alts in aliases.items():
    if std not in df.columns:
        for a in alts:
            if a in df.columns:
                df.rename(columns={a: std}, inplace=True)
                break

num_cols = ['SupplierPrice_incVAT','SellingPrice_incVAT','NetProfit','ROI','ProfitMargin']
coerced = {}
for c in num_cols:
    if c in df.columns:
        before = df[c].isna().sum()
        df[c] = pd.to_numeric(df[c], errors='coerce')
        after = df[c].isna().sum()
        coerced[c] = max(0, after - before)

with st.expander("Diagnostics — Schema & Coercion"):
    st.write({ 'coercions': coerced, 'cols': list(df.columns) })
```

### 5) KPI Policy (don’t drop supplier-only rows)

- For KPI tiles: require NetProfit (and price columns) but do NOT require ASIN.
- For Amazon-dependent visuals (e.g., seller_count, ASIN charts): require ASIN.

Code patch guidance (drop policy):
```python
# BEFORE
# df = df.dropna(subset=['EAN','ASIN'])

# AFTER
kpi_df = df.dropna(subset=['NetProfit']) if 'NetProfit' in df.columns else df.copy()
amazon_df = df.dropna(subset=['ASIN']) if 'ASIN' in df.columns else df.iloc[0:0]
```

### 6) Diagnostics & Verification Expanders

- Show resolved supplier variants, chosen paths, selected run + mtime, row counts, alias/coercion report, and drops.
- Provide a “Test Load” button to print head() of selected CSV.

### 7) Performance Safeguard (large CSVs)

- If selected CSV > 50 MB, show a warning and provide “Sample mode”:
  - read CSV in chunks of 10k rows, stop at 100k rows by default (configurable)
  - indicate sampling in the UI


## Phase 2 — Upstream Matching (Optional; 2–4 hours)

- Price sanity rules: reject price_ratio > 100x; for title_search reject > 10x
- Confidence threshold: require >= 0.70
- Title similarity fallback: Jaccard token overlap with brand/pack-size boosts
- EAN-first enforcement with GTIN checks
- Linking map QA metadata: match_method, confidence, price_ratio, sanity_status
- Anomalies logging for future viz

Note: Keep deterministic rules aligned with your system (EAN-first; normalized similarity ≥ 0.85 for title fallback) when you enable these.


## Test & Verification Protocol

- Launch dashboard and pick a recent run:
  - `streamlit run C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\dashboard\app.py`
- Expect:
  - Red alert if ROI>1000% rows exist; default filters exclude Suspicious
  - “Categories (observed/configured)” tile shows sensible X/Y, no magic constants
  - Run picker present; selected run displays absolute path + mtime
  - Diagnostics expanders list supplier variants, paths, alias/coercion counts
  - KPI tiles computed from supplier-valid rows regardless of ASIN


## Diff Checklist (Exact Targets)

- C:\...\dashboard\metrics_core.py
  - Remove: `is_valid_total_categories_233` logic
  - Add: `observed_categories`, `configured_categories`
  - Update: `resolve_paths` to prefer hyphenated supplier dir for financials

- C:\...\dashboard\app.py
  - Replace Total Categories panel with observed/configured tile
  - Add supplier normalization and run picker sidebar
  - Add Diagnostics expanders

- C:\...\dashboard\streamlit_fba_dashboard.py
  - Add alert & MatchQuality badges + default filters
  - Add alias mapping + numeric coercion reporting
  - Relax ASIN requirement for KPI tiles; keep ASIN only for Amazon visuals
  - Add performance sampling for large CSVs (optional)


## Risks & Mitigations

- Schema drift: alias map and diagnostics keep UI resilient; surface missing columns
- Large files: sampling and chunked reads maintain responsiveness
- Upstream anomalies: alert + badges prevent misleading KPIs until upstream is fixed


## Acceptance Criteria (Phase 1)

- No magic constants; categories tile derives from state + config
- Run picker works and shows selected path/mtime
- Alert & badges visible when extreme ROI present; default filters quarantine Suspicious
- KPIs include supplier-only rows; Amazon visuals require ASIN
- Diagnostics expose path resolution, aliasing, coercion, and row drops


---

This plan is intentionally surgical: minimal, high-impact changes that make the dashboard correct and trustworthy now, while preserving the option to harden upstream matching later.

