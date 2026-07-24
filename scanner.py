"""
scanner.py
-----------
Market Scanner — ek saath bohat saare symbols scan karke best signals dhoondta hai.
Yeh "har din opportunities" dhoondhne ka sabse kaam ka feature hai:
subah kholo, scan chalao, aur dekho kahan strong setup ban raha hai.
"""

import pandas as pd

from data_sources import get_data
from indicators import add_all_indicators
from signals import generate_signal


def scan(market: str, symbols: list[str], interval: str = "1h") -> pd.DataFrame:
    """
    Diye gaye symbols ki list scan karta hai aur ek table return karta hai
    jise signal strength ke hisab se sort kiya gaya hota hai.
    """
    rows = []
    for sym in symbols:
        try:
            df = add_all_indicators(get_data(market, sym, interval, limit=200))
            sig = generate_signal(df)
            last = df.iloc[-1]
            rows.append({
                "Symbol": sym.upper(),
                "Price": round(sig["price"], 6),
                "Signal": sig["action"],
                "Strength %": sig["score"],
                "RSI": round(float(last["RSI"]), 0) if pd.notna(last.get("RSI")) else None,
                "Bull:Bear": f"{sig['bullish_points']}:{sig['bearish_points']}",
            })
        except Exception as e:
            rows.append({
                "Symbol": sym.upper(), "Price": None, "Signal": "ERROR",
                "Strength %": 0, "RSI": None, "Bull:Bear": str(e)[:30],
            })

    df_out = pd.DataFrame(rows)
    if df_out.empty:
        return df_out

    # Strong BUY/SELL upar aayen, HOLD neeche
    order = {"BUY": 0, "SELL": 1, "HOLD": 2, "ERROR": 3}
    df_out["_o"] = df_out["Signal"].map(lambda s: order.get(s, 3))
    df_out = df_out.sort_values(["_o", "Strength %"], ascending=[True, False])
    return df_out.drop(columns="_o").reset_index(drop=True)
