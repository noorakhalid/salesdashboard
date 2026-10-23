import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(page_title="EliteLiving Sales Dashboard", page_icon="💎", layout="wide")

# Custom Dark Theme & High Contrast Mobile Friendly Styling
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Standard text and labels high contrast for mobile */
    p, span, label, div, .stMarkdown {
        color: #ffffff !important;
    }
    
    .logo-container {
        display: flex;
        align-items: center;
        gap: 15px;
        background: linear-gradient(135deg, #1f4068, #1b1b2f);
        padding: 15px 25px;
        border-radius: 14px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.6);
        border: 1px solid #00f5d4;
        margin-bottom: 20px;
    }
    
    .logo-badge {
        background: linear-gradient(135deg, #00f5d4, #7f00ff);
        width: 50px;
        height: 50px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 26px;
        font-weight: bold;
        color: white;
        box-shadow: 0 0 15px rgba(0,245,212,0.5);
    }
    
    .logo-text {
        font-size: 28px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 2px;
        background: linear-gradient(90deg, #00f5d4, #ff9f1c, #ff5722);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .kpi-card {
        background: linear-gradient(135deg, #1f4068, #1b1b2f);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        color: white;
        text-align: center;
        border: 1px solid #00f5d4;
    }
    .kpi-title {
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #00f5d4 !important;
        margin-bottom: 8px;
        font-weight: 700;
    }
    .kpi-value {
        font-size: 22px;
        font-weight: bold;
        color: #ffffff !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #00f5d4 !important;
    }
    </style>

    <div class="logo-container">
        <div class="logo-badge">💎</div>
        <div class="logo-text">EliteLiving</div>
    </div>
""", unsafe_allow_html=True)

# Load Data and Clean text to Lowercase inside app directly
@st.cache_data
def load_and_clean_data():
    df = pd.read_csv("Sales_transactions_2022_2025 (1).csv")
    
    text_cols = [
        'Customer_Name', 'Customer_Gender', 'Customer_Segment', 'Sales_Channel', 
        'Store_Name', 'Country', 'Region', 'City', 'Product_Name', 
        'Product_Category', 'Product_Subcategory', 'Payment_Method', 
        'Order_Status', 'Shipping_Method', 'Return_Flag', 'Return_Reason', 
        'Sales_Representative', 'Promotion_Code'
    ]
    
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.lower().str.strip().replace(['nan', 'none'], 'unknown')
            
    # Debit / Credit Card merge logic using pattern matching
    if 'Payment_Method' in df.columns:
        df.loc[df['Payment_Method'].str.contains('debit', na=False), 'Payment_Method'] = 'debit card'
        df.loc[df['Payment_Method'].str.contains('credit', na=False), 'Payment_Method'] = 'credit card'
            
    df['Order_Date'] = pd.to_datetime(df['Order_Date'])
    return df

df = load_and_clean_data()

# Centered Filter Options
st.subheader("🔍 filter options")
f_col1, f_col2, f_col3 = st.columns([1, 2, 1])

with f_col2:
    selected_year = st.selectbox("select year", options=sorted(df['Order_Year'].unique()))
    selected_category = st.selectbox("select product category", options=["all"] + list(df['Product_Category'].unique()))

st.markdown("---")

# Filter Data based on selection
filtered_df = df[df['Order_Year'] == selected_year]
if selected_category != "all":
    filtered_df = filtered_df[filtered_df['Product_Category'] == selected_category]

# KPI CALCULATIONS
total_sales = filtered_df['Sales_Amount'].sum()
total_profit = filtered_df['Profit'].sum()
total_orders = filtered_df['Transaction_ID'].nunique()
avg_rating = filtered_df['Customer_Rating'].mean()
if pd.isna(avg_rating):
    avg_rating = 0.0

# ---------------------------------------------------------
# 1. KPI CARDS SECTION
# ---------------------------------------------------------
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">total sales</div>
            <div class="kpi-value">₹{total_sales:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">total profit</div>
            <div class="kpi-value">₹{total_profit:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">total orders</div>
            <div class="kpi-value">{total_orders:,}</div>
        </div>
    """, unsafe_allow_html=True)

with kpi4:
    rating_str = f"{avg_rating:.2f} / 5.0" if avg_rating > 0 else "n/a"
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">avg customer rating</div>
            <div class="kpi-value">{rating_str}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------------
# 2. 4 COLOURFUL GAUGES SECTION
# ---------------------------------------------------------
st.subheader("🎯 performance gauges")

g1, g2, g3, g4 = st.columns(4)

with g1:
    fig_sales = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = total_sales,
        number = {'prefix': "₹", 'valueformat': ",.0f", 'font': {'size': 14, 'color': 'white'}},
        title = {'text': "total sales", 'font': {'size': 14, 'color': '#00f5d4'}},
        gauge = {
            'axis': {'range': [0, 5000000], 'tickfont': {'color': 'white', 'size': 10}},
            'bar': {'color': "#00f5d4"},
            'steps': [{'range': [0, 2500000], 'color': "#1a1a2e"}, {'range': [2500000, 5000000], 'color': "#0f3460"}]
        }
    ))
    fig_sales.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), height=200, margin=dict(t=30, b=10, l=10, r=10))
    st.plotly_chart(fig_sales, use_container_width=True)

with g2:
    fig_profit = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = total_profit,
        number = {'prefix': "₹", 'valueformat': ",.0f", 'font': {'size': 14, 'color': 'white'}},
        title = {'text': "total profit", 'font': {'size': 14, 'color': '#00f5d4'}},
        gauge = {
            'axis': {'range': [0, 1000000], 'tickfont': {'color': 'white', 'size': 10}},
            'bar': {'color': "#2ec4b6"},
            'steps': [{'range': [0, 500000], 'color': "#1b262c"}, {'range': [500000, 1000000], 'color': "#3282b8"}]
        }
    ))
    fig_profit.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), height=200, margin=dict(t=30, b=10, l=10, r=10))
    st.plotly_chart(fig_profit, use_container_width=True)

with g3:
    fig_orders = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = total_orders,
        number = {'valueformat': ",.0f", 'font': {'size': 16, 'color': 'white'}},
        title = {'text': "total orders", 'font': {'size': 14, 'color': '#00f5d4'}},
        gauge = {
            'axis': {'range': [0, 10000], 'tickfont': {'color': 'white', 'size': 10}},
            'bar': {'color': "#ff9f1c"},
            'steps': [{'range': [0, 5000], 'color': "#2d132c"}, {'range': [5000, 10000], 'color': "#801336"}]
        }
    ))
    fig_orders.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), height=200, margin=dict(t=30, b=10, l=10, r=10))
    st.plotly_chart(fig_orders, use_container_width=True)

with g4:
    fig_rating = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = avg_rating,
        number = {'valueformat': ".2f", 'suffix': " / 5", 'font': {'size': 14, 'color': 'white'}},
        title = {'text': "customer rating", 'font': {'size': 14, 'color': '#00f5d4'}},
        gauge = {
            'axis': {'range': [0, 5], 'tickfont': {'color': 'white', 'size': 10}},
            'bar': {'color': "#ff5722"},
            'steps': [{'range': [0, 2.5], 'color': "#362fd9"}, {'range': [2.5, 5], 'color': "#780016"}]
        }
    ))
    fig_rating.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), height=200, margin=dict(t=30, b=10, l=10, r=10))
    st.plotly_chart(fig_rating, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------
# 3. OTHER GRAPHS SECTION
# ---------------------------------------------------------

st.subheader("📈 top product categories by sales")
cat_sales = filtered_df.groupby('Product_Category')['Sales_Amount'].sum().reset_index()
fig_cat = go.Figure(data=[
    go.Bar(
        x=cat_sales['Product_Category'],
        y=cat_sales['Sales_Amount'],
        marker_color='#00adb5'
    )
])
fig_cat.update_layout(xaxis_title="product category", yaxis_title="sales amount (₹)", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
st.plotly_chart(fig_cat, use_container_width=True)

st.markdown("---")

st.subheader("📉 sales trend over months")
filtered_df['Month'] = filtered_df['Order_Date'].dt.to_period('M').astype(str)
monthly_sales = filtered_df.groupby('Month')['Sales_Amount'].sum().reset_index()
fig_time = px.line(monthly_sales, x='Month', y='Sales_Amount', markers=True)
fig_time.update_layout(xaxis_title="month", yaxis_title="sales amount (₹)", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
st.plotly_chart(fig_time, use_container_width=True)

st.markdown("---")

st.subheader("🌍 country-wise performance")
country_sales = filtered_df.groupby('Country')['Sales_Amount'].sum().reset_index()
fig_country = px.pie(country_sales, names='Country', values='Sales_Amount')
fig_country.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
st.plotly_chart(fig_country, use_container_width=True)

st.markdown("---")

st.subheader("🛒 sales channel share")
channel_sales = filtered_df.groupby('Sales_Channel')['Sales_Amount'].sum().reset_index()
fig_channel = px.pie(channel_sales, names='Sales_Channel', values='Sales_Amount', hole=0.4)
fig_channel.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
st.plotly_chart(fig_channel, use_container_width=True)

st.markdown("---")

st.subheader("👥 customer segment sales")
segment_sales = filtered_df.groupby('Customer_Segment')['Sales_Amount'].sum().reset_index()
fig_segment = go.Figure(data=[
    go.Bar(
        x=segment_sales['Customer_Segment'],
        y=segment_sales['Sales_Amount'],
        marker_color='#ff9f1c'
    )
])
fig_segment.update_layout(xaxis_title="customer segment", yaxis_title="sales amount (₹)", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
st.plotly_chart(fig_segment, use_container_width=True)

st.markdown("---")

st.subheader("💳 payment methods analysis")
payment_sales = filtered_df.groupby('Payment_Method')['Sales_Amount'].sum().reset_index()
fig_payment = go.Figure(data=[
    go.Bar(
        x=payment_sales['Payment_Method'],
        y=payment_sales['Sales_Amount'],
        marker_color='#2ec4b6'
    )
])
fig_payment.update_layout(xaxis_title="payment method", yaxis_title="sales amount (₹)", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
st.plotly_chart(fig_payment, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------
# 4. SCATTER PLOT SECTION
# ---------------------------------------------------------
st.subheader("📊 scatter plot: quantity vs sales amount")
fig_scatter = px.scatter(
    filtered_df, 
    x='Quantity', 
    y='Sales_Amount', 
    color='Product_Category',
    hover_name='Customer_Name',
    opacity=0.7
)
fig_scatter.update_layout(
    xaxis_title="quantity", 
    yaxis_title="sales amount (₹)", 
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)', 
    font=dict(color='white')
)
st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------
# 5. BOX PLOT SECTION
# ---------------------------------------------------------
st.subheader("📦 box plot: profit distribution by product category")
fig_box = px.box(
    filtered_df, 
    x='Product_Category', 
    y='Profit', 
    color='Product_Category'
)
fig_box.update_layout(
    xaxis_title="product category", 
    yaxis_title="profit (₹)", 
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)', 
    font=dict(color='white'),
    showlegend=False
)
st.plotly_chart(fig_box, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------
# 6. FILTERED DATA TABLE SECTION
# ---------------------------------------------------------
st.subheader("📋 detailed transactions data table")
st.markdown("filtered records based on your selected year and category:")

st.dataframe(filtered_df, use_container_width=True)
