import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf


TRADING_DAYS_PER_YEAR = 252


@st.cache_data(ttl=900)
def get_comparison_data(
    tickers: tuple[str, ...],
    period: str,
) -> pd.DataFrame | None:
    clean_tickers = [
        ticker.strip().upper()
        for ticker in tickers
        if ticker.strip()
    ]

    if len(clean_tickers) < 2:
        return None

    downloaded_data = yf.download(
        tickers=clean_tickers,
        period=period,
        auto_adjust=False,
        progress=False,
        group_by="column",
    )

    if downloaded_data.empty:
        return None

    try:
        close_prices = downloaded_data["Close"].copy()
    except KeyError:
        return None

    if isinstance(close_prices, pd.Series):
        close_prices = close_prices.to_frame(
            name=clean_tickers[0]
        )

    close_prices = close_prices.dropna(
        axis=1,
        how="all",
    )

    close_prices = close_prices.ffill().dropna(
        axis=0,
        how="all",
    )

    if close_prices.shape[1] < 2:
        return None

    return close_prices


def normalize_prices(
    close_prices: pd.DataFrame,
) -> pd.DataFrame:
    normalized = close_prices.copy()

    for ticker in normalized.columns:
        valid_prices = normalized[ticker].dropna()

        if valid_prices.empty:
            normalized[ticker] = np.nan
            continue

        first_price = valid_prices.iloc[0]

        normalized[ticker] = (
            normalized[ticker] / first_price
        ) * 100

    return normalized


def calculate_comparison_metrics(
    close_prices: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    for ticker in close_prices.columns:
        prices = close_prices[ticker].dropna()

        if len(prices) < 2:
            continue

        total_return = (
            prices.iloc[-1] / prices.iloc[0] - 1
        ) * 100

        daily_returns = prices.pct_change().dropna()

        annualized_volatility = (
            daily_returns.std()
            * np.sqrt(TRADING_DAYS_PER_YEAR)
            * 100
        )

        rows.append(
            {
                "Ticker": ticker,
                "Start Price": prices.iloc[0],
                "Current Price": prices.iloc[-1],
                "Return (%)": total_return,
                "Volatility (%)": annualized_volatility,
            }
        )

    if not rows:
        return pd.DataFrame()

    metrics = pd.DataFrame(rows)

    return metrics.sort_values(
        by="Return (%)",
        ascending=False,
    ).reset_index(drop=True)


def create_comparison_chart(
    normalized_prices: pd.DataFrame,
) -> go.Figure:
    fig = go.Figure()

    for ticker in normalized_prices.columns:
        fig.add_trace(
            go.Scatter(
                x=normalized_prices.index,
                y=normalized_prices[ticker],
                mode="lines",
                name=ticker,
            )
        )

    fig.add_hline(
        y=100,
        line_dash="dash",
        annotation_text="Starting level",
    )

    fig.update_layout(
        title="Normalized Stock Performance",
        xaxis_title="Date",
        yaxis_title="Normalized value",
        hovermode="x unified",
        legend_title="Ticker",
    )

    return fig