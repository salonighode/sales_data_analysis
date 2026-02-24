import streamlit as st
import pandas as pd

st.title("👥 Customer Segmentation (RFM Analysis)")

df = pd.read_csv("sales_data.csv")

# 🔎 Show column names (temporary debugging)
st.write("Columns in dataset:", df.columns.tolist())

# Make all column names lowercase and remove spaces
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Convert date safely
df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
df = df.dropna(subset=["order_date"])

snapshot_date = df["order_date"].max()

# ✅ Use named aggregation (safe way)
rfm = df.groupby("customer_name").agg(
    Recency=("order_date", lambda x: (snapshot_date - x.max()).days),
    Frequency=("order_id", "nunique"),
    Monetary=("sales", "sum")
).reset_index()

st.write("RFM Columns:", rfm.columns.tolist())  # Debug line

# Safe numeric conversion
rfm["Monetary"] = pd.to_numeric(rfm["Monetary"], errors="coerce")
rfm = rfm.dropna(subset=["Monetary"])

# Safe segmentation
rfm["Segment"] = pd.qcut(
    rfm["Monetary"],
    q=4,
    labels=["Low", "Medium", "High", "VIP"],
    duplicates="drop"
)

st.dataframe(rfm)
st.bar_chart(rfm["Segment"].value_counts())
