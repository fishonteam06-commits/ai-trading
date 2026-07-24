"""
signals.py
-----------
Builds a simple, rule-based signal from the indicators:
BUY / SELL / HOLD  +  a "confidence score".

** IMPORTANT **: This is NOT financial advice. It is only an educational
technical-analysis tool. The reason behind each signal is written alongside it
so you can understand it and decide for yourself.
"""

import pandas as pd


def multi_timeframe_signal(market: str, symbol: str,
                           timeframes: list[str] | None = None) -> dict:
    """
    Checks a single symbol across several timeframes (e.g. 15m, 1h, 4h, 1d).
    When more timeframes point the same way, the signal is more reliable.

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
    Builds a signal from the indicators of the latest candle.
    Return: dict containing action, score, and reasons.
    """
    last = df.iloc[-1]
    reasons = []
    bullish = 0   # points for an upward move
    bearish = 0   # points for a downward move

    close = float(last["Close"])

    # --- 1. RSI ---
    rsi_val = last.get("RSI")
    if pd.notna(rsi_val):
        if rsi_val < 30:
            bullish += 2
            reasons.append(f"RSI {rsi_val:.0f} — oversold, potential to rise.")
        elif rsi_val > 70:
            bearish += 2
            reasons.append(f"RSI {rsi_val:.0f} — overbought, potential to fall.")
        else:
            reasons.append(f"RSI {rsi_val:.0f} — normal range (neutral).")

    # --- 2. Moving Average trend (SMA20 vs SMA50) ---
    sma20, sma50 = last.get("SMA20"), last.get("SMA50")
    if pd.notna(sma20) and pd.notna(sma50):
        if sma20 > sma50:
            bullish += 1
            reasons.append("Short-term average above long-term — uptrend.")
        else:
            bearish += 1
            reasons.append("Short-term average below long-term — downtrend.")

    # --- 3. Price vs SMA20 ---
    if pd.notna(sma20):
        if close > sma20:
            bullish += 1
            reasons.append("Price above the 20-average — upward momentum.")
        else:
            bearish += 1
            reasons.append("Price below the 20-average — downward momentum.")

    # --- 4. MACD ---
    macd_val, macd_sig = last.get("MACD"), last.get("MACD_SIGNAL")
    if pd.notna(macd_val) and pd.notna(macd_sig):
        if macd_val > macd_sig:
            bullish += 1
            reasons.append("MACD above the signal line — bullish momentum.")
        else:
            bearish += 1
            reasons.append("MACD below the signal line — bearish momentum.")

    # --- 5. Bollinger Bands ---
    bb_up, bb_low = last.get("BB_UPPER"), last.get("BB_LOWER")
    if pd.notna(bb_up) and pd.notna(bb_low):
        if close <= bb_low:
            bullish += 1
            reasons.append("Price touching the lower band — bounce potential.")
        elif close >= bb_up:
            bearish += 1
            reasons.append("Price touching the upper band — pullback potential.")

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
        "score": score,           # 0-100, how strong the signal is
        "bullish_points": bullish,
        "bearish_points": bearish,
        "price": close,
        "reasons": reasons,
    }
