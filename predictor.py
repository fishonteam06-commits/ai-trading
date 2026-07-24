"""
predictor.py
-------------
"Agli candle" (jo abhi ban rahi hai) ka rukh predict karta hai:
UP (BUY / upar) ya DOWN (SELL / neeche) — ek confidence % ke saath.

Yeh kai forward-looking cheezein mila kar ek probability nikalta hai:
  - Trend (EMA9 vs EMA21 aur unki dhalaan/slope)
  - Momentum (pichli candles ke returns)
  - MACD histogram barh raha ya ghat raha
  - RSI level + direction (overbought/oversold pe reversal ka imkaan)
  - Candle body streak (lagataar green/red)
  - Stochastic (%K vs %D)
  - Volume confirmation

** BOHAT ZAROORI **: Yeh 100% pesh-goi (guarantee) NAHI hai. Market kabhi bhi
palat sakta hai. Yeh sirf ek EDUCATIONAL probability estimate hai — is par
apna poora paisa mat lagayein. Hamesha stop-loss use karein.
"""

import pandas as pd


def predict_next_candle(df: pd.DataFrame) -> dict:
    """
    Aakhri candles ka hisab lagakar agli candle ka rukh estimate karta hai.
    Return: {direction, confidence, prob_up, prob_down, reasons}
      direction : 'BUY' (upar), 'SELL' (neeche), ya 'NEUTRAL'
      confidence: 0-100 (kitna strong lean hai)
    """
    if len(df) < 5:
        return {"direction": "NEUTRAL", "confidence": 0, "prob_up": 50,
                "prob_down": 50, "reasons": ["Kaafi data nahi."]}

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
            reasons.append("🟢 Short-term trend upar (EMA9 > EMA21).")
        else:
            down += 1.5
            reasons.append("🔴 Short-term trend neeche (EMA9 < EMA21).")

        # EMA9 ki dhalaan (slope) — pichli 3 candle se compare
        if len(df) >= 4 and "EMA9" in df:
            ema9_prev = df["EMA9"].iloc[-4]
            if pd.notna(ema9_prev):
                if ema9 > ema9_prev:
                    up += 1
                    reasons.append("🟢 EMA9 upar ki taraf mud raha (momentum barh raha).")
                else:
                    down += 1
                    reasons.append("🔴 EMA9 neeche ki taraf mud raha (momentum ghat raha).")

    # --- 2. Recent momentum (pichli 3 candles ka return) ---
    rets = close.pct_change().tail(3)
    mom = float(rets.sum())
    if mom > 0:
        up += 1
        reasons.append(f"🟢 Pichli 3 candles ka rujhan upar ({mom*100:+.2f}%).")
    elif mom < 0:
        down += 1
        reasons.append(f"🔴 Pichli 3 candles ka rujhan neeche ({mom*100:+.2f}%).")

    # --- 3. MACD histogram barh raha ya ghat raha ---
    if "MACD_HIST" in df and len(df) >= 2:
        h_now, h_prev = df["MACD_HIST"].iloc[-1], df["MACD_HIST"].iloc[-2]
        if pd.notna(h_now) and pd.notna(h_prev):
            if h_now > h_prev:
                up += 1
                reasons.append("🟢 MACD momentum barh raha hai.")
            else:
                down += 1
                reasons.append("🔴 MACD momentum ghat raha hai.")

    # --- 4. RSI level + direction ---
    rsi_now = last.get("RSI")
    if pd.notna(rsi_now) and len(df) >= 2:
        rsi_prev = df["RSI"].iloc[-2]
        if rsi_now > 70:
            down += 1.5
            reasons.append(f"🔴 RSI {rsi_now:.0f} — overbought, pullback (neeche) ka imkaan.")
        elif rsi_now < 30:
            up += 1.5
            reasons.append(f"🟢 RSI {rsi_now:.0f} — oversold, bounce (upar) ka imkaan.")
        elif pd.notna(rsi_prev):
            if rsi_now > rsi_prev:
                up += 0.5
                reasons.append("🟢 RSI upar ja raha (buyers active).")
            else:
                down += 0.5
                reasons.append("🔴 RSI neeche ja raha (sellers active).")

    # --- 5. Candle body streak (lagataar green/red) ---
    bodies = (df["Close"] - df["Open"]).tail(3)
    greens = int((bodies > 0).sum())
    reds = int((bodies < 0).sum())
    if greens == 3:
        up += 0.8
        reasons.append("🟢 Pichli 3 candles green — buyers ka control.")
    elif reds == 3:
        down += 0.8
        reasons.append("🔴 Pichli 3 candles red — sellers ka control.")

    # --- 6. Stochastic (%K vs %D) ---
    k, d = last.get("STOCH_K"), last.get("STOCH_D")
    if pd.notna(k) and pd.notna(d):
        if k > d:
            up += 0.7
            reasons.append("🟢 Stochastic %K upar — short-term upar ka dabaao.")
        else:
            down += 0.7
            reasons.append("🔴 Stochastic %K neeche — short-term neeche ka dabaao.")

    # --- 7. Volume confirmation (aakhri candle ka volume average se zyada?) ---
    if "Volume" in df and len(df) >= 20:
        vol_now = float(df["Volume"].iloc[-1])
        vol_avg = float(df["Volume"].tail(20).mean())
        last_body = float(df["Close"].iloc[-1] - df["Open"].iloc[-1])
        if vol_now > vol_avg * 1.2 and last_body != 0:
            if last_body > 0:
                up += 0.6
                reasons.append("🟢 Zyada volume ke saath green candle — strong buying.")
            else:
                down += 0.6
                reasons.append("🔴 Zyada volume ke saath red candle — strong selling.")

    # --- Final probability ---
    total = up + down
    if total == 0:
        return {"direction": "NEUTRAL", "confidence": 0, "prob_up": 50,
                "prob_down": 50, "reasons": reasons or ["Saaf rujhan nahi."]}

    # 5-95% ke darmiyan clamp — kabhi 0%/100% nahi (koi cheez yaqeeni nahi).
    prob_up = round(up / total * 100)
    prob_up = max(5, min(95, prob_up))
    prob_down = 100 - prob_up

    if prob_up >= 58:
        direction = "BUY"
    elif prob_up <= 42:
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
