import pandas as pd
from acr.momentum import latest_prices, rank_by_momentum, select_targets


def _make_prices(closes: dict) -> pd.DataFrame:
    """yfinance-style MultiIndex columns."""
    df = pd.DataFrame(closes)
    df.columns = pd.MultiIndex.from_product([["Close"], list(df.columns)])
    return df


def test_rank_by_momentum_basic():
    prices = _make_prices({
        "A": [100, 110, 120],
        "B": [50, 55, 60],
        "C": [200, 190, 180],
        "D": [30, 33, 39],
        "E": [10, 12, 15],
    })
    result = rank_by_momentum(prices, n_top=2)

    assert len(result) == 2
    assert list(result.columns) == ["Ticker", "Momentum"]
    assert result.iloc[0]["Ticker"] == "E"
    assert result.iloc[1]["Ticker"] == "D"


def test_rank_by_momentum_all_same():
    prices = _make_prices({
        "A": [100, 100, 100],
        "B": [100, 100, 100],
    })
    result = rank_by_momentum(prices, n_top=2)
    assert len(result) == 2
    assert (result["Momentum"] == 0.0).all()


def test_latest_prices():
    prices = _make_prices({
        "A": [10, 20, 30],
        "B": [5, 10, 15],
    })
    result = latest_prices(prices)

    assert result["A"] == 30
    assert result["B"] == 15


def test_select_targets_all_positive():
    momentum_df = pd.DataFrame([
        {"Ticker": "A", "Momentum": 0.05},
        {"Ticker": "B", "Momentum": 0.03},
    ])
    targets = select_targets(momentum_df, safe_asset="SAFE")
    assert targets == ["A", "B"]


def test_select_targets_some_negative():
    momentum_df = pd.DataFrame([
        {"Ticker": "A", "Momentum": 0.05},
        {"Ticker": "B", "Momentum": -0.02},
        {"Ticker": "C", "Momentum": 0.03},
    ])
    targets = select_targets(momentum_df, safe_asset="SAFE")
    assert targets == ["A", "SAFE", "C"]


def test_select_targets_all_negative():
    momentum_df = pd.DataFrame([
        {"Ticker": "A", "Momentum": -0.05},
        {"Ticker": "B", "Momentum": -0.03},
        {"Ticker": "C", "Momentum": -0.01},
    ])
    targets = select_targets(momentum_df, safe_asset="SAFE")
    assert targets == ["SAFE", "SAFE", "SAFE"]
