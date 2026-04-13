import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os

st.set_page_config(page_title="Global Stock Trading Dashboard",
                   layout="wide",
                   page_icon="📈")
# ---------------- TITLE ----------------
st.markdown(
    "<h1 style='text-align:center;'>📊 Global Stock Market Dashboard</h1>",
    unsafe_allow_html=True
)

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
st.sidebar.markdown("## 📌 Filters")

country = st.selectbox("Country", country_list)

company = st.multiselect(
    "Company",
    company_list,
    default=[company_list[0]]
)

date_range = st.date_input(
    "Date Range",
    [filtered_df["Date"].min(), filtered_df["Date"].max()]
)

price_type = st.selectbox(
    "Price Type",
    ["Close", "Open", "High", "Low"]
)

range_option = st.radio(
    "Quick Range",
    ["1M", "3M", "6M", "1Y", "MAX"],
    horizontal=True
)

volume_range = st.slider(
    "Volume Filter",
    int(filtered_df["Volume"].min()),
    int(filtered_df["Volume"].max()),
    (int(filtered_df["Volume"].min()), int(filtered_df["Volume"].max()))
)

indicators = st.multiselect(
    "Indicators",
    ["MA", "EMA", "RSI", "Bollinger Bands"]
)

if st.button("🔄 Reset Filters"):
    st.rerun()
  
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
left_col, right_col = st.columns([3, 1])

with left_col:

    # 🎯 Chart Selection
    chart_type = st.selectbox(
        "📊 Select Chart Type",
        ["Line", "Candlestick", "OHLC", "Area"]
    )

    # 🎯 Indicator Selection
    show_ma = st.checkbox("Show Moving Average (20 days)")
    show_volume = st.checkbox("Show Volume")

    fig = go.Figure()

    # ---------------- CHART TYPES ----------------
    if chart_type == "Line":
        fig.add_trace(go.Scatter(
            x=filtered_df["Date"],
            y=filtered_df["Close"],
            mode='lines',
            name='Close',
            fill=None
        ))

    elif chart_type == "Area":
        fig.add_trace(go.Scatter(
            x=filtered_df["Date"],
            y=filtered_df["Close"],
            mode='lines',
            fill='tozeroy',
            name='Area Chart'
        ))

    elif chart_type == "Candlestick":
        fig.add_trace(go.Candlestick(
            x=filtered_df["Date"],
            open=filtered_df["Open"],
            high=filtered_df["High"],
            low=filtered_df["Low"],
            close=filtered_df["Close"],
            name="Candlestick"
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
            mode='lines',
            name='MA20',
            line=dict(dash='dash')
        ))

    # ---------------- VOLUME ----------------
    if show_volume:
        fig.add_trace(go.Bar(
            x=filtered_df["Date"],
            y=filtered_df["Volume"],
            name="Volume",
            yaxis="y2",
            opacity=0.3
        ))

    # ---------------- LAYOUT ----------------
    fig.update_layout(
        template="plotly_dark",
        height=500,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_rangeslider_visible=True,
        yaxis_title="Price",
        yaxis2=dict(
            overlaying='y',
            side='right',
            title="Volume",
            showgrid=False
        )
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------- KPI SECTION ----------------
with right_col:

    st.markdown("## 📊 Key Metrics")

    high_price = filtered_df["High"].max()
    low_price = filtered_df["Low"].min()
    avg_price = filtered_df["Close"].mean()
    total_volume = int(filtered_df["Volume"].sum())

    # 📈 Returns
    start_price = filtered_df["Close"].iloc[0]
    end_price = filtered_df["Close"].iloc[-1]
    returns = ((end_price - start_price) / start_price) * 100

    # 📉 Volatility
    volatility = filtered_df["Close"].pct_change().std() * 100

    st.metric("Highest Price", f"{high_price:.2f}")
    st.metric("Lowest Price", f"{low_price:.2f}")
    st.metric("Average Price", f"{avg_price:.2f}")
    st.metric("Total Volume", f"{total_volume:,}")
    st.metric("Return %", f"{returns:.2f}%")
    st.metric("Volatility", f"{volatility:.2f}%")

    # ---------------- MARKET INSIGHT ----------------
    st.markdown("## 📌 Market Insight")

    if returns > 2:
        st.success("📈 Strong Uptrend")
    elif returns > 0:
        st.info("📊 Mild Uptrend")
    elif returns < -2:
        st.error("📉 Strong Downtrend")
    elif returns < 0:
        st.warning("⚠️ Mild Downtrend")
    else:
        st.info("➖ Sideways Market")
      
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
