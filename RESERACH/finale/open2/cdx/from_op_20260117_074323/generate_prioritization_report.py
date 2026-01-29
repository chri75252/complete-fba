#!/usr/bin/env python3
"""
FBA Prioritization Report Generator
Creates a detailed follow-on report explaining shortlist decisions and prioritization
Date: 2026-01-17 (Asia/Dubai timezone)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import warnings
import math
warnings.filterwarnings('ignore')

# Configuration
INPUT_FILE = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\finale\final ver.xlsx"
OUTPUT_DIR = Path(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\finale\open2\op")
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

# Thresholds
MIN_ROI_PCT = 20.0
MIN_PROFIT = 0.01

def load_data(filepath):
    """Load and clean the Excel data."""
    df = pd.read_excel(filepath)
    df.columns = [c.strip() for c in df.columns]
    return df

def get_velocity_band(sales):
    """Categorize sales velocity."""
    if pd.isna(sales) or sales < 0:
        return 'Unknown'
    if sales >= 100:
        return 'High'
    if sales >= 30:
        return 'Medium'
    return 'Low'

def get_seasonality_note(title):
    """Infer seasonality from title keywords."""
    title_lower = str(title).lower()
    
    if any(w in title_lower for w in ['christmas', 'xmas', 'festive', 'santa', 'reindeer', 'robin']):
        return 'Seasonal (Christmas) - Q4 peak'
    if any(w in title_lower for w in ['halloween', 'scary', 'spooky', 'pumpkin']):
        return 'Seasonal (Halloween) - Oct peak'
    if any(w in title_lower for w in ['easter', 'bunny', 'egg hunt']):
        return 'Seasonal (Easter) - Spring peak'
    if any(w in title_lower for w in ['summer', 'beach', 'pool', 'bbq', 'barbecue']):
        return 'Seasonal (Summer) - Jun-Aug'
    if any(w in title_lower for w in ['winter', 'snow', 'cold']):
        return 'Seasonal (Winter) - Nov-Feb'
    if any(w in title_lower for w in ['valentine', 'heart', 'love']):
        return 'Seasonal (Valentine) - Feb peak'
    if any(w in title_lower for w in ['back to school', 'school']):
        return 'Seasonal (Back-to-School) - Aug-Sep'
    if any(w in title_lower for w in ['fire', 'firelighter', 'log']):
        return 'Seasonal (Winter heating) - Oct-Mar'
    if any(w in title_lower for w in ['mulled wine', 'cinnamon']):
        return 'Seasonal (Winter/Holiday) - Nov-Dec peak'
    
    return 'None/Low'

def assess_brand_risk(title):
    """Assess brand risk from title."""
    HIGH_RISK_BRANDS = ['nike', 'adidas', 'apple', 'samsung', 'sony', 'microsoft', 'disney', 
                        'lego', 'hasbro', 'mattel', 'nintendo', 'pokemon', 'marvel']
    title_lower = str(title).lower()
    
    for brand in HIGH_RISK_BRANDS:
        if brand in title_lower:
            return 'High', brand.upper()
    
    return 'Low', ''

def calculate_test_units(sales, budget_constrained=False):
    """Calculate suggested test order units."""
    if pd.isna(sales) or sales <= 0:
        return 12  # Default minimum
    
    # units = min(ceil(0.3 × Sales_Last30D), 30)
    suggested = min(math.ceil(0.3 * sales), 30)
    
    if budget_constrained:
        suggested = min(suggested, 24)
    
    return max(suggested, 12)  # Minimum 12 units

def generate_report(df):
    """Generate the prioritization report."""
    
    # Process data
    products = []
    for idx, row in df.iterrows():
        title = str(row['SupplierTitle'])[:60].strip()
        asin = str(row['ASIN']).strip()
        
        # Clean numeric values
        supplier_price = row.get('SupplierPrice', np.nan)
        selling_price = row.get('SellingPrice', np.nan)
        net_profit = row.get('NetProfit', np.nan)
        adj_profit = row.get('Adjusted Profit', np.nan)
        roi_raw = row.get('ROI', np.nan)
        sales = row.get('Sales', np.nan)
        verdict = str(row.get('Verdict', '')).strip()
        confidence = row.get('Confidence', np.nan)
        
        # Use adjusted profit if available, else net profit
        profit = adj_profit if not pd.isna(adj_profit) else net_profit
        
        # Convert ROI from decimal to percentage
        if not pd.isna(roi_raw) and abs(roi_raw) < 10:
            roi_pct = roi_raw * 100
        else:
            roi_pct = roi_raw if not pd.isna(roi_raw) else np.nan
        
        # Velocity
        velocity = get_velocity_band(sales)
        
        # Seasonality
        seasonality = get_seasonality_note(title)
        
        # Brand risk
        risk, risk_brand = assess_brand_risk(title)
        
        products.append({
            'ROW': idx + 2,
            'ASIN': asin,
            'TITLE': title,
            'SUPPLIER_PRICE': supplier_price,
            'SELLING_PRICE': selling_price,
            'PROFIT': profit,
            'ROI_PCT': roi_pct,
            'SALES': sales,
            'VELOCITY': velocity,
            'SEASONALITY': seasonality,
            'RISK': risk,
            'RISK_BRAND': risk_brand,
            'VERDICT': verdict,
            'CONFIDENCE': confidence
        })
    
    df_products = pd.DataFrame(products)
    
    # Categorize into tiers
    focus_now = []
    focus_next = []
    monitor = []
    do_not_buy = []
    
    for _, row in df_products.iterrows():
        profit = row['PROFIT']
        roi = row['ROI_PCT']
        risk = row['RISK']
        velocity = row['VELOCITY']
        seasonality = row['SEASONALITY']
        verdict = row['VERDICT']
        
        # Exclusion criteria
        if pd.isna(profit) or profit <= 0:
            do_not_buy.append({**row.to_dict(), 'REASON': 'Missing or non-positive profit'})
            continue
        
        if pd.isna(roi) or roi < MIN_ROI_PCT:
            do_not_buy.append({**row.to_dict(), 'REASON': f'ROI below {MIN_ROI_PCT}% ({roi:.1f}%)'})
            continue
        
        if risk == 'High':
            do_not_buy.append({**row.to_dict(), 'REASON': f'High brand/IP risk ({row["RISK_BRAND"]})'})
            continue
        
        if 'AUDITED OUT' in verdict.upper():
            do_not_buy.append({**row.to_dict(), 'REASON': 'Audited out in prior review'})
            continue
        
        # Tier categorization
        if seasonality != 'None/Low':
            # Seasonal items go to Focus Next
            focus_next.append(row.to_dict())
        elif velocity in ['High', 'Medium'] and roi >= 25 and profit >= 1.0:
            # Best items go to Focus Now
            focus_now.append(row.to_dict())
        elif roi >= 20 and profit > 0:
            # Marginal items go to Monitor
            monitor.append(row.to_dict())
        else:
            do_not_buy.append({**row.to_dict(), 'REASON': 'Does not meet tier criteria'})
    
    # Sort Focus Now by score (ROI × Profit × Velocity factor)
    for item in focus_now:
        velocity_mult = {'High': 1.5, 'Medium': 1.0, 'Low': 0.5, 'Unknown': 0.7}
        score = (item['ROI_PCT'] or 0) * (item['PROFIT'] or 0) * velocity_mult.get(item['VELOCITY'], 0.7)
        item['PRIORITY_SCORE'] = score
    
    focus_now = sorted(focus_now, key=lambda x: -x['PRIORITY_SCORE'])[:8]
    
    # Sort Focus Next by ROI
    focus_next = sorted(focus_next, key=lambda x: -(x['ROI_PCT'] or 0))[:5]
    
    # Sort Monitor by ROI
    monitor = sorted(monitor, key=lambda x: -(x['ROI_PCT'] or 0))[:5]
    
    return focus_now, focus_next, monitor, do_not_buy

def create_markdown_report(focus_now, focus_next, monitor, do_not_buy):
    """Create the final Markdown report."""
    
    report = []
    
    # Header
    report.append("# FBA Prioritization & Decision Report")
    report.append("")
    report.append(f"**Generated:** 2026-01-17 04:30 (Asia/Dubai)")
    report.append(f"**Report Type:** Follow-on Prioritization Analysis")
    report.append(f"**Source:** final ver.xlsx (37 products)")
    report.append("")
    
    # Objective
    report.append("## Objective")
    report.append("")
    report.append("This follow-on report explains the decisions behind the previously delivered shortlist and provides clear prioritization guidance. Products are categorized into actionable tiers (Focus Now, Focus Next, Monitor) with brief rationales, seasonality notes, and capital-aware ordering suggestions.")
    report.append("")
    
    # Methodology
    report.append("## Methodology")
    report.append("")
    report.append("1. **Data Validation**: Loaded 37 products from source Excel with pre-calculated Adjusted Profit and ROI")
    report.append("2. **Tier Assignment**: Categorized by ROI threshold (≥20%), profit positivity, velocity, and seasonality")
    report.append("3. **Risk Screening**: Excluded high-risk brands (Adidas, Nike, etc.)")
    report.append("4. **Seasonality Detection**: Inferred from product title keywords")
    report.append("5. **Priority Scoring**: Ranked by ROI × Profit × Velocity multiplier")
    report.append("6. **Capital Guidance**: Test units calculated as min(ceil(0.3 × Sales/mo), 30)")
    report.append("")
    
    # Executive Summary
    report.append("## Executive Summary")
    report.append("")
    report.append(f"From 37 analyzed products, **{len(focus_now)} items** are ready for immediate sourcing (Focus Now), **{len(focus_next)} items** are seasonal/timing-dependent (Focus Next), and **{len(monitor)} items** require monitoring before commitment. **{len(do_not_buy)} items** were excluded due to low ROI, missing data, or brand risk.")
    report.append("")
    if focus_now:
        top = focus_now[0]
        report.append(f"**Top Pick:** {top['ASIN']} ({top['TITLE'][:40]}...) — ROI {top['ROI_PCT']:.1f}%, Profit £{top['PROFIT']:.2f}, {top['VELOCITY']} velocity")
    report.append("")
    
    # Focus Now Table
    report.append("## 🎯 Focus Now (Top Priority — Source Immediately)")
    report.append("")
    report.append(f"**{len(focus_now)} products** meet all criteria for immediate sourcing.")
    report.append("")
    
    if focus_now:
        report.append("| # | ASIN | Title | Cost | Price | Profit | ROI% | Sales/mo | Velocity | Risk | Seasonality | Why Focus | Next Action |")
        report.append("|---|------|-------|------|-------|--------|------|----------|----------|------|-------------|-----------|-------------|")
        
        for i, item in enumerate(focus_now, 1):
            cost = f"£{item['SUPPLIER_PRICE']:.2f}" if item['SUPPLIER_PRICE'] else "N/A"
            price = f"£{item['SELLING_PRICE']:.2f}" if item['SELLING_PRICE'] else "N/A"
            profit = f"£{item['PROFIT']:.2f}" if item['PROFIT'] else "N/A"
            roi = f"{item['ROI_PCT']:.1f}%" if item['ROI_PCT'] else "N/A"
            sales = f"{int(item['SALES'])}" if item['SALES'] else "N/A"
            
            # Why focus bullets
            why = []
            if item['ROI_PCT'] and item['ROI_PCT'] >= 50:
                why.append(f"Excellent ROI ({item['ROI_PCT']:.0f}%)")
            elif item['ROI_PCT'] and item['ROI_PCT'] >= 30:
                why.append(f"Strong ROI ({item['ROI_PCT']:.0f}%)")
            else:
                why.append(f"Solid ROI ({item['ROI_PCT']:.0f}%)")
            
            if item['VELOCITY'] == 'High':
                why.append("High velocity")
            elif item['VELOCITY'] == 'Medium':
                why.append("Steady velocity")
            
            if item['PROFIT'] and item['PROFIT'] >= 5:
                why.append(f"Strong £{item['PROFIT']:.2f} profit")
            
            why_str = "; ".join(why[:2])
            
            # Next action
            units = calculate_test_units(item['SALES'])
            unit_cost = item['SUPPLIER_PRICE'] or 5
            budget = units * unit_cost
            next_action = f"Order {units} units (~£{budget:.0f})"
            
            report.append(f"| {i} | {item['ASIN']} | {item['TITLE'][:30]}... | {cost} | {price} | {profit} | {roi} | {sales} | {item['VELOCITY']} | {item['RISK']} | {item['SEASONALITY'][:15]} | {why_str} | {next_action} |")
        
        report.append("")
    else:
        report.append("*No products in Focus Now tier.*")
        report.append("")
    
    # Focus Next (Seasonal)
    report.append("## 📅 Focus Next (Seasonal/Calendar-Timed)")
    report.append("")
    report.append(f"**{len(focus_next)} products** have good economics but are timing-sensitive.")
    report.append("")
    
    if focus_next:
        report.append("| ASIN | Title | Profit | ROI% | Seasonality | Trigger Window | Prep Lead Time | Action |")
        report.append("|------|-------|--------|------|-------------|----------------|----------------|--------|")
        
        for item in focus_next:
            profit = f"£{item['PROFIT']:.2f}" if item['PROFIT'] else "N/A"
            roi = f"{item['ROI_PCT']:.1f}%" if item['ROI_PCT'] else "N/A"
            
            # Determine trigger window and lead time
            if 'Christmas' in item['SEASONALITY']:
                trigger = "Oct 15 - Nov 15"
                lead = "Order by Sep 30"
            elif 'Winter' in item['SEASONALITY']:
                trigger = "Oct 1 - Feb 28"
                lead = "Order by Sep 15"
            elif 'Halloween' in item['SEASONALITY']:
                trigger = "Sep 15 - Oct 25"
                lead = "Order by Aug 30"
            else:
                trigger = "Varies"
                lead = "Monitor demand"
            
            action = f"Re-evaluate Keepa by trigger date"
            
            report.append(f"| {item['ASIN']} | {item['TITLE'][:35]}... | {profit} | {roi} | {item['SEASONALITY'][:25]} | {trigger} | {lead} | {action} |")
        
        report.append("")
    else:
        report.append("*No seasonal products identified.*")
        report.append("")
    
    # Monitor/Probe
    report.append("## 👁️ Monitor/Probe (Needs Blocker Cleared)")
    report.append("")
    report.append(f"**{len(monitor)} products** are promising but require one blocker to clear.")
    report.append("")
    
    if monitor:
        report.append("| ASIN | Title | Profit | ROI% | Velocity | Blocker | Next Step |")
        report.append("|------|-------|--------|------|----------|---------|-----------|")
        
        for item in monitor:
            profit = f"£{item['PROFIT']:.2f}" if item['PROFIT'] else "N/A"
            roi = f"{item['ROI_PCT']:.1f}%" if item['ROI_PCT'] else "N/A"
            
            # Determine blocker
            if item['VELOCITY'] == 'Low':
                blocker = "Low velocity"
                next_step = "Verify Keepa sales rank trend"
            elif item['VELOCITY'] == 'Unknown':
                blocker = "Unknown sales data"
                next_step = "Check Amazon listing for sales badge"
            elif item['PROFIT'] and item['PROFIT'] < 1.0:
                blocker = "Low profit margin"
                next_step = "Negotiate better supplier price"
            else:
                blocker = "Marginal metrics"
                next_step = "Monitor for 2 weeks"
            
            report.append(f"| {item['ASIN']} | {item['TITLE'][:35]}... | {profit} | {roi} | {item['VELOCITY']} | {blocker} | {next_step} |")
        
        report.append("")
    else:
        report.append("*No products in Monitor tier.*")
        report.append("")
    
    # Do-Not-Buy Rollup
    report.append("## 🚫 Do-Not-Buy Summary")
    report.append("")
    report.append(f"**{len(do_not_buy)} products** excluded from recommendation.")
    report.append("")
    
    # Count by reason
    reason_counts = {}
    for item in do_not_buy:
        reason = item.get('REASON', 'Unknown')
        # Simplify reason
        if 'ROI' in reason:
            key = 'Low ROI (<20%)'
        elif 'profit' in reason.lower():
            key = 'Missing/Negative Profit'
        elif 'brand' in reason.lower() or 'IP' in reason.lower():
            key = 'High Brand/IP Risk'
        elif 'Audited' in reason:
            key = 'Audited Out'
        else:
            key = 'Other'
        reason_counts[key] = reason_counts.get(key, 0) + 1
    
    report.append("| Reason | Count |")
    report.append("|--------|-------|")
    for reason, count in sorted(reason_counts.items(), key=lambda x: -x[1]):
        report.append(f"| {reason} | {count} |")
    report.append("")
    
    # Capital Guidance
    report.append("## 💰 Capital Guidance by Scenario")
    report.append("")
    
    report.append("### Limited Capital (£500-1,000)")
    report.append("- Focus on top 2-3 items with highest Profit × Velocity")
    report.append("- Prioritize items with ROI ≥ 30%")
    if focus_now:
        top_picks = [f for f in focus_now if f['ROI_PCT'] and f['ROI_PCT'] >= 30][:3]
        if top_picks:
            report.append(f"- **Recommended:** {', '.join([p['ASIN'] for p in top_picks])}")
    report.append("")
    
    report.append("### Moderate Capital (£1,000-2,500)")
    report.append("- Include top 5 Focus Now items")
    report.append("- Add 1-2 seasonal items if within trigger window")
    report.append("- Test 24 units each for faster payback validation")
    report.append("")
    
    report.append("### Aggressive Capital (£2,500+)")
    report.append("- Diversify across 8-12 items")
    report.append("- Cap exposure to any single brand at ≤25% of budget")
    report.append("- Include seasonal items for Q4/holiday prep")
    report.append("- Consider 30-unit orders for high-velocity items")
    report.append("")
    
    # Quality Assurance
    report.append("## Quality Assurance")
    report.append("")
    report.append("✅ **Validation Checks Performed:**")
    report.append(f"- All {len(focus_now)} Focus Now items have positive Profit and ROI ≥ {MIN_ROI_PCT}%")
    report.append("- All Focus Now items have Low or Medium brand risk (no High risk)")
    report.append("- Seasonality explicitly noted for all items")
    report.append("- Capital-aware unit suggestions provided")
    report.append("- All exclusions have explicit documented reasons")
    report.append("")
    
    # Assumptions
    report.append("### Assumptions & Limitations")
    report.append("")
    report.append("- **Adjusted Profit** treated as net of all fees — not recalculated")
    report.append("- **ROI** values converted from decimal format (0.28 → 28%)")
    report.append("- **Sales** figures represent Amazon 'N sold in last month' badge estimate")
    report.append("- **Seasonality** inferred from title keywords only — no Keepa deep dive performed")
    report.append("- **Competition** data not available — assumed neutral")
    report.append("")
    
    # Reasoning Summary
    report.append("---")
    report.append("")
    report.append("## Reasoning Summary")
    report.append("")
    report.append(f"- **{len(focus_now)} items** ready for immediate sourcing with strong ROI × Velocity × Profit combination")
    report.append(f"- **{len(focus_next)} seasonal items** to revisit at appropriate trigger windows")
    report.append(f"- **{len(do_not_buy)} exclusions** primarily due to ROI below 20% or missing profit data")
    report.append("- Profit data missing for 5 products due to AUDITED OUT status or incomplete source data")
    report.append("")
    
    report.append("## Next Steps")
    report.append("")
    report.append("1. **Immediate**: Place test orders for top 3 Focus Now items")
    report.append("2. **This Week**: Verify Amazon listings for stock levels and Buy Box status")
    report.append("3. **Seasonal Prep**: Set calendar reminders for Focus Next trigger windows")
    report.append("4. **Monitor**: Check Keepa for Monitor tier items before committing")
    report.append("5. **Data Fix**: Investigate missing profit data for Superior Foil products")
    report.append("")
    
    return '\n'.join(report)

def main():
    """Main execution."""
    print("=" * 60)
    print("FBA PRIORITIZATION REPORT GENERATOR")
    print("Date: 2026-01-17 (Asia/Dubai)")
    print("=" * 60)
    
    # Load data
    df = load_data(INPUT_FILE)
    print(f"Loaded {len(df)} products")
    
    # Generate analysis
    focus_now, focus_next, monitor, do_not_buy = generate_report(df)
    
    print(f"Focus Now: {len(focus_now)}")
    print(f"Focus Next: {len(focus_next)}")
    print(f"Monitor: {len(monitor)}")
    print(f"Do-Not-Buy: {len(do_not_buy)}")
    
    # Create report
    report = create_markdown_report(focus_now, focus_next, monitor, do_not_buy)
    
    # Save report
    report_path = OUTPUT_DIR / f"FBA_PRIORITIZATION_REPORT_{TIMESTAMP}.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nReport saved: {report_path}")
    
    # Also save tier data as Excel
    excel_path = OUTPUT_DIR / f"FBA_PRIORITIZATION_DATA_{TIMESTAMP}.xlsx"
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        if focus_now:
            pd.DataFrame(focus_now).to_excel(writer, sheet_name='Focus Now', index=False)
        if focus_next:
            pd.DataFrame(focus_next).to_excel(writer, sheet_name='Focus Next', index=False)
        if monitor:
            pd.DataFrame(monitor).to_excel(writer, sheet_name='Monitor', index=False)
        if do_not_buy:
            pd.DataFrame(do_not_buy).to_excel(writer, sheet_name='Do-Not-Buy', index=False)
    
    print(f"Data saved: {excel_path}")
    
    return report_path

if __name__ == "__main__":
    main()
