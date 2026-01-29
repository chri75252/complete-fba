import pandas as pd
import os

def verify_metrics():
    file_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\FBA_ANALYSIS\financial_reports\angelwholesale-co-uk\fba_financial_report_20251201_205049.csv"
    
    try:
        df = pd.read_csv(file_path, dtype=str, nrows=5)
        print("COLUMNS_START")
        print(list(df.columns))
        print("COLUMNS_END")
        print("FIRST_ROW_START")
        print(df.iloc[0].to_dict())
        print("FIRST_ROW_END")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_metrics()
