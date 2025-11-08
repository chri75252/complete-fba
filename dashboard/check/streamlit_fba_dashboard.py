import streamlit as st
import pandas as pd
import os
import json
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Configure page
st.set_page_config(
    page_title="Amazon FBA Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .positive { color: #00cc00; font-weight: bold; }
    .negative { color: #ff4444; font-weight: bold; }
    .warning { color: #ff9900; font-weight: bold; }
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

class FBAAnalyticsDashboard:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.financial_reports_path = self.base_path / "OUTPUTS" / "FBA_ANALYSIS" / "financial_reports"
        self.poundwholesale_path = self.financial_reports_path / "poundwholesale-co-uk"
        self.cache_path = self.base_path / "OUTPUTS" / "CACHE" / "processing_states"
        
        # Column aliases for flexible schema support
        self.column_aliases = {
            'SupplierPrice_incVAT': ['supplier_price_gbp', 'price_gbp', 'supplier_price', 'cost'],
            'SellingPrice_incVAT': ['amazon_price_gbp', 'amazon_price', 'selling_price', 'list_price'],
            'NetProfit': ['net_profit', 'profit', 'profit_gbp', 'estimated_profit'],
            'ROI': ['roi_pct', 'roi', 'return_on_investment', 'roi_percentage'],
            'ProfitMargin': ['profit_margin_pct', 'profit_margin', 'margin'],
            'EAN': ['ean', 'barcode'],
            'ASIN': ['asin', 'amazon_asin'],
            'SupplierTitle': ['supplier_title', 'title'],
            'AmazonTitle': ['amazon_title']
        }

    def get_latest_financial_report(self):
        """Get the most recent financial report CSV file with robust error handling."""
        try:
            # Look for CSV files in the expected location
            if self.poundwholesale_path.exists():
                csv_files = list(self.poundwholesale_path.glob("fba_financial_report_*.csv"))
                if csv_files:
                    latest_file = max(csv_files, key=lambda x: x.stat().st_mtime)
                    return latest_file

            # Fallback: Look in parent financial_reports directory
            if self.financial_reports_path.exists():
                csv_files = list(self.financial_reports_path.glob("fba_financial_report_*.csv"))
                if csv_files:
                    latest_file = max(csv_files, key=lambda x: x.stat().st_mtime)
                    return latest_file

            return None

        except Exception as e:
            st.error(f"Error finding financial reports: {str(e)}")
            return None

    def get_available_reports(self):
        """Get list of available financial report files with validation."""
        candidates = []
        try:
            # Check supplier-specific directory first
            if self.poundwholesale_path.exists():
                for p in sorted(self.poundwholesale_path.glob("fba_financial_report_*.csv"), 
                               key=lambda x: x.stat().st_mtime, reverse=True):
                    if p.stat().st_size == 0:
                        continue
                    # Validate header
                    try:
                        with open(p, 'r', encoding='utf-8') as f:
                            header = f.readline().strip().split(',')
                            # Check for essential columns
                            if any(col.lower() in ['ean', 'barcode'] for col in header) and \
                               any(col.lower() in ['netprofit', 'net_profit', 'profit', 'roi'] for col in header):
                                candidates.append(p)
                    except Exception:
                        pass
            
            # Fallback to parent directory
            if not candidates and self.financial_reports_path.exists():
                for p in sorted(self.financial_reports_path.glob("fba_financial_report_*.csv"),
                               key=lambda x: x.stat().st_mtime, reverse=True):
                    if p.stat().st_size == 0:
                        continue
                    try:
                        with open(p, 'r', encoding='utf-8') as f:
                            header = f.readline().strip().split(',')
                            if any(col.lower() in ['ean', 'barcode'] for col in header) and \
                               any(col.lower() in ['netprofit', 'net_profit', 'profit', 'roi'] for col in header):
                                candidates.append(p)
                    except Exception:
                        pass
            
            return candidates
        except Exception as e:
            st.error(f"Error scanning for reports: {str(e)}")
            return []

    def load_financial_data(self, file_path):
        """Load financial data with comprehensive error handling, schema aliasing, and validation."""
        try:
            if not file_path or not file_path.exists():
                st.warning("No financial report file found. Please run the FBA analysis first.")
                return None

            # Performance safeguard for large files
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            use_sampling = file_size_mb > 50
            
            if use_sampling:
                st.warning(f"📁 Large file detected ({file_size_mb:.1f} MB). Using sampled mode (first 100k rows).")

            # Read CSV with error handling
            try:
                if use_sampling:
                    df = pd.read_csv(file_path, nrows=100000)
                else:
                    df = pd.read_csv(file_path)

                # Validate DataFrame structure
                if df.empty:
                    st.error("Financial report is empty")
                    return None

                # Apply column aliasing for flexible schema support
                coercion_report = {}
                for std_name, alt_names in self.column_aliases.items():
                    if std_name not in df.columns:
                        for alt in alt_names:
                            if alt in df.columns:
                                df.rename(columns={alt: std_name}, inplace=True)
                                st.info(f"🔄 Mapped column: `{alt}` → `{std_name}`")
                                break

                # Numeric coercion with reporting
                numeric_columns = ['SupplierPrice_incVAT', 'SellingPrice_incVAT', 'NetProfit', 'ROI', 'ProfitMargin']
                for col in numeric_columns:
                    if col in df.columns:
                        before = df[col].isna().sum()
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                        after = df[col].isna().sum()
                        coerced = max(0, after - before)
                        if coerced > 0:
                            coercion_report[col] = coerced

                # Show diagnostics
                with st.expander("🔍 Diagnostics — Schema & Coercion"):
                    st.write(f"**File:** `{file_path.name}`")
                    st.write(f"**Size:** {file_size_mb:.2f} MB")
                    st.write(f"**Rows Loaded:** {len(df):,}")
                    st.write(f"**Columns:** {len(df.columns)}")
                    st.json({'available_columns': list(df.columns), 'coercion_counts': coercion_report})

                # Data quality alert for extreme ROI values
                if 'ROI' in df.columns:
                    roi_series = pd.to_numeric(df['ROI'], errors='coerce')
                    suspicious_count = (roi_series > 1000).sum()
                    total_count = len(df)
                    if suspicious_count > 0:
                        pct = (suspicious_count / total_count) * 100
                        st.error(f"⚠️ **DATA QUALITY ALERT:** {suspicious_count:,}/{total_count:,} ({pct:.1f}%) products have ROI > 1000% — likely indicates wrong Amazon matches.")

                # Add MatchQuality badges based on ROI
                if 'ROI' in df.columns:
                    df['MatchQuality'] = pd.to_numeric(df['ROI'], errors='coerce').apply(
                        lambda r: '✅ Good' if (pd.notna(r) and r < 200) else (
                            '⚠️ Review' if (pd.notna(r) and r < 1000) else '❌ Suspicious'
                        )
                    )

                return df

            except pd.errors.EmptyDataError:
                st.error("Financial report file is empty or corrupted")
                return None
            except pd.errors.ParserError as e:
                st.error(f"Error parsing financial report: {str(e)}")
                return None

        except Exception as e:
            st.error(f"Unexpected error loading financial data: {str(e)}")
            return None

    def get_processing_state(self):
        """Get current processing state information."""
        try:
            # Use underscored format for state file (actual filename format)
            state_file = self.cache_path / "poundwholesale_co_uk_processing_state.json"
            if state_file.exists():
                with open(state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            st.warning(f"Could not load processing state: {str(e)}")
        return None

    def calculate_metrics(self, df):
        """Calculate key performance metrics using flexible column names."""
        if df is None or df.empty:
            return {}

        try:
            # Use kpi_df that doesn't require ASIN
            kpi_df = df.dropna(subset=['NetProfit']) if 'NetProfit' in df.columns else df.copy()
            
            metrics = {
                'total_products': len(kpi_df),
                'profitable_products': len(kpi_df[kpi_df['NetProfit'] > 0]) if 'NetProfit' in kpi_df.columns else 0,
                'avg_roi': kpi_df['ROI'].mean() if 'ROI' in kpi_df.columns else 0,
                'avg_profit_margin': kpi_df['ProfitMargin'].mean() if 'ProfitMargin' in kpi_df.columns else 0,
                'total_potential_profit': kpi_df['NetProfit'].sum() if 'NetProfit' in kpi_df.columns else 0,
                'avg_supplier_price': kpi_df['SupplierPrice_incVAT'].mean() if 'SupplierPrice_incVAT' in kpi_df.columns else 0,
                'avg_selling_price': kpi_df['SellingPrice_incVAT'].mean() if 'SellingPrice_incVAT' in kpi_df.columns else 0,
                'profitable_percentage': (len(kpi_df[kpi_df['NetProfit'] > 0]) / len(kpi_df)) * 100 if 'NetProfit' in kpi_df.columns and len(kpi_df) > 0 else 0
            }
            return metrics
        except Exception as e:
            st.error(f"Error calculating metrics: {str(e)}")
            return {}

    def create_profitability_chart(self, df):
        """Create profitability analysis chart."""
        if df is None or df.empty:
            return None

        try:
            # Create profit categories
            df['Profit_Category'] = pd.cut(df['NetProfit'],
                                         bins=[-float('inf'), 0, 10, 50, float('inf')],
                                         labels=['Loss', 'Low Profit (0-10)', 'Medium Profit (10-50)', 'High Profit (>50)'])

            fig = px.histogram(df, x='Profit_Category',
                             title="Product Profitability Distribution",
                             color='Profit_Category',
                             category_orders={'Profit_Category': ['Loss', 'Low Profit (0-10)', 'Medium Profit (10-50)', 'High Profit (>50)']})

            fig.update_layout(showlegend=False)
            return fig
        except Exception as e:
            st.error(f"Error creating profitability chart: {str(e)}")
            return None

    def create_roi_chart(self, df):
        """Create ROI analysis chart."""
        if df is None or df.empty:
            return None

        try:
            # Create ROI categories
            df['ROI_Category'] = pd.cut(df['ROI'],
                                      bins=[0, 50, 100, 500, float('inf')],
                                      labels=['Low (0-50%)', 'Medium (50-100%)', 'High (100-500%)', 'Very High (>500%)'])

            fig = px.box(df, x='ROI_Category', y='ROI',
                        title="ROI Distribution by Category",
                        color='ROI_Category')

            fig.update_layout(showlegend=False)
            return fig
        except Exception as e:
            st.error(f"Error creating ROI chart: {str(e)}")
            return None

    def create_price_comparison_chart(self, df):
        """Create supplier vs Amazon price comparison."""
        if df is None or df.empty:
            return None

        try:
            # Sample data if too many points
            plot_df = df.head(1000) if len(df) > 1000 else df

            fig = px.scatter(plot_df, x='SupplierPrice_incVAT', y='SellingPrice_incVAT',
                            title="Supplier Price vs Amazon Selling Price",
                            hover_data=['SupplierTitle', 'AmazonTitle'],
                            color='NetProfit',
                            color_continuous_scale='RdYlGn')

            # Add diagonal line for reference
            fig.add_shape(
                type="line",
                x0=0, y0=0,
                x1=max(plot_df['SupplierPrice_incVAT']), y1=max(plot_df['SupplierPrice_incVAT']),
                line=dict(color="gray", dash="dash")
            )

            return fig
        except Exception as e:
            st.error(f"Error creating price comparison chart: {str(e)}")
            return None

    def create_roi_histogram(self, df):
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

    def create_profit_vs_price_chart(self, df):
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
                             labels={'SellingPrice_incVAT': 'Selling Price (GBP)', 'NetProfit': 'Net Profit (GBP)'} )
            return fig
        except Exception as e:
            st.error(f"Error creating Profit vs Price chart: {str(e)}")
            return None

    def create_price_ratio_histogram(self, df):
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

    def create_match_quality_bar(self, df):
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

    def create_seller_mix_bar(self, df):
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

    def render_dashboard(self):
        """Main dashboard rendering."""
        st.markdown('<h1 class="main-header">📊 Amazon FBA Analytics Dashboard</h1>',
                    unsafe_allow_html=True)

        # Sidebar information
        with st.sidebar:
            st.markdown("## 📋 System Information")

            # Processing state
            state = self.get_processing_state()
            if state:
                st.markdown("### Processing Status")
                if 'system_progression' in state:
                    progression = state['system_progression']
                    st.write(f"**Current Phase:** {progression.get('current_phase', 'Unknown')}")
                    st.write(f"**Category Index:** {progression.get('persistent_category_index', 0)}")
                    st.write(f"**Supplier Products Completed:** {progression.get('supplier_products_completed', 0)}")
                    st.write(f"**Amazon Products Completed:** {progression.get('amazon_products_completed', 0)}")

            # Run picker
            st.markdown("### 📁 Select Financial Report")
            available_reports = self.get_available_reports()
            
            if not available_reports:
                st.error("No financial reports found!")
                st.markdown("""
                **Required Actions:**
                1. Run the FBA analysis system
                2. Generate financial reports
                3. Refresh this dashboard
                """)
                return
            
            # Run picker selectbox
            selected_file = st.selectbox(
                "Available Reports",
                available_reports,
                format_func=lambda p: f"{p.name} ({datetime.fromtimestamp(p.stat().st_mtime).strftime('%Y-%m-%d %H:%M')})"
            )
            
            # Display selected run info
            if selected_file:
                st.write("**Selected Run Details:**")
                st.write(f"**Path:** `{selected_file}`")
                st.write(f"**Size:** {selected_file.stat().st_size / 1024:.1f} KB")
                st.write(f"**Modified:** {datetime.fromtimestamp(selected_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")

        # Load financial data from selected file
        with st.spinner("Loading financial data..."):
            df = self.load_financial_data(selected_file)

        if df is None:
            st.error("❌ No financial data available. Please run the FBA analysis first.")
            return

        # Calculate metrics
        metrics = self.calculate_metrics(df)

        # Key metrics row
        st.markdown("## 🎯 Key Performance Metrics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Total Products</h3>
                <h2>{metrics.get('total_products', 0):,}</h2>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            profitable_pct = metrics.get('profitable_percentage', 0)
            color_class = "positive" if profitable_pct > 70 else "warning" if profitable_pct > 50 else "negative"
            st.markdown(f"""
            <div class="metric-card">
                <h3>Profitable Products</h3>
                <h2 class="{color_class}">{profitable_pct:.1f}%</h2>
                <p>{metrics.get('profitable_products', 0):,} out of {metrics.get('total_products', 0):,}</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            avg_roi = metrics.get('avg_roi', 0)
            color_class = "positive" if avg_roi > 100 else "warning" if avg_roi > 50 else "negative"
            st.markdown(f"""
            <div class="metric-card">
                <h3>Average ROI</h3>
                <h2 class="{color_class}">{avg_roi:.0f}%</h2>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            total_profit = metrics.get('total_potential_profit', 0)
            color_class = "positive" if total_profit > 0 else "negative"
            st.markdown(f"""
            <div class="metric-card">
                <h3>Total Potential Profit</h3>
                <h2 class="{color_class}">£{total_profit:,.0f}</h2>
            </div>
            """, unsafe_allow_html=True)

        # Charts section
        st.markdown("## 📈 Analytics Charts")

        # Chart tabs
        tab1, tab2, tab3 = st.tabs(["Profitability Analysis", "ROI Distribution", "Price Comparison"])

        with tab1:
            fig1 = self.create_profitability_chart(df)
            if fig1:
                st.plotly_chart(fig1, use_container_width=True)

            # Top profitable products table
            st.markdown("### 💰 Top 10 Most Profitable Products")
            top_profitable = df.nlargest(10, 'NetProfit')[['SupplierTitle', 'AmazonTitle', 'NetProfit', 'ROI', 'ProfitMargin']]
            st.dataframe(top_profitable, use_container_width=True)

        with tab2:
            fig2 = self.create_roi_chart(df)
            if fig2:
                st.plotly_chart(fig2, use_container_width=True)

            # ROI statistics
            st.markdown("### 📊 ROI Statistics")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Median ROI", f"{df['ROI'].median():.1f}%")
            with col2:
                st.metric("Highest ROI", f"{df['ROI'].max():.1f}%")
            with col3:
                st.metric("Products with ROI > 100%", f"{len(df[df['ROI'] > 100]):,}")

        with tab3:
            fig3 = self.create_price_comparison_chart(df)
            if fig3:
                st.plotly_chart(fig3, use_container_width=True)

            # Price analysis
            st.markdown("### 💷 Price Analysis")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Avg Supplier Price", f"£{metrics.get('avg_supplier_price', 0):.2f}")
                st.metric("Avg Amazon Price", f"£{metrics.get('avg_selling_price', 0):.2f}")
            with col2:
                avg_markup = ((metrics.get('avg_selling_price', 0) - metrics.get('avg_supplier_price', 0)) / metrics.get('avg_supplier_price', 1)) * 100
                st.metric("Average Markup", f"{avg_markup:.1f}%")

        # Data table with filtering
        st.markdown("## 📋 Full Product Data")

        # Filters
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            min_roi = st.slider("Minimum ROI (%)", 0, 1000, 0)
        with col2:
            min_profit = st.slider("Minimum Profit (£)", -50, 1000, -50)
        with col3:
            show_only_profitable = st.checkbox("Show only profitable products")
        with col4:
            # Match quality filter with default to exclude Suspicious
            if 'MatchQuality' in df.columns:
                quality_options = df['MatchQuality'].unique().tolist()
                default_quality = [q for q in quality_options if '❌ Suspicious' not in q]
                selected_quality = st.multiselect(
                    "Match Quality",
                    options=quality_options,
                    default=default_quality
                )
            else:
                selected_quality = None

        # Apply filters
        filtered_df = df.copy()
        if 'ROI' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['ROI'] >= min_roi]
        if 'NetProfit' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['NetProfit'] >= min_profit]
        if show_only_profitable and 'NetProfit' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['NetProfit'] > 0]
        if selected_quality and 'MatchQuality' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['MatchQuality'].isin(selected_quality)]

        st.markdown(f"**Showing {len(filtered_df):,} of {len(df):,} products**")

        # Select and reorder columns for display
        display_columns = ['SupplierTitle', 'AmazonTitle', 'SupplierPrice_incVAT', 'SellingPrice_incVAT',
                          'NetProfit', 'ROI', 'ProfitMargin', 'EAN', 'ASIN']
        available_columns = [col for col in display_columns if col in filtered_df.columns]

        if available_columns:
            # Format numeric columns for better display
            display_df = filtered_df[available_columns].copy()
            if 'NetProfit' in display_df.columns:
                display_df['NetProfit'] = display_df['NetProfit'].apply(lambda x: f"£{x:.2f}")
            if 'ROI' in display_df.columns:
                display_df['ROI'] = display_df['ROI'].apply(lambda x: f"{x:.1f}%")
            if 'ProfitMargin' in display_df.columns:
                display_df['ProfitMargin'] = display_df['ProfitMargin'].apply(lambda x: f"{x:.1f}%")
            if 'SupplierPrice_incVAT' in display_df.columns:
                display_df['SupplierPrice_incVAT'] = display_df['SupplierPrice_incVAT'].apply(lambda x: f"£{x:.2f}")
            if 'SellingPrice_incVAT' in display_df.columns:
                display_df['SellingPrice_incVAT'] = display_df['SellingPrice_incVAT'].apply(lambda x: f"£{x:.2f}")

            st.dataframe(display_df, use_container_width=True, height=400)

        # Download section
        st.markdown("## 📥 Data Export")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("📊 Download Filtered Data as CSV"):
                if not filtered_df.empty:
                    csv_data = filtered_df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name=f"fba_filtered_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No data to download")

        with col2:
            if st.button("🔄 Refresh Dashboard"):
                st.rerun()

def main():
    """Main application entry point."""
    try:
        dashboard = FBAAnalyticsDashboard()
        dashboard.render_dashboard()
    except Exception as e:
        st.error(f"Dashboard error: {str(e)}")
        st.markdown("Please check the console logs for more details.")

if __name__ == "__main__":
    main()
