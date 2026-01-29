Appendix A: Output Schemas (add at end)
```json
{
  "phase1_true_sales_schema": {
    "product_id": "string|optional",
    "timeframe_days": 30,
    "monthly_sold_yellow": "number",
    "weekly_market_volume": "number  (monthly_sold_yellow / 4.3)",
    "sellers": [
      {
        "name": "string",
        "type": "FBA|FBM",
        "keepa_30d": "number|null (\"?\"->0)",
        "true_30d": "number",
        "init_stock": "number|null",
        "price_inc_vat": "number|null",
        "reviews": "number|null",
        "restocks": "array of {date_or_range:string, size_estimate?:number}",
        "big_drops_excluded": "array of {date:string, magnitude_estimate?:number}",
        "flat_segments": "array of {date_or_range:string}",
        "notes": "string"
      }
    ],
    "unit_economics": {
      "supplier_inc_vat": "number",
      "shipping_ex_vat": "number",
      "prep_ex_vat": "number",
      "referral_inc_vat": "number",
      "fba_inc_vat": "number",
      "break_even_inc_vat": "number",
      "roi_table": "array of {price_inc_vat:number, roi_percent:number, margin_percent:number}"
    },
    "cross_checks": {
      "sum_true_30d_vs_monthly_sold_delta": "number",
      "comment": "string"
    }
  },

  "phase2_behavior_schema": {
    "product_id": "string|optional",
    "classifications": [
      {
        "seller": "string",
        "behavior": "Aggressive|Reactive|Premium|Premium-Slight|Premium-Moderate|Premium-High",
        "adjustmentFrequency": "qualitative or numeric est.",
        "buyboxPriceCorrelation": "qualitative",
        "evidence": "string"
      }
    ]
  },

  "phase3_standard_schema": {
    "product_id": "string|optional",
    "my_plan": {"units": "number", "entry_price_inc_vat": "number|\"BB-par\""},
    "weekly_rows": [
      {
        "week": "1..8",
        "date_range": "string",
        "sellers": [
          {"seller":"string","type":"FBA|FBM","start":"number","sold":"number","end":"number","my_bb_share_percent":"number|null"}
        ],
        "total_weekly_volume": "number"
      }
    ],
    "scenario": "Best|Realistic|Worst",
    "sellout_week_for_me": "number|null",
    "revenue": "number",
    "gross_profit_ex_vat": "number"
  },

  "phase3b_advanced_schema": {
    "product_id": "string|optional",
    "monte_carlo": {
      "iterations": ">=10000",
      "params": {"demand":"NegBin(mean, k)","bb_shares":"Dirichlet(alpha)"},
      "week_stats": [
        {"week":1,"my_stock_start":0,"my_sold_mean":0,"my_sold_ci95":[0,0],"my_stock_end":0,"my_bb_share_mean":0,"my_bb_share_ci95":[0,0]}
      ],
      "sellout_week_dist": {"week_k": "probability"},
      "revenue_ci95": [0,0],
      "profit_ci95": [0,0]
    },
    "deterministic": {"tables": "... as per Prompt 3", "sellout_weeks": {"Best":0,"Realistic":0,"Worst":0}},
    "comparison": {"metrics":[{"metric":"string","mc_mean":0,"det_realistic":0,"diff":0,"pct_diff":0}]},
    "sensitivity": {"volume_±20%":"impact","price_±0.50":"impact"},
    "final_reconciled": {"sellout_week":"number±band","revenue":"number±band","profit":"number±band","confidence":"High|Medium|Low"}
  },

  "phase4_decision_schema": {
    "decision": "YES|NO",
    "rationale": {"profit_per_unit_ex":"number","roi_percent":"number","sellout_timeline_weeks":"number","cash_cycle":"string","risk_level":"Low|Medium|High","confidence":"High|Medium|Low"},
    "pricing": {"launch_price":"number or BB-par","operational_floor":"number","stretch_ceiling_rule":"string"},
    "if_then_triggers": ["string ..."],
    "watchlist": ["string ..."],
    "reorder_plan": {"ROP_formula":"string","ROP_value":"number","assumptions":"string"}
  }
}
````

## Appendix B: Next-Phase One-Liners

```
Phase 1 → 2: “Classifies each in-stock seller’s pricing behavior vs the Buy Box.”
Phase 2 → 3: “Quick 8-week factor-weighted depletion forecast (three scenarios).”
Phase 2 → 3B: “Rigorous Monte Carlo + deterministic comparison with confidence intervals.”
Phase 3/3B → 4: “Final Go/No-Go decision, pricing guardrails, IF/THEN triggers, watchlist, reorder plan.”
```

## Appendix C: Validation & Cross-Checks (concise, enforceable)
## Appendix C: Validation & Cross-Checks (concise, enforceable)

```
- Never count single-day big drops as sales; exclude and label them.
- Sum of weekly sales across sellers ≈ market volume (±10%).
- No seller sells > stock; clamp and re-normalize shares after OOS.
- Buy Box weights sum to 1.0 every time.
- Phase 3B: check Monte Carlo convergence (e.g., 5k vs 10k runs).
- Final numbers consistent with Phase 1 & 2; if not, explain discrepancy (don’t force-fit).
```

---