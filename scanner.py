"""
scanner.py
-----------
Market Scanner — scans many symbols at once to find the best signals.
This is the most useful feature for finding "daily opportunities":
open it in the morning, run a scan, and see where a strong setup is forming.
"""

import pandas as pd

from data_sources import get_data
from indicators import add_all_indicators
from signals import generate_signal


def scan(market: str, symbols: list[str], interval: str = "1h") -> pd.DataFrame:
    """
    Scans the given list of symbols and returns a table
    sorted by signal strength.
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

    # Strong BUY/SELL come to the top, HOLD to the bottom
    order = {"BUY": 0, "SELL": 1, "HOLD": 2, "ERROR": 3}
    df_out["_o"] = df_out["Signal"].map(lambda s: order.get(s, 3))
    df_out = df_out.sort_values(["_o", "Strength %"], ascending=[True, False])
    return df_out.drop(columns="_o").reset_index(drop=True)
