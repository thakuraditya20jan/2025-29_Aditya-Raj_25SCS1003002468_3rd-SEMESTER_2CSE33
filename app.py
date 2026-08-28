import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Stock Market Dashboard",
    page_icon="📈",
    layout="wide"
)

# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------
st.title("📈 Real-Time Stock Market Dashboard")
st.markdown(
    "Monitor stock prices, historical trends, trading volume, "
    "and basic market indicators."
)

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
st.sidebar.header("Stock Selection")

stock_options = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Google": "GOOGL",
    "Amazon": "AMZN",
    "Tesla": "TSLA",
    "NVIDIA": "NVDA",
    "Meta": "META"
}

selected_stock = st.sidebar.selectbox(
    "Select a Stock",
    list(stock_options.keys())
)

ticker_symbol = stock_options[selected_stock]

period = st.sidebar.selectbox(
    "Select Time Period",
    ["1mo", "3mo", "6mo", "1y", "2y", "5y"]
)

# ---------------------------------------------------------
# LOAD STOCK DATA
# ---------------------------------------------------------
@st.cache_data(ttl=300)
def get_stock_data(symbol, selected_period):
    ticker = yf.Ticker(symbol)
    data = ticker.history(period=selected_period)
    info = ticker.info
    return data, info


try:
    data, info = get_stock_data(ticker_symbol, period)

    if data.empty:
        st.error("No stock data available. Please try again.")
        st.stop()

    # -----------------------------------------------------
    # CURRENT MARKET INFORMATION
    # -----------------------------------------------------
    current_price = float(data["Close"].iloc[-1])

    previous_close = (
        float(data["Close"].iloc[-2])
        if len(data) > 1
        else current_price
    )

    price_change = current_price - previous_close

    percentage_change = (
        (price_change / previous_close) * 100
        if previous_close != 0
        else 0
    )

    day_high = float(data["High"].iloc[-1])
    day_low = float(data["Low"].iloc[-1])
    volume = int(data["Volume"].iloc[-1])

    # -----------------------------------------------------
    # METRIC CARDS
    # -----------------------------------------------------
    st.subheader(f"{selected_stock} ({ticker_symbol})")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Current Price",
        f"${current_price:,.2f}",
        f"{price_change:+.2f}"
    )

    col2.metric(
        "Change %",
        f"{percentage_change:+.2f}%"
    )

    col3.metric(
        "Day High",
        f"${day_high:,.2f}"
    )

    col4.metric(
        "Day Low",
        f"${day_low:,.2f}"
    )

    # -----------------------------------------------------
    # PRICE CHART
    # -----------------------------------------------------
    st.subheader("📊 Historical Price")

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["Close"],
            mode="lines",
            name="Closing Price"
        )
    )

    fig.update_layout(
        title=f"{selected_stock} Stock Price",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        hovermode="x unified",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------------------------------
    # VOLUME CHART
    # -----------------------------------------------------
    st.subheader("📦 Trading Volume")

    volume_fig = go.Figure()

    volume_fig.add_trace(
        go.Bar(
            x=data.index,
            y=data["Volume"],
            name="Volume"
        )
    )

    volume_fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Volume",
        height=350
    )

    st.plotly_chart(volume_fig, use_container_width=True)

    # -----------------------------------------------------
    # STOCK DATA TABLE
    # -----------------------------------------------------
    st.subheader("📋 Recent Market Data")

    recent_data = data[
        ["Open", "High", "Low", "Close", "Volume"]
    ].tail(10).copy()

    recent_data["Open"] = recent_data["Open"].round(2)
    recent_data["High"] = recent_data["High"].round(2)
    recent_data["Low"] = recent_data["Low"].round(2)
    recent_data["Close"] = recent_data["Close"].round(2)

    st.dataframe(
        recent_data,
        use_container_width=True
    )

    # -----------------------------------------------------
    # COMPANY INFORMATION
    # -----------------------------------------------------
    st.subheader("🏢 Company Information")

    company_col1, company_col2 = st.columns(2)

    company_name = info.get("longName", selected_stock)
    sector = info.get("sector", "Not Available")
    industry = info.get("industry", "Not Available")
    market_cap = info.get("marketCap")

    company_col1.write(f"**Company:** {company_name}")
    company_col1.write(f"**Sector:** {sector}")

    company_col2.write(f"**Industry:** {industry}")

    if market_cap:
        company_col2.write(
            f"**Market Cap:** ${market_cap:,.0f}"
        )
    else:
        company_col2.write("**Market Cap:** Not Available")

    # -----------------------------------------------------
    # FOOTER
    # -----------------------------------------------------
    st.divider()

    st.caption(
        "Stock market data is retrieved using Yahoo Finance through "
        "the yfinance Python library. Market data may be delayed."
    )

except Exception as e:
    st.error("Unable to retrieve stock market data.")
    st.info(
        "Please check your internet connection and try again."
    )