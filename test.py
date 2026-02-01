import streamlit as st
import pandas as pd
import plotly.express as px
import json
from sklearn.linear_model import LinearRegression

# =========================================================
# PAGE CONFIG + THEME
# =========================================================
st.set_page_config(page_title="India EV Transition", layout="wide")

st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #f3f4fb;
}
.block-container { padding-top: 2rem; }
h1, h2, h3 { color: #2c2f6c; }
[data-testid="stSidebar"] { background-color: #e8eafc; }
</style>
""", unsafe_allow_html=True)

st.title("🚗 India’s EV Adoption & ICE → EV Transition Analysis")

# =========================================================
# HELPERS
# =========================================================
def find_column(df, keywords):
    for col in df.columns:
        for k in keywords:
            if k in col.lower():
                return col
    return None

# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data
def load_data():
    df = pd.read_csv("india_ev_ice_adoption_large.csv")
    df.columns = df.columns.str.lower().str.strip()
    df["state"] = df["state"].str.strip()

    policy = pd.read_csv("ev_policy_incentives_india.csv")
    policy.columns = policy.columns.str.lower().str.strip()
    policy["state"] = policy["state"].str.strip()

    return df, policy

adoption_df, policy_df = load_data()

# =========================================================
# NORMALIZE COLUMNS
# =========================================================
EV = find_column(adoption_df, ["ev"])
ICE = find_column(adoption_df, ["ice"])
YEAR = find_column(adoption_df, ["year"])
SEG = find_column(adoption_df, ["segment", "vehicle"])

if None in [EV, ICE, YEAR, SEG]:
    st.error("❌ Required columns missing in dataset")
    st.stop()

adoption_df = adoption_df.rename(columns={
    EV: "ev",
    ICE: "ice",
    YEAR: "year",
    SEG: "vehicle_segment"
})

INC = find_column(policy_df, ["incentive", "subsidy", "amount", "fame"])
if INC:
    policy_df = policy_df.rename(columns={INC: "incentive_amount"})

# =========================================================
# SIDEBAR FILTERS
# =========================================================
st.sidebar.header("🔎 Filters")

selected_state = st.sidebar.selectbox(
    "Select State",
    sorted(adoption_df["state"].unique())
)

segments = sorted(adoption_df["vehicle_segment"].unique())
selected_segments = st.sidebar.multiselect(
    "Vehicle Segment",
    segments,
    default=segments
)

state_df = adoption_df[
    (adoption_df["state"] == selected_state) &
    (adoption_df["vehicle_segment"].isin(selected_segments))
]

national_df = adoption_df[
    adoption_df["vehicle_segment"].isin(selected_segments)
]

# =========================================================
# TABS
# =========================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Market Trends",
    "🗺️ Regional Comparison",
    "🧠 Drivers & Policy",
    "📌 EV Readiness Index",
    "🔮 Forecast"
])

# =========================================================
# TAB 1 — MARKET TRENDS
# =========================================================
with tab1:
    trend = state_df.groupby("year")[["ev", "ice"]].sum().reset_index()
    trend["ev_share"] = trend["ev"] / (trend["ev"] + trend["ice"]) * 100

    latest = trend.iloc[-1]
    c1, c2, c3 = st.columns(3)
    c1.metric("EV Share (%)", f"{latest.ev_share:.2f}")
    c2.metric("EV Units", f"{int(latest.ev):,}")
    c3.metric("ICE Units", f"{int(latest.ice):,}")

    fig = px.line(
        trend,
        x="year",
        y="ev_share",
        markers=True,
        title=f"EV Share Trend — {selected_state}"
    )
    fig.update_traces(line=dict(color="#6a5acd", width=4))
    fig.update_layout(plot_bgcolor="#f3f4fb", paper_bgcolor="#f3f4fb")
    st.plotly_chart(fig, use_container_width=True)

# =========================================================
# TAB 2 — REGIONAL COMPARISON
# =========================================================
with tab2:
    map_df = national_df.groupby("state")[["ev", "ice"]].sum().reset_index()
    map_df["ev_penetration"] = map_df["ev"] / (map_df["ev"] + map_df["ice"]) * 100

    fig = px.bar(
        map_df.sort_values("ev_penetration"),
        x="ev_penetration",
        y="state",
        orientation="h",
        color="ev_penetration",
        color_continuous_scale="Purples",
        title="EV Penetration by State"
    )
    st.plotly_chart(fig, use_container_width=True)

# =========================================================
# TAB 3 — DRIVERS & POLICY (NEW GRAPH TYPE)
# =========================================================
with tab3:
    driver_df = map_df.copy()

    if "incentive_amount" in policy_df.columns:
        policy_state = policy_df.groupby("state")["incentive_amount"].mean().reset_index()
        driver_df = driver_df.merge(policy_state, on="state", how="left")

        # Grouped bar: Adoption vs Incentive (normalized)
        driver_df["policy_norm"] = driver_df["incentive_amount"] / driver_df["incentive_amount"].max()
        driver_df["adoption_norm"] = driver_df["ev_penetration"] / driver_df["ev_penetration"].max()

        compare_df = driver_df.melt(
            id_vars="state",
            value_vars=["policy_norm", "adoption_norm"],
            var_name="metric",
            value_name="score"
        )

        fig = px.bar(
            compare_df,
            x="state",
            y="score",
            color="metric",
            title="Policy Support vs EV Adoption (Normalized)",
            barmode="group"
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

        st.info(
            "States where EV adoption outperforms policy support indicate strong market-driven transition, "
            "while others highlight policy inefficiencies."
        )
    else:
        st.warning("Policy incentive data not available.")

# =========================================================
# TAB 4 — EV READINESS INDEX (NEW)
# =========================================================
with tab4:
    readiness = map_df.copy()

    # Growth rate
    growth = national_df.groupby(["state", "year"])["ev"].sum().reset_index()
    growth["growth"] = growth.groupby("state")["ev"].pct_change()
    growth_rate = growth.groupby("state")["growth"].mean().reset_index()

    readiness = readiness.merge(growth_rate, on="state", how="left")

    if "incentive_amount" in policy_df.columns:
        policy_state = policy_df.groupby("state")["incentive_amount"].mean().reset_index()
        readiness = readiness.merge(policy_state, on="state", how="left")
    else:
        readiness["incentive_amount"] = 0

    readiness = readiness.fillna(0)

    # Normalize & score
    readiness["score"] = (
        0.4 * (readiness["ev_penetration"] / readiness["ev_penetration"].max()) +
        0.3 * (readiness["growth"] / readiness["growth"].max()) +
        0.3 * (readiness["incentive_amount"] / max(readiness["incentive_amount"].max(), 1))
    ) * 100

    fig = px.bar(
        readiness.sort_values("score"),
        x="score",
        y="state",
        orientation="h",
        color="score",
        color_continuous_scale="Viridis",
        title="EV Readiness Index (0–100)"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.success(
        "EV Readiness Index combines current adoption, growth momentum, and policy support "
        "to assess state-level preparedness for accelerated EV transition."
    )

# =========================================================
# TAB 5 — FORECAST
# =========================================================
with tab5:
    fdf = state_df.groupby("year")[["ev", "ice"]].sum().reset_index()
    fdf["share"] = fdf["ev"] / (fdf["ev"] + fdf["ice"]) * 100

    if len(fdf) > 1:
        model = LinearRegression()
        model.fit(fdf[["year"]], fdf["share"])

        future = pd.DataFrame({"year": [2025, 2026, 2027]})
        future["share"] = model.predict(future[["year"]])
        future["type"] = "Forecast"

        fdf["type"] = "Historical"
        plot_df = pd.concat([fdf[["year", "share", "type"]], future])

        fig = px.line(
            plot_df,
            x="year",
            y="share",
            color="type",
            markers=True,
            title=f"EV Share Projection — {selected_state}"
        )
        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# DATA TABLE
# =========================================================
with st.expander("📄 View Filtered Data"):
    st.dataframe(state_df)
