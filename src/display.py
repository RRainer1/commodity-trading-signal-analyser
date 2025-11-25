import streamlit as st
import main


def app():
    st.set_page_config( page_title="Commodity Trading Signal Analyser",layout="wide",)

    st.title("📈 Commodity Trading Signal Analyser")
    st.write(
        "Enter a futures or stock ticker to see moving-average crossovers, RSI, "
        "rolling volatility, ATR and an ATR-based 'let profits run' regime."
    )

    st.sidebar.header("Inputs")

    symbol = st.sidebar.text_input("Ticker", value="CL=F", help="Examples: CL=F (Crude Oil), NG=F (NatGas), GC=F (Gold), NVDA, AAPL, etc.",)

    data_start = st.sidebar.text_input("Data start (YYYY-MM-DD)", value=main.data_Start)
    graph_start = st.sidebar.text_input("Graph start (YYYY-MM-DD)", value=main.graph_Start)
    data_end = st.sidebar.text_input("Data end (YYYY-MM-DD)", value=main.data_End)

    atr_threshold = st.sidebar.slider("ATR calm-regime threshold",min_value=0.5,max_value=1.0,value=0.8,step=0.05,)

    if st.sidebar.button("Run analysis"):
        main.data_Start = data_start
        main.graph_Start = graph_start
        main.data_End = data_end

        try:
            fig, annual_return, sharpe = main.symbol_analysis(symbol, atr_threshold=atr_threshold, show_plot=False)
        except Exception as e:
            st.error(f"Error running analysis for {symbol}: {e}")
            return

        st.pyplot(fig)
        st.subheader("Risk / return snapshot")
        st.write(f"**Annualised Return (from {graph_start}):** {annual_return:.2%}")
        st.write(f"**Sharpe Ratio (from {graph_start}):** {sharpe:.2f}")
    else:
        st.info("Set your inputs on the left and click **Run analysis**.")


if __name__ == "__main__":
    app()
