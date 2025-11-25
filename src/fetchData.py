import yfinance as yf
import pandas as pd

class fetch_Data:
    def __init__(self):
        pass


    def getData(self, stock_symbol: str,start_date: str, end_date: str, interval: str = "1d",)-> pd.DataFrame:
      df = yf.download(tickers = [stock_symbol], start = start_date, end=end_date, interval=interval,  auto_adjust = True)
      df = df.reset_index()
      df = df.rename(columns=str.lower)
      return df[["date", "open", "high", "low", "close", "volume"]]


