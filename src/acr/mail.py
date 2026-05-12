import base64
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from zoneinfo import ZoneInfo
from typing import Any, Dict, List, Optional

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


def send_zerodha_basket_mail(basket: List[Dict[str, Any]], to: List[str]) -> None:
    subject = f"Zerodha Rebalance Basket - {datetime.now(tz=ZoneInfo('Asia/Kolkata')).strftime('%Y-%m-%d')}"
    repo = os.getenv("GITHUB_REPOSITORY", "JDeepD/asset-class-rotation")
    content = f'<h1>PFA: Rebalance Basket</h1><p>Once orders are placed, update your current holdings here: <a href="https://github.com/{repo}/issues/new?template=basket_order.yml">Update Holdings</a></p>'
    attachment = {
        "filename": subject + ".json",
        "content": base64.b64encode(json.dumps(basket, indent=2).encode()).decode(),
    }
    send_email(to, subject, content, attachments=[attachment])
