#!/usr/bin/env python3
"""
combine_csvs.py

Reads all CSV files in a given directory and writes a single combined CSV,
leaving the original files intact.
"""

import os
import pandas as pd

def combine_csv_files(input_dir: str, output_filename: str = "combined_reports.csv") -> None:
    """
    Combine all CSV files in `input_dir` into a single CSV named `output_filename`.

    :param input_dir: Path to the directory containing CSV files.
    :param output_filename: Name of the output CSV file (will be created in input_dir).
    """
    # Absolute path to the output file
    output_path = os.path.join(input_dir, output_filename)

    # List all .csv files, excluding the output file if it already exists
    csv_files = [
        fname for fname in os.listdir(input_dir)
        if fname.lower().endswith(".csv") and fname != output_filename
    ]
    if not csv_files:
        print("No CSV files found to combine.")
        return

    # Read each CSV into a DataFrame
    dataframes = []
    for fname in csv_files:
        file_path = os.path.join(input_dir, fname)
        try:
            df = pd.read_csv(file_path)
            dataframes.append(df)
            print(f"Loaded {fname} ({len(df)} rows).")
        except Exception as e:
            print(f"❌ Skipping {fname}: {e}")

    # Concatenate all DataFrames
    combined_df = pd.concat(dataframes, ignore_index=True)
    print(f"Concatenated {len(dataframes)} files into {len(combined_df)} total rows.")

    # Write out the combined CSV
    combined_df.to_csv(output_path, index=False)
    print(f"✅ Combined CSV written to: {output_path}")

if __name__ == "__main__":
    # Update this path if needed
    INPUT_DIRECTORY = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (3)\OUTPUTS\FBA_ANALYSIS\financial_reports\poundwholesale-co-uk"
    combine_csv_files(INPUT_DIRECTORY)
