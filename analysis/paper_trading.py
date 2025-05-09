import pandas as pd

class Portfolio:
    def __init__(self, initial_cash=100000.0):
        self.cash = initial_cash
        self.position = 0.0       # quantité d’actif
        self.entry_price = None   # prix d’entrée de la position
        self.history = []         # liste de trades et equity

    def buy(self, price, qty=None):
        # si qty None, on investit tout le cash
        qty = qty or (self.cash / price)
        cost = qty * price
        if cost <= self.cash:
            self.cash -= cost
            self.position += qty
            self.entry_price = price
            self.history.append({'action':'buy','price':price,'qty':qty,'cash':self.cash})
        # sinon ignore

    def sell(self, price, qty=None):
        # si qty None, on vend tout
        qty = qty or self.position
        if qty <= self.position:
            proceeds = qty * price
            self.cash += proceeds
            self.position -= qty
            pnl = (price - self.entry_price) * qty if self.entry_price else 0
            self.history.append({'action':'sell','price':price,'qty':qty,'cash':self.cash,'pnl':pnl})
            if self.position==0:
                self.entry_price = None

    def equity(self, current_price):
        return self.cash + self.position * current_price

    def record_equity(self, timestamp, price):
        self.history.append({'action':'equity','timestamp':timestamp,'equity':self.equity(price)})

    def to_dataframe(self):
        return pd.DataFrame(self.history)
