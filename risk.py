"""
risk.py
--------
Risk management — trading mein paisa bachane ki SABSE zaroori cheez.

Asal baat: profit se zyada important 'nuksan ko control' karna hai.
Pro traders ek trade par apni total capital ka sirf 1-2% risk karte hain.
Yeh module wahi hisaab lagata hai: kitna lagana hai, stop-loss/take-profit kahan.
"""


def position_size(capital: float, risk_percent: float, entry: float, stop_loss: float) -> dict:
    """
    Batata hai ke ek trade mein kitni units khareedni chahiye taake
    agar stop-loss lage to sirf 'risk_percent' hi doobe.

    capital      = aapki total raqam (jaise 1000 USD)
    risk_percent = ek trade par kitna % risk (jaise 1 ya 2)
    entry        = khareedne ka price
    stop_loss    = jahan nikal jayenge agar galat hua
    """
    risk_amount = capital * (risk_percent / 100.0)      # kitne paise risk par
    per_unit_risk = abs(entry - stop_loss)              # per unit kitna nuksan
    if per_unit_risk <= 0:
        return {"error": "Stop-loss entry ke barabar nahi ho sakta."}

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
    ATR (volatility) ki bunyaad par stop-loss aur take-profit suggest karta hai.

    direction  = 'BUY' (long) ya 'SELL' (short)
    atr_mult_sl= stop-loss kitne ATR door ho (default 1.5x)
    rr_ratio   = reward:risk ratio (2.0 matlab profit target = 2x risk)

    ** Yeh sirf ek educational reference hai, guarantee nahi. **
    """
    if not atr_value or atr_value <= 0:
        return {"error": "ATR available nahi — level suggest nahi kar sakte."}

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
