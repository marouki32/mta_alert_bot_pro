# analysis/strategy_scoring.py

import pandas as pd
from analysis.technical_analysis import detect_patterns

# Poids par défaut de chaque signal pour le calcul de confiance
DEFAULT_WEIGHTS = {
    'hammer': 1.0,
    'hanging_man': -1.0,
    'bullish_engulfing': 1.5,
    'bearish_harami': -1.5,
    'shooting_star': -1.0,
    'gravestone': -1.0,
    'doji': 0.5,
    'morning_star': 2.0,
    'rsi_overbought': -1.0,
    'rsi_oversold': 1.0,
    'ema_bull_cross': 1.0,
    'ema_bear_cross': -1.0,
    'bb_break_upper': 1.0,
    'bb_break_lower': -1.0
}

def score_strategy(
    df: pd.DataFrame,
    patterns: dict,
    weights: dict = None
) -> float:
    """
    Combine pattern signals, indicator thresholds and Bollinger/EMA breakouts into one score.
    Returns >0 bullish bias, <0 bearish bias.
    - df: DataFrame with columns like 'rsi', 'ema_{n}', 'bb_upper', 'bb_lower', maybe 'close'.
    - patterns: output of detect_patterns().
    - weights: optional override for DEFAULT_WEIGHTS.
    """
    # merge default and custom weights
    wts = DEFAULT_WEIGHTS.copy()
    if weights:
        wts.update(weights)

    score = 0.0

    # 1) patterns
    for patt, present in patterns.items():
        if present and patt in wts:
            score += wts[patt]

    # 2) RSI extremes
    if 'rsi' in df.columns:
        rsi = df['rsi'].iloc[-1]
        mean_rsi = df['rsi'].rolling(window=14, min_periods=1).mean().iloc[-1]
        if rsi > mean_rsi + 10 and 'rsi_overbought' in wts:
            score += wts['rsi_overbought']
        if rsi < mean_rsi - 10 and 'rsi_oversold' in wts:
            score += wts['rsi_oversold']

    # 3) EMA cross (short vs long)
    ema_cols = sorted(
        [c for c in df.columns if c.startswith('ema_')],
        key=lambda c: int(c.split('_')[1])
    )
    if len(ema_cols) >= 2:
        short, long = ema_cols[0], ema_cols[1]
        # check last two values to detect cross
        if df[short].iloc[-1] > df[long].iloc[-1] and df[short].iloc[-2] <= df[long].iloc[-2]:
            score += wts.get('ema_bull_cross', 0.0)
        if df[short].iloc[-1] < df[long].iloc[-1] and df[short].iloc[-2] >= df[long].iloc[-2]:
            score += wts.get('ema_bear_cross', 0.0)

    # 4) Bollinger breakout (only if we have close)
    if 'bb_upper' in df.columns and 'bb_lower' in df.columns and 'close' in df.columns:
        close = df['close'].iloc[-1]
        if close > df['bb_upper'].iloc[-1]:
            score += wts.get('bb_break_upper', 0.0)
        if close < df['bb_lower'].iloc[-1]:
            score += wts.get('bb_break_lower', 0.0)

    return score
