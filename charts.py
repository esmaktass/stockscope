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

def create_candlestick_chart(data, ticker):
    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"],
            name="Price"
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
        title=f"{ticker} Candlestick Analysis",
        xaxis_title="Date",
        yaxis_title="Price",
        hovermode="x unified",
        xaxis_rangeslider_visible=False
    )

    return fig

def create_volume_chart(data, ticker):
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=data.index,
            y=data["Volume"],
            name="Trading Volume",
        )
    )

    fig.update_layout(
        title=f"{ticker} Trading Volume",
        xaxis_title="Date",
        yaxis_title="Volume",
        hovermode="x unified",
        showlegend=False,
    )

    return fig