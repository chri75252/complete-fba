import csv
import json
import re
from pathlib import Path

def normalize_ean(raw: str) -> str:
    if not raw: return ""
    s = str(raw).strip()
    if s.endswith(".0"): s = s[:-2]
    if 'e' in s.lower():
        try: s = str(int(float(s)))
        except: pass
    s = re.sub(r"[^0-9]", "", s)
    if len(s) not in (8, 12, 13, 14): return ""
    return s

def gtin_checksum_valid(ean: str) -> bool:
    if not ean or len(ean) not in (8, 12, 13, 14): return False
    try:
        digits = [int(d) for d in ean]
        check = digits[-1]
        payload = digits[:-1]
        total = sum(d * (3 if i % 2 == 0 else 1) for i, d in enumerate(reversed(payload)))
        expected = (10 - (total % 10)) % 10
        return expected == check
    except Exception:
        return False

def extract_attributes(title: str):
    if not title:
        return set()
    cleaned = title.lower()
    cleaned = re.sub(r'\btwo\b', '2', cleaned)
    cleaned = re.sub(r'\bthree\b', '3', cleaned)
    cleaned = re.sub(r'\bfour\b', '4', cleaned)
    cleaned = re.sub(r'\bfive\b', '5', cleaned)
    cleaned = re.sub(r'\bsix\b', '6', cleaned)
    replacements = {
        r'litre|litres|ltr': 'l',
        r'metre|metres|mtr': 'm',
        r'centimetre|centimetres': 'cm',
        r'millilitre|millilitres': 'ml',
        r'kilogram|kilograms': 'kg',
        r'gram|grams': 'g',
        r'pieces|piece|pcs|pc': 'pack',
        r'pk': 'pack'
    }
    for pat, rep in replacements.items():
        cleaned = re.sub(r'\b' + pat + r'\b', rep, cleaned)
    attributes = set()
    matches = re.finditer(r'(\d+(?:\.\d+)?)\s*(ml|l|g|kg|cm|mm|m|inch|\"|pack|gang)', cleaned)
    for m in matches:
        qty = float(m.group(1))
        unit = m.group(2).replace('"', 'inch')
        if qty.is_integer():
            attributes.add(f"{int(qty)}{unit}")
        else:
            attributes.add(f"{qty}{unit}")
    pack_matches = re.finditer(r'(?:pack of|set of)\s*(\d+)', cleaned)
    for m in pack_matches:
        attributes.add(f"{m.group(1)}pack")
    return attributes

def _get_tokens(text: str):
    if not text: return set()
    text = text.lower()
    text = text.replace("-", " ").replace("/", " ").replace("&", "and")
    tokens = set(re.findall(r'[a-z0-9]+', text))
    stop_words = {"the", "a", "an", "and", "or", "for", "of", "in", "to", "with", "is", "by", "on", "at", "from", "cm", "mm", "ml", "kg", "pack", "set", "new"}
    return tokens - stop_words

def classify_row_new(row: dict) -> dict:
    supplier_ean = normalize_ean(row.get("EAN", ""))
    amazon_ean = normalize_ean(row.get("EAN_OnPage", ""))
    supplier_title = row.get("SupplierTitle", "")
    amazon_title = row.get("AmazonTitle", "")
    
    reasons = []
    flags = []
    
    ean_exact = False
    ean_score = 0
    if supplier_ean and amazon_ean:
        if supplier_ean == amazon_ean:
            ean_exact = True
            ean_score = 50
            reasons.append("Exact EAN match")
            if not gtin_checksum_valid(supplier_ean):
                flags.append("EAN_CHECKSUM_FAIL")
        else:
            ean_score = -15
            reasons.append(f"EAN mismatch")
            flags.append("EAN_MISMATCH")
    elif supplier_ean and not amazon_ean:
        ean_score = 0
        reasons.append("Amazon EAN missing")
        flags.append("AMAZON_EAN_MISSING")
    else:
        ean_score = 0
        flags.append("NO_SUPPLIER_EAN")

    tokens_s = _get_tokens(supplier_title)
    tokens_a = _get_tokens(amazon_title)
    shared = tokens_s & tokens_a
    containment = len(shared) / len(tokens_s) if tokens_s else 0.0
    dice = (2.0 * len(shared)) / (len(tokens_s) + len(tokens_a)) if (tokens_s or tokens_a) else 0.0
    text_score = (containment * 0.70 + dice * 0.30) * 100
    
    if containment >= 0.8:
        reasons.append(f"High subset match ({containment:.0%} containment)")
    elif containment >= 0.5:
        reasons.append(f"Moderate subset match ({containment:.0%} containment)")
    else:
        reasons.append(f"Weak match ({containment:.0%} containment)")
        flags.append("TITLE_MISMATCH")
        if not ean_exact:
            text_score -= 20

    attr_s = extract_attributes(supplier_title)
    attr_a = extract_attributes(amazon_title)
    attr_score = 0
    if attr_s and attr_a:
        units_s = set(re.sub(r'[\d.]+', '', x) for x in attr_s)
        units_a = set(re.sub(r'[\d.]+', '', x) for x in attr_a)
        shared_units = units_s & units_a
        has_conflict = False
        has_match = False
        for u in shared_units:
            vals_s = {x for x in attr_s if x.endswith(u)}
            vals_a = {x for x in attr_a if x.endswith(u)}
            if vals_s & vals_a:
                has_match = True
            elif vals_s and vals_a:
                has_conflict = True
                
        if has_conflict:
            attr_score = -20
            flags.append("VARIANT_MISMATCH")
            reasons.append(f"Size/pack conflict: {attr_s} vs {attr_a}")
        elif has_match:
            attr_score = 10
            reasons.append(f"Size/pack agreement: {attr_s & attr_a}")

    brand_s = (supplier_title.split()[0].lower() if supplier_title else "").replace(r"[^a-z0-9]", "")
    brand_a = (amazon_title.split()[0].lower() if amazon_title else "").replace(r"[^a-z0-9]", "")
    brand_score = 0
    if brand_s and brand_a and brand_s == brand_a and len(brand_s) > 2:
        brand_score = 10
        reasons.append(f"Brand match: {brand_s}")

    confidence = ean_score + text_score + attr_score + brand_score
    confidence = max(0, min(100, confidence))

    if ean_exact and text_score > 30 and "VARIANT_MISMATCH" not in flags:
        tier = "TIER_1_VERIFIED"
    elif confidence >= 60 and "VARIANT_MISMATCH" not in flags:
        tier = "TIER_2_LIKELY"
    elif confidence >= 30:
        tier = "TIER_3_NEEDS_REVIEW"
    else:
        tier = "TIER_4_REJECTED"

    return {
        "tier": tier,
        "confidence_score": round(confidence, 1),
        "reasons": reasons,
        "flags": flags,
        "token_containment": round(containment, 3),
    }

if __name__ == "__main__":
    csv_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\FINAL STALE\15-04-2026\poundwholesale main list\fba_analysis_2026-04-15 (1).csv"
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
        
    print(f"Total rows: {len(rows)}")
    tiers = {"TIER_1_VERIFIED": 0, "TIER_2_LIKELY": 0, "TIER_3_NEEDS_REVIEW": 0, "TIER_4_REJECTED": 0}
    for row in rows:
        res = classify_row_new(row)
        tiers[res["tier"]] += 1
        t_sup = row.get("SupplierTitle", "")
        # Print selected rows to see output
        if "CROSBY" in t_sup or "151 Masonry" in t_sup or "Pan Aroma Assorted" in t_sup or "Roots & Shoots" in t_sup or "FIT EMULSION" in t_sup or "SUPER DREAMER" in t_sup or "SISTEMA" in t_sup or "EVEREADY BATTERIES" in t_sup:
            print(f"\n--- {t_sup} ---")
            print(f"Amazon: {row.get('AmazonTitle')}")
            print(f"Tier: {res['tier']} (Score: {res['confidence_score']})")
            print(f"Reasons: {res['reasons']}")
            print(f"Flags: {res['flags']}")
            
    print(f"\nNew Tiers: {tiers}")
