"""
portfolio.py
-------------
Paper Trading Tracker — practice trades without risking real money.

This tool saves your practice trades to a file (paper_trades.json), so they
stay safe even after you close and reopen the app. It tracks the profit/loss
(P&L) of each trade and the win-rate of the whole portfolio.

** This is for practice/learning only — no real money is involved. **
"""

import json
import os
from datetime import datetime

_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "paper_trades.json")


def _load() -> list:
    if not os.path.exists(_FILE):
        return []
    try:
        with open(_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save(trades: list) -> None:
    with open(_FILE, "w", encoding="utf-8") as f:
        json.dump(trades, f, indent=2, default=str)


def add_trade(market: str, symbol: str, side: str, entry: float, units: float,
              stop_loss: float | None = None, take_profit: float | None = None) -> dict:
    """Opens a new practice trade (status = open)."""
    trades = _load()
    trade = {
        "id": (max([t["id"] for t in trades], default=0) + 1),
        "market": market,
        "symbol": symbol.upper(),
        "side": side.upper(),          # BUY (long) or SELL (short)
        "entry": float(entry),
        "units": float(units),
        "stop_loss": float(stop_loss) if stop_loss else None,
        "take_profit": float(take_profit) if take_profit else None,
        "status": "open",
        "exit": None,
        "pnl": None,
        "opened_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "closed_at": None,
    }
    trades.append(trade)
    _save(trades)
    return trade


def close_trade(trade_id: int, exit_price: float) -> dict | None:
    """Closes an open trade at the given price and computes the P&L."""
    trades = _load()
    for t in trades:
        if t["id"] == trade_id and t["status"] == "open":
            exit_price = float(exit_price)
            if t["side"] == "BUY":
                pnl = (exit_price - t["entry"]) * t["units"]
            else:  # SELL / short: profit when price falls
                pnl = (t["entry"] - exit_price) * t["units"]
            t["exit"] = exit_price
            t["pnl"] = round(pnl, 2)
            t["status"] = "closed"
            t["closed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            _save(trades)
            return t
    return None


def delete_trade(trade_id: int) -> None:
    """Removes a trade record."""
    trades = [t for t in _load() if t["id"] != trade_id]
    _save(trades)


def get_open() -> list:
    return [t for t in _load() if t["status"] == "open"]


def get_closed() -> list:
    return [t for t in _load() if t["status"] == "closed"]


def unrealized_pnl(trade: dict, current_price: float) -> float:
    """The unrealized (on-paper) profit/loss of an open trade so far."""
    if trade["side"] == "BUY":
        return round((current_price - trade["entry"]) * trade["units"], 2)
    return round((trade["entry"] - current_price) * trade["units"], 2)


def summary() -> dict:
    """A summary of the whole paper portfolio: total P&L, win-rate, etc."""
    closed = get_closed()
    total_pnl = round(sum(t["pnl"] for t in closed if t["pnl"] is not None), 2)
    wins = [t for t in closed if t["pnl"] and t["pnl"] > 0]
    win_rate = round(len(wins) / len(closed) * 100, 1) if closed else 0.0
    return {
        "total_trades": len(closed),
        "open_trades": len(get_open()),
        "total_pnl": total_pnl,
        "win_rate": win_rate,
        "wins": len(wins),
        "losses": len(closed) - len(wins),
    }
