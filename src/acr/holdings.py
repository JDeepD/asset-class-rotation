from pathlib import Path

import pandas as pd


def load_holdings(file_path: str | Path) -> pd.DataFrame:
    path = Path(file_path)
    if not path.exists():
        print(
            f"Warning: File {file_path} does not exist. Assuming empty portfolio."
        )
        return pd.DataFrame(columns=["Ticker", "Qty", "Avg_price"])

    try:
        df = pd.read_json(path)
    except Exception as e:
        raise ValueError(f"Error reading current holdings from {file_path}: {e}.")

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
