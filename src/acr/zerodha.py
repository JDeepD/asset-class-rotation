from typing import Any, Dict, List

import pandas as pd


def to_basket(orders_df: pd.DataFrame) -> List[Dict[str, Any]]:
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
