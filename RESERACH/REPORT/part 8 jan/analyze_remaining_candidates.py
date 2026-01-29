import pandas as pd
import json

# 1. Load the processed status from our consolidated JSON
with open('consolidated_verification_data.json', 'r') as f:
    processed_data = json.load(f)

processed_asins = set()
for item in processed_data.get('verified', []):
    processed_asins.add(str(item.get('asin', '')).strip())
for item in processed_data.get('likely', []):
    processed_asins.add(str(item.get('asin', '')).strip())
for item in processed_data.get('different', []):
    processed_asins.add(str(item.get('asin', '')).strip())

try:
    df = pd.read_excel('part 8 jan.xlsx')
except Exception as e:
    print(f"Error reading Excel: {e}")
    exit(1)

candidates = []
# Expanded brand list
known_brands = ['AMTECH', 'KILROCK', 'MASON CASH', 'YALE', 'LAV', 'BAKER & SALT', 'BLUE CANYON', 'CHEF AID', 'PYREX', 'SOUDAL', 'ROLSON', 'ELBOW GREASE', 'COMMAND', 'GORILLA', 'WD40', 'WD-40', 'HG', 'ASTONISH', 'DR BECKMANN', 'STARDROPS', 'TALA', 'ELLIOTT', 'AROCOROC', 'STATUS', '151', 'PAN AROMA', 'GIFTMAKER', 'FIRST STEPS', 'TOYRIFIC', 'BETRON', 'DURACELL', 'ENERGIZER', 'BIC', 'SHARPIE', 'PILOT', 'UNI-BALL', 'STABILO', 'PAPER MATE', 'PARKER', 'SHEAFFER', 'CROSS', 'LAMY', 'ZEBRA', 'PENTEL', 'FABER-CASTELL', 'STAEDTLER', 'MAPED', 'HELIX', 'OXFORD', 'PUKKA', 'BLACK N RED', 'MOLESKINE', 'LEUCHTTURM1917', 'FILOFAX', 'COLLINS', 'RINES', 'WHAM', 'STRATA', 'ADDIS', 'CURVER', 'RUBBERMAID', 'SISTEMA', 'LOCK & LOCK', 'BODUM', 'BRABANTIA', 'SIMPLEHUMAN', 'JOSEPH JOSEPH', 'OXO', 'TEFAL', 'PYREX', 'KILNER', 'MASON CASH', 'LE CREUSET', 'DENBY', 'PORTMEIRION', 'ROYAL WOiRCESTER', 'SPODE', 'WAX LYRICAL', 'YANKEE CANDLE', 'WOODWICK', 'JO MALONE', 'MOLTON BROWN', 'THE BODY SHOP', 'LUSH', 'BOMB COSMETICS', 'BAYLIS & HARDING', 'CAREX', 'IMPERIAL LEATHER', 'RADOR', 'SOURCE', 'ORIGINAL', 'MULTIPACK']

for idx, row in df.iterrows():
    asin = str(row.get('ASIN', '')).strip()
    
    if asin in processed_asins:
        continue
    if len(asin) < 8 or asin.lower() == 'nan':
        continue
        
    supplier_title = str(row.get('SupplierTitle', '')).upper()
    amazon_title = str(row.get('AmazonTitle', '')).upper()
    
    try:
        net_profit = float(row.get('NetProfit', 0))
    except:
        net_profit = 0
        
    # STRICTER LOGIC:
    # 1. Must be a Brand Match
    # 2. OR Must have significant title overlap (word overlap)
    
    brand_match = False
    matched_brand = ""
    for brand in known_brands:
        if brand in supplier_title and brand in amazon_title:
            brand_match = True
            matched_brand = brand
            break
            
    # Word Overlap Check
    s_words = set(w for w in supplier_title.split() if len(w) > 3)
    a_words = set(w for w in amazon_title.split() if len(w) > 3)
    overlap = s_words.intersection(a_words)
    overlap_score = len(overlap)
    
    # Garbage filter: If profit is huge (>50) and overlap is low, it's likely a mismatch
    if net_profit > 50 and overlap_score < 2:
        continue

    score = 0
    reason = []
    
    if brand_match:
        score += 100
        reason.append(f"Brand: {matched_brand}")
    
    if overlap_score >= 3:
        score += 50
        reason.append(f"Overlap: {overlap_score} words")
        
    # Only keep if we have SOME confidence
    if score >= 50 and net_profit > 0.50:
        candidates.append({
            'row': idx + 2,
            'asin': asin,
            'supplier_title': supplier_title,
            'amazon_title': amazon_title,
            'net_profit': net_profit,
            'reason': ", ".join(reason),
            'score': score
        })

candidates.sort(key=lambda x: x['score'], reverse=True)

print(f"Found {len(candidates)} high potential candidates (strict filter).")

with open('candidates_list.json', 'w', encoding='utf-8') as f:
    json.dump(candidates[:200], f, indent=2)

# Generate Markdown Report (Internal Use)
with open('HIGH_POTENTIAL_CANDIDATES.md', 'w', encoding='utf-8') as f:
    f.write("# HIGH POTENTIAL VERIFICATION CANDIDATES (STRICT)\n\n")
    f.write(f"identified {len(candidates)} candidates.\n\n")
    for c in candidates[:20]:
         f.write(f"| {c['score']} | {c['supplier_title'][:30]} | {c['amazon_title'][:30]} | £{c['net_profit']} |\n")
