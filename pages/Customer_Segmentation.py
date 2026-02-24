import streamlit as st
import pandas as pd

st.title("👥 Customer Segmentation (RFM Analysis)")

df = pd.read_csv("sales_data.csv")
df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
df = df.dropna(subset=["order_date"])

snapshot_date = df["order_date"].max()

rfm = df.groupby("customer_name").agg({
    "order_date": lambda x: (snapshot_date - x.max()).days,
    "order_id": "nunique",
    "sales": "sum"
})
# Ensure numeric
rfm["Monetary"] = pd.to_numeric(rfm["Monetary"], errors="coerce")
rfm = rfm.dropna(subset=["Monetary"])

# Safe qcut with duplicates handling
rfm["Segment"] = pd.qcut(
    rfm["Monetary"],
    q=4,
    labels=["Low", "Medium", "High", "VIP"],
    duplicates="drop"
)





