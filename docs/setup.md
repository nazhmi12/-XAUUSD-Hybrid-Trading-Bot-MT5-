# Setup

## Prasyarat

- Windows
- Python 3.8+
- MetaTrader 5 x64 sudah terinstall dan login
- Akun broker demo sangat disarankan

## Install Dependency

```bash
pip install -r requirements.txt
```

## Environment

Copy `.env.example` ke `.env`, lalu isi kredensial MT5.

```powershell
Copy-Item .env.example .env
```

## Run

```bash
PYTHONIOENCODING=utf-8 python apps/run_bot.py
streamlit run apps/dashboard.py
```
