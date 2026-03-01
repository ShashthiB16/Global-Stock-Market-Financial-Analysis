import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os

st.set_page_config(page_title="Global Stock Trading Dashboard",
                   layout="wide",
                   page_icon="📈")

# ---------------- STYLE ----------------
st.markdown("""
<style>
.big-font {
    font-size:28px !important;
    font-weight:600;
}
.metric-card {
    background-color:#111111;
    padding:15px;
    border-radius:10px;
    text-align:center;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_path, "Global_Finance_Data.csv")

    df = pd.read_csv(file_path)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df

df = load_data()

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.title("📌 Filters")

country = st.sidebar.selectbox(
    "Country",
    sorted(df["Country"].dropna().unique())
)

country_df = df[df["Country"] == country]

company = st.sidebar.selectbox(
    "Company",
    sorted(country_df["Company"].dropna().unique())
)

filtered_df = country_df[country_df["Company"] == company]

start_date = st.sidebar.date_input("Start Date", filtered_df["Date"].min())
end_date = st.sidebar.date_input("End Date", filtered_df["Date"].max())

filtered_df = filtered_df[
    (filtered_df["Date"] >= pd.to_datetime(start_date)) &
    (filtered_df["Date"] <= pd.to_datetime(end_date))
]

if filtered_df.empty:
    st.warning("No data available")
    st.stop()

# ---------------- HEADER (FIXED TOP) ----------------
latest_price = filtered_df["Close"].iloc[-1]
first_price = filtered_df["Close"].iloc[0]
percent = ((latest_price - first_price) / first_price) * 100

st.markdown(
    f"<div class='big-font'>📈 {company} ({country})</div>",
    unsafe_allow_html=True
)

if percent >= 0:
    st.markdown(f"### ₹ {latest_price:.2f}  🔼 {percent:.2f}%")
else:
    st.markdown(f"### ₹ {latest_price:.2f}  🔽 {percent:.2f}%")

st.markdown("---")

# ---------------- KPI + CHART LAYOUT ----------------
left_col, right_col = st.columns([2,1])

with left_col:

    chart_type = st.radio(
        "Chart Type",
        ["Line", "Candlestick"],
        horizontal=True
    )

    fig = go.Figure()

    if chart_type == "Line":
        fig.add_trace(go.Scatter(
            x=filtered_df["Date"],
            y=filtered_df["Close"],
            mode='lines',
            name='Close'
        ))
    else:
        fig.add_trace(go.Candlestick(
            x=filtered_df["Date"],
            open=filtered_df["Open"],
            high=filtered_df["High"],
            low=filtered_df["Low"],
            close=filtered_df["Close"],
            name="Candle"
        ))

    fig.update_layout(
        template="plotly_dark",
        height=450,
        margin=dict(l=20, r=20, t=30, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)

with right_col:

    st.markdown("### 📊 Key Metrics")

    high_price = filtered_df["High"].max()
    low_price = filtered_df["Low"].min()
    total_volume = int(filtered_df["Volume"].sum())

    st.metric("Highest Price", f"{high_price:.2f}")
    st.metric("Lowest Price", f"{low_price:.2f}")
    st.metric("Total Volume", f"{total_volume:,}")

    st.markdown("### 📌 Market Insight")

    if percent > 0:
        st.success("Stock is in upward trend.")
    elif percent < 0:
        st.error("Stock is in downward trend.")
    else:
        st.info("Stock is stable.")

# ---------------- VOLUME (COMPACT BELOW) ----------------
st.markdown("---")

fig_volume = px.bar(
    filtered_df,
    x="Date",
    y="Volume",
    template="plotly_dark"
)

fig_volume.update_layout(height=250, margin=dict(l=20, r=20, t=20, b=20))

st.plotly_chart(fig_volume, use_container_width=True)
with left_col:

    # ---------------- THEME SWITCH ----------------
    theme = st.selectbox("🎨 Chart Theme", ["plotly_dark", "plotly_white"])

    # ---------------- TIME RANGE BUTTONS ----------------
    range_option = st.selectbox(
        "⏳ Quick Range",
        ["1M", "3M", "6M", "1Y", "All"]
    )

    if range_option != "All":
        days_map = {"1M":30, "3M":90, "6M":180, "1Y":365}
        filtered_df = filtered_df.tail(days_map[range_option])

    # ---------------- CHART TYPE ----------------
    chart_type = st.selectbox(
        "📊 Select Chart Type",
        ["Line", "Area", "Candlestick", "OHLC"]
    )

    # ---------------- INDICATORS ----------------
    col1, col2, col3 = st.columns(3)
    with col1:
        show_ma = st.checkbox("MA 20")
        show_bb = st.checkbox("Bollinger Bands")
    with col2:
        show_rsi = st.checkbox("RSI")
    with col3:
        show_macd = st.checkbox("MACD")
        show_volume = st.checkbox("Volume")

    fig = go.Figure()

    # ---------------- BASE CHART ----------------
    if chart_type == "Line":
        fig.add_trace(go.Scatter(
            x=filtered_df["Date"],
            y=filtered_df["Close"],
            mode='lines',
            name='Close'
        ))

    elif chart_type == "Area":
        fig.add_trace(go.Scatter(
            x=filtered_df["Date"],
            y=filtered_df["Close"],
            fill='tozeroy',
            mode='lines',
            name='Close'
        ))

    elif chart_type == "Candlestick":
        fig.add_trace(go.Candlestick(
            x=filtered_df["Date"],
            open=filtered_df["Open"],
            high=filtered_df["High"],
            low=filtered_df["Low"],
            close=filtered_df["Close"],
            name="Candle"
        ))

    elif chart_type == "OHLC":
        fig.add_trace(go.Ohlc(
            x=filtered_df["Date"],
            open=filtered_df["Open"],
            high=filtered_df["High"],
            low=filtered_df["Low"],
            close=filtered_df["Close"],
            name="OHLC"
        ))

    # ---------------- MOVING AVERAGE ----------------
    if show_ma:
        filtered_df["MA20"] = filtered_df["Close"].rolling(20).mean()
        fig.add_trace(go.Scatter(
            x=filtered_df["Date"],
            y=filtered_df["MA20"],
            name="MA 20",
            line=dict(dash='dash')
        ))

    # ---------------- BOLLINGER BANDS ----------------
    if show_bb:
        filtered_df["MA20"] = filtered_df["Close"].rolling(20).mean()
        filtered_df["Upper"] = filtered_df["MA20"] + (filtered_df["Close"].rolling(20).std() * 2)
        filtered_df["Lower"] = filtered_df["MA20"] - (filtered_df["Close"].rolling(20).std() * 2)

        fig.add_trace(go.Scatter(x=filtered_df["Date"], y=filtered_df["Upper"],
                                 line=dict(width=1), name="Upper Band"))
        fig.add_trace(go.Scatter(x=filtered_df["Date"], y=filtered_df["Lower"],
                                 line=dict(width=1), name="Lower Band"))

    # ---------------- VOLUME ----------------
    if show_volume:
        fig.add_trace(go.Bar(
            x=filtered_df["Date"],
            y=filtered_df["Volume"],
            name="Volume",
            opacity=0.3,
            yaxis="y2"
        ))

        fig.update_layout(
            yaxis2=dict(
                overlaying='y',
                side='right',
                showgrid=False
            )
        )

    # ---------------- RSI ----------------
    if show_rsi:
        delta = filtered_df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss
        filtered_df["RSI"] = 100 - (100 / (1 + rs))

        fig.add_trace(go.Scatter(
            x=filtered_df["Date"],
            y=filtered_df["RSI"],
            name="RSI (14)",
            yaxis="y3"
        ))

        fig.update_layout(
            yaxis3=dict(
                anchor="free",
                overlaying="y",
                side="right",
                position=0.95
            )
        )

    # ---------------- MACD ----------------
    if show_macd:
        exp1 = filtered_df["Close"].ewm(span=12).mean()
        exp2 = filtered_df["Close"].ewm(span=26).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9).mean()

        fig.add_trace(go.Scatter(
            x=filtered_df["Date"],
            y=macd,
            name="MACD",
            line=dict(width=1)
        ))

        fig.add_trace(go.Scatter(
            x=filtered_df["Date"],
            y=signal,
            name="Signal",
            line=dict(dash='dot')
        ))

    # ---------------- FINAL LAYOUT ----------------
    fig.update_layout(
        template=theme,
        height=550,
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis_rangeslider_visible=False,
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)
