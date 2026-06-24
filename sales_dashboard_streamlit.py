"""
Sales Dashboard 2025 — Streamlit App
=====================================
Requirements:
    pip install streamlit pandas numpy matplotlib seaborn

Run:
    streamlit run sales_dashboard_streamlit.py

Place sales_2025.csv in the same folder as this script.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sales Dashboard 2025",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Dark background */
    .stApp { background-color: #0d0f14; }
    [data-testid="stSidebar"] { background-color: #161921; }
    .block-container { padding: 1.5rem 2rem 2rem; max-width: 1400px; }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: #161921;
        border: 1px solid #2a2f3d;
        border-radius: 10px;
        padding: 16px 20px;
    }
    [data-testid="stMetricLabel"] { font-size: 0.72rem; color: #8a8fa8 !important; text-transform: uppercase; letter-spacing: 0.7px; }
    [data-testid="stMetricValue"] { font-size: 1.55rem; color: #e8eaf0 !important; font-weight: 700; }
    [data-testid="stMetricDelta"] { font-size: 0.8rem; }

    h1, h2, h3 { color: #e8eaf0 !important; }
    .chart-title { font-size: 0.75rem; font-weight: 600; text-transform: uppercase;
                   letter-spacing: 0.7px; color: #8a8fa8; margin-bottom: 4px; }
</style>
""", unsafe_allow_html=True)

# ── Matplotlib theme ───────────────────────────────────────────────────────────
DARK_BG    = "#0d0f14"
SURFACE    = "#161921"
SURFACE2   = "#1e2230"
BORDER     = "#2a2f3d"
TEXT       = "#e8eaf0"
MUTED      = "#8a8fa8"
ACCENT     = "#4f8ef7"
ACCENT2    = "#7c5af0"
ACCENT3    = "#29d4a3"
ACCENT4    = "#f5a623"
RED        = "#f46a6a"
PALETTE    = [ACCENT, ACCENT3, ACCENT2, ACCENT4, RED]

plt.rcParams.update({
    "figure.facecolor": SURFACE,
    "axes.facecolor":   SURFACE,
    "axes.edgecolor":   BORDER,
    "axes.labelcolor":  MUTED,
    "xtick.color":      MUTED,
    "ytick.color":      MUTED,
    "text.color":       TEXT,
    "grid.color":       BORDER,
    "grid.linewidth":   0.6,
    "axes.spines.top":  False,
    "axes.spines.right":False,
    "axes.titlesize":   11,
    "axes.titlecolor":  MUTED,
    "font.family":      "sans-serif",
})

# ── Data loading ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("sales_2025.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    month_order = ["January","February","March","April","May","June",
                   "July","August","September","October","November","December"]
    df["Month"] = pd.Categorical(df["Month"], categories=month_order, ordered=True)
    return df

df = load_data()

# ── Sidebar filters ────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("📊 Filters")
    st.markdown("---")

    quarters = st.multiselect("Quarter", options=["Q1","Q2","Q3","Q4"],
                               default=["Q1","Q2","Q3","Q4"])
    regions = st.multiselect("Region",
                              options=df["Region"].unique().tolist(),
                              default=df["Region"].unique().tolist())
    salespersons = st.multiselect("Salesperson",
                                   options=df["Salesperson"].unique().tolist(),
                                   default=df["Salesperson"].unique().tolist())
    segments = st.multiselect("Customer Segment",
                               options=df["Customer Segment"].unique().tolist(),
                               default=df["Customer Segment"].unique().tolist())

    st.markdown("---")
    st.caption("Sales Dashboard 2025 · Built with Streamlit + Matplotlib + Seaborn")

# ── Apply filters ──────────────────────────────────────────────────────────────
mask = (
    df["Quarter"].isin(quarters) &
    df["Region"].isin(regions) &
    df["Salesperson"].isin(salespersons) &
    df["Customer Segment"].isin(segments)
)
fdf = df[mask]

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("Sales Dashboard 2025")
st.caption(f"Showing **{len(fdf)}** of {len(df)} orders after filters")
st.markdown("---")

# ── KPI Metrics ────────────────────────────────────────────────────────────────
total_rev    = fdf["Net Revenue (USD)"].sum()
total_profit = fdf["Gross Profit (USD)"].sum()
total_units  = fdf["Units Sold"].sum()
avg_discount = fdf["Discount (%)"].mean()
margin_pct   = (total_profit / total_rev * 100) if total_rev else 0

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Net Revenue",    f"${total_rev:,.0f}",    "FY 2025")
k2.metric("Gross Profit",   f"${total_profit:,.0f}", f"{margin_pct:.1f}% margin")
k3.metric("Units Sold",     f"{total_units:,}",      "All categories")
k4.metric("Avg Discount",   f"{avg_discount:.1f}%",  "Across orders")
k5.metric("Orders",         f"{len(fdf)}",            "Filtered")

st.markdown(" ")

# ── Helper to render charts ────────────────────────────────────────────────────
def fig_to_st(fig):
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


# ── Row 1: Monthly Revenue + Quarterly ────────────────────────────────────────
col_a, col_b = st.columns([3, 1])

with col_a:
    st.markdown('<p class="chart-title">Monthly Net Revenue</p>', unsafe_allow_html=True)
    monthly = fdf.groupby("Month", observed=True)["Net Revenue (USD)"].sum()

    fig, ax = plt.subplots(figsize=(10, 3.8))
    bars = ax.bar(range(len(monthly)), monthly.values,
                  color=[ACCENT if v == monthly.values.max() else f"{ACCENT}88" for v in monthly.values],
                  edgecolor="none", width=0.65)
    ax.set_xticks(range(len(monthly)))
    ax.set_xticklabels([m[:3] for m in monthly.index], fontsize=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1000:.0f}K"))
    ax.grid(axis="y", alpha=0.4)
    ax.set_title("", pad=0)
    # annotate max
    max_idx = np.argmax(monthly.values)
    ax.annotate(f"${monthly.values[max_idx]/1000:.1f}K",
                xy=(max_idx, monthly.values[max_idx]),
                xytext=(0, 6), textcoords="offset points",
                ha="center", fontsize=9, color=ACCENT, fontweight="bold")
    fig.tight_layout()
    fig_to_st(fig)

with col_b:
    st.markdown('<p class="chart-title">By Quarter</p>', unsafe_allow_html=True)
    quarterly = fdf.groupby("Quarter")["Net Revenue (USD)"].sum().reindex(["Q1","Q2","Q3","Q4"])

    fig, ax = plt.subplots(figsize=(3, 3.8))
    colors_q = [f"{ACCENT2}{int(0.55*255 + i*0.15*255):02x}" for i in range(4)]
    colors_q = [ACCENT2+"88", ACCENT2+"aa", ACCENT2+"cc", ACCENT2]
    ax.barh(quarterly.index[::-1], quarterly.values[::-1],
            color=colors_q[::-1], edgecolor="none", height=0.55)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1000:.0f}K"))
    ax.grid(axis="x", alpha=0.4)
    fig.tight_layout()
    fig_to_st(fig)

# ── Row 2: Region + Category + Segment ────────────────────────────────────────
col_c, col_d, col_e = st.columns(3)

with col_c:
    st.markdown('<p class="chart-title">Revenue by Region</p>', unsafe_allow_html=True)
    region_data = fdf.groupby("Region")["Net Revenue (USD)"].sum().sort_values(ascending=True)

    fig, ax = plt.subplots(figsize=(4.5, 3.2))
    bars = ax.barh(region_data.index, region_data.values,
                   color=[ACCENT3 if v == region_data.values.max() else f"{ACCENT3}77" for v in region_data.values],
                   edgecolor="none", height=0.55)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1000:.0f}K"))
    ax.grid(axis="x", alpha=0.4)
    fig.tight_layout()
    fig_to_st(fig)

with col_d:
    st.markdown('<p class="chart-title">Revenue by Category</p>', unsafe_allow_html=True)
    cat_data = fdf.groupby("Product Category")["Net Revenue (USD)"].sum().sort_values()

    fig, ax = plt.subplots(figsize=(4.5, 3.2))
    cat_colors = [ACCENT, ACCENT4, ACCENT3, RED]
    ax.barh(cat_data.index, cat_data.values, color=cat_colors[:len(cat_data)],
            edgecolor="none", height=0.55)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1000:.0f}K"))
    ax.grid(axis="x", alpha=0.4)
    fig.tight_layout()
    fig_to_st(fig)

with col_e:
    st.markdown('<p class="chart-title">Customer Segment</p>', unsafe_allow_html=True)
    seg_data = fdf.groupby("Customer Segment")["Net Revenue (USD)"].sum()

    fig, ax = plt.subplots(figsize=(4.5, 3.2))
    wedge_colors = [ACCENT, ACCENT3, ACCENT2]
    wedges, texts, autotexts = ax.pie(
        seg_data.values,
        labels=seg_data.index,
        autopct="%1.1f%%",
        colors=wedge_colors[:len(seg_data)],
        startangle=140,
        wedgeprops={"edgecolor": SURFACE, "linewidth": 2.5},
        pctdistance=0.78,
    )
    for t in texts: t.set_color(MUTED); t.set_fontsize(10)
    for t in autotexts: t.set_color(TEXT); t.set_fontsize(9); t.set_fontweight("bold")
    fig.tight_layout()
    fig_to_st(fig)

# ── Row 3: Salesperson Grouped Bar + Heatmap ──────────────────────────────────
col_f, col_g = st.columns([2, 1])

with col_f:
    st.markdown('<p class="chart-title">Salesperson: Revenue vs Gross Profit</p>', unsafe_allow_html=True)
    sp = fdf.groupby("Salesperson").agg(
        Revenue=("Net Revenue (USD)", "sum"),
        Profit=("Gross Profit (USD)", "sum")
    ).reset_index().sort_values("Revenue", ascending=False)

    x = np.arange(len(sp))
    w = 0.38
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.bar(x - w/2, sp["Revenue"], width=w, label="Net Revenue", color=ACCENT, edgecolor="none")
    ax.bar(x + w/2, sp["Profit"],  width=w, label="Gross Profit", color=ACCENT3, edgecolor="none")
    ax.set_xticks(x)
    ax.set_xticklabels(sp["Salesperson"], fontsize=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1000:.0f}K"))
    ax.grid(axis="y", alpha=0.4)
    ax.legend(fontsize=9, framealpha=0, labelcolor=TEXT)
    fig.tight_layout()
    fig_to_st(fig)

with col_g:
    st.markdown('<p class="chart-title">Units Sold by Category × Salesperson</p>', unsafe_allow_html=True)
    pivot = fdf.pivot_table(index="Product Category", columns="Salesperson",
                             values="Units Sold", aggfunc="sum", fill_value=0)
    fig, ax = plt.subplots(figsize=(4.5, 3.5))
    sns.heatmap(
        pivot, ax=ax, annot=True, fmt="d", cmap="Blues",
        linewidths=1, linecolor=SURFACE,
        cbar_kws={"shrink": 0.8},
        annot_kws={"size": 9, "color": TEXT}
    )
    ax.set_xlabel("", fontsize=9)
    ax.set_ylabel("", fontsize=9)
    ax.set_xticklabels([x.get_text().split()[0] for x in ax.get_xticklabels()], fontsize=8)
    ax.tick_params(left=False, bottom=False)
    fig.tight_layout()
    fig_to_st(fig)

# ── Row 4: Discount vs Profit scatter ─────────────────────────────────────────
st.markdown('<p class="chart-title">Discount % vs Gross Profit — by Category</p>', unsafe_allow_html=True)
fig, ax = plt.subplots(figsize=(12, 3.5))
cat_color_map = {"Electronics": ACCENT, "Software": ACCENT2,
                 "Furniture": ACCENT3, "Accessories": ACCENT4}

for cat, grp in fdf.groupby("Product Category"):
    ax.scatter(grp["Discount (%)"], grp["Gross Profit (USD)"],
               color=cat_color_map.get(cat, RED),
               alpha=0.75, s=60, label=cat, edgecolors="none")

ax.set_xlabel("Discount (%)", fontsize=10)
ax.set_ylabel("Gross Profit (USD)", fontsize=10)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1000:.0f}K"))
ax.grid(alpha=0.3)
ax.legend(fontsize=9, framealpha=0, labelcolor=TEXT, ncol=4, loc="upper right")
fig.tight_layout()
fig_to_st(fig)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Sales Dashboard 2025 · Built with **Streamlit**, **Pandas**, **NumPy**, **Matplotlib** & **Seaborn**")
