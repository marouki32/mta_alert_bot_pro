import pandas as pd
import numpy as np
import pytest

from analysis.technical_analysis import compute_indicators, detect_patterns

@pytest.fixture
def sample_df():
    # 5 barres de prix factices
    data = {
        'open':   [1.0, 1.1, 1.2, 1.1, 1.0],
        'high':   [1.1, 1.2, 1.3, 1.2, 1.1],
        'low':    [0.9, 1.0, 1.1, 1.0, 0.9],
        'close':  [1.05,1.15,1.25,1.05,0.95],
        'volume': [10,  10,   10,   10,   10]
    }
    df = pd.DataFrame(data)
    return df

def test_compute_indicators_dimensions(sample_df):
    params = {'rsi': 2, 'ema': [2,3], 'bollinger': {'window': 2, 'std':1}}
    out = compute_indicators(sample_df, params)
    # on perd (window, rsi) lignes initiales => len doit être >=1
    assert 'rsi' in out.columns
    assert 'ema_2' in out.columns and 'ema_3' in out.columns
    assert all(col in out.columns for col in ['bb_mid','bb_upper','bb_lower'])

def test_detect_patterns_no_pattern(sample_df):
    # Sur cet exemple aucun pattern ne doit être True
    df = compute_indicators(sample_df, {'rsi':2,'ema':[],'bollinger':{'window':2,'std':1}})
    patterns = detect_patterns(df)
    # tous doivent être False ou bool
    for k,v in patterns.items():
        assert isinstance(v, (bool, np.bool_))
    assert not any(patterns.values())

def test_detect_patterns_known_hammer():
    # Construire un marteau : long lower shadow
    df = pd.DataFrame({
        'open':[2,2,2],
        'high':[2.1,2.1,2.1],
        'low':[1.0,2.0,1.0],
        'close':[2.05,2.05,2.05],
        'volume':[1,1,1]
    })
    params={'rsi':2,'ema':[],'bollinger':{'window':2,'std':1}}
    df2=compute_indicators(df,params)
    pats=detect_patterns(df2)
    assert pats['hammer']==True
