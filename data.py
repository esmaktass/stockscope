import yfinance as yf


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