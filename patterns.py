"""
patterns.py
------------
Auto-detects candlestick patterns — the same thing apps like TradingView
show (Doji, Hammer, Engulfing, etc.).

Each pattern comes with its meaning (bullish/bearish/neutral) and a short
plain-English explanation. These are all derived from the shape of the last
2-3 candles — no library, just simple math.
"""

import pandas as pd


def _body(o, c):
    return abs(c - o)


def _range(h, l):
    return (h - l) if (h - l) != 0 else 1e-9


def detect_patterns(df: pd.DataFrame) -> list[dict]:
    """
    Finds patterns present in the last candle (and the one before it).
    Return: list of dicts {name, bias, note}
    bias: 'bullish' (up), 'bearish' (down), 'neutral'
    """
    if len(df) < 3:
        return []

    found = []
    o, h, l, c = df["Open"], df["High"], df["Low"], df["Close"]

    # last 3 candles
    o1, h1, l1, c1 = o.iloc[-1], h.iloc[-1], l.iloc[-1], c.iloc[-1]   # current
    o2, h2, l2, c2 = o.iloc[-2], h.iloc[-2], l.iloc[-2], c.iloc[-2]   # previous
    o3, c3 = o.iloc[-3], c.iloc[-3]                                    # the one before that

    body1 = _body(o1, c1)
    rng1 = _range(h1, l1)
    upper_wick = h1 - max(o1, c1)
    lower_wick = min(o1, c1) - l1

    # ---- DOJI: open ~ close (very small body) => indecision, may reverse ----
    if body1 <= 0.1 * rng1:
        found.append({
            "name": "Doji",
            "bias": "neutral",
            "note": "Buyers and sellers balanced — the trend is stalling and may reverse.",
        })

    # ---- HAMMER: small body on top, long lower wick => bullish reversal ----
    if lower_wick >= 2 * body1 and upper_wick <= body1 and body1 > 0:
        found.append({
            "name": "Hammer",
            "bias": "bullish",
            "note": "Buyers pushed price back up from the lows — the decline may be stalling.",
        })

    # ---- SHOOTING STAR: small body at bottom, long upper wick => bearish ----
    if upper_wick >= 2 * body1 and lower_wick <= body1 and body1 > 0:
        found.append({
            "name": "Shooting Star",
            "bias": "bearish",
            "note": "Sellers pushed price back down from the highs — the rally may be stalling.",
        })

    # ---- BULLISH ENGULFING: a big green candle engulfs the red one ----
    if c2 < o2 and c1 > o1 and c1 >= o2 and o1 <= c2:
        found.append({
            "name": "Bullish Engulfing",
            "bias": "bullish",
            "note": "A large green candle engulfed the previous red one — buyers are strong.",
        })

    # ---- BEARISH ENGULFING: a big red candle engulfs the green one ----
    if c2 > o2 and c1 < o1 and o1 >= c2 and c1 <= o2:
        found.append({
            "name": "Bearish Engulfing",
            "bias": "bearish",
            "note": "A large red candle engulfed the previous green one — sellers are strong.",
        })

    # ---- MORNING STAR (3 candles): red -> small -> green => bullish reversal ----
    small_mid = _body(o2, c2) <= 0.5 * _body(o3, c3)
    if c3 < o3 and small_mid and c1 > o1 and c1 > (o3 + c3) / 2:
        found.append({
            "name": "Morning Star",
            "bias": "bullish",
            "note": "3-candle bottom reversal — signals a rally after a decline.",
        })

    # ---- EVENING STAR (3 candles): green -> small -> red => bearish reversal ----
    if c3 > o3 and small_mid and c1 < o1 and c1 < (o3 + c3) / 2:
        found.append({
            "name": "Evening Star",
            "bias": "bearish",
            "note": "3-candle top reversal — signals a decline after a rally.",
        })

    return found


def bias_summary(patterns: list[dict]) -> str:
    """The overall bias of the patterns in one line."""
    if not patterns:
        return "No notable candlestick pattern found."
    bulls = sum(1 for p in patterns if p["bias"] == "bullish")
    bears = sum(1 for p in patterns if p["bias"] == "bearish")
    if bulls > bears:
        return "🟢 Candlestick patterns are pointing bullish (up)."
    if bears > bulls:
        return "🔴 Candlestick patterns are pointing bearish (down)."
    return "🟡 Candlestick patterns are giving a mixed (neutral) signal."
