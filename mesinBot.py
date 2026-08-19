import MetaTrader5 as mt5
import pandas as pd
import ta
import time
import json
import requests
from datetime import datetime

# ==========================================
# 1. KONFIGURASI AKUN & TELEGRAM
# ==========================================
MT5_LOGIN = 434105373            
MT5_PASSWORD = "Nazh_17405"     
MT5_SERVER = "Exness-MT5Trial7" 

TELEGRAM_TOKEN = "PASTE_TOKEN_DARI_BOTFATHER_DI_SINI"
TELEGRAM_CHAT_ID = "PASTE_ID_ANGKA_LU_DI_SINI"

ENABLE_AUTO_TRADE = True

SYMBOLS = ["EURUSDm", "GBPUSDm", "USDJPYm", "AUDUSDm"] 
TIMEFRAME = mt5.TIMEFRAME_M5

# ==========================================
# 2. MANAJEMEN RISIKO & TARGET HARIAN
# ==========================================
LOT_SIZE = 0.01      
MAGIC_NUMBER = 999000

# Fitur Auto Kill Switch
DAILY_TARGET_PROFIT = 5.0  # Target profit $5
DAILY_MAX_LOSS = 3.0       # Max loss -$3

# ==========================================
# 3. MODUL TELEGRAM NOTIFIER
# ==========================================
def send_telegram_alert(pesan):
    if TELEGRAM_TOKEN == "PASTE_TOKEN_DARI_BOTFATHER_DI_SINI":
        return 
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": pesan, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload)
    except:
        pass

# ==========================================
# 4. MODUL KONEKSI & EKSEKUSI (SAFETY LOCK)
# ==========================================
def initialize_mt5():
    print("Mencoba menghubungkan ke MetaTrader 5...")
    if not mt5.initialize(login=MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER):
        print(f"❌ Gagal login MT5. Error code: {mt5.last_error()}")
        return False
    print("✅ Berhasil login ke MetaTrader 5!")
    return True

def has_open_position():
    positions = mt5.positions_get()
    if positions is None:
        return False
    bot_positions = [p for p in positions if p.magic == MAGIC_NUMBER]
    return len(bot_positions) > 0

def check_daily_target():
    """Menghitung total Profit/Loss khusus hari ini."""
    now = datetime.now()
    today_start = datetime(now.year, now.month, now.day)
    
    deals = mt5.history_deals_get(today_start, now)
    daily_pnl = 0.0
    
    if deals is not None:
        for deal in deals:
            if deal.magic == MAGIC_NUMBER:
                daily_pnl += deal.profit
                
    return daily_pnl

def send_order(symbol, order_type, price, sl, tp):
    if has_open_position():
        print(f"⚠️ Sinyal {symbol} diabaikan: Masih ada posisi jalan!")
        return None

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": LOT_SIZE,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": MAGIC_NUMBER,
        "comment": "SMC Sniper Mode",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"⚠️ Gagal kirim order {symbol}: {result.comment}")
    else:
        print(f"✅ BINGO SMC! Order {symbol} masuk! (Mode Sniper Aktif)")
        tipe_order = "BUY 🚀" if order_type == mt5.ORDER_TYPE_BUY else "SELL 💥"
        pesan_notif = (
            f"<b>✅ ENTRY SCALPING (SNIPER MODE)</b>\n\n"
            f"<b>Pair:</b> {symbol}\n"
            f"<b>Action:</b> {tipe_order}\n"
            f"<b>Harga Entry:</b> {price}\n"
            f"<b>SL Dinamis:</b> {sl:.5f}\n"
            f"<b>TP Dinamis:</b> {tp:.5f}\n\n"
            f"<i>Mesin Bot otomatis eksekusi!</i> 🤖"
        )
        send_telegram_alert(pesan_notif)
    return result

# ==========================================
# 5. MODUL ANALISA SMC (ATR DINAMIS)
# ==========================================
def analyze_market(daily_pnl):
    market_data = []
    
    trade_allowed = ENABLE_AUTO_TRADE
    status_bot = "AKTIF 🟢"
    
    if daily_pnl >= DAILY_TARGET_PROFIT:
        trade_allowed = False
        status_bot = f"TARGET TERCAPAI 🏆 (+${daily_pnl:.2f})"
    elif daily_pnl <= -DAILY_MAX_LOSS:
        trade_allowed = False
        status_bot = f"CUTLOSS HARIAN 🛑 (-${abs(daily_pnl):.2f})"

    for sym in SYMBOLS:
        mt5.symbol_select(sym, True)
        rates = mt5.copy_rates_from_pos(sym, TIMEFRAME, 0, 250)
        clean_symbol = sym.replace('m', '') if sym.endswith('m') else sym
        
        if rates is None or len(rates) == 0:
            market_data.append({"Pair": clean_symbol, "Harga Realtime": "ERROR", "Sinyal": "NO DATA", "Potensi": "ERROR", "Daily_PnL": f"${daily_pnl:.2f}", "Status_Bot": status_bot})
            continue
            
        df = pd.DataFrame(rates)
        
        # Indikator SMC Utama
        df['ema_200'] = ta.trend.EMAIndicator(df['close'], window=200).ema_indicator()
        df['fvg_bull'] = df['low'].shift(1) > df['high'].shift(3)
        df['fvg_bear'] = df['high'].shift(1) < df['low'].shift(3)
        df['bullish_ob'] = (df['close'].shift(1) > df['open'].shift(2)) & (df['close'].shift(2) < df['open'].shift(2))
        df['bearish_ob'] = (df['close'].shift(1) < df['open'].shift(2)) & (df['close'].shift(2) > df['open'].shift(2))
        
        # Indikator ATR untuk SL/TP Dinamis
        df['atr'] = ta.volatility.AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=14).average_true_range()
        latest_atr = df['atr'].iloc[-1]
        
        latest = df.iloc[-1]
        tick = mt5.symbol_info_tick(sym)
        current_price = tick.bid if tick is not None else latest['close']
        
        signal = "HOLD ⏳" if trade_allowed else "STANDBY (TARGET HIT) 💤"
        potensi = "RENDAH ⚪"
        skor = 0
        
        # --- LOGIKA ENTRY KETAT (SNIPER MODE) ---
        if trade_allowed:
            # Pengali Risk/Reward berbasis ATR
            sl_distance = latest_atr * 1.5   # Jarak SL cukup lega
            tp_distance = sl_distance * 2.0  # Reward 1:2
            
            if latest['close'] > latest['ema_200']:
                if latest['fvg_bull']: skor += 1
                if latest['bullish_ob']: skor += 1
                
                # WAJIB SKOR 2 BARU ENTRY (FVG + OB)
                if skor == 2:
                    potensi = "TINGGI 🌟"
                    signal = "BUY (SMC) 🚀"
                    sl_price = tick.ask - sl_distance
                    tp_price = tick.ask + tp_distance
                    send_order(sym, mt5.ORDER_TYPE_BUY, tick.ask, float(sl_price), float(tp_price))
                elif skor == 1:
                    potensi = "MENENGAH 🟡"
                        
            elif latest['close'] < latest['ema_200']:
                if latest['fvg_bear']: skor += 1
                if latest['bearish_ob']: skor += 1
                
                # WAJIB SKOR 2 BARU ENTRY (FVG + OB)
                if skor == 2:
                    potensi = "TINGGI 🌟"
                    signal = "SELL (SMC) 💥"
                    sl_price = tick.bid + sl_distance
                    tp_price = tick.bid - tp_distance
                    send_order(sym, mt5.ORDER_TYPE_SELL, tick.bid, float(sl_price), float(tp_price))

        formatted_price = f"{current_price:.3f}" if "JPY" in sym else f"{current_price:.5f}"
            
        market_data.append({
            "Pair": clean_symbol,
            "Harga Realtime": formatted_price,
            "Sinyal": signal,
            "Potensi": potensi,
            "Daily_PnL": f"${daily_pnl:.2f}",
            "Status_Bot": status_bot
        })
        
    return market_data

if __name__ == "__main__":
    print("=========================================")
    print("🏦 MESIN BOT SMC (Ultimate Sniper + Auto Kill Switch)")
    print("=========================================")
    
    if initialize_mt5():
        try:
            while True:
                daily_pnl = check_daily_target()
                data = analyze_market(daily_pnl)
                
                with open("status_market.json", "w") as f:
                    json.dump(data, f, indent=4)
                    
                now = datetime.now().strftime("%H:%M:%S")
                
                if daily_pnl >= DAILY_TARGET_PROFIT:
                    print(f"[{now}] 🏆 TARGET TERCAPAI (+${daily_pnl:.2f})! Mesin istirahat.")
                elif daily_pnl <= -DAILY_MAX_LOSS:
                    print(f"[{now}] 🛑 CUTLOSS HARIAN (-${abs(daily_pnl):.2f})! Mesin terkunci.")
                else:
                    print(f"[{now}] 🔄 PnL Hari Ini: ${daily_pnl:.2f} | Memindai M5 (Sniper Mode)...")
                    
                time.sleep(2)
        except KeyboardInterrupt:
            print("\n🛑 Mesin Bot dihentikan oleh user.")
        finally:
            mt5.shutdown()