#!/usr/bin/env python3
# backtest.py

import json
from api.api import get_ohlcv
from analysis.technical_analysis import compute_indicators, detect_patterns
from analysis.strategy_scoring import score_strategy, DEFAULT_WEIGHTS

def load_config(path="data/config.json"):
    with open(path) as f:
        return json.load(f)

def run_backtest(cfg):
    results = []
    alert_count = 0
    total = 0

    for symbol in cfg["symbols"]:
        # 1) fetch data
        df = get_ohlcv(symbol, cfg["timeframe"])
        # 2) indicators
        df = compute_indicators(df, cfg["indicators"])
        # 3) patterns
        patterns = detect_patterns(df)
        # 4) score & confidence
        score = score_strategy(df, patterns)
        max_score = sum(w for w in DEFAULT_WEIGHTS.values() if w > 0)
        confidence = score / max_score if max_score else 0

        total += 1
        is_alert = confidence >= cfg["alerts"]["confidence_threshold"]
        if is_alert:
            alert_count += 1

        results.append({
            "symbol": symbol,
            "score": round(score, 2),
            "confidence": round(confidence, 2),
            "alert": is_alert
        })

    return results, alert_count, total

def print_summary(results, alert_count, total):
    # Affiche ligne par ligne
    print(f"\n=== Backtest summary ===")
    for r in results:
        flag = "⚠️" if r["alert"] else "—"
        print(f"{flag} {r['symbol']:8s}  score={r['score']:5.2f}  conf={r['confidence']*100:5.1f}%")
    print(f"\nTotal symbols: {total}, Alerts triggered: {alert_count}")

if __name__ == "__main__":
    config = load_config()
    results, alert_count, total = run_backtest(config)
    print_summary(results, alert_count, total)
