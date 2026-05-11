import yfinance as yf
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import math

import pandas as pd


@dataclass
class AssetClassRotation:
    n_top: int
    assets: list[str]
    safe_asset: str
    momentum: int
    freq: str

    def __post_init__(self) -> None:
        if self.freq not in ["D", "W", "M", "Y"]:
            raise ValueError(f"Invalid Frequency: {self.freq}")

        if not self.assets:
            raise ValueError("Assets list cannot be empty.")

        if not all(isinstance(asset, str) for asset in self.assets):
            raise TypeError("All items in 'assets' must be strings.")

        if self.n_top <= 0:
            raise ValueError(f"Invalid N_TOP: {self.n_top}.")

        if self.momentum <= 0:
            raise ValueError(f"Invalid momentum: {self.momentum}.")

    def export_to_zerodha_basket(
        self, orders_df: pd.DataFrame, file_path: str = "zerodha_basket.json"
    ):
        basket = []
        if orders_df.empty:
            return basket

        for weight, row in orders_df.iterrows():
            symbol = str(row["Ticker"]).replace(".NS", "")
            order = {
                "weight": weight,
                "instrument": {"tradingsymbol": symbol, "exchange": "NSE"},
                "params": {
                    "transactionType": row["Action"],
                    "orderType": "MARKET",
                    "product": "CNC",
                    "quantity": int(row["Qty"]),
                    "price": 0,
                    "triggerPrice": 0,
                    "validity": "DAY",
                    "variety": "regular",
                },
            }
            basket.append(order)

        return basket

    def rebalance(self, file_path, free_cash: float = 0.0):
        strategy_df = self.strategy()
        target_tickers = strategy_df["Ticker"].tolist()
        holdings_df = self.get_current_holdings(file_path)

        total_holdings_value = 0.0
        current_holdings_dict = {}

        if not holdings_df.empty:
            for _, row in holdings_df.iterrows():
                ticker = row["Ticker"]
                qty = row["Qty"]
                current_holdings_dict[ticker] = qty
                current_price = self._latest_prices.get(ticker)
                total_holdings_value += qty * current_price

        total_equity = free_cash + total_holdings_value
        target_capital_per_asset = total_equity / self.n_top
        orders = []

        for ticker, qty in current_holdings_dict.items():
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
            current_price = self._latest_prices.get(ticker)
            target_qty = math.floor(target_capital_per_asset / current_price)
            current_qty = current_holdings_dict.get(ticker, 0)
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

        # SELL orders should be executed before BUY orders
        # (Even though Zerodha settles the amount on T+1, it is kept as a good practice)
        execution_order = ["SELL", "BUY"]
        orders_df["Action"] = pd.Categorical(
            orders_df["Action"], categories=execution_order, ordered=True
        )
        orders_df = orders_df.sort_values(by="Action").reset_index(drop=True)

        return orders_df

    def get_current_holdings(self, file_path: str):
        path = Path(file_path)
        if not path.exists():
            print(
                f"Warning: File {file_path} does not exist. Assuming empty portfolio."
            )
            return pd.DataFrame(columns=["Ticker", "Qty", "Avg_price"])

        try:
            df = pd.read_json(path)
        except Exception as e:
            raise Exception(f"Error reading current holdings from {file_path}: {e}.")

        if df.empty:
            return pd.DataFrame(columns=["Ticker", "Qty", "Avg_price"])

        df = (
            df.groupby("Ticker")
            .apply(
                lambda x: pd.Series(
                    {
                        "Qty": x["Qty"].sum(),
                        "Avg_price": (x["Qty"] * x["Avg_price"]).sum() / x["Qty"].sum(),
                    }
                )
            )
            .reset_index()
        )

        return df

    def strategy(self) -> pd.DataFrame:
        end = datetime.today()
        start = end - timedelta(days=self.momentum)
        df = self._download(start, end)

        prices = df["Close"].dropna()

        start_prices = prices.iloc[0]
        end_prices = prices.iloc[-1]

        self._latest_prices = end_prices

        momentum_scores = (end_prices / start_prices) - 1
        top_assets = momentum_scores.sort_values(ascending=False).head(self.n_top)

        result = top_assets.reset_index()
        result.columns = ["Ticker", "Momentum"]

        return result

    def _download(
        self, start: datetime, end: datetime, interval: str = "1d"
    ) -> pd.DataFrame:
        try:
            df = yf.download(self.assets, start=start, end=end, interval=interval)

            if df is None or df.empty:
                raise Exception("No data returned from yfinance.")

            return df

        except Exception as e:
            raise RuntimeError(f"Failed to download data from yfinance: {e}") from e


if __name__ == "__main__":
    acr = AssetClassRotation(1, ["GOLDBEES.NS"], "GOLDBEES.NS", 100, "M")
    data = acr.strategy()
    print(data)
