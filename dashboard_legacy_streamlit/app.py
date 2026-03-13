"""
FBA Analytics Dashboard
Streamlit dashboard for monitoring Amazon FBA Agent System performance
"""

import streamlit as st
import os
import time
from datetime import datetime
from metrics_core import MetricsLoader, load_metrics
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="FBA Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.metric-container {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #1f77b4;
}
.health-ok { border-left-color: #2ecc71; }
.health-warning { border-left-color: #f39c12; }
.health-error { border-left-color: #e74c3c; }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=10)
def get_cached_metrics(base_dir: str, supplier: str, paths_hash: str):
    """Cached metrics loader - only reloads when files change"""
    try:
        return load_metrics(base_dir, supplier)
    except Exception as e:
        st.error(f"Error loading metrics: {str(e)}")
        return None


def get_paths_hash(paths):
    """Create hash from file modification times for cache invalidation"""
    try:
        mt = []
        sf = paths.get('state_file')
        lf = paths.get('linking_file')
        fin = paths.get('financial_dir')
        ac = paths.get('amazon_cache_dir')
        
        # State and linking file mtimes
        for p in [sf, lf]:
            if p and os.path.exists(p):
                mt.append(os.path.getmtime(p))
        
        # Financial dir: latest CSV mtime and count
        if fin and os.path.exists(fin):
            csvs = [os.path.join(fin, f) for f in os.listdir(fin) 
                   if f.startswith('fba_financial_report_') and f.endswith('.csv')]
            if csvs:
                latest = max(csvs, key=os.path.getmtime)
                mt.append(os.path.getmtime(latest))
                mt.append(len(csvs))
        
        # Amazon cache dir: latest amazon_*.json mtime and count
        if ac and os.path.exists(ac):
            caches = [os.path.join(ac, f) for f in os.listdir(ac) 
                     if f.startswith('amazon_') and f.endswith('.json')]
            if caches:
                latest = max(caches, key=os.path.getmtime)
                mt.append(os.path.getmtime(latest))
                mt.append(len(caches))
        
        return hash(tuple(mt))
    except:
        return 0


def format_number(num):
    """Format numbers with comma separators"""
    if num is None:
        return "—"
    try:
        return f"{num:,}"
    except (ValueError, TypeError):
        return str(num)


def format_percentage(num):
    """Format percentages"""
    if num is None:
        return "—"
    try:
        return f"{num:.1f}%"
    except (ValueError, TypeError):
        return str(num)


def format_currency(amount):
    """Format currency values"""
    if amount is None:
        return "—"
    try:
        return f"£{amount:,.2f}"
    except (ValueError, TypeError):
        return str(amount)


def render_health_panel(state_metrics, linking_metrics=None, supplier_cache_metrics=None):
    """Render the health status panel"""
    st.subheader("🏥 System Health")

    if not state_metrics or not state_metrics.get("state_file_found", False):
        st.warning("⚠️ State file not found")
        return

    cols = st.columns(3)

    with cols[0]:
        obs = state_metrics.get("observed_categories")
        cfg = state_metrics.get("configured_categories")
        
        # Determine health color based on observed vs configured
        if obs is not None and cfg is not None:
            diff_threshold = max(1, int(0.15 * cfg))  # 15% tolerance
            if abs(obs - cfg) <= diff_threshold:
                color = "health-ok"
                status_text = "✅ Categories match configuration"
            else:
                color = "health-warning"
                status_text = f"⚠️ Observed differs from configured"
        else:
            color = "health-warning"
            status_text = "⚠️ Unable to determine category counts"

        st.markdown(f"""
        <div class="metric-container {color}">
            <h4>Categories (observed/configured)</h4>
            <h2>{format_number(obs)} / {format_number(cfg)}</h2>
            <p>{status_text}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Current category and per-category progress (separate tile)
        cc = state_metrics.get("current_category_url")
        short = "—"
        if cc:
            parts = cc.split("://", 1)[-1]
            short = parts.split("/", 1)[-1] if "/" in parts else parts
        
        cp = state_metrics.get("category_progress") or {}
        sup_done = cp.get("supplier_products_completed")
        sup_need = cp.get("supplier_products_needing_extraction")
        amz_done = cp.get("amazon_products_completed")
        amz_need = cp.get("amazon_products_needing_analysis")
        
        st.markdown(f"""
        <div class="metric-container">
            <h4>Current Category</h4>
            <p>{short}</p>
            <p>Supplier: <strong>{sup_done if sup_done is not None else '—'}</strong>/<strong>{sup_need if sup_need is not None else '—'}</strong> •
               Amazon: <strong>{amz_done if amz_done is not None else '—'}</strong>/<strong>{amz_need if amz_need is not None else '—'}</strong></p>
        </div>
        """, unsafe_allow_html=True)

    with cols[1]:
        status = state_metrics.get("processing_status", "Unknown")
        last_updated = state_metrics.get("last_updated")

        st.markdown(f"""
        <div class="metric-container">
            <h4>Processing Status</h4>
            <h2>{status}</h2>
            <p>Updated: {last_updated.strftime('%Y-%m-%d %H:%M') if last_updated else 'Never'}</p>
        </div>
        """, unsafe_allow_html=True)

    with cols[2]:
        # Total Extracted and Total Processed
        linking_total = linking_metrics.get("total_matches", 0) if linking_metrics else 0
        supplier_total = supplier_cache_metrics.get("product_count", 0) if supplier_cache_metrics else 0
        fresh_starts = state_metrics.get("fresh_starts", 0)

        st.markdown(f"""
        <div class="metric-container">
            <h4>Processing Stats</h4>
            <p>Total Extracted (supplier cache): <strong>{format_number(supplier_total)}</strong></p>
            <p>Total Processed (linking map): <strong>{format_number(linking_total)}</strong></p>
            <p>Fresh Starts: <strong>{format_number(fresh_starts)}</strong></p>
        </div>
        """, unsafe_allow_html=True)


def render_matching_panel(linking_metrics):
    """Render the matching statistics panel"""
    st.subheader("🔗 Amazon Matching Performance")

    if not linking_metrics or linking_metrics.get("total_matches", 0) == 0:
        st.warning("⚠️ No matching data available")
        return

    cols = st.columns(4)

    with cols[0]:
        st.metric("Total Matches", format_number(linking_metrics.get("total_matches", 0)))

    with cols[1]:
        st.metric("High Confidence Rate", format_percentage(linking_metrics.get("high_confidence_rate", 0)))

    with cols[2]:
        st.metric("No EAN Count", format_number(linking_metrics.get("no_ean_count", 0)))

    with cols[3]:
        match_methods = linking_metrics.get("match_method_counts", {})
        primary_method = max(match_methods.items(), key=lambda x: x[1])[0] if match_methods else "None"
        st.metric("Primary Method", primary_method.capitalize())

    # Confidence distribution
    if "error" not in linking_metrics:
        st.write("**Confidence Distribution**")
        confidence_counts = linking_metrics.get("confidence_counts", {})
        if confidence_counts:
            conf_cols = st.columns(len(confidence_counts))
            for i, (conf_type, count) in enumerate(confidence_counts.items()):
                with conf_cols[i]:
                    st.write(f"**{conf_type.title()}**: {format_number(count)}")

        # Match method distribution
        st.write("**Match Method Distribution**")
        method_counts = linking_metrics.get("match_method_counts", {})
        if method_counts:
            method_cols = st.columns(len(method_counts))
            for i, (method, count) in enumerate(method_counts.items()):
                with method_cols[i]:
                    st.write(f"**{method.replace('_', ' ').title()}**: {format_number(count)}")


def render_financial_panel(financial_metrics):
    """Render the financial performance panel"""
    st.subheader("💰 Financial Performance")

    if not financial_metrics or financial_metrics.get("files_scanned", 0) == 0:
        st.warning("⚠️ No financial data available")
        if financial_metrics and financial_metrics.get("notes"):
            st.write("**Notes**:")
            for note in financial_metrics["notes"]:
                st.write(f"• {note}")
        return

    cols = st.columns(4)

    with cols[0]:
        st.metric("Files Scanned", format_number(financial_metrics.get("files_scanned", 0)))

    with cols[1]:
        st.metric("Total Rows", format_number(financial_metrics.get("rows_total", 0)))

    with cols[2]:
        st.metric("Profitable Products", format_number(financial_metrics.get("count_profitable", 0)))

    with cols[3]:
        st.metric("Average ROI", format_percentage(financial_metrics.get("avg_roi", 0)))

    # Total profit with emphasis
    total_profit = financial_metrics.get("total_profit", 0)
    if total_profit > 0:
        st.markdown(f"""
        <div class="metric-container health-ok">
            <h3>Total Profit Potential</h3>
            <h1 style="color: #27ae60; font-size: 2.5rem;">{format_currency(total_profit)}</h1>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="metric-container">
            <h3>Total Profit Potential</h3>
            <h1>{format_currency(total_profit)}</h1>
        </div>
        """, unsafe_allow_html=True)

    # Show notes if any
    if financial_metrics.get("notes"):
        st.write("**Processing Notes**:")
        for note in financial_metrics["notes"]:
            st.write(f"• {note}")


def render_logs_panel(log_data):
    """Render the logs panel"""
    st.subheader("📋 Latest Logs")

    if not log_data or not log_data[0]:
        st.warning("⚠️ No log data available")
        return

    lines, filename = log_data

    st.write(f"**Showing last {len(lines)} lines from:** `{filename}`")

    # Display logs with syntax highlighting
    log_text = "\n".join(lines)
    st.code(log_text, language="text")


def create_roi_histogram(df):
    """Histogram of ROI values with sensible bins."""
    try:
        tmp = df.copy()
        tmp['ROI'] = pd.to_numeric(tmp.get('ROI'), errors='coerce')
        tmp = tmp[tmp['ROI'].notna()]
        if tmp.empty:
            return None
        fig = px.histogram(tmp, x='ROI', nbins=50, title="ROI Histogram (All Products)")
        fig.update_layout(xaxis_title="ROI (%)", yaxis_title="Count")
        return fig
    except Exception as e:
        st.error(f"Error creating ROI histogram: {str(e)}")
        return None

def create_profit_vs_price_chart(df):
    """Scatter: NetProfit vs SellingPrice, sized by offer count if available."""
    try:
        tmp = df.copy()
        tmp['SellingPrice_incVAT'] = pd.to_numeric(tmp.get('SellingPrice_incVAT'), errors='coerce')
        tmp['NetProfit'] = pd.to_numeric(tmp.get('NetProfit'), errors='coerce')
        size_col = None
        for c in ['total_offer_count', 'fba_seller_count', 'fbm_seller_count']:
            if c in tmp.columns:
                tmp[c] = pd.to_numeric(tmp[c], errors='coerce')
                size_col = c
                break
        tmp = tmp[tmp['SellingPrice_incVAT'].notna() & tmp['NetProfit'].notna()]
        if tmp.empty:
            return None
        color_col = 'MatchQuality' if 'MatchQuality' in tmp.columns else None
        fig = px.scatter(tmp, x='SellingPrice_incVAT', y='NetProfit',
                         color=color_col, size=size_col,
                         title="Net Profit vs Selling Price",
                         labels={'SellingPrice_incVAT': "Selling Price", 'NetProfit': "Net Profit"} )
        return fig
    except Exception as e:
        st.error(f"Error creating Profit vs Price chart: {str(e)}")
        return None

def create_price_ratio_histogram(df):
    """Histogram of price ratio (Amazon/Supplier)."""
    try:
        tmp = df.copy()
        sp = pd.to_numeric(tmp.get('SupplierPrice_incVAT'), errors='coerce')
        ap = pd.to_numeric(tmp.get('SellingPrice_incVAT'), errors='coerce')
        ratio = ap / sp
        tmp = tmp[ratio.notna() & (sp > 0)]
        if tmp.empty:
            return None
        tmp = tmp.assign(Price_Ratio=ratio[ratio.notna() & (sp > 0)])
        fig = px.histogram(tmp, x='Price_Ratio', nbins=50, title="Price Ratio (Amazon/Supplier)")
        fig.update_layout(xaxis_title="Price Ratio (x)", yaxis_title="Count")
        return fig
    except Exception as e:
        st.error(f"Error creating price ratio histogram: {str(e)}")
        return None

def create_match_quality_bar(df):
    """Bar chart of MatchQuality distribution if available."""
    try:
        if 'MatchQuality' not in df.columns:
            return None
        vc = df['MatchQuality'].value_counts().reset_index()
        vc.columns = ['MatchQuality', 'Count']
        fig = px.bar(vc, x='MatchQuality', y='Count', title="Match Quality Distribution")
        return fig
    except Exception as e:
        st.error(f"Error creating MatchQuality bar chart: {str(e)}")
        return None

def create_seller_mix_bar(df):
    """Stacked bar of FBA vs FBM seller counts (aggregated)."""
    try:
        cols = [c for c in ['fba_seller_count','fbm_seller_count'] if c in df.columns]
        if len(cols) == 0:
            return None
        agg = {c: pd.to_numeric(df[c], errors='coerce').fillna(0).sum() for c in cols}
        plot_df = pd.DataFrame({'Type': list(agg.keys()), 'Count': list(agg.values())})
        fig = px.bar(plot_df, x='Type', y='Count', title="Seller Mix (Aggregated)")
        return fig
    except Exception as e:
        st.error(f"Error creating Seller Mix chart: {str(e)}")
        return None


def render_sidebar():
    """Render the sidebar controls"""
    st.sidebar.header("⚙️ Configuration")

    # Base directory input
    base_dir = st.sidebar.text_input(
        "Base Directory",
        value=os.environ.get("FBA_BASE_DIR", os.getcwd()),
        help="Root directory of the FBA system (FBA_BASE_DIR env var or current directory)"
    )

    # Supplier input - constrained to poundwholesale for this phase
    supplier_options = [
        "poundwholesale.co.uk",
        "poundwholesale_co_uk"
    ]

    supplier = st.sidebar.selectbox(
        "Supplier",
        options=supplier_options + ["Custom..."],
        index=0,
        help="Select supplier or enter custom name (Phase 1: poundwholesale.co.uk only)"
    )

    if supplier == "Custom...":
        supplier = st.sidebar.text_input("Custom Supplier Name")

    # Auto-refresh
    auto_refresh = st.sidebar.slider(
        "Auto Refresh (seconds)",
        min_value=0,
        max_value=300,
        value=0,
        help="How often to refresh the dashboard data (set to 0 to disable)"
    )

    # Resolve and display paths
    loader = MetricsLoader(base_dir)
    paths = loader.resolve_paths(supplier)

    # Diagnostics expander
    with st.sidebar.expander("🔍 Diagnostics - Resolved Paths", expanded=False):
        st.write("### Supplier Normalization")
        if "supplier_variants" in paths:
            variants = paths["supplier_variants"]
            if isinstance(variants, dict):
                st.write(f"**Dotted:** `{variants.get('dotted', 'N/A')}`")
                st.write(f"**Underscored:** `{variants.get('underscored', 'N/A')}`")
                st.write(f"**Hyphenated:** `{variants.get('hyphenated', 'N/A')}`")
        
        st.write("### File Paths")
        for path_name, path_value in paths.items():
            if path_name == "supplier_variants":
                continue
            if path_value:
                st.write(f"**{path_name}:** ✅")
                st.code(str(path_value), language="text")
            else:
                st.write(f"**{path_name}:** ❌ Not found")

    return base_dir, supplier, auto_refresh, paths


def main():
    """Main dashboard application"""
    # Render sidebar
    base_dir, supplier, auto_refresh, paths = render_sidebar()

    # Load metrics with caching
    paths_hash = get_paths_hash(paths)
    metrics_data = get_cached_metrics(base_dir, supplier, str(paths_hash))

    if not metrics_data:
        st.error("❌ Failed to load metrics data")
        return

    # Live Progress section
    link = metrics_data.get('linking_metrics', {})
    cache = metrics_data.get('amazon_cache_metrics', {})
    now_m = link.get('total_matches', 0)
    now_c = cache.get('file_count', 0)
    prev_m = st.session_state.get('prev_matches', now_m)
    prev_c = st.session_state.get('prev_cache', now_c)
    delta_m = now_m - prev_m
    delta_c = now_c - prev_c
    st.session_state['prev_matches'] = now_m
    st.session_state['prev_cache'] = now_c
    st.markdown(f"**Live Progress** — Matches: {now_m} ({delta_m:+}), Cache files: {now_c} ({delta_c:+})")
    
    # Current Category context panel
    cc = metrics_data.get("state_metrics", {}).get("current_category_url")
    short = "—"
    if cc:
        parts = cc.split("://", 1)[-1]
        short = parts.split("/", 1)[-1] if "/" in parts else parts
    
    cp = metrics_data.get("state_metrics", {}).get("category_progress") or {}
    sup_done = cp.get("supplier_products_completed")
    sup_need = cp.get("supplier_products_needing_extraction")
    amz_done = cp.get("amazon_products_completed")
    amz_need = cp.get("amazon_products_needing_analysis")
    
    st.markdown(f"""
    <div class="metric-container">
        <h4>📂 Current Category</h4>
        <p><strong>{short}</strong></p>
        <p>Supplier: <strong>{sup_done if sup_done is not None else '—'}</strong>/<strong>{sup_need if sup_need is not None else '—'}</strong> • 
           Amazon: <strong>{amz_done if amz_done is not None else '—'}</strong>/<strong>{amz_need if amz_need is not None else '—'}</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Render panels
    col1, col2 = st.columns([1, 1])

    with col1:
        render_health_panel(
            metrics_data.get("state_metrics"),
            metrics_data.get("linking_metrics"),
            metrics_data.get("supplier_cache_metrics")
        )

    with col2:
        render_matching_panel(metrics_data.get("linking_metrics"))

    # Financial panel (full width)
    render_financial_panel(metrics_data.get("financial_metrics"))

    # Analytics Charts section
    st.markdown("---")
    st.markdown("## 📊 Analytics Charts")
    
    # Try to load financial data for charts
    fin_metrics = metrics_data.get("financial_metrics", {})
    fin_dir = paths.get("financial_dir")
    
    if fin_dir and os.path.exists(fin_dir):
        try:
            csv_files = [f for f in os.listdir(fin_dir) 
                        if f.startswith('fba_financial_report_') and f.endswith('.csv') 
                        and os.path.isfile(os.path.join(fin_dir, f))]
            
            if csv_files:
                # Load the latest CSV for charting
                latest_csv = sorted(csv_files)[-1]
                df = pd.read_csv(os.path.join(fin_dir, latest_csv))
                
                # Render charts in grid
                c1, c2 = st.columns(2)
                with c1:
                    fig = create_roi_histogram(df)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                with c2:
                    fig = create_price_ratio_histogram(df)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                
                c3, c4 = st.columns(2)
                with c3:
                    fig = create_profit_vs_price_chart(df)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                with c4:
                    fig = create_match_quality_bar(df)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                
                fig_mix = create_seller_mix_bar(df)
                if fig_mix:
                    st.plotly_chart(fig_mix, use_container_width=True)
            else:
                st.info("📁 No financial CSV files available for charting")
        except Exception as e:
            st.error(f"⚠️ Error loading chart data: {str(e)}")
    else:
        st.info("📁 Financial directory not found - charts unavailable")

    # Logs panel (full width)
    render_logs_panel(metrics_data.get("log_data"))

    # Footer
    st.markdown("---")
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | **Supplier:** {supplier}")

    # Non-blocking auto-refresh at the end (after UI renders)
    if auto_refresh and auto_refresh > 0:
        import time as _t
        _t.sleep(auto_refresh)
    st.rerun()


if __name__ == "__main__":
    main()





