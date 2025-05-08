import os
import pandas as pd
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries

# Récupérer la clé API Alpha Vantage depuis l'environnement (optionnel si vous n'utilisez pas 'alpha' comme source)
ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY', None)
# Si vous souhaitez forcer yfinance par défaut et éviter que l'absence de clé bloque l'app, commentez la levée d'erreur :
if not ALPHA_VANTAGE_KEY:
    print("Warning: Alpha Vantage API key not set. 'alpha' source will be unavailable, using yfinance only.")
    # raise EnvironmentError("Alpha Vantage API key not set. Please define ALPHA_VANTAGE_KEY environment variable.")("Alpha Vantage API key not set. Please define ALPHA_VANTAGE_KEY environment variable.")


def get_ohlcv_yfinance(symbol: str, timeframe: str) -> pd.DataFrame:
    """
    Récupère les données OHLCV via yfinance.
    timeframe: '1m','5m','15m','1h','1d', etc.
    """
    ticker = yf.Ticker(symbol)
    df = ticker.history(period='7d', interval=timeframe)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    df.columns = ['open', 'high', 'low', 'close', 'volume']
    df.dropna(inplace=True)
    return df


def get_ohlcv_alpha_vantage(symbol: str, timeframe: str) -> pd.DataFrame:
    """
    Récupère les données OHLCV via Alpha Vantage.
    timeframe: '1min','5min','15min','60min','Daily'
    """
    ts = TimeSeries(key=ALPHA_VANTAGE_KEY, output_format='pandas')
    # Choix de la fonction selon l'intervalle
    if timeframe in ['1min','5min','15min','60min']:
        df, _ = ts.get_intraday(symbol=symbol, interval=timeframe, outputsize='compact')
    elif timeframe == 'Daily':
        df, _ = ts.get_daily(symbol=symbol, outputsize='compact')
    else:
        raise ValueError(f"Invalid timeframe for Alpha Vantage: {timeframe}")

    df = df.rename(columns={
        '1. open':'open', '2. high':'high', '3. low':'low', '4. close':'close', '5. volume':'volume'
    })
    df.dropna(inplace=True)
    return df


def get_ohlcv(symbol: str, timeframe: str = '1h', source: str = 'yfinance') -> pd.DataFrame:
    """
    Wrapper pour récupérer OHLCV depuis yfinance ou Alpha Vantage.
    - symbol: ticker (ex. 'EURUSD=X' pour Forex, 'BTC-USD' pour crypto)
    - timeframe: intervalle
    - source: 'yfinance' ou 'alpha'

    Retourne un DataFrame avec colonnes ['open','high','low','close','volume'] indexé en datetime.
    """
    if source not in ('yfinance','alpha'):
        raise ValueError(f"Source inconnue: {source}")
    if source == 'alpha':
        return get_ohlcv_alpha_vantage(symbol, timeframe)
    return get_ohlcv_yfinance(symbol, timeframe)
