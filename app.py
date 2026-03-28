import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
from datetime import datetime

# Works locally (.env file) AND on Streamlit Cloud (Secrets Manager)
load_dotenv()  # loads .env if running locally — ignored on Streamlit Cloud

# On Streamlit Cloud, st.secrets is used automatically via os.getenv
# after adding the key in the Secrets tab
API_KEY = os.getenv("API_KEY") or st.secrets.get("API_KEY", None)

# Page configuration
st.set_page_config(
    page_title="Bitcoin Live Dashboard",
    page_icon="₿",
    layout="centered"
)

st.title("₿ Bitcoin Live Dashboard")
st.caption("Live Bitcoin price powered by CoinMarketCap API")


# ── Fetch current Bitcoin price ───────────────────────────────────────────────
def fetch_bitcoin_price():
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": API_KEY,
    }
    params = {"symbol": "BTC", "convert": "USD"}
    response = requests.get(url, headers=headers, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    quote = data["data"]["BTC"]["quote"]["USD"]
    return {
        "price":      quote["price"],
        "change_24h": quote["percent_change_24h"],
        "market_cap": quote["market_cap"],
        "volume_24h": quote["volume_24h"],
    }


# ── Fetch 7-day historical prices (CoinGecko — no key needed) ─────────────────
def fetch_historical_data():
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": "7", "interval": "hourly"}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    raw = response.json()["prices"]
    df = pd.DataFrame(raw, columns=["timestamp", "price"])
    df["time"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df


# ── API key check ─────────────────────────────────────────────────────────────
if not API_KEY:
    st.error("⚠️ API key not found.")
    st.info(
        "**Running locally?** Create a `.env` file next to `app.py` with:\n"
        "```\nAPI_KEY=your_key_here\n```\n\n"
        "**On Streamlit Cloud?** Go to your app → **Settings → Secrets** and add:\n"
        "```\nAPI_KEY = \"your_key_here\"\n```"
    )
    st.stop()

# ── Refresh button ────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col2:
    refresh = st.button("🔄 Refresh", use_container_width=True)

if "bitcoin_data" not in st.session_state or refresh:
    with st.spinner("Fetching live data…"):
        try:
            st.session_state["bitcoin_data"]    = fetch_bitcoin_price()
            st.session_state["last_updated"]    = datetime.now().strftime("%H:%M:%S")
        except requests.exceptions.HTTPError as e:
            st.error(f"❌ API error: {e} — check your key or usage limits.")
            st.stop()
        except requests.exceptions.ConnectionError:
            st.error("❌ Connection error. Check your internet connection.")
            st.stop()
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
            st.stop()

data         = st.session_state["bitcoin_data"]
last_updated = st.session_state.get("last_updated", "—")

# ── Metrics ───────────────────────────────────────────────────────────────────
st.markdown(f"*Last updated: {last_updated}*")

m1, m2, m3, m4 = st.columns(4)
change    = data["change_24h"]
delta_str = f"{change:+.2f}%"

m1.metric("💰 BTC Price (USD)", f"${data['price']:,.2f}",           delta=delta_str)
m2.metric("📈 24h Change",       delta_str)
m3.metric("🏦 Market Cap",       f"${data['market_cap'] / 1e9:.2f}B")
m4.metric("🔄 24h Volume",       f"${data['volume_24h'] / 1e9:.2f}B")

st.divider()

# ── 7-day chart ───────────────────────────────────────────────────────────────
st.subheader("📊 7-Day Price Chart")

try:
    hist_df = fetch_historical_data()
    color   = "#00c853" if change >= 0 else "#f44336"

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hist_df["time"],
        y=hist_df["price"],
        mode="lines",
        line=dict(color=color, width=2),
        fill="tozeroy",
        fillcolor=color + "14",
        name="BTC/USD",
    ))
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis=dict(tickformat="$,.0f"),
    )
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.warning(f"⚠️ Could not load chart: {e}")

st.caption("Historical data by CoinGecko (public API — no key required).")
