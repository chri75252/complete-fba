
import pandas as pd
import re

INPUT_FILE = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\part 8 jan.xlsx"

def clean(x):
    return re.sub(r'\D', '', str(x))

print("Loading data...")
df = pd.read_excel(INPUT_FILE)

print(f"Total Rows: {len(df)}")

# 1. Exact String Match
exact = df[df['EAN'].astype(str).str.strip() == df['EAN_OnPage'].astype(str).str.strip()]
print(f"Exact String Matches: {len(exact)}")

# 2. Cleaned Digit Match
df['EAN_clean'] = df['EAN'].apply(clean)
df['OnPage_clean'] = df['EAN_OnPage'].apply(clean)

digit_match = df[df['EAN_clean'] == df['OnPage_clean']]
print(f"Digit Matches (ignoring validity): {len(digit_match)}")

# 3. Trailing Zero Issue (Supplier matches Amazon excluding last digit)
# Amazon = Supplier + '0'
df['OnPage_Strip0'] = df['OnPage_clean'].apply(lambda x: x[:-1] if x.endswith('0') else x)
trailing_zero = df[(df['EAN_clean'] == df['OnPage_Strip0']) & (df['EAN_clean'] != '')]
print(f"Trailing Zero Matches (Sup == Amz[:-1]): {len(trailing_zero)}")

# 4. Checksum Failures on Matches
# Let's inspect the "Digit Matches" to see why they failed 'is_strict_valid_barcode'
def gtin_checksum_ok(digits):
    if len(digits) not in (8, 12, 13, 14): return False
    body = digits[:-1]
    check = int(digits[-1])
    body_rev = list(map(int, body[::-1]))
    total = sum(d * (3 if i % 2 == 1 else 1) for i, d in enumerate(body_rev, start=1))
    calc = (10 - (total % 10)) % 10
    return calc == check

print("\n--- Diagnostic on Digit Matches ---")
count_valid = 0
for idx, row in digit_match.iterrows():
    ean = row['EAN_clean']
    valid = gtin_checksum_ok(ean)
    if valid:
        count_valid += 1
    else:
        if count_valid < 5: # Print first few failures
            print(f"Match but Invalid Checksum: {ean}")

print(f"Valid Checksum Matches: {count_valid}")

print("\n--- Diagnostic on Trailing Zero Matches ---")
print(f"Sample Trailing Zero Matches (Sup vs Amz):")
print(trailing_zero[['EAN', 'EAN_OnPage']].head(5))
