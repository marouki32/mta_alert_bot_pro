import pandas as pd
import pytest
from analysis.strategy_scoring import score_strategy, DEFAULT_WEIGHTS

@pytest.fixture
def flat_df():
    # DataFrame minimal avec colonnes nécessaires
    return pd.DataFrame({
        'rsi': [50,50,50],
        'ema_20': [1,1,1],
        'bb_upper': [1,1,1],
        'bb_lower': [1,1,1]
    })

def test_score_no_patterns(flat_df):
    patterns = {k: False for k in DEFAULT_WEIGHTS.keys()}
    score = score_strategy(flat_df, patterns)
    assert score == pytest.approx(0.0)

def test_score_simple_pattern(flat_df):
    # un seul pattern bullish_engulfing à True
    patterns = {k: False for k in DEFAULT_WEIGHTS.keys()}
    patterns['bullish_engulfing'] = True
    score = score_strategy(flat_df, patterns)
    assert score == pytest.approx(DEFAULT_WEIGHTS['bullish_engulfing'])
