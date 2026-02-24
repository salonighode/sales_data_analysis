import streamlit as st
import pandas as pd

st.title("👥 Customer Segmentation (RFM Analysis)")

df = pd.read_csv("sales_data.csv")
df["order_date"] = pd.to_datetime(df["order_date"])

snapshot_date = df["order_date"].max()

rfm = df.groupby("customer_name").agg({
    "order_date": lambda x: (snapshot_date - x.max()).days,
    "order_id": "nunique",
    "sales": "sum"
})

rfm.columns = ["Recency", "Frequency", "Monetary"]

rfm["Segment"] = pd.qcut(rfm["Monetary"], 4,
                         labels=["Low", "Medium", "High", "VIP"])

st.dataframe(rfm)

st.bar_chart(rfm["Segment"].value_counts())