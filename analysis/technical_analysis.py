import pandas as pd

def compute_indicators(df,params):
    p=params
    # RSI
    df['rsi'] = 100 - (100 / (1 + (df['close'].diff().clip(lower=0).rolling(p.get('rsi',14)).mean() / (-df['close'].diff().clip(upper=0).rolling(p.get('rsi',14)).mean()))))
    # EMAs
    for e in p.get('ema', []):
        df[f'ema_{e}'] = df['close'].ewm(span=e, adjust=False).mean()
    # Bollinger Bands
    w, s = p.get('bollinger', {}).get('window', 20), p.get('bollinger', {}).get('std', 2)
    df['bb_mid'] = df['close'].rolling(w).mean()
    df['bb_std'] = df['close'].rolling(w).std()
    df['bb_upper'] = df['bb_mid'] + s * df['bb_std']
    df['bb_lower'] = df['bb_mid'] - s * df['bb_std']
    return df

def detect_patterns(df):
    o, c, h, l = df['open'].values, df['close'].values, df['high'].values, df['low'].values
    L = len(df)
    patterns = {}
    # compute shadows & body for last candle
    i = -1
    body = abs(c[i] - o[i]); rng = h[i] - l[i]
    upper_shadow = h[i] - max(o[i], c[i]); lower_shadow = min(o[i], c[i]) - l[i]
    # Hammer & Hanging Man
    patterns['hammer'] = (lower_shadow > 2 * body) and (body < 0.3 * rng)
    patterns['hanging_man'] = patterns['hammer'] and (L > 2) and (c[-2] > c[-3])
    # Engulfing & Harami
    patterns['bullish_engulfing'] = (L > 1) and (c[i] > o[i]) and (o[i] < c[-2]) and (c[i] > o[-2])
    patterns['bearish_harami'] = (L > 1) and (o[i] < c[i]) and (o[i] > c[-2]) and (c[i] < o[-2])
    # Shooting Star & Gravestone Doji
    patterns['shooting_star'] = (upper_shadow > 2 * body) and (body < 0.3 * rng)
    patterns['gravestone'] = (body < 0.1 * rng) and (upper_shadow < 0.05 * rng)
    # Doji
    patterns['doji'] = (body < 0.1 * rng) and (upper_shadow > 0.1 * rng) and (lower_shadow > 0.1 * rng)
    # Morning Star
    if L > 2:
        o1, c1 = o[-3], c[-3]; o2, c2 = o[-2], c[-2]; o3, c3 = o[-1], c[-1]
        b1, b2, b3 = abs(c1 - o1), abs(c2 - o2), abs(c3 - o3)
        cond1 = (c1 < o1) and (b1 > 0)
        cond2 = b2 < 0.5 * b1
        cond3 = (c3 > o3) and (c3 > (o1 - 0.5 * b1))
        patterns['morning_star'] = cond1 and cond2 and cond3
    else:
        patterns['morning_star'] = False
    return patterns
