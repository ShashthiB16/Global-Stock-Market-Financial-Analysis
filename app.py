import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Global Finance Dashboard", layout="wide")

st.title("📊 Global Finance Interactive Dashboard")

# -------------------- FILE UPLOAD -------------------- #
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:

    # Read Data
    df = pd.read_csv(uploaded_file)

    # 🔥 Remove Unnamed Columns Automatically
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

    # Convert Date Column if exists
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])

    st.success("File Uploaded Successfully!")

    # -------------------- DATA PREVIEW -------------------- #
    with st.expander("📄 View Raw Data"):
        st.dataframe(df)

    # -------------------- SIDEBAR FILTERS -------------------- #
    st.sidebar.header("🔎 Filters")

    # Date Filter
    if "Date" in df.columns:
        start_date = st.sidebar.date_input("Start Date", df["Date"].min())
        end_date = st.sidebar.date_input("End Date", df["Date"].max())

        df = df[(df["Date"] >= pd.to_datetime(start_date)) &
                (df["Date"] <= pd.to_datetime(end_date))]

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

    selected_col = st.sidebar.selectbox("Select Column", numeric_cols)

    chart_type = st.sidebar.radio(
        "Select Chart Type",
        ["Line Chart", "Bar Chart", "Area Chart"]
    )

    # -------------------- KPI SECTION -------------------- #
    st.subheader("📌 Key Metrics")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Records", len(df))
    col2.metric("Average Value", round(df[selected_col].mean(), 2))
    col3.metric("Maximum Value", round(df[selected_col].max(), 2))

    # -------------------- INTERACTIVE CHART -------------------- #
    st.subheader(f"📈 {chart_type} of {selected_col}")

    if "Date" in df.columns:

        if chart_type == "Line Chart":
            fig = px.line(df, x="Date", y=selected_col)

        elif chart_type == "Bar Chart":
            fig = px.bar(df, x="Date", y=selected_col)

        else:
            fig = px.area(df, x="Date", y=selected_col)

        fig.update_layout(xaxis_title="Date", yaxis_title=selected_col)

        st.plotly_chart(fig, use_container_width=True)

    # -------------------- CORRELATION -------------------- #
    st.subheader("🔥 Correlation Heatmap")

    corr = df[numeric_cols].corr()

    fig2 = px.imshow(
        corr,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="RdBu_r"
    )

    st.plotly_chart(fig2, use_container_width=True)

    # -------------------- DOWNLOAD BUTTON -------------------- #
    st.subheader("⬇ Download Filtered Data")

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="filtered_data.csv",
        mime="text/csv",
    )

else:
    st.info("👆 Please upload a CSV file to start the dashboard.")
