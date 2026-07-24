# 📈 AI Trading Assistant

Ek simple, beginner-friendly tool jo **Crypto, Stocks aur Forex** ka live data
leke technical analysis karta hai, **BUY / SELL / HOLD signals** deta hai, aur
(optional) **AI se plain-language analysis** deta hai.

> ⚠️ **ZAROORI DISCLAIMER**
> Yeh tool sirf **education** ke liye hai. Yeh:
> - Aapke paise se trades **khud NAHI** karta.
> - **Financial / investment advice NAHI** hai.
> - Trading mein paisa **doob bhi** sakta hai.
>
> Har signal ke saath uski **wajah** likhi hoti hai taake aap **seekhein** aur
> **khud** faisla karein. Paisa lagane se pehle apni research karein ya kisi
> licensed advisor se poochein.

---

## 🚀 Kaise chalayein (2 tareeke)

### Tareeka 1 — Sabse aasan (double-click)
1. `START.bat` file par **double-click** karein.
2. Thori der mein browser khud khul jayega dashboard ke saath.
3. Band karna ho to black window mein `Ctrl + C` dabayein.

### Tareeka 2 — Terminal se
```powershell
cd C:\Project\Trading
python -m streamlit run app.py
```

Pehli dafa chalane se pehle (sirf ek baar) dependencies install karein:
```powershell
cd C:\Project\Trading
python -m pip install -r requirements.txt
```

---

## 🖥️ Dashboard kaise use karein

Left side (sidebar) mein:
1. **Market chunein** — Crypto / Stocks / Forex
2. **Symbol** chunein (jaise BTCUSDT, AAPL, EURUSD) — ya apna likhein
3. **Timeframe** — 1 ghanta / 4 ghante / 1 din
4. (Optional) **AI analysis** on karein aur Anthropic API key daalein

Screen par aapko milega:
- **Price + change %**
- **Signal**: 🟢 BUY / 🔴 SELL / 🟡 HOLD (strength ke saath)
- **Alerts**: jab RSI oversold/overbought ho ya signal strong ho
- **Charts**: Price, RSI, MACD
- **Reasons**: signal kis wajah se bana
- **AI analysis** (agar on kiya ho)

---

## 🤖 AI analysis on karna (optional)

AI plain-language mein samjhata hai ke market kya keh raha hai. Iske liye
Anthropic API key chahiye:

1. Key lein: <https://console.anthropic.com>
2. Dashboard ki sidebar mein "Anthropic API key" box mein paste karein
3. "AI analysis on karein" par tick lagayein

> Bina AI ke bhi tool **poora chalta hai** — signals, charts, alerts sab.

---

## 📂 Files kya karti hain

| File | Kaam |
|------|------|
| `app.py` | Dashboard (main screen) |
| `data_sources.py` | Live data laata hai (crypto/stock/forex) |
| `indicators.py` | RSI, MACD, Moving Average, Bollinger calculate karta hai |
| `signals.py` | BUY/SELL/HOLD signal banata hai |
| `ai_analysis.py` | AI (Claude) analysis (optional) |
| `START.bat` | Double-click launcher |

---

## ❓ Masla aaye to

- **"data laane mein masla"** → Internet check karein, symbol theek likhein.
- **"yfinance install nahi"** → `python -m pip install yfinance` chalayein.
- **Stocks/forex ka data nahi aata** → Yahoo par kabhi kabhi symbol format alag
  hota hai. Crypto sabse zyada reliable hai (Binance se).
- **PSX (Pakistan stocks)** → Yahoo par reliable free data nahi hota; is version
  mein US stocks + crypto + major forex best chalte hain.
