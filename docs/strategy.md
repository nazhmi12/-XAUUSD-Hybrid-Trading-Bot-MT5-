# Strategy

Engine saat ini memakai timeframe M5.

## Indikator

- EMA 200 sebagai filter trend utama
- Fair Value Gap sederhana
- Order Block sederhana
- ATR 14 untuk jarak SL/TP dinamis

## Entry

BUY jika:

- Close di atas EMA 200
- FVG bullish valid
- Bullish order block valid

SELL jika:

- Close di bawah EMA 200
- FVG bearish valid
- Bearish order block valid

## Risk Reward

- SL = ATR x 1.5
- TP = SL distance x 2.0
