# EFGHOUSEWARES Stale Data Analysis Report

## Executive Summary
- **Report Date**: 20260108 (101 days old - CRITICALLY)
- **Source File**: fba_financial_report_MERGED_20260108_010448.csv
- **Analysis Date**: 20260419_095834

## Phase Results

### Phase 1: Data Loading
- Total rows: 21356
- Exclusion set: 3205 ASINs, 2826 URLs

### Phase 2: Data Cleansing
- Input: 21356
- Removed: 682
- Output: 20674
- Cleansing steps:
  - Superior brand: 25 removed
  - Price plausibility: 589 removed  
  - Luxury false match: 68 removed
  - Unit qty mismatch: 1896 flagged

### Phase 3: Bucket Classification
| Bucket | Count | Description |
|--------|-------|-------------|
| A | 2810 | Proven Demand (Sales>0, Profit>0) |
| B | 5279 | Opportunity (Profit>0, Sales=0) |
| C | 1963 | Margin Flip (Sales>50, Profit -3 to 0.5) |

### Phase 4: Category Sandbox Targets
Top 10 categories recommended for re-scrape:
1. **christmas-musical-snow-globe-christmas-santa-123403** - 1 products, weighted value: £12113
2. **festive-magic-led-lights-500-clear-cable-whit-102527** - 1 products, weighted value: £11291
3. **addis-long-handle-dustpan-brush** - 1 products, weighted value: £5460
4. **apollo-wood-nail-brush-pk24-4-2-23** - 1 products, weighted value: £5348
5. **onya-dinner-set-16-pieces-4-mugs-4-bowls-4-dinner-plates-4-side-plates-seize-the-day-poppy-118033** - 1 products, weighted value: £4883
6. **bauer-straightener-brush-38820-black-21-04** - 1 products, weighted value: £4555
7. **kitchen-king-aluminium-pot-glorious-set-5pc-115288** - 1 products, weighted value: £4006
8. **bbq-tongs-108059** - 1 products, weighted value: £3969
9. **sabichi-kitchen-digital-scale-red-5kg** - 1 products, weighted value: £3969
10. **geepas-rechargeable-portable-blender-black-330ml-gsb44111uk-bk-112787** - 1 products, weighted value: £3385

### Phase 5: Final Product List
- Total products: 6997
- After ASIN exclusion: 6997
- After URL exclusion: 6997  
- After category exclusion: 6997

### Excluded Categories (10)
The following categories were excluded from recommendations:
1. disposable-tableware
2. diy---tools
3. bin-bag-carrier-bag-paper-bag
4. candles-air-fresheners-diffuse
5. air-fresheners
6. bathroom---cosmetics---beauty
7. amtech-tools
8. home-baking
9. light-bulbs
10. glass-tableware

## Verification Checks
- [x] Bucket column in CSV: YES
- [x] Unit_Qty_Flag column: YES  
- [x] Overlap with exclusion ASINs: 0 (target: 0)
- [x] Excluded categories in recommendations: 0 (target: 0)
- [x] Product count matches: YES

## Output Files
| File | Path |
|------|------|
| Product List JSON | C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\PRODUCTS_LISTS\product_list_efghousewares-co-uk_20260419_095834.json |
| Master CSV | C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\PRODUCTS_LISTS\efghousewares-co-uk_stale_analysis_20260419_095834\csvs\efghousewares-co-uk_VALIDATED_master_20260419_095834.csv |
| Bucket A CSV | C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\PRODUCTS_LISTS\efghousewares-co-uk_stale_analysis_20260419_095834\csvs\efghousewares-co-uk_VALIDATED_bucketA_20260419_095834.csv |
| Bucket BC CSV | C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\PRODUCTS_LISTS\efghousewares-co-uk_stale_analysis_20260419_095834\csvs\efghousewares-co-uk_VALIDATED_bucketBC_20260419_095834.csv |
| Category Targets | C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\PRODUCTS_LISTS\efghousewares-co-uk_stale_analysis_20260419_095834\categories\efghousewares-co-uk_category_sandbox_targets_20260419_095834.json |

## Recommendations
1. Run sandbox analysis for top 5 category targets
2. Validate top Bucket A products via Amazon listing checks
3. Review Bucket B products for untapped opportunities
4. Monitor Bucket C products for margin flip potential
