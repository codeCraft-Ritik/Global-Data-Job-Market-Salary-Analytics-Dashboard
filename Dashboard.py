import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ─── Page Configuration ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Data Jobs Salary Analytics 2025",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { padding: 0rem 1rem; }
    .block-container { padding-top: 1rem; }
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .stMetric label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }
    .stMetric [data-testid="stMetricDelta"] {
        color: #e0e0e0 !important;
    }
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    div[data-testid="stSidebar"] .stMarkdown h1,
    div[data-testid="stSidebar"] .stMarkdown h2,
    div[data-testid="stSidebar"] .stMarkdown h3 {
        color: #e0e0e0 !important;
    }
    .salary-header {
        text-align: center;
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 20px;
    }
    .salary-header h1 { color: #ffffff; font-size: 2.2rem; margin: 0; }
    .salary-header p  { color: #b0b0b0; font-size: 1rem; margin: 5px 0 0 0; }
</style>
""", unsafe_allow_html=True)

# ─── Load Data ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("salaries.csv")
    df["salary_in_usd"] = pd.to_numeric(df["salary_in_usd"], errors="coerce")
    df["salary"] = pd.to_numeric(df["salary"], errors="coerce")
    df["remote_ratio"] = pd.to_numeric(df["remote_ratio"], errors="coerce")

    # Human-readable mappings
    exp_map = {"EN": "Entry-Level", "MI": "Mid-Level", "SE": "Senior", "EX": "Executive"}
    emp_map = {"FT": "Full-Time", "PT": "Part-Time", "CT": "Contract"}
    size_map = {"S": "Small", "M": "Medium", "L": "Large"}
    remote_map = {0: "On-Site", 50: "Hybrid", 100: "Remote"}

    df["Experience"] = df["experience_level"].map(exp_map).fillna(df["experience_level"])
    df["Employment"] = df["employment_type"].map(emp_map).fillna(df["employment_type"])
    df["Company Size"] = df["company_size"].map(size_map).fillna(df["company_size"])
    df["Work Mode"] = df["remote_ratio"].map(remote_map).fillna("Unknown")
    return df

df = load_data()

# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="salary-header">
    <h1>💼 Data Jobs — Salary Analytics Dashboard</h1>
    <p>Comprehensive analysis of salaries, job demand, and hiring trends in the data industry (2025)</p>
</div>
""", unsafe_allow_html=True)

# ─── Sidebar Filters ────────────────────────────────────────────────────────
st.sidebar.markdown("## 🎛️ Dashboard Filters")

# Experience Level
experience_options = sorted(df["Experience"].unique())
selected_experience = st.sidebar.multiselect(
    "Experience Level", experience_options, default=experience_options
)

# Employment Type
employment_options = sorted(df["Employment"].unique())
selected_employment = st.sidebar.multiselect(
    "Employment Type", employment_options, default=employment_options
)

# Work Mode
work_mode_options = sorted(df["Work Mode"].unique())
selected_work_mode = st.sidebar.multiselect(
    "Work Mode", work_mode_options, default=work_mode_options
)

# Company Size
size_options = sorted(df["Company Size"].unique())
selected_size = st.sidebar.multiselect(
    "Company Size", size_options, default=size_options
)

# Salary Range
min_sal, max_sal = int(df["salary_in_usd"].min()), int(df["salary_in_usd"].max())
salary_range = st.sidebar.slider(
    "Salary Range (USD)", min_sal, max_sal, (min_sal, max_sal), step=5000,
    format="$%d"
)

# Top N
top_n = st.sidebar.slider("Top N for Rankings", 5, 25, 10)

# ─── Apply Filters ───────────────────────────────────────────────────────────
filtered = df[
    (df["Experience"].isin(selected_experience)) &
    (df["Employment"].isin(selected_employment)) &
    (df["Work Mode"].isin(selected_work_mode)) &
    (df["Company Size"].isin(selected_size)) &
    (df["salary_in_usd"] >= salary_range[0]) &
    (df["salary_in_usd"] <= salary_range[1])
]

if filtered.empty:
    st.warning("No data matches the current filters. Please adjust the sidebar filters.")
    st.stop()

# ─── KPI Metrics Row ────────────────────────────────────────────────────────
st.markdown("### 📌 Key Metrics")
k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.metric("Total Listings", f"{len(filtered):,}")
with k2:
    st.metric("Avg Salary", f"${filtered['salary_in_usd'].mean():,.0f}")
with k3:
    st.metric("Median Salary", f"${filtered['salary_in_usd'].median():,.0f}")
with k4:
    st.metric("Unique Roles", f"{filtered['job_title'].nunique()}")
with k5:
    st.metric("Countries", f"{filtered['company_location'].nunique()}")

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: Salary Distribution
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("## 📊 Salary Distribution")

col_a, col_b = st.columns(2)

with col_a:
    fig_hist = px.histogram(
        filtered, x="salary_in_usd", nbins=40, marginal="box",
        color_discrete_sequence=["#667eea"],
        labels={"salary_in_usd": "Salary (USD)"},
        title="Salary Distribution with Box Plot",
    )
    fig_hist.update_layout(
        height=420, showlegend=False,
        xaxis_title="Salary (USD)", yaxis_title="Count",
        title_font_size=16,
    )
    st.plotly_chart(fig_hist, use_container_width=True)

with col_b:
    fig_violin = px.violin(
        filtered, y="salary_in_usd", x="Experience", box=True, points="outliers",
        color="Experience",
        color_discrete_sequence=px.colors.qualitative.Set2,
        labels={"salary_in_usd": "Salary (USD)", "Experience": "Experience Level"},
        title="Salary Spread by Experience Level",
        category_orders={"Experience": ["Entry-Level", "Mid-Level", "Senior", "Executive"]},
    )
    fig_violin.update_layout(height=420, showlegend=False, title_font_size=16)
    st.plotly_chart(fig_violin, use_container_width=True)

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: Top Paying & In-Demand Jobs
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("## 💰 Top Paying & Most In-Demand Jobs")

col_c, col_d = st.columns(2)

with col_c:
    avg_salary_role = (
        filtered.groupby("job_title")["salary_in_usd"]
        .agg(["mean", "count"])
        .rename(columns={"mean": "avg_salary", "count": "listings"})
        .query("listings >= 2")
        .sort_values("avg_salary", ascending=False)
        .head(top_n)
        .reset_index()
    )
    fig_top_pay = px.bar(
        avg_salary_role.sort_values("avg_salary"),
        y="job_title", x="avg_salary", orientation="h",
        color="avg_salary",
        color_continuous_scale="Plasma",
        text=avg_salary_role.sort_values("avg_salary")["avg_salary"].apply(lambda v: f"${v:,.0f}"),
        labels={"job_title": "Job Title", "avg_salary": "Avg Salary (USD)"},
        title=f"Top {top_n} Highest Paying Roles",
    )
    fig_top_pay.update_traces(textposition="outside")
    fig_top_pay.update_layout(
        height=480, showlegend=False, title_font_size=16,
        yaxis_title="", coloraxis_showscale=False,
    )
    st.plotly_chart(fig_top_pay, use_container_width=True)

with col_d:
    top_demand = (
        filtered["job_title"].value_counts().head(top_n).reset_index()
    )
    top_demand.columns = ["job_title", "count"]
    fig_demand = px.bar(
        top_demand.sort_values("count"),
        y="job_title", x="count", orientation="h",
        color="count",
        color_continuous_scale="Tealgrn",
        text="count",
        labels={"job_title": "Job Title", "count": "Listings"},
        title=f"Top {top_n} Most In-Demand Roles",
    )
    fig_demand.update_traces(textposition="outside")
    fig_demand.update_layout(
        height=480, showlegend=False, title_font_size=16,
        yaxis_title="", coloraxis_showscale=False,
    )
    st.plotly_chart(fig_demand, use_container_width=True)

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: Experience Level & Employment Type Breakdown
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("## 🎯 Experience & Employment Breakdown")

col_e, col_f = st.columns(2)

with col_e:
    exp_salary = (
        filtered.groupby("Experience")["salary_in_usd"]
        .mean().sort_values().reset_index()
    )
    exp_salary.columns = ["Experience", "avg_salary"]
    fig_exp = px.bar(
        exp_salary, y="Experience", x="avg_salary", orientation="h",
        color="Experience",
        color_discrete_sequence=["#00b894", "#00cec9", "#6c5ce7", "#e17055"],
        text=exp_salary["avg_salary"].apply(lambda v: f"${v:,.0f}"),
        labels={"avg_salary": "Avg Salary (USD)"},
        title="Average Salary by Experience Level",
        category_orders={"Experience": ["Entry-Level", "Mid-Level", "Senior", "Executive"]},
    )
    fig_exp.update_traces(textposition="outside")
    fig_exp.update_layout(height=400, showlegend=False, title_font_size=16, yaxis_title="")
    st.plotly_chart(fig_exp, use_container_width=True)

with col_f:
    emp_counts = filtered["Employment"].value_counts().reset_index()
    emp_counts.columns = ["Employment", "count"]
    fig_emp = px.pie(
        emp_counts, values="count", names="Employment",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        title="Employment Type Distribution",
        hole=0.45,
    )
    fig_emp.update_traces(textinfo="percent+label", textfont_size=13)
    fig_emp.update_layout(height=400, title_font_size=16)
    st.plotly_chart(fig_emp, use_container_width=True)

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4: Remote Work & Company Size Analysis
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("## 🌐 Remote Work & Company Size")

col_g, col_h = st.columns(2)

with col_g:
    remote_counts = filtered["Work Mode"].value_counts().reset_index()
    remote_counts.columns = ["Work Mode", "count"]
    fig_remote = px.pie(
        remote_counts, values="count", names="Work Mode",
        color_discrete_map={"On-Site": "#ff6b6b", "Hybrid": "#feca57", "Remote": "#48dbfb"},
        title="Work Mode Distribution",
        hole=0.45,
    )
    fig_remote.update_traces(textinfo="percent+label", textfont_size=13)
    fig_remote.update_layout(height=400, title_font_size=16)
    st.plotly_chart(fig_remote, use_container_width=True)

with col_h:
    size_salary = (
        filtered.groupby("Company Size")["salary_in_usd"]
        .mean().sort_values().reset_index()
    )
    size_salary.columns = ["Company Size", "avg_salary"]
    fig_size = px.bar(
        size_salary, x="Company Size", y="avg_salary",
        color="Company Size",
        color_discrete_sequence=["#a29bfe", "#74b9ff", "#55efc4"],
        text=size_salary["avg_salary"].apply(lambda v: f"${v:,.0f}"),
        labels={"avg_salary": "Avg Salary (USD)"},
        title="Average Salary by Company Size",
    )
    fig_size.update_traces(textposition="outside")
    fig_size.update_layout(height=400, showlegend=False, title_font_size=16, xaxis_title="")
    st.plotly_chart(fig_size, use_container_width=True)

# Salary by Work Mode grouped by Experience
st.markdown("#### Salary by Work Mode & Experience Level")
heatmap_data = (
    filtered.groupby(["Work Mode", "Experience"])["salary_in_usd"]
    .mean().reset_index()
)
fig_heat = px.density_heatmap(
    heatmap_data, x="Experience", y="Work Mode", z="salary_in_usd",
    color_continuous_scale="Viridis",
    labels={"salary_in_usd": "Avg Salary (USD)"},
    title="Average Salary Heatmap: Work Mode × Experience",
    category_orders={
        "Experience": ["Entry-Level", "Mid-Level", "Senior", "Executive"],
        "Work Mode": ["On-Site", "Hybrid", "Remote"],
    },
    text_auto="$.2s",
)
fig_heat.update_layout(height=380, title_font_size=16)
st.plotly_chart(fig_heat, use_container_width=True)

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 5: Global Hiring Map & Top Countries
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("## 🗺️ Global Hiring Landscape")

col_i, col_j = st.columns([3, 2])

with col_i:
    country_stats = (
        filtered.groupby("company_location")
        .agg(listings=("salary_in_usd", "size"), avg_salary=("salary_in_usd", "mean"))
        .reset_index()
    )
    fig_map = px.choropleth(
        country_stats, locations="company_location",
        locationmode="ISO-3",
        color="listings",
        hover_name="company_location",
        hover_data={"avg_salary": ":$,.0f", "listings": True},
        color_continuous_scale="Blues",
        title="Job Listings by Country",
        labels={"listings": "Listings", "avg_salary": "Avg Salary"},
    )
    fig_map.update_layout(height=450, title_font_size=16, geo=dict(showframe=False))
    st.plotly_chart(fig_map, use_container_width=True)

with col_j:
    top_countries = (
        filtered["company_location"].value_counts().head(top_n).reset_index()
    )
    top_countries.columns = ["Country", "Listings"]
    fig_country = px.bar(
        top_countries.sort_values("Listings"),
        y="Country", x="Listings", orientation="h",
        color="Listings",
        color_continuous_scale="Sunset",
        text="Listings",
        title=f"Top {top_n} Hiring Countries",
    )
    fig_country.update_traces(textposition="outside")
    fig_country.update_layout(
        height=450, showlegend=False, title_font_size=16,
        yaxis_title="", coloraxis_showscale=False,
    )
    st.plotly_chart(fig_country, use_container_width=True)

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 6: Salary Comparison — Scatter & Treemap
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("## 🔍 Deep Dive — Role-Level Insights")

col_k, col_l = st.columns(2)

with col_k:
    role_stats = (
        filtered.groupby("job_title")
        .agg(
            avg_salary=("salary_in_usd", "mean"),
            listings=("salary_in_usd", "size"),
            median_salary=("salary_in_usd", "median"),
        )
        .reset_index()
        .query("listings >= 3")
    )
    fig_scatter = px.scatter(
        role_stats, x="listings", y="avg_salary", size="listings",
        color="avg_salary",
        color_continuous_scale="Turbo",
        hover_name="job_title",
        hover_data={"median_salary": ":$,.0f", "avg_salary": ":$,.0f", "listings": True},
        labels={"listings": "Number of Listings", "avg_salary": "Avg Salary (USD)"},
        title="Demand vs. Salary — Bubble Chart",
    )
    fig_scatter.update_layout(height=480, title_font_size=16, coloraxis_showscale=False)
    st.plotly_chart(fig_scatter, use_container_width=True)

with col_l:
    treemap_data = (
        filtered.groupby(["Experience", "job_title"])
        .agg(listings=("salary_in_usd", "size"), avg_salary=("salary_in_usd", "mean"))
        .reset_index()
        .sort_values("listings", ascending=False)
        .head(50)
    )
    fig_tree = px.treemap(
        treemap_data, path=["Experience", "job_title"], values="listings",
        color="avg_salary",
        color_continuous_scale="RdYlGn",
        hover_data={"avg_salary": ":$,.0f"},
        title="Job Landscape — Treemap (size = listings, color = salary)",
        labels={"avg_salary": "Avg Salary"},
    )
    fig_tree.update_layout(height=480, title_font_size=16)
    st.plotly_chart(fig_tree, use_container_width=True)

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 7: Salary Percentile Analysis
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("## 📈 Salary Percentile Analysis by Experience")

percentile_data = (
    filtered.groupby("Experience")["salary_in_usd"]
    .quantile([0.25, 0.50, 0.75])
    .unstack()
    .reset_index()
)
percentile_data.columns = ["Experience", "P25", "Median", "P75"]

fig_percentile = go.Figure()
colors = {"P25": "#74b9ff", "Median": "#6c5ce7", "P75": "#00b894"}
for col_name, color in colors.items():
    fig_percentile.add_trace(go.Bar(
        x=percentile_data["Experience"], y=percentile_data[col_name],
        name=col_name, marker_color=color,
        text=percentile_data[col_name].apply(lambda v: f"${v:,.0f}"),
        textposition="outside",
    ))

fig_percentile.update_layout(
    barmode="group", height=420, title="Salary Percentiles (25th, Median, 75th)",
    title_font_size=16,
    xaxis_title="Experience Level", yaxis_title="Salary (USD)",
    xaxis=dict(categoryorder="array", categoryarray=["Entry-Level", "Mid-Level", "Senior", "Executive"]),
)
st.plotly_chart(fig_percentile, use_container_width=True)

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 8: Sunburst — hierarchical view
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("## 🌀 Hierarchical View — Experience → Work Mode → Top Roles")

sunburst_data = (
    filtered.groupby(["Experience", "Work Mode", "job_title"])
    .agg(listings=("salary_in_usd", "size"), avg_salary=("salary_in_usd", "mean"))
    .reset_index()
    .sort_values("listings", ascending=False)
    .head(80)
)
fig_sun = px.sunburst(
    sunburst_data, path=["Experience", "Work Mode", "job_title"],
    values="listings", color="avg_salary",
    color_continuous_scale="RdYlBu_r",
    hover_data={"avg_salary": ":$,.0f"},
    title="Interactive Sunburst — Drill Down by Experience → Work Mode → Role",
)
fig_sun.update_layout(height=550, title_font_size=16)
st.plotly_chart(fig_sun, use_container_width=True)

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 9: Data Explorer
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("## 🗂️ Data Explorer")

# Search by job title
search_query = st.text_input("🔎 Search by Job Title", placeholder="e.g. Data Scientist")
display_df = filtered.copy()
if search_query:
    display_df = display_df[
        display_df["job_title"].str.contains(search_query, case=False, na=False)
    ]

display_cols = [
    "job_title", "Experience", "Employment", "salary_in_usd",
    "Work Mode", "Company Size", "company_location",
]
st.dataframe(
    display_df[display_cols].rename(columns={
        "job_title": "Job Title",
        "salary_in_usd": "Salary (USD)",
        "company_location": "Country",
    }).sort_values("Salary (USD)", ascending=False).reset_index(drop=True),
    use_container_width=True,
    height=420,
)

st.markdown(f"**Showing {len(display_df):,} records** (filtered from {len(df):,} total)")

# ─── Footer ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:gray;'>"
    "Data Jobs Salary Analytics Dashboard 2025 &nbsp;|&nbsp; Built with Streamlit & Plotly"
    "</p>",
    unsafe_allow_html=True,
)
