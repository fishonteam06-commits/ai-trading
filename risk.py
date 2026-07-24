"""
risk.py
--------
Risk management — the single most important thing for protecting your money
in trading.

The core idea: controlling losses matters more than chasing profit. Pro traders
risk only 1-2% of their total capital on a single trade. This module does exactly
that calculation: how much to put in, and where the stop-loss/take-profit go.
"""


def position_size(capital: float, risk_percent: float, entry: float, stop_loss: float) -> dict:
    """
    Tells you how many units to buy in a trade so that if the stop-loss is hit,
    only 'risk_percent' of your capital is lost.

    capital      = your total amount (e.g. 1000 USD)
    risk_percent = how much % to risk on one trade (e.g. 1 or 2)
    entry        = the buy price
    stop_loss    = where you exit if the trade goes wrong
    """
    risk_amount = capital * (risk_percent / 100.0)      # how much money is at risk
    per_unit_risk = abs(entry - stop_loss)              # loss per unit
    if per_unit_risk <= 0:
        return {"error": "Stop-loss cannot be equal to the entry."}

    units = risk_amount / per_unit_risk
    position_value = units * entry
    return {
        "risk_amount": round(risk_amount, 2),
        "units": round(units, 6),
        "position_value": round(position_value, 2),
        "per_unit_risk": round(per_unit_risk, 6),
    }


def suggest_levels(entry: float, atr_value: float, direction: str = "BUY",
                   atr_mult_sl: float = 1.5, rr_ratio: float = 2.0) -> dict:
    """
    Suggests a stop-loss and take-profit based on ATR (volatility).

    direction  = 'BUY' (long) or 'SELL' (short)
    atr_mult_sl= how many ATR the stop-loss sits away (default 1.5x)
    rr_ratio   = reward:risk ratio (2.0 means profit target = 2x risk)

    ** This is only an educational reference, not a guarantee. **
    """
    if not atr_value or atr_value <= 0:
        return {"error": "ATR not available — cannot suggest levels."}

    risk_dist = atr_value * atr_mult_sl
    reward_dist = risk_dist * rr_ratio

    if direction.upper() == "BUY":
        stop_loss = entry - risk_dist
        take_profit = entry + reward_dist
    else:  # SELL / short
        stop_loss = entry + risk_dist
        take_profit = entry - reward_dist

    return {
        "direction": direction.upper(),
        "entry": round(entry, 6),
        "stop_loss": round(stop_loss, 6),
        "take_profit": round(take_profit, 6),
        "risk_reward": f"1 : {rr_ratio:g}",
        "risk_distance": round(risk_dist, 6),
    }
