import pandas as pd
import streamlit as st

from charts import (
    create_bollinger_chart,
    create_candlestick_chart,
    create_macd_chart,
    create_price_chart,
    create_rsi_chart,
    create_volume_chart,
)
from comparison import (
    calculate_comparison_metrics,
    create_comparison_chart,
    get_comparison_data,
    normalize_prices,
)
from data import get_company_info, get_stock_data
from indicators import calculate_indicators
from insights import build_market_insights
from financials import render_financial_analysis


def format_large_number(value):
    if value is None or pd.isna(value):
        return "N/A"

    if value >= 1_000_000_000_000:
        return f"{value / 1_000_000_000_000:.2f}T"

    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"

    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"

    return f"{value:,.0f}"


def format_number(value):
    if value is None or pd.isna(value):
        return "N/A"

    return f"{value:.2f}"


def format_dividend_yield(value):
    if value is None or pd.isna(value):
        return "N/A"

    if value < 0.1:
        value *= 100

    return f"{value:.2f}%"


def render_market_insights(market_insights):
    st.subheader("Technical Market Summary")

    insight_label = market_insights["label"]
    insight_score = market_insights["score"]
    insight_status = market_insights["status"]

    summary_text = (
        f"**Overall outlook:** {insight_label}  \n"
        f"**Technical score:** {insight_score:+d}"
    )

    if insight_status == "positive":
        st.success(
            summary_text,
            icon="📈",
        )
    elif insight_status == "negative":
        st.warning(
            summary_text,
            icon="📉",
        )
    else:
        st.info(
            summary_text,
            icon="ℹ️",
        )

    for message in market_insights["messages"]:
        st.markdown(f"- {message}")

    st.caption(
        "This summary is generated from technical rules "
        "and does not constitute investment advice."
    )


def render_single_stock_analysis():
    ticker = st.text_input(
        "Ticker Symbol",
        value="AAPL",
        key="single_ticker",
    )

    period = st.selectbox(
        "Analysis Period",
        options=[
            "1mo",
            "3mo",
            "6mo",
            "1y",
            "2y",
            "5y",
        ],
        index=2,
        key="single_period",
    )

    chart_type = st.selectbox(
        "Chart Type",
        options=[
            "Line",
            "Candlestick",
        ],
        key="single_chart_type",
    )

    analyze_button = st.button(
        "Analyze Stock",
        type="primary",
        width="stretch",
        key="single_analyze",
    )

    if not analyze_button:
        return

    clean_ticker = ticker.strip().upper()

    if not clean_ticker:
        st.error("Please enter a ticker symbol.")
        return

    with st.spinner("Loading market data..."):
        data = get_stock_data(
            clean_ticker,
            period,
        )
        company_info = get_company_info(
            clean_ticker
        )

    if data is None:
        st.error(
            "No valid market data was found. "
            "Check the ticker symbol and try again."
        )
        return

    if company_info is None:
        company_info = {}

    data = calculate_indicators(data)

    # İndikatörler hesaplandıktan sonra teknik yorumları üret.
    market_insights = build_market_insights(data)

    company_name = (
        company_info.get("name")
        or clean_ticker
    )
    sector = (
        company_info.get("sector")
        or "N/A"
    )
    industry = (
        company_info.get("industry")
        or "N/A"
    )
    currency = (
        company_info.get("currency")
        or ""
    )

    st.subheader(company_name)
    st.caption(
        f"{clean_ticker} · {sector} · {industry}"
    )

    current_price = data["Close"].iloc[-1]
    previous_price = data["Close"].iloc[-2]

    daily_change = (
        current_price - previous_price
    )
    daily_change_percent = (
        daily_change / previous_price
    ) * 100

    latest_ma20 = data["MA20"].iloc[-1]
    latest_ma50 = data["MA50"].iloc[-1]
    latest_rsi = data["RSI"].iloc[-1]

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

    rsi_display = (
        f"{latest_rsi:.2f}"
        if pd.notna(latest_rsi)
        else "Not enough data"
    )

    currency_suffix = (
        f" {currency}"
        if currency
        else ""
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Current Price",
        f"{current_price:.2f}{currency_suffix}",
        f"{daily_change_percent:.2f}%",
    )

    col2.metric(
        "Daily Change",
        f"{daily_change:.2f}{currency_suffix}",
    )

    col3.metric(
        "MA20",
        ma20_display,
    )

    col4.metric(
        "MA50",
        ma50_display,
    )

    col5.metric(
        "RSI (14)",
        rsi_display,
    )

    st.subheader("Company Fundamentals")

    fundamentals_columns = st.columns(5)

    fundamentals_columns[0].metric(
        "Market Cap",
        format_large_number(
            company_info.get("market_cap")
        ),
    )

    fundamentals_columns[1].metric(
        "Trailing P/E",
        format_number(
            company_info.get("trailing_pe")
        ),
    )

    fundamentals_columns[2].metric(
        "EPS",
        format_number(
            company_info.get("eps")
        ),
    )

    fundamentals_columns[3].metric(
        "Beta",
        format_number(
            company_info.get("beta")
        ),
    )

    fundamentals_columns[4].metric(
        "Dividend Yield",
        format_dividend_yield(
            company_info.get("dividend_yield")
        ),
    )

    # Şirket metriklerinden sonra teknik özet gösterilir.
    render_market_insights(market_insights)

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
        width="stretch",
    )

    st.plotly_chart(
        create_volume_chart(
            data,
            clean_ticker,
        ),
        width="stretch",
    )

    st.plotly_chart(
        create_rsi_chart(
            data,
            clean_ticker,
        ),
        width="stretch",
    )

    st.plotly_chart(
        create_bollinger_chart(
            data,
            clean_ticker,
        ),
        width="stretch",
    )

    st.plotly_chart(
        create_macd_chart(
            data,
            clean_ticker,
        ),
        width="stretch",
    )


def render_stock_comparison():
    st.subheader("Compare Stocks")

    ticker_input = st.text_input(
        "Ticker Symbols",
        value="AAPL, MSFT, NVDA",
        help=(
            "Enter at least two ticker symbols "
            "separated by commas."
        ),
        key="comparison_tickers",
    )

    comparison_period = st.selectbox(
        "Comparison Period",
        options=[
            "1mo",
            "3mo",
            "6mo",
            "1y",
            "2y",
            "5y",
        ],
        index=3,
        key="comparison_period",
    )

    compare_button = st.button(
        "Compare Stocks",
        type="primary",
        width="stretch",
        key="comparison_button",
    )

    if not compare_button:
        return

    tickers = tuple(
        ticker.strip().upper()
        for ticker in ticker_input.split(",")
        if ticker.strip()
    )

    unique_tickers = tuple(
        dict.fromkeys(tickers)
    )

    if len(unique_tickers) < 2:
        st.error(
            "Enter at least two different "
            "ticker symbols."
        )
        return

    if len(unique_tickers) > 5:
        st.error(
            "Compare a maximum of five stocks "
            "at the same time."
        )
        return

    with st.spinner(
        "Loading comparison data..."
    ):
        close_prices = get_comparison_data(
            unique_tickers,
            comparison_period,
        )

    if close_prices is None:
        st.error(
            "Comparison data could not be loaded. "
            "Check the ticker symbols."
        )
        return

    normalized_prices = normalize_prices(
        close_prices
    )

    metrics = calculate_comparison_metrics(
        close_prices
    )

    if metrics.empty:
        st.error(
            "There is not enough data to "
            "calculate comparison metrics."
        )
        return

    best_stock = metrics.iloc[0]

    best_col, return_col, risk_col = st.columns(3)

    best_col.metric(
        "Best Performer",
        best_stock["Ticker"],
    )

    return_col.metric(
        "Best Return",
        f"{best_stock['Return (%)']:.2f}%",
    )

    risk_col.metric(
        "Its Annualized Volatility",
        f"{best_stock['Volatility (%)']:.2f}%",
    )

    comparison_chart = create_comparison_chart(
        normalized_prices
    )

    st.plotly_chart(
        comparison_chart,
        width="stretch",
    )

    st.subheader("Performance Comparison")

    formatted_metrics = metrics.copy()

    formatted_metrics["Start Price"] = (
        formatted_metrics["Start Price"]
        .map(lambda value: f"{value:.2f}")
    )

    formatted_metrics["Current Price"] = (
        formatted_metrics["Current Price"]
        .map(lambda value: f"{value:.2f}")
    )

    formatted_metrics["Return (%)"] = (
        formatted_metrics["Return (%)"]
        .map(lambda value: f"{value:.2f}%")
    )

    formatted_metrics["Volatility (%)"] = (
        formatted_metrics["Volatility (%)"]
        .map(lambda value: f"{value:.2f}%")
    )

    st.dataframe(
        formatted_metrics,
        width="stretch",
        hide_index=True,
    )

    st.caption(
        "Normalized values begin at 100. "
        "Volatility is annualized using "
        "252 trading days."
    )


st.set_page_config(
    page_title="StockScope",
    page_icon="📈",
    layout="wide",
)

st.title("📈 StockScope")
st.caption(
    "Explore historical prices, moving averages, momentum, "
    "company fundamentals and comparative performance "
    "through an interactive dashboard."
)

(
    single_stock_tab,
    comparison_tab,
    financials_tab,
) = st.tabs(
    [
        "Single Stock Analysis",
        "Compare Stocks",
        "Financial Statements",
    ]
)

with single_stock_tab:
    render_single_stock_analysis()

with comparison_tab:
    render_stock_comparison()

with financials_tab:
    render_financial_analysis()