def calculate_rsi(data, period=14):
    price_change = data["Close"].diff()

    gains = price_change.clip(lower=0)
    losses = -price_change.clip(upper=0)

    average_gain = gains.rolling(window=period).mean()
    average_loss = losses.rolling(window=period).mean()

    relative_strength = average_gain / average_loss

    return 100 - (100 / (1 + relative_strength))


def calculate_indicators(data):
    data = data.copy()

    # Simple moving averages
    data["MA20"] = data["Close"].rolling(window=20).mean()
    data["MA50"] = data["Close"].rolling(window=50).mean()

    # RSI
    data["RSI"] = calculate_rsi(data)

    # Bollinger Bands
    data["BB_Middle"] = data["Close"].rolling(window=20).mean()
    rolling_std = data["Close"].rolling(window=20).std()

    data["BB_Upper"] = data["BB_Middle"] + (2 * rolling_std)
    data["BB_Lower"] = data["BB_Middle"] - (2 * rolling_std)

    # MACD
    data["EMA12"] = data["Close"].ewm(
        span=12,
        adjust=False,
    ).mean()

    data["EMA26"] = data["Close"].ewm(
        span=26,
        adjust=False,
    ).mean()

    data["MACD"] = data["EMA12"] - data["EMA26"]

    data["MACD_Signal"] = data["MACD"].ewm(
        span=9,
        adjust=False,
    ).mean()

    data["MACD_Histogram"] = (
        data["MACD"] - data["MACD_Signal"]
    )

    return data