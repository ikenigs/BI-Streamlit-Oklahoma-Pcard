"""
ALY 6110 – Assignment 4: PCard Spending Dashboard (Tasks 5 & 6)
Oklahoma State Purchasing Card Transactions — Aug 2023 to Jul 2024

Run: streamlit run dashboard.py
"""

import glob
import os

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Oklahoma PCard Dashboard",
    page_icon="💳",
    layout="wide",
)

# ── Data loading ─────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_data(show_spinner="Loading PCard data…")
def load_data():
    parquet_path = os.path.join(SCRIPT_DIR, "pcard_clean.parquet")
    if os.path.exists(parquet_path):
        df = pd.read_parquet(parquet_path)
        df["TRANSACTION_DATE"] = pd.to_datetime(df["TRANSACTION_DATE"], errors="coerce")
        df = df[df["YEAR_MONTH"] >= "2023-07"]
    else:
        files = sorted(glob.glob(os.path.join(SCRIPT_DIR, "Dataset", "pcard_public_*.csv")))
        dfs = []
        for f in files:
            chunk = pd.read_csv(f, encoding="utf-8", low_memory=False)
            dfs.append(chunk)
        df = pd.concat(dfs, ignore_index=True)
        str_cols = df.select_dtypes("object").columns
        df[str_cols] = df[str_cols].apply(lambda s: s.str.strip())
        df["TRANSACTION_DATE"] = pd.to_datetime(df["TRANSACTION_DATE"], format="%d-%b-%y", errors="coerce")
        df["AMOUNT"] = pd.to_numeric(df["AMOUNT"], errors="coerce")
        df["YEAR_MONTH"] = df["TRANSACTION_DATE"].dt.to_period("M").astype(str)
        df["MONTH_NAME"] = df["TRANSACTION_DATE"].dt.strftime("%b %Y")
        df = df.dropna(subset=["AMOUNT"])
        df = df[df["YEAR_MONTH"] >= "2023-07"]

    df = df[df["AMOUNT"] > 0].copy()  # purchases only
    return df


df = load_data()

# ── Sidebar — Filters ────────────────────────────────────────────────────────
st.sidebar.header("Filters")

all_months = sorted(df["YEAR_MONTH"].dropna().unique().tolist())
sel_months = st.sidebar.multiselect(
    "Month(s)",
    options=all_months,
    default=all_months,
    help="Select one or more months to include in all charts.",
)

all_agencies = sorted(df["AGENCYNAME"].dropna().unique().tolist())
sel_agencies = st.sidebar.multiselect(
    "Agency / Department",
    options=all_agencies,
    default=[],
    placeholder="All agencies",
    help="Leave blank to show all agencies.",
)

top_n = st.sidebar.slider("Top N for bar charts", min_value=5, max_value=25, value=10, step=1)

# Apply filters
mask = df["YEAR_MONTH"].isin(sel_months)
if sel_agencies:
    mask &= df["AGENCYNAME"].isin(sel_agencies)
filtered = df[mask]

# ── Header ───────────────────────────────────────────────────────────────────
st.title("💳 Oklahoma State PCard Spending Dashboard")
st.caption(
    "Purchase card transactions across Oklahoma state agencies — Aug 2023 to Jul 2024.  "
    "Use the sidebar to filter by month or agency."
)
st.markdown("---")

# ── KPI Cards (Task 5 — element 1) ──────────────────────────────────────────
# Explanation (Task 6): Four headline metrics give an at-a-glance summary of the
# filtered dataset. They answer "how big is this spend?" without requiring the
# user to read any chart, supporting the overall research question.
k1, k2, k3, k4 = st.columns(4)

total_spend = filtered["AMOUNT"].sum()
tx_count = len(filtered)
avg_tx = filtered["AMOUNT"].mean() if tx_count > 0 else 0
n_agencies = filtered["AGENCYNAME"].nunique()

k1.metric("Total Spend", f"${total_spend:,.0f}")
k2.metric("Transactions", f"{tx_count:,}")
k3.metric("Avg Transaction", f"${avg_tx:,.2f}")
k4.metric("Agencies Active", f"{n_agencies:,}")

st.markdown("---")

# ── Row 1: Line chart + Bar chart ────────────────────────────────────────────
col_left, col_right = st.columns([1.4, 1])

# Element 2 — Line chart: Monthly spend trend
# Explanation (Task 6): Shows how total PCard spend evolves month-over-month.
# This directly addresses the research question about temporal patterns and
# reveals the spring fiscal-year-end spending surge (Insight 2).
with col_left:
    st.subheader("Monthly Spend Trend")
    st.caption(
        "**What it shows:** Total purchase-card spend per calendar month.  "
        "**Insight supported:** Spending rises sharply in spring (Mar–May) as agencies "
        "exhaust fiscal-year budgets before the June 30 close."
    )
    monthly = (
        filtered.groupby("YEAR_MONTH")["AMOUNT"]
        .agg(total_spend="sum", tx_count="count")
        .reset_index()
        .sort_values("YEAR_MONTH")
    )
    fig_line = go.Figure()
    fig_line.add_trace(
        go.Scatter(
            x=monthly["YEAR_MONTH"],
            y=monthly["total_spend"],
            mode="lines+markers",
            name="Total Spend",
            line=dict(color="#4C72B0", width=3),
            marker=dict(size=7),
            hovertemplate="<b>%{x}</b><br>Spend: $%{y:,.0f}<extra></extra>",
        )
    )
    fig_line.update_layout(
        yaxis_tickformat="$,.0f",
        yaxis_title="Spend ($)",
        xaxis_title="",
        height=340,
        margin=dict(l=10, r=10, t=10, b=10),
        hovermode="x unified",
    )
    st.plotly_chart(fig_line, width='stretch')

# Element 3 — Bar chart: Top N agencies
# Explanation (Task 6): Ranks agencies by total PCard spend. This directly
# identifies which departments drive the budget (Insight 1) and helps auditors
# prioritise oversight attention.
with col_right:
    st.subheader(f"Top {top_n} Agencies by Spend")
    st.caption(
        f"**What it shows:** The {top_n} highest-spending agencies in the selected period.  "
        "**Insight supported:** Spending is concentrated — a handful of agencies account "
        "for the majority of all PCard dollars (Insight 1)."
    )
    top_ag = (
        filtered.groupby("AGENCYNAME")["AMOUNT"]
        .sum()
        .nlargest(top_n)
        .reset_index()
        .sort_values("AMOUNT")
    )
    top_ag["SHORT"] = top_ag["AGENCYNAME"].str[:35]
    fig_bar = px.bar(
        top_ag,
        x="AMOUNT",
        y="SHORT",
        orientation="h",
        color="AMOUNT",
        color_continuous_scale="Blues",
        labels={"AMOUNT": "Total Spend ($)", "SHORT": ""},
        hover_data={"AGENCYNAME": True, "AMOUNT": ":$,.0f", "SHORT": False},
    )
    fig_bar.update_layout(
        height=340,
        margin=dict(l=10, r=10, t=10, b=10),
        coloraxis_showscale=False,
        xaxis_tickformat="$,.0f",
    )
    st.plotly_chart(fig_bar, width='stretch')

st.markdown("---")

# ── Row 2: Pie chart + Heatmap ───────────────────────────────────────────────
col_pie, col_heat = st.columns([1, 1.5])

# Element 4 — Pie chart: MCC category share
# Explanation (Task 6): Shows the proportional breakdown of spend by Merchant
# Category Code. Reveals which purchasing categories dominate (Insight 3) and
# highlights whether spend is diverse or concentrated in a few categories.
with col_pie:
    st.subheader("Spend by Merchant Category")
    st.caption(
        "**What it shows:** Share of total spend for each MCC category (top 10).  "
        "**Insight supported:** IT/technology and travel-related MCCs absorb a "
        "disproportionate share of PCard spend (Insight 3)."
    )
    mcc_data = (
        filtered.groupby("MCC_DESCRIPTION")["AMOUNT"]
        .sum()
        .nlargest(10)
        .reset_index()
    )
    mcc_data["MCC_SHORT"] = mcc_data["MCC_DESCRIPTION"].str[:40]
    fig_pie = px.pie(
        mcc_data,
        values="AMOUNT",
        names="MCC_SHORT",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_pie.update_traces(
        textposition="inside",
        textinfo="percent",
        hovertemplate="<b>%{label}</b><br>Spend: $%{value:,.0f}<br>Share: %{percent}<extra></extra>",
    )
    fig_pie.update_layout(
        height=380,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(font=dict(size=9)),
        showlegend=True,
    )
    st.plotly_chart(fig_pie, width='stretch')

# Element 5 — Heatmap: Agency × Month
# Explanation (Task 6): A two-dimensional heatmap crosses the top agencies
# against each month, making seasonal bursts and agency-specific patterns
# immediately visible. It supports both Insight 1 (concentration) and
# Insight 2 (seasonality) simultaneously.
with col_heat:
    st.subheader("Monthly Spend Heatmap — Top Agencies")
    st.caption(
        "**What it shows:** Monthly spend for the top agencies; darker cells = higher spend.  "
        "**Insight supported:** Combines Insight 1 (agency concentration) and Insight 2 "
        "(seasonal peaks) in a single view."
    )
    top10_ags = (
        filtered.groupby("AGENCYNAME")["AMOUNT"].sum().nlargest(10).index.tolist()
    )
    heat_df = (
        filtered[filtered["AGENCYNAME"].isin(top10_ags)]
        .groupby(["AGENCYNAME", "YEAR_MONTH"])["AMOUNT"]
        .sum()
        .unstack("YEAR_MONTH")
        .fillna(0)
        .sort_index()
    )
    heat_df.index = heat_df.index.str[:35]
    heat_df.columns = heat_df.columns.astype(str)

    fig_heat = px.imshow(
        heat_df / 1e6,
        color_continuous_scale="YlOrRd",
        labels=dict(x="Month", y="", color="Spend ($M)"),
        text_auto=".1f",
        aspect="auto",
    )
    fig_heat.update_layout(
        height=380,
        margin=dict(l=10, r=10, t=10, b=10),
        coloraxis_colorbar=dict(title="$M"),
    )
    st.plotly_chart(fig_heat, width='stretch')

st.markdown("---")

# ── Row 3: Scatter plot ──────────────────────────────────────────────────────
# Element 6 — Scatter plot: Transactions vs. Spend per agency
# Explanation (Task 6): Plots each agency as a point with transaction count on
# the x-axis and total spend on the y-axis. Agencies far above the trend line
# make fewer but larger purchases — a signal for potential policy violations or
# procurement bypasses.
st.subheader("Agency Transactions vs. Total Spend")
st.caption(
    "**What it shows:** Each dot is an agency; position reveals whether high spend comes "
    "from many small purchases or a few large ones.  "
    "**Insight supported:** Supports Insight 1 — outlier agencies above the regression "
    "line spend heavily with fewer transactions, indicating large individual purchases."
)

scatter_df = (
    filtered.groupby("AGENCYNAME")
    .agg(total_spend=("AMOUNT", "sum"), tx_count=("AMOUNT", "count"), avg_tx=("AMOUNT", "mean"))
    .reset_index()
)
scatter_df["SHORT"] = scatter_df["AGENCYNAME"].str[:30]

fig_scatter = px.scatter(
    scatter_df,
    x="tx_count",
    y="total_spend",
    hover_name="AGENCYNAME",
    hover_data={"tx_count": True, "total_spend": ":$,.0f", "avg_tx": ":$,.2f", "SHORT": False},
    size="total_spend",
    size_max=40,
    color="avg_tx",
    color_continuous_scale="Viridis",
    labels={
        "tx_count": "Number of Transactions",
        "total_spend": "Total Spend ($)",
        "avg_tx": "Avg Tx ($)",
    },
    trendline="ols",
    trendline_color_override="red",
)
fig_scatter.update_layout(
    height=420,
    margin=dict(l=10, r=10, t=10, b=10),
    yaxis_tickformat="$,.0f",
    coloraxis_colorbar=dict(title="Avg Tx ($)", tickformat="$,.0f"),
)
st.plotly_chart(fig_scatter, width='stretch')

st.markdown("---")

# ── Raw data explorer ─────────────────────────────────────────────────────────
with st.expander("View Filtered Transaction Data"):
    st.dataframe(
        filtered[["TRANSACTION_DATE", "AGENCYNAME", "MERCHANT", "MCC_DESCRIPTION", "AMOUNT"]]
        .sort_values("AMOUNT", ascending=False)
        .head(1000)
        .reset_index(drop=True),
        width='stretch',
    )
    st.caption(f"Showing up to 1,000 of {len(filtered):,} filtered rows.")

st.markdown(
    "<div style='text-align:center; color:gray; font-size:0.8em;'>"
    "ALY 6110 – Assignment 4 | Data: Oklahoma OMES PCard Public Records"
    "</div>",
    unsafe_allow_html=True,
)
