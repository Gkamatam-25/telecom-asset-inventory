"""
Telecom Asset and Inventory Analytics - Streamlit Dashboard
Author: Gowthami Kamatam
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings("ignore")

# Page config
st.set_page_config(
    page_title="Telecom Asset and Inventory Analytics",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f, #0d2137);
        border: 1px solid #1f6feb;
        border-radius: 12px;
        padding: 18px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("data/telecom_assets.csv",
                      parse_dates=["purchase_date", "warranty_expiry", "last_audit_date"])
    return df

df = load_data()

# Header
st.markdown("# Telecom Asset and Inventory Analytics Dashboard")
st.markdown("Asset lifecycle tracking, inventory valuation, and audit compliance monitoring")
st.divider()

# Sidebar filters
with st.sidebar:
    st.markdown("## Filters")

    sites = st.multiselect(
        "Site",
        options=sorted(df["site"].unique()),
        default=[]
    )

    asset_types = st.multiselect(
        "Asset Type",
        options=sorted(df["asset_type"].unique()),
        default=[]
    )

    statuses = st.multiselect(
        "Status",
        options=sorted(df["status"].unique()),
        default=[]
    )

    lifecycle_filter = st.multiselect(
        "Lifecycle Stage",
        options=["New", "Active", "Aging", "End of Life - Plan Replace", "End of Support"],
        default=[]
    )

# Apply filters
filtered_df = df.copy()
if sites:
    filtered_df = filtered_df[filtered_df["site"].isin(sites)]
if asset_types:
    filtered_df = filtered_df[filtered_df["asset_type"].isin(asset_types)]
if statuses:
    filtered_df = filtered_df[filtered_df["status"].isin(statuses)]
if lifecycle_filter:
    filtered_df = filtered_df[filtered_df["lifecycle_stage"].isin(lifecycle_filter)]

# TABS
tab1, tab2, tab3, tab4 = st.tabs([
    "Overview",
    "Lifecycle and Warranty",
    "Sites and Manufacturers",
    "Replacement Planning"
])

# TAB 1: OVERVIEW
with tab1:
    st.markdown("## Key Inventory Metrics")

    col1, col2, col3, col4 = st.columns(4)

    total_assets = len(filtered_df)
    total_value = filtered_df["unit_cost"].sum()
    avg_cost = filtered_df["unit_cost"].mean()
    needs_audit = filtered_df["needs_audit"].sum()

    with col1:
        st.metric("Total Assets", f"{total_assets:,}")
    with col2:
        st.metric("Total Inventory Value", f"${total_value:,.0f}")
    with col3:
        st.metric("Average Asset Cost", f"${avg_cost:,.0f}")
    with col4:
        st.metric("Assets Needing Audit", f"{needs_audit:,}")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Assets by Status")
        status_counts = filtered_df["status"].value_counts()
        fig_status = go.Figure(go.Pie(
            labels=status_counts.index, values=status_counts.values,
            hole=0.4,
            marker_colors=["#3fb950", "#d29922", "#58a6ff", "#f85149"]
        ))
        fig_status.update_layout(
            paper_bgcolor="#0e1117", font_color="#e6edf3",
            height=320, margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_status, use_container_width=True)

    with col2:
        st.markdown("### Inventory Value by Asset Type")
        type_value = filtered_df.groupby("asset_type")["unit_cost"].sum().sort_values(ascending=True).reset_index()
        fig_type_value = go.Figure(go.Bar(
            x=type_value["unit_cost"], y=type_value["asset_type"],
            orientation="h", marker_color="#58a6ff"
        ))
        fig_type_value.update_layout(
            paper_bgcolor="#0e1117", plot_bgcolor="#161b22",
            font_color="#e6edf3", height=320,
            margin=dict(t=20, b=20, l=20, r=20),
            xaxis_title="Total Value ($)"
        )
        st.plotly_chart(fig_type_value, use_container_width=True)

    st.markdown("### Purchases by Year")
    yearly = filtered_df.groupby(filtered_df["purchase_date"].dt.year).agg(
        asset_count=("asset_id", "count"),
        total_spend=("unit_cost", "sum")
    ).reset_index()
    yearly.columns = ["year", "asset_count", "total_spend"]

    fig_yearly = go.Figure()
    fig_yearly.add_trace(go.Bar(
        x=yearly["year"], y=yearly["total_spend"],
        marker_color="#a371f7", name="Total Spend"
    ))
    fig_yearly.update_layout(
        paper_bgcolor="#0e1117", plot_bgcolor="#161b22",
        font_color="#e6edf3", height=300,
        margin=dict(t=20, b=20, l=20, r=20),
        xaxis_title="Purchase Year", yaxis_title="Total Spend ($)"
    )
    st.plotly_chart(fig_yearly, use_container_width=True)

# TAB 2: LIFECYCLE AND WARRANTY
with tab2:
    st.markdown("## Lifecycle Stage and Warranty Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Assets by Lifecycle Stage")
        lifecycle_order = ["New", "Active", "Aging", "End of Life - Plan Replace", "End of Support"]
        lifecycle_counts = filtered_df["lifecycle_stage"].value_counts().reindex(lifecycle_order).fillna(0)

        colors = {"New": "#3fb950", "Active": "#58a6ff", "Aging": "#d29922",
                  "End of Life - Plan Replace": "#f85149", "End of Support": "#8b2635"}

        fig_lifecycle = go.Figure(go.Bar(
            x=lifecycle_counts.index, y=lifecycle_counts.values,
            marker_color=[colors[s] for s in lifecycle_counts.index],
            text=lifecycle_counts.values, textposition="auto"
        ))
        fig_lifecycle.update_layout(
            paper_bgcolor="#0e1117", plot_bgcolor="#161b22",
            font_color="#e6edf3", height=350,
            margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_lifecycle, use_container_width=True)

    with col2:
        st.markdown("### Warranty Status")
        warranty_counts = filtered_df["warranty_active"].value_counts()
        labels = ["Under Warranty" if k else "Warranty Expired" for k in warranty_counts.index]
        fig_warranty = go.Figure(go.Pie(
            labels=labels, values=warranty_counts.values,
            hole=0.4, marker_colors=["#3fb950", "#f85149"]
        ))
        fig_warranty.update_layout(
            paper_bgcolor="#0e1117", font_color="#e6edf3",
            height=350, margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_warranty, use_container_width=True)

    st.markdown("### Average Utilization by Asset Type (Active Assets)")
    active_df = filtered_df[filtered_df["status"] == "Active"]
    util_summary = active_df.groupby("asset_type")["utilization_pct"].mean().sort_values(ascending=True).reset_index()

    fig_util = go.Figure(go.Bar(
        x=util_summary["utilization_pct"], y=util_summary["asset_type"],
        orientation="h", marker_color="#3fb950"
    ))
    fig_util.update_layout(
        paper_bgcolor="#0e1117", plot_bgcolor="#161b22",
        font_color="#e6edf3", height=350,
        margin=dict(t=20, b=20, l=20, r=20),
        xaxis_title="Average Utilization (%)"
    )
    st.plotly_chart(fig_util, use_container_width=True)

# TAB 3: SITES AND MANUFACTURERS
with tab3:
    st.markdown("## Site and Manufacturer Breakdown")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Inventory Value by Site")
        site_value = filtered_df.groupby("site")["unit_cost"].sum().sort_values(ascending=False).head(8).reset_index()

        fig_site = go.Figure(go.Bar(
            x=site_value["site"], y=site_value["unit_cost"],
            marker_color="#58a6ff"
        ))
        fig_site.update_layout(
            paper_bgcolor="#0e1117", plot_bgcolor="#161b22",
            font_color="#e6edf3", height=380,
            margin=dict(t=20, b=20, l=20, r=20),
            yaxis_title="Total Value ($)"
        )
        st.plotly_chart(fig_site, use_container_width=True)

    with col2:
        st.markdown("### Asset Count by Manufacturer")
        manufacturer_counts = filtered_df["manufacturer"].value_counts().reset_index()
        manufacturer_counts.columns = ["manufacturer", "count"]

        fig_manuf = go.Figure(go.Pie(
            labels=manufacturer_counts["manufacturer"],
            values=manufacturer_counts["count"],
            hole=0.35
        ))
        fig_manuf.update_layout(
            paper_bgcolor="#0e1117", font_color="#e6edf3",
            height=380, margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_manuf, use_container_width=True)

    st.markdown("### Audit Compliance by Site")
    audit_summary = filtered_df.groupby("site").agg(
        total_assets=("asset_id", "count"),
        overdue=("needs_audit", "sum")
    ).reset_index()
    audit_summary["pct_overdue"] = (audit_summary["overdue"] / audit_summary["total_assets"] * 100).round(1)
    audit_summary = audit_summary.sort_values("pct_overdue", ascending=False)

    fig_audit = go.Figure(go.Bar(
        x=audit_summary["site"], y=audit_summary["pct_overdue"],
        marker_color=["#f85149" if v >= 50 else "#d29922" for v in audit_summary["pct_overdue"]],
        text=[f"{v}%" for v in audit_summary["pct_overdue"]], textposition="auto"
    ))
    fig_audit.add_hline(y=50, line_dash="dash", line_color="#8b949e",
                        annotation_text="50% threshold")
    fig_audit.update_layout(
        paper_bgcolor="#0e1117", plot_bgcolor="#161b22",
        font_color="#e6edf3", height=320,
        margin=dict(t=20, b=20, l=20, r=20),
        yaxis_title="Percent Overdue for Audit"
    )
    st.plotly_chart(fig_audit, use_container_width=True)

# TAB 4: REPLACEMENT PLANNING
with tab4:
    st.markdown("## Replacement Planning and End of Life Tracking")

    eol_df = filtered_df[filtered_df["lifecycle_stage"].isin(
        ["End of Life - Plan Replace", "End of Support"]
    )]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Assets Needing Replacement", f"{len(eol_df):,}")
    with col2:
        st.metric("Total Replacement Value", f"${eol_df['unit_cost'].sum():,.0f}")
    with col3:
        pct_of_fleet = (len(eol_df) / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
        st.metric("Percent of Fleet", f"{pct_of_fleet:.1f}%")

    st.divider()

    st.markdown("### Top Site and Asset Type Combinations Needing Replacement")
    eol_summary = eol_df.groupby(["site", "asset_type"]).agg(
        asset_count=("asset_id", "count"),
        replacement_value=("unit_cost", "sum")
    ).sort_values("replacement_value", ascending=False).head(10).reset_index()

    fig_eol = go.Figure(go.Bar(
        x=eol_summary["replacement_value"],
        y=[f"{row['site']} - {row['asset_type']}" for _, row in eol_summary.iterrows()],
        orientation="h", marker_color="#f85149"
    ))
    fig_eol.update_layout(
        paper_bgcolor="#0e1117", plot_bgcolor="#161b22",
        font_color="#e6edf3", height=400,
        margin=dict(t=20, b=20, l=20, r=20),
        xaxis_title="Replacement Value ($)"
    )
    st.plotly_chart(fig_eol, use_container_width=True)

    st.markdown("### Asset Records (Filtered)")
    st.dataframe(
        filtered_df[["asset_id", "asset_type", "manufacturer", "site",
                     "status", "lifecycle_stage", "unit_cost",
                     "warranty_active", "needs_audit"]].head(100),
        use_container_width=True,
        height=400
    )
