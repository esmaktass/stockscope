import yfinance as yf

stock = yf.Ticker("AAPL")
data = stock.history(period="1y")

print("\nSon 5 satır:")
print(data.tail())

print("\nSütunlar:")
print(data.columns)

print("\nVeri boyutu:")
print(data.shape)

print("\nVeri tipi:")
print(type(data))