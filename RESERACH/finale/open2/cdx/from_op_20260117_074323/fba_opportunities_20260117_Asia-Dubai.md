## Overview
As of **2026-01-17 (Asia/Dubai)**, this report triages **18 shortlisted rows** from `/mnt/data/shortlist.csv` into action buckets for a sourcing operator. Decisions use the file’s `NetProfit` (already fee-inclusive), `ROI_calc` (ROI%), and the `Sales` badge (last-month demand proxy), with `BrandRisk`/`Pack Verdict` treated as risk flags. `/mnt/data/backlog.csv` is **Not provided**; Keepa/SellerAmp were **Not checked** here, so verification steps are specified per item.

## Decision logic
- Hard floor: positive `NetProfit` and practical ROI (the exclusion list shows many were dropped for ~<20% ROI).
- Primary signals: `NetProfit` (cash/unit), `ROI_calc` (capital efficiency), `Sales` + `Velocity` (demand).
- Risk treatment: `BrandRisk=Medium`, non-`1:1 Match` packs, missing `Sales`, or much-lower `Adjusted Profit` => verify first.
- Exclusion context (`/mnt/data/do_not_buy.csv`): most exclusions are low ROI; 2 were flagged "High Brand Risk".

## Focus recommendation (top 5-8 items)
| ASIN       | Title (short)                                           | Why now                                   | Key risk                         | Next action |
|:-----------|:--------------------------------------------------------|:------------------------------------------|:---------------------------------|:-----------|
| B07WDRQ4J7 | Air Wick Reed Diffuser (Mulled Wine, 5x30ml)             | GBP 16.55/unit, 123.2% ROI; 200 sold/mo   | Pack/variation + hazmat check    | Confirm the listing is 5x30ml; SellerAmp restrictions; Keepa 90d price + offer count |
| B0DJDH23JW | Superior Foil Trays 9x9 (10-pack)                       | GBP 2.13/unit, 58.2% ROI; 700 sold/mo     | Pack count/variation correctness | Confirm "10-pack" is correct; Keepa 90d offers/price; check size-tier assumptions |
| B005XKFN0O | Eveready T8 Tube Light 4ft 36W (3500k)                  | GBP 8.00/unit, 267.6% ROI; 50 sold/mo     | Fragile/oversize + BB stability  | Keepa 90d price stability; check Amazon on listing/competition; confirm exact spec |
| B01IFIJ91Y | Mason Cash Mixing Bowl 29cm / 4L                        | GBP 5.11/unit, 66.7% ROI; 200 sold/mo     | BrandRisk=Medium + breakage risk | SellerAmp restrictions/gating; Keepa 90d; confirm packaging/fragile handling |
| B09KCLYC1D | Pan Aroma Candle 85g (Salted Caramel)                   | GBP 2.82/unit, 324.1% ROI; 50 sold/mo     | Commodity pricing pressure       | Keepa 90d price + offer count; confirm variation/85g; check hazmat status |
| B09KCMWXQX | Pan Aroma Candle 85g (Red Berry)                        | GBP 2.82/unit, 324.1% ROI; 50 sold/mo     | Adjusted profit lower (GBP 1.49) | Re-verify profit on current price; Keepa 90d; confirm variation/85g |
| 6040418214 | Fragrant Cloud Rose EDP 100ml                           | GBP 1.24/unit, 77.0% ROI; 100 sold/mo     | Hazmat/flammable + restrictions  | SellerAmp restrictions/hazmat; Keepa 90d; confirm exact 100ml variant |
| B07GZGXQYG | Superior Foil Containers w/ Lids (9x13)                 | GBP 2.50/unit, 65.8% ROI; sales missing   | Missing Sales + pack fields      | Re-check "sold last month" badge + pack count; Keepa 90d; validate variation |

## Per-item triage (all 18)
| ASIN       | Title | ROI | Profit | Sales | Priority bucket | Rationale | Next checks |
|:-----------|:------|:----|:-------|:------|:----------------|:----------|:-----------|
| B07WDRQ4J7 | Air Wick Reed Diffuser (Mulled Wine, 5x30ml) | 123.2% | GBP 16.55 | 200 | Focus Now | - Strong cash/unit (GBP 16.55) at 123.2% ROI<br>- Demand signal: 200 sold last month (High)<br>- Pack shows 5x1 vs 1x5: variation accuracy is critical | Confirm exact 5x30ml listing; SellerAmp restrictions/hazmat; Keepa 90d price + offer count |
| B0DJDH23JW | Superior Foil Trays 9x9 (10-pack) | 58.2% | GBP 2.13 | 700 | Focus Now | - GBP 2.13 profit/unit at 58.2% ROI<br>- Demand signal: 700 sold last month (High)<br>- Pack shows 1x10 vs 10x1: confirm pack count/variation | Confirm pack/variation; Keepa 90d offers/price; confirm size-tier/oversize risk |
| B005XKFN0O | Eveready T8 Tube Light 4ft 36W (3500k) | 267.6% | GBP 8.00 | 50 | Focus After Verification | - Excellent ROI (267.6%) and GBP 8.00 profit/unit<br>- Demand signal: 50 sold last month (Medium)<br>- Electrical/fragile risk: avoid surprises on returns/competition | Keepa 90d price stability; check Amazon-on-listing + offer count; confirm exact spec/variation |
| B09KCMWXQX | Pan Aroma Candle 85g (Red Berry) | 324.1% | GBP 2.82 | 50 | Focus After Verification | - Very high ROI (324.1%) with GBP 2.82 profit/unit<br>- Demand signal: 50 sold last month (Medium)<br>- `Adjusted Profit` GBP 1.49 vs GBP 2.82: profit sensitivity | Re-verify profit at current price; Keepa 90d; confirm exact 85g variation |
| B09KCLYC1D | Pan Aroma Candle 85g (Salted Caramel) | 324.1% | GBP 2.82 | 50 | Focus After Verification | - Very high ROI (324.1%) with GBP 2.82 profit/unit<br>- Demand signal: 50 sold last month (Medium)<br>- Likely commodity pricing: profit depends on stable Buy Box | Keepa 90d price/offers; confirm exact 85g variation; check hazmat classification |
| 6040418214 | Fragrant Cloud Rose EDP 100ml | 77.0% | GBP 1.24 | 100 | Focus After Verification | - GBP 1.24 profit/unit at 77.0% ROI<br>- Demand signal: 100 sold last month (High)<br>- Perfume category: restrictions/hazmat risk can block scaling | SellerAmp restrictions/hazmat; Keepa 90d; confirm exact 100ml variant and category |
| B01IFIJ91Y | Mason Cash Mixing Bowl 29cm / 4L | 66.7% | GBP 5.11 | 200 | Focus After Verification | - GBP 5.11 profit/unit at 66.7% ROI<br>- Demand signal: 200 sold last month (High)<br>- BrandRisk: Medium (from file) + fragile/breakage risk | SellerAmp restrictions/gating; Keepa 90d; confirm packaging + fragile handling assumptions |
| B07GZGXQYG | Superior Foil Containers w/ Lids (9x13) | 65.8% | GBP 2.50 |  | Focus After Verification | - GBP 2.50 profit/unit at 65.8% ROI<br>- Sales badge missing in file (demand uncertain)<br>- Pack verdict missing: high risk of wrong variation/pack count | Re-check Sales badge on listing; confirm pack count/variation; Keepa 90d price/offers |
| B08L66NXB5 | Superior Foil Containers w/ Lids (10x12) | 62.5% | GBP 3.00 |  | Focus After Verification | - GBP 3.00 profit/unit at 62.5% ROI<br>- Sales badge missing in file (demand uncertain)<br>- Pack verdict/Confidence missing: treat as incomplete row | Re-check Sales badge + pack count; Keepa 90d; validate variation matches supplier |
| B074ZH6DXK | Superior Large Foil Trays (Pack of 10, 32x26cm) | 37.8% | GBP 1.70 | 50 | Focus After Verification | - GBP 1.70 profit/unit at 37.8% ROI<br>- Demand signal: 50 sold last month (Medium)<br>- Pack verdict missing: size/oversize fees can flip economics | Confirm pack/variation + dimensions; Keepa 90d; verify FBA size tier assumptions |
| B0126CHB24 | Alberto Balsam Shampoo (Tea Tree, pack of 6) | 38.1% | GBP 2.76 | 50 | Defer / Seasonal / Watchlist | - GBP 2.76 profit/unit at 38.1% ROI (good on paper)<br>- Demand signal: 50 sold last month (Medium)<br>- `Filter Reason` = OTHER SUPPLIER: sourcing assumptions likely invalid | Only proceed if you can source from the intended supplier at the stated buy cost; then run SellerAmp + Keepa 90d |
| B07YQ5HFFN | Paper Lace Doyleys 22cm (40-pack) | 44.8% | GBP 0.30 | 700 | Defer / Seasonal / Watchlist | - High demand (700/mo) but very thin profit (GBP 0.30/unit)<br>- ROI looks OK, but price/fee shifts can wipe profit<br>- Commodity product: high competition risk | Only revisit if buy cost improves or you can bundle; Keepa 90d for price slides/offer spikes |
| B08G1Q1L46 | Swiss Roll Tray 32x23.5cm | 22.3% | GBP 0.72 | 600 | Defer / Seasonal / Watchlist | - High demand (600/mo) but low ROI (22.3%) and thin profit (GBP 0.72)<br>- Likely fee/competition sensitivity<br>- Only makes sense at better buy cost or very stable BB | Keepa 90d for stability; confirm size tier/fees; consider skipping unless cost improves |
| B009SJXB32 | Glass Vinegar Shaker | 48.9% | GBP 0.46 | 50 | Defer / Seasonal / Watchlist | - GBP 0.46 profit/unit despite 48.9% ROI (ROI misleading on low buy cost)<br>- Medium demand (50/mo)<br>- Glass/fragile returns risk can erase margin | Keepa 90d; confirm fragile packaging assumptions; only proceed with higher profit buffer |
| B0042FBWQ0 | Glass Carafe 580ml | 29.7% | GBP 0.76 | 50 | Defer / Seasonal / Watchlist | - Borderline ROI (29.7%) with GBP 0.76 profit/unit<br>- Medium demand (50/mo)<br>- Fragile glass: returns/defects likely reduce real profit | Keepa 90d; confirm size tier + breakage rate; proceed only if profit buffer improves |
| B00LZRJTEA | Bamboo Cocktail Sticks 200-pack | 37.3% | GBP 0.25 | 50 | Defer / Seasonal / Watchlist | - GBP 0.25 profit/unit (very thin) despite 37.3% ROI<br>- Medium demand (50/mo)<br>- BrandRisk: Medium (from file) on a commodity product | SellerAmp restrictions; Keepa 90d; only proceed if buy cost improves materially |
| B0111N9Z1O | Stainless Steel Cleaner/Polisher 400ml | 20.3% | GBP 0.79 | 50 | Defer / Seasonal / Watchlist | - Just above ROI floor (20.3%) with GBP 0.79 profit/unit<br>- Medium demand (50/mo)<br>- Any price drop pushes ROI below threshold | Keepa 90d; verify competition; proceed only if price is stable and restrictions are clear |
| B0DJDH23JW | SUPERIOR FOIL 10 CONTAINERS & LID 9x9 (duplicate row) | 52.6% | GBP 2.00 |  | Defer / Seasonal / Watchlist | - Same ASIN as the 700-sales row, but this row is missing Sales/Pack/Confidence<br>- Treat as data-quality duplicate within `shortlist.csv`<br>- Use the other B0DJDH23JW entry for decisions | Ignore this duplicate row; use the other entry for the same ASIN |

## Seasonality & timing guidance
- Keepa not checked in this pass; guidance is conditional only.
- If a title/keyword suggests Q4 seasonality (Christmas/Winter): proceed only if Keepa shows repeatable Q4 spikes and a clean exit window.
- For commodity/disposable items (foil trays, paper doyleys, cocktail sticks): proceed only when offer count is stable and price is not sliding.
- For fragile/hazmat-prone items (glassware, perfumes, oils/diffusers): confirm FBA size tier + hazmat status before buying.

## Action checklist (next 7 days)
- Pull the top 8: listing confirmation (pack/variation) -> SellerAmp restrictions -> Keepa 90d price/offers.
- For Focus Now: test-buy small and fast (rule of thumb: ~10-20 units when Sales>=200 and Profit>=GBP 2; otherwise ~5-10).
- For Focus After Verification: only buy after clearing the specific missing fields/risk flags noted per item.
- For Defer/Watchlist: avoid tying up capital unless buy cost improves or competition/price stabilizes.
