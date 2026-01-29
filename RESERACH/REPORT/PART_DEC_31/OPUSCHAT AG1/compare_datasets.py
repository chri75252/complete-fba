"""
DIRECT COMPARISON: Find every VERIFIED product from ground truth
and check if it exists in NEW dataset with matching EAN
"""
import pandas as pd
import re

# Ground truth EANs from the REAL FINAL report (33 VERIFIED RECOMMENDED)
ground_truth_verified = [
    {"ean": "5059001500861", "title": "AIRWICK REED DIFFUSER MULLED WINE 33ML PK5"},
    {"ean": "5050028016069", "title": "EVERREADY T8 4FT 36W TUBE LIGHT"},
    {"ean": "5010853235530", "title": "MASON CASH MIXING BOWL CREAM 29CM"},
    {"ean": "5053249248356", "title": "PAN AROMA JAR CANDLE 85GM SALTED CARAMEL"},
    {"ean": "5032759031078", "title": "AMTECH LED MINI TORCH"},
    {"ean": "5060357990107", "title": "SUPERIOR FOIL 10 CONTAINERS & LID 9X9IN"},
    {"ean": "5053249248295", "title": "PAN AROMA JAR CANDLE 85GM RED BERRY"},
    {"ean": "5053249228174", "title": "PAN AROMA C TEA-LIGHTS 16PK APP&CIN"},
    {"ean": "5010792542676", "title": "CHRISTMAS LAPTRAY ROBINS"},
    {"ean": "5010792542737", "title": "GEL LED CANDLE FESTIVE ROBIN"},
    {"ean": "5010792749549", "title": "HIGHLAND COW PLAQUE FRIENDS"},
    {"ean": "5039295201040", "title": "HOUSE MATE STAINLESS STEEL CLEANER & POLISH"},
    {"ean": "26102251102", "title": "CARAFE .5LT GLASS"},
    {"ean": "5025364001970", "title": "TIDYZ DOGGY BAGS STRONG 50 PCS"},
    {"ean": "5019200117338", "title": "PRODEC CAULKER 12 INCH"},
    {"ean": "5026180033572", "title": "APOLLO VINEGAR SHAKER"},
    {"ean": "5060187173633", "title": "MIRROR BLUE CANYON SQUARE PLASTIC MIRROR"},
    {"ean": "5030481940088", "title": "PPS ROUND 40 DOYLEYS 21CM"},
    {"ean": "5013159300353", "title": "ELLIOTT WINDOW SQUEEGEE 20CM"},
    {"ean": "5036200121479", "title": "THE BIG CHEESE QUICK CLICK MOUSE TRAP 2PK"},
    {"ean": "5012904061204", "title": "TALA COCKTAIL STICKS 200"},
    {"ean": "5013159004428", "title": "ELLIOTTS GLASS SPRAY BOTTLE BROWN 480ML"},
    {"ean": "5060187175750", "title": "BLUE CANYON VECTOR SHOWER SPRAY"},
    {"ean": "5010853203508", "title": "MASON CASH CERAMIC RECT DISH 16cm"},
    {"ean": "5012904004188", "title": "CHEF AID STRAINER DIAMETER 18CM"},
    {"ean": "5055361761119", "title": "MEMORIAL WATERPROOF GRAVESIDE LANTERN"},
    {"ean": "5012904148738", "title": "CHEF AID SHOT GLASSES ASSORTED 20PCE"},
    {"ean": "5022704000013", "title": "FIRE UP NATURAL FIRELIGHTERS 28 PACK"},
    {"ean": "8711252100531", "title": "GLASS WHISKEY DECANTER"},
]

# Ground truth FILTERED OUT (12 products)
ground_truth_filtered = [
    {"ean": "5014749165598", "title": "BEAUTY VELCRO HAIR GRIP ROLLERS 7 PACK"},
    {"ean": "5060357991357", "title": "PHOODS FOIL TRAY ROASTER"},
    {"ean": "5015302202996", "title": "SAMS SCRUMMY GIANT LEG DOG BONE"},
    {"ean": "5038135108600", "title": "WHAM CRYSTAL 32LTR CLEAR UNDERBED BOX&LID"},
    # Note: Some entries don't have EAN in the report
]

# Load NEW dataset
df_new = pd.read_excel(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART_DEC_31\PART_DEC_31.xlsx')

# Load OLD dataset
df_old = pd.read_excel(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_30_dec\part_30_dec.xlsx')

# Clean EANs
def clean_ean(x):
    if pd.isna(x):
        return ''
    s = str(x).strip().replace('.0', '')
    return re.sub(r'\D', '', s)

df_new['EAN_clean'] = df_new['EAN'].apply(clean_ean)
df_new['EAN_OnPage_clean'] = df_new['EAN_OnPage'].apply(clean_ean)
df_old['EAN_clean'] = df_old['EAN'].apply(clean_ean)
df_old['EAN_OnPage_clean'] = df_old['EAN_OnPage'].apply(clean_ean)

print("="*80)
print("CHECKING EVERY GROUND TRUTH EAN AGAINST NEW DATASET")
print("="*80)
print()

found_in_new = 0
missing_from_new = 0
ean_doesnt_match_in_new = 0

for item in ground_truth_verified:
    ean = item['ean']
    title = item['title']
    
    # Check if EAN exists in NEW dataset
    rows_with_ean = df_new[df_new['EAN_clean'] == ean]
    
    if len(rows_with_ean) == 0:
        print(f"[X] MISSING FROM NEW DATASET: {ean} | {title}")
        missing_from_new += 1
    else:
        row = rows_with_ean.iloc[0]
        amz_ean = row['EAN_OnPage_clean']
        if ean == amz_ean:
            print(f"[OK] FOUND (EAN MATCH): {ean} | {title[:40]}")
            found_in_new += 1
        else:
            print(f"[!] FOUND BUT NO EAN MATCH: {ean} vs {amz_ean} | {title[:40]}")
            ean_doesnt_match_in_new += 1

print()
print("="*80)
print("SUMMARY")
print("="*80)
print(f"Ground truth VERIFIED count: {len(ground_truth_verified)}")
print(f"Found in NEW with matching EAN: {found_in_new}")
print(f"Missing from NEW dataset: {missing_from_new}")
print(f"Found but EAN doesn't match: {ean_doesnt_match_in_new}")

# Also count total EAN matches in each dataset
old_matches = (df_old['EAN_clean'] == df_old['EAN_OnPage_clean']) & (df_old['EAN_clean'] != '') & (df_old['EAN_clean'] != 'nan')
new_matches = (df_new['EAN_clean'] == df_new['EAN_OnPage_clean']) & (df_new['EAN_clean'] != '') & (df_new['EAN_clean'] != 'nan')

print()
print(f"OLD dataset total EAN matches: {old_matches.sum()}")
print(f"NEW dataset total EAN matches: {new_matches.sum()}")
