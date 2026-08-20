from datetime import datetime

import MetaTrader5 as mt5

from .config import Settings
from .notifier import send_telegram_alert


def initialize_mt5(settings: Settings) -> bool:
    print("Mencoba menghubungkan ke MetaTrader 5...")
    if not settings.mt5_login or not settings.mt5_password or not settings.mt5_server:
        print("❌ Konfigurasi MT5 belum lengkap. Isi .env dulu.")
        return False

    if not mt5.initialize(login=settings.mt5_login, password=settings.mt5_password, server=settings.mt5_server):
        print(f"❌ Gagal login MT5. Error code: {mt5.last_error()}")
        return False

    print("✅ Berhasil login ke MetaTrader 5!")
    return True


def shutdown_mt5() -> None:
    mt5.shutdown()


def has_open_position(settings: Settings) -> bool:
    positions = mt5.positions_get()
    if positions is None:
        return False
    return any(p.magic == settings.magic_number for p in positions)


def check_daily_pnl(settings: Settings) -> float:
    now = datetime.now()
    today_start = datetime(now.year, now.month, now.day)
    deals = mt5.history_deals_get(today_start, now)
    daily_pnl = 0.0

    if deals is not None:
        for deal in deals:
            if deal.magic == settings.magic_number:
                daily_pnl += deal.profit

    return daily_pnl


def send_order(settings: Settings, symbol: str, order_type: int, price: float, sl: float, tp: float):
    if not settings.enable_auto_trade:
        print(f"🧪 DRY-RUN: sinyal {symbol} terdeteksi, order tidak dikirim.")
        return None

    if has_open_position(settings):
        print(f"⚠️ Sinyal {symbol} diabaikan: Masih ada posisi jalan!")
        return None

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": settings.lot_size,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": settings.magic_number,
        "comment": "SMC Sniper Mode",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"⚠️ Gagal kirim order {symbol}: {result.comment}")
    else:
        print(f"✅ BINGO SMC! Order {symbol} masuk! (Mode Sniper Aktif)")
        order_label = "BUY 🚀" if order_type == mt5.ORDER_TYPE_BUY else "SELL 💥"
        message = (
            f"<b>✅ ENTRY SCALPING (SNIPER MODE)</b>\n\n"
            f"<b>Pair:</b> {symbol}\n"
            f"<b>Action:</b> {order_label}\n"
            f"<b>Harga Entry:</b> {price}\n"
            f"<b>SL Dinamis:</b> {sl:.5f}\n"
            f"<b>TP Dinamis:</b> {tp:.5f}\n\n"
            f"<i>Mesin Bot otomatis eksekusi!</i> 🤖"
        )
        send_telegram_alert(settings, message)
    return result
