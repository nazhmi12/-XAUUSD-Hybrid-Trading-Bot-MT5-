# Troubleshooting

## `MetaTrader 5 x64 not found`

Pastikan MetaTrader 5 x64 sudah terinstall dan bisa dibuka manual.

## Gagal login MT5

Cek `MT5_LOGIN`, `MT5_PASSWORD`, dan `MT5_SERVER` di `.env`.

## Symbol no data

Broker bisa punya suffix berbeda. Contoh:

- `EURUSD`
- `EURUSDm`
- `EURUSD.a`

Update `SYMBOLS` di `.env`.

## Emoji encoding error di Windows

Jalankan dengan:

```bash
PYTHONIOENCODING=utf-8 python apps/run_bot.py
```
