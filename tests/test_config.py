import pytest
from acr.config import Config


def test_config_from_toml(tmp_path):
    toml_content = """
[assets]
equity = ["NIFTYBEES.NS", "GOLDBEES.NS"]

[meta]
N_TOP = 3
MOMENTUM = 100
SAFE_ASSET = "LIQUIDBEES.NS"
INIT_CASH = 10000
"""
    path = tmp_path / "config.toml"
    path.write_text(toml_content)

    config = Config.from_toml(path)

    assert config.assets == ["NIFTYBEES.NS", "GOLDBEES.NS"]
    assert config.n_top == 3
    assert config.momentum == 100
    assert config.safe_asset == "LIQUIDBEES.NS"
    assert config.init_cash == 10000


def test_config_missing_file():
    with pytest.raises(ValueError, match="Config file not found"):
        Config.from_toml("nonexistent.toml")


def test_config_empty_assets(tmp_path):
    toml_content = """
[assets]
equity = []

[meta]
N_TOP = 3
MOMENTUM = 100
SAFE_ASSET = "LIQUIDBEES.NS"
INIT_CASH = 10000
"""
    path = tmp_path / "config.toml"
    path.write_text(toml_content)

    with pytest.raises(ValueError, match="Assets list cannot be empty"):
        Config.from_toml(path)


def test_config_invalid_n_top(tmp_path):
    toml_content = """
[assets]
equity = ["NIFTYBEES.NS"]

[meta]
N_TOP = 0
MOMENTUM = 100
SAFE_ASSET = "LIQUIDBEES.NS"
INIT_CASH = 10000
"""
    path = tmp_path / "config.toml"
    path.write_text(toml_content)

    with pytest.raises(ValueError, match="Invalid N_TOP"):
        Config.from_toml(path)


def test_config_invalid_momentum(tmp_path):
    toml_content = """
[assets]
equity = ["NIFTYBEES.NS"]

[meta]
N_TOP = 3
MOMENTUM = -1
SAFE_ASSET = "LIQUIDBEES.NS"
INIT_CASH = 10000
"""
    path = tmp_path / "config.toml"
    path.write_text(toml_content)

    with pytest.raises(ValueError, match="Invalid MOMENTUM"):
        Config.from_toml(path)
