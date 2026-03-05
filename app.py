import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# ============================
# Load Dataset
# ============================
df = pd.read_csv("sales_data.csv")

# Clean column names
df.columns = df.columns.str.strip().str.lower()
df.columns = df.columns.str.replace(" ", "_")

print("Columns in dataset:", df.columns)

# Convert data types safely
df["sales"] = pd.to_numeric(df["sales"], errors="coerce")
df["profit"] = pd.to_numeric(df["profit"], errors="coerce")
df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

# Create time columns
df["month"] = df["order_date"].dt.to_period("M").astype(str)
df["year"] = df["order_date"].dt.year

# Remove rows with missing sales
df = df.dropna(subset=["sales"])

# ============================
# App Initialization
# ============================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE])
app.title = "Executive Sales Dashboard"

# ============================
# Styles
# ============================
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "18rem",
    "padding": "2rem 1rem",
    "background": "linear-gradient(180deg, #0f2027, #203a43, #2c5364)",
    "color": "white",
}

CONTENT_STYLE = {
    "margin-left": "20rem",
    "padding": "2rem 1rem",
    "backgroundColor": "#f4f6f9",
    "minHeight": "100vh",
}

# ============================
# Sidebar
# ============================
sidebar = html.Div(
    [
        html.H2("📊 Sales Analytics"),
        html.Hr(),
        html.P("Filters"),

        dbc.Label("Select Region"),
        dcc.Dropdown(
            id="region_filter",
            options=[{"label": "All", "value": "All"}] +
                    [{"label": r, "value": r} for r in sorted(df["region"].dropna().unique())],
            value="All",
            clearable=False
        ),

        html.Br(),

        dbc.Label("Select Year"),
        dcc.Dropdown(
            id="year_filter",
            options=[{"label": "All", "value": "All"}] +
                    [{"label": int(y), "value": int(y)} for y in sorted(df["year"].dropna().unique())],
            value="All",
            clearable=False
        ),
    ],
    style=SIDEBAR_STYLE,
)

# ============================
# KPI Card
# ============================
def create_kpi_card(title, id_name):
    return dbc.Card(
        dbc.CardBody([
            html.H6(title, className="text-muted"),
            html.H2(id=id_name, className="fw-bold")
        ]),
        style={
            "borderRadius": "15px",
            "boxShadow": "0px 4px 12px rgba(0,0,0,0.1)",
        },
    )

# ============================
# Layout
# ============================
content = html.Div(
    [
        html.H1("Executive Sales Dashboard", className="mb-4"),

        dbc.Row([
            dbc.Col(create_kpi_card("Total Sales", "kpi_sales"), md=3),
            dbc.Col(create_kpi_card("Total Profit", "kpi_profit"), md=3),
            dbc.Col(create_kpi_card("Profit Margin %", "kpi_margin"), md=3),
            dbc.Col(create_kpi_card("Total Orders", "kpi_orders"), md=3),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(dcc.Graph(id="region_chart"), md=6),
            dbc.Col(dcc.Graph(id="category_chart"), md=6),
        ]),

        dbc.Row([
            dbc.Col(dcc.Graph(id="monthly_chart"), md=6),
            dbc.Col(dcc.Graph(id="top_customers_chart"), md=6),
        ])
    ],
    style=CONTENT_STYLE,
)

app.layout = html.Div([sidebar, content])

# ============================
# Callback
# ============================
@app.callback(
    [
        Output("kpi_sales", "children"),
        Output("kpi_profit", "children"),
        Output("kpi_margin", "children"),
        Output("kpi_orders", "children"),
        Output("region_chart", "figure"),
        Output("category_chart", "figure"),
        Output("monthly_chart", "figure"),
        Output("top_customers_chart", "figure"),
    ],
    [
        Input("region_filter", "value"),
        Input("year_filter", "value"),
    ],
)
def update_dashboard(selected_region, selected_year):

    filtered_df = df.copy()

    if selected_region != "All":
        filtered_df = filtered_df[filtered_df["region"] == selected_region]

    if selected_year != "All":
        filtered_df = filtered_df[filtered_df["year"] == selected_year]

    # If no data after filtering
    if filtered_df.empty:
        empty_fig = px.bar(title="No Data Available")
        return "0", "0", "0%", "0", empty_fig, empty_fig, empty_fig, empty_fig

    # KPIs
    total_sales = filtered_df["sales"].sum()
    total_profit = filtered_df["profit"].sum()
    total_orders = filtered_df["order_id"].nunique() if "order_id" in filtered_df.columns else len(filtered_df)
    profit_margin = (total_profit / total_sales * 100) if total_sales != 0 else 0

    # Charts
    region_sales = filtered_df.groupby("region")["sales"].sum().reset_index()
    fig_region = px.bar(region_sales, x="region", y="sales",
                        title="Sales by Region", template="plotly_dark")

    category_sales = filtered_df.groupby("category")["sales"].sum().reset_index()
    fig_category = px.pie(category_sales, names="category",
                          values="sales", title="Sales by Category")

    monthly_sales = filtered_df.groupby("month")["sales"].sum().reset_index()
    fig_monthly = px.line(monthly_sales, x="month", y="sales",
                          title="Monthly Sales Trend", markers=True)

    if "customer_name" in filtered_df.columns:
        top_customers = filtered_df.groupby("customer_name")["sales"].sum().reset_index()
        top_customers = top_customers.sort_values(by="sales", ascending=False).head(5)
        fig_top = px.bar(top_customers, x="customer_name", y="sales",
                         title="Top 5 Customers")
    else:
        fig_top = px.bar(title="Customer Data Not Available")

    return (
        f"${total_sales:,.0f}",
        f"${total_profit:,.0f}",
        f"{profit_margin:.2f}%",
        f"{total_orders}",
        fig_region,
        fig_category,
        fig_monthly,
        fig_top,
    )

# ============================
# Run App
# ============================
if __name__ == "__main__":
    app.run(debug=True)