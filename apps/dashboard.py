import sys
import time as time_mod
from datetime import datetime
from pathlib import Path

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "src"))

from bot_mt5.config import get_settings
from bot_mt5.news import get_live_news
from bot_mt5.storage import read_market_status

st.set_page_config(page_title="Live Auto-Trading Terminal", layout="wide", initial_sidebar_state="collapsed")


@st.cache_data(ttl=20)
def cached_live_news():
    return get_live_news()


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
        .list-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; border-bottom: 1px solid #222; padding-bottom: 5px;}
        .list-label { color: #d1d1d1; font-size: 14px; }
        .list-val { color: #ffffff; font-size: 14px; font-weight: 600; }
        </style>
    """, unsafe_allow_html=True)


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
        signal = item.get("Sinyal", "HOLD")
        if "BUY" in signal:
            border_class, color_class = "border-green", "metric-change-up"
        elif "SELL" in signal:
            border_class, color_class = "border-red", "metric-change-down"
        else:
            border_class, color_class = "border-gray", "metric-change-hold"

        cols[i].markdown(f"""
        <div class="metric-container {border_class}">
            <div class="metric-title">{item.get('Pair', 'UNKNOWN')}</div>
            <div class="metric-value-row">
                <div class="metric-price">{item.get('Harga Realtime', '0.00')}</div>
                <div class="{color_class}">{signal}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.write("")


def render_left_panel(machine_status, market_data):
    dot_class = "status-dot-active" if machine_status == "ACTIVE" else "status-dot-error"
    status_color = "#00C853" if machine_status == "ACTIVE" else "#D50000"

    st.markdown(f"""
    <div class="panel-card">
        <div class="panel-header">💾 STATUS MESIN</div>
        <div><span class="status-dot {dot_class}"></span><span class="status-text" style="color:{status_color};">{machine_status}</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="panel-card"><div class="panel-header">🎯 REKOMENDASI ENTRY (SMC)</div>', unsafe_allow_html=True)
    for item in market_data:
        potential = item.get("Potensi", "RENDAH ⚪")
        val_color = "#00C853" if "TINGGI" in potential else "#FFAB00" if "MENENGAH" in potential else "#8a8a8a"
        st.markdown(f'<div class="list-row"><span class="list-label">{item.get("Pair", "")}</span><span class="list-val" style="color:{val_color};">{potential}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_right_panel():
    st.markdown('<div class="panel-card"><div class="panel-header">📰 KATALIS SENTIMEN MARKET</div>', unsafe_allow_html=True)
    news_data = cached_live_news()
    if not news_data:
        st.markdown("<div style='color:#8a8a8a;'>Sedang menarik data berita RSS...</div>", unsafe_allow_html=True)
    else:
        for n in news_data:
            st.markdown(f"<a href='{n['link']}' target='_blank' style='color: #64b5f6; font-size: 15px; font-weight: 600; text-decoration: none;'>{n['title']}</a>", unsafe_allow_html=True)
            st.markdown(f"<div style='color: #8a8a8a; font-size: 11px; margin-top: 2px; margin-bottom: 6px;'>🕒 {n['time']} | 📡 {n['source']}</div>", unsafe_allow_html=True)
            st.markdown("<hr style='border-color: #2b2b2b; margin: 12px 0;'>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def main():
    settings = get_settings()
    load_custom_css()
    main_placeholder = st.empty()

    while True:
        market_data = read_market_status(settings.status_file)
        machine_status = "ACTIVE" if market_data else "OFFLINE"
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
