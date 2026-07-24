"""
guide.py
---------
"Learn" tab — a complete guide for absolute beginners (English).
Covers trading basics, the meaning of every term, how to use each tab,
and a realistic approach to making money.
"""

import streamlit as st


def render():
    st.subheader("📚 Learn — Start from Zero")
    st.write("Don't worry. If things aren't making sense yet, read this guide "
             "from start to finish. Everything is explained in plain language.")

    st.info("⏱️ **Want a quick start?** Open the 'What should I do first?' section "
            "below — it's a 5-minute plan.")

    # ---------------------------------------------------------------- quick start
    with st.expander("🚀 1. What should I do first? (5-minute plan)", expanded=True):
        st.markdown("""
**Do this today — without spending a single rupee:**

1. Open the **📊 Dashboard** tab above. Set Market to "Crypto" and Symbol to "BTCUSDT".
2. Look at the large coloured boxes: **Price**, **RSI**, **Signal** (🟢 BUY / 🔴 SELL / 🟡 HOLD).
3. Read **"Why this signal?"** below — the tool explains its reasoning.
4. Open the **📝 Paper Trade** tab → open a **practice trade** (no real money!).
5. Come back after a few days and check whether your decision was right or wrong.

**That's all.** For the first week, just *watch and understand*. Money comes later.
        """)

    # ---------------------------------------------------------------- basics
    with st.expander("💡 2. What is trading? (the very basics)"):
        st.markdown("""
**Trading** means: **buying** something **cheap** and **selling** it **expensive** —
the difference is your profit.

Example: you bought Bitcoin at $60,000 and sold it at $63,000 → **$3,000 profit**.
If you had to sell at $57,000 → **$3,000 loss**.

3 well-known markets:
- 🪙 **Crypto** — Bitcoin, Ethereum, etc. Open 24 hours. Moves up and down the most.
- 📊 **Stocks** — shares of companies (Apple, Tesla). Open during the day.
- 💱 **Forex** — currencies (Dollar, Euro). A huge market with smaller moves.

**The truth:** Prices go up and down. Nobody can say for *certain* what happens next.
This tool's job is to *improve your odds* — not to give guarantees.
        """)

    # ---------------------------------------------------------------- glossary
    with st.expander("📖 3. Essential terms (dictionary) — all in plain language"):
        st.markdown("""
| Term | Simple meaning |
|------|--------------|
| **Signal** | The tool's suggestion: 🟢 BUY (worth buying), 🔴 SELL (worth selling), 🟡 HOLD (wait) |
| **RSI** | A number from 0-100. **Below 30 = cheap** (chance of rising), **above 70 = expensive** (chance of falling) |
| **Moving Average (SMA/EMA)** | The average price over recent days. Used to see the trend |
| **MACD** | Shows momentum — whether the market is accelerating up or down |
| **Bollinger Bands** | The price's "normal range". Upper line = expensive, lower line = cheap |
| **Support** | The price where the market often **bounces back up** (the floor) |
| **Resistance** | The price where the market often **turns back down** (the ceiling) |
| **Stop-Loss** | The price where you accept the loss and **exit** the trade (it protects your capital) |
| **Take-Profit** | The price where you **take your profit** and exit |
| **ATR** | How much the market "moves" (volatility). Used to set your stop-loss |
| **Bullish / Bearish** | Bullish = expecting a rise 🐂, Bearish = expecting a fall 🐻 |
| **Overbought / Oversold** | Overbought = bought heavily (expensive), Oversold = sold heavily (cheap) |
| **Long / Short** | Long = profit when price rises (BUY). Short = profit when price falls (SELL) |
        """)

    # ---------------------------------------------------------------- tabs guide
    with st.expander("🧭 4. How to use each tab of this tool"):
        st.markdown("""
- **📊 Dashboard** — The full picture for one symbol: live price, chart, signal, and
  suggested Stop-Loss/Take-Profit. This is where you *understand* what the market is saying.

- **🔍 Scanner** — Scans many coins/stocks at once and tells you where a
  **strong signal** is forming. Use it **every morning** to build your shortlist for the day.

- **🛡️ Risk Calculator** — **The most important tool.** It tells you **how many units**
  to buy in a trade so that if you're wrong, you only lose 1-2%, not your whole account.

- **📝 Paper Trade** — Practice trades with **no real money**. The tool tracks your
  profit/loss and **win rate**. This is where you should practise for months.

- **🧪 Backtest** — Shows what would have happened if this strategy had run on past data.
  It reveals that no strategy wins **every time**.
        """)

    # ---------------------------------------------------------------- where to trade
    with st.expander("🏦 5. Where to trade for real? (apps/exchanges — information only)"):
        st.markdown("""
This tool only provides **analysis**. Actual buying and selling has to be done on an
**exchange/broker**. These are some common, well-known platforms (this is **information
only**, not a recommendation of any one — always do your own research and check the laws
of your country):

**For crypto (common names):**
- Binance, Coinbase, Kraken, OKX, Bybit

**For stocks (common names):**
- Interactive Brokers, eToro (in many regions), local brokers

**⚠️ Pakistan/local note:**
- Not every app works in every country, and crypto regulations differ from place to place.
  Check your country's laws before opening an account.
- Deposit/withdrawal methods (bank, card) vary by country.

**I CANNOT open an account for you or carry out any money transactions** — you must do
that yourself, of your own free will, after your own research. This is for your own
protection.
        """)

    # ---------------------------------------------------------------- roadmap
    with st.expander("🗺️ 6. A REALISTIC roadmap to making money"):
        st.markdown("""
**Anyone who promises 'guaranteed daily profit' or to 'double your money' is a SCAM.**
The real way is slow and safe:

**Weeks 1-2: Just watch**
- Open the Dashboard and Scanner daily. Watch the signals. Learn the terms.
- Don't buy anything. Just train your eye.

**Weeks 3-6: Paper Trade (no money)**
- Do 1-2 practice trades daily in the 📝 Paper Trade tab.
- Write down a Stop-Loss and Take-Profit for every trade.
- Watch your **win rate**. Target: **right 60%+ of the time**.

**Months 2-3: Small real amounts**
- Once you're winning consistently on paper, start with **an amount so small**
  that even if you lose it, it makes no difference to your life.
- Use the **Risk Calculator** on every trade (the 1-2% rule).

**Beyond:**
- Consistency is everything. Even 5-10% a month is **very good**.
- Trying to get rich quick is exactly what wipes out most people's money.
        """)

    # ---------------------------------------------------------------- golden rules
    with st.expander("🏅 7. Golden rules (remember these and you'll save money)"):
        st.markdown("""
1. **Always set a Stop-Loss.** A trade without a stop-loss = driving with your eyes closed.
2. **Risk only 1-2% per trade.** Even if 10 trades go wrong, you're still standing.
3. **Don't trade on emotion.** Fear and greed are your biggest enemies.
4. **Don't jump on every signal.** Only strong ones (60%+) that you understand.
5. **Only risk what you can afford to lose.** Never borrowed money or money you need.
6. **Keep learning.** From every trade — win or lose — write down one lesson.
        """)

    # ---------------------------------------------------------------- scam warning
    with st.expander("🚨 8. Avoid scams (very important)"):
        st.markdown("""
The moment you hear these, **walk away** — they are 100% frauds:
- "Invest your money, we'll **double** it" / "guaranteed profit"
- "Just pay our signal group's fee and get rich"
- A stranger offering an 'investment plan' on WhatsApp/Telegram
- Anyone asking to 'manage' your money in their own account

**Remember:** If making money were this easy and certain, nobody would work at all.
This tool helps you **learn and decide for yourself** — there is no magic.
        """)

    st.markdown("---")
    st.success("✅ Now you're ready! Start with the **📊 Dashboard**, then "
               "practise in **📝 Paper Trade**. If you have any questions, just ask.")
