# MT5 SMC Auto-Trading Terminal

Bot trading berbasis Python untuk MetaTrader 5 dengan dashboard Streamlit. Engine bot membaca data market MT5, menghitung sinyal SMC/ATR, menulis status ke JSON, lalu dashboard menampilkannya secara realtime.

> ⚠️ Educational only. Selalu test di akun demo. Default `ENABLE_AUTO_TRADE=false` agar aman.

## Struktur Project

```text
bot-mt5/
├── apps/
│   ├── run_bot.py          # entrypoint engine trading
│   └── dashboard.py        # dashboard Streamlit
├── src/bot_mt5/
│   ├── config.py           # load konfigurasi dari .env
│   ├── mt5_client.py       # koneksi MT5, PnL, order
│   ├── strategy.py         # logic SMC + ATR
│   ├── notifier.py         # Telegram notifier
│   ├── news.py             # RSS news + sentiment
│   └── storage.py          # baca/tulis status_market.json
├── data/                   # generated runtime data
├── docs/                   # dokumentasi tambahan
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
└── tests/
```

## Setup

1. Install MetaTrader 5 x64 dan login ke broker/demo.
2. Aktifkan `Tools -> Options -> Expert Advisors -> Allow algorithmic trading`.
3. Install dependency:

```bash
pip install -r requirements.txt
```

4. Copy `.env.example` ke `.env`, lalu isi konfigurasi MT5:

```bash
cp .env.example .env
```

Di Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

## Menjalankan

Terminal 1 - engine bot:

```bash
PYTHONIOENCODING=utf-8 python apps/run_bot.py
```

Terminal 2 - dashboard:

```bash
streamlit run apps/dashboard.py
```

## Konfigurasi Penting

Lihat `.env.example`.

- `ENABLE_AUTO_TRADE=false`: dry-run, sinyal dihitung tapi order tidak dikirim.
- `ENABLE_AUTO_TRADE=true`: order real dikirim ke MT5 jika sinyal valid.
- `SYMBOLS`: sesuaikan suffix broker, misalnya `EURUSDm` atau `EURUSD`.
- `DAILY_TARGET_PROFIT` dan `DAILY_MAX_LOSS`: kill switch harian.

## Dokumentasi

- `docs/setup.md`
- `docs/configuration.md`
- `docs/strategy.md`
- `docs/troubleshooting.md`
