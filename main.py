import yfinance as yf
import plotly.graph_objects as go


def create_price_chart(data, ticker):
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["Close"],
            mode="lines",
            name="Close Price"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["MA20"],
            mode="lines",
            name="MA20"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["MA50"],
            mode="lines",
            name="MA50"
        )
    )

    fig.update_layout(
        title=f"{ticker} Price Analysis",
        xaxis_title="Date",
        yaxis_title="Price",
        hovermode="x unified"
    )

    return fig


while True:
    hisse = input("Hisse kodunu giriniz: ")
    ticker = hisse.strip().upper()

    stock = yf.Ticker(ticker)
    data = stock.history(period="6mo")

    if data.empty:
        print(
            "Bu hisse kodu bulunamadı. "
            "Lütfen kodu kontrol edip tekrar deneyin."
        )
        continue

    # Close değeri eksik olan satırları tamamen kaldır.
    data = data.dropna(subset=["Close"]).copy()

    if len(data) < 2:
        print(
            "Günlük değişimi hesaplamak için yeterli veri bulunamadı. "
            "Lütfen başka bir hisse kodu deneyin."
        )
        continue

    # Hareketli ortalamaları temizlenmiş veri üzerinden hesapla.
    data["MA20"] = data["Close"].rolling(window=20).mean()
    data["MA50"] = data["Close"].rolling(window=50).mean()

    current_price = data["Close"].iloc[-1]
    previous_price = data["Close"].iloc[-2]

    daily_change = current_price - previous_price
    daily_change_percent = (
        daily_change / previous_price
    ) * 100

    latest_ma20 = data["MA20"].iloc[-1]
    latest_ma50 = data["MA50"].iloc[-1]

    print(data[["Close", "MA20", "MA50"]].tail())

    print(f"\nHisse kodu: {ticker}")
    print(f"Son kapanış fiyatı: {current_price:.2f}")
    print(f"Önceki kapanış fiyatı: {previous_price:.2f}")
    print(f"Günlük fiyat değişimi: {daily_change:.2f}")
    print(f"Günlük değişim: {daily_change_percent:.2f}%")
    print(f"20 günlük hareketli ortalama: {latest_ma20:.2f}")
    print(f"50 günlük hareketli ortalama: {latest_ma50:.2f}")

    price_chart = create_price_chart(data, ticker)

    price_chart.write_html(
        "stockscope_chart.html",
        auto_open=True
    )

    break