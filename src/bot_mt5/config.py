import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # python-dotenv is optional at runtime
    load_dotenv = None

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
STATUS_FILE = DATA_DIR / "status_market.json"

if load_dotenv:
    load_dotenv(ROOT_DIR / ".env")


def _bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _symbols_env() -> list[str]:
    raw = os.getenv("SYMBOLS", "EURUSDm,GBPUSDm,USDJPYm,AUDUSDm")
    return [s.strip() for s in raw.split(",") if s.strip()]


@dataclass(frozen=True)
class Settings:
    mt5_login: int
    mt5_password: str
    mt5_server: str
    telegram_token: str
    telegram_chat_id: str
    enable_auto_trade: bool
    symbols: list[str]
    lot_size: float
    magic_number: int
    daily_target_profit: float
    daily_max_loss: float
    scan_interval_seconds: int
    status_file: Path


def get_settings() -> Settings:
    login = os.getenv("MT5_LOGIN", "0")
    return Settings(
        mt5_login=int(login) if login.isdigit() else 0,
        mt5_password=os.getenv("MT5_PASSWORD", ""),
        mt5_server=os.getenv("MT5_SERVER", ""),
        telegram_token=os.getenv("TELEGRAM_TOKEN", ""),
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
        enable_auto_trade=_bool_env("ENABLE_AUTO_TRADE", False),
        symbols=_symbols_env(),
        lot_size=float(os.getenv("LOT_SIZE", "0.01")),
        magic_number=int(os.getenv("MAGIC_NUMBER", "999000")),
        daily_target_profit=float(os.getenv("DAILY_TARGET_PROFIT", "5.0")),
        daily_max_loss=float(os.getenv("DAILY_MAX_LOSS", "3.0")),
        scan_interval_seconds=int(os.getenv("SCAN_INTERVAL_SECONDS", "2")),
        status_file=STATUS_FILE,
    )
