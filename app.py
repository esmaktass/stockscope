import streamlit as st

from data import get_stock_data
from indicators import calculate_indicators
from charts import create_price_chart


st.set_page_config(
    page_title="StockScope",
    page_icon="📈",
    layout="wide"
)

st.title("StockScope")
st.caption("Interactive stock market analysis dashboard")

ticker = st.text_input(
    "Ticker Symbol",
    value="AAPL"
)

analyze_button = st.button("Analyze Stock")

if analyze_button:
    clean_ticker = ticker.strip().upper()

    with st.spinner("Loading market data..."):
        data = get_stock_data(clean_ticker)

    if data is None:
        st.error(
            "No valid market data was found. "
            "Check the ticker symbol and try again."
        )
        st.stop()

    data = calculate_indicators(data)

    current_price = data["Close"].iloc[-1]
    previous_price = data["Close"].iloc[-2]

    daily_change = current_price - previous_price
    daily_change_percent = (
        daily_change / previous_price
    ) * 100

    latest_ma20 = data["MA20"].iloc[-1]
    latest_ma50 = data["MA50"].iloc[-1]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Current Price",
        f"{current_price:.2f}",
        f"{daily_change_percent:.2f}%"
    )

    col2.metric(
        "Daily Change",
        f"{daily_change:.2f}"
    )

    col3.metric(
        "MA20",
        f"{latest_ma20:.2f}"
    )

    col4.metric(
        "MA50",
        f"{latest_ma50:.2f}"
    )

    price_chart = create_price_chart(
        data,
        clean_ticker
    )

    st.plotly_chart(
        price_chart,
        use_container_width=True
    )