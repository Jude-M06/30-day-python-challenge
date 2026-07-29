#---------------------------------------------------
# you need to install streamlit plotly pandas first
# python -m pip install streamlit plotly pandas
#---------------------------------------------------

import io
from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Expense Dashboard",
    page_icon="💰",
    layout="wide",
)


SAMPLE = pd.DataFrame([
    {"date": "2025-06-01", "category": "Food",          "amount": 12.50, "description": "Lunch"},
    {"date": "2025-06-01", "category": "Transport",     "amount": 3.20,  "description": "Bus fare"},
    {"date": "2025-06-02", "category": "Food",          "amount": 45.00, "description": "Groceries"},
    {"date": "2025-06-03", "category": "Entertainment", "amount": 9.99,  "description": "Streaming"},
    {"date": "2025-06-04", "category": "Food",          "amount": 8.75,  "description": "Coffee"},
    {"date": "2025-06-04", "category": "Transport",     "amount": 22.00, "description": "Train"},
    {"date": "2025-06-05", "category": "Health",        "amount": 35.00, "description": "Gym"},
    {"date": "2025-06-06", "category": "Entertainment", "amount": 15.00, "description": "Cinema"},
    {"date": "2025-06-07", "category": "Food",          "amount": 60.00, "description": "Weekly shop"},
    {"date": "2025-06-08", "category": "Transport",     "amount": 3.20,  "description": "Bus fare"},
])

@st.cache_data
def load_csv(file) -> pd.DataFrame:
    df = pd.read_csv(file)
    df.columns = df.columns.str.lower().str.strip()
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["date"]   = pd.to_datetime(df["date"],   errors="coerce")
    return df.dropna(subset=["amount"])

def prep_sample() -> pd.DataFrame:
    df = SAMPLE.copy()
    df["date"]   = pd.to_datetime(df["date"])
    df["amount"] = df["amount"].astype(float)
    return df


with st.sidebar:
    st.title("⚙️ Filters")

    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    df_raw = load_csv(uploaded) if uploaded else prep_sample()

    if uploaded:
        st.success(f"Loaded {len(df_raw):,} rows from {uploaded.name}")
    else:
        st.info("Using sample expense data.")

    st.divider()

    
    all_cats = sorted(df_raw["category"].dropna().unique().tolist())
    selected_cats = st.multiselect("Categories", all_cats, default=all_cats)

    
    min_date = df_raw["date"].min().date()
    max_date = df_raw["date"].max().date()
    date_range = st.date_input("Date range", [min_date, max_date])

    
    max_amt = float(df_raw["amount"].max())
    amt_range = st.slider("Amount range (£)", 0.0, max_amt, (0.0, max_amt), step=0.5)


df = df_raw.copy()
if selected_cats:
    df = df[df["category"].isin(selected_cats)]
if len(date_range) == 2:
    df = df[
        (df["date"].dt.date >= date_range[0]) &
        (df["date"].dt.date <= date_range[1])
    ]
df = df[(df["amount"] >= amt_range[0]) & (df["amount"] <= amt_range[1])]


st.title("💰 Expense Dashboard")
st.caption(f"Showing {len(df):,} of {len(df_raw):,} transactions")

if df.empty:
    st.warning("No data matches your filters — try adjusting them.")
    st.stop()


total    = df["amount"].sum()
avg_tx   = df["amount"].mean()
top_cat  = df.groupby("category")["amount"].sum().idxmax()
tx_count = len(df)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Spent",       f"£{total:,.2f}")
col2.metric("Transactions",      f"{tx_count:,}")
col3.metric("Avg per Transaction", f"£{avg_tx:.2f}")
col4.metric("Top Category",      top_cat)

st.divider()


col_a, col_b = st.columns(2)

with col_a:
    by_cat = df.groupby("category")["amount"].sum().reset_index()
    by_cat = by_cat.sort_values("amount", ascending=False)
    fig_bar = px.bar(
        by_cat, x="category", y="amount",
        title="Spending by Category",
        labels={"amount": "Amount (£)", "category": ""},
        color="amount", color_continuous_scale="blues",
    )
    fig_bar.update_layout(showlegend=False, coloraxis_showscale=False)
    st.plotly_chart(fig_bar, use_container_width=True)

with col_b:
    fig_pie = px.pie(
        by_cat, names="category", values="amount",
        title="Spending Proportion",
        hole=0.35,
    )
    st.plotly_chart(fig_pie, use_container_width=True)


df_time = (
    df.set_index("date")
    .resample("D")["amount"]
    .sum()
    .reset_index()
)
fig_line = px.line(
    df_time, x="date", y="amount",
    title="Daily Spending Over Time",
    labels={"amount": "Amount (£)", "date": "Date"},
    markers=True,
)
fig_line.update_traces(line_color="#2563eb")
st.plotly_chart(fig_line, use_container_width=True)


with st.expander("📋 Raw transaction data"):
    st.dataframe(
        df.sort_values("date", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download filtered data as CSV",
        data=csv_bytes,
        file_name="filtered_expenses.csv",
        mime="text/csv",
    )