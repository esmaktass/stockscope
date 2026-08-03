import pandas as pd
import streamlit as st

from charts import (
    create_candlestick_chart,
    create_price_chart,
    create_volume_chart,
)
from data import get_stock_data
from indicators import calculate_indicators


st.set_page_config(
    page_title="StockScope",
    page_icon="📈",
    layout="wide",
)

st.title("📈 StockScope")
st.caption(
    "Explore historical prices, moving averages "
    "and trading volume through an interactive dashboard."
)

ticker = st.text_input(
    "Ticker Symbol",
    value="AAPL",
)

period = st.selectbox(
    "Analysis Period",
    options=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
    index=2,
)

chart_type = st.selectbox(
    "Chart Type",
    options=["Line", "Candlestick"],
)

analyze_button = st.button(
    "Analyze Stock",
    type="primary",
    width="stretch",
)

if analyze_button:
    clean_ticker = ticker.strip().upper()

    with st.spinner("Loading market data..."):
        data = get_stock_data(clean_ticker, period)

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

    ma20_display = (
        f"{latest_ma20:.2f}"
        if pd.notna(latest_ma20)
        else "Not enough data"
    )

    ma50_display = (
        f"{latest_ma50:.2f}"
        if pd.notna(latest_ma50)
        else "Not enough data"
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Current Price",
        f"{current_price:.2f}",
        f"{daily_change_percent:.2f}%",
    )

    col2.metric(
        "Daily Change",
        f"{daily_change:.2f}",
    )

    col3.metric(
        "MA20",
        ma20_display,
    )

    col4.metric(
        "MA50",
        ma50_display,
    )

    if chart_type == "Candlestick":
        price_chart = create_candlestick_chart(
            data,
            clean_ticker,
        )
    else:
        price_chart = create_price_chart(
            data,
            clean_ticker,
        )

    st.plotly_chart(
        price_chart,
        use_container_width=True,
    )

    volume_chart = create_volume_chart(
        data,
        clean_ticker,
    )

    st.plotly_chart(
        volume_chart,
        use_container_width=True,
    )