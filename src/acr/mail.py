import base64
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

import pandas as pd
import resend


def _ensure_api_key() -> None:
    if not resend.api_key:
        from dotenv import load_dotenv
        load_dotenv()
        resend.api_key = os.getenv("RESEND_API_KEY")


def send_email(
    to_emails: List[str],
    subject: str,
    html_content: str,
    from_email: str = "INFO <info@algo.jdeep.in>",
    text_content: Optional[str] = None,
    attachments: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    _ensure_api_key()

    if not resend.api_key:
        raise ValueError(
            "RESEND_API_KEY environment variable is not set or couldn't be loaded."
        )

    params: resend.Emails.SendParams = {
        "from": from_email,
        "to": to_emails,
        "subject": subject,
        "html": html_content,
    }

    if text_content:
        params["text"] = text_content

    if attachments:
        params["attachments"] = attachments

    try:
        response = resend.Emails.send(params)
        return response
    except Exception as e:
        print(f"Error sending email via Resend: {e}")
        return {"error": str(e)}


def _build_trade_table(
    orders_df: pd.DataFrame,
    momentum_df: pd.DataFrame,
    prices: pd.Series,
) -> str:
    if orders_df.empty:
        return "<p>No trades required this month.</p>"

    momentum_lookup = dict(zip(momentum_df["Ticker"], momentum_df["Momentum"]))

    rows = []
    for _, row in orders_df.iterrows():
        ticker = row["Ticker"]
        symbol = ticker.replace(".NS", "")
        price = prices.get(ticker)
        price_str = f"₹{price:.2f}" if isinstance(price, (int, float)) else "-"
        momentum = momentum_lookup.get(ticker)
        if momentum is not None:
            momentum_str = f'{momentum:.2%}'
        else:
            momentum_str = "-"

        action = row["Action"]
        color = "#dc2626" if action == "SELL" else "#16a34a"

        rows.append(
            f"<tr>"
            f"<td>{symbol}</td>"
            f"<td>{price_str}</td>"
            f"<td>{momentum_str}</td>"
            f"<td style='color:{color};font-weight:700'>{action}</td>"
            f"<td>{int(row['Qty'])}</td>"
            f"<td>{row['Reason']}</td>"
            f"</tr>"
        )

    header = (
        "<tr>"
        "<th>Ticker</th><th>Price</th><th>Momentum</th>"
        "<th>Action</th><th>Qty</th><th>Reason</th>"
        "</tr>"
    )

    style = (
        "<style>"
        "table{border-collapse:collapse;width:100%;font-family:monospace}"
        "th,td{border:1px solid #d4d4d4;padding:8px 12px;text-align:left}"
        "th{background:#f5f5f5}"
        "</style>"
    )

    return f"{style}<table><thead>{header}</thead><tbody>{''.join(rows)}</tbody></table>"


def send_zerodha_basket_mail(
    basket: List[Dict[str, Any]],
    orders_df: pd.DataFrame,
    momentum_df: pd.DataFrame,
    prices: pd.Series,
    to: List[str],
) -> None:
    subject = f"Zerodha Rebalance Basket - {datetime.now(tz=ZoneInfo('Asia/Kolkata')).strftime('%Y-%m-%d')}"
    repo = os.getenv("GITHUB_REPOSITORY", "JDeepD/asset-class-rotation")

    table = _build_trade_table(orders_df, momentum_df, prices)

    content = (
        f"<h2>Rebalance Trades</h2>"
        f"{table}"
        f"<br>"
        f"<p>Once orders are placed, update your current holdings here: "
        f"<a href='https://github.com/{repo}/issues/new?template=basket_order.yml'>Update Holdings</a></p>"
    )

    attachment = {
        "filename": subject + ".json",
        "content": base64.b64encode(json.dumps(basket, indent=2).encode()).decode(),
    }
    send_email(to, subject, content, attachments=[attachment])
