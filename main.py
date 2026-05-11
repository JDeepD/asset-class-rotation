import tomllib
from asset_class_rotation import AssetClassRotation


def get_data(file_path: str):
    try:
        with open(file_path, "rb") as f:
            data = tomllib.load(f)
        return data
    except FileNotFoundError:
        raise ValueError(f"File not found: {file_path}")


def main():
    config = get_data("config.toml")
    etfs = config["assets"]["equity"]
    meta = config["meta"]

    acr = AssetClassRotation(
        meta["N_TOP"], etfs, meta["SAFE_ASSET"], meta["MOMENTUM"], meta["FREQUENCY"]
    )

    res = acr.rebalance("0xdha-holdings.json", free_cash=meta["INIT_CASH"])
    basket = acr.export_to_zerodha_basket(res)

    print(basket)


if __name__ == "__main__":
    main()
