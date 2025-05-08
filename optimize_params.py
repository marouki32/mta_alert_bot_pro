#!/usr/bin/env python3
# optimize_params.py
import json
import itertools
import datetime
from datetime import timezone
import pandas as pd

from api.api import get_ohlcv
from analysis.technical_analysis import compute_indicators, detect_patterns
from analysis.strategy_scoring import score_strategy, DEFAULT_WEIGHTS

def load_config(path="data/config.json"):
    with open(path) as f:
        return json.load(f)

def evaluate_params(cfg, rsi, ema_pair, bb_window, bb_std):
    # modifie la config en mémoire
    cfg2 = cfg.copy()
    cfg2["indicators"] = {
        "rsi": rsi,
        "ema": list(ema_pair),
        "bollinger": {"window": bb_window, "std": bb_std}
    }
    # backtest simple: sur chaque symbole, timeframe unique
    results = []
    for sym in cfg2["symbols"]:
        df = get_ohlcv(sym, cfg2["timeframe"])
        if df is None or df.empty: continue
        df = compute_indicators(df, cfg2["indicators"])
        patt = detect_patterns(df)
        score = score_strategy(df, patt)
        max_score = sum(w for w in DEFAULT_WEIGHTS.values() if w>0)
        conf = score / max_score if max_score else 0
        # alerte si conf ≥ threshold
        alert = conf >= cfg2["alerts"]["confidence_threshold"]
        results.append(alert)
    # win_rate = fraction of symbols that triggered an alert
    win_rate = sum(results) / len(results) if results else 0
    return win_rate

def main():
    cfg = load_config()
    # définir les plages à tester
    rsi_range      = [7, 14, 21]
    ema_ranges     = [(10,20), (20,50), (50,100)]
    bb_windows     = [10, 20, 30]
    bb_stds        = [1.0, 2.0, 3.0]

    combos = list(itertools.product(rsi_range, ema_ranges, bb_windows, bb_stds))
    print(f"Testing {len(combos)} parameter combinations…\n")

    records = []
    for (rsi, ema_pair, bb_w, bb_s) in combos:
        win_rate = evaluate_params(cfg, rsi, ema_pair, bb_w, bb_s)
        records.append({
            "rsi": rsi,
            "ema_short": ema_pair[0],
            "ema_long":  ema_pair[1],
            "bb_window": bb_w,
            "bb_std":    bb_s,
            "win_rate":  win_rate
        })
        print(f"RSI={rsi}, EMA={ema_pair}, BB=({bb_w},{bb_s}) → win_rate={win_rate:.2%}")

    # créer DataFrame et trier
    df = pd.DataFrame(records)
    df = df.sort_values("win_rate", ascending=False).reset_index(drop=True)

    # afficher top 10
    print("\n=== Top 10 combinations by win_rate ===")
    print(df.head(10).to_string(index=False))

    # sauvegarder résultats
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_csv = f"data/opt_results_{ts}.csv"
    df.to_csv(out_csv, index=False)
    print(f"\nResults saved to {out_csv}")

if __name__ == "__main__":
    main()
