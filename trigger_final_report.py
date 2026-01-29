
from tools.FBA_Financial_calculator_linking_map_processor_FINAL_RUN import run_calculations_from_linking_map

if __name__ == "__main__":
    print("Starting Financial Calculation Run using linking_map_COMPLETE_FINAL.json...")
    try:
        run_calculations_from_linking_map("efghousewares.co.uk")
        print("Run Completed Successfully.")
    except Exception as e:
        print(f"Run Failed: {e}")
