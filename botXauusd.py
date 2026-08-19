import streamlit as st
import json
import time as time_mod
import os
import feedparser
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# ==========================================
# 1. INISIALISASI HALAMAN & NLP
# ==========================================
st.set_page_config(page_title="Live Auto-Trading Terminal", layout="wide", initial_sidebar_state="collapsed")

@st.cache_resource
def get_analyzer():
    return SentimentIntensityAnalyzer()

analyzer = get_analyzer()

def analyze_news_impact(title):
    title_lower = title.lower()
    asset = "GLOBAL"
    if any(w in title_lower for w in ["usd", "dollar", "fed", "powell", "rate", "inflation", "cpi"]): asset = "USD"
    elif any(w in title_lower for w in ["eur", "euro", "ecb"]): asset = "EURUSD"
    elif any(w in title_lower for w in ["gbp", "pound", "boe"]): asset = "GBPUSD"
    elif any(w in title_lower for w in ["jpy", "yen", "boj"]): asset = "USDJPY"
        
    score = analyzer.polarity_scores(title)['compound']
    if score >= 0.15: return asset, "NAIK", "buy", round(abs(score), 2)
    elif score <= -0.15: return asset, "TURUN", "sell", round(abs(score), 2)
    return asset, "NETRAL", "hold", round(abs(score), 2)

@st.cache_data(ttl=20)
def get_live_news():
    rss_sources = {
        "FOREX FACTORY": "https://www.forexfactory.com/news.xml",
        "FXSTREET": "https://www.fxstreet.com/rss/news",
        "FOREXLIVE": "https://www.forexlive.com/feed/news",
        "YAHOO": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=DX-Y.NYB&region=US&lang=en-US"
    }
    
    news_items = []
    for source_name, url in rss_sources.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:
                asset, impact_text, impact_type, conf = analyze_news_impact(entry.title)
                
                # Parsing Waktu Lebih Akurat (Mendapatkan Tanggal)
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
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
                    "link": entry.link
                })
        except:
            continue
    return news_items

# ==========================================
# 3. CSS INJECTION 
# ==========================================
def load_custom_css():
    st.markdown("""
        <style>
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        .metric-container { background-color: #141414; border-radius: 8px; padding: 15px 20px; display: flex; flex-direction: column; border: 1px solid #2b2b2b; }
        .border-green { border-left: 4px solid #00C853 !important; }
        .border-red { border-left: 4px solid #D50000 !important; }
        .border-gray { border-left: 4px solid #666666 !important; }
        .metric-title { color: #8a8a8a; font-size: 12px; font-weight: 600; text-transform: uppercase; margin-bottom: 5px; }
        .metric-value-row { display: flex; align-items: baseline; gap: 10px; }
        .metric-price { color: #ffffff; font-size: 20px; font-weight: 700; margin: 0; }
        .metric-change-up { color: #00C853; font-size: 13px; font-weight: 600; }
        .metric-change-down { color: #D50000; font-size: 13px; font-weight: 600; }
        .metric-change-hold { color: #8a8a8a; font-size: 13px; font-weight: 600; }
        .panel-card { background-color: #141414; border: 1px solid #2b2b2b; border-radius: 8px; padding: 20px; margin-bottom: 15px; }
        .panel-header { color: #8a8a8a; font-size: 12px; font-weight: 600; text-transform: uppercase; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; }
        .status-dot { height: 10px; width: 10px; background-color: #ffffff; border-radius: 50%; display: inline-block; margin-right: 8px; }
        .status-dot-active { background-color: #00C853; }
        .status-dot-error { background-color: #D50000; }
        .status-text { color: #ffffff; font-size: 18px; font-weight: 700; margin-bottom: 5px; }
        .status-sub { color: #8a8a8a; font-size: 12px; font-family: monospace; }
        .list-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; border-bottom: 1px solid #222; padding-bottom: 5px;}
        .list-label { color: #d1d1d1; font-size: 14px; }
        .list-val { color: #ffffff; font-size: 14px; font-weight: 600; }
        .badge { padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
        .badge-sell { background-color: rgba(213, 0, 0, 0.15); color: #D50000; }
        .badge-buy { background-color: rgba(0, 200, 83, 0.15); color: #00C853; }
        .badge-hold { background-color: rgba(255, 171, 0, 0.15); color: #FFAB00; }
        .badge-blue { background-color: rgba(41, 121, 255, 0.15); color: #2979ff; }
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# 4. KOMPONEN UI DINAMIS
# ==========================================
def render_header():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("<h2 style='margin:0; font-weight: 800;'>🎛️ Live Auto-Trading Terminal</h2>", unsafe_allow_html=True)
    with col2:
        now_str = datetime.now().strftime("%d %b %Y %H:%M:%S").upper()
        st.markdown(f"<div style='text-align: right; color: #8a8a8a; font-family: monospace; margin-top: 15px;'>{now_str}</div>", unsafe_allow_html=True)
    st.markdown("<hr style='margin-top: 10px; margin-bottom: 20px;'>", unsafe_allow_html=True)

def render_top_metrics(market_data):
    cols = st.columns(len(market_data))
    for i, item in enumerate(market_data):
        sinyal = item.get("Sinyal", "HOLD")
        if "BUY" in sinyal:
            border_class, color_class = "border-green", "metric-change-up"
        elif "SELL" in sinyal:
            border_class, color_class = "border-red", "metric-change-down"
        else:
            border_class, color_class = "border-gray", "metric-change-hold"
            
        html = f"""
        <div class="metric-container {border_class}">
            <div class="metric-title">{item.get('Pair', 'UNKNOWN')}</div>
            <div class="metric-value-row">
                <div class="metric-price">{item.get('Harga Realtime', '0.00')}</div>
                <div class="{color_class}">{sinyal}</div>
            </div>
        </div>
        """
        cols[i].markdown(html, unsafe_allow_html=True)
    st.write("") 

def render_left_panel(machine_status, market_data):
    # Logika Status
    dot_class = "status-dot-active" if machine_status == "ACTIVE" else "status-dot-error"
    status_color = "#00C853" if machine_status == "ACTIVE" else "#D50000"
    
    st.markdown(f"""
    <div class="panel-card">
        <div class="panel-header">💾 STATUS MESIN</div>
        <div><span class="status-dot {dot_class}"></span><span class="status-text" style="color:{status_color};">{machine_status}</span></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Panel Rekomendasi (Risk Mitigation)
    st.markdown('<div class="panel-card"><div class="panel-header">🎯 REKOMENDASI ENTRY (SMC)</div>', unsafe_allow_html=True)
    for item in market_data:
        pair = item.get("Pair", "")
        potensi = item.get("Potensi", "RENDAH ⚪")
        
        # Pewarnaan teks potensi
        val_color = "#00C853" if "TINGGI" in potensi else "#FFAB00" if "MENENGAH" in potensi else "#8a8a8a"
        st.markdown(f'<div class="list-row"><span class="list-label">{pair}</span><span class="list-val" style="color:{val_color};">{potensi}</span></div>', unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

def render_right_panel():
    st.markdown('<div class="panel-card"><div class="panel-header">📰 KATALIS SENTIMEN MARKET</div>', unsafe_allow_html=True)
    news_data = get_live_news()
    
    if not news_data:
        st.markdown("<div class='status-sub'>Sedang menarik data berita RSS...</div>", unsafe_allow_html=True)
    else:
        for n in news_data:
            st.markdown(f"<a href='{n['link']}' target='_blank' style='color: #64b5f6; font-size: 15px; font-weight: 600; text-decoration: none;'>{n['title']}</a>", unsafe_allow_html=True)
            # Tanggal terbit sekarang ditampilkan rapi di sini
            st.markdown(f"<div style='color: #8a8a8a; font-size: 11px; margin-top: 2px; margin-bottom: 6px;'>🕒 {n['time']} | 📡 {n['source']}</div>", unsafe_allow_html=True)
            st.markdown("<hr style='border-color: #2b2b2b; margin: 12px 0;'>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 5. MAIN LOOP
# ==========================================
def main():
    load_custom_css()
    main_placeholder = st.empty()
    
    while True:
        market_data = []
        machine_status = "OFFLINE"
        
        if os.path.exists("status_market.json"):
            try:
                with open("status_market.json", "r") as f:
                    market_data = json.load(f)
                machine_status = "ACTIVE"
            except:
                pass
                
        if not market_data:
            market_data = [{"Pair": "MENUNGGU DATA", "Harga Realtime": "0.00", "Sinyal": "Standby", "Potensi": "..."}]

        with main_placeholder.container():
            render_header()
            render_top_metrics(market_data)
            
            col_left, col_right = st.columns([1, 2.5])
            with col_left:
                render_left_panel(machine_status, market_data)
            with col_right:
                render_right_panel()
                
        time_mod.sleep(2)

if __name__ == "__main__":
    main()