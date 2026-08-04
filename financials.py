import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf


def clean_statement(statement):
    """
    Clean a financial statement returned by yfinance.
    """
    if statement is None or statement.empty:
        return pd.DataFrame()

    cleaned = statement.copy()

    cleaned = cleaned.dropna(
        axis=1,
        how="all",
    )

    cleaned = cleaned.dropna(
        axis=0,
        how="all",
    )

    # Financial statement columns are dates.
    # Sort them from oldest to newest so iloc[-1]
    # always represents the latest available year.
    try:
        cleaned = cleaned[
            sorted(cleaned.columns)
        ]
    except (TypeError, ValueError):
        pass

    return cleaned


def get_financial_statements(ticker: str):
    """
    Fetch annual financial statements for one ticker.

    The property-based yfinance access methods are used first
    because they work correctly in the current environment.
    """
    clean_ticker = ticker.strip().upper()

    if not clean_ticker:
        return None

    try:
        stock = yf.Ticker(clean_ticker)

        income_statement = stock.income_stmt
        balance_sheet = stock.balance_sheet
        cash_flow = stock.cashflow

        # Fallback methods in case a property returns empty.
        if (
            income_statement is None
            or income_statement.empty
        ):
            income_statement = stock.get_income_stmt(
                freq="yearly",
                pretty=False,
            )

        if (
            balance_sheet is None
            or balance_sheet.empty
        ):
            balance_sheet = stock.get_balance_sheet(
                freq="yearly",
                pretty=False,
            )

        if (
            cash_flow is None
            or cash_flow.empty
        ):
            cash_flow = stock.get_cash_flow(
                freq="yearly",
                pretty=False,
            )

    except Exception as error:
        print(
            f"Financial statement error for "
            f"{clean_ticker}: {error}"
        )
        return None

    return {
        "income_statement": clean_statement(
            income_statement
        ),
        "balance_sheet": clean_statement(
            balance_sheet
        ),
        "cash_flow": clean_statement(
            cash_flow
        ),
    }


def find_statement_row(
    statement: pd.DataFrame,
    possible_names: list[str],
):
    """
    Return the first matching financial statement row.
    """
    if statement is None or statement.empty:
        return None

    normalized_index = {
        str(index).strip().lower(): index
        for index in statement.index
    }

    for name in possible_names:
        normalized_name = name.strip().lower()

        if normalized_name in normalized_index:
            original_index = normalized_index[
                normalized_name
            ]

            return statement.loc[original_index]

    return None


def format_financial_value(value):
    """
    Format large financial values for metric cards.
    """
    if value is None or pd.isna(value):
        return "N/A"

    absolute_value = abs(value)

    if absolute_value >= 1_000_000_000_000:
        return (
            f"{value / 1_000_000_000_000:.2f}T"
        )

    if absolute_value >= 1_000_000_000:
        return (
            f"{value / 1_000_000_000:.2f}B"
        )

    if absolute_value >= 1_000_000:
        return (
            f"{value / 1_000_000:.2f}M"
        )

    if absolute_value >= 1_000:
        return (
            f"{value / 1_000:.2f}K"
        )

    return f"{value:,.2f}"


def get_latest_value(series):
    """
    Return the most recent non-null value from a Series.
    """
    if series is None:
        return None

    valid_values = series.dropna()

    if valid_values.empty:
        return None

    return valid_values.iloc[-1]


def calculate_growth(series):
    """
    Calculate percentage growth between the two
    most recent available annual values.
    """
    if series is None:
        return None

    valid_values = series.dropna()

    if len(valid_values) < 2:
        return None

    previous_value = valid_values.iloc[-2]
    current_value = valid_values.iloc[-1]

    if previous_value == 0:
        return None

    return (
        (current_value - previous_value)
        / abs(previous_value)
    ) * 100


def format_growth(value):
    if value is None or pd.isna(value):
        return None

    return f"{value:+.2f}%"


def prepare_trend_data(
    statement: pd.DataFrame,
    rows: dict[str, list[str]],
):
    """
    Convert selected statement rows into a
    chart-friendly DataFrame.
    """
    trend_data = {}

    for display_name, possible_names in rows.items():
        series = find_statement_row(
            statement,
            possible_names,
        )

        if series is not None:
            trend_data[display_name] = series

    if not trend_data:
        return pd.DataFrame()

    result = pd.DataFrame(trend_data)

    result.index = pd.to_datetime(
        result.index,
        errors="coerce",
    )

    result = result[
        result.index.notna()
    ]

    return result.sort_index()


def create_financial_trend_chart(
    trend_data: pd.DataFrame,
    title: str,
    y_axis_title: str,
):
    fig = go.Figure()

    for column in trend_data.columns:
        fig.add_trace(
            go.Bar(
                x=trend_data.index,
                y=trend_data[column],
                name=column,
            )
        )

    fig.update_layout(
        title=title,
        xaxis_title="Fiscal Year",
        yaxis_title=y_axis_title,
        barmode="group",
        hovermode="x unified",
    )

    return fig


def prepare_statement_for_display(
    statement: pd.DataFrame,
):
    """
    Prepare a financial statement for Streamlit.
    """
    if statement is None or statement.empty:
        return pd.DataFrame()

    displayed = statement.copy()

    displayed.columns = [
        column.strftime("%Y")
        if hasattr(column, "strftime")
        else str(column)
        for column in displayed.columns
    ]

    # Newest year first.
    displayed = displayed[
        list(reversed(displayed.columns))
    ]

    return displayed


def render_statement_table(
    statement: pd.DataFrame,
    title: str,
):
    st.subheader(title)

    displayed = prepare_statement_for_display(
        statement
    )

    if displayed.empty:
        st.info(
            f"No {title.lower()} data is available "
            "for this ticker."
        )
        return

    st.dataframe(
        displayed.style.format(
            lambda value: (
                format_financial_value(value)
                if pd.notna(value)
                else "N/A"
            )
        ),
        width="stretch",
    )


def render_financial_analysis():
    st.subheader("Financial Statements")

    ticker = st.text_input(
        "Ticker Symbol",
        value="AAPL",
        key="financial_ticker",
    )

    load_button = st.button(
        "Load Financial Statements",
        type="primary",
        width="stretch",
        key="financial_load_button",
    )

    if not load_button:
        return

    clean_ticker = ticker.strip().upper()

    if not clean_ticker:
        st.error("Please enter a ticker symbol.")
        return

    with st.spinner(
        "Loading financial statements..."
    ):
        statements = get_financial_statements(
            clean_ticker
        )

    if statements is None:
        st.error(
            "Financial statements could not be loaded. "
            "Check the ticker symbol and try again."
        )
        return

    income_statement = statements[
        "income_statement"
    ]
    balance_sheet = statements[
        "balance_sheet"
    ]
    cash_flow = statements[
        "cash_flow"
    ]

    all_statements_empty = (
        income_statement.empty
        and balance_sheet.empty
        and cash_flow.empty
    )

    if all_statements_empty:
        if clean_ticker.endswith("-USD"):
            st.info(
                "Financial statements are not applicable "
                "to cryptocurrencies. Use the Single Stock "
                "Analysis tab for price and technical analysis."
            )
        else:
            st.warning(
                "No annual financial statements are "
                "available for this ticker."
            )

        return

    total_revenue = find_statement_row(
        income_statement,
        [
            "Total Revenue",
            "Operating Revenue",
        ],
    )

    net_income = find_statement_row(
        income_statement,
        [
            "Net Income",
            "Net Income Common Stockholders",
        ],
    )

    total_assets = find_statement_row(
        balance_sheet,
        [
            "Total Assets",
        ],
    )

    total_debt = find_statement_row(
        balance_sheet,
        [
            "Total Debt",
        ],
    )

    operating_cash_flow = find_statement_row(
        cash_flow,
        [
            "Operating Cash Flow",
            "Cash Flow From Continuing Operating Activities",
        ],
    )

    free_cash_flow = find_statement_row(
        cash_flow,
        [
            "Free Cash Flow",
        ],
    )

    revenue_value = get_latest_value(
        total_revenue
    )
    net_income_value = get_latest_value(
        net_income
    )
    assets_value = get_latest_value(
        total_assets
    )
    debt_value = get_latest_value(
        total_debt
    )
    operating_cash_flow_value = get_latest_value(
        operating_cash_flow
    )
    free_cash_flow_value = get_latest_value(
        free_cash_flow
    )

    revenue_growth = calculate_growth(
        total_revenue
    )
    net_income_growth = calculate_growth(
        net_income
    )

    st.markdown(f"### {clean_ticker}")

    metric_columns = st.columns(3)

    metric_columns[0].metric(
        "Revenue",
        format_financial_value(
            revenue_value
        ),
        format_growth(
            revenue_growth
        ),
    )

    metric_columns[1].metric(
        "Net Income",
        format_financial_value(
            net_income_value
        ),
        format_growth(
            net_income_growth
        ),
    )

    metric_columns[2].metric(
        "Total Assets",
        format_financial_value(
            assets_value
        ),
    )

    second_metric_columns = st.columns(3)

    second_metric_columns[0].metric(
        "Total Debt",
        format_financial_value(
            debt_value
        ),
    )

    second_metric_columns[1].metric(
        "Operating Cash Flow",
        format_financial_value(
            operating_cash_flow_value
        ),
    )

    second_metric_columns[2].metric(
        "Free Cash Flow",
        format_financial_value(
            free_cash_flow_value
        ),
    )

    income_trends = prepare_trend_data(
        income_statement,
        {
            "Revenue": [
                "Total Revenue",
                "Operating Revenue",
            ],
            "Net Income": [
                "Net Income",
                "Net Income Common Stockholders",
            ],
        },
    )

    if not income_trends.empty:
        income_chart = create_financial_trend_chart(
            income_trends,
            (
                f"{clean_ticker} Revenue and "
                "Net Income Trend"
            ),
            "Financial Value",
        )

        st.plotly_chart(
            income_chart,
            width="stretch",
        )

    cash_flow_trends = prepare_trend_data(
        cash_flow,
        {
            "Operating Cash Flow": [
                "Operating Cash Flow",
                (
                    "Cash Flow From Continuing "
                    "Operating Activities"
                ),
            ],
            "Free Cash Flow": [
                "Free Cash Flow",
            ],
        },
    )

    if not cash_flow_trends.empty:
        cash_flow_chart = create_financial_trend_chart(
            cash_flow_trends,
            f"{clean_ticker} Cash Flow Trend",
            "Cash Flow",
        )

        st.plotly_chart(
            cash_flow_chart,
            width="stretch",
        )

    statement_tabs = st.tabs(
        [
            "Income Statement",
            "Balance Sheet",
            "Cash Flow",
        ]
    )

    with statement_tabs[0]:
        render_statement_table(
            income_statement,
            "Income Statement",
        )

    with statement_tabs[1]:
        render_statement_table(
            balance_sheet,
            "Balance Sheet",
        )

    with statement_tabs[2]:
        render_statement_table(
            cash_flow,
            "Cash Flow Statement",
        )

    st.caption(
        "Financial statement availability and labels "
        "depend on Yahoo Finance data. Values are "
        "reported in the company's statement currency."
    )