import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# PAGE CONFIG (MUST BE FIRST)
# -----------------------------
st.set_page_config(
    page_title="Premium Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("sales_data.csv", encoding="utf-8-sig")

    numeric_columns = ["sales", "profit", "quantity", "discount", "shipping_cost"]
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

    return df

df = load_data()

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("🔎 Filters")

# Region Filter
selected_region = st.sidebar.multiselect(
    "Select Region",
    options=df["region"].dropna().unique(),
    default=df["region"].dropna().unique()
)

# Category Filter
selected_category = st.sidebar.multiselect(
    "Select Category",
    options=df["category"].dropna().unique(),
    default=df["category"].dropna().unique()
)

# Date Range Filter
min_date = df["order_date"].min()
max_date = df["order_date"].max()

date_range = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Apply Filters
filtered_df = df[
    (df["region"].isin(selected_region)) &
    (df["category"].isin(selected_category)) &
    (df["order_date"] >= pd.to_datetime(date_range[0])) &
    (df["order_date"] <= pd.to_datetime(date_range[1]))
]

# -----------------------------
# TITLE
# -----------------------------
st.title("📊 Advanced Sales Intelligence Dashboard")

# -----------------------------
# KPI SECTION
# -----------------------------
total_sales = filtered_df["sales"].sum()
total_profit = filtered_df["profit"].sum()
total_orders = filtered_df["order_id"].nunique()
total_customers = filtered_df["customer_name"].nunique()

profit_margin = (total_profit / total_sales * 100) if total_sales != 0 else 0

col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Total Sales", f"{total_sales:,.0f}")
col2.metric("📈 Total Profit", f"{total_profit:,.0f}")
col3.metric("📦 Total Orders", total_orders)
col4.metric("👥 Total Customers", total_customers)

st.metric("💹 Profit Margin %", f"{profit_margin:.2f}%")

st.markdown("---")

# -----------------------------
# MONTHLY TREND + GROWTH
# -----------------------------
filtered_df["month"] = filtered_df["order_date"].dt.to_period("M")
monthly_sales = (
    filtered_df.groupby("month")["sales"]
    .sum()
    .reset_index()
)

monthly_sales["month"] = monthly_sales["month"].astype(str)

fig_line = px.line(
    monthly_sales,
    x="month",
    y="sales",
    markers=True,
    title="📈 Monthly Sales Trend"
)

st.plotly_chart(fig_line, use_container_width=True)

# Growth Calculation
if len(monthly_sales) > 1:
    growth = ((monthly_sales["sales"].iloc[-1] -
               monthly_sales["sales"].iloc[-2]) /
               monthly_sales["sales"].iloc[-2]) * 100
else:
    growth = 0

st.metric("📊 Monthly Growth %", f"{growth:.2f}%")

st.markdown("---")

# -----------------------------
# SALES BY CATEGORY
# -----------------------------
colA, colB = st.columns(2)

with colA:
    fig_bar = px.bar(
        filtered_df,
        x="category",
        y="sales",
        color="category",
        title="Sales by Category"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with colB:
    sales_by_category = (
        filtered_df.groupby("category")["sales"]
        .sum()
        .reset_index()
    )

    fig_pie = px.pie(
        sales_by_category,
        names="category",
        values="sales",
        title="Sales Distribution"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# -----------------------------
# TOP / BOTTOM PRODUCTS
# -----------------------------
st.subheader("🏆 Product Performance")

view_option = st.selectbox("Select View", ["Top 10 Products", "Bottom 10 Products"])

product_sales = (
    filtered_df.groupby("product_name")["sales"]
    .sum()
    .reset_index()
)

if view_option == "Top 10 Products":
    product_sales = product_sales.sort_values("sales", ascending=False).head(10)
else:
    product_sales = product_sales.sort_values("sales").head(10)

fig_products = px.bar(
    product_sales,
    x="sales",
    y="product_name",
    orientation="h",
    title=view_option
)

st.plotly_chart(fig_products, use_container_width=True)

st.markdown("---")

# -----------------------------
# DATA TABLE
# -----------------------------
st.subheader("📋 Detailed Data View")
st.dataframe(filtered_df, use_container_width=True)

# -----------------------------
# DOWNLOAD BUTTON
# -----------------------------
st.download_button(
    label="⬇ Download Filtered Data",
    data=filtered_df.to_csv(index=False),
    file_name="filtered_sales_data.csv",
    mime="text/csv"
)

st.success("✅ Advanced Premium Dashboard Loaded Successfully 🚀")
theme = st.sidebar.selectbox("Theme Mode", ["Light", "Dark"])

if theme == "Dark":
    st.markdown(
        """
        <style>
        body {
            background-color: #0E1117;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )