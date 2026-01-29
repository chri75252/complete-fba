ННННННННННННННННННННННННННННННННННННННННННННННННННННННН  
?? PROMPT 5: BACK-TEST & RECALIBRATION (PHASES A–E)  
ННННННННННННННННННННННННННННННННННННННННННННННННННННННН

USE THIS PROMPT ONLY **AFTER** PROMPTS 1–4 HAVE BEEN RUN FOR A GIVEN ASIN AND YOU NOW HAVE NEW 30-DAY KEEPA DATA FOR THE SAME ASIN.

This is a **POST-HOC COMPUTATIONAL ANALYSIS**: you are back-testing a previous forecast (Prompt 3 or 3B) against newly realised data, diagnosing errors, and recalibrating both Monte Carlo and deterministic models before building a new forward 8-week forecast.

?? BEFORE USING THIS PROMPT, PREPARE:

- New Keepa screenshots for the **same ASIN** (latest ~30 days):
  - 3-panel price graph with updated yellow “Bought in past month” line  
  - Updated Buy Box stats (30d)  
  - Updated offers page with stock graphs/mini-graphs  
- Your **previous forecast outputs**:
  - 8-week depletion table(s) (deterministic and/or Monte Carlo)  
  - Scenario assumptions (Best/Realistic/Worst)  
- Financial inputs (selling price, fees, costs) – defaults from the main workflow unless changed.

? EXPECTED OUTPUT (OVERALL MODULE):

- Clear back-test of forecast vs realised behaviour (per seller and market-level).  
- Identified error sources: demand, competition, modelling.  
- Recalibrated Monte Carlo parameters (μ, k, alpha logic) and deterministic parameters (HistWeeklyRate_i, etc.).  
- New reconciled 8-week forecast with updated confidence level and sensitivity analysis.  
- Guidance on how this recalibration should change your future usage of Prompts 3 vs 3B for similar ASINs.

ДДДДДДДДДДДД COPY BELOW THIS LINE ДДДДДДДДДДДД

You are now performing a **BACK-TEST & RECALIBRATION** for an ASIN previously analysed with Prompts 1–4.

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
   - Never exceed Keepa “Sold 30d” per seller (treat “?” as 0 upper bound).

2. **Approximate realised weekly sales** over the latest ~4 weeks:
   - For each major seller with visible stock history, estimate weekly sales per week.  
   - For the total market, cross-check vs the yellow “Bought in past month” line (MonthlySold / 4.3).

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
     - Did Monte Carlo’s Negative Binomial / Dirichlet parameters misrepresent variance or shares?

Summarise Phase A clearly before moving to Phase B.

---

## PHASE B: METHOD 1 – RECALIBRATED MONTE CARLO

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
     - Use or adapt the `keepa_monte_carlo_depletion_simulator.py` script.  
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

## PHASE C: METHOD 2 – RECALIBRATED DETERMINISTIC MODEL

Re-run the deterministic factor-weight model (Prompt 3) with recalibrated inputs.

1. Compute `HistWeeklyRate_i = true_30d_new_i / 4.3` from Phase A.  
2. Use `WeeklyMarketVolume_new` from Phase B.  
3. For each week:
   - Calculate FBA_score, Price_score, Review_score, Stock_score and derive BuyBoxShare_i_week (deterministic, not random).  
   - Apply `Sales_week_i = HistWeeklyRate_i * w_factor + BuyBoxShare_i_week * WeeklyMarketVolume_new` (w_factor per Prompt 3).  
   - Clamp to stock; once stock hits 0, mark seller OOS and redistribute shares among remaining sellers.

4. Generate deterministic **Best / Realistic / Worst** scenarios as in Prompt 3/3B:
   - Best: competitors raise prices +5% or go OOS 20% sooner.  
   - Realistic: today’s observed configuration persists.  
   - Worst: new aggressive FBM undercuts by ~3% with 25% of combined stock.

Produce a single 8-week table per deterministic scenario, plus total weekly sales and cross-check vs `WeeklyMarketVolume_new` (±10 units unless constrained by stock).

---

## PHASE D: COMPARATIVE ANALYSIS (MC vs DETERMINISTIC vs REALISED)

Construct a comparison table for **your listing**:

| Metric           | Monte Carlo (mean) | Deterministic (Realistic) | Realised (last 4w) | Diff vs Realised | % Diff vs Realised |

Include:
- Weekly sales (Weeks 1–8, where applicable).  
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
   - If 10–20%: use 70% Monte Carlo + 30% deterministic.  
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

ДДДДДДДДДДДД END OF PROMPT 5 ДДДДДДДДДДДД

