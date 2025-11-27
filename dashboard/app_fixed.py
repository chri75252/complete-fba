"""
FBA Analytics Dashboard - FIXED VERSION
Streamlit dashboard for monitoring Amazon FBA Agent System performance
Fixed issues: path resolution, timeout handling, auto-refresh loops
"""

import streamlit as st
import os
import time
import sys
from datetime import datetime
from pathlib import Path
import plotly.express as px
import pandas as pd

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from metrics_core import MetricsLoader, load_metrics
except ImportError as e:
    st.error(f"❌ Cannot import metrics_core: {str(e)}")
    st.stop()

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
.error-container {
    background-color: #ffebee;
    border: 1px solid #f44336;
    border-radius: 0.5rem;
    padding: 1rem;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)


def get_base_directory():
    """Get the correct base directory for the FBA system"""
    # Try multiple approaches to find the right base directory
    candidates = [
        os.environ.get("FBA_BASE_DIR"),
        str(Path(__file__).parent.parent),  # Dashboard parent directory
        os.getcwd(),
        "."
    ]

    for candidate in candidates:
        if candidate and os.path.exists(os.path.join(candidate, "OUTPUTS")):
            return candidate

    # Fallback to current directory
    return os.getcwd()


def validate_supplier_data(base_dir, supplier):
    """Validate that supplier data exists"""
    loader = MetricsLoader(base_dir)
    paths = loader.resolve_paths(supplier)

    issues = []
    if not paths.get("state_file") or not os.path.exists(paths["state_file"]):
        issues.append("State file not found")
    if not paths.get("linking_file") or not os.path.exists(paths["linking_file"]):
        issues.append("Linking map file not found")
    if not paths.get("financial_dir") or not os.path.exists(paths["financial_dir"]):
        issues.append("Financial reports directory not found")
    if not paths.get("logs_dir") or not os.path.exists(paths["logs_dir"]):
        issues.append("Logs directory not found")

    return issues, paths


@st.cache_data(ttl=120)  # Increased TTL to prevent excessive reloading
def get_cached_metrics(base_dir: str, supplier: str):
    """Cached metrics loader with better error handling"""
    try:
        # Validate supplier data first
        issues, paths = validate_supplier_data(base_dir, supplier)

        if issues:
            return {
                "error": True,
                "issues": issues,
                "paths": paths,
                "state_metrics": {"state_file_found": False},
                "linking_metrics": {"total_matches": 0},
                "financial_metrics": {"files_scanned": 0},
                "log_data": [[], None]
            }

        # Load metrics with timeout protection
        return load_metrics(base_dir, supplier)
    except Exception as e:
        return {
            "error": True,
            "issues": [f"Error loading metrics: {str(e)}"],
            "state_metrics": {"state_file_found": False},
            "linking_metrics": {"total_matches": 0},
            "financial_metrics": {"files_scanned": 0},
            "log_data": [[], None]
        }


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


def render_error_panel(issues, paths):
    """Render error panel when data files are missing"""
    st.subheader("❌ Data Loading Issues")

    st.markdown("""
    <div class="error-container">
        <h4>⚠️ Cannot Load Dashboard Data</h4>
        <p>The dashboard cannot find the required data files. Please check:</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("**Issues Found:**")
    for issue in issues:
        st.write(f"• {issue}")

    st.write("**Resolved Paths:**")
    for path_name, path_value in paths.items():
        if path_value:
            st.write(f"• **{path_name}:** `{path_value}` ✅")
        else:
            st.write(f"• **{path_name}:** Not found ❌")

    st.write("**Troubleshooting Steps:**")
    st.write("1. Ensure the FBA system has been run at least once")
    st.write("2. Check that OUTPUTS directory contains data files")
    st.write("3. Verify supplier name matches the actual data directory structure")
    st.write("4. Check file permissions and accessibility")


def render_health_panel(state_metrics, linking_metrics=None, supplier_cache_metrics=None):
    """Render the health status panel"""
    st.subheader("🏥 System Health")

    if not state_metrics or not state_metrics.get("state_file_found", False):
        st.warning("⚠️ State file not found")
        return

    cols = st.columns(3)

    with cols[0]:
        # System Progression (Phase & Category)
        phase = state_metrics.get("processing_status", "Unknown")
        cat_idx = state_metrics.get("persistent_category_index", 0)
        total_cats = state_metrics.get("total_categories", 0)
        
        # Current category name
        cc = state_metrics.get("current_category_url", "")
        short_cat = "—"
        if cc:
            parts = cc.split("://", 1)[-1]
            short_cat = parts.split("/", 1)[-1] if "/" in parts else parts

        st.markdown(f"""
        <div class="metric-container">
            <h4>System Progression</h4>
            <p>Phase: <strong>{phase}</strong></p>
            <p>Category: <strong>{cat_idx}</strong> / <strong>{total_cats}</strong></p>
            <p>Current: {short_cat}</p>
        </div>
        """, unsafe_allow_html=True)

    with cols[1]:
        # Extraction & Analysis Progress
        cp = state_metrics.get("category_progress") or {}
        sup_done = cp.get("supplier_products_completed", 0)
        sup_need = cp.get("supplier_products_needing_extraction", 0)
        amz_done = cp.get("amazon_products_completed", 0)
        amz_need = cp.get("amazon_products_needing_analysis", 0)

        st.markdown(f"""
        <div class="metric-container">
            <h4>Category Progress</h4>
            <p>Supplier Extracted: <strong>{format_number(sup_done)}</strong> / <strong>{format_number(sup_need)}</strong></p>
            <p>Amazon Analyzed: <strong>{format_number(amz_done)}</strong> / <strong>{format_number(amz_need)}</strong></p>
        </div>
        """, unsafe_allow_html=True)

    with cols[2]:
        # Total Stats
        linking_total = linking_metrics.get("total_matches", 0) if linking_metrics else 0
        # Use total_products from state as "Total Extracted" if available, else fallback
        total_extracted = state_metrics.get("total_products", 0)
        fresh_starts = state_metrics.get("fresh_starts", 0)

        st.markdown(f"""
        <div class="metric-container">
            <h4>Total Stats</h4>
            <p>Total Extracted: <strong>{format_number(total_extracted)}</strong></p>
            <p>Total Processed: <strong>{format_number(linking_total)}</strong></p>
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


def render_logs_panel(log_data):
    """Render the logs panel"""
    st.subheader("📋 Latest Logs")

    if not log_data or not log_data[0]:
        st.warning("⚠️ No log data available")
        return

    lines, filename = log_data

    st.write(f"**Showing last {len(lines)} lines from:** `{filename}`")

    # Display logs with syntax highlighting
    log_text = "\n".join(lines[-50:])  # Show only last 50 lines to prevent UI lag
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

    # Base directory input with auto-detection
    base_dir = get_base_directory()
    base_dir = st.sidebar.text_input(
        "Base Directory",
        value=base_dir,
        help="Root directory of the FBA system (auto-detected)"
    )

    # Supplier input with better defaults
    supplier_options = [
        "poundwholesale_co_uk",
        "poundwholesale.co.uk",
        "clearance_king_co_uk",
        "clearance-king.co.uk",
        "angelwholesale_co_uk",
        "angelwholesale.co.uk"
    ]

    supplier = st.sidebar.selectbox(
        "Supplier",
        options=supplier_options + ["Custom..."],
        index=0,
        help="Select supplier that matches your data directory structure"
    )

    if supplier == "Custom...":
        supplier = st.sidebar.text_input("Custom Supplier Name")

    # Auto-refresh with safety controls
    auto_refresh = st.sidebar.slider(
        "Auto Refresh (seconds)",
        min_value=0,
        max_value=300,
        value=60,  # Increased default to prevent rapid refresh
        help="Set to 0 to disable auto-refresh (recommended for debugging)"
    )

    # Validate data availability
    issues, paths = validate_supplier_data(base_dir, supplier)

    if issues:
        st.sidebar.error("⚠️ Data Issues Found")
        for issue in issues:
            st.sidebar.write(f"• {issue}")
    else:
        st.sidebar.success("✅ All data files found")

    # System information
    st.sidebar.write("---")
    st.sidebar.write("**System Information:**")
    st.sidebar.write(f"Base Dir: `{base_dir}`")
    st.sidebar.write(f"Supplier: `{supplier}`")
    st.sidebar.write(f"Auto Refresh: `{auto_refresh}s`")

    return base_dir, supplier, auto_refresh


def main():
    """Main dashboard application with better error handling"""
    try:
        # Render sidebar
        base_dir, supplier, auto_refresh = render_sidebar()

        # Load metrics with error handling
        metrics_data = get_cached_metrics(base_dir, supplier)

        # Check for errors
        if metrics_data.get("error"):
            render_error_panel(metrics_data.get("issues", []), metrics_data.get("paths", {}))

            # Stop auto-refresh if there are errors
            if auto_refresh > 0:
                st.warning("⚠️ Auto-refresh disabled due to data loading errors")
                auto_refresh = 0

        # Render panels only if data is available
        if not metrics_data.get("error"):
            # Live Progress Ticker
            link = metrics_data.get('linking_metrics', {})
            now_m = link.get('total_matches', 0)
            prev_m = st.session_state.get('prev_matches', now_m)
            delta_m = now_m - prev_m
            st.session_state['prev_matches'] = now_m
            
            st.markdown(f"**Live Progress** — Matches: {now_m} ({delta_m:+})")

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
            
            fin_metrics = metrics_data.get("financial_metrics", {})
            fin_dir = metrics_data.get("paths", {}).get("financial_dir")
            
            # Check if we have a latest file identified by metrics_core
            latest_file = fin_metrics.get("latest_file")
            
            if fin_dir and latest_file and os.path.exists(os.path.join(fin_dir, latest_file)):
                try:
                    df = pd.read_csv(os.path.join(fin_dir, latest_file))
                    
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
                except Exception as e:
                    st.error(f"⚠️ Error loading chart data: {str(e)}")
            else:
                st.info("📁 No financial CSV files available for charting")

            # Logs panel (full width)
            render_logs_panel(metrics_data.get("log_data"))

        # Auto-refresh mechanism with safety check
        if auto_refresh > 0:
            time.sleep(auto_refresh)
            st.rerun()

        # Footer
        st.markdown("---")
        st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | **Supplier:** {supplier}")

    except Exception as e:
        st.error(f"❌ Dashboard error: {str(e)}")
        st.write("**Please check:**")
        st.write("1. Base directory path is correct")
        st.write("2. Supplier name matches data directories")
        st.write("3. Required data files exist")
        st.write("4. File permissions are correct")


if __name__ == "__main__":
    main()