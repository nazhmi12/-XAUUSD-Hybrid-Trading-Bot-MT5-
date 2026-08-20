import time as time_mod
from datetime import datetime

import feedparser
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def get_analyzer() -> SentimentIntensityAnalyzer:
    return SentimentIntensityAnalyzer()


def analyze_news_impact(title: str, analyzer: SentimentIntensityAnalyzer | None = None):
    analyzer = analyzer or get_analyzer()
    title_lower = title.lower()
    asset = "GLOBAL"
    if any(w in title_lower for w in ["usd", "dollar", "fed", "powell", "rate", "inflation", "cpi"]):
        asset = "USD"
    elif any(w in title_lower for w in ["eur", "euro", "ecb"]):
        asset = "EURUSD"
    elif any(w in title_lower for w in ["gbp", "pound", "boe"]):
        asset = "GBPUSD"
    elif any(w in title_lower for w in ["jpy", "yen", "boj"]):
        asset = "USDJPY"

    score = analyzer.polarity_scores(title)["compound"]
    if score >= 0.15:
        return asset, "NAIK", "buy", round(abs(score), 2)
    if score <= -0.15:
        return asset, "TURUN", "sell", round(abs(score), 2)
    return asset, "NETRAL", "hold", round(abs(score), 2)


def get_live_news() -> list[dict]:
    rss_sources = {
        "FOREX FACTORY": "https://www.forexfactory.com/news.xml",
        "FXSTREET": "https://www.fxstreet.com/rss/news",
        "FOREXLIVE": "https://www.forexlive.com/feed/news",
        "YAHOO": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=DX-Y.NYB&region=US&lang=en-US",
    }

    analyzer = get_analyzer()
    news_items = []
    for source_name, url in rss_sources.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:
                asset, impact_text, impact_type, conf = analyze_news_impact(entry.title, analyzer)
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    pub_time = time_mod.strftime("%d %b %Y - %H:%M WIB", entry.published_parsed)
                else:
                    pub_time = datetime.now().strftime("%d %b %Y - %H:%M WIB")

                news_items.append({
                    "title": entry.title,
                    "time": pub_time,
                    "source": source_name,
                    "asset": asset,
                    "impact": impact_text,
                    "conf": conf,
                    "link": entry.link,
                })
        except Exception:
            continue
    return news_items
