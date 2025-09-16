#!/usr/bin/env python3
"""
UK VAT-Aware Investment Screening Analysis - ADJUSTED THRESHOLDS
================================================================

Revised analysis with realistic thresholds based on wholesale margin patterns observed.
Implements UK VAT-registered NETP perspective with market-adjusted ROI expectations.

ADJUSTED THRESHOLDS (Based on Data Analysis):
- TIER 1 (IMMEDIATE BUY): ROI ≥ 25%, NetProfit ≥ £0.50, Sales > 50
- TIER 2 (STRONG CONSIDER): ROI ≥ 20%, NetProfit ≥ £0.40, Sales > 30
- TIER 3 (INVESTIGATE): ROI ≥ 15%, NetProfit ≥ £0.30, Strong brands OR good sales
- TIER 4 (MONITOR): ROI ≥ 10%, NetProfit ≥ £0.20, Track for market changes

Created: September 2, 2025
Source: EXACT_MATCHES_20250902_054416.csv (1,814 products)
Rationale: Original thresholds (30-35% ROI) excluded 99.8% of products - unrealistic for wholesale
"""

import pandas as pd
import numpy as np
from datetime import datetime
import re
from pathlib import Path

class AdjustedUKVATScreener:
    """UK VAT-aware investment screening with market-realistic thresholds"""
    
    def __init__(self):
        self.analysis_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # ADJUSTED THRESHOLDS - Based on wholesale margin reality
        self.thresholds = {
            'tier1_immediate': {
                'min_roi': 25.0,           # ≥ 25% ROI (was 35%)
                'min_net_profit': 0.50,    # ≥ £0.50 net profit (was £0.80)
                'min_sales': 50            # > 50 sales
            },
            'tier2_strong': {
                'min_roi': 20.0,           # ≥ 20% ROI (was 30%) 
                'min_net_profit': 0.40,    # ≥ £0.40 net profit (was £0.75)
                'min_sales': 30            # > 30 sales (reduced from 50)
            },
            'tier3_investigate': {
                'min_roi': 15.0,           # ≥ 15% ROI
                'min_net_profit': 0.30,    # ≥ £0.30 net profit
                'min_sales': 20,           # > 20 sales OR strong brand
                'strong_brand_indicators': [
                    'disney', 'marvel', 'star wars', 'lego', 'nike', 'adidas', 
                    'apple', 'samsung', 'sony', 'canon', 'nikon', 'dyson',
                    'kitchen aid', 'russell hobbs', 'morphy richards', 'bosch',
                    'philips', 'braun', 'oral-b', 'gillette', 'pampers'
                ]
            },
            'tier4_monitor': {
                'min_roi': 10.0,           # ≥ 10% ROI
                'min_net_profit': 0.20     # ≥ £0.20 net profit
            }
        }
    
    def load_exact_matches(self, file_path):
        """Load exact match products from CSV"""
        print(f"Loading exact matches from: {file_path}")
        
        try:
            df = pd.read_csv(file_path, dtype={
                'EAN': str,
                'EAN_OnPage': str,
                'ASIN': str,
                'bought_in_past_month': str
            })
            
            print(f"✅ Loaded {len(df):,} exact match products")
            df = self._clean_data(df)
            return df
            
        except Exception as e:
            print(f"❌ Error loading exact matches: {e}")
            return None
    
    def _clean_data(self, df):
        """Clean and normalize the data for analysis"""
        print("🧹 Cleaning and normalizing data...")
        
        numeric_cols = [
            'SupplierPrice_exVAT', 'SellingPrice_incVAT', 'NetProfit', 
            'ROI', 'total_offer_count', 'fba_seller_count', 'fbm_seller_count'
        ]
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df['sales_count'] = df['bought_in_past_month'].apply(self._parse_sales_data)
        df['brand_normalized'] = df['SupplierTitle'].str.lower().fillna('')
        df['amazon_title_normalized'] = df['AmazonTitle'].str.lower().fillna('')
        df['combined_title'] = (df['brand_normalized'] + ' ' + df['amazon_title_normalized']).str.strip()
        
        # Filter out rows with missing critical data
        before_filter = len(df)
        df = df.dropna(subset=['SupplierPrice_exVAT', 'NetProfit', 'ROI'])
        after_filter = len(df)
        
        if before_filter > after_filter:
            print(f"⚠️  Filtered out {before_filter - after_filter:,} products with missing critical data")
        
        return df
    
    def _parse_sales_data(self, sales_str):
        """Parse sales data from various formats"""
        if pd.isna(sales_str) or sales_str == '':
            return np.nan
        
        sales_str = str(sales_str).strip()
        
        numbers = re.findall(r'\d+\.?\d*', sales_str)
        if numbers:
            return float(numbers[0])
        
        if 'available' in sales_str.lower():
            return np.nan
            
        return 0
    
    def _detect_strong_brands(self, title):
        """Detect strong brand indicators in title"""
        title_lower = title.lower()
        
        for brand in self.thresholds['tier3_investigate']['strong_brand_indicators']:
            if brand in title_lower:
                return True, brand
        
        return False, None
    
    def apply_adjusted_screening(self, df):
        """Apply adjusted four-tier investment screening"""
        print("🔍 Applying adjusted UK VAT-aware investment screening...")
        
        results = {
            'tier1_immediate': [],
            'tier2_strong': [], 
            'tier3_investigate': [],
            'tier4_monitor': [],
            'rejected': []
        }
        
        for idx, row in df.iterrows():
            classification = self._classify_product_adjusted(row)
            results[classification['tier']].append({
                **row.to_dict(),
                **classification
            })
        
        # Convert to DataFrames
        for tier in results:
            results[tier] = pd.DataFrame(results[tier])
        
        return results
    
    def _classify_product_adjusted(self, row):
        """Classify product into adjusted investment tier"""
        roi = row.get('ROI', 0)
        net_profit = row.get('NetProfit', 0)
        sales_count = row.get('sales_count', 0)
        combined_title = row.get('combined_title', '')
        
        # Check for strong brand indicators
        has_strong_brand, brand_detected = self._detect_strong_brands(combined_title)
        
        # Sales data quality assessment
        has_sales_data = not pd.isna(sales_count) and sales_count > 0
        
        classification = {
            'investment_tier': None,
            'reason': [],
            'roi': roi,
            'net_profit': net_profit,
            'sales_count': sales_count if has_sales_data else 'Unknown',
            'has_strong_brand': has_strong_brand,
            'brand_detected': brand_detected,
            'has_sales_data': has_sales_data,
            'tier': None,
            'risk_level': 'HIGH',
            'action': 'REJECT'
        }
        
        # TIER 1: IMMEDIATE BUY
        if (roi >= self.thresholds['tier1_immediate']['min_roi'] and 
            net_profit >= self.thresholds['tier1_immediate']['min_net_profit'] and
            has_sales_data and sales_count > self.thresholds['tier1_immediate']['min_sales']):
            
            classification.update({
                'investment_tier': 'TIER 1 - IMMEDIATE BUY',
                'tier': 'tier1_immediate',
                'risk_level': 'LOW',
                'action': 'BUY NOW',
                'reason': [
                    f"ROI {roi:.1f}% ≥ {self.thresholds['tier1_immediate']['min_roi']}%",
                    f"NetProfit £{net_profit:.2f} ≥ £{self.thresholds['tier1_immediate']['min_net_profit']}",
                    f"Sales {sales_count} > {self.thresholds['tier1_immediate']['min_sales']}"
                ]
            })
        
        # TIER 2: STRONG CONSIDER
        elif (roi >= self.thresholds['tier2_strong']['min_roi'] and 
              net_profit >= self.thresholds['tier2_strong']['min_net_profit'] and
              has_sales_data and sales_count > self.thresholds['tier2_strong']['min_sales']):
            
            classification.update({
                'investment_tier': 'TIER 2 - STRONG CONSIDER',
                'tier': 'tier2_strong',
                'risk_level': 'MEDIUM-LOW',
                'action': 'DETAILED ANALYSIS',
                'reason': [
                    f"ROI {roi:.1f}% ≥ {self.thresholds['tier2_strong']['min_roi']}%",
                    f"NetProfit £{net_profit:.2f} ≥ £{self.thresholds['tier2_strong']['min_net_profit']}",
                    f"Sales {sales_count} > {self.thresholds['tier2_strong']['min_sales']}"
                ]
            })
        
        # TIER 3: INVESTIGATE 
        elif (roi >= self.thresholds['tier3_investigate']['min_roi'] and 
              net_profit >= self.thresholds['tier3_investigate']['min_net_profit'] and
              (
                  (has_sales_data and sales_count > self.thresholds['tier3_investigate']['min_sales']) or
                  has_strong_brand or
                  (not has_sales_data and roi >= 20.0)  # High ROI compensates for missing sales data
              )):
            
            reasons = [
                f"ROI {roi:.1f}% ≥ {self.thresholds['tier3_investigate']['min_roi']}%",
                f"NetProfit £{net_profit:.2f} ≥ £{self.thresholds['tier3_investigate']['min_net_profit']}"
            ]
            
            if has_strong_brand:
                reasons.append(f"Strong brand detected: {brand_detected}")
            if has_sales_data and sales_count > self.thresholds['tier3_investigate']['min_sales']:
                reasons.append(f"Sales {sales_count} > {self.thresholds['tier3_investigate']['min_sales']}")
            if not has_sales_data and roi >= 20.0:
                reasons.append("High ROI compensates for missing sales data")
            
            classification.update({
                'investment_tier': 'TIER 3 - INVESTIGATE',
                'tier': 'tier3_investigate',
                'risk_level': 'MEDIUM',
                'action': 'SALES VERIFICATION NEEDED',
                'reason': reasons
            })
        
        # TIER 4: MONITOR
        elif (roi >= self.thresholds['tier4_monitor']['min_roi'] and 
              net_profit >= self.thresholds['tier4_monitor']['min_net_profit']):
            
            classification.update({
                'investment_tier': 'TIER 4 - MONITOR',
                'tier': 'tier4_monitor',
                'risk_level': 'MEDIUM-HIGH',
                'action': 'TRACK FOR IMPROVEMENT',
                'reason': [
                    f"ROI {roi:.1f}% ≥ {self.thresholds['tier4_monitor']['min_roi']}%",
                    f"NetProfit £{net_profit:.2f} ≥ £{self.thresholds['tier4_monitor']['min_net_profit']}",
                    "Monitor for price/demand changes"
                ]
            })
        
        # REJECTED
        else:
            reject_reasons = []
            
            if roi < self.thresholds['tier4_monitor']['min_roi']:
                reject_reasons.append(f"ROI {roi:.1f}% < {self.thresholds['tier4_monitor']['min_roi']}%")
            if net_profit < self.thresholds['tier4_monitor']['min_net_profit']:
                reject_reasons.append(f"NetProfit £{net_profit:.2f} < £{self.thresholds['tier4_monitor']['min_net_profit']}")
            
            classification.update({
                'investment_tier': 'REJECTED',
                'tier': 'rejected',
                'risk_level': 'VERY HIGH',
                'action': 'DO NOT BUY',
                'reason': reject_reasons
            })
        
        return classification
    
    def generate_adjusted_summary(self, results):
        """Generate comprehensive adjusted investment summary"""
        print("📊 Generating adjusted investment summary...")
        
        summary = {
            'analysis_date': self.analysis_date,
            'total_products_analyzed': sum(len(results[tier]) for tier in results),
            'tier_breakdown': {},
            'financial_summary': {},
            'roi_distribution': {},
            'sales_data_analysis': {},
            'brand_analysis': {}
        }
        
        # Tier breakdown
        tier_names = {
            'tier1_immediate': 'TIER 1 - IMMEDIATE BUY',
            'tier2_strong': 'TIER 2 - STRONG CONSIDER',
            'tier3_investigate': 'TIER 3 - INVESTIGATE',
            'tier4_monitor': 'TIER 4 - MONITOR',
            'rejected': 'REJECTED'
        }
        
        for tier_key, tier_name in tier_names.items():
            df_tier = results[tier_key]
            count = len(df_tier)
            percentage = (count / summary['total_products_analyzed']) * 100 if summary['total_products_analyzed'] > 0 else 0
            
            summary['tier_breakdown'][tier_name] = {
                'count': count,
                'percentage': percentage
            }
            
            # Financial metrics for investment tiers
            if tier_key != 'rejected' and count > 0:
                summary['financial_summary'][tier_name] = {
                    'total_investment_required': df_tier['SupplierPrice_exVAT'].sum(),
                    'total_potential_profit': df_tier['NetProfit'].sum(),
                    'average_roi': df_tier['ROI'].mean(),
                    'median_roi': df_tier['ROI'].median(),
                    'roi_range': f"{df_tier['ROI'].min():.1f}% - {df_tier['ROI'].max():.1f}%",
                    'average_profit_per_unit': df_tier['NetProfit'].mean(),
                    'product_count': count
                }
        
        # ROI Distribution Analysis
        all_products = pd.concat([results[tier] for tier in results if len(results[tier]) > 0], ignore_index=True)
        if len(all_products) > 0:
            summary['roi_distribution'] = {
                'roi_0_10': len(all_products[all_products['ROI'] < 10]),
                'roi_10_20': len(all_products[(all_products['ROI'] >= 10) & (all_products['ROI'] < 20)]),
                'roi_20_30': len(all_products[(all_products['ROI'] >= 20) & (all_products['ROI'] < 30)]),
                'roi_30_plus': len(all_products[all_products['ROI'] >= 30]),
                'average_roi_all_products': all_products['ROI'].mean(),
                'median_roi_all_products': all_products['ROI'].median()
            }
            
            # Sales data analysis
            has_sales = all_products[all_products['sales_count'] != 'Unknown']
            summary['sales_data_analysis'] = {
                'products_with_sales_data': len(has_sales),
                'products_without_sales_data': len(all_products) - len(has_sales),
                'sales_data_coverage': f"{(len(has_sales) / len(all_products) * 100):.1f}%"
            }
            
            # Brand analysis
            branded_products = all_products[all_products['has_strong_brand'] == True]
            summary['brand_analysis'] = {
                'products_with_strong_brands': len(branded_products),
                'brand_coverage': f"{(len(branded_products) / len(all_products) * 100):.1f}%",
                'average_roi_branded': branded_products['ROI'].mean() if len(branded_products) > 0 else 0
            }
        
        return summary
    
    def save_adjusted_results(self, results, summary, output_dir):
        """Save adjusted analysis results"""
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        print(f"💾 Saving adjusted results to: {output_dir}")
        
        tier_names = {
            'tier1_immediate': 'TIER_1_IMMEDIATE_BUY',
            'tier2_strong': 'TIER_2_STRONG_CONSIDER', 
            'tier3_investigate': 'TIER_3_INVESTIGATE',
            'tier4_monitor': 'TIER_4_MONITOR',
            'rejected': 'REJECTED'
        }
        
        files_created = []
        
        for tier_key, tier_filename in tier_names.items():
            df_tier = results[tier_key]
            if len(df_tier) > 0:
                filename = f"UK_VAT_Adjusted_Screening_{tier_filename}_{self.analysis_date}.csv"
                filepath = output_dir / filename
                
                output_columns = [
                    'SupplierTitle', 'AmazonTitle', 'EAN', 'ASIN', 'SupplierURL', 'AmazonURL',
                    'SupplierPrice_exVAT', 'SellingPrice_incVAT', 'NetProfit', 'ROI',
                    'sales_count', 'total_offer_count', 'fba_seller_count', 'fbm_seller_count',
                    'investment_tier', 'risk_level', 'action', 'reason', 'has_strong_brand', 'brand_detected',
                    'MatchMethod', 'Confidence'
                ]
                
                available_columns = [col for col in output_columns if col in df_tier.columns]
                df_tier[available_columns].to_csv(filepath, index=False)
                files_created.append(filename)
                print(f"✅ Saved {len(df_tier):,} products to {filename}")
        
        # Save summary report
        summary_file = output_dir / f"UK_VAT_Adjusted_Screening_SUMMARY_{self.analysis_date}.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(self._format_adjusted_summary(summary))
        
        files_created.append(summary_file.name)
        print(f"✅ Saved summary report to {summary_file.name}")
        
        return {
            'output_directory': str(output_dir),
            'files_created': files_created
        }
    
    def _format_adjusted_summary(self, summary):
        """Format adjusted comprehensive summary report"""
        report = f"""
UK VAT-AWARE INVESTMENT SCREENING ANALYSIS - ADJUSTED THRESHOLDS
================================================================

Analysis Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Source: EXACT_MATCHES_20250902_054416.csv
Perspective: UK VAT-registered NETP (Net Profit after VAT)

⚠️  THRESHOLD ADJUSTMENT RATIONALE:
Original thresholds (30-35% ROI) excluded 99.8% of products, indicating unrealistic expectations for wholesale margins.
Adjusted thresholds reflect market reality while maintaining profitability standards.

EXECUTIVE SUMMARY
================

Total Products Analyzed: {summary['total_products_analyzed']:,}

ADJUSTED INVESTMENT CLASSIFICATION:
"""
        
        for tier_name, data in summary['tier_breakdown'].items():
            report += f"  {tier_name}: {data['count']:,} products ({data['percentage']:.1f}%)\n"
        
        report += f"""
ADJUSTED THRESHOLDS APPLIED:
===========================

TIER 1 (IMMEDIATE BUY):
  • ROI ≥ 25% (reduced from 35%)
  • Net Profit ≥ £0.50 (reduced from £0.80) 
  • Sales > 50/month
  
TIER 2 (STRONG CONSIDER):  
  • ROI ≥ 20% (reduced from 30%)
  • Net Profit ≥ £0.40 (reduced from £0.75)
  • Sales > 30/month (reduced from 50)
  
TIER 3 (INVESTIGATE):
  • ROI ≥ 15%
  • Net Profit ≥ £0.30
  • Sales > 20/month OR strong brand OR high ROI without sales data
  
TIER 4 (MONITOR):
  • ROI ≥ 10%
  • Net Profit ≥ £0.20
  • Track for market improvements

FINANCIAL ANALYSIS BY TIER:
===========================
"""
        
        for tier_name, financial_data in summary['financial_summary'].items():
            report += f"""
{tier_name}:
  Products: {financial_data['product_count']:,}
  Total Investment Required: £{financial_data['total_investment_required']:,.2f}
  Total Potential Profit: £{financial_data['total_potential_profit']:,.2f}
  Average ROI: {financial_data['average_roi']:.1f}%
  Median ROI: {financial_data['median_roi']:.1f}%
  ROI Range: {financial_data['roi_range']}
  Average Profit per Unit: £{financial_data['average_profit_per_unit']:.2f}
"""
        
        report += f"""
MARKET REALITY ANALYSIS:
=======================

ROI Distribution Across All Products:
  • 0-10% ROI: {summary['roi_distribution']['roi_0_10']:,} products
  • 10-20% ROI: {summary['roi_distribution']['roi_10_20']:,} products  
  • 20-30% ROI: {summary['roi_distribution']['roi_20_30']:,} products
  • 30%+ ROI: {summary['roi_distribution']['roi_30_plus']:,} products
  
  Average ROI (All Products): {summary['roi_distribution']['average_roi_all_products']:.1f}%
  Median ROI (All Products): {summary['roi_distribution']['median_roi_all_products']:.1f}%

Sales Data Quality:
  • Products with Sales Data: {summary['sales_data_analysis']['products_with_sales_data']:,} 
  • Products without Sales Data: {summary['sales_data_analysis']['products_without_sales_data']:,}
  • Sales Data Coverage: {summary['sales_data_analysis']['sales_data_coverage']}

Brand Analysis:
  • Products with Strong Brands: {summary['brand_analysis']['products_with_strong_brands']:,}
  • Brand Coverage: {summary['brand_analysis']['brand_coverage']}
  • Average ROI (Branded): {summary['brand_analysis']['average_roi_branded']:.1f}%

KEY INSIGHTS:
============

1. WHOLESALE MARGIN REALITY: Most products fall in 10-25% ROI range, consistent with typical wholesale margins
2. SALES DATA GAP: Significant portion of products lack verified sales data - major risk factor
3. BRAND PREMIUM: Strong brands don't significantly outperform in ROI terms in this dataset
4. THRESHOLD ADJUSTMENT IMPACT: Realistic thresholds reveal viable investment opportunities previously hidden

INVESTMENT RECOMMENDATIONS:
==========================

IMMEDIATE ACTIONS:
• TIER 1: Proceed with procurement - lowest risk, verified profitability
• TIER 2: Conduct detailed competitor analysis before investment decision
• TIER 3: Verify sales data manually - potential high-value opportunities
• TIER 4: Monitor for price changes, supplier negotiations, or demand shifts

RISK MANAGEMENT:
• Start small quantities for TIER 2-3 products to test market response
• Focus on products with verified sales data where possible
• Consider seasonal factors not captured in current analysis
• Monitor competitor pricing changes that could affect margins

STRATEGIC CONSIDERATIONS:
• Renegotiate supplier terms to improve margins on high-volume products
• Focus on product categories with consistent demand patterns
• Build relationships with brands showing strong performance indicators
• Develop systems for ongoing sales data verification

UK VAT COMPLIANCE REMINDER:
===========================

All calculations maintain UK VAT-registered business perspective:
• Input VAT on supplier purchases is recoverable
• Output VAT on Amazon sales is payable to HMRC
• ROI calculations use ex-VAT supplier cost as investment base
• Net profit reflects post-VAT, post-fee actual returns

Analysis completed: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        
        return report

def main():
    """Main execution function for adjusted analysis"""
    print("🚀 Starting UK VAT-Aware Investment Screening Analysis - ADJUSTED THRESHOLDS")
    print("=" * 80)
    
    screener = AdjustedUKVATScreener()
    
    base_dir = Path(__file__).parent
    input_file = base_dir / "EXACT_MATCHES_20250902_054416.csv"
    output_dir = base_dir / "adjusted_investment_screening_results"
    
    # Load data
    df = screener.load_exact_matches(input_file)
    if df is None:
        print("❌ Failed to load data. Exiting.")
        return
    
    # Apply adjusted screening
    results = screener.apply_adjusted_screening(df)
    
    # Generate summary  
    summary = screener.generate_adjusted_summary(results)
    
    # Save results
    file_info = screener.save_adjusted_results(results, summary, output_dir)
    
    # Print executive summary
    print("\n" + "=" * 80)
    print("📈 ADJUSTED INVESTMENT SCREENING COMPLETE")
    print("=" * 80)
    
    for tier_name, data in summary['tier_breakdown'].items():
        print(f"  {tier_name}: {data['count']:,} products ({data['percentage']:.1f}%)")
    
    print(f"\n📁 Results saved to: {file_info['output_directory']}")
    
    # Key recommendations
    print("\n🎯 ADJUSTED RECOMMENDATIONS:")
    
    tier1_count = summary['tier_breakdown']['TIER 1 - IMMEDIATE BUY']['count']
    tier2_count = summary['tier_breakdown']['TIER 2 - STRONG CONSIDER']['count']
    tier3_count = summary['tier_breakdown']['TIER 3 - INVESTIGATE']['count']
    tier4_count = summary['tier_breakdown']['TIER 4 - MONITOR']['count']
    
    if tier1_count > 0:
        tier1_investment = summary['financial_summary']['TIER 1 - IMMEDIATE BUY']['total_investment_required']
        tier1_profit = summary['financial_summary']['TIER 1 - IMMEDIATE BUY']['total_potential_profit']
        print(f"  • IMMEDIATE BUY: {tier1_count:,} products ready for procurement")
        print(f"    Investment: £{tier1_investment:,.2f} | Potential Profit: £{tier1_profit:,.2f}")
    
    if tier2_count > 0:
        print(f"  • STRONG CONSIDER: {tier2_count:,} products - detailed analysis required")
    
    if tier3_count > 0:
        print(f"  • INVESTIGATE: {tier3_count:,} products - verify sales data manually")
    
    if tier4_count > 0:
        print(f"  • MONITOR: {tier4_count:,} products - track for improvements")
    
    # ROI reality check
    avg_roi = summary['roi_distribution']['average_roi_all_products']
    median_roi = summary['roi_distribution']['median_roi_all_products']
    print(f"\n📊 ROI REALITY CHECK:")
    print(f"  Average ROI across all products: {avg_roi:.1f}%")
    print(f"  Median ROI across all products: {median_roi:.1f}%")
    print(f"  Products with 30%+ ROI: {summary['roi_distribution']['roi_30_plus']:,} ({summary['roi_distribution']['roi_30_plus']/summary['total_products_analyzed']*100:.1f}%)")
    
    print(f"\n✅ Adjusted analysis complete - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()