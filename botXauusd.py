import MetaTrader5 as mt5
import pandas as pd
import requests
import time
import feedparser  # Tambahkan library ini
from datetime import datetime
import ta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# ==========================================
# KONFIGURASI AKUN MT5 & PARAMETER TRADING
# ==========================================
MT5_LOGIN = 12345678            # Ganti dengan nomor akun MT5 kamu
MT5_PASSWORD = "PasswordKamu"   # Ganti dengan password akun MT5 kamu
MT5_SERVER = "Nama-Server-Broker" # Ganti nama server (contoh: "MetaQuotes-Demo" atau "Exness-MT5Trial6")

SYMBOL = "XAUUSD"
LOT_SIZE = 0.01
MAGIC_NUMBER = 999111
TIMEFRAME = mt5.TIMEFRAME_H1
# Multiplier untuk SL dan TP berbasis ATR
SL_MULTIPLIER = 1.5 
RR_RATIO = 2.0      

# Inisialisasi NLP untuk Sentimen
analyzer = SentimentIntensityAnalyzer()

# ==========================================
# MODUL 1: KONEKSI & LOGIN MT5
# ==========================================
def initialize_mt5(symbol):
    """Logika inisialisasi koneksi dan login ke akun MT5."""
    # Initialize MT5 dengan kredensial
    if not mt5.initialize(login=MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER):
        print(f"Gagal menghubungkan ke MT5. Error: {mt5.last_error()}")
        return False
        
    # Validasi eksistensi simbol
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"Error: Simbol {symbol} tidak ditemukan di server broker.")
        mt5.shutdown()
        return False
        
    # Eksekusi penambahan simbol ke Market Watch terminal jika belum ada
    if not symbol_info.visible:
        print(f"Menambahkan {symbol} ke Market Watch...")
        if not mt5.symbol_select(symbol, True):
            print(f"Gagal menambahkan {symbol}.")
            mt5.shutdown()
            return False
            
    print(f"✅ Berhasil Login ke Akun: {MT5_LOGIN} | Server: {MT5_SERVER}")
    return True

# ==========================================
# MODUL 2: TARIK DATA MARKET (OHLCV)
# ==========================================
def get_market_data(symbol, timeframe, limit=100):
    """Menarik data candlestick dari MT5 dan mengubahnya jadi DataFrame."""
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, limit)
    
    if rates is None or len(rates) == 0:
        print("❌ Gagal menarik data market.")
        return None
        
    # Konversi ke format DataFrame Pandas
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    # Kalkulasi Indikator Teknikal (Modul sebelumnya)
    # Hitung RSI
    df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
    # Hitung EMA
    df['ema_short'] = ta.trend.EMAIndicator(df['close'], window=9).ema_indicator()
    df['ema_long'] = ta.trend.EMAIndicator(df['close'], window=21).ema_indicator()
    # Hitung ATR untuk volatilitas
    df['atr'] = ta.volatility.AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=14).average_true_range()
    
    return df

def get_technical_signals(df):
    """Membaca tren teknikal dan mengekstrak nilai ATR."""
    latest = df.iloc[-1]
    tech_signal = 'HOLD'
    
    if latest['ema_short'] > latest['ema_long'] and latest['rsi'] < 40:
        tech_signal = 'BUY'
    elif latest['ema_short'] < latest['ema_long'] and latest['rsi'] > 70:
        tech_signal = 'SELL'
        
    return tech_signal, latest['atr']

# ==========================================
# MODUL 3: ANALISA SENTIMEN BERITA (GRATIS VIA RSS)
# ==========================================
def get_news_sentiment(query_tidak_dipakai=""):
    """Menarik berita Emas terbaru via Yahoo Finance RSS secara gratis."""
    # Link RSS Yahoo Finance khusus ticker Emas (GC=F)
    rss_url = "https://feeds.finance.yahoo.com/rss/2.0/headline?s=GC=F&region=US&lang=en-US"
    
    try:
        # Parse RSS Feed
        feed = feedparser.parse(rss_url)
        articles = feed.entries[:5] # Ambil 5 berita emas terbaru
        
        if not articles:
            return 'NEUTRAL'
            
        total_score = 0
        print("\n--- Berita Emas Terbaru (Yahoo Finance) ---")
        for article in articles:
            title = article.title
            score = analyzer.polarity_scores(title)
            total_score += score['compound']
            print(f"> {title} (Score: {score['compound']:.2f})")
            
        avg_score = total_score / len(articles)
        
        if avg_score > 0.15:
            return 'BULLISH'
        elif avg_score < -0.15:
            return 'BEARISH'
        return 'NEUTRAL'
        
    except Exception as e:
        print(f"Error fetch RSS news: {e}")
        return 'NEUTRAL'

# ==========================================
# MODUL 4: MANAJEMEN RISIKO (SL/TP)
# ==========================================
def calculate_dynamic_sltp(entry_price, atr_value, signal_type):
    """Hitung Stop Loss dan Take Profit berdasarkan nilai ATR."""
    jarak_sl = atr_value * SL_MULTIPLIER
    jarak_tp = jarak_sl * RR_RATIO
    
    if signal_type == 'BUY':
        sl_price = entry_price - jarak_sl
        tp_price = entry_price + jarak_tp
    elif signal_type == 'SELL':
        sl_price = entry_price + jarak_sl
        tp_price = entry_price - jarak_tp
    else:
        return 0.0, 0.0
        
    return float(sl_price), float(tp_price)

# ==========================================
# MODUL 5: EKSEKUSI ORDER MT5
# ==========================================
def execute_trade(symbol, signal, atr_value, sentiment):
    """Eksekusi trade berdasarkan konfirmasi ganda (Teknikal + Sentimen)."""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Evaluasi {symbol}")
    print(f"  > Technical : {signal} (ATR: {atr_value:.2f})")
    print(f"  > Sentiment : {sentiment}")
    
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        print("  ❌ Gagal mengambil data tick harga.")
        return
        
    # LOGIKA ENTRY BUY
    if signal == 'BUY' and sentiment == 'BULLISH':
        entry_price = tick.ask
        sl_price, tp_price = calculate_dynamic_sltp(entry_price, atr_value, 'BUY')
        
        print(f"  🚀 ACTION: ENTRY BUY @ {entry_price}")
        print(f"     SL: {sl_price:.2f} | TP: {tp_price:.2f}")
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": LOT_SIZE,
            "type": mt5.ORDER_TYPE_BUY,
            "price": entry_price,
            "sl": sl_price,
            "tp": tp_price,
            "deviation": 50,
            "magic": MAGIC_NUMBER,
            "comment": "Hybrid Bot Buy",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"  ❌ Order Gagal! Kode MT5: {result.retcode}")
        else:
            print("  ✅ Order BUY Berhasil Tereksekusi!")

    # LOGIKA ENTRY SELL
    elif signal == 'SELL' and sentiment == 'BEARISH':
        entry_price = tick.bid
        sl_price, tp_price = calculate_dynamic_sltp(entry_price, atr_value, 'SELL')
        
        print(f"  💥 ACTION: ENTRY SELL @ {entry_price}")
        print(f"     SL: {sl_price:.2f} | TP: {tp_price:.2f}")
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": LOT_SIZE,
            "type": mt5.ORDER_TYPE_SELL,
            "price": entry_price,
            "sl": sl_price,
            "tp": tp_price,
            "deviation": 50,
            "magic": MAGIC_NUMBER,
            "comment": "Hybrid Bot Sell",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"  ❌ Order Gagal! Kode MT5: {result.retcode}")
        else:
            print("  ✅ Order SELL Berhasil Tereksekusi!")
            
    else:
        print("  ⏳ ACTION: HOLD. Kondisi belum valid.")

# ==========================================
# MAIN LOOP (SISTEM UTAMA)
# ==========================================
def run_bot():
    """Fungsi utama untuk melooping bot agar terus berjalan."""
    if not initialize_mt5(SYMBOL):
        return
        
    print("\n=========================================")
    print(f"🤖 Bot {SYMBOL} Aktif (Tekan Ctrl+C untuk Stop)")
    print("=========================================")
    
    try:
        while True:
            # 1. Ambil Data Market
            df = get_market_data(SYMBOL, TIMEFRAME)
            if df is None:
                time.sleep(60)
                continue
                
            # 2. Analisa Chart & Volatilitas
            tech_signal, atr_value = get_technical_signals(df)
            
            # 3. Analisa Berita (Sekarang narik otomatis dari RSS Yahoo Finance)
            news_sentiment = get_news_sentiment()
            
            # 4. Eksekusi
            execute_trade(SYMBOL, tech_signal, atr_value, news_sentiment)
            
            # Jeda 1 Jam sesuai timeframe agar tidak spam request
            time.sleep(3600)
            
    except KeyboardInterrupt:
        print("\nBot dihentikan oleh user.")
    except Exception as e:
        print(f"\nTerjadi Error Sistem: {e}")
    finally:
        mt5.shutdown()
        print("Koneksi MT5 diputus.")

if __name__ == "__main__":
    run_bot()