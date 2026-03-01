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
    file_path = os.path.join(base_path, "Global_Stock_Data.csv")

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
