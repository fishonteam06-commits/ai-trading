"""
patterns.py
------------
Candlestick patterns auto-detect karta hai — yeh wahi cheez hai jo
TradingView jaisi apps dikhati hain (Doji, Hammer, Engulfing, etc.).

Har pattern ke saath uska matlab (bullish/bearish/neutral) aur ek chhoti
Roman-Urdu tashreeh hoti hai. Yeh sab pichli 2-3 candles ke shape se
nikaalte hain — koi library nahi, sirf simple math.
"""

import pandas as pd


def _body(o, c):
    return abs(c - o)


def _range(h, l):
    return (h - l) if (h - l) != 0 else 1e-9


def detect_patterns(df: pd.DataFrame) -> list[dict]:
    """
    Aakhri candle (aur usse pehle wali) mein maujood patterns dhoondta hai.
    Return: list of dicts {name, bias, note}
    bias: 'bullish' (upar), 'bearish' (neeche), 'neutral'
    """
    if len(df) < 3:
        return []

    found = []
    o, h, l, c = df["Open"], df["High"], df["Low"], df["Close"]

    # aakhri 3 candles
    o1, h1, l1, c1 = o.iloc[-1], h.iloc[-1], l.iloc[-1], c.iloc[-1]   # abhi wali
    o2, h2, l2, c2 = o.iloc[-2], h.iloc[-2], l.iloc[-2], c.iloc[-2]   # pichli
    o3, c3 = o.iloc[-3], c.iloc[-3]                                    # us se pichli

    body1 = _body(o1, c1)
    rng1 = _range(h1, l1)
    upper_wick = h1 - max(o1, c1)
    lower_wick = min(o1, c1) - l1

    # ---- DOJI: open ~ close (bohat chhota body) => aksani, palat sakta hai ----
    if body1 <= 0.1 * rng1:
        found.append({
            "name": "Doji",
            "bias": "neutral",
            "note": "Buyers/sellers barabar — trend ruk raha hai, palat sakta hai.",
        })

    # ---- HAMMER: chhota body upar, lamba lower wick => bullish reversal ----
    if lower_wick >= 2 * body1 and upper_wick <= body1 and body1 > 0:
        found.append({
            "name": "Hammer",
            "bias": "bullish",
            "note": "Neeche se buyers ne wapas dhakela — girawat ruk sakti hai.",
        })

    # ---- SHOOTING STAR: chhota body neeche, lamba upper wick => bearish ----
    if upper_wick >= 2 * body1 and lower_wick <= body1 and body1 > 0:
        found.append({
            "name": "Shooting Star",
            "bias": "bearish",
            "note": "Upar se sellers ne wapas dhakela — tezi ruk sakti hai.",
        })

    # ---- BULLISH ENGULFING: red candle ko badi green candle nigal le ----
    if c2 < o2 and c1 > o1 and c1 >= o2 and o1 <= c2:
        found.append({
            "name": "Bullish Engulfing",
            "bias": "bullish",
            "note": "Badi green candle ne pichli red ko nigal liya — buyers strong.",
        })

    # ---- BEARISH ENGULFING: green candle ko badi red candle nigal le ----
    if c2 > o2 and c1 < o1 and o1 >= c2 and c1 <= o2:
        found.append({
            "name": "Bearish Engulfing",
            "bias": "bearish",
            "note": "Badi red candle ne pichli green ko nigal liya — sellers strong.",
        })

    # ---- MORNING STAR (3 candles): red -> chhota -> green => bullish reversal ----
    small_mid = _body(o2, c2) <= 0.5 * _body(o3, c3)
    if c3 < o3 and small_mid and c1 > o1 and c1 > (o3 + c3) / 2:
        found.append({
            "name": "Morning Star",
            "bias": "bullish",
            "note": "3-candle bottom reversal — girawat ke baad tezi ka ishaara.",
        })

    # ---- EVENING STAR (3 candles): green -> chhota -> red => bearish reversal ----
    if c3 > o3 and small_mid and c1 < o1 and c1 < (o3 + c3) / 2:
        found.append({
            "name": "Evening Star",
            "bias": "bearish",
            "note": "3-candle top reversal — tezi ke baad girawat ka ishaara.",
        })

    return found


def bias_summary(patterns: list[dict]) -> str:
    """Patterns ka overall jhukaao ek line mein."""
    if not patterns:
        return "Koi khaas candlestick pattern nahi mila."
    bulls = sum(1 for p in patterns if p["bias"] == "bullish")
    bears = sum(1 for p in patterns if p["bias"] == "bearish")
    if bulls > bears:
        return "🟢 Candlestick patterns bullish (upar) ka ishaara de rahe hain."
    if bears > bulls:
        return "🔴 Candlestick patterns bearish (neeche) ka ishaara de rahe hain."
    return "🟡 Candlestick patterns mila-jula (neutral) ishaara de rahe hain."
