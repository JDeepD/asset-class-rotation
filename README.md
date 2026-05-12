# Asset Class Rotation

Momentum-based ETF rotation bot. Ranks Indian ETFs by price momentum, generates Zerodha basket orders, and emails them monthly — all automated via GitHub Actions.

## How It Works

1. Downloads price data for configured ETFs via yfinance
2. Ranks them by momentum (return over a configurable lookback window)
3. Picks the top N performers
4. Computes BUY/SELL orders by diffing against your current holdings
5. Exports orders to Zerodha basket JSON and emails it

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
equity = ["NIFTYBEES.NS", "GOLDBEES.NS", ...]

[meta]
N_TOP = 3          # number of top ETFs to hold
MOMENTUM = 100     # lookback window in days
SAFE_ASSET = "LIQUIDBEES.NS"
INIT_CASH = 10000  # initial cash for fresh portfolios
```

### 4. Submit your holdings

(If not starting out fresh)

In your fork, create a new issue using the **Submit Holdings** template. Enter your holdings as a CSV list:

```
GOLDBEES.NS, 10, 1000
LIQUIDBEES.NS, 5, 500
```

The `parse-holdings` workflow will automatically commit `0xdha-holdings.json` to your repo.

### 5. Done

The **Rebalance** workflow runs automatically on the 1st of every month (4:00 PM IST). 
You can also trigger it manually from the **Actions** tab.

You will receive a JSON file over your email at configured `TO_EMAIL`.

Navigate to Kite > Orders > Baskets > Create new basket.

Click on the upload button to upload a new basket and upload the JSON file.

Verify the orders manually and click on execute.

## Updating Holdings

Whenever you execute the orders on Zerodha, create a new issue using the **Submit Holdings** template with your updated portfolio. The holdings JSON will be updated automatically and used in the next monthly rebalance.
