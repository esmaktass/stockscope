import pandas as pd


def build_market_insights(data):
    required_columns = [
        "Close",
        "MA20",
        "MA50",
        "RSI",
        "MACD",
        "MACD_Signal",
        "BB_Upper",
        "BB_Lower",
        "BB_Middle",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        return {
            "label": "Insufficient data",
            "score": 0,
            "status": "neutral",
            "messages": [
                "Some technical indicators could not be calculated."
            ],
        }

    latest = data.iloc[-1]

    required_values = [
        latest["Close"],
        latest["MA20"],
        latest["MA50"],
        latest["RSI"],
        latest["MACD"],
        latest["MACD_Signal"],
        latest["BB_Upper"],
        latest["BB_Lower"],
        latest["BB_Middle"],
    ]

    if any(pd.isna(value) for value in required_values):
        return {
            "label": "Insufficient data",
            "score": 0,
            "status": "neutral",
            "messages": [
                "The selected period does not contain enough data "
                "for a complete technical summary."
            ],
        }

    close_price = latest["Close"]
    ma20 = latest["MA20"]
    ma50 = latest["MA50"]
    rsi = latest["RSI"]
    macd = latest["MACD"]
    macd_signal = latest["MACD_Signal"]
    upper_band = latest["BB_Upper"]
    lower_band = latest["BB_Lower"]
    middle_band = latest["BB_Middle"]

    score = 0
    messages = []

    # Price versus moving averages
    if close_price > ma20:
        score += 1
        messages.append(
            "Price is trading above the 20-day moving average."
        )
    else:
        score -= 1
        messages.append(
            "Price is trading below the 20-day moving average."
        )

    if close_price > ma50:
        score += 1
        messages.append(
            "Price is trading above the 50-day moving average."
        )
    else:
        score -= 1
        messages.append(
            "Price is trading below the 50-day moving average."
        )

    # Moving-average structure
    if ma20 > ma50:
        score += 1
        messages.append(
            "MA20 is above MA50, indicating positive short-term momentum."
        )
    else:
        score -= 1
        messages.append(
            "MA20 is below MA50, indicating weaker short-term momentum."
        )

    # RSI
    if rsi >= 70:
        score -= 1
        messages.append(
            "RSI is in the overbought region."
        )
    elif rsi <= 30:
        score += 1
        messages.append(
            "RSI is in the oversold region."
        )
    elif rsi >= 55:
        score += 1
        messages.append(
            "RSI shows moderately positive momentum."
        )
    elif rsi <= 45:
        score -= 1
        messages.append(
            "RSI shows moderately negative momentum."
        )
    else:
        messages.append(
            "RSI is in the neutral region."
        )

    # MACD
    if macd > macd_signal:
        score += 1
        messages.append(
            "MACD is above its signal line."
        )
    else:
        score -= 1
        messages.append(
            "MACD is below its signal line."
        )

    # Bollinger position
    band_width = upper_band - lower_band

    if band_width > 0:
        band_position = (
            close_price - lower_band
        ) / band_width

        if band_position >= 0.8:
            messages.append(
                "Price is trading near the upper Bollinger Band."
            )
        elif band_position <= 0.2:
            messages.append(
                "Price is trading near the lower Bollinger Band."
            )
        elif close_price >= middle_band:
            messages.append(
                "Price is trading in the upper half of the Bollinger range."
            )
        else:
            messages.append(
                "Price is trading in the lower half of the Bollinger range."
            )

    label, status = classify_score(score)

    return {
        "label": label,
        "score": score,
        "status": status,
        "messages": messages,
    }


def classify_score(score):
    if score >= 4:
        return "Strongly bullish", "positive"

    if score >= 2:
        return "Moderately bullish", "positive"

    if score <= -4:
        return "Strongly bearish", "negative"

    if score <= -2:
        return "Moderately bearish", "negative"

    return "Neutral / mixed", "neutral"