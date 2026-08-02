def calculate_indicators(data):
    data = data.copy()

    data["MA20"] = data["Close"].rolling(window=20).mean()
    data["MA50"] = data["Close"].rolling(window=50).mean()

    return data