import pandas as pd


def rank_by_momentum(prices_df: pd.DataFrame, n_top: int) -> pd.DataFrame:
    closes = prices_df["Close"].dropna()

    start_prices = closes.iloc[0]
    end_prices = closes.iloc[-1]

    momentum_scores = (end_prices / start_prices) - 1
    top = momentum_scores.sort_values(ascending=False).head(n_top)

    result = top.reset_index()
    result.columns = ["Ticker", "Momentum"]

    return result


def select_targets(momentum_df: pd.DataFrame, safe_asset: str) -> list[str]:
    targets = []
    for _, row in momentum_df.iterrows():
        if row["Momentum"] < 0:
            targets.append(safe_asset)
        else:
            targets.append(row["Ticker"])
    return targets


def latest_prices(prices_df: pd.DataFrame) -> pd.Series:
    closes = prices_df["Close"].dropna()
    return closes.iloc[-1]
