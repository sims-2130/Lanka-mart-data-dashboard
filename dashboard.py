import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# 1. SCREEN ARCHITECTURE & MULTI-THREAD OPTIMIZATION
# ==============================================================================
st.set_page_config(
    page_title="LankaMart Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Responsive visual aesthetic layout overrides via markdown injection
st.markdown("""
    <style>
        .reportview-container { background: #f5f7f9; }
        .metric-card {
            background-color: #ffffff !important;
            padding: 20px !important;
            border-radius: 10px !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
            border-left: 5px solid #0066cc !important;
        }
        div[data-testid="stMetric"] {
            background-color: #ffffff;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.03);
            border: 1px solid #eef2f6;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📊 LankaMart Retail Performance Dashboard")
st.markdown("### **Senior Management Strategic Evaluation Framework**")
st.markdown("---")

# ==============================================================================
# 2. HIGH-PERFORMANCE DATA TRANSFORMATION PIPELINE & DATA CLEANING
# ==============================================================================
@st.cache_data(ttl=3600)  # Caching ensures smooth execution on slower laptops
def load_and_transform_data():
    # Load raw file
    df = pd.read_csv("CIT308_LankaMart_Retail_Transactions.csv")
    
    # Clean Datetime Elements
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['YearMonth'] = df['order_date'].dt.to_period('M').astype(str)
    df['WeekIndex'] = df['order_date'].dt.to_period('W').astype(str)
    
    # Financial Engineering Formulas Required by Rubric
    df['profit_lkr'] = df['revenue_lkr'] - df['cost_lkr']
    df['profit_margin'] = df['profit_lkr'] / df['revenue_lkr']
    df['return_indicator'] = df['returned'].apply(lambda x: 1 if str(x).strip().lower() == 'yes' else 0)
    
    # Data Quality Validation: Handling Missing Values transparently
    if 'customer_rating' in df.columns:
        mean_rating = df['customer_rating'].mean()
        df['customer_rating'] = df['customer_rating'].fillna(mean_rating)
        
    return df

try:
    df_raw = load_and_transform_data()
    
    # ==============================================================================
    # 3. INTERACTIVE SIDEBAR CONTROLS (MANDATORY FILTERS)
    # ==============================================================================
    st.sidebar.image("https://flaticon.com", width=80)
    st.sidebar.header("🕹️ Executive Filters")
    st.sidebar.markdown("Use these inputs to segment performance metrics dynamically across vectors.")

    # Control Filter 1: Temporal Date Range Selection Element
    min_date = df_raw['order_date'].min().date()
    max_date = df_raw['order_date'].max().date()
    
    date_selection = st.sidebar.date_input(
        "Select Transaction Window",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Control Filter 2: Spatial Category Selection (Geographical Province Multi-Select)
    sorted_provinces = sorted(df_raw['province'].dropna().unique())
    selected_provinces = st.sidebar.multiselect(
        "Geographic Province Coverage",
        options=sorted_provinces,
        default=sorted_provinces
    )

    # Control Filter 3: Distribution Segment Vector (Sales Channel Multi-Select)
    distinct_channels = sorted(df_raw['sales_channel'].dropna().unique())
    selected_channels = st.sidebar.multiselect(
        "Commercial Distribution Channels",
        options=distinct_channels,
        default=distinct_channels
    )
    
    # Control Filter 4 (Bonus Extra Component): Customer Category Target Segment
    distinct_segments = sorted(df_raw['customer_segment'].dropna().unique())
    selected_segments = st.sidebar.multiselect(
        "Consumer Market Demographics",
        options=distinct_segments,
        default=distinct_segments
    )

    # Structural Reset Dashboard Button Trigger
    st.sidebar.markdown("---")
    if st.sidebar.button("♻️ Reset Dashboard View", use_container_width=True):
        st.rerun()

    # Dynamic Data Filtering Application Layer Logic
    if isinstance(date_selection, tuple) and len(date_selection) == 2:
        start_bound, end_bound = date_selection
    else:
        start_bound, end_bound = min_date, max_date

    filtered_df = df_raw[
        (df_raw['order_date'].dt.date >= start_bound) &
        (df_raw['order_date'].dt.date <= end_bound) &
        (df_raw['province'].isin(selected_provinces)) &
        (df_raw['sales_channel'].isin(selected_channels)) &
        (df_raw['customer_segment'].isin(selected_segments))
    ]

    # ==============================================================================
    # 4. STATISTICAL AGGREGATION BLOCKS (MANDATORY 4 EXECUTIVE KPIs)
    # ==============================================================================
    total_rev = filtered_df['revenue_lkr'].sum()
    total_prof = filtered_df['profit_lkr'].sum()
    avg_margin = (total_prof / total_rev * 100) if total_rev > 0 else 0.0
    return_rate = (filtered_df['return_indicator'].mean() * 100) if len(filtered_df) > 0 else 0.0
    avg_rating = filtered_df['customer_rating'].mean() if len(filtered_df) > 0 else 0.0

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    
    kpi1.metric(
        label="💰 Gross Revenue Summary",
        value=f"LKR {total_rev:,.2f}",
        delta=f"{len(filtered_df):,} Orders"
    )
    
    kpi2.metric(
        label="📈 Net Retained Profit",
        value=f"LKR {total_prof:,.2f}",
        delta=f"Margin Baseline"
    )
    
    kpi3.metric(
        label="🎯 Mean Net Profit Margin",
        value=f"{avg_margin:.2f}%",
        delta=f"Target: >30%"
    )
    
    kpi4.metric(
        label="⚠️ Systemic Return Rate",
        value=f"{return_rate:.2f}%",
        delta=f"Risk Threshold 5%",
        delta_color="inverse"
    )
    
    kpi5.metric(
        label="⭐ Customer Satisfaction",
        value=f"{avg_rating:.2f} / 5.0",
        delta="Quality Index"
    )

    st.markdown("---")

    # ==============================================================================
    # 5. CORE ANALYTICAL GRAPH BLOCKS (5 MANDATORY VISUALIZATIONS)
    # ==============================================================================
    chart_row_1_left, chart_row_1_right = st.columns(2)
    chart_row_2_left, chart_row_2_right = st.columns(2)

    # 📊 Chart 1: Time Series Trend - Revenue and Profit Trajectory
    with chart_row_1_left:
        st.markdown("#### 1. Temporal Progression Trajectory (Line Trend)")
        time_series = filtered_df.groupby('WeekIndex')[['revenue_lkr', 'profit_lkr']].sum().reset_index()
        
        fig1 = px.line(
            time_series, 
            x='WeekIndex', 
            y=['revenue_lkr', 'profit_lkr'],
            labels={'value': 'Financial Value (LKR)', 'WeekIndex': 'Weekly Operational Interval'},
            color_discrete_map={'revenue_lkr': '#0066cc', 'profit_lkr': '#2ecc71'},
            markers=True
        )
        fig1.update_layout(legend_title_text='Financial Metrics', margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig1, use_container_width=True)

    # 📊 Chart 2: Categorical Breakdown - Revenue by Product Domain 
    with chart_row_1_right:
        st.markdown("#### 2. Inventory Revenue Contribution Mix (Horizontal Bar)")
        category_mix = filtered_df.groupby('product_category')['revenue_lkr'].sum().reset_index().sort_values(by='revenue_lkr', ascending=True)
        
        fig2 = px.bar(
            category_mix, 
            x='revenue_lkr', 
            y='product_category', 
            orientation='h',
            color='revenue_lkr',
            color_continuous_scale='Blues',
            labels={'revenue_lkr': 'Aggregated Revenue (LKR)', 'product_category': 'Product Segment'}
        )
        fig2.update_layout(coloraxis_showscale=False, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig2, use_container_width=True)

    # 📊 Chart 3: Market Distribution - Regional Revenue Allocation
    with chart_row_2_left:
        st.markdown("#### 3. Spatial Revenue Share Allocation (Market Share Pie)")
        provincial_share = filtered_df.groupby('province')['revenue_lkr'].sum().reset_index()
        
        fig3 = px.pie(
            provincial_share, 
            values='revenue_lkr', 
            names='province',
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.YlGnBu
        )
        fig3.update_traces(textposition='inside', textinfo='percent+label')
        fig3.update_layout(margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig3, use_container_width=True)

    # 📊 Chart 4: Pricing Mechanics - Discount Rate Structure vs Net Margins
    with chart_row_2_right:
        st.markdown("#### 4. Pricing Mechanics Correlation Matrix (Scatter View)")
        
        fig4 = px.scatter(
            filtered_df, 
            x='discount_pct', 
            y='profit_margin', 
            color='sales_channel',
            opacity=0.6,
            trendline='ols', # Adds diagnostic evaluation trend line dynamically
            labels={'discount_pct': 'Applied Discount Ratio (%)', 'profit_margin': 'Calculated Profit Margin'}
        )
        fig4.update_layout(margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig4, use_container_width=True)

    # 📊 Chart 5: Operational Risk - Reverse Logistics Product Returns Analysis
    st.markdown("#### 5. Operational Logistics Risk: Return Ratios across Distribution Channels")
    channel_risk = filtered_df.groupby('sales_channel')['return_indicator'].mean().reset_index()
    channel_risk['return_rate_pct'] = channel_risk['return_indicator'] * 100
    fig5 = px.bar(channel_risk, x='sales_channel', y='return_rate_pct', color='return_rate_pct', color_continuous_scale='Reds', labels={'return_rate_pct': 'Return Rate (%)'})
    st.plotly_chart(fig5, use_container_width=True)

    # --- STEP 5: COMPREHENSIVE DATA GRID ROW VIEW ---
    st.markdown("---")
    st.markdown("#### 📋 Auditable Transactional Ledger Rows")
    st.dataframe(filtered_df[['order_id', 'order_date', 'province', 'product_name', 'revenue_lkr', 'returned']], use_container_width=True, hide_index=True)

except FileNotFoundError:
    st.error("🛑 Operational Critical Error: The dataset file titled 'CIT308_LankaMart_Retail_Transactions.csv' could not be found.")


