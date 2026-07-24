"""
backtest.py
------------
Simple backtest — "if I had followed this signal over the past few months,
what would have happened?" It tests the strategy against history.

** IMPORTANT **: Past results are NOT a guarantee of the future. This is only
to understand that a signal is not blindly reliable — every strategy is
sometimes wrong. That is exactly why risk management matters.
"""

import pandas as pd

from indicators import add_all_indicators
from signals import generate_signal


def run_backtest(df: pd.DataFrame, start_capital: float = 1000.0) -> dict:
    """
    Derives a signal at each candle and runs a simple long-only strategy:
      - BUY signal and no position -> buy with the full capital
      - SELL signal and holding a position -> sell
    Fees/slippage are ignored (this is only an educational estimate).
    """
    df = df.copy()
    capital = start_capital
    units = 0.0
    in_position = False
    trades = []
    equity_curve = []
    buy_price = 0.0

    # enough warmup is needed so the indicators are ready
    warmup = 60
    for i in range(warmup, len(df)):
        window = df.iloc[: i + 1]
        sig = generate_signal(window)
        price = sig["price"]

        if sig["action"] == "BUY" and not in_position:
            units = capital / price
            buy_price = price
            capital = 0.0
            in_position = True
            trades.append({"type": "BUY", "price": price, "time": window.index[-1]})
        elif sig["action"] == "SELL" and in_position:
            capital = units * price
            pnl_pct = (price - buy_price) / buy_price * 100
            trades.append({"type": "SELL", "price": price, "time": window.index[-1], "pnl_pct": round(pnl_pct, 2)})
            units = 0.0
            in_position = False

        equity = capital + units * price
        equity_curve.append({"time": window.index[-1], "equity": equity})

    # at the end, if a position is still open, close it at the final price
    final_price = float(df.iloc[-1]["Close"])
    final_equity = capital + units * final_price

    sells = [t for t in trades if t["type"] == "SELL"]
    wins = [t for t in sells if t.get("pnl_pct", 0) > 0]
    total_return = (final_equity - start_capital) / start_capital * 100

    # comparison against buy & hold
    first_price = float(df.iloc[warmup]["Close"])
    buy_hold_return = (final_price - first_price) / first_price * 100

    return {
        "start_capital": round(start_capital, 2),
        "final_equity": round(final_equity, 2),
        "total_return_pct": round(total_return, 2),
        "buy_hold_return_pct": round(buy_hold_return, 2),
        "num_trades": len(sells),
        "win_rate": round(len(wins) / len(sells) * 100, 1) if sells else 0.0,
        "equity_curve": pd.DataFrame(equity_curve).set_index("time") if equity_curve else pd.DataFrame(),
        "trades": trades,
    }
