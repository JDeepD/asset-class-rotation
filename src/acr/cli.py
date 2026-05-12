import os

from dotenv import load_dotenv

from acr.config import Config
from acr.downloader import download_prices
from acr.holdings import load_holdings
from acr.mail import send_zerodha_basket_mail
from acr.momentum import latest_prices, rank_by_momentum, select_targets
from acr.rebalancer import compute_orders
from acr.zerodha import to_basket


def main() -> None:
    load_dotenv()

    config = Config.from_toml("config.toml")

    prices_df = download_prices(config.assets, config.momentum)
    momentum_df = rank_by_momentum(prices_df, config.n_top)
    prices = latest_prices(prices_df)

    target_tickers = select_targets(momentum_df, config.safe_asset)

    holdings_df = load_holdings("0xdha-holdings.json")

    orders_df = compute_orders(
        target_tickers=target_tickers,
        holdings_df=holdings_df,
        prices=prices,
        free_cash=config.init_cash,
        n_top=config.n_top,
    )

    basket = to_basket(orders_df)
    to_email = os.getenv("TO_EMAIL")
    send_zerodha_basket_mail(basket, [to_email])


if __name__ == "__main__":
    main()
