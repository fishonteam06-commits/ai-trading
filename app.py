"""
app.py  —  AI Trading Assistant (ADVANCED Dashboard)
=====================================================
Chalane ke liye terminal mein:  streamlit run app.py
Ya START.bat par double-click.

Tabs:
  1. 📊 Dashboard  — live candlestick chart + indicators + signal + AI
  2. 🔍 Scanner    — ek saath kai symbols scan, best opportunities upar
  3. 🧪 Backtest   — strategy ko history par test karo
  4. 🛡️ Risk Calc  — position size, stop-loss, take-profit (paisa bachao)

** DISCLAIMER **: Sirf EDUCATION ke liye. Trades khud execute NAHI karta,
financial advice NAHI hai. Trading mein paisa doob sakta hai.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from data_sources import get_data, get_live_price
from indicators import add_all_indicators, support_resistance, fibonacci_levels
from signals import generate_signal, multi_timeframe_signal
from patterns import detect_patterns, bias_summary
from predictor import predict_next_candle
from strategies import run_all_strategies
import wisdom
import auth
from scanner import scan
from backtest import run_backtest
from risk import position_size, suggest_levels
import portfolio
import guide
import ai_analysis


def play_alert_sound():
    """Browser mein ek chhoti beep bajata hai (strong signal par)."""
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

# ---- Mobile / phone par acha dikhne ke liye (aur "Add to Home Screen" support) ----
st.markdown(
    """
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-title" content="AI Trading">
    <meta name="theme-color" content="#0e1117">
    <style>
      /* Phone (chhoti screen) ke liye adjustments */
      @media (max-width: 640px) {
        .block-container { padding: 0.6rem 0.7rem 3rem 0.7rem !important; }
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.2rem !important; }
        h3 { font-size: 1.05rem !important; }
        /* Metrics chhote karo taake number kate nahi */
        [data-testid="stMetricValue"] { font-size: 1.15rem !important; }
        [data-testid="stMetricLabel"] { font-size: 0.72rem !important; }
        /* Tabs ko scroll karne layak banao */
        .stTabs [data-baseweb="tab-list"] {
          overflow-x: auto; flex-wrap: nowrap; scrollbar-width: none;
        }
        .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }
        .stTabs [data-baseweb="tab"] { padding: 0.4rem 0.6rem; font-size: 0.85rem; }
        /* Buttons ungli se dabane layak (touch-friendly) */
        .stButton button { width: 100%; min-height: 2.6rem; }
        /* Tables horizontally scroll karein */
        [data-testid="stDataFrame"] { overflow-x: auto; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---- SECURITY: login gate (deploy karne se pehle password set karein) ----
auth.require_login()

PRESETS = {
    "crypto": ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "AVAXUSDT"],
    "stock": ["AAPL", "TSLA", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "AMD"],
    "forex": ["EURUSD", "GBPUSD", "USDJPY", "USDPKR", "AUDUSD", "USDCAD"],
}
MK_LABEL = {"crypto": "Crypto 🪙", "stock": "Stocks 📊", "forex": "Forex 💱"}
TF_LABEL = {"5m": "5 Min", "15m": "15 Min", "1h": "1 Ghanta", "4h": "4 Ghante", "1d": "1 Din"}

# ------------------------------------------------------------------ sidebar
st.sidebar.title("⚙️ Settings")
auth.logout_button()
if st.session_state.get("_no_pw_warning"):
    st.sidebar.warning("🔓 Abhi koi password set nahi. Online deploy karne se PEHLE "
                       "secrets mein `app_password` zaroor daalein (DEPLOY-ONLINE dekhein).")
market = st.sidebar.selectbox("Market", ["crypto", "stock", "forex"], format_func=lambda m: MK_LABEL[m])
symbol = st.sidebar.selectbox("Symbol", PRESETS[market])
custom = st.sidebar.text_input("...ya apna symbol likhein", "")
if custom.strip():
    symbol = custom.strip().upper()
interval = st.sidebar.selectbox("Timeframe", ["5m", "15m", "1h", "4h", "1d"],
                                index=2, format_func=lambda i: TF_LABEL[i])

st.sidebar.markdown("---")
st.sidebar.subheader("📈 Chart")
chart_type = st.sidebar.radio("Chart type", ["Candlestick", "Line"], horizontal=True)
show_ind = st.sidebar.multiselect(
    "Chart par kya dikhayein?",
    ["Bollinger", "SMA20", "SMA50", "EMA9/21", "VWAP", "Volume", "RSI", "MACD", "Stochastic"],
    default=["Bollinger", "SMA20", "SMA50", "Volume", "RSI", "MACD"],
)

st.sidebar.markdown("---")
st.sidebar.subheader("🤖 AI Analysis (optional)")
ai_provider = st.sidebar.selectbox(
    "AI provider", list(ai_analysis.PROVIDERS.keys()),
    format_func=lambda p: ai_analysis.PROVIDERS[p]["label"],
    help="Jo aapke paas key ho wahi chunein. Teeno optional hain.",
)
api_key = st.sidebar.text_input(
    f"{ai_analysis.PROVIDERS[ai_provider]['label']} API key", type="password",
    help="Optional. Bina key ke bhi saare signals chalte hain. Key browser mein hi rehti hai.",
)
st.sidebar.caption(f"🔑 Free/paid key yahan se: {ai_analysis.PROVIDERS[ai_provider]['key_url']}")
use_ai = st.sidebar.checkbox("AI analysis on karein", value=False)

st.sidebar.markdown("---")
st.sidebar.subheader("🔴 Live Update")
live_on = st.sidebar.checkbox("Live auto-update ON", value=True)
refresh_sec = st.sidebar.select_slider(
    "Kitni jaldi update ho?", options=[3, 5, 10, 15, 30, 60], value=5,
    format_func=lambda s: f"{s} sec",
)
if market != "crypto" and refresh_sec < 30:
    st.sidebar.caption("⚠️ Stocks/Forex ka free data (Yahoo) ~15 min delayed aur "
                       "rate-limited hota hai — yahan 30 sec use hoga. Sirf crypto "
                       "hi asli seconds-level live hai.")
sound_on = st.sidebar.checkbox("🔔 Strong signal par beep bajayein", value=True)

# ------------------------------------------------------------------ header
st.title("📈 AI Trading Assistant")
st.caption("Sirf education ke liye — yeh tool trades khud nahi karta aur financial advice nahi deta.")

tab_guide, tab_dash, tab_strat, tab_scan, tab_bt, tab_risk, tab_paper = st.tabs(
    ["📚 Seekhein", "📊 Dashboard", "🎓 Strategies", "🔍 Scanner", "🧪 Backtest",
     "🛡️ Risk Calculator", "📝 Paper Trade"]
)

# ================================================================== TAB 0: GUIDE
with tab_guide:
    guide.render()

# ================================================================== TAB 1: DASHBOARD
with tab_dash:
    # Effective interval: crypto seconds-level; stock/forex kam se kam 30 sec.
    _eff = refresh_sec if market == "crypto" else max(refresh_sec, 30)
    _run_every = _eff if live_on else None

    # Yeh hissa auto-update hota hai (sirf yahi, poora page nahi -> smooth).
    @st.fragment(run_every=_run_every)
    def render_live_dashboard():
        from datetime import datetime
        try:
            df = add_all_indicators(get_data(market, symbol, interval, limit=200))
            sig = generate_signal(df)
        except Exception as e:
            st.error(f"Data laane mein masla: {e}")
            st.info("Symbol theek likha? Internet on hai? Crypto sabse reliable hai (BTCUSDT).")
            return

        last = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else last
        # Live latest price (halki call) — chart wale candle se bhi fresh
        live_price = get_live_price(market, symbol)
        price = live_price if live_price else float(last["Close"])
        change_pct = ((price - float(prev["Close"])) / float(prev["Close"]) * 100) if prev["Close"] else 0
        rsi_val = last.get("RSI")
        atr_val = float(last["ATR"]) if pd.notna(last.get("ATR")) else 0
        action = sig["action"]
        color = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}[action]

        # live status line
        now = datetime.now().strftime("%H:%M:%S")
        dot = "🟢 LIVE" if live_on else "⚪ paused"
        st.caption(f"{dot} — aakhri update: **{now}** "
                   f"(har {_eff} sec) · source: {'Binance (real-time)' if market=='crypto' else 'Yahoo (~15 min delay)'}")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Price (live)", f"{price:,.4f}".rstrip("0").rstrip("."), f"{change_pct:+.2f}%")
        c2.metric("RSI (14)", f"{rsi_val:.0f}" if pd.notna(rsi_val) else "—")
        c3.metric("Signal", f"{color} {action}", f"strength {sig['score']}%")
        c4.metric("Bull vs Bear", f"{sig['bullish_points']} : {sig['bearish_points']}")

        # alerts
        if pd.notna(rsi_val):
            if rsi_val < 30:
                st.success(f"⚠️ ALERT: RSI {rsi_val:.0f} — oversold (sasta). Bounce ka chance.")
            elif rsi_val > 70:
                st.warning(f"⚠️ ALERT: RSI {rsi_val:.0f} — overbought (mehnga). Pullback ka chance.")
        if sig["score"] >= 60 and action != "HOLD":
            st.info(f"🔔 ALERT: Strong {action} signal ({sig['score']}% strength).")
            st.toast(f"🔔 {symbol}: Strong {action} signal ({sig['score']}%)!", icon="🔔")
            if sound_on:
                play_alert_sound()

        # ---- Agli Candle Prediction (next candle ka rukh) ----
        pred = predict_next_candle(df)
        st.markdown("### 🔮 Agli Candle Prediction")
        pdir = pred["direction"]
        pcolor = {"BUY": "🟢", "SELL": "🔴", "NEUTRAL": "🟡"}[pdir]
        ptext = {"BUY": "UPAR jaane ka imkaan (BUY)",
                 "SELL": "NEECHE jaane ka imkaan (SELL)",
                 "NEUTRAL": "Saaf rukh nahi (wait karein)"}[pdir]
        pc1, pc2, pc3 = st.columns([2, 1, 1])
        pc1.metric("Agli candle ka rukh", f"{pcolor} {pdir}", ptext)
        pc2.metric("🟢 Upar (BUY)", f"{pred['prob_up']}%")
        pc3.metric("🔴 Neeche (SELL)", f"{pred['prob_down']}%")
        # confidence bar
        st.progress(pred["prob_up"] / 100,
                    text=f"Upar {pred['prob_up']}%  vs  Neeche {pred['prob_down']}%  "
                         f"(confidence {pred['confidence']}%)")
        if pdir == "BUY":
            st.success(f"🟢 Model ka anumaan: agli candle **UPAR (BUY)** — {pred['confidence']}% confidence.")
        elif pdir == "SELL":
            st.error(f"🔴 Model ka anumaan: agli candle **NEECHE (SELL)** — {pred['confidence']}% confidence.")
        else:
            st.warning("🟡 Rukh saaf nahi — behtar hai thora rukein.")
        with st.expander("🔍 Yeh anumaan kaise laga? (wajah dekhein)"):
            for r in pred["reasons"]:
                st.markdown(f"- {r}")
            st.caption("⚠️ Yeh 100% pesh-goi NAHI — sirf probability estimate. "
                       "Market kabhi bhi palat sakta hai. Stop-loss zaroor lagayein.")
        st.markdown("---")

        # ---- Chart (dynamic: sidebar toggles ke hisab se) ----
        st.subheader(f"{symbol} — {chart_type} + Indicators")
        plot_df = df.tail(120)

        # Neeche wale panels (oscillators) jo user ne chune
        panels = [p for p in ["Volume", "RSI", "MACD", "Stochastic"] if p in show_ind]
        n_rows = 1 + len(panels)
        heights = [0.55] + [round(0.45 / len(panels), 3)] * len(panels) if panels else [1.0]
        titles = ["Price"] + panels
        fig = make_subplots(rows=n_rows, cols=1, shared_xaxes=True,
                            vertical_spacing=0.03, row_heights=heights,
                            subplot_titles=titles)

        # -- main price (candlestick ya line) --
        if chart_type == "Candlestick":
            fig.add_trace(go.Candlestick(
                x=plot_df.index, open=plot_df["Open"], high=plot_df["High"],
                low=plot_df["Low"], close=plot_df["Close"], name="Price"), row=1, col=1)
        else:
            fig.add_trace(go.Scatter(x=plot_df.index, y=plot_df["Close"], name="Price",
                                     line=dict(color="#2ecc71", width=2)), row=1, col=1)

        # -- Prediction ARROW candle ke upar (agli candle ka rukh) --
        if pred["direction"] in ("BUY", "SELL"):
            last_x = plot_df.index[-1]
            hi = float(plot_df["High"].iloc[-1])
            if pred["direction"] == "BUY":
                fig.add_annotation(
                    x=last_x, y=hi, row=1, col=1,
                    text=f"▲ BUY {pred['prob_up']}%",
                    showarrow=True, arrowhead=2, arrowsize=1.6, arrowwidth=2.5,
                    arrowcolor="#2ecc71", ax=0, ay=-45,
                    font=dict(color="#2ecc71", size=13),
                    bgcolor="rgba(0,0,0,0.55)", bordercolor="#2ecc71", borderwidth=1)
            else:
                fig.add_annotation(
                    x=last_x, y=hi, row=1, col=1,
                    text=f"▼ SELL {pred['prob_down']}%",
                    showarrow=True, arrowhead=2, arrowsize=1.6, arrowwidth=2.5,
                    arrowcolor="#e74c3c", ax=0, ay=-45,
                    font=dict(color="#e74c3c", size=13),
                    bgcolor="rgba(0,0,0,0.55)", bordercolor="#e74c3c", borderwidth=1)

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

        fig.update_layout(height=300 + 130 * len(panels), xaxis_rangeslider_visible=False,
                          margin=dict(l=10, r=10, t=30, b=10), showlegend=True,
                          legend=dict(orientation="h", y=1.02), dragmode="pan")
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
        st.caption("Yeh ATR (volatility) par bane hain — guarantee nahi. Risk tab par jaa kar apna size nikaalein.")

        # ---- Fibonacci retracement levels ----
        with st.expander("📐 Fibonacci Levels (jahan price ruk/palat sakti hai)"):
            fib = fibonacci_levels(df)
            fcols = st.columns(len(fib))
            for i, (lvl, val) in enumerate(fib.items()):
                near = "👉 " if abs(val - price) / price < 0.005 else ""
                fcols[i].metric(f"{near}{lvl}", f"{val:,.4f}".rstrip("0").rstrip("."))
            st.caption("61.8% ko 'Golden' level kehte hain — yahan aksar bounce hota hai. "
                       "👉 = price abhi is level ke qareeb hai.")

        # ---- reasons ----
        st.subheader("🧠 Signal kis wajah se?")
        for r in sig["reasons"]:
            st.markdown(f"- {r}")

    render_live_dashboard()

    # ---- Multi-Timeframe confluence (on-demand — 4 timeframes check) ----
    st.markdown("---")
    st.subheader("🔀 Multi-Timeframe Confluence")
    st.caption("Jab 15m, 1h, 4h aur 1d — chaaron ek hi taraf ishaara karein, "
               "to signal zyada bharosemand hota hai. (Button dabane par chalta hai.)")
    if st.button("🔍 Saare timeframes check karein"):
        with st.spinner("15m, 1h, 4h, 1d check ho rahe hain..."):
            mtf = multi_timeframe_signal(market, symbol)
        cols = st.columns(len(mtf["per_tf"]))
        for i, (tf, act) in enumerate(mtf["per_tf"].items()):
            emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡", "N/A": "⚪"}.get(act, "⚪")
            cols[i].metric(TF_LABEL.get(tf, tf), f"{emoji} {act}")
        cons = mtf["consensus"]
        if cons == "MIXED":
            st.warning(f"🟡 MIXED — timeframes aapas mein ikhtelaaf kar rahe hain "
                       f"({mtf['agree']}/{mtf['total']} agree). Ehtiyaat karein.")
        else:
            ce = "🟢" if cons == "BUY" else "🔴"
            st.success(f"{ce} STRONG {cons} — {mtf['agree']}/{mtf['total']} timeframes "
                       f"ek hi taraf. Yeh zyada bharosemand signal hai.")

    # ---- AI (auto-refresh se BAHAR — taake har update par API call na ho) ----
    st.markdown("---")
    st.subheader("🤖 AI Analysis")
    st.caption("AI on-demand hai (button dabane par), auto-refresh se alag — "
               "warna har few seconds mein API call ho kar paise/limit kharch hote.")
    _prov_label = ai_analysis.PROVIDERS[ai_provider]["label"]
    if not use_ai:
        st.caption("AI off hai. Sidebar se 'AI analysis on karein' choose karein (optional).")
    elif not ai_analysis.is_available(ai_provider, api_key):
        st.warning(f"Sidebar mein **{_prov_label}** ki API key daalein (AI optional hai).")
    elif st.button(f"🤖 Ab {_prov_label} se analysis lein"):
        with st.spinner(f"{_prov_label} se analysis..."):
            df_ai = add_all_indicators(get_data(market, symbol, interval, limit=200))
            sig_ai = generate_signal(df_ai)
            st.info(ai_analysis.analyze(ai_provider, market, symbol, sig_ai, api_key))

# ================================================================== TAB: STRATEGIES
with tab_strat:
    st.subheader("🎓 Pro Strategies + Confluence")
    st.write("Duniya ke mashhoor traders/books ki proven strategies — sab ek saath "
             f"**{symbol}** par. Jab zyada strategies ek taraf aa jayein, signal utna strong.")
    if st.button("⚡ Saari strategies chalayein", type="primary"):
        try:
            with st.spinner("Strategies analyze ho rahi hain..."):
                df_st = add_all_indicators(get_data(market, symbol, interval, limit=200))
                res = run_all_strategies(df_st)
        except Exception as e:
            st.error(f"Masla: {e}")
            res = None
        if res:
            cons = res["consensus"]
            if cons == "BUY":
                st.success(f"🟢 CONFLUENCE: BUY — {res['buys']}/{res['total']} strategies "
                           "upar keh rahi hain. Yeh zyada bharosemand hai.")
            elif cons == "SELL":
                st.error(f"🔴 CONFLUENCE: SELL — {res['sells']}/{res['total']} strategies "
                         "neeche keh rahi hain. Yeh zyada bharosemand hai.")
            else:
                st.warning(f"🟡 MIXED — strategies aapas mein ikhtelaaf kar rahi hain "
                           f"({res['buys']} buy / {res['sells']} sell). Ehtiyaat karein / wait.")
            rows = []
            for r in res["results"]:
                emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(r["signal"], "⚪")
                rows.append({"Strategy": r["name"], "Signal": f"{emoji} {r['signal']}",
                             "Source": r["source"], "Wajah": r["note"]})
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            st.caption("⚠️ Koi strategy hamesha nahi jeetti. Risk management sab se zaroori hai.")

    st.markdown("---")
    wisdom.render()

# ================================================================== TAB 2: SCANNER
with tab_scan:
    st.subheader("🔍 Market Scanner")
    st.write("Ek saath kai symbols scan karke best signals dhoondein. Rozana subah chalayein!")
    default_syms = ", ".join(PRESETS[market])
    syms_text = st.text_area("Symbols (comma se alag)", default_syms, height=80)
    if st.button("🚀 Scan chalayein", type="primary"):
        syms = [s.strip().upper() for s in syms_text.split(",") if s.strip()]
        with st.spinner(f"{len(syms)} symbols scan ho rahe hain..."):
            result = scan(market, syms, interval)
        if not result.empty:
            def _hl(row):
                clr = {"BUY": "background-color: #123d1a", "SELL": "background-color: #3d1212"}.get(row["Signal"], "")
                return [clr] * len(row)
            st.dataframe(result.style.apply(_hl, axis=1), use_container_width=True)
            buys = result[result["Signal"] == "BUY"]
            if not buys.empty:
                st.success(f"🟢 {len(buys)} BUY opportunities mile. Top: {buys.iloc[0]['Symbol']} ({buys.iloc[0]['Strength %']}%)")
        else:
            st.warning("Koi result nahi mila.")

# ================================================================== TAB 3: BACKTEST
with tab_bt:
    st.subheader("🧪 Backtest — history par strategy test")
    st.write("Dekhein agar yeh signals pichle data par follow karte to kya hota.")
    cap = st.number_input("Shuru ki capital (USD)", value=1000.0, min_value=10.0, step=100.0)
    if st.button("▶️ Backtest chalayein", type="primary"):
        try:
            with st.spinner("Backtest chal raha hai (thora waqt lagta hai)..."):
                df_bt = add_all_indicators(get_data(market, symbol, interval, limit=200))
                res = run_backtest(df_bt, cap)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Final Equity", f"${res['final_equity']:,.2f}", f"{res['total_return_pct']:+.2f}%")
            m2.metric("Strategy Return", f"{res['total_return_pct']:+.2f}%")
            m3.metric("Buy & Hold Return", f"{res['buy_hold_return_pct']:+.2f}%")
            m4.metric("Win Rate", f"{res['win_rate']}%", f"{res['num_trades']} trades")
            if not res["equity_curve"].empty:
                st.line_chart(res["equity_curve"], height=300)
            if res["total_return_pct"] < res["buy_hold_return_pct"]:
                st.info("💡 Is case mein sirf hold karna behtar tha — strategy har waqt jeet nahi. Isi liye risk management zaroori hai.")
        except Exception as e:
            st.error(f"Backtest error: {e}")

# ================================================================== TAB 4: RISK CALCULATOR
with tab_risk:
    st.subheader("🛡️ Risk Calculator — paisa bachane ka asal formula")
    st.write("Pro rule: ek trade par apni total capital ka sirf **1-2%** risk karo. "
             "Yeh calculator batata hai kitna khareedna hai.")
    rc1, rc2 = st.columns(2)
    with rc1:
        capital = st.number_input("Total capital (USD)", value=1000.0, min_value=1.0, step=100.0)
        risk_pct = st.slider("Risk per trade (%)", 0.5, 5.0, 1.0, 0.5)
        entry_p = st.number_input("Entry price", value=100.0, min_value=0.0001, format="%.4f")
    with rc2:
        stop_p = st.number_input("Stop-loss price", value=95.0, min_value=0.0001, format="%.4f")
        st.caption("Stop-loss = wo price jahan aap nuksan qubool karke nikal jayenge.")

    if st.button("🧮 Calculate karein", type="primary"):
        r = position_size(capital, risk_pct, entry_p, stop_p)
        if "error" in r:
            st.error(r["error"])
        else:
            x1, x2, x3 = st.columns(3)
            x1.metric("Max nuksan (risk)", f"${r['risk_amount']}")
            x2.metric("Kitni units khareedein", f"{r['units']}")
            x3.metric("Total position value", f"${r['position_value']}")
            st.success(
                f"Matlab: ${capital:,.0f} capital ke saath, agar aap ${entry_p} par "
                f"khareed kar ${stop_p} par stop-loss lagayein, to **{r['units']} units** "
                f"khareedein. Galat hone par sirf **${r['risk_amount']}** ({risk_pct}%) doobega."
            )

# ================================================================== TAB 5: PAPER TRADE
with tab_paper:
    st.subheader("📝 Paper Trading — bina asli paisa lagaye practice")
    st.write("Yahan apne practice trades likhein. Tool aapka nafa/nuqsan aur win-rate "
             "track karega. Pehle yahan **1 mahina** jeetna seekhein, PHIR asli paisa.")

    # -- portfolio summary --
    s = portfolio.summary()
    m1, m2, m3, m4 = st.columns(4)
    pnl_color = "normal" if s["total_pnl"] == 0 else ("off" if s["total_pnl"] < 0 else "normal")
    m1.metric("Total P&L (practice)", f"${s['total_pnl']:,.2f}")
    m2.metric("Win Rate", f"{s['win_rate']}%", f"{s['wins']}W / {s['losses']}L")
    m3.metric("Closed trades", s["total_trades"])
    m4.metric("Open trades", s["open_trades"])

    st.markdown("---")

    # -- naya trade kholein --
    st.markdown("#### ➕ Naya practice trade kholein")
    live_now = get_live_price(market, symbol)
    with st.form("new_trade", clear_on_submit=True):
        f1, f2, f3 = st.columns(3)
        side = f1.selectbox("Side", ["BUY", "SELL"],
                            help="BUY = price barhne par faida. SELL = price girne par faida.")
        entry = f2.number_input("Entry price", value=float(live_now) if live_now else 100.0,
                                min_value=0.0, format="%.4f")
        units = f3.number_input("Units (kitni quantity)", value=1.0, min_value=0.0, format="%.6f")
        g1, g2 = st.columns(2)
        sl = g1.number_input("Stop-Loss (optional)", value=0.0, min_value=0.0, format="%.4f")
        tp = g2.number_input("Take-Profit (optional)", value=0.0, min_value=0.0, format="%.4f")
        submitted = st.form_submit_button(f"✅ {symbol} par practice trade kholein", type="primary")
        if submitted:
            portfolio.add_trade(market, symbol, side, entry, units,
                                sl if sl > 0 else None, tp if tp > 0 else None)
            st.success(f"Trade khul gaya: {side} {units} {symbol} @ {entry}")
            st.rerun()

    st.caption(f"💡 Tip: 'Entry' abhi ke live price ({live_now}) se bhar diya gaya hai. "
               "Units nikaalne ke liye 🛡️ Risk Calculator use karein.")

    # -- open trades --
    st.markdown("#### 📂 Khule (open) trades")
    open_trades = portfolio.get_open()
    if not open_trades:
        st.info("Abhi koi open trade nahi. Upar se ek kholein.")
    else:
        for t in open_trades:
            cur = get_live_price(t["market"], t["symbol"]) or t["entry"]
            upnl = portfolio.unrealized_pnl(t, cur)
            emoji = "🟢" if upnl >= 0 else "🔴"
            cc = st.columns([3, 2, 2, 2, 2])
            cc[0].markdown(f"**#{t['id']} {t['side']} {t['symbol']}**  \n{t['units']} units @ {t['entry']}")
            cc[1].metric("Abhi price", f"{cur:,.4f}".rstrip("0").rstrip("."))
            cc[2].metric("Live P&L", f"{emoji} ${upnl:,.2f}")
            cc[3].caption(f"SL: {t['stop_loss'] or '—'}\n\nTP: {t['take_profit'] or '—'}")
            if cc[4].button("Band karein", key=f"close_{t['id']}"):
                closed = portfolio.close_trade(t["id"], cur)
                st.success(f"Trade #{t['id']} band. P&L: ${closed['pnl']}")
                st.rerun()

    # -- closed trades --
    st.markdown("#### ✅ Band (closed) trades — history")
    closed_trades = portfolio.get_closed()
    if not closed_trades:
        st.caption("Abhi koi closed trade nahi.")
    else:
        rows = [{
            "ID": t["id"], "Symbol": t["symbol"], "Side": t["side"],
            "Entry": t["entry"], "Exit": t["exit"], "Units": t["units"],
            "P&L $": t["pnl"], "Opened": t["opened_at"], "Closed": t["closed_at"],
        } for t in reversed(closed_trades)]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        if st.button("🗑️ Saari history saaf karein"):
            for t in closed_trades:
                portfolio.delete_trade(t["id"])
            st.rerun()

st.markdown("---")
st.caption("⚠️ Disclaimer: Educational tool. Investment advice nahi. Trading mein paisa doob sakta hai. Apni research khud karein.")
