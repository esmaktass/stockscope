# StockScope

StockScope is a stock market dashboard built with Python.

## Screenshot

![StockScope Dashboard](assets/dashboard.png)

## Features

- Fetch stock data using Yahoo Finance API
- Display latest closing price
- Calculate daily price change
- Calculate daily percentage change
- Historical stock data
- Interactive Plotly charts
- Moving Average (20)
- Moving Average (50) 
- Selectable analysis period
- Responsive Streamlit dashboard
- Fetch historical stock market data
- Display the latest closing price
- Calculate daily price and percentage changes
- Visualize prices with interactive Plotly charts
- Switch between line and candlestick charts
- Display trading volume
- Calculate 20-day moving average
- Calculate 50-day moving average
- Select the analysis period
- Cache repeated market data requests
- Use a responsive Streamlit dashboard
- Display company name, sector and industry
- Show market capitalization, P/E, EPS, beta and dividend yield
- Display ticker currency in price metrics
- Visualize Bollinger Bands
- Calculate MACD, signal line and histogram
- Compare up to five stocks in one dashboard
- Normalize prices for relative performance analysis
- Calculate total return and annualized volatility
- Identify the best-performing stock
- Generate explainable rule-based technical market summaries
- Classify the technical outlook as bullish, bearish or neutral
- Display annual income statements, balance sheets and cash flow statements
- Visualize revenue, net income and cash flow trends
- Calculate annual revenue and net income growth
- Summarize revenue, assets, debt and free cash flow

## Technologies

- Python
- Pandas
- yfinance

## Installation

git clone https://github.com/esmaktass/stockscope.git
cd stockscope

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py

## Project Structure

stockscope/
├── app.py
├── charts.py
├── comparison.py
├── data.py
├── financials.py
├── indicators.py
├── insights.py
├── requirements.txt
├── assets/
└── README.md
