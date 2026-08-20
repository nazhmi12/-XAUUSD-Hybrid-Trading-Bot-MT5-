# Configuration

Semua konfigurasi dibaca dari `.env`.

## MT5

```env
MT5_LOGIN=12345678
MT5_PASSWORD=your_password
MT5_SERVER=your_broker_server
```

## Safety

```env
ENABLE_AUTO_TRADE=false
DAILY_TARGET_PROFIT=5.0
DAILY_MAX_LOSS=3.0
```

Default auto-trade dimatikan. Ubah ke `true` hanya kalau sudah yakin dan sudah test demo.

## Symbols

```env
SYMBOLS=EURUSDm,GBPUSDm,USDJPYm,AUDUSDm
```

Sesuaikan suffix symbol dengan broker masing-masing.
