# analysis/paper_trading.py

import pandas as pd
from datetime import datetime
from analysis.technical_analysis import detect_patterns
from analysis.strategy_scoring import score_strategy

class Portfolio:
    def __init__(self, initial_cash: float = 100000.0):
        self.cash        = initial_cash
        self.position    = 0.0
        self.entry_price = None
        self.history     = []  # liste de dicts

    def buy(self, price: float, timestamp):
        """Ouvre une position full cash → qty = cash/price."""
        qty  = self.cash / price
        cost = qty * price
        self.cash         -= cost
        self.position     += qty
        self.entry_price  = price
        self.history.append({
            'action':    'BUY',
            'timestamp': timestamp,
            'price':     price,
            'qty':       qty,
            'cash':      self.cash
        })

    def sell(self, price: float, timestamp):
        """Clôture toute position."""
        qty      = self.position
        proceeds = qty * price
        pnl      = (price - self.entry_price) * qty if self.entry_price is not None else 0.0
        self.cash     += proceeds
        self.position  = 0.0
        self.history.append({
            'action':    'SELL',
            'timestamp': timestamp,
            'price':     price,
            'qty':       qty,
            'cash':      self.cash,
            'pnl':       pnl
        })
        self.entry_price = None

    def record_equity(self, timestamp, price: float):
        """Ajoute un point equity = cash + position*price."""
        eq = self.cash + self.position * price
        self.history.append({
            'action':    'EQUITY',
            'timestamp': timestamp,
            'equity':    eq
        })

    def to_dataframe(self) -> pd.DataFrame:
        """Retourne l’historique sous forme de DataFrame."""
        return pd.DataFrame(self.history)


def run_paper_trading(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Simule du paper-trading spot :
     - BUY dès que score >= threshold et on est à découvert
     - SELL dès que score < threshold et on est long
     - Enregistre equity à chaque bougie
    Retourne un DataFrame avec colonnes [action, timestamp, price?, qty?, cash, pnl?, equity?].
    """
    # 1) Initialisation
    initial_cash = config.get('paper_initial_cash', 100000.0)
    thr          = config['alerts']['score_threshold']
    port         = Portfolio(initial_cash=initial_cash)

    # 2) Boucle sur chaque bougie
    for timestamp, row in df.iterrows():
        price = row.get('close', None)
        if price is None:
            continue

        # Calcul du score up-to-date
        try:
            patterns = detect_patterns(df.loc[:timestamp])
            score    = score_strategy(df.loc[:timestamp], patterns)
        except Exception as e:
            # En cas d’erreur, on skip cette bougie
            port.record_equity(timestamp, price)
            continue

        # Signal BUY / SELL
        if score >= thr and port.position == 0:
            port.buy(price, timestamp)
        elif score < thr and port.position > 0:
            port.sell(price, timestamp)

        # Toujours enregistrer equity
        port.record_equity(timestamp, price)

    # 3) Retour
    return port.to_dataframe()
