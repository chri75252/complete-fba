## Quick Links (add to the top of your MD)
```

* [PHASE 1 — Prompt 1: TRUE SALES AUDIT](#phase-1-prompt-1-true-sales-audit)
* [PHASE 2 — Prompt 2: PRICING BEHAVIOR](#phase-2-prompt-2-pricing-behavior)
* [PHASE 3 — Prompt 3: STANDARD FORECAST](#phase-3-prompt-3-standard-forecast)
* [PHASE 3B — Prompt 3B: ADVANCED FORECAST](#phase-3b-prompt-3b-advanced-forecast)
* [PHASE 4 — Prompt 4: FINAL DECISION](#phase-4-prompt-4-final-decision)
* [Appendix A: Output Schemas](#appendix-a-output-schemas)
* [Appendix B: Next-Phase One-Liners](#appendix-b-next-phase-one-liners)
* [Appendix C: Validation & Cross-Checks](#appendix-c-validation--cross-checks)

````

═══════════════════════════════════════════════════════  
📊 FINAL AMAZON FBA PRODUCT ANALYSIS PROMPT SET  
═══════════════════════════════════════════════════════  
Optimized for FBA sellers | VAT-registered (20%) | UK marketplace  
Extracted from Chat 68eb5e1a ("final o3 product analysis")  
Last Updated: November 2025

🔵 WORKFLOW OVERVIEW:  
Prompt 1: Sales Audit → Prompt 2: Behavior Analysis → Prompt 3: Depletion Forecast

Use these prompts SEQUENTIALLY on new products for accurate profitability analysis.

═══════════════════════════════════════════════════════  
PROMPT 1: TRUE SALES AUDIT  
═══════════════════════════════════════════════════════

📝 BEFORE USING THIS PROMPT, FILL IN:  
• Screenshot timeframe: \[DEFAULT: 30 days\] (Update to 45 days if needed)  
• Referral fee (inc-VAT): £\_\_\_  
• FBA fee (inc-VAT): £\_\_\_    
• Prep fee (ex-VAT): £\_\_\_ per unit  
• Supplier cost (inc-VAT, after discounts): £\_\_\_ per unit  
• Shipping cost (ex-VAT): £\_\_\_ per unit  
• Unit definition: \[e.g., "1 unit \= 2 mugs" or "1 unit \= 1 baking pan"\]

✅ EXPECTED OUTPUT:  
\- Table showing TRUE 30-day sales per seller (excluding stock adjustments)  
\- Seller roster with FBA/FBM status, pricing, stock levels, reviews  
\- Weekly market volume calculation  
\- Unit economics table (break-even, margins, ROI at different prices)

──────────── COPY BELOW THIS LINE ────────────

You have access to Keepa's "Sold in 30 Days" metrics for multiple sellers, alongside each seller's 30-day stock history graph. Your task is to identify genuine sales from these graphs by differentiating between actual customer purchases and inventory adjustments or removals.

Important Guidelines:

1\. Distinguish Genuine Sales vs. Adjustments  
\- Small, stepwise declines over several days typically represent real sales.  
\- Sudden, large single-day drops often indicate stock removal, relocation, or other non-sale adjustments.  
\- If the graph stays flat after a large drop, assume zero (or near-zero) actual sales occurred during that period.

2\. Estimate True Sales  
\- For each seller, examine the entire 30-day graph.  
\- Count only the cumulative effect of gradual stepwise decreases as sales.  
\- Exclude the "big drop" (relatively speaking meaning big drop compared to product approximate daily sales (estimated using monthly sold yellow graph line)) sections from your sales count if they happen in a single day.  
\- If the line is flat for an extended period, assume zero sales in that time.

3\. Compare Against Keepa "Sold 30 Days" (which is found in the "Sold 30 Days" column on the left of the graphs)  
\- State Keepa's reported sales figure.  
\- Provide your own best estimate of actual sales based on the graph analysis.  
\- If there is a major discrepancy (more than 5–10 units difference), explain briefly why (e.g., "One large stock adjustment was misread as sales").

4\. Seller-by-Seller Summary  
\- Include for each seller:  
   \- Keepa 30-day sold figure.  
   \- Your estimated 30-day sales.  
   \- Notable restocks (sharp upward jumps).  
   \- Notable zero-sales segments (flat lines).  
   \- Any big drop events that are likely not real sales.  
   \- Whether the discrepancy is minor or major.

5\. Recommendations  
\- Conclude with any general insights or recommendations (e.g., "Sellers showing large abrupt drops may be inflating their 'Sold 30 Days' figures.").

Output Format:  
\- Present the final result in a concise, clear table or bullet format.  
\- Highlight which sellers have consistent keepa-vs.-actual numbers and which do not.

CRITICAL NOTES:  
1\) Whenever you come across a "?" this is the same as 0, however if the "?" only appears in the buybox stats screenshot, it implies only that the seller is out of stock, which does not necessarily mean that the seller also had 0 sales.

2\) UNDER ABSOLUTELY NO CIRCUMSTANCE can your estimated/calculated sales value be higher than sales mentioned in the screenshots (use this when checking for discrepancies after you complete your own sales analysis and calculations), even if value in 30 days sold column is ? (= 0\)

3\) After completing your analysis for each seller, if discrepancy between Keepa sold in 30 days and yours are major and not due to a sharp drop (in a single day) retrace the graph line to confirm your initial analysis and calculation and if needed, rectify your error.

4\) DISCREPANCY CROSS-CHECKING STRATEGY: Check the sum of all the sales you estimated and compare it to the monthly sold value (extracted from the pricing history graph screenshot- containing 3 graphs); it is the value extracted from the yellow line in the middle graph), review your calculations and if needed rectify any misinterpreted/miscalculated seller's 30 day sales metric. Do not compare it with the sum of the "30 day sold" column, it has to be compared with the value extracted from the yellow line in the pricing history screenshot. The value will be the same as the one mentioned on the bottom of the screenshot in the sentence: "Bought in past month:"

When applicable, sellers not appearing in the graphs/table but appearing in the buybox stats screenshot (for example with high buybox percentage, despite being out of stock), their sales are to be considered in the comparison with the "Monthly Sold"/"bought in the past month" value. You can get a rough estimate by using the buybox percentage share multiplied by the "monthly sold"; this type of sales calculation is only to be used in this case with no exception.

If total calculated sales are below the monthly sold value after adding (when applicable) sales of seller appearing in buybox stats screenshot ONLY, just mention it at the end of your analysis (NO FURTHER ACTION NEEDED). UNDER NO CIRCUMSTANCE WILL YOU USE THIS METHOD FOR SELLERS APPEARING IN THE GRAPHS SCREENSHOTS.

Regarding the above cross-checking strategies, do not try to generate an explanation/interpretation with the purpose of matching your calculated sales rate with the cross-checking metrics. If need be you will recalculate the sales rate in an additional step, only after this step you are to generate a table with your findings.

I PURCHASE 5 CASES OF 24 UNITS (TOTAL 120 UNITS). 1 UNIT \= \[INSERT YOUR UNIT DEFINITION\]  
FBA FEE: \[INSERT\]  
REFERRAL FEE: \[INSERT\]

──────────── END OF PROMPT 1 ────────────

═══════════════════════════════════════════════════════  
PROMPT 2: PRICING BEHAVIOR ANALYSIS  
═══════════════════════════════════════════════════════

📝 BEFORE USING THIS PROMPT:  
• Complete Prompt 1 first  
• Screenshot timeframe reference: \[Same as Prompt 1 \- DEFAULT: 30 days\]

✅ EXPECTED OUTPUT:  
\- Classification of each seller (Aggressive BuyBox Chaser / Reactive / Premium)  
\- Seller behavior patterns vs. Buy Box price  
\- Adjustment frequency and Buy Box correlation metrics

──────────── COPY BELOW THIS LINE ────────────

You have completed Phase 1, confirming each seller's actual 30-day sales. Now, for Phase 2 (Part A), I want you to conduct a computational analysis of the graphs in order to classify each in-stock seller according to how they price relative to the product's BuyBox price in the main Keepa graphs.

\* Compare each seller's price line to the product's BuyBox line in the main Keepa graph, not just to other sellers.  
\* Capture how quickly they adjust (adjustmentFrequency), how closely they track the BuyBox (buyboxPriceCorrelation), etc.

CLASSIFY EACH SELLER  
Use these simplified categories:  
\* Aggressive BuyBox Chaser: frequently matches/undercuts BuyBox in ≤1 day.  
\* Reactive BuyBox Chaser: chases or matches the BuyBox but with a delay.  
\* Premium (can further split into "Slight," "Moderate," or "High" if needed): stays above the BuyBox, rarely lowering price.

──────────── END OF PROMPT 2 ────────────

═══════════════════════════════════════════════════════  
PROMPT 3: 8-WEEK STANDARD DEPLETION FORECAST (FACTOR-WEIGHTED)  
═══════════════════════════════════════════════════════

📝 BEFORE USING THIS PROMPT, FILL IN:  
• My planned inventory: \[DEFAULT: 20 FBA units\] (Adjust as needed)  
• My entry price: £\_\_\_ (or "match current Buy Box")  
• Screenshot timeframe reference: \[Same as Prompts 1 & 2 \- DEFAULT: 30 days\]

✅ EXPECTED OUTPUT:  
\- 8-week depletion forecast with 3 scenarios (Best / Realistic / Worst)  
\- Week-by-week stock depletion: (StartStock – WeeklySales \= EndStock)  
\- My Buy Box share percentage each week  
\- Sell-out week prediction for each scenario  
\- Expected revenue and gross profit  
\- Entry/Avoid recommendation with justification

──────────── COPY BELOW THIS LINE ────────────

After having classified each seller, please conduct a computational analysis of an 8-week depletion forecast using a deterministic factor-weighted model (not Monte Carlo). Use a detailed or code-like simulation approach, similar to the style shown below.

FACTOR-WEIGHTED BUYBOX REDISTRIBUTION  
Each week, assign BuyBox share via these weights:  
\- FBA vs FBM: \~65%  
\- Price Competitiveness: \~22.5%  
\- Reviews: \~5%  
\- Stock: 8.5%

Normalize so total \= 100%. Sellers with stock=0 → 0% share.

WEEKLY SALES FORMULA (DETERMINISTIC)  
Use: Sales\_week \= (HistWeeklyRate × w) \+ (BuyBoxShare × MarketVolume)

where:  
\- w \= 30% in Week 1 & Week 2, 20% in subsequent weeks.  
\- MarketVolume \= sales rate from Phase 1's yellow line graph (Monthly Sold ÷ 4.3)  
\- If sales \> stock, clamp to stock and mark OOS.

OUTPUT TABLE FORMAT (REALISTIC SCENARIO – REQUIRED)  
Create a single 8-week depletion table:  
| Seller | Type | Behavior | Monthly Sales | Initial Stock | Week 1 (Date Range) | Week 2 (Date Range) | Week 3 (Date Range) | Week 4 (Date Range) | Week 5 (Date Range) | Week 6 (Date Range) | Week 7 (Date Range) | Week 8 (Date Range) | Final Stock |

\- Include one row per current in-stock seller **plus** a row `YOU (new FBA)` (or equivalent for your listing).  
\- Each Week cell must show the full transition in this form: `oldStock – weeklySales = newStock`, rounded to 1 decimal.  
\- Add a **"Total weekly sales"** row at the bottom, summing weekly sales across all sellers for Weeks 1–8 (used for cross-checking vs `MonthlySold / 4.3` from Phase 1\).

IMPORTANT NOTES:  
1\. If a seller only appears in the BuyBox stats table (with "?" stock=0) and does not appear in the offer/graph screenshots, they are out of stock and EXCLUDED FROM THIS STEP despite having possibly appeared in previous step (having past 30 days sales rate but are now OOS)

2\. Confirm whether each seller is FBA or FBM by cross-checking the stock-graph screenshot and the BuyBox stats screenshot.

3\. Simulate THREE scenarios for me:  
   \* \*\*Best-Case\*\* – rivals raise price 5% or go OOS 20% sooner.  
   \* \*\*Realistic\*\* – today's trends hold.  
   \* \*\*Worst-Case\*\* – one new aggressive FBM rival undercuts by ≥3% and adds 25% stock.

4\. For each scenario output:  
   \- Expected weekly sales (weeks 1-8) in the form (oldStock – sales \= newStock)  
   \- Week I sell out  
   \- Total revenue & gross profit (at my chosen price)

5\. RECOMMENDATIONS (≤8 concise bullets):  
   \* Enter vs Avoid decision \+ justification  
   \* Suggested starting price & inventory  
   \* Best / Realistic / Worst sales-rate summary  
   \* Risk notes (price war, stock-dumpers, data anomalies)

I WILL LIST \[INSERT NUMBER\] UNITS VIA FBA AT £\[INSERT PRICE\].

IMPORTANT CROSS-CHECKS:  
\* Sum of your estimated sales should be \*\*close to\*\* the yellow-line Monthly Sold (± 10 units).  
\* If not, re-trace graphs or explain the gap (do \*\*not\*\* force-fit numbers).  
\* If a seller appears only in Buy-Box stats ("?" stock) but not in graphs, estimate their sales \= BuyBox % × Monthly Sold \*\*only for the cross-check\*\*, never for the forecast.

──────────── END OF PROMPT 3 ────────────

═══════════════════════════════════════════════════════  
💰 FINANCE FORMULAS (UK FBA VAT-REGISTERED)  
═══════════════════════════════════════════════════════

BREAK-EVEN CALCULATION:  
amazon\_exVAT \= selling\_price\_incVAT / 1.20  
net\_proceeds \= amazon\_exVAT \- referral\_fee\_ex \- fba\_fee\_ex  
landed\_cost\_ex \= supplier\_cost\_ex \+ shipping\_ex \+ prep\_ex  
net\_profit\_ex \= net\_proceeds \- landed\_cost\_ex  
break\_even\_incVAT \= 1.20 × (referral\_ex \+ fba\_ex \+ landed\_ex)

ROI & MARGIN:  
roi\_percent \= 100 × net\_profit\_ex / landed\_cost\_ex  
margin\_percent \= 100 × net\_profit\_ex / amazon\_exVAT

CONVERT TO EX-VAT:  
supplier\_ex \= supplier\_inc / 1.20  
referral\_ex \= referral\_inc / 1.20  
fba\_ex \= fba\_inc / 1.20

EXAMPLE (Mugs 2-pack):  
\- Supplier: £4.64 ex-VAT (£2.32/mug)  
\- Shipping: £0.89 ex-VAT  
\- Prep: £0.55 ex-VAT  
\- Landed: £6.08 ex-VAT  
\- Fees: £1.375 (ref) \+ £2.533 (FBA) \= £3.908 ex-VAT  
\- Break-even: 1.20 × (3.908 \+ 6.08) \= £11.99 inc-VAT  
\- Selling at £12.49: Profit \= (12.49/1.20) \- 3.908 \- 6.08 \= £0.42 → 6.9% ROI

═══════════════════════════════════════════════════════  
📌 HOW TO USE THIS PROMPT SET  
═══════════════════════════════════════════════════════

1\. GATHER YOUR SCREENSHOTS (30-day window recommended):  
   • Keepa: Buy Box Statistics (30d)  
   • Keepa: 3-panel price history with yellow "Monthly Sold" line  
   • Keepa: Offers page with 30-day stock mini-graphs  
   • (Optional) Supplier quote/invoice for cost data

2\. PREPARE YOUR INPUTS:  
   • Fill in the variables listed before each prompt  
   • Know your unit definition (1 unit \= X mugs/pans/etc.)  
   • Get accurate fees from Amazon Seller Central

3\. EXECUTE PROMPTS SEQUENTIALLY:  
   • Start with Prompt 1 (Sales Audit)  
   • Review output, then run Prompt 2 (Behavior Analysis)  
   • Finally run Prompt 3 (Depletion Forecast)  
   • DO NOT skip prompts \- each builds on the previous

4\. VERIFY OUTPUTS:  
   • Check that sum of estimated sales ≈ Monthly Sold (±10 units)  
   • Confirm Buy Box weights sum to 100%  
   • Validate break-even price makes sense

5\. MAKE YOUR DECISION:  
   • Review Best/Realistic/Worst scenarios  
   • Check sell-out timeline against your cash flow needs  
   • Evaluate ROI vs. your minimum threshold

═══════════════════════════════════════════════════════  
✅ MODIFICATIONS MADE TO ORIGINAL CHAT PROMPTS  
═══════════════════════════════════════════════════════

ALL CORE PROMPT TEXT IS COPIED VERBATIM FROM CHAT 68eb5e1a.

Changes made for usability:  
1\. ❌ REMOVED: References to FBM inventory, reserved stock, inbound ETA  
   (You're FBA-only, so these complicate the prompts unnecessarily)

2\. ❌ REMOVED: "VAT status" variable   
   (You're always VAT-registered at 20%)

3\. ➕ ADDED: Clear "Before Using" sections with variable checklists

4\. ➕ ADDED: "Expected Output" descriptions for each prompt

5\. 🔄 REORGANIZED: Prompts split into 3 sequential steps instead of single massive prompt  
   (Original chat had everything in one prompt, but workflow analysis showed   
   you used them sequentially for best results)

6\. ➕ ADDED: Finance formulas and usage instructions

7\. 🔄 SIMPLIFIED: Default to "30 days" with option to update to 45 days  
   (Instead of asking for timeframe every time)

THE ACTUAL SALES AUDIT METHODOLOGY, BUY BOX WEIGHTS, FORMULAS, AND  
ACCURACY RULES ARE 100% IDENTICAL TO THE SOURCE CHAT.

═══════════════════════════════════════════════════════  
🏁 END OF PROMPT SET  
═══════════════════════════════════════════════════════

Extracted from: Chat 68eb5e1a \- "final o3 product analysis"  
Optimized for: UK FBA sellers, VAT-registered, new product analysis  
Last updated: November 7, 2025

═══════════════════════════════════════════════════════  
📊 PROMPT 3B: ADVANCED COMPUTATIONAL FORECAST (RECOMMENDED)  
═══════════════════════════════════════════════════════

USE THIS VERSION INSTEAD OF PROMPT 3 FOR MAXIMUM ACCURACY

This enhanced version requires rigorous computational modeling with Monte Carlo simulation  
for the most accurate sell-out predictions and confidence intervals.

📝 BEFORE USING THIS PROMPT, FILL IN:  
• My planned inventory: \[DEFAULT: 20 FBA units\] (Adjust as needed)  
• My entry price: £\_\_\_ (or "match current Buy Box")  
• Screenshot timeframe reference: \[Same as Prompts 1 & 2 \- DEFAULT: 30 days\]

✅ EXPECTED OUTPUT:  
\- TWO independent forecasts using different methodologies  
\- Comparative analysis identifying discrepancies between methods  
\- Final reconciled forecast with confidence intervals (95% CI)  
\- 8-week depletion with Best/Realistic/Worst scenarios  
\- Week-by-week stock depletion with Buy Box share percentages  
\- Sell-out week predictions with probability distributions  
\- Revenue and profit projections with risk analysis

──────────── COPY BELOW THIS LINE ────────────

You are required to conduct a RIGOROUS COMPUTATIONAL ANALYSIS using advanced forecasting methodologies to predict inventory depletion with maximum accuracy.

MANDATORY APPROACH:  
You MUST generate TWO INDEPENDENT forecasts using different methodologies, then compare and reconcile them into a final forecast.

═══ METHOD 1: MONTE CARLO SIMULATION (REQUIRED) ═══

Implement a Monte Carlo simulation with the following specifications:

Implementation note (when code is available):  
- You may use the `keepa_monte_carlo_depletion_simulator.py` script in the same folder as this MD.  
- Before running it, set `MONTHLY_SOLD_MARKET`, `WEEKLY_MARKET_VOLUME`, `NEG_BINOMIAL_K`, and the `SELLERS` list using Phase 1 & 2 outputs (true 30d sales, prices, reviews, initial stock, FBA/FBM, and which seller is YOU).  
- When the script cannot be run (no code execution), you must still follow all Monte Carlo rules below, but clearly label any Monte Carlo statistics as **conceptual / not actually simulated**.
1\. DEMAND MODEL:  
   \- Daily demand follows Negative Binomial distribution  
   \- Mean \= WeeklyMarketVolume / 7 (from Phase 1 yellow line)  
   \- Dispersion parameter k \= 1.2 (or estimate from variance if data available)  
   \- Run 10,000 iterations minimum

2\. BUY BOX ALLOCATION (per simulation iteration):  
   \- Use Dirichlet distribution to model stochastic Buy Box share  
   \- Alpha parameters built from weighted score for each seller:  
       \* α\_i \= w\_FBA × FBA\_score \+ w\_Price × Price\_score \+ w\_Reviews × Review\_score \+ w\_Stock × Stock\_score  
       \* Weights: FBA=0.65, Price=0.225, Reviews=0.05, Stock=0.085  
   \- Price\_score \= (min\_price / seller\_price) clipped to \[0.80, 1.10\]  
   \- Review\_score \= (seller\_reviews / max\_reviews)  
   \- Stock\_score \= (seller\_stock / total\_stock)  
   \- FBA\_score \= 1.0 if FBA, 0.3 if FBM  
   \- Assert: Sum of weights \= 1.0

3\. DAILY SIMULATION LOOP (for each of 10,000 iterations):  
   \- For each day in 8-week period:  
       a) Draw daily demand from Negative Binomial  
       b) Draw Buy Box shares from Dirichlet(alpha)  
       c) Allocate demand proportionally to Buy Box shares  
       d) Clamp sales to available stock for each seller  
       e) Update stock levels  
       f) When seller hits stock=0, re-normalize Buy Box shares among remaining sellers  
       g) Model restock hazard: λ\_i \= exp(− stock\_i / θ) where θ \= 24-30 (case size)

4\. OUTPUT FROM MONTE CARLO:  
   \- Weekly sales statistics: mean, median, 95% confidence intervals  
   \- Sell-out week probability distribution  
   \- My Buy Box share over time with confidence bands  
   \- Revenue and profit distributions

═══ METHOD 2: FACTOR-WEIGHTED DETERMINISTIC MODEL ═══

Implement the factor-weighted approach as described in standard Prompt 3:

WEEKLY SALES FORMULA:  
Sales\_week \= (HistWeeklyRate × w) \+ (BuyBoxShare × MarketVolume)

where:  
\- w \= 30% in Week 1 & Week 2, 20% in subsequent weeks  
\- MarketVolume \= Monthly Sold ÷ 4.3  
\- BuyBoxShare calculated using same weights as Monte Carlo (65/22.5/5/8.5)  
\- Sales clamped to stock; OOS sellers removed and shares re-normalized

Generate three scenarios:  
1\. \*\*Best-Case:\*\* Rivals raise price 5% or go OOS 20% sooner  
2\. \*\*Realistic:\*\* Current trends persist  
3\. \*\*Worst-Case:\*\* New aggressive FBM undercuts by ≥3% with 25% more stock

═══ COMPARATIVE ANALYSIS (MANDATORY) ═══

After generating both forecasts, you MUST:

1\. CREATE COMPARISON TABLE:  
   | Metric | Monte Carlo (mean) | Deterministic (realistic) | Difference | % Diff |  
   \- Week-by-week sales for ME  
   \- Sell-out week  
   \- Total revenue  
   \- Average Buy Box share

2\. IDENTIFY DISCREPANCIES:  
   \- Flag any week where forecasts differ by \>15%  
   \- Explain WHY discrepancies exist (e.g., "Monte Carlo accounts for demand variance; deterministic assumes fixed weekly rate")  
   \- Assess which model is more conservative

3\. RECONCILE INTO FINAL FORECAST:  
   \- If discrepancy \<10%: Use Monte Carlo mean as final forecast  
   \- If discrepancy 10-20%: Use weighted average (70% Monte Carlo, 30% Deterministic)  
   \- If discrepancy \>20%: Flag as HIGH UNCERTAINTY and provide BOTH forecasts with explanation

4\. SENSITIVITY ANALYSIS:  
   \- Test impact of ±20% change in weekly market volume  
   \- Test impact of my entry price ±£0.50  
   \- Report how sell-out week changes under these scenarios

═══ FINAL OUTPUT FORMAT (MANDATORY STRUCTURE) ═══

Deliver your analysis in exactly this structure:

\*\*SECTION 1: MONTE CARLO SIMULATION RESULTS\*\*  
Table showing weeks 1-8 with:  
\- My stock: Start | Sold (mean; 95% CI) | End  
\- My BB share %: (mean; 95% CI)  
\- Other sellers' status (who goes OOS when)  
\- Total weekly volume vs. baseline

Sell-out week: \[Week X (probability Y%)\]  
Revenue: £\_\_\_ (95% CI: \[£\_\_\_, £\_\_\_\])  
Profit: £\_\_\_ (95% CI: \[£\_\_\_, £\_\_\_\])

\*\*SECTION 2: DETERMINISTIC MODEL RESULTS\*\*  
Three tables (Best / Realistic / Worst) showing weeks 1-8:  
| Seller | Type | Start | Sold | End | My BB % | Notes |

Sell-out weeks: Best=\[Wx\], Realistic=\[Wy\], Worst=\[Wz\]  
Revenue & Profit for each scenario

\*\*SECTION 3: COMPARATIVE ANALYSIS\*\*  
Comparison table (as specified above)  
Discrepancy analysis with explanations  
Sensitivity test results

\*\*SECTION 4: FINAL RECONCILED FORECAST\*\*  
Final sell-out prediction: Week \_\_\_ (±\_\_\_ weeks)  
Expected revenue: £\_\_\_ (±£\_\_\_)  
Expected profit: £\_\_\_ (±£\_\_\_)  
Confidence level: \[High / Medium / Low\] with justification

\*\*SECTION 5: DECISION RECOMMENDATION\*\*  
• GO / NO-GO decision with clear justification  
• Optimal entry price and quantity  
• Key risks and mitigation strategies  
• Watchlist: Which competitors to monitor daily  
• Trigger points for repricing decisions  
• Cash flow implications (how long capital is tied up)  
• Recommended action if sell-out takes longer than expected  
• Reorder point calculation (when to place next order)

═══ CRITICAL REQUIREMENTS ═══

✅ You MUST show your computational work:  
   \- State the distributions used and their parameters  
   \- Show example calculations for at least Week 1  
   \- Provide Python/R code snippets if using programmatic simulation  
   \- Display intermediate validation checks

✅ You MUST validate results:  
   \- Verify sum of all sellers' weekly sales ≈ market volume (±10%)  
   \- Confirm no seller sells \> available stock  
   \- Check Buy Box weights sum to 1.0 each iteration  
   \- Ensure Monte Carlo convergence (check if increasing iterations changes results)

✅ You MUST account for uncertainty:  
   \- Provide confidence intervals, not just point estimates  
   \- Quantify probability of different outcomes  
   \- State assumptions explicitly and their impact on results

✅ UNVERIFIABLE data handling:  
   \- If any seller data is unclear, mark as UNVERIFIABLE  
   \- Use conservative bounds rather than guessing  
   \- State how missing data impacts forecast accuracy

I WILL LIST \[INSERT NUMBER\] UNITS VIA FBA AT £\[INSERT PRICE\].

CROSS-CHECKS:  
• Monte Carlo iterations must converge (test with 5k vs 10k runs)  
• Deterministic realistic case should fall within Monte Carlo 80% confidence interval  
• If not, investigate and explain the divergence  
• Final forecast must be internally consistent with Phase 1 & 2 data

──────────── END OF PROMPT 3B ────────────

ℹ️ NOTE: Use Prompt 3B instead of Prompt 3 when you need:  
\- Maximum forecast accuracy with confidence intervals  
\- Rigorous quantification of uncertainty  
\- Comparative validation between methodologies    
\- Publication-quality analysis with full computational transparency

Prompt 3 (simpler version) is sufficient for quick assessments.  
Prompt 3B (this version) is recommended for large inventory commitments or high-value products.

═════════════════════════════════════════════════════════

📋 PROMPT 4: FINAL DECISION & PRICING STRATEGY

BEFORE USING THIS PROMPT, FILL IN:  
\- Results from Prompts 1, 2, and 3 (or 3B)  
\- Current competitive landscape snapshot  
\- Your order quantity and lead time

EXPECTED OUTPUT:  
\- Clear YES/NO Go decision with justification  
\- Launch pricing strategy with guardrails  
\- IF/THEN trigger playbook for price adjustments  
\- Competitive monitoring watchlist  
\- Inventory reorder plan

─────────────── \[COPY BELOW\] ───────────────

ROLE: You are providing the final investment decision for an Amazon FBA product opportunity.

Based on the complete analysis from Phases 1-3, you must deliver:

\=== 1\) GO/NO-GO DECISION \===

Provide a clear binary recommendation: \*\*YES – PROCEED\*\* or \*\*NO – PASS\*\*

Justification must reference:  
\- Expected profit per unit (ex-VAT) across Best/Realistic/Worst scenarios  
\- ROI% and payback period  
\- Sell-out timeline and cash flow implications    
\- Competitive risks and market stability  
\- Confidence level in forecast accuracy

If the decision is borderline, state the key assumptions that would need to hold true for success.

\=== 2\) PRICING STRATEGY (Required for BOTH Go and No-Go) \===

A) LAUNCH PRICE GUARDRAILS:

\- \*\*BB-Par Launch\*\*: Set initial price at Buy Box parity (match current BB price)  
\- \*\*Operational Floor\*\*: Never price below 30% ROI threshold  
  → Calculate: Operational\_Floor \= 1.20 × (fees\_ex \+ landed\_ex) / 0.70  
\- \*\*Stretch Ceiling\*\*: Maximum price justified only if BB% ≥ 60-65% sustained for ≥24h  
  → Test cautiously; monitor BB% hourly during stretch attempts

B) TRIGGER → ACTION PLAYBOOK (IF/THEN rules):

\*\*TRIGGER 1\*\* — Competitor Stockouts:  
\- IF ≥2 FBA rivals show OOS ≥12h AND my BB% ≥ 55%   
  → RAISE price by \+£0.25  
  → RE-CHECK BB% after 6–12h  
  → If BB% remains ≥50%, consider second \+£0.25 increment

\*\*TRIGGER 2\*\* — New Entrant Flood:  
\- IF New-Offer Count spikes by \+3 sellers within 72h  
  → HOLD current price OR drop to Operational Floor  
  → PAUSE all undercutting attempts for 48h  
  → Reassess competitive positioning after initial shake-out

\*\*TRIGGER 3\*\* — Cheap FBM Attack:  
\- IF FBM seller enters at −3% vs BB with ≥25 stock  
  → DEFEND at (Launch\_Price − £0.20) for 48–72h  
  → Monitor FBM stock depletion rate  
  → If FBM sustains \>100 stock, revert to Launch\_Price and accept lower BB%

\*\*TRIGGER 4\*\* — Loss of Buy Box Share:  
\- IF BB% drops \<45% for 24h straight with ≥2 FBA sellers near-par (±£0.05)  
  → MATCH BB price exactly for 24h  
  → Reassess seller stock levels and pricing behavior  
  → If no improvement, evaluate operational floor vs. holding inventory

C) PRICE LADDER REFERENCE:

Maintain awareness of the elasticity-based price ladder (from Phase 3):  
\- Argmax Profit price  
\- Volume trade-offs at each £0.25 increment  
\- Margin% and ROI% at operational boundaries

\=== 3\) COMPETITIVE MONITORING WATCHLIST \===

Track daily (or multiple times per day during critical periods):

\*\*Seller Behavior Intelligence:\*\*  
\- \*\*Aggressive Liquidators\*\*: Sellers with declining stock \+ frequent price drops → likely short-term pressure  
\- \*\*Steady Resellers\*\*: Consistent restocking patterns \+ stable pricing → long-term competitors  
\- \*\*Overstock Situations\*\*: Sudden large inventory increases (\>100 units jump) → potential dump risk

\*\*Stock Level Tracking:\*\*  
\- Projected OOS dates for each FBA competitor (based on True\_30D sales rates)  
\- Restock frequency patterns (weekly vs. monthly vs. sporadic)  
\- New seller entries and their initial stock commitments

\*\*Price Movement Patterns:\*\*  
\- Morning vs. evening repricing behavior  
\- Algorithmic repricers (instant matching) vs. manual adjusters  
\- Price floor discovery (lowest defensible price per competitor)

\*\*FBA vs. FBM Dynamics:\*\*  
\- FBM seller persistence and stock depth  
\- Shipping speed claims (Prime-like vs. standard)  
\- Price gaps required for FBM to win BB (typically −5% to −8%)

\*\*Buy Box Share Monitoring:\*\*  
\- Your BB% over time (target: maintain ≥55% during normal conditions)  
\- BB rotation patterns (if multi-seller BB splits exist)  
\- Amazon as seller (if applicable) – treat as absolute price ceiling

\=== 4\) INVENTORY & CASH FLOW PLAN \===

A) REORDER POINT CALCULATION:

ROP \= (Weekly\_Demand × Lead\_Time\_Weeks) \+ Safety\_Stock

Where:  
\- Weekly\_Demand \= Use REALISTIC scenario forecast (conservative)  
\- Lead\_Time\_Weeks \= Supplier production \+ shipping \+ FBA receiving  
\- Safety\_Stock \= 1.5–2.0 weeks of demand (higher for volatile markets)

Example:  
\- Realistic demand \= 40 units/week  
\- Lead time \= 4 weeks  
\- Safety stock \= 60 units (1.5 weeks)  
\- ROP \= (40 × 4\) \+ 60 \= 220 units  
→ Trigger reorder when stock reaches 220 units

B) SCENARIO-BASED CASH IMPLICATIONS:

\*\*BEST Case\*\*: Early sell-out (Week 4–5)  
\- Fast cash recovery  
\- Opportunity cost if out of stock during high BB% period  
\- Prioritize rush reorder if margin supports expedited shipping

\*\*REALISTIC Case\*\*: Steady depletion (Week 6–8)  
\- Standard reorder timing  
\- Maintain price discipline per guardrails  
\- Monitor for mid-cycle competitive changes

\*\*WORST Case\*\*: Slow burn (Week 10+)  
\- Extended cash lockup  
\- Evaluate price reductions vs. storage fee accumulation  
\- Decision point: defend vs. liquidate (\>90 days \= long-term storage fee risk)

C) PERFORMANCE REVIEW CHECKPOINTS:

\*\*Week 1\*\*: Initial BB% achievement and price stability  
\*\*Week 2\*\*: Sales rate validation vs. forecast (flag if \>15% deviation)  
\*\*Week 4\*\*: Competitive landscape changes and reorder decision  
\*\*Week 6\*\*: Profitability check (actual vs. projected) and pricing optimization

\=== 5\) DECISION STATEMENT TEMPLATE \===

\[Use this structure for final recommendation\]

\*\*DECISION\*\*: \[YES – PROCEED / NO – PASS\]

\*\*RATIONALE\*\*:  
\- \*\*Profit Potential\*\*: £X.XX per unit (Realistic case) with Y% ROI  
\- \*\*Sell-Out Timeline\*\*: Z weeks under Realistic assumptions  
\- \*\*Cash Cycle\*\*: Initial investment £AAA, recovered by Week W  
\- \*\*Competitive Risk\*\*: \[Low/Medium/High\] based on \[specific factors\]  
\- \*\*Confidence Level\*\*: \[High/Medium/Low\] – \[key assumptions stated\]

\*\*LAUNCH PRICE\*\*: £X.XX (BB-par) with Operational Floor at £Y.YY

\*\*PRIMARY RISKS\*\*:  
1\. \[Risk 1 \+ probability assessment\]  
2\. \[Risk 2 \+ probability assessment\]    
3\. \[Risk 3 \+ probability assessment\]

\*\*SUCCESS CRITERIA\*\*:  
\- Achieve ≥Z% BB share within first week  
\- Maintain ≥£X profit per unit after price competition  
\- Sell through ≥Y units/week to meet payback timeline

\*\*MONITORING PRIORITIES\*\*: \[Top 3 specific metrics to track daily\]

\*\*FALLBACK PLAN\*\* (if Realistic case underperforms):  
\- \[Specific action 1 at week X\]  
\- \[Specific action 2 at metric threshold Y\]  
\- \[Exit criteria and liquidation trigger\]

─────────────── \[END OF COPY\] ───────────────

────────────────── END OF PROMPT 4 ──────────────────

═════════════════════════════════════════════════════════

✅ COMPLETE PROMPT SET FOR NET-P FBA SELLERS

This document contains all 4 prompts needed for comprehensive Amazon FBA product analysis:

• PROMPT 1: Master System Instruction \- Sets role, working mode, and data inputs  
• PROMPT 2: Sales Estimation Methodology \- True sales audit from Keepa graphs    
• PROMPT 3: Standard Depletion Forecast \- Quick 8-week simulation  
• PROMPT 3B: Advanced Computational Forecast \- Monte Carlo \+ deterministic comparison  
• PROMPT 4: Final Decision & Pricing Strategy \- Go/No-Go recommendation with triggers

USAGE WORKFLOW:  
1\. Start with Prompt 1 (role \+ inputs)  
2\. Add Prompt 2 (sales audit)  
3\. Add Prompt 3 OR 3B (forecast)  
4\. Finish with Prompt 4 (decision \+ strategy)

 All prompts adapted for NET-P FBA-only sellers (VAT-registered, 20% fixed rate).
 

═════════════════════════════════════════════════════════

📋 PROMPT 5: BACK-TEST & RECALIBRATION (PHASES A-E)  

USE THIS PROMPT ONLY **AFTER** PROMPTS 1-4 HAVE BEEN RUN FOR A GIVEN ASIN AND YOU NOW HAVE NEW 30-DAY KEEPA DATA FOR THE SAME ASIN.

This is a **POST-HOC COMPUTATIONAL ANALYSIS**: you are back-testing a previous forecast (Prompt 3 or 3B) against newly realised data, diagnosing errors, and recalibrating both Monte Carlo and deterministic models before building a new forward 8-week forecast.

?? BEFORE USING THIS PROMPT, PREPARE:

- New Keepa screenshots for the **same ASIN** (latest ~30 days):
  - 3-panel price graph with updated yellow "Bought in past month" line  
  - Updated Buy Box stats (30d)  
  - Updated offers page with stock graphs/mini-graphs  
- Your **previous forecast outputs**:
  - 8-week depletion table(s) (deterministic and/or Monte Carlo)  
  - Scenario assumptions (Best/Realistic/Worst)  
- Financial inputs (selling price, fees, costs) - defaults from the main workflow unless changed.

? EXPECTED OUTPUT (OVERALL MODULE):

- Clear back-test of forecast vs realised behaviour (per seller and market-level).  
- Identified error sources: demand, competition, modelling.  
- Recalibrated Monte Carlo parameters (μ, k, alpha logic) and deterministic parameters (HistWeeklyRate_i, etc.).  
- New reconciled 8-week forecast with updated confidence level and sensitivity analysis.  
- Guidance on how this recalibration should change your future usage of Prompts 3 vs 3B for similar ASINs.

─────────────── \[COPY BELOW\] ───────────────

You are now performing a **BACK-TEST & RECALIBRATION** for an ASIN previously analysed with Prompts 1-4.

Assume:

- Phase 1, 2, and 3 or 3B were completed for this ASIN using an earlier 30-day window.  
- Full 8-week forecast tables were produced (deterministic and/or Monte Carlo) and are available.  
- You now have **new Keepa screenshots** for the latest ~30 days for the same ASIN, plus those previous forecast tables.

You MUST follow the structure below: Phase A → B → C → D → E. Run one Phase per assistant response.

---

## PHASE A: BACK-TEST vs PREVIOUS FORECAST

1. **Recompute TRUE 30-day sales per seller** from the new screenshots using Phase 1 rules:
   - Only count gradual multi-day stepwise declines as sales.  
   - Exclude one-day big drops and mirrored restocks as inventory moves.  
   - Never exceed Keepa "Sold 30d" per seller (treat "?" as 0 upper bound).

2. **Approximate realised weekly sales** over the latest ~4 weeks:
   - For each major seller with visible stock history, estimate weekly sales per week.  
   - For the total market, cross-check vs the yellow "Bought in past month" line (MonthlySold / 4.3).

3. **Compare vs the old forecast**:
   - For each seller (and your listing, if it was live):
     - Forecast vs actual total units over the period.  
     - Forecast vs actual approximate weekly path.  
   - Compute:
     - Absolute error  
     - Percentage error  
     - Directional bias (systematically high/low/mixed).

4. **Identify root causes of error**:
   - **Demand side**:  
     - Was actual market volume higher/lower than assumed?  
     - Was realised variance (lumpiness) higher/lower than the model?  
   - **Competitive side**:  
     - Did some sellers price more aggressively or restock differently than assumed?  
     - Any unexpected new entrants, exits, or stock dumps?  
   - **Modelling side**:  
     - Did the deterministic factor-weight model systematically over/under-allocate Buy Box to certain classes (e.g. parked FBMs)?  
     - Did Monte Carlo's Negative Binomial / Dirichlet parameters misrepresent variance or shares?

Summarise Phase A clearly before moving to Phase B.

---

## PHASE B: METHOD 1 - RECALIBRATED MONTE CARLO

You now recalibrate the Monte Carlo model using the new realised data.

1. **Recalibrate demand (Negative Binomial)**:
   - Let `WeeklyMarketVolume_new = MonthlySold_new / 4.3` from the updated yellow line.  
   - Use realised variance of daily/weekly demand to re-estimate k where possible:
     - Var ≈ μ + μ² / k ⇒ solve for k.  
   - State explicitly whether you kept k = 1.2 or updated it and why.

2. **Recalibrate Buy Box shares (Dirichlet)**:
   - Check whether the original FBA/Price/Reviews/Stock weighting over/under-weighted some seller classes, especially large parked FBMs with very low hist_weekly_rate.  
   - Describe how you adapt `alpha_i` (e.g. adding a component from HistWeeklyRate or down-weighting parked FBMs) while preserving the basic FBA/Price/Reviews/Stock structure.

3. **Run or specify the recalibrated Monte Carlo**:
   - If code execution is available:
     - Use or adapt the Monte Carlo depletion simulator script described in your knowledge base.  
     - Update `MONTHLY_SOLD_MARKET`, `WEEKLY_MARKET_VOLUME`, `NEG_BINOMIAL_K`, and `SELLERS` from Phase A.  
     - Run ≥10,000 iterations (daily for 8 weeks), clamping to stock and dropping OOS sellers.
   - If code execution is **not** available:
     - Do NOT fabricate simulations.  
     - Provide the model setup and (if possible) ready-to-run code, and clearly label all MC statistics as UNCOMPUTED / conceptual.

4. **Summarise recalibrated Monte Carlo outputs**:
   - For **your listing** (per week):
     - Sales: mean, median, 95% CI.  
     - Buy Box share: mean, 95% CI.  
     - Stock path: start, mean sold, CI on sold, end.  
     - Sell-out week probabilities P(sell_out_by_week_w).  
   - For the **whole market**:
     - Total weekly volume vs WeeklyMarketVolume_new baseline (mean ± 95% CI).  
     - Probability distribution for OOS timing of major competitors.  
   - Revenue & profit distributions for your listing (mean, median, 95% CI).

---

## PHASE C: METHOD 2 - RECALIBRATED DETERMINISTIC MODEL

Re-run the deterministic factor-weight model (Prompt 3) with recalibrated inputs.

1. Compute `HistWeeklyRate_i = true_30d_new_i / 4.3` from Phase A.  
2. Use `WeeklyMarketVolume_new` from Phase B.  
3. For each week:
   - Calculate FBA_score, Price_score, Review_score, Stock_score and derive BuyBoxShare_i_week (deterministic, not random).  
   - Apply `Sales_week_i = HistWeeklyRate_i * w_factor + BuyBoxShare_i_week * WeeklyMarketVolume_new` (w_factor per Prompt 3).  
   - Clamp to stock; once stock hits 0, mark seller OOS and redistribute shares among remaining sellers.

4. Generate deterministic **Best / Realistic / Worst** scenarios as in Prompt 3/3B:
   - Best: competitors raise prices +5% or go OOS 20% sooner.  
   - Realistic: today's observed configuration persists.  
   - Worst: new aggressive FBM undercuts by ~3% with 25% of combined stock.

Produce a single 8-week table per deterministic scenario, plus total weekly sales and cross-check vs `WeeklyMarketVolume_new` (±10 units unless constrained by stock).

---

## PHASE D: COMPARATIVE ANALYSIS (MC vs DETERMINISTIC vs REALISED)

Construct a comparison table for **your listing**:

| Metric           | Monte Carlo (mean) | Deterministic (Realistic) | Realised (last 4w) | Diff vs Realised | % Diff vs Realised |

Include:
- Weekly sales (Weeks 1-8, where applicable).  
- Sell-out week.  
- Total units sold (8 weeks).  
- Total revenue & profit.  
- Average BB share over the horizon.

For each large discrepancy, explain whether it is driven by:
- Demand variance vs deterministic smoothness.  
- Mis-specified shares (e.g. parked FBMs too strong/weak).  
- Unmodelled events (e.g. new entrant).

Conclude whether Monte Carlo or deterministic is currently **more conservative** for this ASIN.

---

## PHASE E: RECALIBRATED FORWARD 8-WEEK FORECAST & SENSITIVITY

Finally, produce a new forward 8-week forecast using both recalibrated models.

1. **Forward forecast**:
   - Use recalibrated Monte Carlo (Method 1) to derive per-week sales / BB% / stock distributions for your listing.  
   - Use the recalibrated deterministic model (Method 2) to produce Best / Realistic / Worst deterministic paths.

2. **Reconciliation rules** (same as Prompt 3B):
   - If deterministic Realistic vs Monte Carlo mean differ by <10% on total units: use Monte Carlo mean.  
   - If 10-20%: use 70% Monte Carlo + 30% deterministic.  
   - If >20%: flag **HIGH UNCERTAINTY** and present both side-by-side with explanation.

3. **Sensitivity analysis**:
   - Re-run both models with WeeklyMarketVolume_new * 0.8 and * 1.2 and summarise impact on sell-out week and total units.  
   - Re-run with your price ±£0.50 and summarise impact on sell-out timing and total profit.

4. **Final recalibrated forecast summary**:
   - Final sell-out prediction (week ± band) for your listing.  
   - Expected revenue & profit with uncertainty range.  
   - Confidence level (High / Medium / Low) with explicit reference to:
     - Back-test error from Phase A,  
     - How well MC and deterministic now agree,  
     - Sensitivity results.

─────────────── \[END OF COPY\] ───────────────

────────────────── END OF PROMPT 5 ──────────────────

═════════════════════════════════════════════════════════
