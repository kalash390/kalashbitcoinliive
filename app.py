import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
from datetime import datetime
from pathlib import Path

# Load .env from the same folder as app.py (explicit path — fixes most issues)
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("API_KEY")

# Page configuration
st.set_page_config(
    page_title="Bitcoin Live Dashboard",
    page_icon="₿",
    layout="centered"
)

# Title
st.title("₿ Bitcoin Live Dashboard")
st.caption("Live Bitcoin price powered by CoinMarketCap API")

# ── Fetch current Bitcoin price ──────────────────────────────────────────────
def fetch_bitcoin_price():
    """Fetch the current Bitcoin price from CoinMarketCap API."""
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
        "price": quote["price"],
        "change_24h": quote["percent_change_24h"],
        "market_cap": quote["market_cap"],
        "volume_24h": quote["volume_24h"],
    }


# ── Fetch historical data for line chart (7-day) ─────────────────────────────
def fetch_historical_data():
    """Fetch 7-day historical Bitcoin prices from CoinGecko (no API key needed)."""
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": "7", "interval": "hourly"}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    raw = response.json()["prices"]          # [[timestamp_ms, price], ...]
    df = pd.DataFrame(raw, columns=["timestamp", "price"])
    df["time"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df


# ── Debug helper (remove after confirming it works) ──────────────────────────
with st.expander("🔧 Debug Info (remove after fixing)"):
    st.write(f"Looking for .env at: `{env_path}`")
    st.write(f".env file exists: `{env_path.exists()}`")
    st.write(f"API_KEY loaded: `{'✅ Yes' if API_KEY else '❌ No — key missing or wrong filename'}`")

# ── Check API key ─────────────────────────────────────────────────────────────
if not API_KEY:
    st.error(
        "⚠️ API key not found. Please add your CoinMarketCap API key to the "
        "`.env` file as `API_KEY=your_key_here` and restart the app."
    )
    st.stop()

# ── Refresh button ────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col2:
    refresh = st.button("🔄 Refresh", use_container_width=True)

# Use session state so the data persists between reruns unless Refresh is clicked
if "bitcoin_data" not in st.session_state or refresh:
    with st.spinner("Fetching live data…"):
        try:
            st.session_state["bitcoin_data"] = fetch_bitcoin_price()
            st.session_state["last_updated"] = datetime.now().strftime("%H:%M:%S")
        except requests.exceptions.HTTPError as e:
            st.error(f"❌ API error: {e}. Check your API key or usage limits.")
            st.stop()
        except requests.exceptions.ConnectionError:
            st.error("❌ Connection error. Please check your internet connection.")
            st.stop()
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
            st.stop()

data = st.session_state["bitcoin_data"]
last_updated = st.session_state.get("last_updated", "—")

# ── Metrics row ───────────────────────────────────────────────────────────────
st.markdown(f"*Last updated: {last_updated}*")

m1, m2, m3, m4 = st.columns(4)
change = data["change_24h"]
delta_str = f"{change:+.2f}%"

m1.metric("💰 BTC Price (USD)", f"${data['price']:,.2f}", delta=delta_str)
m2.metric("📈 24h Change",      delta_str)
m3.metric("🏦 Market Cap",      f"${data['market_cap'] / 1e9:.2f}B")
m4.metric("🔄 24h Volume",      f"${data['volume_24h'] / 1e9:.2f}B")

st.divider()

# ── 7-day line chart ──────────────────────────────────────────────────────────
st.subheader("📊 7-Day Price Chart")

try:
    hist_df = fetch_historical_data()
    color = "#00c853" if change >= 0 else "#f44336"

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=hist_df["time"],
            y=hist_df["price"],
            mode="lines",
            line=dict(color=color, width=2),
            fill="tozeroy",
            fillcolor=color.replace(")", ", 0.08)").replace("rgb", "rgba")
            if color.startswith("rgb")
            else color + "14",        # hex with ~8% alpha
            name="BTC/USD",
        )
    )
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
    st.warning(f"⚠️ Could not load historical chart: {e}")

st.caption("Historical data provided by CoinGecko (public API, no key required).")

