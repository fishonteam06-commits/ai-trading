"""
data_sources.py
----------------
Yahan se market ka live data aata hai. Sab free sources:
  - Crypto  -> Binance public API (koi key nahi chahiye)
  - Stocks  -> Yahoo Finance (yfinance library)
  - Forex   -> Yahoo Finance (currency pairs)

Har function ek pandas DataFrame return karta hai jismein
columns hote hain: Open, High, Low, Close, Volume  (index = time).
"""

import re

import pandas as pd
import requests

# yfinance optional import — agar install na ho to crypto phir bhi chale
try:
    import yfinance as yf
    _HAS_YF = True
except Exception:
    _HAS_YF = False

# Sirf yeh characters symbol mein allowed hain (baaqi block — security).
_SYMBOL_RE = re.compile(r"^[A-Za-z0-9\.\-=]{1,15}$")


def sanitize_symbol(symbol: str) -> str:
    """
    Symbol ko saaf karta hai — sirf jaayaz characters. Ghalat/khatarnaak input
    (injection, lambe strings) block karta hai. Bad input par ValueError.
    """
    s = (symbol or "").strip().upper()
    if not _SYMBOL_RE.match(s):
        raise ValueError(
            f"Ghalat symbol: '{symbol}'. Sirf letters/numbers use karein "
            "(jaise BTCUSDT, AAPL, EURUSD)."
        )
    return s


# Binance intervals ka mapping (dashboard ke aasan naamon se)
_BINANCE_INTERVAL = {
    "5m": "5m",
    "15m": "15m",
    "1h": "1h",
    "4h": "4h",
    "1d": "1d",
}
_YF_INTERVAL = {
    "5m": ("5m", "5d"),     # (interval, period)
    "15m": ("15m", "5d"),
    "1h": ("60m", "60d"),
    "4h": ("1h", "60d"),    # yfinance mein 4h nahi, 1h use karenge
    "1d": ("1d", "1y"),
}


def get_crypto(symbol: str = "BTCUSDT", interval: str = "1h", limit: int = 200) -> pd.DataFrame:
    """
    Crypto data Binance se. symbol jaise 'BTCUSDT', 'ETHUSDT', 'BNBUSDT'.
    """
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol.upper(),
        "interval": _BINANCE_INTERVAL.get(interval, "1h"),
        "limit": limit,
    }
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    raw = resp.json()

    df = pd.DataFrame(
        raw,
        columns=[
            "open_time", "Open", "High", "Low", "Close", "Volume",
            "close_time", "qav", "trades", "tbav", "tqav", "ignore",
        ],
    )
    df["time"] = pd.to_datetime(df["open_time"], unit="ms")
    df = df.set_index("time")
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        df[col] = pd.to_numeric(df[col])
    return df[["Open", "High", "Low", "Close", "Volume"]]


def _get_yahoo(symbol: str, interval: str, limit: int) -> pd.DataFrame:
    if not _HAS_YF:
        raise RuntimeError(
            "yfinance install nahi hai. Terminal mein chalayein: pip install yfinance"
        )
    yf_interval, period = _YF_INTERVAL.get(interval, ("1d", "1y"))
    data = yf.download(
        symbol, period=period, interval=yf_interval,
        progress=False, auto_adjust=True,
    )
    if data is None or data.empty:
        raise RuntimeError(f"'{symbol}' ka data nahi mila. Symbol dobara check karein.")

    # yfinance kabhi multi-level columns deta hai — unhe flat karo
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    data = data.rename(columns=str.title)
    keep = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c in data.columns]
    return data[keep].tail(limit)


def get_stock(symbol: str = "AAPL", interval: str = "1d", limit: int = 200) -> pd.DataFrame:
    """
    Stock data Yahoo Finance se. symbol jaise 'AAPL', 'TSLA', 'MSFT'.
    Pakistan stocks (PSX) ke liye Yahoo par reliable data nahi hota.
    """
    return _get_yahoo(symbol.upper(), interval, limit)


def get_forex(symbol: str = "EURUSD", interval: str = "1d", limit: int = 200) -> pd.DataFrame:
    """
    Forex data Yahoo Finance se. symbol jaise 'EURUSD', 'GBPUSD', 'USDPKR'.
    Andar Yahoo ka format 'EURUSD=X' ban jaata hai.
    """
    yahoo_symbol = symbol.upper().replace("=X", "") + "=X"
    return _get_yahoo(yahoo_symbol, interval, limit)


def get_live_price(market: str, symbol: str) -> float | None:
    """
    Sirf latest price (bohat tez, halki call). Live ticker ke liye.
    Crypto  -> Binance ka real-time ticker (seconds mein update)
    Stock/Forex -> Yahoo (yaad rahe: free Yahoo data ~15 min delayed hota hai)
    """
    market = market.lower()
    try:
        symbol = sanitize_symbol(symbol)   # security: bad input block
        if market == "crypto":
            url = "https://api.binance.com/api/v3/ticker/price"
            resp = requests.get(url, params={"symbol": symbol}, timeout=8)
            resp.raise_for_status()
            return float(resp.json()["price"])

        if not _HAS_YF:
            return None
        yahoo_symbol = symbol.upper()
        if market == "forex":
            yahoo_symbol = yahoo_symbol.replace("=X", "") + "=X"
        ticker = yf.Ticker(yahoo_symbol)
        info = getattr(ticker, "fast_info", None)
        if info is not None:
            price = info.get("last_price") or info.get("lastPrice")
            if price:
                return float(price)
    except Exception:
        return None
    return None


def get_data(market: str, symbol: str, interval: str = "1h", limit: int = 200) -> pd.DataFrame:
    """
    Ek hi jagah se sahi source chunta hai.
    market: 'crypto' | 'stock' | 'forex'
    """
    market = market.lower()
    symbol = sanitize_symbol(symbol)       # security: bad input block
    limit = max(10, min(int(limit), 1000)) # limit ko sensible range mein rakho
    if market == "crypto":
        return get_crypto(symbol, interval, limit)
    if market == "stock":
        return get_stock(symbol, interval, limit)
    if market == "forex":
        return get_forex(symbol, interval, limit)
    raise ValueError(f"Market pehchana nahi gaya: {market}")
