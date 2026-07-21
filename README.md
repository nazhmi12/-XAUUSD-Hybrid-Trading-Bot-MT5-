🤖 XAUUSD Hybrid Trading Bot (MT5)

An algorithmic trading bot built with Python for MetaTrader 5 (MT5). This bot is specifically designed for trading XAUUSD (Gold) by utilizing a Dual-Confirmation Strategy: combining Technical Analysis (TA) and Fundamental News Sentiment.

✨ Features

MetaTrader 5 Integration: Direct order execution and OHLCV data fetching using the official MetaTrader5 Python library.

Technical Analysis: Uses EMA (Exponential Moving Average) crossovers and RSI (Relative Strength Index) to identify trends and momentum.

Dynamic Risk Management (ATR): Stop Loss (SL) and Take Profit (TP) are calculated dynamically based on market volatility using the Average True Range (ATR) indicator.

News Sentiment Analysis (NLP): Scrapes real-time financial news via Yahoo Finance RSS feeds and evaluates market sentiment (Bullish/Bearish) using VADER Sentiment Analysis.

Dual-Confirmation Logic: Trades are only executed when Technical signals and News Sentiment align, minimizing false breakouts.

⚙️ Prerequisites

OS: Windows (The MetaTrader5 library only supports Windows).

Python: Version 3.8 or higher.

MetaTrader 5: Installed and logged into a broker account (Demo recommended).

📦 Installation

Clone this repository:

git clone https://github.com/USERNAME/XAUUSD-Hybrid-Trading-Bot.git
cd XAUUSD-Hybrid-Trading-Bot


Install the required Python dependencies:

pip install MetaTrader5 pandas ta vaderSentiment feedparser requests


🚀 How to Use

Open your MetaTrader 5 application.

Go to Tools -> Options -> Expert Advisors and check the "Allow algorithmic trading" box.

Open xauusd_bot.py in your code editor.

Update the MT5 configuration section with your account details:

MT5_LOGIN = 12345678            # Your MT5 Account ID
MT5_PASSWORD = "YourPassword"   # Your MT5 Password
MT5_SERVER = "Your-Broker-Server" # E.g., "Exness-MT5Trial6"


Run the bot:

python xauusd_bot.py


🧠 Strategy Logic

ENTRY BUY: EMA 9 crosses above EMA 21 + RSI < 40 + News Sentiment is BULLISH.

ENTRY SELL: EMA 9 crosses below EMA 21 + RSI > 70 + News Sentiment is BEARISH.

STOP LOSS: Entry Price ± (ATR * 1.5)

TAKE PROFIT: Entry Price ± (ATR * 1.5 * 2.0) (1:2 Risk to Reward Ratio)

⚠️ Disclaimer

Educational Purposes Only. Trading in financial markets (Forex, Commodities, Crypto) involves a high degree of risk. The developer is not responsible for any financial losses incurred while using this software. Always test algorithms on a Demo Account before deploying real capital.

Created by [Your Name/Handle] - 2026
