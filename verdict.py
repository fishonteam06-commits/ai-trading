"""
verdict.py
-----------
Combines every signal in the app — the rule-based signal, the next-candle
prediction, the multi-strategy confluence, and candlestick patterns — into ONE
clear Overall Verdict with a plain-English recommendation and a strength score.

This is the "just tell me what it says" layer: instead of reading five panels,
the user sees a single BUY / SELL / WAIT call with a confidence bar and a short
breakdown of what drove it.

** DISCLAIMER **: Educational only. Not financial advice. No verdict is a
guarantee — always use a stop-loss and risk only a small % per trade.
"""

from signals import generate_signal
from strategies import run_all_strategies
from predictor import predict_next_candle
from patterns import detect_patterns


def overall_verdict(df) -> dict:
    """
    Aggregate all sub-signals into one weighted verdict.
    Returns: {action, strength, buy_score, sell_score, components, summary}
      action  : 'BUY' | 'SELL' | 'WAIT'
      strength: 0-100 confidence in the direction
    """
    buy = 0.0
    sell = 0.0
    components = []

    # 1) Rule-based technical signal (weight up to ~3)
    sig = generate_signal(df)
    if sig["action"] == "BUY":
        w = 1 + sig["score"] / 50
        buy += w
        components.append(("Technical signal", "BUY", f"{sig['score']}% strength"))
    elif sig["action"] == "SELL":
        w = 1 + sig["score"] / 50
        sell += w
        components.append(("Technical signal", "SELL", f"{sig['score']}% strength"))
    else:
        components.append(("Technical signal", "NEUTRAL", "no clear edge"))

    # 2) Next-candle prediction (weight up to ~2)
    pred = predict_next_candle(df)
    if pred["direction"] == "BUY":
        buy += pred["confidence"] / 50
        components.append(("Next-candle prediction", "BUY", f"{pred['prob_up']}% up"))
    elif pred["direction"] == "SELL":
        sell += pred["confidence"] / 50
        components.append(("Next-candle prediction", "SELL", f"{pred['prob_down']}% down"))
    else:
        components.append(("Next-candle prediction", "NEUTRAL", "no clear lean"))

    # 3) Multi-strategy confluence (weight = number of agreeing strategies)
    strat = run_all_strategies(df)
    if strat["consensus"] == "BUY":
        buy += strat["buys"]
        components.append(("Strategy confluence", "BUY",
                           f"{strat['buys']}/{strat['total']} strategies"))
    elif strat["consensus"] == "SELL":
        sell += strat["sells"]
        components.append(("Strategy confluence", "SELL",
                           f"{strat['sells']}/{strat['total']} strategies"))
    else:
        components.append(("Strategy confluence", "MIXED",
                           f"{strat['buys']} buy / {strat['sells']} sell"))

    # 4) Candlestick patterns (weight up to ~1.5)
    pats = detect_patterns(df)
    bull = sum(1 for p in pats if p["bias"] == "bullish")
    bear = sum(1 for p in pats if p["bias"] == "bearish")
    if bull > bear:
        buy += 1.5
        components.append(("Candlestick patterns", "BUY",
                           ", ".join(p["name"] for p in pats if p["bias"] == "bullish")))
    elif bear > bull:
        sell += 1.5
        components.append(("Candlestick patterns", "SELL",
                           ", ".join(p["name"] for p in pats if p["bias"] == "bearish")))
    else:
        components.append(("Candlestick patterns", "NEUTRAL", "none / mixed"))

    # ---- Combine ----
    # Count how many of the 4 components clearly lean each way (confirmation).
    buy_votes = sum(1 for _, side, _ in components if side == "BUY")
    sell_votes = sum(1 for _, side, _ in components if side == "SELL")

    total = buy + sell
    if total == 0:
        return {"action": "WAIT", "strength": 0, "buy_score": 50, "sell_score": 50,
                "components": components,
                "summary": "No clear edge right now — best to wait for a cleaner setup."}

    # Weighted split, clamped to 5-95% (nothing is ever certain).
    buy_pct = round(buy / total * 100)
    buy_pct = max(5, min(95, buy_pct))
    sell_pct = 100 - buy_pct

    # A directional call needs a clear weighted lean AND at least 2 components
    # confirming the same direction — otherwise it's WAIT.
    if buy_pct >= 60 and buy_votes >= 2 and buy_votes > sell_votes:
        action, strength = "BUY", buy_pct
        summary = ("Most indicators lean UP. Consider a long setup only with a "
                   "defined stop-loss — never risk more than 1-2% of your capital.")
    elif sell_pct >= 60 and sell_votes >= 2 and sell_votes > buy_votes:
        action, strength = "SELL", sell_pct
        summary = ("Most indicators lean DOWN. Consider a short/exit setup only with "
                   "a defined stop-loss — never risk more than 1-2% of your capital.")
    else:
        action, strength = "WAIT", max(buy_pct, sell_pct)
        summary = ("Signals are mixed or unconfirmed — no strong agreement yet. The "
                   "disciplined move is usually to wait for a cleaner setup.")

    return {
        "action": action,          # BUY / SELL / WAIT
        "strength": strength,      # 0-100
        "buy_score": buy_pct,
        "sell_score": sell_pct,
        "components": components,   # list of (name, side, detail)
        "summary": summary,
    }
