"""
Keepa Monte Carlo Depletion Simulator
-------------------------------------

Self-contained Monte Carlo engine for an Amazon UK ASIN using Keepa-derived inputs.

Usage overview:
1. Edit MONTHLY_SOLD_MARKET, NEG_BINOMIAL_K, NUM_ITERATIONS if needed.
2. Edit the SELLERS list so that each Seller reflects:
   - name
   - FBA/FBM flag
   - price (inc VAT)
   - reviews (count)
   - initial stock
   - hist_weekly_rate (true 30d sales / 4.3 from Phase 1)
   - is_me flag for your listing
3. Run this file with Python 3.12+:
      python keepa_monte_carlo_depletion_simulator.py
4. Use the printed summary tables as the Monte Carlo component for Prompt 3B.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np


# =============================
# CONFIG: EDIT THIS SECTION ONLY
# =============================

# 1) Market-level settings ----------------------------------------

# Monthly units sold from Keepa yellow line ("Bought in past month").
MONTHLY_SOLD_MARKET: float = 400.0

# Weekly market volume implied by yellow line.
WEEKLY_MARKET_VOLUME: float = MONTHLY_SOLD_MARKET / 4.3

# Negative Binomial dispersion parameter k (higher = less variance).
NEG_BINOMIAL_K: float = 1.2

# Number of weeks and iterations
NUM_WEEKS: int = 8
NUM_DAYS: int = NUM_WEEKS * 7
NUM_ITERATIONS: int = 10_000
RANDOM_SEED: int = 42


@dataclass
class Seller:
    name: str
    price: float
    reviews: int
    stock: int
    is_fba: bool
    hist_weekly_rate: float
    is_me: bool = False


# Example SELLERS configuration – replace with your actual Phase 1/2 data
SELLERS: List[Seller] = [
    Seller("Example FBM", price=10.75, reviews=3_000, stock=50, is_fba=False, hist_weekly_rate=20.0),
    Seller("Example FBA", price=11.25, reviews=50, stock=40, is_fba=True, hist_weekly_rate=18.0),
    Seller("ME", price=11.50, reviews=0, stock=60, is_fba=True, hist_weekly_rate=0.0, is_me=True),
]


# 2) Weighting and scoring ----------------------------------------

W_FBA = 0.65
W_PRICE = 0.225
W_REVIEWS = 0.05
W_STOCK = 0.085


def build_alpha_vector(sellers: List[Seller], stocks: np.ndarray) -> np.ndarray:
    """
    Build Dirichlet alpha parameters for in-stock sellers using
    FBA / Price / Reviews / Stock factors.
    """
    assert len(sellers) == len(stocks)

    prices = np.array([s.price for s in sellers], dtype=float)
    reviews = np.array([max(s.reviews, 0) for s in sellers], dtype=float)
    max_reviews = max(reviews.max(), 1.0)
    min_price = prices.min()
    total_stock = max(stocks.sum(), 1.0)

    fba_score = np.array([1.0 if s.is_fba else 0.3 for s in sellers], dtype=float)
    price_score = np.clip(min_price / prices, 0.80, 1.10)
    review_score = reviews / max_reviews
    stock_score = stocks / total_stock

    alpha = (
        W_FBA * fba_score
        + W_PRICE * price_score
        + W_REVIEWS * review_score
        + W_STOCK * stock_score
    )

    # Safety: ensure strictly positive alphas
    alpha = np.clip(alpha, 1e-6, None)
    return alpha


# 3) Monte Carlo core ---------------------------------------------

def negbin_params_from_mean_k(mean: float, k: float) -> Tuple[float, float]:
    """
    Convert Negative Binomial parameterization (mean, k)
    into (r, p) for numpy.random.negative_binomial.

    mean = r(1-p)/p
    var = mean + mean^2 / k
    """
    r = k
    p = r / (r + mean)
    return r, p


def simulate_paths(
    sellers: List[Seller],
    weekly_market_volume: float,
    k: float,
    num_weeks: int,
    num_iterations: int,
    rng: np.random.Generator,
) -> Dict[str, np.ndarray]:
    num_sellers = len(sellers)
    num_days = num_weeks * 7

    sales_paths = np.zeros((num_iterations, num_sellers, num_days), dtype=float)
    bb_share_paths = np.zeros((num_iterations, num_sellers, num_days), dtype=float)
    stockout_day = np.full((num_iterations, num_sellers), num_days + 1, dtype=int)

    mean_daily = weekly_market_volume / 7.0
    r, p = negbin_params_from_mean_k(mean_daily, k)

    for it in range(num_iterations):
        stocks = np.array([s.stock for s in sellers], dtype=float)
        in_play = stocks > 0

        for t in range(num_days):
            idx = np.where(in_play)[0]
            if not len(idx):
                break

            active_sellers = [sellers[i] for i in idx]
            active_stocks = stocks[idx]

            alpha = build_alpha_vector(active_sellers, active_stocks)
            shares = rng.dirichlet(alpha)
            demand = rng.negative_binomial(r, p)

            if demand <= 0:
                continue

            alloc = rng.multinomial(demand, shares)

            for local_pos, seller_idx in enumerate(idx):
                potential = alloc[local_pos]
                sale = min(potential, stocks[seller_idx])
                sales_paths[it, seller_idx, t] = sale
                bb_share_paths[it, seller_idx, t] = shares[local_pos]
                stocks[seller_idx] -= sale

                if stocks[seller_idx] <= 0 and stockout_day[it, seller_idx] == num_days + 1:
                    stockout_day[it, seller_idx] = t + 1

            in_play = stocks > 0

    return {
        "sales_paths": sales_paths,
        "bb_share_paths": bb_share_paths,
        "stockout_day": stockout_day,
    }


def summarise_results(
    sellers: List[Seller],
    raw: Dict[str, np.ndarray],
    num_weeks: int,
) -> None:
    sales_paths = raw["sales_paths"]
    bb_share_paths = raw["bb_share_paths"]
    stockout_day = raw["stockout_day"]

    num_iterations, num_sellers, num_days = sales_paths.shape
    assert num_days == num_weeks * 7

    sales_by_week = sales_paths.reshape(num_iterations, num_sellers, num_weeks, 7).sum(axis=3)
    bb_by_week = bb_share_paths.reshape(num_iterations, num_sellers, num_weeks, 7).mean(axis=3)

    me_idx: Optional[int] = None
    for i, s in enumerate(sellers):
        if s.is_me:
            me_idx = i
            break

    print("\n==== WEEKLY SALES (mean, 2.5%, 97.5%) ====")
    for i, s in enumerate(sellers):
        weekly = sales_by_week[:, i, :]
        mean = weekly.mean(axis=0)
        lo = np.percentile(weekly, 2.5, axis=0)
        hi = np.percentile(weekly, 97.5, axis=0)
        print(f"\nSeller: {s.name}")
        for w in range(num_weeks):
            print(
                f"  Week {w+1}: mean={mean[w]:.1f}, "
                f"CI95=({lo[w]:.1f}, {hi[w]:.1f})"
            )

    if me_idx is not None:
        me_weekly = sales_by_week[:, me_idx, :]
        me_bb = bb_by_week[:, me_idx, :]
        print("\n==== MY LISTING: WEEKLY SALES & BB SHARE (mean, CI95) ====")
        for w in range(num_weeks):
            mean_sales = me_weekly[:, w].mean()
            lo_sales = np.percentile(me_weekly[:, w], 2.5)
            hi_sales = np.percentile(me_weekly[:, w], 97.5)

            mean_bb = 100 * me_bb[:, w].mean()
            lo_bb = 100 * np.percentile(me_bb[:, w], 2.5)
            hi_bb = 100 * np.percentile(me_bb[:, w], 97.5)

            print(
                f"Week {w+1}: "
                f"Sales mean={mean_sales:.1f}, CI95=({lo_sales:.1f}, {hi_sales:.1f}); "
                f"BB% mean={mean_bb:.1f}, CI95=({lo_bb:.1f}, {hi_bb:.1f})"
            )

    print("\n==== STOCKOUT WEEK DISTRIBUTION (per seller) ====")
    for i, s in enumerate(sellers):
        days = stockout_day[:, i]
        # Map day index -> week index (1..num_weeks), >num_days => no stockout.
        weeks = np.where(days <= num_weeks * 7, (days - 1) // 7 + 1, 0)
        if (weeks > 0).any():
            print(f"\nSeller: {s.name}")
            for w in range(1, num_weeks + 1):
                prob = (weeks == w).mean()
                if prob > 0:
                    print(f"  P(stockout by week {w}) ~ {prob*100:.1f}%")


def main() -> None:
    rng = np.random.default_rng(RANDOM_SEED)
    raw = simulate_paths(
        sellers=SELLERS,
        weekly_market_volume=WEEKLY_MARKET_VOLUME,
        k=NEG_BINOMIAL_K,
        num_weeks=NUM_WEEKS,
        num_iterations=NUM_ITERATIONS,
        rng=rng,
    )
    summarise_results(SELLERS, raw, NUM_WEEKS)


if __name__ == "__main__":
    main()

