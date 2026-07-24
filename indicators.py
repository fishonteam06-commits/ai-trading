"""
indicators.py
--------------
Technical indicators — yeh sab price data se calculate hote hain.
Koi bhi external library nahi (sirf pandas/numpy), taake install asaan rahe.
"""

import pandas as pd
import numpy as np


def sma(series: pd.Series, period: int) -> pd.Series:
    """Simple Moving Average — pichle N candles ka average price."""
    return series.rolling(window=period).mean()


def ema(series: pd.Series, period: int) -> pd.Series:
    """Exponential Moving Average — naye prices ko zyada weight deta hai."""
    return series.ewm(span=period, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Relative Strength Index (0-100).
    > 70 = overbought (bohat khareeda gaya, girne ka chance)
    < 30 = oversold  (bohat becha gaya, barhne ka chance)
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
    MACD — trend aur momentum dikhata hai.
    Returns: (macd_line, signal_line, histogram)
    macd_line signal_line ke upar cross kare = bullish (upar).
    """
    macd_line = ema(series, fast) - ema(series, slow)
    signal_line = ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Average True Range — market kitna 'hilta' hai (volatility).
    Stop-loss aur take-profit set karne ke liye bohat useful.
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
    Recent support (neeche wali floor) aur resistance (upar wali ceiling).
    Simple version: pichle N candles ka high aur low.
    """
    recent = df.tail(lookback)
    return float(recent["Low"].min()), float(recent["High"].max())


def fibonacci_levels(df: pd.DataFrame, lookback: int = 100) -> dict:
    """
    Fibonacci retracement levels — traders in par bounce/rejection dekhte hain.
    Recent high se low tak ke beech ke 'magic levels' nikalta hai.
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
    VWAP (Volume Weighted Average Price) — jahan asal mein volume trade hua.
    Day-traders isay 'fair price' line ki tarah use karte hain.
    """
    typical = (df["High"] + df["Low"] + df["Close"]) / 3
    vol = df["Volume"].replace(0, 1e-9)
    return (typical * vol).cumsum() / vol.cumsum()


def bollinger_bands(series: pd.Series, period: int = 20, std_mult: float = 2.0):
    """
    Bollinger Bands — price ka normal range.
    Returns: (upper_band, middle_band, lower_band)
    Price upper band ke qareeb = mehnga; lower band ke qareeb = sasta.
    """
    middle = sma(series, period)
    std = series.rolling(window=period).std()
    upper = middle + std_mult * std
    lower = middle - std_mult * std
    return upper, middle, lower


def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ek price DataFrame leke usmein saare indicators add kar deta hai.
    DataFrame mein 'Close' column hona zaroori hai.
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
