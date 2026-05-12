import pandas as pd
from acr.rebalancer import compute_orders


def test_empty_holdings_buys_targets():
    holdings = pd.DataFrame(columns=["Ticker", "Qty", "Avg_price"])
    prices = pd.Series({"A": 100, "B": 200, "C": 300})
    targets = ["A", "B", "C"]

    orders = compute_orders(
        target_tickers=targets,
        holdings_df=holdings,
        prices=prices,
        free_cash=30000,
        n_top=3,
    )

    assert len(orders) == 3
    actions = orders["Action"].tolist()
    assert actions == ["BUY", "BUY", "BUY"]


def test_sell_when_not_in_targets():
    holdings = pd.DataFrame([
        {"Ticker": "SELL_ME", "Qty": 10, "Avg_price": 50},
    ])
    prices = pd.Series({"A": 100, "SELL_ME": 50})
    targets = ["A"]

    orders = compute_orders(
        target_tickers=targets,
        holdings_df=holdings,
        prices=prices,
        free_cash=0,
        n_top=1,
    )

    sells = orders[orders["Action"] == "SELL"]
    assert len(sells) == 1
    assert sells.iloc[0]["Ticker"] == "SELL_ME"
    assert sells.iloc[0]["Reason"] == "Liquidate Asset"


def test_sells_before_buys():
    holdings = pd.DataFrame([
        {"Ticker": "OLD", "Qty": 20, "Avg_price": 50},
    ])
    prices = pd.Series({"NEW": 100, "OLD": 50})
    targets = ["NEW"]

    orders = compute_orders(
        target_tickers=targets,
        holdings_df=holdings,
        prices=prices,
        free_cash=0,
        n_top=1,
    )

    actions = orders["Action"].tolist()
    assert actions[0] == "SELL"
    assert actions[1] == "BUY"


def test_rebalance_zero_target_qty():
    holdings = pd.DataFrame([
        {"Ticker": "A", "Qty": 5, "Avg_price": 100},
    ])
    prices = pd.Series({"A": 1000})
    targets = ["A"]

    orders = compute_orders(
        target_tickers=targets,
        holdings_df=holdings,
        prices=prices,
        free_cash=0,
        n_top=1,
    )

    assert orders.empty


def test_empty_targets_liquidates_all():
    holdings = pd.DataFrame([
        {"Ticker": "A", "Qty": 10, "Avg_price": 50},
    ])
    prices = pd.Series({"A": 100})
    targets = []

    orders = compute_orders(
        target_tickers=targets,
        holdings_df=holdings,
        prices=prices,
        free_cash=0,
        n_top=1,
    )

    assert len(orders) == 1
    assert orders.iloc[0]["Action"] == "SELL"
    assert orders.iloc[0]["Reason"] == "Liquidate Asset"


def test_duplicate_safe_asset_aggregates():
    holdings = pd.DataFrame(columns=["Ticker", "Qty", "Avg_price"])
    prices = pd.Series({"SAFE": 100})
    targets = ["SAFE", "SAFE", "SAFE"]

    orders = compute_orders(
        target_tickers=targets,
        holdings_df=holdings,
        prices=prices,
        free_cash=30000,
        n_top=3,
    )

    assert len(orders) == 1
    assert orders.iloc[0]["Ticker"] == "SAFE"
    assert orders.iloc[0]["Action"] == "BUY"
    assert orders.iloc[0]["Qty"] == 300
