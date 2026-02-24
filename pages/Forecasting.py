import streamlit as st
import pandas as pd
from prophet import Prophet
import plotly.express as px

st.title("🔮 Sales Forecasting")

df = pd.read_csv("sales_data.csv")
df["order_date"] = pd.to_datetime(df["order_date"])

monthly = df.groupby("order_date")["sales"].sum().reset_index()
monthly.columns = ["ds", "y"]

model = Prophet()
model.fit(monthly)

future = model.make_future_dataframe(periods=6, freq="M")
forecast = model.predict(future)

fig = px.line(forecast, x="ds", y="yhat", title="Sales Forecast")
st.plotly_chart(fig, use_container_width=True)