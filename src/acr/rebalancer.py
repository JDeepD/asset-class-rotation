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
    target_capital_per_asset = total_equity / n_top

    orders = []

    for ticker, qty in current_holdings.items():
        if ticker not in target_tickers:
            orders.append(
                {
                    "Ticker": ticker,
                    "Action": "SELL",
                    "Qty": qty,
                    "Reason": "Liquidate Asset",
                }
            )

    for ticker in target_tickers:
        current_price = prices.get(ticker)
        if current_price is None or current_price <= 0:
            continue
        target_qty = math.floor(target_capital_per_asset / current_price)
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
