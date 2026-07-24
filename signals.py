"""
signals.py
-----------
Yeh indicators dekhkar ek simple, rule-based signal banata hai:
BUY / SELL / HOLD  +  ek "confidence score".

** ZAROORI **: Yeh financial advice NAHI hai. Yeh sirf ek educational
technical-analysis tool hai. Har signal ki wajah bhi saath likhi hoti hai
taake aap khud samajh kar faisla karein.
"""

import pandas as pd


def multi_timeframe_signal(market: str, symbol: str,
                           timeframes: list[str] | None = None) -> dict:
    """
    Ek hi symbol ko kai timeframes (jaise 15m, 1h, 4h, 1d) par check karta hai.
    Jab zyada timeframes ek hi taraf ishaara karein to signal zyada bharosemand.

    Return: {per_tf: {tf: action}, consensus: 'BUY'/'SELL'/'MIXED', agree: int, total: int}
    """
    from data_sources import get_data
    from indicators import add_all_indicators

    timeframes = timeframes or ["15m", "1h", "4h", "1d"]
    per_tf = {}
    for tf in timeframes:
        try:
            df = add_all_indicators(get_data(market, symbol, tf, limit=200))
            per_tf[tf] = generate_signal(df)["action"]
        except Exception:
            per_tf[tf] = "N/A"

    votes = [a for a in per_tf.values() if a in ("BUY", "SELL", "HOLD")]
    buys = votes.count("BUY")
    sells = votes.count("SELL")
    if buys > sells and buys >= 2:
        consensus, agree = "BUY", buys
    elif sells > buys and sells >= 2:
        consensus, agree = "SELL", sells
    else:
        consensus, agree = "MIXED", max(buys, sells)

    return {"per_tf": per_tf, "consensus": consensus,
            "agree": agree, "total": len(votes)}


def generate_signal(df: pd.DataFrame) -> dict:
    """
    Aakhri (latest) candle ke indicators dekhkar signal banata hai.
    Return: dict jismein action, score, aur reasons (wajah) hoti hain.
    """
    last = df.iloc[-1]
    reasons = []
    bullish = 0   # upar jaane ke points
    bearish = 0   # neeche jaane ke points

    close = float(last["Close"])

    # --- 1. RSI ---
    rsi_val = last.get("RSI")
    if pd.notna(rsi_val):
        if rsi_val < 30:
            bullish += 2
            reasons.append(f"RSI {rsi_val:.0f} — oversold (sasta), barhne ka chance.")
        elif rsi_val > 70:
            bearish += 2
            reasons.append(f"RSI {rsi_val:.0f} — overbought (mehnga), girne ka chance.")
        else:
            reasons.append(f"RSI {rsi_val:.0f} — normal range (neutral).")

    # --- 2. Moving Average trend (SMA20 vs SMA50) ---
    sma20, sma50 = last.get("SMA20"), last.get("SMA50")
    if pd.notna(sma20) and pd.notna(sma50):
        if sma20 > sma50:
            bullish += 1
            reasons.append("Short-term average long-term se upar — uptrend.")
        else:
            bearish += 1
            reasons.append("Short-term average long-term se neeche — downtrend.")

    # --- 3. Price vs SMA20 ---
    if pd.notna(sma20):
        if close > sma20:
            bullish += 1
            reasons.append("Price 20-average se upar — momentum upar.")
        else:
            bearish += 1
            reasons.append("Price 20-average se neeche — momentum neeche.")

    # --- 4. MACD ---
    macd_val, macd_sig = last.get("MACD"), last.get("MACD_SIGNAL")
    if pd.notna(macd_val) and pd.notna(macd_sig):
        if macd_val > macd_sig:
            bullish += 1
            reasons.append("MACD signal line se upar — bullish momentum.")
        else:
            bearish += 1
            reasons.append("MACD signal line se neeche — bearish momentum.")

    # --- 5. Bollinger Bands ---
    bb_up, bb_low = last.get("BB_UPPER"), last.get("BB_LOWER")
    if pd.notna(bb_up) and pd.notna(bb_low):
        if close <= bb_low:
            bullish += 1
            reasons.append("Price lower band ko chhoo raha — bounce ka chance.")
        elif close >= bb_up:
            bearish += 1
            reasons.append("Price upper band ko chhoo raha — pullback ka chance.")

    # --- Final decision ---
    total = bullish + bearish
    score = 0 if total == 0 else round(abs(bullish - bearish) / total * 100)

    if bullish > bearish + 1:
        action = "BUY"
    elif bearish > bullish + 1:
        action = "SELL"
    else:
        action = "HOLD"

    return {
        "action": action,
        "score": score,           # 0-100, kitna strong signal hai
        "bullish_points": bullish,
        "bearish_points": bearish,
        "price": close,
        "reasons": reasons,
    }
