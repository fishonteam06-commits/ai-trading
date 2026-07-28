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
import time

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


# Friendly / MT5-style symbols mapped to the ticker Yahoo actually serves.
# (Yahoo has no free spot XAUUSD/XAGUSD, so we use the futures as a close proxy.)
_YAHOO_ALIAS = {
    "XAUUSD": "GC=F",      # Spot Gold  -> Gold futures (close proxy)
    "XAGUSD": "SI=F",      # Spot Silver -> Silver futures
    "DXY": "DX-Y.NYB",     # US Dollar Index
    "US30": "^DJI",        # Dow Jones
    "US500": "^GSPC",      # S&P 500
    "NAS100": "^NDX",      # Nasdaq 100
}


def _resolve_yahoo(symbol: str) -> str:
    """Maps a friendly/MT5-style symbol to the ticker Yahoo serves."""
    return _YAHOO_ALIAS.get(symbol.upper(), symbol)


# Some symbols are best sourced from Binance (real-time, reliable on the cloud).
# PAXG is a gold-backed token (~1 troy oz), so PAXGUSDT tracks the gold price.
_BINANCE_PROXY = {
    "XAUUSD": "PAXGUSDT",   # Spot Gold  -> PAX Gold on Binance (real-time)
    "GC=F": "PAXGUSDT",     # Gold futures symbol also routed to real-time gold
}


def is_realtime(market: str, symbol: str) -> bool:
    """True if the data comes from Binance (real-time), else Yahoo (delayed)."""
    s = (symbol or "").strip().upper()
    return market.lower() == "crypto" or s in _BINANCE_PROXY


def binance_symbol_for(market: str, symbol: str) -> str | None:
    """The Binance trading pair for this symbol (for the live client-side chart),
    or None if it isn't a Binance-sourced symbol. Sanitizes first (security)."""
    try:
        s = sanitize_symbol(symbol)          # blocks injection / bad input
    except Exception:
        return None
    if s in _BINANCE_PROXY:
        return _BINANCE_PROXY[s]
    if market.lower() == "crypto":
        return s
    return None


def market_status(market: str, symbol: str) -> tuple[bool, str]:
    """
    Is the market open right now? Returns (is_open, label).
    - Crypto and PAXG-gold (XAUUSD/GC=F) trade 24/7.
    - Forex / metals / indices (via Yahoo) close on the weekend.
    - US stocks trade roughly Mon-Fri 13:30-20:00 UTC.
    This is why on a Sunday nothing updates — the market is simply closed.
    """
    from datetime import datetime, timezone
    if is_realtime(market, symbol):
        return True, "🟢 OPEN — trades 24/7"

    now = datetime.now(timezone.utc)
    wd = now.weekday()          # Mon=0 ... Sat=5, Sun=6
    minutes = now.hour * 60 + now.minute

    if market.lower() == "stock":
        if wd >= 5:
            return False, "🔴 CLOSED — weekend (US stocks reopen Monday)"
        if 13 * 60 + 30 <= minutes <= 20 * 60:
            return True, "🟢 OPEN — US market hours"
        return False, "🔴 CLOSED — outside US market hours (approx 13:30–20:00 UTC)"

    # Forex / commodities / indices: open Sunday ~22:00 UTC to Friday ~22:00 UTC
    if wd == 5:
        return False, "🔴 CLOSED — weekend (Saturday). Reopens Sunday ~22:00 UTC"
    if wd == 6 and minutes < 22 * 60:
        return False, "🔴 CLOSED — weekend (Sunday). Reopens ~22:00 UTC"
    if wd == 4 and minutes >= 22 * 60:
        return False, "🔴 CLOSED — weekend just started (Friday close)"
    return True, "🟢 OPEN"


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
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "1h": "1h",
    "4h": "4h",
    "1d": "1d",
}
_YF_INTERVAL = {
    "1m": ("1m", "5d"),     # (interval, period)
    "5m": ("5m", "5d"),
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
        raise RuntimeError("yfinance is not installed. Run: pip install yfinance")

    yf_interval, period = _YF_INTERVAL.get(interval, ("1d", "1y"))
    resolved = _resolve_yahoo(symbol)
    data = None
    # Retry a few times (short) — Yahoo rate-limits shared cloud IPs intermittently.
    for attempt in range(3):
        try:
            data = yf.download(resolved, period=period, interval=yf_interval,
                               progress=False, auto_adjust=True)
            if data is not None and not data.empty:
                break
        except Exception:
            data = None
        time.sleep(0.6)

    if data is None or data.empty:
        raise RuntimeError(
            f"No data for '{symbol}' right now (Yahoo sometimes rate-limits cloud "
            "servers). Please try again in a moment — or use Crypto and Gold (XAUUSD), "
            "which stream live from Binance and are always reliable."
        )

    # yfinance sometimes returns multi-level columns — flatten them
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    data = data.rename(columns=str.title)
    keep = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c in data.columns]
    # Drop rows with no Close (indices sometimes have a trailing empty bar)
    result = data[keep].dropna(subset=["Close"])
    if result.empty:
        raise RuntimeError(f"No usable data for '{symbol}'.")

    # Yahoo has no native 4h — we fetch 1h and resample to real 4h candles,
    # so the timeframe matches the label (instead of silently showing 1h data).
    if interval == "4h" and not result.empty:
        result = result.resample("4h").agg(
            {"Open": "first", "High": "max", "Low": "min",
             "Close": "last", "Volume": "sum"}
        ).dropna(subset=["Close"])

    return result.tail(limit)


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
        proxy = _BINANCE_PROXY.get(symbol)
        if proxy:
            data = _binance_get("/api/v3/ticker/price", {"symbol": proxy})
            return float(data["price"])
        if market == "crypto":
            data = _binance_get("/api/v3/ticker/price", {"symbol": symbol})
            return float(data["price"])

        if not _HAS_YF:
            return None
        yahoo_symbol = symbol.upper()
        if market == "forex":
            yahoo_symbol = yahoo_symbol.replace("=X", "") + "=X"
        ticker = yf.Ticker(_resolve_yahoo(yahoo_symbol))
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
    # Gold (and a few symbols) stream live from Binance instead of delayed Yahoo.
    proxy = _BINANCE_PROXY.get(symbol)
    if proxy:
        return get_crypto(proxy, interval, limit)
    if market == "crypto":
        return get_crypto(symbol, interval, limit)
    if market == "stock":
        return get_stock(symbol, interval, limit)
    if market == "forex":
        return get_forex(symbol, interval, limit)
    if market == "commodity":
        return get_commodity(symbol, interval, limit)
    raise ValueError(f"Unrecognized market: {market}")
