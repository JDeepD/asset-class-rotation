from datetime import datetime, timedelta
from typing import List

import pandas as pd
import yfinance as yf


def download_prices(
    tickers: List[str],
    lookback_days: int,
    end: datetime | None = None,
    interval: str = "1d",
) -> pd.DataFrame:
    if end is None:
        end = datetime.today()
    start = end - timedelta(days=lookback_days)

    try:
        df = yf.download(tickers, start=start, end=end, interval=interval)
    except Exception as e:
        raise RuntimeError(f"Failed to download data from yfinance: {e}") from e

    if df is None or df.empty:
        raise RuntimeError("No data returned from yfinance.")

    return df
