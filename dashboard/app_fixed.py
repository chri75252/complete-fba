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

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

import os  # Add missing import

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


def render_health_panel(state_metrics):
    """Render the health status panel"""
    st.subheader("🏥 System Health")

    if not state_metrics or not state_metrics.get("state_file_found", False):
        st.warning("⚠️ State file not found")
        return

    cols = st.columns(3)

    with cols[0]:
        total_products = state_metrics.get("total_products", 0)
        successful_products = state_metrics.get("successful_products", 0)

        st.markdown(f"""
        <div class="metric-container health-ok">
            <h4>Total Products</h4>
            <h2>{format_number(total_products)}</h2>
            <p>Successful: {format_number(successful_products)}</p>
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
        fresh_starts = state_metrics.get("fresh_starts", 0)
        last_index = state_metrics.get("last_processed_index", 0)

        st.markdown(f"""
        <div class="metric-container">
            <h4>Processing Stats</h4>
            <p>Last Index: <strong>{format_number(last_index)}</strong></p>
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
        "clearance-king.co.uk"
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