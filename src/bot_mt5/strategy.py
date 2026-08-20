import MetaTrader5 as mt5
import pandas as pd
import ta

from .config import Settings
from .mt5_client import send_order

TIMEFRAME = mt5.TIMEFRAME_M5


def analyze_market(settings: Settings, daily_pnl: float) -> list[dict]:
    market_data = []
    trade_allowed = settings.enable_auto_trade
    status_bot = "AKTIF 🟢" if settings.enable_auto_trade else "DRY-RUN 🧪"

    if daily_pnl >= settings.daily_target_profit:
        trade_allowed = False
        status_bot = f"TARGET TERCAPAI 🏆 (+${daily_pnl:.2f})"
    elif daily_pnl <= -settings.daily_max_loss:
        trade_allowed = False
        status_bot = f"CUTLOSS HARIAN 🛑 (-${abs(daily_pnl):.2f})"

    for symbol in settings.symbols:
        mt5.symbol_select(symbol, True)
        rates = mt5.copy_rates_from_pos(symbol, TIMEFRAME, 0, 250)
        clean_symbol = symbol.removesuffix("m")

        if rates is None or len(rates) == 0:
            market_data.append(_row(clean_symbol, "ERROR", "NO DATA", "ERROR", daily_pnl, status_bot))
            continue

        df = pd.DataFrame(rates)
        df["ema_200"] = ta.trend.EMAIndicator(df["close"], window=200).ema_indicator()
        df["fvg_bull"] = df["low"].shift(1) > df["high"].shift(3)
        df["fvg_bear"] = df["high"].shift(1) < df["low"].shift(3)
        df["bullish_ob"] = (df["close"].shift(1) > df["open"].shift(2)) & (df["close"].shift(2) < df["open"].shift(2))
        df["bearish_ob"] = (df["close"].shift(1) < df["open"].shift(2)) & (df["close"].shift(2) > df["open"].shift(2))
        df["atr"] = ta.volatility.AverageTrueRange(
            high=df["high"], low=df["low"], close=df["close"], window=14
        ).average_true_range()

        latest = df.iloc[-1]
        tick = mt5.symbol_info_tick(symbol)
        current_price = tick.bid if tick is not None else latest["close"]
        signal = "HOLD ⏳" if trade_allowed else "STANDBY 💤"
        potential = "RENDAH ⚪"
        score = 0

        if trade_allowed and tick is not None:
            sl_distance = df["atr"].iloc[-1] * 1.5
            tp_distance = sl_distance * 2.0

            if latest["close"] > latest["ema_200"]:
                if latest["fvg_bull"]:
                    score += 1
                if latest["bullish_ob"]:
                    score += 1

                if score == 2:
                    potential = "TINGGI 🌟"
                    signal = "BUY (SMC) 🚀"
                    send_order(settings, symbol, mt5.ORDER_TYPE_BUY, tick.ask, float(tick.ask - sl_distance), float(tick.ask + tp_distance))
                elif score == 1:
                    potential = "MENENGAH 🟡"

            elif latest["close"] < latest["ema_200"]:
                if latest["fvg_bear"]:
                    score += 1
                if latest["bearish_ob"]:
                    score += 1

                if score == 2:
                    potential = "TINGGI 🌟"
                    signal = "SELL (SMC) 💥"
                    send_order(settings, symbol, mt5.ORDER_TYPE_SELL, tick.bid, float(tick.bid + sl_distance), float(tick.bid - tp_distance))
                elif score == 1:
                    potential = "MENENGAH 🟡"

        formatted_price = f"{current_price:.3f}" if "JPY" in symbol else f"{current_price:.5f}"
        market_data.append(_row(clean_symbol, formatted_price, signal, potential, daily_pnl, status_bot))

    return market_data


def _row(pair: str, price: str, signal: str, potential: str, daily_pnl: float, status_bot: str) -> dict:
    return {
        "Pair": pair,
        "Harga Realtime": price,
        "Sinyal": signal,
        "Potensi": potential,
        "Daily_PnL": f"${daily_pnl:.2f}",
        "Status_Bot": status_bot,
    }
