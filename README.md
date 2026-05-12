# Asset Class Rotation

Momentum-based ETF rotation. Ranks Indian ETFs by price momentum, generates Zerodha basket orders, and emails them monthly — all automated via GitHub Actions.

## How It Works

1. Downloads price data for configured ETFs via yfinance
2. Ranks them by momentum (return over a configurable lookback window)
3. Picks the top N performers
4. Computes BUY/SELL orders by diffing against your current holdings
5. Exports orders to Zerodha basket JSON and emails it

<img width="870" height="614" alt="diag" src="https://github.com/user-attachments/assets/a2fdd1d0-acf9-4655-8582-398c407d75b8" />


## Getting Started

### 1. Fork this repo

Click **Fork** on GitHub to create your own copy.

### 2. Set secrets

In your fork, go to **Settings > Secrets and variables > Actions** and add:

| Secret | Description |
|--------|-------------|
| `RESEND_API_KEY` | API key for [Resend](https://resend.com) email service |
| `TO_EMAIL` | Recipient email address |

### 3. Configure your strategy

Edit `config.toml` in your fork:

```toml
[assets]
equity = ["NIFTYBEES.NS", "GOLDBEES.NS" ]

[meta]
N_TOP = 3
MOMENTUM = 100
SAFE_ASSET = "LIQUIDBEES.NS"
INIT_CASH = 10000
```

### 4. Submit your holdings

(If not starting out fresh)

In your fork, create a new issue using the **Submit Holdings** template. Enter your holdings as a CSV list:
```csv
# TICKER(in yfinance format), Qty, Avg_Price

GOLDBEES.NS, 10, 1000
LIQUIDBEES.NS, 5, 500
```

The `parse-holdings` workflow will automatically commit `0xdha-holdings.json` to your repo.

### 5. Done

The **Rebalance** workflow runs automatically on the 1st of every month (4:00 PM IST). 
You can also trigger it manually from the **Actions** tab.

You will receive a JSON file over your email at configured `TO_EMAIL`.

## Navigate to Kite > Orders > Baskets > Create new basket.
<img width="1000" alt="Screenshot 2026-05-12 at 3 19 33 PM" src="https://github.com/user-attachments/assets/676b2474-0892-48e6-8a58-55d4ea96a72c" />


## Click on the upload button to upload a new basket and upload the JSON file.
<img width="1710" height="914" alt="Screenshot 2026-05-12 at 3 24 26 PM" src="https://github.com/user-attachments/assets/eca8b8d7-10d7-4e6c-a7c7-2187edf7d2ff" />


## Verify the orders manually and click on execute.
<img width="1037" height="550" alt="image" src="https://github.com/user-attachments/assets/b2381a5f-5c4b-41fa-b782-d77c297187ed" />


## Updating Holdings

Whenever you execute the orders on Zerodha, create a new issue using the **Submit Holdings** template with your updated portfolio. The holdings JSON will be updated automatically and used in the next monthly rebalance.
