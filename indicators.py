"""
indicators.py
--------------
Technical indicators — all calculated from price data.
No external library (only pandas/numpy), to keep installation easy.
"""

import pandas as pd
import numpy as np


def sma(series: pd.Series, period: int) -> pd.Series:
    """Simple Moving Average — the average price over the last N candles."""
    return series.rolling(window=period).mean()


def ema(series: pd.Series, period: int) -> pd.Series:
    """Exponential Moving Average — gives more weight to recent prices."""
    return series.ewm(span=period, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Relative Strength Index (0-100).
    > 70 = overbought (heavily bought, chance of a fall)
    < 30 = oversold  (heavily sold, chance of a rise)
    """
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """
    MACD — shows trend and momentum.
    Returns: (macd_line, signal_line, histogram)
    macd_line crossing above the signal_line = bullish (up).
    """
    macd_line = ema(series, fast) - ema(series, slow)
    signal_line = ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Average True Range — how much the market 'moves' (volatility).
    Very useful for setting stop-loss and take-profit levels.
    """
    high, low, close = df["High"], df["Low"], df["Close"]
    prev_close = close.shift(1)
    tr = pd.concat(
        [(high - low), (high - prev_close).abs(), (low - prev_close).abs()],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()


def stochastic(df: pd.DataFrame, k_period: int = 14, d_period: int = 3):
    """
    Stochastic Oscillator (0-100) — momentum.
    > 80 overbought, < 20 oversold.  Returns: (%K, %D)
    """
    low_min = df["Low"].rolling(window=k_period).min()
    high_max = df["High"].rolling(window=k_period).max()
    k = 100 * (df["Close"] - low_min) / (high_max - low_min).replace(0, np.nan)
    d = k.rolling(window=d_period).mean()
    return k, d


def support_resistance(df: pd.DataFrame, lookback: int = 50):
    """
    Recent support (the floor below) and resistance (the ceiling above).
    Simple version: the high and low of the last N candles.
    """
    recent = df.tail(lookback)
    return float(recent["Low"].min()), float(recent["High"].max())


def fibonacci_levels(df: pd.DataFrame, lookback: int = 100) -> dict:
    """
    Fibonacci retracement levels — traders watch for bounces/rejections at these.
    Computes the 'magic levels' between the recent high and low.
    """
    recent = df.tail(lookback)
    hi = float(recent["High"].max())
    lo = float(recent["Low"].min())
    diff = hi - lo
    return {
        "0.0% (High)": hi,
        "23.6%": hi - 0.236 * diff,
        "38.2%": hi - 0.382 * diff,
        "50.0%": hi - 0.5 * diff,
        "61.8% (Golden)": hi - 0.618 * diff,
        "78.6%": hi - 0.786 * diff,
        "100% (Low)": lo,
    }


def vwap(df: pd.DataFrame) -> pd.Series:
    """
    VWAP (Volume Weighted Average Price) — where the volume actually traded.
    Day-traders use it like a 'fair price' line.
    """
    typical = (df["High"] + df["Low"] + df["Close"]) / 3
    vol = df["Volume"].replace(0, 1e-9)
    return (typical * vol).cumsum() / vol.cumsum()


def bollinger_bands(series: pd.Series, period: int = 20, std_mult: float = 2.0):
    """
    Bollinger Bands — the normal range of price.
    Returns: (upper_band, middle_band, lower_band)
    Price near the upper band = expensive; near the lower band = cheap.
    """
    middle = sma(series, period)
    std = series.rolling(window=period).std()
    upper = middle + std_mult * std
    lower = middle - std_mult * std
    return upper, middle, lower


def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes a price DataFrame and adds all indicators to it.
    The DataFrame must contain a 'Close' column.
    """
    df = df.copy()
    close = df["Close"]

    df["SMA20"] = sma(close, 20)
    df["SMA50"] = sma(close, 50)
    df["EMA9"] = ema(close, 9)
    df["EMA20"] = ema(close, 20)
    df["EMA21"] = ema(close, 21)
    df["RSI"] = rsi(close, 14)
    df["ATR"] = atr(df, 14)
    df["VWAP"] = vwap(df)

    k, d = stochastic(df)
    df["STOCH_K"] = k
    df["STOCH_D"] = d

    macd_line, signal_line, hist = macd(close)
    df["MACD"] = macd_line
    df["MACD_SIGNAL"] = signal_line
    df["MACD_HIST"] = hist

    upper, mid, lower = bollinger_bands(close)
    df["BB_UPPER"] = upper
    df["BB_MIDDLE"] = mid
    df["BB_LOWER"] = lower

    return df
