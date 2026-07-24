"""
guide.py
---------
"Seekhein" tab — bilkul beginner ke liye poori guide (Roman Urdu).
Yahan trading ki basics, har lafz ka matlab, har tab ka istemaal,
aur paisa kamane ka realistic tareeqa samjhaya gaya hai.
"""

import streamlit as st


def render():
    st.subheader("📚 Seekhein — Zero se shuru")
    st.write("Ghabrayein nahi. Agar abhi kuch samajh nahi aa raha, to yeh guide "
             "shuru se aakhir tak parhein. Har cheez aasan zubaan mein hai.")

    st.info("⏱️ **Jaldi shuru karna hai?** Neeche 'Sabse pehle kya karun?' section "
            "kholein — 5 minute ka plan hai.")

    # ---------------------------------------------------------------- quick start
    with st.expander("🚀 1. Sabse pehle kya karun? (5-minute plan)", expanded=True):
        st.markdown("""
**Aaj hi yeh karein — bina ek rupya lagaye:**

1. Upar **📊 Dashboard** tab kholein. Market "Crypto", Symbol "BTCUSDT" rakhein.
2. Bade rang wale box dekhein: **Price**, **RSI**, **Signal** (🟢 BUY / 🔴 SELL / 🟡 HOLD).
3. Neeche **"Signal kis wajah se?"** parhein — tool khud batata hai kyun.
4. **📝 Paper Trade** tab kholein → ek **practice trade** kholein (asli paisa nahi!).
5. Kuch din baad wapas aayein aur dekhein aapka faisla sahi tha ya galat.

**Bas itna hi.** Pehle hafte sirf *dekhna aur samajhna* hai. Paisa baad mein.
        """)

    # ---------------------------------------------------------------- basics
    with st.expander("💡 2. Trading kya hai? (bilkul basics)"):
        st.markdown("""
**Trading** ka matlab hai: kisi cheez ko **saste mein khareedna** aur **mehnge
mein bechna** — farq aapka nafa (profit).

Misaal: aapne Bitcoin $60,000 mein khareeda, aur $63,000 mein becha → **$3,000 faida**.
Agar $57,000 mein bechna para → **$3,000 nuksan**.

3 mashhoor markets:
- 🪙 **Crypto** — Bitcoin, Ethereum waghera. 24 ghante khula. Sabse zyada upar-neeche hota hai.
- 📊 **Stocks** — companies ke hissay (Apple, Tesla). Din ke waqt khula.
- 💱 **Forex** — currencies (Dollar, Euro). Bara market, kam upar-neeche.

**Sach:** Price kabhi upar kabhi neeche jaata hai. Koi *pakka* nahi bata sakta agla
kya hoga. Is tool ka kaam hai *chances* barhana — guarantee dena nahi.
        """)

    # ---------------------------------------------------------------- glossary
    with st.expander("📖 3. Zaroori lafz (dictionary) — sab aasan mein"):
        st.markdown("""
| Lafz | Aasan matlab |
|------|--------------|
| **Signal** | Tool ka mashwara: 🟢 BUY (khareedne layak), 🔴 SELL (bechne layak), 🟡 HOLD (rukein) |
| **RSI** | 0-100 ka number. **30 se neeche = sasta** (barhne ka chance), **70 se upar = mehnga** (girne ka chance) |
| **Moving Average (SMA/EMA)** | Pichle kuch din ka average price. Trend dekhne ke liye |
| **MACD** | Momentum (raftaar) dikhata hai — market upar ki taraf tez hai ya neeche |
| **Bollinger Bands** | Price ka "normal range". Upar wali line = mehnga, neeche wali = sasta |
| **Support** | Woh price jahan se aksar price wapas **upar** bounce karta hai (farsh/floor) |
| **Resistance** | Woh price jahan se aksar price wapas **neeche** aata hai (chhat/ceiling) |
| **Stop-Loss** | Woh price jahan aap nuksan qubool karke **nikal jaate** hain (paisa bachata hai) |
| **Take-Profit** | Woh price jahan aap **faida le kar** nikal jaate hain |
| **ATR** | Market kitna "hilta" hai (volatility). Stop-loss set karne ke liye |
| **Bullish / Bearish** | Bullish = upar jaane ki umeed 🐂, Bearish = neeche jaane ki umeed 🐻 |
| **Overbought / Oversold** | Overbought = bohat khareeda gaya (mehnga), Oversold = bohat becha gaya (sasta) |
| **Long / Short** | Long = price barhne par faida (BUY). Short = price girne par faida (SELL) |
        """)

    # ---------------------------------------------------------------- tabs guide
    with st.expander("🧭 4. Is tool ke har tab ka istemaal"):
        st.markdown("""
- **📊 Dashboard** — Ek symbol ka poora haal: live price, chart, signal, aur
  suggested Stop-Loss/Take-Profit. Yahan se *samajhte* hain market kya keh raha hai.

- **🔍 Scanner** — Ek saath bohat saare coins/stocks scan karke batata hai kahan
  **strong signal** ban raha hai. **Rozana subah** yahan se din ki shortlist banayein.

- **🛡️ Risk Calculator** — **Sabse zaroori.** Batata hai ek trade mein **kitni units**
  khareedni hain taake galat hone par sirf 1-2% doobe, poora paisa nahi.

- **📝 Paper Trade** — **Bina asli paisa** practice trades. Tool aapka nafa/nuqsan
  aur **win-rate** track karta hai. Yahin par mahino practice karni hai.

- **🧪 Backtest** — Dikhata hai agar yeh strategy pichle data par chalti to kya hota.
  Is se pata chalta hai koi strategy **har waqt** nahi jeet-ti.
        """)

    # ---------------------------------------------------------------- where to trade
    with st.expander("🏦 5. Asli trading kahan karein? (apps/exchanges — sirf maloomat)"):
        st.markdown("""
Yeh tool sirf **analysis** deta hai. Asli khareed-farokht aapko ek **exchange/broker**
par karni hoti hai. Yeh aam mashhoor platforms hain (yeh sirf **maloomat** hai, kisi
ek ki sifarish nahi — apni research aur apne mulk ke qanoon zaroor check karein):

**Crypto ke liye (aam naam):**
- Binance, Coinbase, Kraken, OKX, Bybit

**Stocks ke liye (aam naam):**
- Interactive Brokers, eToro (kai jagah), local brokers

**⚠️ Pakistan/local note:**
- Har mulk mein har app kaam nahi karti, aur crypto ke qawaneen mukhtalif hote hain.
  Account banane se pehle apne mulk ka qanoon check karein.
- Deposit/withdraw ke tareeqe (bank, card) mulk ke hisab se alag hote hain.

**Main aapke liye account NAHI bana sakta aur na hi paise ki transaction kar sakta
hoon** — yeh aapko khud, apni marzi se, apni tehqeeq ke baad karna hoga. Yeh aapki
hifazat ke liye hai.
        """)

    # ---------------------------------------------------------------- roadmap
    with st.expander("🗺️ 6. Paisa kamane ka REALISTIC roadmap"):
        st.markdown("""
**Koi bhi jo 'har din pakka profit' ya 'paisa double' ka wada kare — SCAM hai.**
Asli tareeqa dheema aur mehfooz hai:

**Hafta 1-2: Sirf dekho**
- Rozana Dashboard aur Scanner kholo. Signals dekho. Lafz samjho.
- Kuch mat khareedo. Bas nazar banao.

**Hafta 3-6: Paper Trade (bina paisa)**
- 📝 Paper Trade tab mein rozana 1-2 practice trade karo.
- Har trade par Stop-Loss aur Take-Profit likho.
- Apna **win-rate** dekho. Target: **60%+ baar sahi**.

**Mahina 2-3: Chhoti asli raqam**
- Jab paper mein consistent jeetne lago, tab **itni chhoti raqam** se shuru karo
  jo doob bhi jaye to zindagi par farq na paray.
- Har trade par **Risk Calculator** use karo (1-2% rule).

**Aage:**
- Consistency sab kuch hai. Mahine mein 5-10% bhi **bohat achha** hai.
- Jaldi ameer banne ki koshish hi zyadatar logon ka paisa dubo deti hai.
        """)

    # ---------------------------------------------------------------- golden rules
    with st.expander("🏅 7. Sunehri usool (yeh yaad rakho to paisa bachega)"):
        st.markdown("""
1. **Hamesha Stop-Loss lagao.** Bina stop-loss trade = aankh band kar ke gaari chalana.
2. **Ek trade par sirf 1-2% risk.** 10 trade galat bhi ho jayein to bhi aap zinda ho.
3. **Emotion se trade mat karo.** Dar (fear) aur laalach (greed) sabse bare dushman.
4. **Har signal par mat kudo.** Sirf strong (60%+) aur samajh mein aane wale par.
5. **Jo doobne ka gham na kar sako, utna hi lagao.** Udhaar ya zaroorat ka paisa kabhi nahi.
6. **Seekhte raho.** Har trade — jeet ya haar — se ek sabak likho.
        """)

    # ---------------------------------------------------------------- scam warning
    with st.expander("🚨 8. Scam se bachein (bohat zaroori)"):
        st.markdown("""
Yeh baatein sun-te hi **bhag jayein** — yeh 100% dhoka hain:
- "Paisa lagao, **double** kar ke denge" / "guaranteed profit"
- "Sirf hamare signal group ki fees do, ameer ho jao"
- Koi ajnabi WhatsApp/Telegram par 'investment plan' de raha ho
- Aisa banda jo aapke paise apne account mein 'manage' karne ko kahe

**Yaad rakho:** Agar paisa kamana itna aasan aur pakka hota, to koi bhi kaam na karta.
Yeh tool aapko **seekhne aur khud faisla karne** mein madad deta hai — koi jaadu nahi.
        """)

    st.markdown("---")
    st.success("✅ Ab aap taiyaar hain! **📊 Dashboard** se shuru karein, phir "
               "**📝 Paper Trade** mein practice karein. Koi sawal ho to poochein.")
