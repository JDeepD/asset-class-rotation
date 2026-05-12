import pandas as pd
from acr.momentum import latest_prices, rank_by_momentum


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
