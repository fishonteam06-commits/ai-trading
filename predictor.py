"""
predictor.py
-------------
Predicts the direction of the "next candle" (the one currently forming):
UP (BUY) or DOWN (SELL) — together with a confidence %.

It combines several forward-looking factors into a single probability:
  - Trend (EMA9 vs EMA21 and their slope)
  - Momentum (returns of the most recent candles)
  - MACD histogram rising or falling
  - RSI level + direction (reversal potential at overbought/oversold)
  - Candle body streak (consecutive green/red)
  - Stochastic (%K vs %D)
  - Volume confirmation

** IMPORTANT **: This is NOT a 100% guarantee. The market can reverse at any
time. This is only an EDUCATIONAL probability estimate — do not risk all your
capital on it. Always use a stop-loss.
"""

import pandas as pd


def prediction_accuracy(df: pd.DataFrame, lookback: int = 120) -> dict:
    """
    Honest backtest: for each recent candle, run the predictor on the data up to
    that point and check whether the NEXT candle actually moved that way.
    Returns {hits, total, accuracy%}. Indicators are causal, so there's no look-ahead.
    """
    n = len(df)
    if n < 70:
        return {"hits": 0, "total": 0, "accuracy": 0}
    start = max(60, n - lookback)
    hits = 0
    total = 0
    closes = df["Close"].values
    for i in range(start, n - 1):
        p = predict_next_candle(df.iloc[: i + 1])
        if p["direction"] == "NEUTRAL":
            continue
        actual_up = closes[i + 1] > closes[i]
        pred_up = p["direction"] == "BUY"
        if pred_up == actual_up:
            hits += 1
        total += 1
    return {"hits": hits, "total": total,
            "accuracy": round(hits / total * 100, 1) if total else 0}


def predict_next_candle(df: pd.DataFrame) -> dict:
    """
    Estimates the direction of the next candle from the most recent candles.
    Return: {direction, confidence, prob_up, prob_down, reasons}
      direction : 'BUY' (up), 'SELL' (down), or 'NEUTRAL'
      confidence: 0-100 (how strong the lean is)
    """
    if len(df) < 5:
        return {"direction": "NEUTRAL", "confidence": 0, "prob_up": 50,
                "prob_down": 50, "reasons": ["Not enough data."]}

    last = df.iloc[-1]
    up = 0.0
    down = 0.0
    reasons = []

    close = df["Close"]

    # --- 1. EMA trend (EMA9 vs EMA21) ---
    ema9, ema21 = last.get("EMA9"), last.get("EMA21")
    if pd.notna(ema9) and pd.notna(ema21):
        if ema9 > ema21:
            up += 1.5
            reasons.append("🟢 Short-term trend is up (EMA9 > EMA21).")
        else:
            down += 1.5
            reasons.append("🔴 Short-term trend is down (EMA9 < EMA21).")

        # EMA9 slope — compared with 3 candles ago
        if len(df) >= 4 and "EMA9" in df:
            ema9_prev = df["EMA9"].iloc[-4]
            if pd.notna(ema9_prev):
                if ema9 > ema9_prev:
                    up += 1
                    reasons.append("🟢 EMA9 is turning up (momentum building).")
                else:
                    down += 1
                    reasons.append("🔴 EMA9 is turning down (momentum fading).")

    # --- 2. Recent momentum (return of the last 3 candles) ---
    rets = close.pct_change().tail(3)
    mom = float(rets.sum())
    if mom > 0:
        up += 1
        reasons.append(f"🟢 Last 3 candles are trending up ({mom*100:+.2f}%).")
    elif mom < 0:
        down += 1
        reasons.append(f"🔴 Last 3 candles are trending down ({mom*100:+.2f}%).")

    # --- 3. MACD histogram rising or falling ---
    if "MACD_HIST" in df and len(df) >= 2:
        h_now, h_prev = df["MACD_HIST"].iloc[-1], df["MACD_HIST"].iloc[-2]
        if pd.notna(h_now) and pd.notna(h_prev):
            if h_now > h_prev:
                up += 1
                reasons.append("🟢 MACD momentum is rising.")
            else:
                down += 1
                reasons.append("🔴 MACD momentum is fading.")

    # --- 4. RSI level + direction ---
    rsi_now = last.get("RSI")
    if pd.notna(rsi_now) and len(df) >= 2:
        rsi_prev = df["RSI"].iloc[-2]
        if rsi_now > 70:
            down += 1.5
            reasons.append(f"🔴 RSI {rsi_now:.0f} — overbought, pullback (down) likely.")
        elif rsi_now < 30:
            up += 1.5
            reasons.append(f"🟢 RSI {rsi_now:.0f} — oversold, bounce (up) likely.")
        elif pd.notna(rsi_prev):
            if rsi_now > rsi_prev:
                up += 0.5
                reasons.append("🟢 RSI is rising (buyers active).")
            else:
                down += 0.5
                reasons.append("🔴 RSI is falling (sellers active).")

    # --- 5. Candle body streak (consecutive green/red) ---
    bodies = (df["Close"] - df["Open"]).tail(3)
    greens = int((bodies > 0).sum())
    reds = int((bodies < 0).sum())
    if greens == 3:
        up += 0.8
        reasons.append("🟢 Last 3 candles green — buyers in control.")
    elif reds == 3:
        down += 0.8
        reasons.append("🔴 Last 3 candles red — sellers in control.")

    # --- 6. Stochastic (%K vs %D) ---
    k, d = last.get("STOCH_K"), last.get("STOCH_D")
    if pd.notna(k) and pd.notna(d):
        if k > d:
            up += 0.7
            reasons.append("🟢 Stochastic %K above %D — short-term upward pressure.")
        else:
            down += 0.7
            reasons.append("🔴 Stochastic %K below %D — short-term downward pressure.")

    # --- 7. Volume confirmation (is the last candle's volume above average?) ---
    if "Volume" in df and len(df) >= 20:
        vol_now = float(df["Volume"].iloc[-1])
        vol_avg = float(df["Volume"].tail(20).mean())
        last_body = float(df["Close"].iloc[-1] - df["Open"].iloc[-1])
        if vol_now > vol_avg * 1.2 and last_body != 0:
            if last_body > 0:
                up += 0.6
                reasons.append("🟢 Green candle on above-average volume — strong buying.")
            else:
                down += 0.6
                reasons.append("🔴 Red candle on above-average volume — strong selling.")

    # --- Final probability ---
    total = up + down
    if total == 0:
        return {"direction": "NEUTRAL", "confidence": 0, "prob_up": 50,
                "prob_down": 50, "reasons": reasons or ["No clear trend."]}

    # Clamp between 5-95% — never 0%/100% (nothing is certain).
    prob_up = round(up / total * 100)
    prob_up = max(5, min(95, prob_up))
    prob_down = 100 - prob_up

    # Only call a direction on stronger conviction (>=62/<=38); otherwise NEUTRAL.
    # Being selective means fewer, higher-quality calls instead of coin-flip guesses.
    if prob_up >= 62:
        direction = "BUY"
    elif prob_up <= 38:
        direction = "SELL"
    else:
        direction = "NEUTRAL"

    confidence = max(prob_up, prob_down)

    return {
        "direction": direction,     # BUY / SELL / NEUTRAL
        "confidence": confidence,   # 0-100
        "prob_up": prob_up,
        "prob_down": prob_down,
        "reasons": reasons,
    }
