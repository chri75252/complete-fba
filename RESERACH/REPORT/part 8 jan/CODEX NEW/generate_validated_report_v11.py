from __future__ import annotations

import math
import re
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-")
XLSX_PATH = REPO_ROOT / r"RESERACH\REPORT\part 8 jan\part 8 jan.xlsx"
PREV_REPORT = REPO_ROOT / r"RESERACH\REPORT\part 8 jan\CODEX NEW\PHASEA_MANUAL_REPORT_2601090031.md"
OUT_DIR = REPO_ROOT / r"RESERACH\REPORT\part 8 jan\CODEX NEW"

DUBAI = timezone(timedelta(hours=4))
now_dubai = datetime.now(DUBAI)
report_date = now_dubai.strftime('%Y-%m-%d')
file_stamp = now_dubai.strftime('%y%m%d%H%M')
out_path = OUT_DIR / f"PHASEA_MANUAL_REPORT_VALIDATED_{file_stamp}.md"

SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": ["pk", "cases", "bag", "capsule"],
    "allow_trailing_number_as_qty": False,
    "leading_multiplier_check": False,
    "dimension_shield_keywords": ["cm", "mm", "ml", "l", "ltr", "kg", "g", "oz", "inch", "in"],
    "brand_position": "start",
    "brand_in_supplier_usually_present": True,
    "brand_in_amazon_usually_present": True,
    "brand_format_patterns": ["ALL_CAPS_AT_START"],
    "brand_sparse_supplier_mode": False,
    "strong_similarity_threshold": 0.33,
    "strong_shared_tokens_threshold": 3,
    "very_strong_similarity_threshold": 0.45,
    "very_strong_shared_tokens_threshold": 4,
    "gate_mode": "A_strict",
    "sales_column": "bought_in_past_month",
    "capacity_pattern_as_rsu": True,
    "spec_x_shield_keywords": ["magnification", "zoom", "microscope", "scope", "times"],
    "table_pipe_sanitization": True,
}

SPEC_X_SHIELD = set(SUPPLIER_NAMING_CONVENTION["spec_x_shield_keywords"])

IP_PHRASES = [
    (re.compile(r"\bjo\s+malone\b", re.I), 'Jo Malone'),
    (re.compile(r"\bchanel\b", re.I), 'Chanel'),
    (re.compile(r"\bdior\b", re.I), 'Dior'),
    (re.compile(r"\bgucci\b", re.I), 'Gucci'),
    (re.compile(r"\bprada\b", re.I), 'Prada'),
    (re.compile(r"\bherm[eè]s\b", re.I), 'Hermès'),
    (re.compile(r"\blouis\s+vuitton\b", re.I), 'Louis Vuitton'),
    (re.compile(r"\bmicrosoft\b", re.I), 'Microsoft'),
    (re.compile(r"\bsamsung\b", re.I), 'Samsung'),
    (re.compile(r"\bsony\b", re.I), 'Sony'),
    (re.compile(r"\bnike\b", re.I), 'Nike'),
    (re.compile(r"\badidas\b", re.I), 'Adidas'),
]
APPLE_CONTEXT = re.compile(r"\b(iphone|ipad|macbook|imac|mac\b|ios\b|airpods|watch\b)\b", re.I)
APPLE_WORD = re.compile(r"\bapple\b", re.I)


def ip_risk_brand(title_a: str, title_s: str) -> str | None:
    text = f"{title_s} {title_a}"
    if APPLE_WORD.search(text) and APPLE_CONTEXT.search(text):
        return 'Apple'
    for rx, name in IP_PHRASES:
        if rx.search(text):
            return name
    return None


def sanitize_cell(val) -> str:
    s = '' if val is None else str(val)
    s = s.replace('\r', ' ').replace('\n', ' ')
    if SUPPLIER_NAMING_CONVENTION.get('table_pipe_sanitization'):
        s = s.replace('|', '/')
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def tokens(val) -> list[str]:
    s = sanitize_cell(val).lower()
    s = re.sub(r'[^a-z0-9]+', ' ', s)
    return [t for t in s.split() if t]

STOP = {
    'the','and','or','with','for','to','of','a','an','in','on','by','from','new','all','set','pack','pk',
    'assorted','assort','each','single','pcs','pc','pce','piece','pieces','units','unit'
}


def extract_brand_supplier(title: str) -> str | None:
    toks = [t for t in tokens(title) if t not in STOP]
    if not toks:
        return None
    for t in toks[:4]:
        if re.search(r'[a-z]', t) and len(t) >= 3 and t not in {'white','black','blue','red','green','pink','gold','silver','assorted'}:
            return t
    return None


def shared_token_count(supplier: str, amazon: str) -> int:
    st = set([t for t in tokens(supplier) if t not in STOP])
    at = set([t for t in tokens(amazon) if t not in STOP])
    return len(st & at)


def jaccard(supplier: str, amazon: str) -> float:
    st = set([t for t in tokens(supplier) if t not in STOP])
    at = set([t for t in tokens(amazon) if t not in STOP])
    if not st or not at:
        return 0.0
    return len(st & at) / len(st | at)


def clean_to_digits(val) -> str:
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return ''
    if isinstance(val, (np.integer, int)):
        return str(int(val))
    if isinstance(val, (np.floating, float)):
        if float(val).is_integer():
            return str(int(val))
        return ''
    s = str(val).strip()
    if not s or s.lower() in {'nan','none','null','-'}:
        return ''
    if re.search(r'[eE][+-]?\d+', s):
        return ''
    s = s.replace('.0', '')
    return re.sub(r'\D', '', s)


def gtin_checksum_ok(digits: str) -> bool:
    if not digits.isdigit() or len(digits) not in (8, 12, 13, 14):
        return False
    body = digits[:-1]
    check = int(digits[-1])
    total = 0
    for i, d in enumerate(map(int, body[::-1]), start=1):
        total += d * (3 if i % 2 == 1 else 1)
    calc = (10 - (total % 10)) % 10
    return calc == check


def normalize_gtin(digits: str) -> str:
    if not isinstance(digits, str) or not digits.isdigit():
        return ''
    if len(digits) in (8, 12, 13, 14) and gtin_checksum_ok(digits):
        return digits
    for target_len in (12, 13, 14):
        if len(digits) < target_len:
            padded = digits.zfill(target_len)
            if gtin_checksum_ok(padded):
                return padded
    return digits


def is_strict_valid_barcode(digits: str) -> bool:
    if not isinstance(digits, str) or not digits.isdigit():
        return False
    normalized = normalize_gtin(digits)
    if len(normalized) not in (8, 12, 13, 14):
        return False
    if re.search(r'0{6,}$', normalized):
        return False
    return gtin_checksum_ok(normalized)


def money_gbp(x) -> str:
    try:
        if x is None or (isinstance(x, float) and math.isnan(x)):
            return '-'
        return f"£{float(x):.2f}"
    except Exception:
        return '-'


def pct(x) -> str:
    try:
        if x is None or (isinstance(x, float) and math.isnan(x)):
            return '-'
        return f"{float(x):.1f}%"
    except Exception:
        return '-'

# Pack parsing
re_pk = re.compile(r"\bpk\s*(\d{1,4})\b", re.I)
re_packof = re.compile(r"\b(pack of|set of)\s*(\d{1,4})\b", re.I)
re_npack = re.compile(r"\b(\d{1,4})\s*[- ]?pack\b", re.I)

COUNT_NOUNS = (
    'pcs','pc','pce','piece','pieces','pairs','case','cases','bag','bags','capsule','capsules',
    'roll','rolls','liner','liners','container','containers','tray','trays','tube','tubes','bulb','bulbs',
    'sheet','sheets','wipe','wipes','plate','plates','stick','sticks','doyley','doyleys','glass','glasses',
    'refill','refills','can','cans','bottle','bottles'
)
re_qty_word = re.compile(r"\b(\d{1,5})\s*(%s)\b" % '|'.join(map(re.escape, COUNT_NOUNS)), re.I)

re_amz_nx_capacity = re.compile(r"\b(\d{1,3})\s*[xX*]\s*(\d+(?:\.\d+)?)\s*(ml|l|ltr|g|kg)\b", re.I)
re_amz_nx_qty = re.compile(r"\b(\d{1,3})\s*[xX*]\s*(\d{1,5})\b")

re_capacity = re.compile(r"\b(\d+(?:\.\d+)?)\s*(ml|l|ltr|g|kg)\b", re.I)


def supplier_sold_each(title: str) -> bool:
    t = sanitize_cell(title).lower()
    return ('sold each' in t) or re.search(r"\beach\b", t) is not None


def supplier_units_per_pack(title: str) -> int:
    t = sanitize_cell(title).lower()
    if supplier_sold_each(t):
        return 1
    m = re_pk.search(t)
    if m:
        n = int(m.group(1))
        return n if 1 < n < 500 else 1
    m = re_packof.search(t)
    if m:
        n = int(m.group(2))
        return n if 1 < n < 500 else 1
    m = re_npack.search(t)
    if m:
        n = int(m.group(1))
        return n if 1 < n < 500 else 1
    m = re_qty_word.search(t)
    if m:
        n = int(m.group(1))
        return n if 1 < n < 5000 else 1
    return 1


def amazon_units_required(title: str):
    raw = sanitize_cell(title)
    t = raw.lower()
    if 'x' in t and any(k in t for k in SPEC_X_SHIELD):
        return (1, 'spec_x_shield', False)
    m = re_amz_nx_capacity.search(t)
    if m:
        n = int(m.group(1))
        return (n, m.group(0), True)
    m = re_packof.search(t)
    if m:
        n = int(m.group(2))
        return (n, m.group(0), True)
    m = re_npack.search(t)
    if m:
        n = int(m.group(1))
        return (n, m.group(0), True)
    for m in re_amz_nx_qty.finditer(t):
        outer = int(m.group(1)); inner = int(m.group(2))
        frag = m.group(0)
        window = t[max(0, m.start()-16): min(len(t), m.end()+16)]
        if re.search(r"\b(cm|mm|ml|l|ltr|kg|g|oz|inch|in)\b", window):
            continue
        if 1 < outer <= 50 and 1 < inner <= 5000:
            return (outer * inner, frag, True)
    m = re.search(r"\b(\d{2,5})\s*[xX]\b", t)
    if m:
        n = int(m.group(1))
        if 1 < n <= 5000:
            return (n, m.group(0), True)
    return (1, '-', False)


def adjusted_profit(net_profit, supplier_cost, rsu: int) -> float:
    return float(net_profit) - float(supplier_cost) * max(0, rsu - 1)


def parse_capacity(title: str):
    t = sanitize_cell(title).lower()
    m = re_capacity.search(t)
    if not m:
        return None
    val = float(m.group(1))
    unit = m.group(2).lower()
    if unit in {'l', 'ltr'}:
        return ('ml', val * 1000.0)
    if unit == 'ml':
        return ('ml', val)
    if unit == 'kg':
        return ('g', val * 1000.0)
    if unit == 'g':
        return ('g', val)
    return None


def capacity_bucket(s_title: str, a_title: str):
    s = parse_capacity(s_title)
    a = parse_capacity(a_title)
    if not s or not a or s[0] != a[0]:
        return None
    s_val, a_val = s[1], a[1]
    if s_val <= 0 or a_val <= 0:
        return None
    diff = abs(s_val - a_val) / min(s_val, a_val)
    if diff <= 0.10:
        return ('OK_0_10', diff)
    if diff <= 0.25:
        return ('VERIFY_10_25', diff)
    if diff <= 0.50:
        return ('AUDIT_25_50', diff)
    return ('AUDIT_GT_50', diff)


def parse_prev(report_path: Path):
    text = report_path.read_text(encoding='utf-8')
    section = None
    in_table = False
    headers = None
    col_index = {}
    rowids = defaultdict(set)
    rowid_re = re.compile(r"\bRowID\s+(\d+)\b")

    for line in text.splitlines():
        if line.startswith('## '):
            section = line[3:].strip()
            continue
        if line.strip() == '```text':
            in_table = True
            headers = None
            col_index = {}
            continue
        if line.strip() == '```':
            in_table = False
            headers = None
            col_index = {}
            continue
        if not in_table or not line.startswith('|'):
            continue
        parts = [p.strip() for p in line.strip().strip('|').split('|')]
        if headers is None:
            headers = parts
            col_index = {h: i for i, h in enumerate(headers)}
            continue
        if all(set(p) <= {'-'} for p in parts):
            continue
        if not headers or 'Key Match Evidence' not in col_index:
            continue
        ev = parts[col_index['Key Match Evidence']] if col_index['Key Match Evidence'] < len(parts) else ''
        m = rowid_re.search(ev)
        if m:
            rowids[section].add(int(m.group(1)))
    return rowids


def render_table(rows, headers):
    widths = [len(h) for h in headers]
    for r in rows:
        for i, v in enumerate(r):
            widths[i] = max(widths[i], len(str(v)))

    def fmt_row(vals):
        return '| ' + ' | '.join(str(v).ljust(w) for v, w in zip(vals, widths)) + ' |'

    sep = '|-' + '-|-'.join('-' * w for w in widths) + '-|'
    lines = [fmt_row(headers), sep]
    for r in rows:
        lines.append(fmt_row(r))
    return '\n'.join(lines)


def main():
    prev_rowids = parse_prev(PREV_REPORT)

    df = pd.read_excel(XLSX_PATH, sheet_name=0, engine='openpyxl')
    if 'ROI ( % ) ' in df.columns:
        df = df.rename(columns={'ROI ( % ) ': 'ROI_pct'})
    df = df.copy()
    df['RowID'] = np.arange(1, len(df)+1)

    sales_col = SUPPLIER_NAMING_CONVENTION.get('sales_column')
    df['Sales'] = pd.to_numeric(df[sales_col], errors='coerce').fillna(0).astype(int) if sales_col in df.columns else 0

    for c in ['SupplierPrice_incVAT','SellingPrice_incVAT','NetProfit','ROI_pct']:
        df[c] = pd.to_numeric(df[c], errors='coerce')

    supplier_domains = df['SupplierURL'].fillna('').astype(str).str.extract(r"https?://([^/]+)/")[0].fillna('')
    supplier_domain = supplier_domains.value_counts().index[0] if len(supplier_domains.value_counts()) else 'UNKNOWN'

    sup_digits = df['EAN'].apply(clean_to_digits)
    amz_digits = df['EAN_OnPage'].apply(clean_to_digits)

    df['Supplier_EAN_norm'] = sup_digits.apply(normalize_gtin)
    df['Amazon_EAN_norm'] = amz_digits.apply(normalize_gtin)

    df['Supplier_EAN_strict_valid'] = df['Supplier_EAN_norm'].apply(is_strict_valid_barcode)
    df['Amazon_EAN_strict_valid'] = df['Amazon_EAN_norm'].apply(is_strict_valid_barcode)

    df['is_exact_ean_strict'] = df['Supplier_EAN_strict_valid'] & df['Amazon_EAN_strict_valid'] & (df['Supplier_EAN_norm'] == df['Amazon_EAN_norm'])
    df['ean_conflict'] = df['Supplier_EAN_strict_valid'] & df['Amazon_EAN_strict_valid'] & (df['Supplier_EAN_norm'] != df['Amazon_EAN_norm'])

    df['brand_guess'] = df['SupplierTitle'].fillna('').astype(str).apply(extract_brand_supplier)

    def brand_in_both(row) -> bool:
        b = row['brand_guess']
        return bool(b) and (b in set(tokens(row['AmazonTitle'])))

    df['brand_in_both'] = df.apply(brand_in_both, axis=1)
    df['shared'] = [shared_token_count(s,a) for s,a in zip(df['SupplierTitle'].fillna(''), df['AmazonTitle'].fillna(''))]
    df['jac'] = [jaccard(s,a) for s,a in zip(df['SupplierTitle'].fillna(''), df['AmazonTitle'].fillna(''))]

    sup_units_list=[]; amz_units_list=[]; ev_list=[]; exp_list=[]; rsu_list=[]; adj_list=[]; cap_b=[]; cap_d=[]

    for _, row in df.iterrows():
        s_title = sanitize_cell(row['SupplierTitle'])
        a_title = sanitize_cell(row['AmazonTitle'])

        sup_units = supplier_units_per_pack(s_title)
        amz_units, ev, explicit = amazon_units_required(a_title)

        if amz_units <= 1:
            rsu = 1
        else:
            if sup_units > 0 and amz_units % sup_units == 0:
                rsu = amz_units // sup_units
            else:
                rsu = 1
                if ev != '-':
                    ev = f"UNCERTAIN:{ev}"
                explicit = False

        try:
            adj = adjusted_profit(row['NetProfit'], row['SupplierPrice_incVAT'], int(rsu))
        except Exception:
            adj = float('nan')

        cb = capacity_bucket(s_title, a_title)

        sup_units_list.append(int(sup_units))
        amz_units_list.append(int(amz_units))
        ev_list.append(ev)
        exp_list.append(bool(explicit))
        rsu_list.append(int(rsu))
        adj_list.append(adj)
        cap_b.append(cb[0] if cb else None)
        cap_d.append(cb[1] if cb else None)

    df['SupUnits'] = sup_units_list
    df['AmzUnits'] = amz_units_list
    df['AmzPackEvidence'] = ev_list
    df['AmzPackExplicit'] = exp_list
    df['RSU'] = rsu_list
    df['Adjusted_Profit'] = adj_list
    df['capacity_bucket'] = cap_b
    df['capacity_diff'] = cap_d

    def ev(row):
        bits = [f"RowID {int(row['RowID'])}"]
        if row['is_exact_ean_strict']:
            bits.append('Exact EAN match')
        b = row['brand_guess']
        if b:
            s = sanitize_cell(row['SupplierTitle']).lower()
            a = sanitize_cell(row['AmazonTitle']).lower()
            if b in s and b in a:
                bits.append(f"brand='{b}'")
        if row['AmzPackEvidence'] and row['AmzPackEvidence'] != '-':
            bits.append(str(row['AmzPackEvidence']))
        if row['capacity_bucket'] and row['capacity_diff'] is not None:
            bits.append(f"capacity_diff~{row['capacity_diff']*100.0:.0f}%")
        return '; '.join(bits)

    def pv(row):
        rsu = int(row['RSU'])
        if rsu == 1 and row['is_exact_ean_strict']:
            return '1:1 Match (Exact EAN)'
        if rsu == 1:
            return '1:1 Match'
        return f"BUNDLE (RSU={rsu}x)"

    def display_ean(norm, valid):
        return norm if bool(valid) and norm else '-'

    HEADERS = [
        'Verdict','Confidence','SupplierTitle','AmazonTitle','Supplier EAN','Amazon EAN','ASIN',
        'SupplierPrice','SellingPrice','NetProfit','ROI','Sales','Pack Verdict','Adjusted Profit',
        'Key Match Evidence','Filter Reason'
    ]

    def clip(s: str, n: int):
        s = sanitize_cell(s)
        return s if len(s) <= n else (s[: n-1] + '…')

    def format_rows(rows):
        out=[]
        for r in rows:
            r=list(r)
            r[2]=clip(r[2],140)
            r[3]=clip(r[3],140)
            r[14]=clip(r[14],120)
            r[15]=clip(r[15],110)
            out.append([sanitize_cell(x) for x in r])
        return out

    VERIFIED_REC=[]; VERIFIED_AUDIT=[]; HL_REC=[]; HL_AUDIT=[]; NEEDS_VER=[]
    unrelated=0

    for _, row in df.iterrows():
        s_title = sanitize_cell(row['SupplierTitle'])
        a_title = sanitize_cell(row['AmazonTitle'])

        sup_ean = display_ean(row['Supplier_EAN_norm'], row['Supplier_EAN_strict_valid'])
        amz_ean = display_ean(row['Amazon_EAN_norm'], row['Amazon_EAN_strict_valid'])

        rsu = int(row['RSU'])
        adj = float(row['Adjusted_Profit'])

        ip = ip_risk_brand(a_title, s_title)

        if (not row['is_exact_ean_strict']) and bool(row['ean_conflict']):
            unrelated += 1
            continue

        if (not row['is_exact_ean_strict']) and (not row['brand_in_both']) and int(row['shared']) <= 1 and float(row['jac']) < 0.12:
            unrelated += 1
            continue

        cap = row['capacity_bucket']

        if row['is_exact_ean_strict']:
            conf = 95
            if cap in {'AUDIT_25_50','AUDIT_GT_50'}:
                conf = 85
                fr = f"Different SKU signal (capacity mismatch {row['capacity_diff']*100.0:.0f}%)" + (f"; IP risk ({ip})" if ip else '')
                VERIFIED_AUDIT.append((
                    'VERIFIED — AUDITED OUT', conf, s_title, a_title, sup_ean, amz_ean, str(row['ASIN']),
                    money_gbp(row['SupplierPrice_incVAT']), money_gbp(row['SellingPrice_incVAT']), money_gbp(row['NetProfit']),
                    pct(row['ROI_pct']), str(int(row['Sales'])), pv(row), money_gbp(adj), ev(row), fr
                ))
                continue

            if rsu > 1:
                if str(row['AmzPackEvidence']).startswith('UNCERTAIN'):
                    conf = 90
                if adj <= 0:
                    fr = f"Pack mismatch (amazon={int(row['AmzUnits'])} vs supplier={int(row['SupUnits'])}); RSU={rsu}; adjusted profit ≤ 0" + (f"; IP risk ({ip})" if ip else '')
                    VERIFIED_AUDIT.append((
                        'VERIFIED — AUDITED OUT', conf, s_title, a_title, sup_ean, amz_ean, str(row['ASIN']),
                        money_gbp(row['SupplierPrice_incVAT']), money_gbp(row['SellingPrice_incVAT']), money_gbp(row['NetProfit']),
                        pct(row['ROI_pct']), str(int(row['Sales'])), pv(row) + f"; amazon={int(row['AmzUnits'])}, supplier={int(row['SupUnits'])}",
                        money_gbp(adj), ev(row), fr
                    ))
                else:
                    fr = '-' if not ip else f"IP risk ({ip})"
                    VERIFIED_REC.append((
                        'VERIFIED', conf, s_title, a_title, sup_ean, amz_ean, str(row['ASIN']),
                        money_gbp(row['SupplierPrice_incVAT']), money_gbp(row['SellingPrice_incVAT']), money_gbp(row['NetProfit']),
                        pct(row['ROI_pct']), str(int(row['Sales'])), pv(row) + f"; amazon={int(row['AmzUnits'])}, supplier={int(row['SupUnits'])}",
                        money_gbp(adj), ev(row), fr
                    ))
                continue

            VERIFIED_REC.append((
                'VERIFIED', conf, s_title, a_title, sup_ean, amz_ean, str(row['ASIN']),
                money_gbp(row['SupplierPrice_incVAT']), money_gbp(row['SellingPrice_incVAT']), money_gbp(row['NetProfit']),
                pct(row['ROI_pct']), str(int(row['Sales'])), pv(row), money_gbp(adj), ev(row), '-' if not ip else f"IP risk ({ip})"
            ))
            continue

        plausible_hl = bool(row['brand_in_both']) and int(row['shared']) >= 3 and float(row['jac']) >= 0.20
        plausible_nv = (int(row['shared']) >= 5 and float(row['jac']) >= 0.22) or (bool(row['brand_in_both']) and int(row['shared']) >= 2 and float(row['jac']) >= 0.18)

        if cap in {'AUDIT_GT_50','AUDIT_25_50'} and plausible_hl:
            HL_AUDIT.append((
                'HIGHLY LIKELY — AUDITED OUT', 80, s_title, a_title, sup_ean, amz_ean, str(row['ASIN']),
                money_gbp(row['SupplierPrice_incVAT']), money_gbp(row['SellingPrice_incVAT']), money_gbp(row['NetProfit']),
                pct(row['ROI_pct']), str(int(row['Sales'])), pv(row), money_gbp(adj), ev(row),
                f"Different SKU signal (capacity mismatch {row['capacity_diff']*100.0:.0f}%)" + (f"; IP risk ({ip})" if ip else '')
            ))
            continue

        if plausible_hl:
            conf = 90 if (int(row['shared']) >= 6 and float(row['jac']) >= 0.40) else 85
            if cap == 'VERIFY_10_25':
                NEEDS_VER.append((
                    'NEEDS VERIFICATION', min(conf, 74), s_title, a_title, sup_ean, amz_ean, str(row['ASIN']),
                    money_gbp(row['SupplierPrice_incVAT']), money_gbp(row['SellingPrice_incVAT']), money_gbp(row['NetProfit']),
                    pct(row['ROI_pct']), str(int(row['Sales'])), pv(row), money_gbp(adj), ev(row),
                    f"Confirm capacity variant ({row['capacity_diff']*100.0:.0f}% diff)" + (f"; IP risk ({ip})" if ip else '')
                ))
                continue
            if rsu > 1 and bool(row['AmzPackExplicit']) and adj <= 0:
                HL_AUDIT.append((
                    'HIGHLY LIKELY — AUDITED OUT', 80, s_title, a_title, sup_ean, amz_ean, str(row['ASIN']),
                    money_gbp(row['SupplierPrice_incVAT']), money_gbp(row['SellingPrice_incVAT']), money_gbp(row['NetProfit']),
                    pct(row['ROI_pct']), str(int(row['Sales'])), pv(row) + f"; amazon={int(row['AmzUnits'])}, supplier={int(row['SupUnits'])}",
                    money_gbp(adj), ev(row),
                    f"Pack mismatch implies RSU={rsu}; adjusted profit ≤ 0" + (f"; IP risk ({ip})" if ip else '')
                ))
                continue
            HL_REC.append((
                'HIGHLY LIKELY', conf, s_title, a_title, sup_ean, amz_ean, str(row['ASIN']),
                money_gbp(row['SupplierPrice_incVAT']), money_gbp(row['SellingPrice_incVAT']), money_gbp(row['NetProfit']),
                pct(row['ROI_pct']), str(int(row['Sales'])), pv(row), money_gbp(adj), ev(row), '-' if not ip else f"IP risk ({ip})"
            ))
            continue

        if plausible_nv:
            conf = 72 if (int(row['shared']) >= 6 and float(row['jac']) >= 0.35) else 65
            conf = max(40, min(conf, 74))
            blockers=[]
            if not row['brand_in_both']:
                blockers.append('Confirm brand/variant')
            if cap == 'VERIFY_10_25':
                blockers.append(f"Confirm capacity variant ({row['capacity_diff']*100.0:.0f}% diff)")
            if str(row['AmzPackEvidence']).startswith('UNCERTAIN'):
                blockers.append('Confirm pack count')
            if ip:
                blockers.append(f"IP risk ({ip})")
            fr='; '.join(blockers) if blockers else 'Confirm 1 key detail (pack/variant)'
            # Per methodology + acceptance tests: never leave Adjusted Profit <= 0 in NEEDS VERIFICATION.
            # If the match is otherwise strong (brand+anchors) treat as HIGHLY LIKELY — AUDITED OUT; else exclude as unrelated.
            if rsu > 1 and bool(row['AmzPackExplicit']) and adj <= 0:
                if row['brand_in_both'] and int(row['shared']) >= 3 and float(row['jac']) >= 0.20:
                    HL_AUDIT.append((
                        'HIGHLY LIKELY — AUDITED OUT', 78, s_title, a_title, sup_ean, amz_ean, str(row['ASIN']),
                        money_gbp(row['SupplierPrice_incVAT']), money_gbp(row['SellingPrice_incVAT']), money_gbp(row['NetProfit']),
                        pct(row['ROI_pct']), str(int(row['Sales'])), pv(row) + f"; amazon={int(row['AmzUnits'])}, supplier={int(row['SupUnits'])}",
                        money_gbp(adj), ev(row), f"Pack mismatch implies RSU={rsu}; adjusted profit ≤ 0" + (f"; IP risk ({ip})" if ip else '')
                    ))
                else:
                    unrelated += 1
            else:
                NEEDS_VER.append((
                    'NEEDS VERIFICATION', conf, s_title, a_title, sup_ean, amz_ean, str(row['ASIN']),
                    money_gbp(row['SupplierPrice_incVAT']), money_gbp(row['SellingPrice_incVAT']), money_gbp(row['NetProfit']),
                    pct(row['ROI_pct']), str(int(row['Sales'])), pv(row), money_gbp(adj), ev(row), fr
                ))
        else:
            unrelated += 1

    VERIFIED_REC = sorted(VERIFIED_REC, key=lambda r: int(r[11]), reverse=True)
    VERIFIED_AUDIT = sorted(VERIFIED_AUDIT, key=lambda r: int(r[11]), reverse=True)
    HL_REC = sorted(HL_REC, key=lambda r: (int(r[1]), int(r[11])), reverse=True)
    HL_AUDIT = sorted(HL_AUDIT, key=lambda r: (int(r[1]), int(r[11])), reverse=True)
    NEEDS_VER = sorted(NEEDS_VER, key=lambda r: (int(r[1]), int(r[11])), reverse=True)

    # Compute diffs vs previous
    def rowids(rows):
        rx = re.compile(r"\bRowID\s+(\d+)\b")
        out=set()
        for r in rows:
            m = rx.search(r[14])
            if m:
                out.add(int(m.group(1)))
        return out

    new_sets = {
        'VERIFIED — RECOMMENDED': rowids(VERIFIED_REC),
        'VERIFIED — AUDITED OUT / EXCLUDED': rowids(VERIFIED_AUDIT),
        'HIGHLY LIKELY — RECOMMENDED': rowids(HL_REC),
        'HIGHLY LIKELY — AUDITED OUT / EXCLUDED': rowids(HL_AUDIT),
        'NEEDS VERIFICATION': rowids(NEEDS_VER),
    }

    prev_sets = {
        'VERIFIED — RECOMMENDED': prev_rowids.get('VERIFIED — RECOMMENDED (count=39)', set()),
        'VERIFIED — AUDITED OUT / EXCLUDED': prev_rowids.get('VERIFIED — AUDITED OUT / EXCLUDED (count=1)', set()),
        'HIGHLY LIKELY — RECOMMENDED': prev_rowids.get('HIGHLY LIKELY — RECOMMENDED (count=221)', set()),
        'HIGHLY LIKELY — AUDITED OUT / EXCLUDED': prev_rowids.get('HIGHLY LIKELY — AUDITED OUT / EXCLUDED (count=41)', set()),
        'NEEDS VERIFICATION': prev_rowids.get('NEEDS VERIFICATION (count=120)', set()),
    }

    moved=[]
    for rid in set().union(*prev_sets.values()):
        prev_cat = next((k for k,v in prev_sets.items() if rid in v), None)
        new_cat = next((k for k,v in new_sets.items() if rid in v), None)
        if prev_cat != new_cat:
            moved.append((rid, prev_cat, new_cat))

    moved_verified_to_audit = [x for x in moved if x[1]=='VERIFIED — RECOMMENDED' and x[2]=='VERIFIED — AUDITED OUT / EXCLUDED']
    removed_from_tables = [x for x in moved if x[2] is None]

    removed_non_ean_conflict = 0
    for rid, prev_cat, new_cat in removed_from_tables:
        if prev_cat in {'HIGHLY LIKELY — RECOMMENDED','HIGHLY LIKELY — AUDITED OUT / EXCLUDED','NEEDS VERIFICATION'}:
            # check if the underlying row has ean_conflict
            r = df.loc[df['RowID']==rid].iloc[0]
            if bool(r['ean_conflict']):
                removed_non_ean_conflict += 1

    # Build markdown
    summary = {
        'VERIFIED_REC': len(VERIFIED_REC),
        'VERIFIED_AUDIT': len(VERIFIED_AUDIT),
        'HL_REC': len(HL_REC),
        'HL_AUDIT': len(HL_AUDIT),
        'NEEDS_VER': len(NEEDS_VER),
        'UNRELATED': unrelated,
        'TOTAL': len(df),
    }

    # Apply truncation before rendering
    VERIFIED_REC_F = format_rows(VERIFIED_REC)
    VERIFIED_AUDIT_F = format_rows(VERIFIED_AUDIT)
    HL_REC_F = format_rows(HL_REC)
    HL_AUDIT_F = format_rows(HL_AUDIT)
    NEEDS_VER_F = format_rows(NEEDS_VER)

    md=[]
    md.append('# PHASEA MANUAL REPORT (Validated Review)')
    md.append(f"**Generated:** {report_date} (Asia/Dubai)")
    md.append(f"**Reviewed Report:** {PREV_REPORT}")
    md.append(f"**Source Financial File:** {XLSX_PATH}")
    md.append(f"**Supplier:** {supplier_domain}")
    md.append('')
    md.append('## Corrections Made')
    md.append(f"- Re-applied strict pack-size verification for exact-EAN rows; moved {len(moved_verified_to_audit)} items from VERIFIED → VERIFIED — AUDITED OUT where RSU>1 made adjusted profit ≤ 0.")
    md.append(f"- Enforced hard EAN-conflict rule for non-EAN items (both EANs strict-valid but different) → UNRELATED / NOT INCLUDED; removed {removed_non_ean_conflict} previously-listed rows.")
    md.append('- Kept dimension/measurement shield: patterns like "9x9in" / "30cm x 36cm" are treated as size, not quantity; only explicit pack wording triggers RSU.')
    md.append('- IP risk flags remain context-based (e.g., Apple only when iPhone/iPad/etc appears).')
    md.append('')

    md.append('## Summary Counts')
    md.append(f"- VERIFIED — RECOMMENDED: {summary['VERIFIED_REC']}")
    md.append(f"- VERIFIED — AUDITED OUT / EXCLUDED: {summary['VERIFIED_AUDIT']}")
    md.append(f"- HIGHLY LIKELY — RECOMMENDED: {summary['HL_REC']}")
    md.append(f"- HIGHLY LIKELY — AUDITED OUT / EXCLUDED: {summary['HL_AUDIT']}")
    md.append(f"- NEEDS VERIFICATION: {summary['NEEDS_VER']}")
    md.append(f"- UNRELATED / NOT INCLUDED: {summary['UNRELATED']}")
    md.append(f"- TOTAL ANALYZED: {summary['TOTAL']}")
    md.append('')

    md.append(f"## VERIFIED — RECOMMENDED (count={summary['VERIFIED_REC']})")
    md.append('```text')
    md.append(render_table(VERIFIED_REC_F, HEADERS))
    md.append('```')
    md.append('')

    md.append(f"## VERIFIED — AUDITED OUT / EXCLUDED (count={summary['VERIFIED_AUDIT']})")
    md.append('```text')
    md.append(render_table(VERIFIED_AUDIT_F, HEADERS))
    md.append('```')
    md.append('')

    md.append(f"## HIGHLY LIKELY — RECOMMENDED (count={summary['HL_REC']})")
    md.append('```text')
    md.append(render_table(HL_REC_F, HEADERS))
    md.append('```')
    md.append('')

    md.append(f"## HIGHLY LIKELY — AUDITED OUT / EXCLUDED (count={summary['HL_AUDIT']})")
    md.append('```text')
    md.append(render_table(HL_AUDIT_F, HEADERS))
    md.append('```')
    md.append('')

    md.append(f"## NEEDS VERIFICATION (count={summary['NEEDS_VER']})")
    md.append('```text')
    md.append(render_table(NEEDS_VER_F, HEADERS))
    md.append('```')
    md.append('')

    md.append('## Reconciliation')
    md.append(f"- VERIFIED total: {summary['VERIFIED_REC'] + summary['VERIFIED_AUDIT']}")
    md.append(f"- HIGHLY LIKELY total: {summary['HL_REC'] + summary['HL_AUDIT']}")
    md.append(f"- NEEDS VERIFICATION total: {summary['NEEDS_VER']}")
    md.append(f"- UNRELATED / NOT INCLUDED total: {summary['UNRELATED']}")
    md.append(f"- TOTAL ANALYZED (check): {summary['TOTAL']}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path.write_text('\n'.join(md), encoding='utf-8')

    print(out_path)
    print('bytes:', out_path.stat().st_size)
    print('counts:', summary)


if __name__ == '__main__':
    main()
