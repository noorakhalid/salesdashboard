import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# PAGE CONFIG
st.set_page_config(page_title="Sales Model Dashboard", layout="wide")

# DARK THEME – POWER BI STYLE
st.markdown("""
<style>
/* Main background */
.stApp {
    background-color: rgb(100, 212, 155);
    color: white;
}
/* KPI Cards */
.kpi-box {
    background-color: #1E1E1E;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    color: white;
    box-shadow: 0 0 10px rgba(0,0,0,0.5);
}
.kpi-title {
    font-size: 18px;
    color: #A0A0A0;
}
.kpi-value {
    font-size: 32px;
    font-weight: bold;
    color: #4CAF50; /* Green */
}
            
/* Sidebar */
.css-1d391kg {
    background-color: #161A23;
}

/* Metric cards */
[data-testid="metric-container"] {
    background-color: #1F2937;
    border: 1px solid #374151;
    padding: 15px;
    border-radius: 10px;
}

/* Headings */
h1, h2, h3, h4 {
    color: #F9FAFB;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    background-color: #1F2937;
}

/* Buttons */
.stDownloadButton button {
    background-color: #2563EB;
    color: white;
    border-radius: 6px;
}
</style>
""", unsafe_allow_html=True)

st.title("Sales Performance Dashboard")

# CSV UPLOAD
st.sidebar.header(" Upload Sales CSV")

uploaded_file = st.sidebar.file_uploader(
    "Upload sales_data.csv",
    type=["csv"]
)

if uploaded_file is None:
    st.info(" Upload sales_data.csv to view dashboard")
    st.stop()

data = pd.read_csv(uploaded_file)

# DATA VALIDATION
required_cols = [
    "Order_ID", "Date", "Product",
    "Region", "Quantity", "Unit_Price", "Total_Sales"
]

if not all(col in data.columns for col in required_cols):
    st.error(f"CSV must contain columns: {required_cols}")
    st.stop()

# DATA PREPARATION
data["Date"] = pd.to_datetime(data["Date"])
data["Month"] = data["Date"].dt.strftime("%b-%Y")

# SIDEBAR FILTERS
st.sidebar.header(" Filters")

region = st.sidebar.selectbox(
    "Select Region",
    ["All"] + list(data["Region"].unique())
)

product = st.sidebar.selectbox(
    "Select Product",
    ["All"] + list(data["Product"].unique())
)

filtered = data.copy()

if region != "All":
    filtered = filtered[filtered["Region"] == region]

if product != "All":
    filtered = filtered[filtered["Product"] == product]

# KPI CARDS (TOP ROW)
k1, k2, k3, k4 = st.columns(4)

k1.metric("Total Sales", f"₹ {filtered['Total_Sales'].sum():,.0f}")
k2.metric("Total Quantity", filtered["Quantity"].sum())
k3.metric("Avg Unit Price", f"₹ {filtered['Unit_Price'].mean():,.2f}")
k4.metric("Orders", filtered["Order_ID"].nunique())

# GAUGE CHARTS (MODEL STYLE)

g1, g2, g3, g4 = st.columns(4)

def gauge(title, value, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": color}
        },
        title={"text": title}
    ))
    fig.update_layout(height=220, margin=dict(l=10, r=10, t=40, b=10))
    return fig

g1.plotly_chart(gauge("Sales Target Achieved %", 78, "steelblue"), use_container_width=True)
g2.plotly_chart(gauge("Avg Delivery Days", 42, "orange"), use_container_width=True)
g3.plotly_chart(gauge("Return Rate %", 12, "red"), use_container_width=True)
g4.plotly_chart(gauge("Customer Satisfaction", 88, "green"), use_container_width=True)

# BAR CHART – Region Sales
st.subheader("Region-wise Sales")

region_sales = (
    filtered
    .groupby("Region")["Total_Sales"]
    .sum()
    .reset_index()
)

bar_fig = px.bar(
    region_sales,
    x="Region",
    y="Total_Sales",
    text_auto=True
)

st.plotly_chart(bar_fig, use_container_width=True)

# LINE CHART – Monthly Sales Trend
st.subheader(" Monthly Sales Trend")

monthly_sales = (
    filtered
    .groupby("Month")["Total_Sales"]
    .sum()
    .reset_index()
)

line_fig = px.line(
    monthly_sales,
    x="Month",
    y="Total_Sales",
    markers=True
)

st.plotly_chart(line_fig, use_container_width=True)

# STACKED BAR – Product Sales by Month
st.subheader("Product Sales Summary")

prod_month = (
    filtered
    .groupby(["Month", "Product"])["Total_Sales"]
    .sum()
    .reset_index()
)

stack_fig = px.bar(
    prod_month,
    x="Month",
    y="Total_Sales",
    color="Product",
    barmode="stack"
)

st.plotly_chart(stack_fig, use_container_width=True)

# DATA TABLE
st.subheader(" Sales Data Table")
st.dataframe(filtered)

# DOWNLOAD OPTION
st.download_button(
    "Download Filtered Data",
    filtered.to_csv(index=False),
    "filtered_sales_data.csv",
    "text/csv"
)
  