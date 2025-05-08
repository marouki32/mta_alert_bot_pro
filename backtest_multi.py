#!/usr/bin/env python3
# backtest_multi.py

import json
import datetime
from datetime import timezone
from api.api import get_ohlcv
from analysis.technical_analysis import compute_indicators, detect_patterns
from analysis.strategy_scoring import score_strategy, DEFAULT_WEIGHTS
import pandas as pd

def load_config():
    with open('data/config.json') as f:
        return json.load(f)

def backtest_one(df, cfg):
    """Retourne (alert, score, confidence)."""
    df = compute_indicators(df, cfg['indicators'])
    patterns = detect_patterns(df)
    score = score_strategy(df, patterns)
    max_score = sum(w for w in DEFAULT_WEIGHTS.values() if w > 0)
    confidence = score / max_score if max_score else 0
    return confidence >= cfg['alerts']['confidence_threshold'], score, confidence

def run_backtest_multi(cfg):
    results = []
    today = datetime.datetime.now(timezone.utc)

    for sym in cfg['symbols']:
        # Récupère toujours l'historique complet via get_ohlcv
        for tf in cfg['backtest']['timeframes']:
            df_full = get_ohlcv(sym, tf)
            if df_full is None or df_full.empty:
                print(f"Aucune donnée pour {sym} en {tf}")
                continue

            for period in cfg['backtest']['periods']:
                days = period['days']
                since = today - datetime.timedelta(days=days)
                # Filtrer le DataFrame sur les derniers `days`
                df = df_full[df_full.index >= since]
                if df.empty:
                    print(f"Aucune donnée récente pour {sym} - {tf} - {period['label']}")
                    continue

                alert, score, conf = backtest_one(df, cfg)
                results.append({
                    'symbol': sym,
                    'timeframe': tf,
                    'period': period['label'],
                    'alert': alert,
                    'score': round(score, 2),
                    'confidence': round(conf, 2)
                })

    return pd.DataFrame(results)

def summarize(df):
    stats = df.groupby(['timeframe','period']).agg(
        total=('alert','size'),
        alerts=('alert','sum'),
        win_rate=('alert', lambda x: float(x.sum())/len(x) if len(x)>0 else 0),
        avg_confidence=('confidence','mean')
    ).reset_index()
    return stats

if __name__ == '__main__':
    cfg = load_config()
    print("🔍 Backtest multi-périodes démarré…")
    df = run_backtest_multi(cfg)
    if df.empty:
        print("⚠️ Aucun résultat de backtest.")
    else:
        print("\n=== Résultats détaillés ===")
        print(df.to_string(index=False))
        stats = summarize(df)
        print("\n=== Statistiques résumées ===")
        print(stats.to_string(index=False))

