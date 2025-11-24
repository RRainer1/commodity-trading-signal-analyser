from fontTools.misc.plistlib import end_date

from fetchData import fetch_Data
from analytics import Analyse_patterns
import matplotlib.pyplot as plt

Commodity_symbols = ["CL=F", "NG=F", "GC=F"]

graph_Start = "2024-07-01"
data_Start = "2024-03-01"
data_End = "2025-01-15"



def symbol_analysis(symbol: str) -> None:
    fd = fetch_Data()
    df = fd.getData(stock_symbol=symbol, start_date=data_Start, end_date=data_End)
    analyser = Analyse_patterns(df)

    analyser.moving_average(20)
    analyser.moving_average(50)
    analyser.cross_Over_Points()
    analyser.relative_strength_index(14)
    analyser.logReturn_rollingVolatility(20)
    ##only calculated from data on graph timeframe
    annual_return = analyser.annualised_Returns(start_date=graph_Start)
    sharpe = analyser.raw_sharpe_ratio(start_date=graph_Start)
    analyser.average_true_range(14)
    analyser.atr_regime_signal(atr_period=14, regime_window=50, calm_threshold=0.8)

    ##data stats being plotted from graph_start
    visible = analyser.prices.loc[analyser.prices.index >= graph_Start]

    print(analyser.prices[
              ["close", "movingAverage_20", "movingAverage_50", "rsi_14", "volatility_20", "annualized_vol_20"]].tail())

    fig, axes = plt.subplots(4, 1, figsize=(10, 12), sharex=True)

    visible["rsi_14"].plot(ax=axes[0], color="purple")
    axes[0].set_title("RSI 14")
    # If over 70 stock could be considered overbought
    axes[0].axhline(70, color="red", linestyle="--", alpha=0.5)
    ##if under 30 stock could be considered underbought
    axes[0].axhline(30, color="green", linestyle="--", alpha=0.5)
    axes[0].set_ylabel("RSI")

    visible["volatility_20"].plot(ax=axes[1], color="orange")
    axes[1].set_title("20-Day Rolling Volatility")
    axes[1].set_ylabel("Volatility")

    visible[["close", "movingAverage_20", "movingAverage_50"]].plot(ax=axes[2], color=["blue", "orange", "green"])

    axes[2].plot(visible[visible["signal"] == 1].index, visible["movingAverage_20"][visible["signal"] == 1], '^',
                 markersize=9, color='green', label="20MA>50MA - buy signal")

    axes[2].plot(visible[visible["signal"] == -1].index, visible["movingAverage_50"][visible["signal"] == -1], 'v',
                 markersize=9, color='red', label="20MA<50MA - sell signal")

    axes[2].set_title(f"{symbol} Close vs 20-Day Moving Average")
    axes[2].set_ylabel("Price $")
    axes[2].set_xlabel("Date")

    hold_mask = visible["atr_let_run"] == 1

    regime_change = visible["atr_let_run"].diff().fillna(0)
    regime_start = regime_change == 1
    regime_end = regime_change == -1

    print("ATR regime counts:")
    print(visible["atr_let_run"].value_counts(dropna=False))

    axes[2].plot(visible.index[regime_start], visible["close"][regime_start] * 0.995, '^', markersize=9,
                 color='darkblue', linestyle='none', label="Let profits run (ATR low)", )

    axes[2].plot(visible.index[regime_end], visible["close"][regime_end] * 0.995, 'v', markersize=9, color='darkred',
                 linestyle='none', label="End of low volatility uptrend (ATR high)", )

    axes[2].legend(loc="upper left", bbox_to_anchor=(1.02, 1), fontsize=12, markerscale=1.2)

    visible["atr_14"].plot(ax=axes[3], color="blue")
    axes[3].set_title("ATR 14")
    axes[3].set_ylabel("ATR")
    axes[3].set_xlabel("Date")

    plt.tight_layout()
    plt.show()

    print(f"Annualised Return: {annual_return:.4f}")
    print(f"Sharpe Ratio: {sharpe:.4f}")








def main ():
    for symbol in Commodity_symbols:
        print(f"\n --- Running analysis for {symbol} --- ")
        symbol_analysis(symbol)




if __name__ == "__main__":
    main()

