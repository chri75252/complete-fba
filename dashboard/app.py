"""
FBA Analytics Dashboard
Streamlit dashboard for monitoring Amazon FBA Agent System performance
"""

import streamlit as st
import os
import time
from datetime import datetime
from metrics_core import MetricsLoader, load_metrics

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


@st.cache_data(ttl=60)
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
        mtimes = []
        for path_key, path_value in paths.items():
            if path_value and os.path.exists(path_value):
                mtimes.append(os.path.getmtime(path_value))
        return hash(tuple(mtimes))
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


def render_health_panel(state_metrics):
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
        successful = state_metrics.get("successful_products", 0)
        processed = state_metrics.get("processed_products", 0)
        fresh_starts = state_metrics.get("fresh_starts", 0)

        st.markdown(f"""
        <div class="metric-container">
            <h4>Processing Stats</h4>
            <p>Successful: <strong>{format_number(successful)}</strong></p>
            <p>Processed: <strong>{format_number(processed)}</strong></p>
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

    # Auto-refresh mechanism
    if auto_refresh > 0:
        time.sleep(auto_refresh)
        st.rerun()

    # Load metrics with caching
    paths_hash = get_paths_hash(paths)
    metrics_data = get_cached_metrics(base_dir, supplier, str(paths_hash))

    if not metrics_data:
        st.error("❌ Failed to load metrics data")
        return

    # Render panels
    col1, col2 = st.columns([1, 1])

    with col1:
        render_health_panel(metrics_data.get("state_metrics"))

    with col2:
        render_matching_panel(metrics_data.get("linking_metrics"))

    # Financial panel (full width)
    render_financial_panel(metrics_data.get("financial_metrics"))

    # Logs panel (full width)
    render_logs_panel(metrics_data.get("log_data"))

    # Footer
    st.markdown("---")
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | **Supplier:** {supplier}")


if __name__ == "__main__":
    main()
