import math
from typing import Dict, List

import pandas as pd


def compute_orders(
    target_tickers: List[str],
    holdings_df: pd.DataFrame,
    prices: pd.Series,
    free_cash: float,
    n_top: int,
) -> pd.DataFrame:
    current_holdings: Dict[str, int] = {}
    total_holdings_value = 0.0

    if not holdings_df.empty:
        for _, row in holdings_df.iterrows():
            ticker = row["Ticker"]
            qty = row["Qty"]
            current_holdings[ticker] = qty
            total_holdings_value += qty * prices.get(ticker, 0)

    total_equity = free_cash + total_holdings_value
    per_slot_capital = total_equity / n_top

    target_quantities: Dict[str, float] = {}
    for ticker in target_tickers:
        price = prices.get(ticker, 0)
        if price <= 0:
            continue
        target_quantities[ticker] = target_quantities.get(ticker, 0) + per_slot_capital / price

    orders = []

    target_set = set(target_quantities.keys())
    for ticker, qty in current_holdings.items():
        if ticker not in target_set:
            orders.append(
                {
                    "Ticker": ticker,
                    "Action": "SELL",
                    "Qty": qty,
                    "Reason": "Liquidate Asset",
                }
            )

    for ticker, target_qty_float in target_quantities.items():
        target_qty = math.floor(target_qty_float)
        current_qty = current_holdings.get(ticker, 0)
        delta = target_qty - current_qty
        if delta > 0:
            orders.append(
                {
                    "Ticker": ticker,
                    "Action": "BUY",
                    "Qty": delta,
                    "Reason": "Rebalance BUY",
                }
            )
        elif delta < 0:
            orders.append(
                {
                    "Ticker": ticker,
                    "Action": "SELL",
                    "Qty": abs(delta),
                    "Reason": "Rebalance SELL",
                }
            )

    orders_df = pd.DataFrame(orders)
    if orders_df.empty:
        return pd.DataFrame(columns=["Ticker", "Action", "Qty", "Reason"])

    execution_order = ["SELL", "BUY"]
    orders_df["Action"] = pd.Categorical(
        orders_df["Action"], categories=execution_order, ordered=True
    )
    orders_df = orders_df.sort_values(by="Action").reset_index(drop=True)

    return orders_df
