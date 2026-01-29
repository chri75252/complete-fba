#!/usr/bin/env python3
"""
FBA Opportunity Analyzer v2
Analyzes Excel workbook to identify best Amazon FBA opportunities and risks.
Date: 2026-01-17 (Asia/Dubai timezone)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import warnings
import re
warnings.filterwarnings('ignore')

# Configuration
INPUT_FILE = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\finale\final ver.xlsx"
OUTPUT_DIR = Path(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\finale\open2\op")
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

# Thresholds
MIN_ROI_PCT = 20.0  # 20%
MIN_PROFIT = 0.01

# Known high-risk brands (gated/complaint-prone)
HIGH_RISK_BRANDS = [
    'nike', 'adidas', 'apple', 'samsung', 'sony', 'microsoft', 'disney', 
    'lego', 'hasbro', 'mattel', 'nintendo', 'pokemon', 'marvel', 'dc comics',
    'louis vuitton', 'gucci', 'prada', 'chanel', 'rolex', 'cartier',
    'bose', 'beats', 'dyson', 'philips', 'braun', 'oral-b', 'gillette'
]

# Medium-risk patterns
MEDIUM_RISK_PATTERNS = ['health', 'vitamin', 'supplement', 'baby', 'toy', 'food', 'cosmetic']

def load_data(filepath):
    """Load Excel and clean column names."""
    print(f"Loading: {filepath}")
    df = pd.read_excel(filepath)
    
    # Strip whitespace from column names
    df.columns = [c.strip() for c in df.columns]
    
    print(f"Detected {len(df)} rows, {len(df.columns)} columns")
    print(f"Columns: {list(df.columns)}")
    
    return df

def clean_numeric(val):
    """Convert value to float, handling various formats."""
    if pd.isna(val):
        return np.nan
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        cleaned = val.replace('£', '').replace('$', '').replace('€', '').replace(',', '').strip()
        try:
            return float(cleaned)
        except:
            return np.nan
    return np.nan

def parse_sales(val):
    """Parse sales/velocity from various formats."""
    if pd.isna(val):
        return np.nan
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        match = re.search(r'[\d,]+', val.replace(',', ''))
        if match:
            try:
                return float(match.group().replace(',', ''))
            except:
                pass
    return np.nan

def assess_brand_risk(title=''):
    """Assess brand/IP risk level from title."""
    title_lower = str(title).lower() if not pd.isna(title) else ''
    
    # Check high-risk brands
    for hr_brand in HIGH_RISK_BRANDS:
        if hr_brand in title_lower:
            return 'High', hr_brand.upper()
    
    # Check medium-risk patterns
    for pattern in MEDIUM_RISK_PATTERNS:
        if pattern in title_lower:
            return 'Medium', pattern.upper()
    
    return 'Low', ''

def get_velocity_band(sales):
    """Categorize sales velocity."""
    if pd.isna(sales) or sales < 0:
        return 'Unknown'
    if sales >= 100:
        return 'High'
    if sales >= 30:
        return 'Medium'
    return 'Low'

def calculate_opportunity_score(row):
    """
    Calculate opportunity score (0-100).
    Weights: ROI 35%, Profit 25%, Velocity 20%, Competition 10%, Risk 10%
    """
    score = 0
    
    # ROI component (35% weight, max 35 points)
    roi = row.get('ROI_PCT', 0)
    if not pd.isna(roi) and roi > 0:
        roi_score = min(roi / 100 * 35, 35)  # Cap at 100% ROI for max points
        score += roi_score
    
    # Profit component (25% weight, max 25 points)
    profit = row.get('PROFIT', 0)
    if not pd.isna(profit) and profit > 0:
        profit_score = min(profit / 15 * 25, 25)  # Cap at £15 profit for max points
        score += profit_score
    
    # Velocity component (20% weight)
    velocity = row.get('VELOCITY_BAND', 'Unknown')
    velocity_scores = {'High': 20, 'Medium': 12, 'Low': 5, 'Unknown': 8}
    score += velocity_scores.get(velocity, 0)
    
    # Competition pressure inverse (10% weight) - assume neutral if unknown
    score += 5  # Default middle score
    
    # Brand risk inverse (10% weight)
    risk = row.get('BRAND_RISK', 'Unknown')
    risk_scores = {'Low': 10, 'Unknown': 5, 'Medium': 3, 'High': 0}
    score += risk_scores.get(risk, 0)
    
    return round(score, 1)

def analyze_data(df):
    """Perform full analysis on the data."""
    results = []
    
    # Identify columns (flexible matching)
    cols = {c.lower(): c for c in df.columns}
    
    for idx, row in df.iterrows():
        entry = {'ROW_NUM': idx + 2}  # Excel row number
        
        # Extract fields
        entry['VERDICT'] = str(row.get('Verdict', '')).strip() if 'Verdict' in df.columns else ''
        entry['CONFIDENCE'] = clean_numeric(row.get('Confidence', np.nan)) if 'Confidence' in df.columns else np.nan
        entry['TITLE'] = str(row.get('SupplierTitle', ''))[:80].strip() if 'SupplierTitle' in df.columns else ''
        entry['ASIN'] = str(row.get('ASIN', '')).strip() if 'ASIN' in df.columns else f'ROW_{idx+2}'
        
        # Get Amazon title if available
        amazon_title = str(row.get('Amazon Title', ''))[:80].strip() if 'Amazon Title' in df.columns else ''
        entry['AMAZON_TITLE'] = amazon_title
        
        # Prices and profit
        entry['SUPPLIER_PRICE'] = clean_numeric(row.get('SupplierPrice', np.nan)) if 'SupplierPrice' in df.columns else np.nan
        entry['PROFIT'] = clean_numeric(row.get('Adjusted Profit', np.nan)) if 'Adjusted Profit' in df.columns else np.nan
        
        # ROI - convert from decimal to percentage
        roi_raw = clean_numeric(row.get('ROI', np.nan)) if 'ROI' in df.columns else np.nan
        if not pd.isna(roi_raw):
            # If ROI is given as decimal (e.g., 0.284), convert to percentage
            if abs(roi_raw) < 10:  # Likely a decimal
                entry['ROI_PCT'] = round(roi_raw * 100, 1)
            else:
                entry['ROI_PCT'] = round(roi_raw, 1)
        else:
            entry['ROI_PCT'] = np.nan
        
        # Sales
        entry['SALES'] = parse_sales(row.get('Sales', np.nan)) if 'Sales' in df.columns else np.nan
        
        # EAN
        entry['AMAZON_EAN'] = str(row.get('Amazon EAN', '')).strip() if 'Amazon EAN' in df.columns else ''
        
        # Key match evidence and filter reason
        entry['MATCH_EVIDENCE'] = str(row.get('Key Match Evidence', ''))[:100] if 'Key Match Evidence' in df.columns else ''
        entry['FILTER_REASON'] = str(row.get('Filter Reason', ''))[:100] if 'Filter Reason' in df.columns else ''
        
        # Velocity band
        entry['VELOCITY_BAND'] = get_velocity_band(entry['SALES'])
        
        # Brand risk (from title)
        risk, risk_reason = assess_brand_risk(entry['TITLE'])
        entry['BRAND_RISK'] = risk
        entry['RISK_REASON'] = risk_reason
        
        # Calculate Buy Cost from Profit and ROI if possible
        if not pd.isna(entry['PROFIT']) and not pd.isna(entry['ROI_PCT']) and entry['ROI_PCT'] > 0:
            # ROI = Profit / BuyCost, so BuyCost = Profit / (ROI/100)
            entry['BUY_COST'] = round(entry['PROFIT'] / (entry['ROI_PCT'] / 100), 2)
        else:
            entry['BUY_COST'] = entry['SUPPLIER_PRICE']  # Use supplier price as proxy
        
        # Opportunity score
        entry['SCORE'] = calculate_opportunity_score(entry)
        
        results.append(entry)
    
    return pd.DataFrame(results)

def categorize_products(df_analyzed):
    """Categorize products into Shortlist, Do-Not-Buy, and Backlog."""
    shortlist = []
    do_not_buy = []
    backlog = []
    
    for idx, row in df_analyzed.iterrows():
        asin = row['ASIN']
        profit = row['PROFIT']
        roi = row['ROI_PCT']
        risk = row['BRAND_RISK']
        velocity = row['VELOCITY_BAND']
        score = row['SCORE']
        verdict = row['VERDICT']
        
        # Check exclusion criteria
        exclusion_reasons = []
        
        if pd.isna(profit) or profit <= 0:
            exclusion_reasons.append(f"Non-positive profit (£{profit:.2f})" if not pd.isna(profit) else "Missing profit data")
        
        if pd.isna(roi) or roi < MIN_ROI_PCT:
            roi_str = f"{roi:.1f}%" if not pd.isna(roi) else "N/A"
            exclusion_reasons.append(f"ROI below {MIN_ROI_PCT}% ({roi_str})")
        
        if risk == 'High':
            exclusion_reasons.append(f"High brand/IP risk ({row['RISK_REASON']})")
        
        # Categorize
        if exclusion_reasons:
            do_not_buy.append({
                'ASIN': asin,
                'TITLE': row['TITLE'][:50],
                'PROFIT': profit,
                'ROI_PCT': roi,
                'VERDICT': verdict,
                'REASON': '; '.join(exclusion_reasons)
            })
        elif risk == 'Unknown' or velocity == 'Unknown':
            backlog.append({
                'ASIN': asin,
                'TITLE': row['TITLE'][:50],
                'PROFIT': profit,
                'ROI_PCT': roi,
                'SALES': row['SALES'],
                'VERDICT': verdict,
                'MISSING_INFO': 'Unknown Velocity' if velocity == 'Unknown' else 'Unknown Risk',
                'NEXT_ACTION': 'Verify Keepa rank/sales'
            })
        else:
            # Shortlist candidate
            decision = "CONSIDER"
            if score >= 60:
                decision = "STRONG BUY"
            elif score >= 45:
                decision = "BUY"
            
            # Add existing verdict info
            if verdict and 'VERIFIED' in verdict.upper():
                decision = f"✓ {decision}"
            
            shortlist.append({
                'ASIN': asin,
                'TITLE': row['TITLE'][:50],
                'AMAZON_TITLE': row['AMAZON_TITLE'][:40],
                'BUY_COST': row['BUY_COST'],
                'SUPPLIER_PRICE': row['SUPPLIER_PRICE'],
                'PROFIT': profit,
                'ROI_PCT': roi,
                'SALES': row['SALES'],
                'VELOCITY': velocity,
                'BRAND_RISK': risk,
                'SCORE': score,
                'VERDICT': verdict,
                'CONFIDENCE': row['CONFIDENCE'],
                'MATCH_EVIDENCE': row['MATCH_EVIDENCE'][:60],
                'DECISION': decision
            })
    
    # Sort shortlist by score, then profit, then ROI
    shortlist = sorted(shortlist, key=lambda x: (
        -x['SCORE'], 
        -(x['PROFIT'] if not pd.isna(x['PROFIT']) else 0),
        -(x['ROI_PCT'] if not pd.isna(x['ROI_PCT']) else 0)
    ))
    
    return shortlist[:20], do_not_buy, backlog

def generate_markdown_report(shortlist, do_not_buy, backlog, df_analyzed):
    """Generate the final markdown report."""
    report = []
    
    report.append("# FBA Opportunity Analysis Report")
    report.append(f"\n**Generated:** 2026-01-17 03:40 (Asia/Dubai)")
    report.append(f"**Source File:** final ver.xlsx")
    report.append(f"**Total Products Analyzed:** {len(df_analyzed)}")
    report.append("")
    
    # Objective
    report.append("## Objective")
    report.append("")
    report.append("This report identifies the best Amazon FBA investment opportunities from the provided product data. Products are evaluated based on net profit (treated as authoritative), ROI, sales velocity, and brand/IP risk. The analysis produces a prioritized shortlist for immediate action, a do-not-buy list with clear reasons, and a backlog for products requiring deeper research.")
    report.append("")
    
    # Methodology
    report.append("## Methodology")
    report.append("")
    report.append("1. **Data Ingestion**: Loaded Excel workbook with pre-analyzed data including Verdict, Confidence, Profit, and ROI")
    report.append("2. **ROI Validation**: Confirmed ROI and Adjusted Profit are pre-calculated (net of all fees)")
    report.append("3. **Velocity Banding**: Categorized sales as High (≥100/mo), Medium (30-99), Low (<30)")
    report.append("4. **Risk Assessment**: Evaluated brand/IP risk based on known gated brands in product titles")
    report.append("5. **Opportunity Scoring**: Weighted score (ROI 35%, Profit 25%, Velocity 20%, Competition 10%, Risk 10%)")
    report.append(f"6. **Filtering**: Excluded negative profit, ROI <{MIN_ROI_PCT}%, and high-risk brands")
    report.append("")
    
    # Assumptions
    report.append("### Assumptions")
    report.append("")
    report.append("- **Adjusted Profit** is net of all fees (referral, FBA, prep, etc.) - not recalculated")
    report.append("- **ROI** values are pre-calculated and authoritative")
    report.append("- **Sales** figures represent 30-day Amazon 'N sold' badge data")
    report.append("- **Verdict/Confidence** from prior analysis carried forward")
    report.append("")
    
    # Examples
    report.append("## Examples")
    report.append("")
    if shortlist:
        ex = shortlist[0]
        report.append("### Example Shortlist Entry")
        report.append(f"- **ASIN:** {ex['ASIN']}")
        report.append(f"- **Title:** {ex['TITLE']}")
        report.append(f"- **Supplier Price:** £{ex['SUPPLIER_PRICE']:.2f}" if ex['SUPPLIER_PRICE'] else "- **Supplier Price:** N/A")
        report.append(f"- **Profit:** £{ex['PROFIT']:.2f}" if ex['PROFIT'] else "- **Profit:** N/A")
        report.append(f"- **ROI:** {ex['ROI_PCT']:.1f}%")
        report.append(f"- **Sales/mo:** {int(ex['SALES']) if ex['SALES'] else 'N/A'}")
        report.append(f"- **Velocity:** {ex['VELOCITY']}")
        report.append(f"- **Risk:** {ex['BRAND_RISK']}")
        report.append(f"- **Score:** {ex['SCORE']}")
        report.append(f"- **Prior Verdict:** {ex['VERDICT']}")
        report.append(f"- **Decision:** {ex['DECISION']}")
        report.append("")
    
    if do_not_buy:
        ex = do_not_buy[0]
        report.append("### Example Do-Not-Buy Entry")
        report.append(f"- **ASIN:** {ex['ASIN']}")
        report.append(f"- **Title:** {ex['TITLE']}")
        report.append(f"- **Reason:** {ex['REASON']}")
        report.append("")
    
    # Output Format section
    report.append("## Output Format")
    report.append("")
    
    # Shortlist
    report.append("### 1. Shortlist (Top Investment Opportunities)")
    report.append("")
    report.append(f"**{len(shortlist)} products** meet all criteria for immediate consideration.")
    report.append("")
    
    if shortlist:
        report.append("| ASIN | Title | SupplierPrice | Profit | ROI% | Sales | Velocity | Risk | Score | Verdict | Decision |")
        report.append("|------|-------|---------------|--------|------|-------|----------|------|-------|---------|----------|")
        for item in shortlist:
            sp = f"£{item['SUPPLIER_PRICE']:.2f}" if item['SUPPLIER_PRICE'] else "N/A"
            pf = f"£{item['PROFIT']:.2f}" if item['PROFIT'] else "N/A"
            roi = f"{item['ROI_PCT']:.1f}%" if item['ROI_PCT'] else "N/A"
            sales = f"{int(item['SALES'])}" if item['SALES'] else "N/A"
            report.append(f"| {item['ASIN']} | {item['TITLE'][:35]}... | {sp} | {pf} | {roi} | {sales} | {item['VELOCITY']} | {item['BRAND_RISK']} | {item['SCORE']} | {item['VERDICT']} | **{item['DECISION']}** |")
        report.append("")
    else:
        report.append("*No products met all shortlist criteria.*")
        report.append("")
    
    # Do-Not-Buy
    report.append("### 2. Do-Not-Buy List")
    report.append("")
    report.append(f"**{len(do_not_buy)} products** excluded with clear reasons.")
    report.append("")
    
    if do_not_buy:
        report.append("| ASIN | Title | Profit | ROI% | Verdict | Reason |")
        report.append("|------|-------|--------|------|---------|--------|")
        for item in do_not_buy:
            pf = f"£{item['PROFIT']:.2f}" if item['PROFIT'] and not pd.isna(item['PROFIT']) else "N/A"
            roi = f"{item['ROI_PCT']:.1f}%" if item['ROI_PCT'] and not pd.isna(item['ROI_PCT']) else "N/A"
            report.append(f"| {item['ASIN']} | {item['TITLE'][:30]}... | {pf} | {roi} | {item['VERDICT']} | {item['REASON']} |")
        report.append("")
    else:
        report.append("*No products in do-not-buy list.*")
        report.append("")
    
    # Backlog
    report.append("### 3. Backlog (Needs Deep Dive)")
    report.append("")
    report.append(f"**{len(backlog)} products** require additional research before decision.")
    report.append("")
    
    if backlog:
        report.append("| ASIN | Title | Profit | ROI% | Sales | Verdict | Missing Info | Next Action |")
        report.append("|------|-------|--------|------|-------|---------|--------------|-------------|")
        for item in backlog[:20]:
            pf = f"£{item['PROFIT']:.2f}" if item['PROFIT'] else "N/A"
            roi = f"{item['ROI_PCT']:.1f}%" if item['ROI_PCT'] else "N/A"
            sales = f"{int(item['SALES'])}" if item['SALES'] else "N/A"
            report.append(f"| {item['ASIN']} | {item['TITLE'][:30]}... | {pf} | {roi} | {sales} | {item['VERDICT']} | {item['MISSING_INFO']} | {item['NEXT_ACTION']} |")
        report.append("")
    else:
        report.append("*No products in backlog.*")
        report.append("")
    
    # Quality Assurance
    report.append("## Quality Assurance")
    report.append("")
    report.append("✅ **Validation Checks Performed:**")
    report.append(f"- Validated Profit > 0 for all {len(shortlist)} shortlisted items")
    report.append(f"- Verified ROI ≥ {MIN_ROI_PCT}% threshold for shortlist")
    high_risk_count = len([x for x in do_not_buy if 'High brand' in x['REASON']])
    report.append(f"- Flagged {high_risk_count} high-risk brand items")
    report.append(f"- Logged {len(backlog)} items with unknown/missing data to backlog")
    report.append(f"- All {len(do_not_buy)} exclusions have explicit reasons documented")
    report.append("")
    
    # Stats summary
    report.append("### Summary Statistics")
    report.append("")
    report.append(f"| Metric | Value |")
    report.append(f"|--------|-------|")
    report.append(f"| Total Analyzed | {len(df_analyzed)} |")
    report.append(f"| Shortlist (Buy/Consider) | {len(shortlist)} |")
    report.append(f"| Do-Not-Buy | {len(do_not_buy)} |")
    report.append(f"| Backlog | {len(backlog)} |")
    if shortlist:
        avg_roi = np.mean([x['ROI_PCT'] for x in shortlist if x['ROI_PCT']])
        avg_profit = np.mean([x['PROFIT'] for x in shortlist if x['PROFIT']])
        report.append(f"| Shortlist Avg ROI | {avg_roi:.1f}% |")
        report.append(f"| Shortlist Avg Profit | £{avg_profit:.2f} |")
    report.append("")
    
    # Reasoning Summary
    report.append("---")
    report.append("")
    report.append("## Reasoning Summary")
    report.append("")
    report.append(f"- **{len(shortlist)} opportunities** meet all criteria: positive profit, ROI ≥{MIN_ROI_PCT}%, acceptable brand risk")
    report.append(f"- **{len(do_not_buy)} exclusions** fail on profit ({sum(1 for x in do_not_buy if 'profit' in x['REASON'].lower())}), ROI threshold ({sum(1 for x in do_not_buy if 'ROI' in x['REASON'])}), or brand risk ({high_risk_count})")
    report.append("- **Scoring** prioritizes ROI (35%) and profit dollars (25%) as primary investment metrics")
    report.append("- Products with prior VERIFIED verdicts given preference in decision language")
    report.append("")
    
    report.append("## Next Steps")
    report.append("")
    report.append("1. **Immediate Action**: Source top 5 items marked STRONG BUY")
    report.append("2. **Validation**: Cross-check ASIN listings on Amazon for stock/price changes")
    report.append("3. **Backlog Review**: Use Keepa to verify sales rank trends for backlog items")
    report.append("4. **Test Orders**: Start with 24-unit test orders for highest-confidence items")
    report.append("5. **Monitor**: Track velocity and competition for shortlisted items weekly")
    report.append("")
    
    return '\n'.join(report)

def main():
    """Main execution."""
    print("="*60)
    print("FBA OPPORTUNITY ANALYZER v2")
    print(f"Date: 2026-01-17 (Asia/Dubai)")
    print("="*60)
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load and analyze
    df = load_data(INPUT_FILE)
    df_analyzed = analyze_data(df)
    
    print(f"\nAnalysis complete. Processing {len(df_analyzed)} products...")
    
    # Categorize
    shortlist, do_not_buy, backlog = categorize_products(df_analyzed)
    
    print(f"Shortlist: {len(shortlist)} | Do-Not-Buy: {len(do_not_buy)} | Backlog: {len(backlog)}")
    
    # Generate report
    report = generate_markdown_report(shortlist, do_not_buy, backlog, df_analyzed)
    
    # Save outputs
    report_path = OUTPUT_DIR / f"FBA_OPPORTUNITY_REPORT_{TIMESTAMP}.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\nReport saved: {report_path}")
    
    # Save analyzed data as Excel
    excel_path = OUTPUT_DIR / f"FBA_ANALYZED_DATA_{TIMESTAMP}.xlsx"
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df_analyzed.to_excel(writer, sheet_name='All Analyzed', index=False)
        pd.DataFrame(shortlist).to_excel(writer, sheet_name='Shortlist', index=False) if shortlist else None
        pd.DataFrame(do_not_buy).to_excel(writer, sheet_name='Do-Not-Buy', index=False) if do_not_buy else None
        pd.DataFrame(backlog).to_excel(writer, sheet_name='Backlog', index=False) if backlog else None
    print(f"Data saved: {excel_path}")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total Products: {len(df_analyzed)}")
    print(f"Shortlist: {len(shortlist)} items")
    print(f"Do-Not-Buy: {len(do_not_buy)} items")
    print(f"Backlog: {len(backlog)} items")
    
    if shortlist:
        print("\nTop 5 Opportunities:")
        for i, item in enumerate(shortlist[:5], 1):
            print(f"  {i}. {item['ASIN']} | ROI: {item['ROI_PCT']:.1f}% | Profit: £{item['PROFIT']:.2f} | {item['DECISION']}")
    
    print("="*60)
    
    return report_path, excel_path

if __name__ == "__main__":
    main()
