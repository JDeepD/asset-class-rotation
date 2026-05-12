import pandas as pd
from acr.zerodha import to_basket


def test_empty_orders():
    orders = pd.DataFrame(columns=["Ticker", "Action", "Qty", "Reason"])
    basket = to_basket(orders)
    assert basket == []


def test_to_basket_basic():
    orders = pd.DataFrame([
        {"Ticker": "GOLDBEES.NS", "Action": "BUY", "Qty": 10, "Reason": "Rebalance BUY"},
        {"Ticker": "NIFTYBEES.NS", "Action": "SELL", "Qty": 5, "Reason": "Liquidate Asset"},
    ])

    basket = to_basket(orders)

    assert len(basket) == 2
    assert basket[0]["instrument"]["tradingsymbol"] == "GOLDBEES"
    assert basket[0]["instrument"]["exchange"] == "NSE"
    assert basket[0]["params"]["transactionType"] == "BUY"
    assert basket[0]["params"]["quantity"] == 10
    assert basket[0]["params"]["product"] == "CNC"
    assert basket[0]["params"]["orderType"] == "MARKET"

    assert basket[1]["instrument"]["tradingsymbol"] == "NIFTYBEES"
    assert basket[1]["params"]["transactionType"] == "SELL"
    assert basket[1]["params"]["quantity"] == 5


def test_to_basket_strips_ns_suffix():
    orders = pd.DataFrame([
        {"Ticker": "TECH.NS", "Action": "BUY", "Qty": 3, "Reason": "Rebalance BUY"},
    ])

    basket = to_basket(orders)
    assert basket[0]["instrument"]["tradingsymbol"] == "TECH"
