import pandas as pd
from acr.mail import _build_trade_table


def test_build_trade_table_empty():
    orders = pd.DataFrame(columns=["Ticker", "Action", "Qty", "Reason"])
    momentum = pd.DataFrame(columns=["Ticker", "Momentum"])
    prices = pd.Series(dtype=float)

    html = _build_trade_table(orders, momentum, prices)
    assert "No trades required" in html


def test_build_trade_table_with_trades():
    orders = pd.DataFrame([
        {"Ticker": "GOLDBEES.NS", "Action": "BUY", "Qty": 10, "Reason": "Rebalance BUY"},
        {"Ticker": "NIFTYBEES.NS", "Action": "SELL", "Qty": 5, "Reason": "Liquidate Asset"},
    ])
    momentum = pd.DataFrame([
        {"Ticker": "GOLDBEES.NS", "Momentum": 0.05},
        {"Ticker": "NIFTYBEES.NS", "Momentum": 0.12},
    ])
    prices = pd.Series({"GOLDBEES.NS": 65.50, "NIFTYBEES.NS": 280.0})

    html = _build_trade_table(orders, momentum, prices)

    assert "GOLDBEES" in html
    assert "NIFTYBEES" in html
    assert "5.00%" in html
    assert "12.00%" in html
    assert "BUY" in html
    assert "SELL" in html
    assert "10" in html
    assert "5" in html
    assert "Rebalance BUY" in html
    assert "Liquidate Asset" in html
    assert "₹65.50" in html
    assert "₹280.00" in html


def test_build_trade_table_ticker_without_momentum():
    orders = pd.DataFrame([
        {"Ticker": "OLD.NS", "Action": "SELL", "Qty": 3, "Reason": "Liquidate Asset"},
    ])
    momentum = pd.DataFrame(columns=["Ticker", "Momentum"])
    prices = pd.Series({"OLD.NS": 42.0})

    html = _build_trade_table(orders, momentum, prices)

    assert "OLD" in html
    assert "-" in html
    assert "SELL" in html
