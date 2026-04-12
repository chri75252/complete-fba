import sys
sys.path.insert(0, r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion')
from dashboard_legacy_streamlit.metrics_core import MetricsLoader

loader = MetricsLoader(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion')
paths = loader.resolve_paths('efghousewares.co.uk__sandbox__4e269fb4')
print('financial_dir:', paths['financial_dir'])
import os
if paths['financial_dir']:
    print('CSV files:', [f for f in os.listdir(paths['financial_dir']) if f.endswith('.csv') and 'MERGED' not in f])
fm = loader.load_financial_metrics(paths['financial_dir'])
print('financial_metrics:', fm)
