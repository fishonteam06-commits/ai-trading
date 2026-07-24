"""
strategies.py
--------------
Duniya ke mashhoor traders aur trading books ki PROVEN strategies — har ek
current data par apna signal deti hai, aur saath uska source (kis trader/book se).

Jab kai alag strategies ek hi taraf ishaara karein (confluence), to signal
zyada bharosemand hota hai — yeh professional traders ka tareeka hai.

Sources (asal usool, koi copyrighted text nahi — sirf mechanics + attribution):
  - Turtle Trading / Donchian Breakout ...... Richard Dennis (1983)
  - Moving Average Cross (trend) ............. John Murphy (Technical Analysis)
  - RSI Reversal ............................. J. Welles Wilder (RSI inventor)
  - MACD Momentum ............................ Gerald Appel (MACD inventor)
  - Bollinger Bands Bounce ................... John Bollinger
  - EMA Trend + Pullback ..................... common professional setup

** DISCLAIMER **: Sirf education. Koi strategy hamesha nahi jeetti. Risk
management (stop-loss, position size) har strategy se ZYADA zaroori hai.
"""

import pandas as pd


def _turtle_breakout(df: pd.DataFrame) -> dict:
    """Richard Dennis — 20-candle high/low breakout (trend following)."""
    if len(df) < 21:
        return {}
    close = float(df["Close"].iloc[-1])
    hh = float(df["High"].iloc[-21:-1].max())   # pichli 20 candle ka high
    ll = float(df["Low"].iloc[-21:-1].min())
    if close > hh:
        sig, note = "BUY", "Price ne 20-candle high tod diya — naya uptrend shuru ho sakta hai."
    elif close < ll:
        sig, note = "SELL", "Price ne 20-candle low tod diya — naya downtrend shuru ho sakta hai."
    else:
        sig, note = "HOLD", "Price abhi range ke andar — breakout ka intezaar."
    return {"name": "Turtle Breakout", "source": "Richard Dennis (Turtle Traders)",
            "signal": sig, "note": note}


def _ma_cross(df: pd.DataFrame) -> dict:
    """John Murphy — Golden/Death cross (SMA20 vs SMA50)."""
    s20, s50 = df.get("SMA20"), df.get("SMA50")
    if s20 is None or s50 is None or s20.isna().iloc[-1] or s50.isna().iloc[-1]:
        return {}
    if s20.iloc[-1] > s50.iloc[-1]:
        sig = "BUY"
        note = "Short average long se upar (Golden Cross zone) — trend upar."
    else:
        sig = "SELL"
        note = "Short average long se neeche (Death Cross zone) — trend neeche."
    return {"name": "Moving Average Cross", "source": "John Murphy (Trend Following)",
            "signal": sig, "note": note}


def _rsi_reversal(df: pd.DataFrame) -> dict:
    """Welles Wilder — RSI oversold/overbought reversal."""
    rsi = df.get("RSI")
    if rsi is None or rsi.isna().iloc[-1]:
        return {}
    r = float(rsi.iloc[-1])
    if r < 30:
        sig, note = "BUY", f"RSI {r:.0f} — oversold, bounce (upar) ka imkaan."
    elif r > 70:
        sig, note = "SELL", f"RSI {r:.0f} — overbought, pullback (neeche) ka imkaan."
    else:
        sig, note = "HOLD", f"RSI {r:.0f} — neutral zone, saaf signal nahi."
    return {"name": "RSI Reversal", "source": "J. Welles Wilder (RSI)",
            "signal": sig, "note": note}


def _macd_momentum(df: pd.DataFrame) -> dict:
    """Gerald Appel — MACD vs signal line."""
    m, s = df.get("MACD"), df.get("MACD_SIGNAL")
    if m is None or s is None or m.isna().iloc[-1] or s.isna().iloc[-1]:
        return {}
    if m.iloc[-1] > s.iloc[-1]:
        sig, note = "BUY", "MACD signal line se upar — bullish momentum."
    else:
        sig, note = "SELL", "MACD signal line se neeche — bearish momentum."
    return {"name": "MACD Momentum", "source": "Gerald Appel (MACD)",
            "signal": sig, "note": note}


def _bollinger_bounce(df: pd.DataFrame) -> dict:
    """John Bollinger — band bounce."""
    up, low = df.get("BB_UPPER"), df.get("BB_LOWER")
    if up is None or low is None or up.isna().iloc[-1] or low.isna().iloc[-1]:
        return {}
    close = float(df["Close"].iloc[-1])
    if close <= float(low.iloc[-1]):
        sig, note = "BUY", "Price lower band ko chhoo raha — bounce ka imkaan."
    elif close >= float(up.iloc[-1]):
        sig, note = "SELL", "Price upper band ko chhoo raha — pullback ka imkaan."
    else:
        sig, note = "HOLD", "Price bands ke beech — koi extreme nahi."
    return {"name": "Bollinger Bounce", "source": "John Bollinger",
            "signal": sig, "note": note}


def _ema_trend_pullback(df: pd.DataFrame) -> dict:
    """Common pro setup — EMA9/EMA21 trend + pullback entry."""
    e9, e21 = df.get("EMA9"), df.get("EMA21")
    if e9 is None or e21 is None or e9.isna().iloc[-1] or e21.isna().iloc[-1]:
        return {}
    close = float(df["Close"].iloc[-1])
    e9v, e21v = float(e9.iloc[-1]), float(e21.iloc[-1])
    if e9v > e21v:
        sig = "BUY"
        note = "Uptrend (EMA9 > EMA21). Best entry: price EMA21 tak wapas aaye to."
    else:
        sig = "SELL"
        note = "Downtrend (EMA9 < EMA21). Best entry: price EMA21 tak uchhle to."
    return {"name": "EMA Trend + Pullback", "source": "Professional trend setup",
            "signal": sig, "note": note}


def run_all_strategies(df: pd.DataFrame) -> dict:
    """
    Saari strategies chala kar unke signals aur confluence (kitni agree karti hain)
    return karta hai.
    """
    fns = [_turtle_breakout, _ma_cross, _rsi_reversal,
           _macd_momentum, _bollinger_bounce, _ema_trend_pullback]
    results = [r for r in (fn(df) for fn in fns) if r]

    buys = sum(1 for r in results if r["signal"] == "BUY")
    sells = sum(1 for r in results if r["signal"] == "SELL")
    holds = sum(1 for r in results if r["signal"] == "HOLD")
    total = len(results)

    if buys > sells and buys >= max(2, total // 2):
        consensus = "BUY"
    elif sells > buys and sells >= max(2, total // 2):
        consensus = "SELL"
    else:
        consensus = "MIXED"

    return {"results": results, "buys": buys, "sells": sells,
            "holds": holds, "total": total, "consensus": consensus}
