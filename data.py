import yfinance as yf
import streamlit as st

@st.cache_data(ttl=900)
def get_stock_data(ticker: str, period: str = "6mo"):
    ticker = ticker.strip().upper()

    stock = yf.Ticker(ticker)
    data = stock.history(period=period)

    if data.empty:
        return None

    data = data.dropna(subset=["Close"]).copy()

    if len(data) < 2:
        return None

    return data

@st.cache_data(ttl=3600)
def get_company_info(ticker: str):
    ticker = ticker.strip().upper()

    stock = yf.Ticker(ticker)

    try:
        info = stock.info
    except Exception:
        return {}

    return {
        "name": info.get("longName") or info.get("shortName") or ticker,
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "currency": info.get("currency"),
        "market_cap": info.get("marketCap"),
        "trailing_pe": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "eps": info.get("trailingEps"),
        "beta": info.get("beta"),
        "dividend_yield": info.get("dividendYield"),
        "website": info.get("website"),
    }