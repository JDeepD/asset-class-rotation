import os
import resend
from dotenv import load_dotenv
from typing import List, Optional, Dict, Any
import base64
import json
from datetime import datetime

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


def send_zerodha_basket_mail(basket, to: List[str]):
    subject = f"Zerodha Rebalance Basket - {datetime.today().strftime('%Y-%m-%d')}"
    content = '<h1>PFA: Rebalance Basket</h1><p>Once orders are placed, update your current holdings here: <a href="https://github.com/JDeepD/asset-class-rotation/issues/new?template=basket_order.yml">Update Holdings</a></p>'
    attachment = {
        "filename": subject + ".json",
        "content": base64.b64encode(json.dumps(basket, indent=2).encode()).decode(),
    }
    send_email(to, subject, content, attachments=[attachment])


if __name__ == "__main__":
    result = send_email(
        to_emails=["jaydeepjd.1125@gmail.com"],
        subject="Welcome to the platform!",
        html_content="<h1>Hello!</h1><p>Thanks for signing up.</p>",
    )

    if "error" in result:
        print("Failed to send email.")
    else:
        print(f"Email sent successfully! Response: {result}")
