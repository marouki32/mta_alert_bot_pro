import pandas as pd
import numpy as np

def compute_performance(returns: pd.Series):
    """
    À partir d'une série de % changes (returns), calcule :
     - equity curve
     - drawdown
     - total_return, annual_return, annual_vol, sharpe, max_drawdown
    """
    # 1) Equity curve
    equity = (1 + returns).cumprod()

    # 2) Drawdown
    running_max = equity.cummax()
    drawdown = (equity / running_max) - 1

    # 3) Metrics
    total_return  = equity.iloc[-1] - 1
    # annualisation sur 252 périodes
    annual_return = equity.iloc[-1] ** (252 / len(returns)) - 1  
    annual_vol    = returns.std() * np.sqrt(252)
    sharpe        = annual_return / annual_vol if annual_vol else np.nan
    max_dd        = drawdown.min()

    stats = {
        "total_return":  total_return,
        "annual_return": annual_return,
        "annual_vol":    annual_vol,
        "sharpe":        sharpe,
        "max_drawdown":  max_dd
    }

    # DataFrame pour tracés
    df = pd.DataFrame({
        "equity":   equity,
        "drawdown": drawdown
    })

    return df, stats
