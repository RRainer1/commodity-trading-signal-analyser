import pandas as pd
import numpy as np

# Computes technical indicators and trading signals for stocks/commodities
class Analyse_patterns:
    def __init__(self, prices: pd.DataFrame):
        df = prices.sort_values("date").copy()
        df = df.set_index("date")
        self.prices = df
        self.returns = df["close"].pct_change()

    def moving_average(self, window: int) -> pd.DataFrame:
        #changes what column says depending on how many days moving average is used
        amountOfDays = f"movingAverage_{window}"
        self.prices[amountOfDays] = self.prices["close"].rolling(window).mean()
        return self.prices


    def relative_strength_index(self, window: int) -> pd.DataFrame:
        change = self.prices["close"].diff()
        change_up = change.copy()
        change_down = change.copy()
        change_up[change_up < 0] = 0
        change_down[change_down > 0] = 0
        avg_gain = change_up.rolling(window, min_periods=window).mean()
        avg_loss = change_down.rolling(window, min_periods=window).mean().abs()

        rsiStep1 = 100 - (100/(1+(avg_gain/avg_loss)))

        ## Using wilders moving average
        for i in range(window, len(self.prices)):
                if i == window:
                    continue

                avg_gain.iloc[i] = (avg_gain.iloc[i - 1] * (window - 1) + change_up.iloc[i]) / window
                avg_loss.iloc[i] = (avg_loss.iloc[i - 1] * (window - 1) + abs(change_down.iloc[i])) / window

        rsiStep2 = 100 - (100/(1+(avg_gain/avg_loss)))
        self.prices[f"rsi_{window}"] = rsiStep2
        return self.prices


    def logReturn_rollingVolatility(self, window: int) -> pd.DataFrame:
        self.prices["log_return"] = np.log(self.prices["close"] / self.prices["close"].shift(1))
        ##rolling volatility
        vol_col = f"volatility_{window}"
        self.prices[vol_col] = self.prices["log_return"].rolling(window).std()
        ##annual volatility
        ann_vol_col = f"annualized_vol_{window}"
        self.prices[ann_vol_col] = self.prices[vol_col] * np.sqrt(252)
        return self.prices

    def annualised_Returns(self,start_date=None) -> float:

        if "log_return" not in self.prices.columns:
            self.prices["log_return"] = np.log(self.prices["close"] / self.prices["close"].shift(1))

        r = self.prices["log_return"].dropna()

        if start_date is not None:
            r = r.loc[r.index >= start_date]


        compounded_growth = (1 + r).prod()
        n_periods = len(r)

        if n_periods == 0:
            return float("0 error")


        annual_return = compounded_growth ** (252 / n_periods) - 1
        return annual_return

    def raw_sharpe_ratio(self,start_date=None) ->float:

        if "log_return" not in self.prices.columns:
            self.prices["log_return"] = np.log(self.prices["close"] / self.prices["close"].shift(1))

        r = self.prices["log_return"].dropna()

        if start_date is not None:
            r = r.loc[r.index >= start_date]

        compounded_growth = (1 + r).prod()
        n_periods = len(r)
        if n_periods == 0:
            return float("0 error")
        annual_return = compounded_growth ** (252 / n_periods) - 1
        ann_vol = r.std() * np.sqrt(252)

        return annual_return / ann_vol

    def cross_Over_Points(self) -> pd.DataFrame:
        self.prices["crossover_state"] = np.where(
            self.prices["movingAverage_20"] > self.prices["movingAverage_50"], 1, 0
        )
        self.prices["signal"] = self.prices["crossover_state"].diff()
        return self.prices


    def average_true_range(self, period: int = 14) -> pd.DataFrame:
        high = self.prices["high"]
        low = self.prices["low"]
        close = self.prices["close"]
        prev_close = close.shift(1)
        true_range = pd.concat([
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs()
        ], axis=1).max(axis=1)
        self.prices[f"atr_{period}"] = true_range.rolling(period, min_periods=period).mean()
        return self.prices


    def atr_regime_signal(self, atr_period: int = 14, regime_window: int = 50, calm_threshold: float = 0.8) -> pd.DataFrame:
        atr_col = f"atr_{atr_period}"
        if atr_col not in self.prices.columns:
            self.average_true_range(atr_period)

        # make sure moving averages exist
        if "movingAverage_20" not in self.prices.columns:
            self.moving_average(20)
        if "movingAverage_50" not in self.prices.columns:
            self.moving_average(50)

        atr = self.prices[atr_col]
        atr_mean = atr.rolling(regime_window, min_periods=regime_window).mean()

        calm = atr < (calm_threshold * atr_mean)


        close = self.prices["close"]
        ma20 = self.prices["movingAverage_20"]
        ma50 = self.prices["movingAverage_50"]

        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]
        if isinstance(ma20, pd.DataFrame):
            ma20 = ma20.iloc[:, 0]
        if isinstance(ma50, pd.DataFrame):
            ma50 = ma50.iloc[:, 0]


        uptrend = (close > ma20) & (ma20 > ma50)

        self.prices["atr_let_run"] = (calm & uptrend).astype(int)
        return self.prices
