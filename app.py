import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Global Finance Dashboard", layout="wide")

st.title("📊 Global Finance Data Dashboard")

# File uploader
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    
    # Read data
    df = pd.read_csv(uploaded_file)
    
    # Convert Date column
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])
    
    st.subheader("📌 Data Preview")
    st.dataframe(df.head())

    st.subheader("📊 Dataset Info")
    st.write("Rows:", df.shape[0])
    st.write("Columns:", df.shape[1])

    # Sidebar filters
    st.sidebar.header("Filter Options")

    if "Date" in df.columns:
        start_date = st.sidebar.date_input("Start Date", df["Date"].min())
        end_date = st.sidebar.date_input("End Date", df["Date"].max())

        df = df[(df["Date"] >= pd.to_datetime(start_date)) & 
                (df["Date"] <= pd.to_datetime(end_date))]

    numeric_columns = df.select_dtypes(include=np.number).columns.tolist()

    selected_column = st.sidebar.selectbox(
        "Select Column for Visualization",
        numeric_columns
    )

    # Line Chart
    st.subheader(f"📈 Line Chart of {selected_column}")
    fig, ax = plt.subplots()
    ax.plot(df["Date"], df[selected_column])
    ax.set_xlabel("Date")
    ax.set_ylabel(selected_column)
    st.pyplot(fig)

    # Correlation Heatmap
    st.subheader("🔥 Correlation Heatmap")
    fig2, ax2 = plt.subplots()
    sns.heatmap(df[numeric_columns].corr(), annot=True, cmap="coolwarm", ax=ax2)
    st.pyplot(fig2)

else:
    st.info("Please upload a CSV file to continue.")
