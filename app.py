import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="Earthquake Dashboard", page_icon="🌍", layout="wide")

st.markdown("""
<style>
    .kpi-card {
        background: linear-gradient(135deg, #1e2130, #252a3d);
        border: 1px solid #3a3f5c;
        border-radius: 12px;
        padding: 18px 22px;
        text-align: center;
        margin-bottom: 10px;
    }
    .kpi-label { color: #8b92b3; font-size: 13px; font-weight: 600;
                 letter-spacing: 0.8px; text-transform: uppercase; }
    .kpi-value { color: #e0e4f7; font-size: 28px; font-weight: 700; margin-top:  6px; }
    .kpi-sub   { color: #5b9bd5; font-size: 12px; margin-top: 4px; }
    .chart-title { color: #e0e4f7; font-size: 15px; font-weight: 600; margin-bottom: 6px; }
</style>
""", unsafe_allow_html=True)

PALETTE = ["#5b9bd5","#e8734a","#4caf8a","#f5c842","#9b6fd4","#e84a6f","#42c8f5","#f5844a"]

plt.rcParams.update({
    "figure.facecolor": "#1e2130",
 "axes.facecolor":   "#1e2130",
    "axes.edgecolor":   "#3a3f5c",
    "axes.labelcolor":  "#8b92b3",
    "xtick.color":      "#8b92b3",
    "ytick.color":      "#8b92b3",
    "text.color":       "#e0e4f7",
    "grid.color":       "#2a2f45",
    "grid.linestyle":   "--",
    "grid.alpha":       0.5,
})
@st.cache_data
def load_data():
   df = pd.read_csv("https://raw.githubusercontent.com/zoha685/earthquake-dashboard/refs/heads/main/database.csv")
    df["DateTime"] = pd.to_datetime(df["Date"] + " " + df["Time"], errors="coerce")
    df["Year"]     = df["DateTime"].dt.year
    df["Month"]    = df["DateTime"].dt.month
    df["MonthName"] = df["DateTime"].dt.strftime("%b")
    for col in ["Depth","Magnitude","Latitude","Longitude",
                "Depth Error","Magnitude Error",
                "Azimuthal Gap","Horizontal Distance","Root Mean Square"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df.dropna(subset=["DateTime","Magnitude","Depth","Type"], inplace=True)
  df.reset_index(drop=True, inplace=True)
    return df

df_raw = load_data()

# ── SIDEBAR FILTERS ──────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 Filters")
    st.markdown("---")

    search_query = st.text_input("🔎 Search by ID / Source", "")
     min_date = df_raw["DateTime"].min().date()
    max_date = df_raw["DateTime"].max().date()
    date_range = st.date_input("📅 Date Range",
                               value=(min_date, max_date),
                               min_value=min_date,
                               max_value=max_date)

    mag_min = float(df_raw["Magnitude"].min())
    mag_max = float(df_raw["Magnitude"].max())
    mag_range = st.slider("📊 Magnitude Range",
                          min_value=round(mag_min,1),
                          max_value=round(mag_max,1),
                          value=(round(mag_min,1), round(mag_max,1)),
    step=0.1)

    dep_min = float(df_raw["Depth"].min())
    dep_max = float(df_raw["Depth"].max())
    dep_range = st.slider("🌊 Depth Range (km)",
                          min_value=round(dep_min,1),
                          max_value=round(dep_max,1),
                          value=(round(dep_min,1), round(dep_max,1)),
                          step=1.0)

    all_types = sorted(df_raw["Type"].dropna().unique().tolist())
 selected_types = st.multiselect("🗂 Event Type", options=all_types, default=all_types)

    all_mag_types = sorted(df_raw["Magnitude Type"].dropna().unique().tolist())
    selected_mag_types = st.multiselect("📐 Magnitude Type", options=all_mag_types, default=all_mag_types)

    if st.button("🔄 Reset All Filters"):
        st.rerun()

    st.markdown("---")
    st.caption("EDA Project | Instructor: Ali Hassan Sherazi")

# ── APPLY FILTERS ────────────────────────────────────────────
df = df_raw.copy()

if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    df = df[(df["DateTime"] >= pd.Timestamp(date_range[0])) &
            (df["DateTime"] <= pd.Timestamp(date_range[1]))]

df = df[(df["Magnitude"] >= mag_range[0]) & (df["Magnitude"] <= mag_range[1])]
df = df[(df["Depth"]     >= dep_range[0]) & (df["Depth"]     <= dep_range[1])]

if selected_types:
    df = df[df["Type"].isin(selected_types)]
if selected_mag_types:
     df = df[df["Magnitude Type"].isin(selected_mag_types)]
if search_query.strip():
    mask = df.apply(lambda row: row.astype(str).str.contains(
                    search_query.strip(), case=False).any(), axis=1)
    df = df[mask]

df.reset_index(drop=True, inplace=True)

# ── HEADER ───────────────────────────────────────────────────
st.markdown("""
<h1 style='text-align:center; font-size:36px; margin-bottom:0'>
    🌍 Global Earthquake Data Dashboard
</h1>
<p style='text-align:center; color:#8b92b3; font-size:15px; margin-top:6px'>
    Interactive analysis of seismic activity (1965–2016) | EDA Project
</p>
<hr style='border-color:#3a3f5c; margin:12px 0 20px'>
""", unsafe_allow_html=True)

# ── KPI CARDS ────────────────────────────────────────────────
k1,k2,k3,k4,k5 = st.columns(5)
def kpi(col, label, value, sub=""):
    col.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-label'>{label}</div>
         <div class='kpi-value'>{value}</div>
        <div class='kpi-sub'>{sub}</div>
    </div>""", unsafe_allow_html=True)

kpi(k1, "Total Records",  f"{len(df):,}",                        "filtered events")
kpi(k2, "Avg Magnitude",  f"{df['Magnitude'].mean():.2f}" if len(df) else "—", "Richter scale")
kpi(k3, "Max Magnitude",  f"{df['Magnitude'].max():.1f}"  if len(df) else "—", "highest recorded")
kpi(k4, "Avg Depth",      f"{df['Depth'].mean():.1f} km"  if len(df) else "—", "below surface")
kpi(k5, "Max Depth",      f"{df['Depth'].max():.0f} km"   if len(df) else "—", "deepest event")

st.markdown("<br>", unsafe_allow_html=True)

if df.empty:
    st.warning("⚠️ No data matches the current filters.")
    st.stop()

def styled_fig(w=7, h=4):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor("#1e2130")
    ax.set_facecolor("#1e2130")
    ax.grid(True, linestyle="--", alpha=0.4, color="#2a2f45")
    ax.spines[["top","right"]].set_visible(False)
        ax.spines[["left","bottom"]].set_color("#3a3f5c")
    return fig, ax

# ══════════════════════════════════════════
# SECTION 1 – DISTRIBUTION & COMPOSITION
# ══════════════════════════════════════════
st.markdown("### 📊 Distribution & Composition")
c1, c2, c3 = st.columns(3)

# 1. PIE CHART
with c1:
    st.markdown("<div class='chart-title'>Event Type Distribution</div>", unsafe_allow_html=True)
    type_counts = df["Type"].value_counts()
    fig, ax = plt.subplots(figsize=(5,4))
    fig.patch.set_facecolor("#1e2130")
    wedges, texts, autotexts = ax.pie(
        type_counts.values, labels=type_counts.index,
        autopct="%1.1f%%", colors=PALETTE[:len(type_counts)],
        startangle=140, wedgeprops={"edgecolor":"#1e2130","linewidth":1.5})
    for t in texts:
        t.set_color("#8b92b3"); t.set_fontsize(9)
    for at in autotexts:
        at.set_color("#e0e4f7"); at.set_fontsize(8)
    ax.set_title("Event Type", color="#e0e4f7", fontsize=12, pad=10)
      st.pyplot(fig); plt.close(fig)

# 2. HISTOGRAM
with c2:
    st.markdown("<div class='chart-title'>Magnitude Frequency Distribution</div>", unsafe_allow_html=True)
    fig, ax = styled_fig(5,4)
    ax.hist(df["Magnitude"].dropna(), bins=30, color=PALETTE[0], edgecolor="#1e2130", alpha=0.85)
    ax.set_xlabel("Magnitude"); ax.set_ylabel("Frequency")
    ax.set_title("Magnitude Histogram", color="#e0e4f7", fontsize=12)
    st.pyplot(fig); plt.close(fig)

# 3. COUNT PLOT
with c3:
    st.markdown("<div class='chart-title'>Magnitude Type Count</div>", unsafe_allow_html=True)
    fig, ax = styled_fig(5,4)
    mc = df["Magnitude Type"].value_counts()
    ax.bar(mc.index, mc.values, color=PALETTE[2], edgecolor="#1e2130")
    ax.set_xlabel("Magnitude Type"); ax.set_ylabel("Count")
    ax.set_title("Magnitude Type Count Plot", color="#e0e4f7", fontsize=12)
    plt.xticks(rotation=30, ha="right")
    st.pyplot(fig); plt.close(fig)

st.markdown("---")

# ══════════════════════════════════════════
# SECTION 2 – TRENDS OVER TIME
st.markdown("### 📈 Trends Over Time")
c4, c5 = st.columns(2)

# 4. LINE CHART
with c4:
    st.markdown("<div class='chart-title'>Yearly Earthquake Count</div>", unsafe_allow_html=True)
    yearly = df.groupby("Year").size().reset_index(name="Count")
    fig, ax = styled_fig(7,4)
    ax.plot(yearly["Year"], yearly["Count"], color=PALETTE[0], linewidth=2.2, marker="o", markersize=3)
    ax.fill_between(yearly["Year"], yearly["Count"], alpha=0.15, color=PALETTE[0])
    ax.set_xlabel("Year"); ax.set_ylabel("Number of Events")
    ax.set_title("Earthquakes per Year (Line Chart)", color="#e0e4f7", fontsize=12)
    st.pyplot(fig); plt.close(fig)

# 5. AREA CHART
with c5:
    st.markdown("<div class='chart-title'>Cumulative Earthquake Events</div>", unsafe_allow_html=True)
    yearly_cum = yearly.copy()
    yearly_cum["Cumulative"] = yearly_cum["Count"].cumsum()
    fig, ax = styled_fig(7,4)
    ax.fill_between(yearly_cum["Year"], yearly_cum["Cumulative"], color=PALETTE[3], alpha=0.55)
    ax.plot(yearly_cum["Year"], yearly_cum["Cumulative"], color=PALETTE[3], linewidth=2)
    ax.set_xlabel("Year"); ax.set_ylabel("Cumulative Count")
    ax.set_title("Cumulative Events (Area Chart)", color="#e0e4f7", fontsize=12)
    st.pyplot(fig); plt.close(fig)
    st.markdown("---")

# ══════════════════════════════════════════
# SECTION 3 – COMPARISONS
# ══════════════════════════════════════════
st.markdown("### 📉 Comparisons & Relationships")
c6, c7 = st.columns(2)

# 6. BAR CHART
with c6:
    st.markdown("<div class='chart-title'>Avg Magnitude by Year (Top 20)</div>", unsafe_allow_html=True)
    avg_mag = (df.groupby("Year")["Magnitude"].mean()
                 .reset_index()
                 .sort_values("Magnitude", ascending=False)
                 .head(20))
    fig, ax = styled_fig(7,4)
    ax.bar(avg_mag["Year"].astype(str), avg_mag["Magnitude"], color=PALETTE[1], edgecolor="#1e2130")
    ax.set_xlabel("Year"); ax.set_ylabel("Avg Magnitude")
    ax.set_title("Average Magnitude per Year (Bar Chart)", color="#e0e4f7", fontsize=12)
    plt.xticks(rotation=45, ha="right", fontsize=8)
    st.pyplot(fig); plt.close(fig)

# 7. SCATTER PLOT
with c7:
    st.markdown("<div class='chart-title'>Depth vs Magnitude</div>", unsafe_allow_html=True)
    sample = df.sample(min(3000, len(df)), random_state=42)
    fig, ax = styled_fig(7,4)
    sc = ax.scatter(sample["Depth"], sample["Magnitude"],
                    c=sample["Magnitude"], cmap="plasma",
                    alpha=0.5, s=10, linewidths=0)
    plt.colorbar(sc, ax=ax, label="Magnitude")
    ax.set_xlabel("Depth (km)"); ax.set_ylabel("Magnitude")
    ax.set_title("Depth vs Magnitude (Scatter Plot)", color="#e0e4f7", fontsize=12)
    st.pyplot(fig); plt.close(fig)

st.markdown("---")

# ══════════════════════════════════════════
# SECTION 4 – SPREAD & DENSITY
# ══════════════════════════════════════════
st.markdown("### 🎻 Spread & Density Analysis")
c8, c9 = st.columns(2)

# 8. BOX PLOT
with c8:
    st.markdown("<div class='chart-title'>Magnitude Spread by Event Type</div>", unsafe_allow_html=True)
    types_to_plot = df["Type"].value_counts().index.tolist()
    data_to_plot  = [df[df["Type"]==t]["Magnitude"].dropna().values for t in types_to_plot]
    fig, ax = styled_fig(7,4)
    bp = ax.boxplot(data_to_plot, patch_artist=True,
                    medianprops={"color":"#f5c842","linewidth":2})
    for patch, color in zip(bp["boxes"], PALETTE):
        patch.set_facecolor(color); patch.set_alpha(0.7)
    ax.set_xticklabels(types_to_plot, rotation=25, ha="right", fontsize=9)
    ax.set_ylabel("Magnitude")
     ax.set_title("Magnitude Box Plot by Event Type", color="#e0e4f7", fontsize=12)
    st.pyplot(fig); plt.close(fig)

# 9. VIOLIN PLOT
with c9:
    st.markdown("<div class='chart-title'>Depth Distribution by Event Type</div>", unsafe_allow_html=True)
    top_types = df["Type"].value_counts().head(4).index.tolist()
    df_viol   = df[df["Type"].isin(top_types)]
    fig, ax   = styled_fig(7,4)
    parts = ax.violinplot(
        [df_viol[df_viol["Type"]==t]["Depth"].dropna().values for t in top_types],
        positions=range(len(top_types)), showmedians=True)
    for i, pc in enumerate(parts["bodies"]):
        pc.set_facecolor(PALETTE[i % len(PALETTE)]); pc.set_alpha(0.7)
    parts["cmedians"].set_color("#f5c842")
    ax.set_xticks(range(len(top_types)))
    ax.set_xticklabels(top_types, rotation=20, ha="right", fontsize=9)
    ax.set_ylabel("Depth (km)")
    ax.set_title("Depth Violin Plot by Event Type", color="#e0e4f7", fontsize=12)
    st.pyplot(fig); plt.close(fig)

st.markdown("---")

# ══════════════════════════════════════════
# SECTION 5 – HEATMAP
# ══════════════════════════════════════════
        st.markdown("### 🌡️ Correlation Heatmap")
num_cols = ["Magnitude","Depth","Latitude","Longitude",
            "Depth Error","Magnitude Error",
            "Azimuthal Gap","Horizontal Distance","Root Mean Square"]
num_cols = [c for c in num_cols if c in df.columns]
corr_df  = df[num_cols].dropna(how="all").corr()

fig, ax = plt.subplots(figsize=(12,5))
fig.patch.set_facecolor("#1e2130")
ax.set_facecolor("#1e2130")
sns.heatmap(corr_df, ax=ax, annot=True, fmt=".2f", cmap="coolwarm",
            linewidths=0.5, linecolor="#1e2130", annot_kws={"size":9},
            cbar_kws={"shrink":0.8})
ax.set_title("Feature Correlation Matrix (Heatmap)", color="#e0e4f7", fontsize=14, pad=12)
plt.xticks(rotation=30, ha="right", fontsize=9)
plt.yticks(rotation=0, fontsize=9)
st.pyplot(fig); plt.close(fig)

st.markdown("---")

# ══════════════════════════════════════════
# SECTION 6 – MONTHLY + RAW TABLE
# ══════════════════════════════════════════
st.markdown("### 🗓️ Monthly Frequency & Raw Data")
c10, c11 = st.columns(2)
with c10:
    st.markdown("<div class='chart-title'>Events per Month</div>", unsafe_allow_html=True)
    month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    monthly = df.groupby("MonthName").size().reindex(month_order, fill_value=0)
    fig, ax = styled_fig(7,4)
    ax.bar(monthly.index, monthly.values, color=PALETTE[5], edgecolor="#1e2130")
    ax.set_xlabel("Month"); ax.set_ylabel("Event Count")
    ax.set_title("Earthquake Count by Month", color="#e0e4f7", fontsize=12)
    st.pyplot(fig); plt.close(fig)

with c11:
    st.markdown("<div class='chart-title'>Filtered Dataset Preview</div>", unsafe_allow_html=True)
    display_cols = ["DateTime","Type","Magnitude","Magnitude Type","Depth","Latitude","Longitude","Status"]
    display_cols = [c for c in display_cols if c in df.columns]
    st.dataframe(df[display_cols].head(200), use_container_width=True, height=320)
    st.caption(f"Showing up to 200 of {len(df):,} filtered rows.")

st.markdown("---")
st.markdown("""
<p style='text-align:center; color:#4a4f6e; font-size:12px'>
    🌍 Earthquake Dashboard · EDA Project · Instructor: Ali Hassan Sherazi
</p>
""", unsafe_allow_html=True)


