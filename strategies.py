"""
strategies.py
--------------
PROVEN strategies from world-famous traders and trading books — each one
produces its signal from the current data, along with its source (which
trader/book it comes from).

When several different strategies point the same way (confluence), the signal
is more reliable — this is how professional traders work.

Sources (core principles only, no copyrighted text — mechanics + attribution):
  - Turtle Trading / Donchian Breakout ...... Richard Dennis (1983)
  - Moving Average Cross (trend) ............. John Murphy (Technical Analysis)
  - RSI Reversal ............................. J. Welles Wilder (RSI inventor)
  - MACD Momentum ............................ Gerald Appel (MACD inventor)
  - Bollinger Bands Bounce ................... John Bollinger
  - EMA Trend + Pullback ..................... common professional setup

** DISCLAIMER **: For education only. No strategy wins every time. Risk
management (stop-loss, position size) matters MORE than any strategy.
"""

import pandas as pd


def _turtle_breakout(df: pd.DataFrame) -> dict:
    """Richard Dennis — 20-candle high/low breakout (trend following)."""
    if len(df) < 21:
        return {}
    close = float(df["Close"].iloc[-1])
    hh = float(df["High"].iloc[-21:-1].max())   # high of the last 20 candles
    ll = float(df["Low"].iloc[-21:-1].min())
    if close > hh:
        sig, note = "BUY", "Price broke above the 20-candle high — a new uptrend may be starting."
    elif close < ll:
        sig, note = "SELL", "Price broke below the 20-candle low — a new downtrend may be starting."
    else:
        sig, note = "HOLD", "Price is still within the range — waiting for a breakout."
    return {"name": "Turtle Breakout", "source": "Richard Dennis (Turtle Traders)",
            "signal": sig, "note": note}


def _ma_cross(df: pd.DataFrame) -> dict:
    """John Murphy — Golden/Death cross (SMA20 vs SMA50)."""
    s20, s50 = df.get("SMA20"), df.get("SMA50")
    if s20 is None or s50 is None or s20.isna().iloc[-1] or s50.isna().iloc[-1]:
        return {}
    if s20.iloc[-1] > s50.iloc[-1]:
        sig = "BUY"
        note = "Short average above the long average (Golden Cross zone) — trend is up."
    else:
        sig = "SELL"
        note = "Short average below the long average (Death Cross zone) — trend is down."
    return {"name": "Moving Average Cross", "source": "John Murphy (Trend Following)",
            "signal": sig, "note": note}


def _rsi_reversal(df: pd.DataFrame) -> dict:
    """Welles Wilder — RSI oversold/overbought reversal."""
    rsi = df.get("RSI")
    if rsi is None or rsi.isna().iloc[-1]:
        return {}
    r = float(rsi.iloc[-1])
    if r < 30:
        sig, note = "BUY", f"RSI {r:.0f} — oversold, bounce (up) likely."
    elif r > 70:
        sig, note = "SELL", f"RSI {r:.0f} — overbought, pullback (down) likely."
    else:
        sig, note = "HOLD", f"RSI {r:.0f} — neutral zone, no clear signal."
    return {"name": "RSI Reversal", "source": "J. Welles Wilder (RSI)",
            "signal": sig, "note": note}


def _macd_momentum(df: pd.DataFrame) -> dict:
    """Gerald Appel — MACD vs signal line."""
    m, s = df.get("MACD"), df.get("MACD_SIGNAL")
    if m is None or s is None or m.isna().iloc[-1] or s.isna().iloc[-1]:
        return {}
    if m.iloc[-1] > s.iloc[-1]:
        sig, note = "BUY", "MACD above the signal line — bullish momentum."
    else:
        sig, note = "SELL", "MACD below the signal line — bearish momentum."
    return {"name": "MACD Momentum", "source": "Gerald Appel (MACD)",
            "signal": sig, "note": note}


def _bollinger_bounce(df: pd.DataFrame) -> dict:
    """John Bollinger — band bounce."""
    up, low = df.get("BB_UPPER"), df.get("BB_LOWER")
    if up is None or low is None or up.isna().iloc[-1] or low.isna().iloc[-1]:
        return {}
    close = float(df["Close"].iloc[-1])
    if close <= float(low.iloc[-1]):
        sig, note = "BUY", "Price is touching the lower band — bounce likely."
    elif close >= float(up.iloc[-1]):
        sig, note = "SELL", "Price is touching the upper band — pullback likely."
    else:
        sig, note = "HOLD", "Price is between the bands — no extreme."
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
        note = "Uptrend (EMA9 > EMA21). Best entry: when price pulls back to EMA21."
    else:
        sig = "SELL"
        note = "Downtrend (EMA9 < EMA21). Best entry: when price rallies up to EMA21."
    return {"name": "EMA Trend + Pullback", "source": "Professional trend setup",
            "signal": sig, "note": note}


def run_all_strategies(df: pd.DataFrame) -> dict:
    """
    Runs all strategies and returns their signals plus the confluence
    (how many of them agree).
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
