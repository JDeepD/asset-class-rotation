import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class Config:
    assets: List[str]
    n_top: int
    momentum: int
    safe_asset: str
    init_cash: float

    @classmethod
    def from_toml(cls, path: str | Path) -> "Config":
        path = Path(path)
        try:
            with open(path, "rb") as f:
                data = tomllib.load(f)
        except FileNotFoundError:
            raise ValueError(f"Config file not found: {path}")

        assets = list(data["assets"]["equity"])
        meta = data["meta"]

        config = cls(
            assets=assets,
            n_top=meta["N_TOP"],
            momentum=meta["MOMENTUM"],
            safe_asset=meta["SAFE_ASSET"],
            init_cash=meta["INIT_CASH"],
        )
        config._validate()
        return config

    def _validate(self) -> None:
        if not self.assets:
            raise ValueError("Assets list cannot be empty.")
        if not all(isinstance(a, str) for a in self.assets):
            raise TypeError("All items in 'assets' must be strings.")
        if self.n_top <= 0:
            raise ValueError(f"Invalid N_TOP: {self.n_top}.")
        if self.momentum <= 0:
            raise ValueError(f"Invalid MOMENTUM: {self.momentum}.")
        if self.init_cash < 0:
            raise ValueError(f"Invalid INIT_CASH: {self.init_cash}.")
