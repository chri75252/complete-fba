import json
import pathlib
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Check sandbox manifest readiness")
    parser.add_argument("--domain", required=True, help="Supplier domain (e.g., angelwholesale.co.uk)")
    parser.add_argument("--suffix", required=True, help="Sandbox suffix (e.g., sandbox)")
    args = parser.parse_args()

    sandbox_supplier = f"{args.domain}__{args.suffix}"
    config_path = pathlib.Path("config") / f"{sandbox_supplier.replace('.co.uk', '')}_categories.json"
    
    print(f"Expected path: {config_path}")
    
    if not config_path.exists():
        print(f"FAIL: {config_path} does not exist.")
        sys.exit(1)
        
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
        urls = data.get("category_urls", [])
        print(f"SUCCESS: {config_path} exists with {len(urls)} category_urls.")
        if not urls:
            print("FAIL: category_urls is empty.")
            sys.exit(1)
    except Exception as e:
        print(f"FAIL: Cannot read/parse json: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
