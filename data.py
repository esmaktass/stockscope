import yfinance as yf

while True:
    hisse = input("Hisse kodunu giriniz: ")
    ticker = hisse.strip().upper()
    stock = yf.Ticker(ticker)
    data = stock.history(period="6mo")

    if data.empty :
        print("Bu hisse kodu bulunamadı. Lütfen kodu kontrol edip tekrar deneyin.")
        continue

    close_prices = data["Close"].dropna()

    if len(close_prices) < 2:
        print("Yeterli veri bulunamadı. Lütfen başka bir hisse kodu deneyin.")
        continue

    else :
        current_price = close_prices.iloc[-1]
        previous_price = close_prices.iloc[-2]
        daily_change = current_price - previous_price
        daily_change_percent = (daily_change/previous_price)*100
        print(f"Hisse kodu: {ticker}")
        print(f"Son kapanış fiyatı: {current_price:.2f}")
        print(f"Önceki kapanış fiyatı: {previous_price:.2f}")
        print(f"Günlük fiyat değişimi: {daily_change:.2f}")
        print(f"Günlük değişim: {daily_change_percent:.2f}%")
        break
 