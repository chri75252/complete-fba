# FBA Analytics Dashboard

A real-time monitoring dashboard for the Amazon FBA Agent System that provides insights into system health, product matching performance, and financial analytics.

## Quick Start

### Prerequisites
- Python 3.10+
- Streamlit dashboard environment

### Installation

```bash
# Navigate to your project directory
cd path/to/your/fba-system

# Install required packages
pip install streamlit pandas python-dateutil

# Set environment variable (optional)
export FBA_BASE_DIR="/path/to/your/project"
```

### Running the Dashboard

```bash
# Start the dashboard
streamlit run dashboard/app.py

# Or specify the exact path
python -m streamlit run dashboard/app.py --server.port 8501
```

The dashboard will open automatically in your browser at `http://localhost:8501`

## Features

### 📊 Real-time Monitoring
- **System Health**: Monitor processing state, category completion, and system status
- **Amazon Matching**: Track confidence levels, match methods, and EAN coverage
- **Financial Performance**: Analyze ROI, profit potential, and product profitability
- **Live Logs**: View real-time system logs and processing status

### 🔧 Configuration Options

#### Sidebar Controls
- **Base Directory**: Path to your FBA system (auto-detected from `FBA_BASE_DIR` env var)
- **Supplier Selection**: Choose from predefined suppliers or enter custom name
- **Auto Refresh**: Set refresh interval (10-300 seconds)

#### Supported Suppliers
- `poundwholesale.co.uk` / `poundwholesale_co_uk`
- `clearance-king.co.uk` / `clearance_king_co_uk`
- Custom suppliers (enter name manually)

## Data Sources

The dashboard reads from existing system files without requiring any database:

### Required Files
```
OUTPUTS/CACHE/processing_states/<supplier>_processing_state.json
OUTPUTS/FBA_ANALYSIS/linking_maps/<supplier>/linking_map.json
OUTPUTS/FBA_ANALYSIS/financial_reports/*.csv
logs/debug/run_custom_*.log
```

### File Resolution Logic
- Automatically normalizes supplier names (`domain.tld` → `domain_tld`)
- Finds the newest matching files for each supplier
- Gracefully handles missing files and directories

## Performance Features

### ⚡ Efficient Data Processing
- **Chunked JSON Parsing**: Handles large files (131K+ entries) without memory issues
- **Smart Caching**: Only reloads data when files change
- **Streaming Log Tailing**: Efficient log file reading
- **Memory Management**: Prevents UI freezing with large datasets

### 🛡️ Error Handling
- Graceful degradation when files are missing
- Clear error messages without tracebacks
- Robust column inference for CSV files
- Handles various datetime formats automatically

## Understanding the Metrics

### Health Panel
- **Total Categories**: Should equal 233 for optimal performance
- **Processing Status**: Current system state (active, completed, error)
- **Successful Products**: Count of successfully processed items
- **Fresh Starts**: Number of times system restarted from scratch

### Matching Panel
- **Total Matches**: Number of supplier-to-Amazon matches
- **High Confidence Rate**: Percentage of matches with high confidence scores
- **No EAN Count**: Products matched without EAN codes (title-based matching)
- **Primary Method**: Most successful matching approach

### Financial Panel
- **Files Scanned**: Number of CSV files processed
- **Total Rows**: Total number of product records analyzed
- **Profitable Products**: Products with ROI > 15%
- **Average ROI**: Mean return on investment across all products
- **Total Profit Potential**: Sum of all profitable product margins

## Troubleshooting

### Common Issues

#### Dashboard Shows "—" (Missing Data)
**Problem**: Required files not found
**Solution**:
1. Verify `FBA_BASE_DIR` points to correct project root
2. Check that processing has completed successfully
3. Use sidebar "Resolved Paths" to confirm file locations

#### High Memory Usage
**Problem**: Large JSON files causing performance issues
**Solution**: Dashboard uses chunked processing automatically. If issues persist:
1. Increase cache TTL in `@st.cache_data(ttl=60)`
2. Reduce auto-refresh frequency

#### Financial Panel Shows No Data
**Problem**: CSV column names don't match expected patterns
**Solution**: Dashboard automatically detects multiple column name patterns:
- ROI: `roi`, `roi_percent`, `return_on_investment`
- Profit: `profit`, `net_profit`, `estimated_profit`, `margin`

#### Log Panel Empty
**Problem**: No matching log files found
**Solution**: Ensure logs are in `logs/debug/` directory with `run_custom_*.log` pattern

### Performance Optimization

For large datasets (>100K products):
1. Set auto-refresh to 60+ seconds
2. Monitor memory usage in Task Manager
3. Consider processing data in batches

## Development

### Adding New Panels
1. Add new function in `metrics_core.py` for data loading
2. Create rendering function in `app.py`
3. Add panel to main dashboard layout

### Custom Metrics
Modify `metrics_core.py` to add:
- New data sources
- Custom calculations
- Additional filtering options

### MCP Integration (Optional)
```bash
# Install MCP dependencies
pip install mcp

# Run MCP server
python dashboard/fba_metrics_mcp.py
```

Available MCP tools:
- `get_health(supplier)` - System health metrics
- `get_matching_stats(supplier)` - Matching performance
- `get_financial_summary()` - Financial aggregates
- `tail_latest_log(lines)` - Recent log entries

## Security & Data Privacy

- **Read-Only Access**: Dashboard only reads existing files
- **No External Dependencies**: Works offline after installation
- **Local Processing**: All data processed locally, no external connections
- **No Data Modification**: Cannot change or delete system files

## Support

For issues or questions:
1. Check this README for common solutions
2. Verify file structure and permissions
3. Review Streamlit console output for error details
4. Ensure all prerequisites are installed correctly

## Technical Details

### Dependencies
- `streamlit`: Web application framework
- `pandas`: Data processing and CSV handling
- `python-dateutil`: Flexible datetime parsing
- Standard library: `json`, `os`, `re`, `datetime`, `typing`

### Architecture
- `metrics_core.py`: Pure Python data processing (no Streamlit dependencies)
- `app.py`: Streamlit UI and visualization
- Separation of concerns enables easy testing and maintenance

### Caching Strategy
- File modification time checking prevents unnecessary reloads
- Streamlit built-in caching with 60-second TTL
- Memory-efficient chunked processing for large files