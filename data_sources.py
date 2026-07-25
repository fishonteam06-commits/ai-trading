"""
data_sources.py
----------------
This is where the live market data comes from. All free sources:
  - Crypto  -> Binance public API (no key needed)
  - Stocks  -> Yahoo Finance (yfinance library)
  - Forex   -> Yahoo Finance (currency pairs)

Each function returns a pandas DataFrame with the columns:
Open, High, Low, Close, Volume  (index = time).
"""

import re

import pandas as pd
import requests

# yfinance optional import — so crypto still works even if it isn't installed
try:
    import yfinance as yf
    _HAS_YF = True
except Exception:
    _HAS_YF = False

# Only these characters are allowed in a symbol (everything else is blocked — security).
_SYMBOL_RE = re.compile(r"^[A-Za-z0-9\.\-=]{1,15}$")


def sanitize_symbol(symbol: str) -> str:
    """
    Cleans the symbol — only valid characters. Blocks invalid/dangerous input
    (injection, long strings). Raises ValueError on bad input.
    """
    s = (symbol or "").strip().upper()
    if not _SYMBOL_RE.match(s):
        raise ValueError(
            f"Invalid symbol: '{symbol}'. Use letters/numbers only "
            "(e.g. BTCUSDT, AAPL, EURUSD)."
        )
    return s


# Mapping of Binance intervals (from the dashboard's simple names)
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
    "4h": ("1h", "60d"),    # yfinance has no 4h, so we use 1h
    "1d": ("1d", "1y"),
}


# Binance public hosts — the first may be blocked (HTTP 451) from the US/some regions,
# so 'data-api.binance.vision' is a fallback (it works everywhere, including from cloud servers).
_BINANCE_HOSTS = [
    "https://api.binance.com",
    "https://data-api.binance.vision",
    "https://api1.binance.com",
]


def _binance_get(path: str, params: dict):
    """Binance call — if one host is blocked/fails, it tries the next."""
    last_err = None
    for host in _BINANCE_HOSTS:
        try:
            resp = requests.get(host + path, params=params, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            last_err = e
            continue
    raise RuntimeError(f"Could not fetch data from Binance (all hosts failed): {last_err}")


def get_crypto(symbol: str = "BTCUSDT", interval: str = "1h", limit: int = 200) -> pd.DataFrame:
    """
    Crypto data from Binance. symbol like 'BTCUSDT', 'ETHUSDT', 'BNBUSDT'.
    """
    raw = _binance_get("/api/v3/klines", {
        "symbol": symbol.upper(),
        "interval": _BINANCE_INTERVAL.get(interval, "1h"),
        "limit": limit,
    })

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
            "yfinance is not installed. Run in the terminal: pip install yfinance"
        )
    yf_interval, period = _YF_INTERVAL.get(interval, ("1d", "1y"))
    data = yf.download(
        symbol, period=period, interval=yf_interval,
        progress=False, auto_adjust=True,
    )
    if data is None or data.empty:
        raise RuntimeError(f"No data found for '{symbol}'. Please check the symbol again.")

    # yfinance sometimes returns multi-level columns — flatten them
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    data = data.rename(columns=str.title)
    keep = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c in data.columns]
    return data[keep].tail(limit)


def get_stock(symbol: str = "AAPL", interval: str = "1d", limit: int = 200) -> pd.DataFrame:
    """
    Stock data from Yahoo Finance. symbol like 'AAPL', 'TSLA', 'MSFT'.
    Yahoo does not provide reliable data for Pakistan stocks (PSX).
    """
    return _get_yahoo(symbol.upper(), interval, limit)


def get_forex(symbol: str = "EURUSD", interval: str = "1d", limit: int = 200) -> pd.DataFrame:
    """
    Forex data from Yahoo Finance. symbol like 'EURUSD', 'GBPUSD', 'USDPKR'.
    Internally this becomes Yahoo's 'EURUSD=X' format.
    """
    yahoo_symbol = symbol.upper().replace("=X", "") + "=X"
    return _get_yahoo(yahoo_symbol, interval, limit)


def get_commodity(symbol: str = "GC=F", interval: str = "1d", limit: int = 200) -> pd.DataFrame:
    """
    Commodity data from Yahoo Finance (futures). Examples:
    Gold 'GC=F', Silver 'SI=F', Platinum 'PL=F', Copper 'HG=F',
    Crude Oil 'CL=F', Natural Gas 'NG=F'.
    """
    return _get_yahoo(symbol.upper(), interval, limit)


def get_live_price(market: str, symbol: str) -> float | None:
    """
    Just the latest price (very fast, lightweight call). For the live ticker.
    Crypto  -> Binance's real-time ticker (updates within seconds)
    Stock/Forex -> Yahoo (note: free Yahoo data is ~15 min delayed)
    """
    market = market.lower()
    try:
        symbol = sanitize_symbol(symbol)   # security: block bad input
        if market == "crypto":
            data = _binance_get("/api/v3/ticker/price", {"symbol": symbol})
            return float(data["price"])

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
    Picks the right source from a single place.
    market: 'crypto' | 'stock' | 'forex'
    """
    market = market.lower()
    symbol = sanitize_symbol(symbol)       # security: block bad input
    limit = max(10, min(int(limit), 1000)) # keep limit within a sensible range
    if market == "crypto":
        return get_crypto(symbol, interval, limit)
    if market == "stock":
        return get_stock(symbol, interval, limit)
    if market == "forex":
        return get_forex(symbol, interval, limit)
    if market == "commodity":
        return get_commodity(symbol, interval, limit)
    raise ValueError(f"Unrecognized market: {market}")
