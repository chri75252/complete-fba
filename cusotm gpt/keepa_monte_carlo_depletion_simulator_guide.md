## Keepa Monte Carlo Depletion Simulator – Usage Guide

File: `cusotm gpt/keepa_monte_carlo_depletion_simulator.py`

This script implements the Monte Carlo side of **Prompt 3B (Advanced Forecast)**. It is designed to be simple to edit by hand or from a notebook/Code Interpreter.

### 1. Map Phase 1 & 2 outputs into the script

- From **Phase 1 (True Sales Audit)**:
  - Take `MonthlySold_market` from the yellow "Bought in past month" line and set:
    - `MONTHLY_SOLD_MARKET`
    - `WEEKLY_MARKET_VOLUME = MONTHLY_SOLD_MARKET / 4.3`
  - For each seller, compute `hist_weekly_rate = true_30d_sales / 4.3`.
- From **Phase 2 (Pricing Behaviour)**:
  - Keep the seller names and FBA/FBM status.
  - Keep relative pricing and review counts; copy them into the `SELLERS` list.

### 2. Edit the configuration block

In `keepa_monte_carlo_depletion_simulator.py`:

- Set:
  - `MONTHLY_SOLD_MARKET` to your yellow-line monthly sold.
  - `NEG_BINOMIAL_K` if you want to recalibrate dispersion (k) using realized variance.
  - `NUM_ITERATIONS` (>= 10,000 for Prompt 3B).
- Update the `SELLERS` list so each entry has:
  - `name`: seller name (e.g. "REVON LTD", "YOU").
  - `price`: current price (inc VAT).
  - `reviews`: review count (or 0 if none).
  - `stock`: initial stock at forecast start.
  - `is_fba`: `True` for FBA, `False` for FBM.
  - `hist_weekly_rate`: true weekly sales from Phase 1.
  - `is_me`: `True` only for your own listing.

### 3. Run the script

From the repo root:

```bash
cd "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
python "cusotm gpt/keepa_monte_carlo_depletion_simulator.py"
```

The script will print:

- Per-seller **weekly sales** (mean and 95% CI) for Weeks 1–8.
- For **your listing**:
  - Weekly sales (mean, 95% CI).
  - Weekly Buy Box share % (mean, 95% CI).
- Approximate **stockout week distribution** for each seller.

### 4. How to use in Prompt 3B

When running Prompt 3B:

- Treat the script output as the **Monte Carlo component** of Method 1.
- Do **not** fabricate simulated numbers:
  - If you have not run the script (or Code Interpreter) for this ASIN in the current context, clearly mark Monte Carlo quantities as **UNCOMPUTED** and describe only qualitative expectations.
- When the user explicitly requests Monte Carlo:
  - Always interpret **what the Monte Carlo distributions imply**:
    - Sell-out week probability band for your listing.
    - Risk of very slow sell-through (long tail weeks).
    - Upside potential (fast sell-out scenarios).
  - Carry those implications into:
    - The comparative table vs deterministic.
    - The final reconciled forecast.
    - The final decision & pricing strategy (Prompt 4).

### 5. Alignment with Prompt 3B text

- Demand: Negative Binomial with mean `WEEKLY_MARKET_VOLUME / 7`, dispersion `NEG_BINOMIAL_K`.
- Buy Box shares: Dirichlet with alpha built from FBA / Price / Reviews / Stock using weights 65 / 22.5 / 5 / 8.5.
- Horizon: 8 weeks (56 days), no restocks by default.
- All sellers’ weekly sales must be **clamped to stock**, and OOS sellers drop out of future allocation.

You can extend this script (e.g. separate SELLERS_BEST / SELLERS_REAL / SELLERS_WORST) to implement the Best/Realistic/Worst Monte Carlo scenarios described in Prompt 3B, but the core structure already matches the methodology in your knowledge base and chat. 

