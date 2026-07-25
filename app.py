"""
app.py  —  AI Trading Assistant (ADVANCED Dashboard)
=====================================================
To run, in the terminal:  streamlit run app.py
Or double-click START.bat.

Tabs:
  1. 📊 Dashboard  — live candlestick chart + indicators + signal + AI
  2. 🔍 Scanner    — scan multiple symbols at once, best opportunities on top
  3. 🧪 Backtest   — test a strategy against historical data
  4. 🛡️ Risk Calc  — position size, stop-loss, take-profit (protect your capital)

** DISCLAIMER **: For EDUCATIONAL purposes only. Does NOT execute trades,
and is NOT financial advice. Trading carries a real risk of losing money.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from data_sources import get_data, get_live_price, is_realtime
from indicators import add_all_indicators, support_resistance, fibonacci_levels
from signals import generate_signal, multi_timeframe_signal
from patterns import detect_patterns, bias_summary
from predictor import predict_next_candle
from strategies import run_all_strategies
from verdict import overall_verdict
import wisdom
import auth
from scanner import scan
from backtest import run_backtest
from risk import position_size, suggest_levels
import portfolio
import guide
import ai_analysis


@st.cache_data(ttl=4, show_spinner=False, max_entries=64)
def load_indicator_df(market: str, symbol: str, interval: str):
    """Fetch data + indicators, cached briefly so reruns/tabs are instant & smooth."""
    return add_all_indicators(get_data(market, symbol, interval, limit=200))


def play_alert_sound():
    """Plays a short beep in the browser (on a strong signal)."""
    st.components.v1.html(
        """
        <script>
        try {
          const ctx = new (window.AudioContext || window.webkitAudioContext)();
          const o = ctx.createOscillator(); const g = ctx.createGain();
          o.connect(g); g.connect(ctx.destination);
          o.type = 'sine'; o.frequency.value = 880;
          g.gain.setValueAtTime(0.15, ctx.currentTime);
          o.start();
          g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.4);
          o.stop(ctx.currentTime + 0.4);
        } catch(e) {}
        </script>
        """,
        height=0,
    )

st.set_page_config(page_title="AI Trading Assistant", page_icon="📈", layout="wide")

# ---- For a better look on mobile / phones (plus "Add to Home Screen" support) ----
st.markdown(
    """
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-title" content="AI Trading">
    <meta name="theme-color" content="#0e1117">
    <style>
      /* Adjustments for phones (small screens) */
      @media (max-width: 640px) {
        .block-container { padding: 0.6rem 0.7rem 3rem 0.7rem !important; }
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.2rem !important; }
        h3 { font-size: 1.05rem !important; }
        /* Shrink metrics so the numbers don't get clipped */
        [data-testid="stMetricValue"] { font-size: 1.15rem !important; }
        [data-testid="stMetricLabel"] { font-size: 0.72rem !important; }
        /* Make the tabs horizontally scrollable */
        .stTabs [data-baseweb="tab-list"] {
          overflow-x: auto; flex-wrap: nowrap; scrollbar-width: none;
        }
        .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }
        .stTabs [data-baseweb="tab"] { padding: 0.4rem 0.6rem; font-size: 0.85rem; }
        /* Make buttons easy to tap (touch-friendly) */
        .stButton button { width: 100%; min-height: 2.6rem; }
        /* Let tables scroll horizontally */
        [data-testid="stDataFrame"] { overflow-x: auto; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---- SECURITY: login gate (set a password before deploying) ----
auth.require_login()

PRESETS = {
    "crypto": ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT",
               "DOGEUSDT", "AVAXUSDT", "LTCUSDT", "LINKUSDT", "DOTUSDT", "MATICUSDT"],
    "stock": ["AAPL", "TSLA", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "AMD", "NFLX", "INTC"],
    "forex": ["EURUSD", "GBPUSD", "USDJPY", "USDPKR", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD"],
    "commodity": ["XAUUSD", "XAGUSD", "DXY", "GC=F", "SI=F", "PL=F", "HG=F",
                  "CL=F", "NG=F", "US30", "US500", "NAS100"],
}
MK_LABEL = {"crypto": "Crypto 🪙", "stock": "Stocks 📊", "forex": "Forex 💱",
            "commodity": "Commodities 🥇"}
# Friendly names shown in the Symbol picker (instead of the raw ticker), per market.
SYMBOL_NAMES = {
    "crypto": {
        "BTCUSDT": "Bitcoin (BTCUSDT)", "ETHUSDT": "Ethereum (ETHUSDT)",
        "BNBUSDT": "BNB (BNBUSDT)", "SOLUSDT": "Solana (SOLUSDT)",
        "XRPUSDT": "XRP (XRPUSDT)", "ADAUSDT": "Cardano (ADAUSDT)",
        "DOGEUSDT": "Dogecoin (DOGEUSDT)", "AVAXUSDT": "Avalanche (AVAXUSDT)",
        "LTCUSDT": "Litecoin (LTCUSDT)", "LINKUSDT": "Chainlink (LINKUSDT)",
        "DOTUSDT": "Polkadot (DOTUSDT)", "MATICUSDT": "Polygon (MATICUSDT)",
    },
    "stock": {
        "AAPL": "Apple (AAPL)", "TSLA": "Tesla (TSLA)", "MSFT": "Microsoft (MSFT)",
        "NVDA": "Nvidia (NVDA)", "AMZN": "Amazon (AMZN)", "GOOGL": "Google (GOOGL)",
        "META": "Meta (META)", "AMD": "AMD (AMD)", "NFLX": "Netflix (NFLX)",
        "INTC": "Intel (INTC)",
    },
    "forex": {
        "EURUSD": "Euro / Dollar (EURUSD)", "GBPUSD": "Pound / Dollar (GBPUSD)",
        "USDJPY": "Dollar / Yen (USDJPY)", "USDPKR": "Dollar / Rupee (USDPKR)",
        "AUDUSD": "Aussie / Dollar (AUDUSD)", "USDCAD": "Dollar / Canadian (USDCAD)",
        "USDCHF": "Dollar / Swiss Franc (USDCHF)", "NZDUSD": "Kiwi / Dollar (NZDUSD)",
    },
    "commodity": {
        "XAUUSD": "Gold Spot (XAUUSD)", "XAGUSD": "Silver Spot (XAGUSD)",
        "DXY": "US Dollar Index (DXY)",
        "GC=F": "Gold Futures (GC=F)", "SI=F": "Silver Futures (SI=F)",
        "PL=F": "Platinum (PL=F)", "HG=F": "Copper (HG=F)",
        "CL=F": "Crude Oil (CL=F)", "NG=F": "Natural Gas (NG=F)",
        "US30": "Dow Jones (US30)", "US500": "S&P 500 (US500)",
        "NAS100": "Nasdaq 100 (NAS100)",
    },
}
TF_LABEL = {"1m": "1 Min", "5m": "5 Min", "15m": "15 Min", "1h": "1 Hour", "4h": "4 Hours", "1d": "1 Day"}

# ------------------------------------------------------------------ sidebar
st.sidebar.title("⚙️ Settings")
auth.logout_button()
if st.session_state.get("_no_pw_warning"):
    st.sidebar.warning("🔓 No password is set yet. BEFORE deploying online, be sure to "
                       "add `app_password` to your secrets (see DEPLOY-ONLINE).")
market = st.sidebar.selectbox("Market", ["crypto", "stock", "forex", "commodity"],
                              format_func=lambda m: MK_LABEL[m])
symbol = st.sidebar.selectbox(
    "Symbol", PRESETS[market],
    format_func=lambda s: SYMBOL_NAMES.get(market, {}).get(s, s),
)
custom = st.sidebar.text_input("...or enter your own symbol", "")
if custom.strip():
    symbol = custom.strip().upper()
interval = st.sidebar.selectbox("Timeframe", ["1m", "5m", "15m", "1h", "4h", "1d"],
                                index=3, format_func=lambda i: TF_LABEL[i])

st.sidebar.markdown("---")
st.sidebar.subheader("📈 Chart")
chart_type = st.sidebar.radio("Chart type", ["Candlestick", "Line"], horizontal=True)
show_ind = st.sidebar.multiselect(
    "What to show on the chart?",
    ["Bollinger", "SMA20", "SMA50", "EMA9/21", "VWAP", "Volume", "RSI", "MACD", "Stochastic"],
    default=["Bollinger", "SMA20", "SMA50", "Volume", "RSI", "MACD"],
)

st.sidebar.markdown("---")
st.sidebar.subheader("🤖 AI Analysis (optional)")
ai_provider = st.sidebar.selectbox(
    "AI provider", list(ai_analysis.PROVIDERS.keys()),
    format_func=lambda p: ai_analysis.PROVIDERS[p]["label"],
    help="Pick whichever one you have a key for. All three are optional.",
)
api_key = st.sidebar.text_input(
    f"{ai_analysis.PROVIDERS[ai_provider]['label']} API key", type="password",
    help="Optional. All signals work without a key. The key stays in your browser only.",
)
st.sidebar.caption(f"🔑 Get a free/paid key here: {ai_analysis.PROVIDERS[ai_provider]['key_url']}")
use_ai = st.sidebar.checkbox("Enable AI analysis", value=False)

st.sidebar.markdown("---")
st.sidebar.subheader("🔴 Live Update")
live_on = st.sidebar.checkbox("Live auto-update ON", value=True)
refresh_sec = st.sidebar.select_slider(
    "How often should it update?", options=[3, 5, 10, 15, 30, 60], value=5,
    format_func=lambda s: f"{s} sec",
)
if not is_realtime(market, symbol) and refresh_sec < 30:
    st.sidebar.caption("⚠️ Free Stocks/Forex data (Yahoo) is ~15 min delayed and "
                       "rate-limited — 30 sec will be used here. Only crypto is "
                       "truly seconds-level live.")
sound_on = st.sidebar.checkbox("🔔 Beep on a strong signal", value=True)

# ------------------------------------------------------------------ header
st.title("📈 AI Trading Assistant")
st.caption("For educational purposes only — this tool does not place trades and does not provide financial advice.")

tab_guide, tab_dash, tab_strat, tab_scan, tab_bt, tab_risk, tab_paper = st.tabs(
    ["📚 Learn", "📊 Dashboard", "🎓 Strategies", "🔍 Scanner", "🧪 Backtest",
     "🛡️ Risk Calculator", "📝 Paper Trade"]
)

# ================================================================== TAB 0: GUIDE
with tab_guide:
    guide.render()

# ================================================================== TAB 1: DASHBOARD
with tab_dash:
    # Effective interval: real-time (Binance) sources can refresh fast; Yahoo min 30 sec.
    _eff = refresh_sec if is_realtime(market, symbol) else max(refresh_sec, 30)
    _run_every = _eff if live_on else None

    # This section auto-updates (only this part, not the whole page -> smooth).
    @st.fragment(run_every=_run_every)
    def render_live_dashboard():
        from datetime import datetime
        try:
            df = load_indicator_df(market, symbol, interval)
            sig = generate_signal(df)
        except Exception as e:
            st.error(f"Problem fetching data: {e}")
            st.info("Is the symbol spelled correctly? Is your internet on? Crypto is the most reliable (BTCUSDT).")
            return

        last = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else last
        # Use the latest candle's close as the live price (no extra network call -> faster).
        # For live sources the forming candle already reflects the current price.
        price = float(last["Close"])
        change_pct = ((price - float(prev["Close"])) / float(prev["Close"]) * 100) if prev["Close"] else 0
        rsi_val = last.get("RSI")
        atr_val = float(last["ATR"]) if pd.notna(last.get("ATR")) else 0
        action = sig["action"]
        color = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}[action]

        # live status line
        now = datetime.now().strftime("%H:%M:%S")
        dot = "🟢 LIVE" if live_on else "⚪ paused"
        st.caption(f"{dot} — last update: **{now}** "
                   f"(every {_eff} sec) · source: {'Binance (real-time)' if is_realtime(market, symbol) else 'Yahoo (~15 min delay)'}")

        # ---- OVERALL VERDICT (the single, combined recommendation) ----
        verdict = overall_verdict(df)
        vact = verdict["action"]
        vemoji = {"BUY": "🟢", "SELL": "🔴", "WAIT": "🟡"}[vact]
        vlabel = {"BUY": "BUY (bias up)", "SELL": "SELL (bias down)",
                  "WAIT": "WAIT (no clear edge)"}[vact]
        with st.container(border=True):
            st.markdown(f"## {vemoji} Overall Verdict: {vlabel}")
            st.progress(verdict["buy_score"] / 100,
                        text=f"Buy pressure {verdict['buy_score']}%  ·  "
                             f"Sell pressure {verdict['sell_score']}%  ·  "
                             f"strength {verdict['strength']}%")
            st.write(verdict["summary"])
            with st.expander("What drives this verdict? (combined from all signals)"):
                for name, side, detail in verdict["components"]:
                    se = {"BUY": "🟢", "SELL": "🔴"}.get(side, "⚪")
                    st.markdown(f"- **{name}:** {se} {side} — {detail}")
                st.caption("This blends the technical signal, next-candle prediction, "
                           "6-strategy confluence, and candlestick patterns into one call. "
                           "It is an educational estimate, not a guarantee — always use a stop-loss.")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Price (live)", f"{price:,.4f}".rstrip("0").rstrip("."), f"{change_pct:+.2f}%")
        c2.metric("RSI (14)", f"{rsi_val:.0f}" if pd.notna(rsi_val) else "—")
        c3.metric("Signal", f"{color} {action}", f"strength {sig['score']}%")
        c4.metric("Bull vs Bear", f"{sig['bullish_points']} : {sig['bearish_points']}")

        # alerts
        if pd.notna(rsi_val):
            if rsi_val < 30:
                st.success(f"⚠️ ALERT: RSI {rsi_val:.0f} — oversold (cheap). Chance of a bounce.")
            elif rsi_val > 70:
                st.warning(f"⚠️ ALERT: RSI {rsi_val:.0f} — overbought (expensive). Chance of a pullback.")
        if sig["score"] >= 60 and action != "HOLD":
            st.info(f"🔔 ALERT: Strong {action} signal ({sig['score']}% strength).")
            st.toast(f"🔔 {symbol}: Strong {action} signal ({sig['score']}%)!", icon="🔔")
            if sound_on:
                play_alert_sound()

        # ---- Next Candle Prediction (direction of the next candle) ----
        pred = predict_next_candle(df)
        st.markdown("### 🔮 Next Candle Prediction")
        pdir = pred["direction"]
        pcolor = {"BUY": "🟢", "SELL": "🔴", "NEUTRAL": "🟡"}[pdir]
        ptext = {"BUY": "Likely to move UP (BUY)",
                 "SELL": "Likely to move DOWN (SELL)",
                 "NEUTRAL": "No clear direction (wait)"}[pdir]
        pc1, pc2, pc3 = st.columns([2, 1, 1])
        pc1.metric("Next candle direction", f"{pcolor} {pdir}", ptext)
        pc2.metric("🟢 Up (BUY)", f"{pred['prob_up']}%")
        pc3.metric("🔴 Down (SELL)", f"{pred['prob_down']}%")
        # confidence bar
        st.progress(pred["prob_up"] / 100,
                    text=f"Up {pred['prob_up']}%  vs  Down {pred['prob_down']}%  "
                         f"(confidence {pred['confidence']}%)")
        if pdir == "BUY":
            st.success(f"🟢 Model estimate: next candle **UP (BUY)** — {pred['confidence']}% confidence.")
        elif pdir == "SELL":
            st.error(f"🔴 Model estimate: next candle **DOWN (SELL)** — {pred['confidence']}% confidence.")
        else:
            st.warning("🟡 Direction is unclear — better to wait a bit.")
        with st.expander("🔍 How was this estimate made? (see the reasons)"):
            for r in pred["reasons"]:
                st.markdown(f"- {r}")
            st.caption("⚠️ This is NOT a 100% prediction — only a probability estimate. "
                       "The market can reverse at any time. Always set a stop-loss.")
        st.markdown("---")

        # ---- Chart (dynamic: based on the sidebar toggles) ----
        st.subheader(f"{symbol} — {chart_type} + Indicators")
        plot_df = df.tail(120)

        # Lower panels (oscillators) selected by the user
        panels = [p for p in ["Volume", "RSI", "MACD", "Stochastic"] if p in show_ind]
        n_rows = 1 + len(panels)
        heights = [0.55] + [round(0.45 / len(panels), 3)] * len(panels) if panels else [1.0]
        titles = ["Price"] + panels
        fig = make_subplots(rows=n_rows, cols=1, shared_xaxes=True,
                            vertical_spacing=0.03, row_heights=heights,
                            subplot_titles=titles)

        # -- main price (candlestick or line) --
        if chart_type == "Candlestick":
            fig.add_trace(go.Candlestick(
                x=plot_df.index, open=plot_df["Open"], high=plot_df["High"],
                low=plot_df["Low"], close=plot_df["Close"], name="Price"), row=1, col=1)
        else:
            fig.add_trace(go.Scatter(x=plot_df.index, y=plot_df["Close"], name="Price",
                                     line=dict(color="#2ecc71", width=2)), row=1, col=1)

        # -- Prediction badge (top-left corner) — never covers the candles --
        if pred["direction"] in ("BUY", "SELL"):
            if pred["direction"] == "BUY":
                badge, bclr = f"▲ Prediction: BUY {pred['prob_up']}%", "#2ecc71"
            else:
                badge, bclr = f"▼ Prediction: SELL {pred['prob_down']}%", "#e74c3c"
            fig.add_annotation(
                xref="x domain", yref="y domain", x=0.01, y=0.98,
                xanchor="left", yanchor="top", text=badge, showarrow=False,
                font=dict(color="white", size=12), bgcolor=bclr,
                borderpad=4, opacity=0.92)

        # -- overlays on price --
        overlays = []
        if "Bollinger" in show_ind:
            overlays += [("BB_UPPER", "#888"), ("BB_LOWER", "#888")]
        if "SMA20" in show_ind:
            overlays.append(("SMA20", "#f5a623"))
        if "SMA50" in show_ind:
            overlays.append(("SMA50", "#4a90e2"))
        if "EMA9/21" in show_ind:
            overlays += [("EMA9", "#e67e22"), ("EMA21", "#9b59b6")]
        if "VWAP" in show_ind:
            overlays.append(("VWAP", "#1abc9c"))
        for col, clr in overlays:
            if col in plot_df:
                fig.add_trace(go.Scatter(x=plot_df.index, y=plot_df[col], name=col,
                                         line=dict(width=1, color=clr)), row=1, col=1)

        # -- oscillator panels --
        r = 2
        for p in panels:
            if p == "Volume":
                vcolors = ["#2ecc71" if c >= o else "#e74c3c"
                           for o, c in zip(plot_df["Open"], plot_df["Close"])]
                fig.add_trace(go.Bar(x=plot_df.index, y=plot_df["Volume"], name="Volume",
                                     marker_color=vcolors), row=r, col=1)
            elif p == "RSI":
                fig.add_trace(go.Scatter(x=plot_df.index, y=plot_df["RSI"], name="RSI",
                                         line=dict(color="#9b59b6")), row=r, col=1)
                fig.add_hline(y=70, line_dash="dash", line_color="red", row=r, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="green", row=r, col=1)
            elif p == "MACD":
                fig.add_trace(go.Bar(x=plot_df.index, y=plot_df["MACD_HIST"], name="Hist",
                                     marker_color="#7f8c8d"), row=r, col=1)
                fig.add_trace(go.Scatter(x=plot_df.index, y=plot_df["MACD"], name="MACD",
                                         line=dict(color="#2ecc71")), row=r, col=1)
                fig.add_trace(go.Scatter(x=plot_df.index, y=plot_df["MACD_SIGNAL"], name="Signal",
                                         line=dict(color="#e74c3c")), row=r, col=1)
            elif p == "Stochastic":
                fig.add_trace(go.Scatter(x=plot_df.index, y=plot_df["STOCH_K"], name="%K",
                                         line=dict(color="#3498db")), row=r, col=1)
                fig.add_trace(go.Scatter(x=plot_df.index, y=plot_df["STOCH_D"], name="%D",
                                         line=dict(color="#e67e22")), row=r, col=1)
                fig.add_hline(y=80, line_dash="dash", line_color="red", row=r, col=1)
                fig.add_hline(y=20, line_dash="dash", line_color="green", row=r, col=1)
            r += 1

        # -- Current price level line (like TradingView's price line) --
        price_line_color = "#2ecc71" if change_pct >= 0 else "#e74c3c"
        fig.add_hline(
            y=price, line_dash="dot", line_width=1.2, line_color=price_line_color,
            annotation_text=f" {price:,.4f}".rstrip("0").rstrip("."),
            annotation_position="right",
            annotation_font_color="#ffffff",
            annotation_bgcolor=price_line_color,
            row=1, col=1)

        fig.update_layout(height=300 + 130 * len(panels), xaxis_rangeslider_visible=False,
                          margin=dict(l=8, r=68, t=30, b=10), showlegend=True,
                          legend=dict(orientation="h", y=1.02), dragmode="pan",
                          uirevision=f"{symbol}-{interval}",  # keep zoom/view on live refresh
                          transition=dict(duration=0))
        # Price/indicator scale on the RIGHT side (like TradingView / MT5)
        fig.update_yaxes(side="right", showgrid=True, gridcolor="rgba(128,128,128,0.15)")
        st.plotly_chart(fig, use_container_width=True,
                        config={"scrollZoom": True, "displaylogo": False})

        # ---- Candlestick patterns (auto-detect) ----
        pats = detect_patterns(df)
        st.markdown("**🕯️ Candlestick Patterns:** " + bias_summary(pats))
        if pats:
            pc = st.columns(min(len(pats), 3))
            for i, p in enumerate(pats):
                emoji = {"bullish": "🟢", "bearish": "🔴", "neutral": "🟡"}[p["bias"]]
                pc[i % len(pc)].info(f"{emoji} **{p['name']}**\n\n{p['note']}")

        # ---- Suggested levels + support/resistance ----
        st.subheader("🎯 Suggested Levels (educational reference)")
        support, resistance = support_resistance(df)
        direction = action if action in ("BUY", "SELL") else "BUY"
        levels = suggest_levels(price, atr_val, direction)
        lc1, lc2, lc3, lc4 = st.columns(4)
        lc1.metric("Support (floor)", f"{support:,.4f}".rstrip("0").rstrip("."))
        lc2.metric("Resistance (ceiling)", f"{resistance:,.4f}".rstrip("0").rstrip("."))
        if "error" not in levels:
            lc3.metric(f"Stop-Loss ({direction})", f"{levels['stop_loss']:,.4f}".rstrip("0").rstrip("."))
            lc4.metric("Take-Profit", f"{levels['take_profit']:,.4f}".rstrip("0").rstrip("."))
        st.caption("These are based on ATR (volatility) — not guaranteed. Go to the Risk tab to work out your position size.")

        # ---- Fibonacci retracement levels ----
        with st.expander("📐 Fibonacci Levels (where price may pause or reverse)"):
            fib = fibonacci_levels(df)
            fcols = st.columns(len(fib))
            for i, (lvl, val) in enumerate(fib.items()):
                near = "👉 " if abs(val - price) / price < 0.005 else ""
                fcols[i].metric(f"{near}{lvl}", f"{val:,.4f}".rstrip("0").rstrip("."))
            st.caption("The 61.8% level is called the 'Golden' level — price often bounces here. "
                       "👉 = price is currently near this level.")

        # ---- reasons ----
        st.subheader("🧠 Why this signal?")
        for r in sig["reasons"]:
            st.markdown(f"- {r}")

    render_live_dashboard()

    # ---- Multi-Timeframe confluence (on-demand — 4 timeframes check) ----
    st.markdown("---")
    st.subheader("🔀 Multi-Timeframe Confluence")
    st.caption("When 15m, 1h, 4h and 1d all point the same way, "
               "the signal is more reliable. (Runs when you press the button.)")
    if st.button("🔍 Check all timeframes"):
        with st.spinner("Checking 15m, 1h, 4h, 1d..."):
            mtf = multi_timeframe_signal(market, symbol)
        cols = st.columns(len(mtf["per_tf"]))
        for i, (tf, act) in enumerate(mtf["per_tf"].items()):
            emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡", "N/A": "⚪"}.get(act, "⚪")
            cols[i].metric(TF_LABEL.get(tf, tf), f"{emoji} {act}")
        cons = mtf["consensus"]
        if cons == "MIXED":
            st.warning(f"🟡 MIXED — the timeframes disagree with each other "
                       f"({mtf['agree']}/{mtf['total']} agree). Proceed with caution.")
        else:
            ce = "🟢" if cons == "BUY" else "🔴"
            st.success(f"{ce} STRONG {cons} — {mtf['agree']}/{mtf['total']} timeframes "
                       f"point the same way. This is a more reliable signal.")

    # ---- AI (OUTSIDE the auto-refresh — so an API call isn't made on every update) ----
    st.markdown("---")
    st.subheader("🤖 AI Analysis")
    st.caption("AI is on-demand (when you press the button), separate from auto-refresh — "
               "otherwise an API call every few seconds would burn through cost/limits.")
    _prov_label = ai_analysis.PROVIDERS[ai_provider]["label"]
    if not use_ai:
        st.caption("AI is off. Choose 'Enable AI analysis' in the sidebar (optional).")
    elif not ai_analysis.is_available(ai_provider, api_key):
        st.warning(f"Enter your **{_prov_label}** API key in the sidebar (AI is optional).")
    elif st.button(f"🤖 Get analysis from {_prov_label} now"):
        with st.spinner(f"Analyzing with {_prov_label}..."):
            df_ai = load_indicator_df(market, symbol, interval)
            sig_ai = generate_signal(df_ai)
            st.info(ai_analysis.analyze(ai_provider, market, symbol, sig_ai, api_key))

# ================================================================== TAB: STRATEGIES
with tab_strat:
    st.subheader("🎓 Pro Strategies + Confluence")
    st.write("Proven strategies from world-famous traders and books — all at once "
             f"on **{symbol}**. The more strategies that agree on a direction, the stronger the signal.")
    if st.button("⚡ Run all strategies", type="primary"):
        try:
            with st.spinner("Analyzing strategies..."):
                df_st = load_indicator_df(market, symbol, interval)
                res = run_all_strategies(df_st)
        except Exception as e:
            st.error(f"Problem: {e}")
            res = None
        if res:
            cons = res["consensus"]
            if cons == "BUY":
                st.success(f"🟢 CONFLUENCE: BUY — {res['buys']}/{res['total']} strategies "
                           "are pointing up. This is more reliable.")
            elif cons == "SELL":
                st.error(f"🔴 CONFLUENCE: SELL — {res['sells']}/{res['total']} strategies "
                         "are pointing down. This is more reliable.")
            else:
                st.warning(f"🟡 MIXED — the strategies disagree with each other "
                           f"({res['buys']} buy / {res['sells']} sell). Be cautious / wait.")
            rows = []
            for r in res["results"]:
                emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(r["signal"], "⚪")
                rows.append({"Strategy": r["name"], "Signal": f"{emoji} {r['signal']}",
                             "Source": r["source"], "Why": r["note"]})
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            st.caption("⚠️ No strategy wins every time. Risk management matters most.")

    st.markdown("---")
    wisdom.render()

# ================================================================== TAB 2: SCANNER
with tab_scan:
    st.subheader("🔍 Market Scanner")
    st.write("Scan multiple symbols at once to find the best signals. Run it every morning!")
    default_syms = ", ".join(PRESETS[market])
    syms_text = st.text_area("Symbols (comma-separated)", default_syms, height=80)
    if st.button("🚀 Run scan", type="primary"):
        syms = [s.strip().upper() for s in syms_text.split(",") if s.strip()]
        with st.spinner(f"Scanning {len(syms)} symbols..."):
            result = scan(market, syms, interval)
        if not result.empty:
            def _hl(row):
                clr = {"BUY": "background-color: #123d1a", "SELL": "background-color: #3d1212"}.get(row["Signal"], "")
                return [clr] * len(row)
            st.dataframe(result.style.apply(_hl, axis=1), use_container_width=True)
            buys = result[result["Signal"] == "BUY"]
            if not buys.empty:
                st.success(f"🟢 Found {len(buys)} BUY opportunities. Top: {buys.iloc[0]['Symbol']} ({buys.iloc[0]['Strength %']}%)")
        else:
            st.warning("No results found.")

# ================================================================== TAB 3: BACKTEST
with tab_bt:
    st.subheader("🧪 Backtest — test a strategy on history")
    st.write("See what would have happened if you had followed these signals on past data.")
    cap = st.number_input("Starting capital (USD)", value=1000.0, min_value=10.0, step=100.0)
    if st.button("▶️ Run backtest", type="primary"):
        try:
            with st.spinner("Running backtest (this takes a moment)..."):
                df_bt = load_indicator_df(market, symbol, interval)
                res = run_backtest(df_bt, cap)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Final Equity", f"${res['final_equity']:,.2f}", f"{res['total_return_pct']:+.2f}%")
            m2.metric("Strategy Return", f"{res['total_return_pct']:+.2f}%")
            m3.metric("Buy & Hold Return", f"{res['buy_hold_return_pct']:+.2f}%")
            m4.metric("Win Rate", f"{res['win_rate']}%", f"{res['num_trades']} trades")
            if not res["equity_curve"].empty:
                st.line_chart(res["equity_curve"], height=300)
            if res["total_return_pct"] < res["buy_hold_return_pct"]:
                st.info("💡 In this case, simply holding would have been better — a strategy doesn't win every time. That's why risk management matters.")
        except Exception as e:
            st.error(f"Backtest error: {e}")

# ================================================================== TAB 4: RISK CALCULATOR
with tab_risk:
    st.subheader("🛡️ Risk Calculator — the real formula for protecting your capital")
    st.write("Pro rule: risk only **1-2%** of your total capital on a single trade. "
             "This calculator tells you how much to buy.")
    rc1, rc2 = st.columns(2)
    with rc1:
        capital = st.number_input("Total capital (USD)", value=1000.0, min_value=1.0, step=100.0)
        risk_pct = st.slider("Risk per trade (%)", 0.5, 5.0, 1.0, 0.5)
        entry_p = st.number_input("Entry price", value=100.0, min_value=0.0001, format="%.4f")
    with rc2:
        stop_p = st.number_input("Stop-loss price", value=95.0, min_value=0.0001, format="%.4f")
        st.caption("Stop-loss = the price at which you accept the loss and exit.")

    if st.button("🧮 Calculate", type="primary"):
        r = position_size(capital, risk_pct, entry_p, stop_p)
        if "error" in r:
            st.error(r["error"])
        else:
            x1, x2, x3 = st.columns(3)
            x1.metric("Max loss (risk)", f"${r['risk_amount']}")
            x2.metric("Units to buy", f"{r['units']}")
            x3.metric("Total position value", f"${r['position_value']}")
            st.success(
                f"In other words: with ${capital:,.0f} of capital, if you buy at ${entry_p} "
                f"and set your stop-loss at ${stop_p}, buy **{r['units']} units**. "
                f"If it goes wrong, you only lose **${r['risk_amount']}** ({risk_pct}%)."
            )

# ================================================================== TAB 5: PAPER TRADE
with tab_paper:
    st.subheader("📝 Paper Trading — practice without risking real money")
    st.write("Log your practice trades here. The tool will track your profit/loss and win-rate. "
             "Learn to win here for **1 month** first, THEN use real money.")

    # -- portfolio summary --
    s = portfolio.summary()
    m1, m2, m3, m4 = st.columns(4)
    pnl_color = "normal" if s["total_pnl"] == 0 else ("off" if s["total_pnl"] < 0 else "normal")
    m1.metric("Total P&L (practice)", f"${s['total_pnl']:,.2f}")
    m2.metric("Win Rate", f"{s['win_rate']}%", f"{s['wins']}W / {s['losses']}L")
    m3.metric("Closed trades", s["total_trades"])
    m4.metric("Open trades", s["open_trades"])

    st.markdown("---")

    # -- open a new trade --
    st.markdown("#### ➕ Open a new practice trade")
    live_now = get_live_price(market, symbol)
    with st.form("new_trade", clear_on_submit=True):
        f1, f2, f3 = st.columns(3)
        side = f1.selectbox("Side", ["BUY", "SELL"],
                            help="BUY = profit when price rises. SELL = profit when price falls.")
        entry = f2.number_input("Entry price", value=float(live_now) if live_now else 100.0,
                                min_value=0.0, format="%.4f")
        units = f3.number_input("Units (quantity)", value=1.0, min_value=0.0, format="%.6f")
        g1, g2 = st.columns(2)
        sl = g1.number_input("Stop-Loss (optional)", value=0.0, min_value=0.0, format="%.4f")
        tp = g2.number_input("Take-Profit (optional)", value=0.0, min_value=0.0, format="%.4f")
        submitted = st.form_submit_button(f"✅ Open a practice trade on {symbol}", type="primary")
        if submitted:
            portfolio.add_trade(market, symbol, side, entry, units,
                                sl if sl > 0 else None, tp if tp > 0 else None)
            st.success(f"Trade opened: {side} {units} {symbol} @ {entry}")
            st.rerun()

    st.caption(f"💡 Tip: 'Entry' has been pre-filled with the current live price ({live_now}). "
               "Use the 🛡️ Risk Calculator to work out your units.")

    # -- open trades --
    st.markdown("#### 📂 Open trades")
    open_trades = portfolio.get_open()
    if not open_trades:
        st.info("No open trades yet. Open one above.")
    else:
        for t in open_trades:
            cur = get_live_price(t["market"], t["symbol"]) or t["entry"]
            upnl = portfolio.unrealized_pnl(t, cur)
            emoji = "🟢" if upnl >= 0 else "🔴"
            cc = st.columns([3, 2, 2, 2, 2])
            cc[0].markdown(f"**#{t['id']} {t['side']} {t['symbol']}**  \n{t['units']} units @ {t['entry']}")
            cc[1].metric("Current price", f"{cur:,.4f}".rstrip("0").rstrip("."))
            cc[2].metric("Live P&L", f"{emoji} ${upnl:,.2f}")
            cc[3].caption(f"SL: {t['stop_loss'] or '—'}\n\nTP: {t['take_profit'] or '—'}")
            if cc[4].button("Close", key=f"close_{t['id']}"):
                closed = portfolio.close_trade(t["id"], cur)
                st.success(f"Trade #{t['id']} closed. P&L: ${closed['pnl']}")
                st.rerun()

    # -- closed trades --
    st.markdown("#### ✅ Closed trades — history")
    closed_trades = portfolio.get_closed()
    if not closed_trades:
        st.caption("No closed trades yet.")
    else:
        rows = [{
            "ID": t["id"], "Symbol": t["symbol"], "Side": t["side"],
            "Entry": t["entry"], "Exit": t["exit"], "Units": t["units"],
            "P&L $": t["pnl"], "Opened": t["opened_at"], "Closed": t["closed_at"],
        } for t in reversed(closed_trades)]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        if st.button("🗑️ Clear all history"):
            for t in closed_trades:
                portfolio.delete_trade(t["id"])
            st.rerun()

st.markdown("---")
st.caption("⚠️ Disclaimer: Educational tool. Not investment advice. Trading carries a real risk of losing money. Always do your own research.")
