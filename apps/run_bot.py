import sys
import time
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "src"))

from bot_mt5.config import get_settings
from bot_mt5.mt5_client import check_daily_pnl, initialize_mt5, shutdown_mt5
from bot_mt5.storage import write_market_status
from bot_mt5.strategy import analyze_market


def main() -> None:
    settings = get_settings()
    print("=========================================")
    print("🏦 MESIN BOT SMC (Ultimate Sniper + Auto Kill Switch)")
    print("=========================================")

    if not initialize_mt5(settings):
        return

    try:
        while True:
            daily_pnl = check_daily_pnl(settings)
            data = analyze_market(settings, daily_pnl)
            write_market_status(settings.status_file, data)
            now = datetime.now().strftime("%H:%M:%S")

            if daily_pnl >= settings.daily_target_profit:
                print(f"[{now}] 🏆 TARGET TERCAPAI (+${daily_pnl:.2f})! Mesin istirahat.")
            elif daily_pnl <= -settings.daily_max_loss:
                print(f"[{now}] 🛑 CUTLOSS HARIAN (-${abs(daily_pnl):.2f})! Mesin terkunci.")
            else:
                print(f"[{now}] 🔄 PnL Hari Ini: ${daily_pnl:.2f} | Memindai M5 (Sniper Mode)...")

            time.sleep(settings.scan_interval_seconds)
    except KeyboardInterrupt:
        print("\n🛑 Mesin Bot dihentikan oleh user.")
    finally:
        shutdown_mt5()


if __name__ == "__main__":
    main()
