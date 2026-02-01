import streamlit as st
import pandas as pd
import plotly.express as px
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

    fig_line = px.line(
        trend,
        x="year",
        y="ev_share",
        markers=True,
        title=f"EV Share Trend — {selected_state}"
    )
    fig_line.update_traces(line=dict(color="#6a5acd", width=4))
    st.plotly_chart(fig_line, use_container_width=True)

    fig_scatter = px.scatter(
        trend,
        x="ice",
        y="ev",
        color="year",
        size="ev",
        title="ICE vs EV Adoption (Substitution Pattern)",
        labels={"ice": "ICE Registrations", "ev": "EV Registrations"}
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

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
# TAB 3 — DRIVERS & POLICY (ONLY MARKET STRUCTURE)
# =========================================================
with tab3:
    st.subheader("Drivers of EV Adoption")

    driver_df = map_df.copy()
    driver_df["total_market"] = driver_df["ev"] + driver_df["ice"]

    fig_base = px.scatter(
        driver_df,
        x="total_market",
        y="ev_penetration",
        size="ev",
        color="ev_penetration",
        color_continuous_scale="Purples",
        hover_name="state",
        title="EV Penetration vs Total Vehicle Market Size",
        labels={
            "total_market": "Total Vehicle Registrations",
            "ev_penetration": "EV Penetration (%)"
        }
    )
    st.plotly_chart(fig_base, use_container_width=True)

    st.info(
        "EV adoption does not depend solely on market size. "
        "Several smaller states achieve high EV penetration, indicating "
        "urban density, charging access, and early-adopter behavior."
    )

# =========================================================
# TAB 4 — EV READINESS INDEX
# =========================================================
with tab4:
    readiness = map_df.copy()

    growth = national_df.groupby(["state", "year"])["ev"].sum().reset_index()
    growth["growth"] = growth.groupby("state")["ev"].pct_change()
    growth_rate = growth.groupby("state")["growth"].mean().reset_index()

    readiness = readiness.merge(growth_rate, on="state", how="left").fillna(0)

    readiness["score"] = (
        0.6 * (readiness["ev_penetration"] / readiness["ev_penetration"].max()) +
        0.4 * (readiness["growth"] / readiness["growth"].max())
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

# =========================================================
# TAB 5 — FORECAST
# =========================================================
with tab5:
    fdf = state_df.groupby("year")[["ev", "ice"]].sum().reset_index()
    fdf["share"] = fdf["ev"] / (fdf["ev"] + fdf["ice"]) * 100

    model = LinearRegression()
    model.fit(fdf[["year"]], fdf["share"])

    min_year = int(fdf["year"].max() + 1)
    max_year = min_year + 10

    selected_year = st.slider(
        "Select a future year",
        min_value=min_year,
        max_value=max_year,
        value=min_year
    )

    predicted_share = model.predict([[selected_year]])[0]

    st.success(
        f"📈 In **{selected_year}**, approximately "
        f"**{predicted_share:.2f}%** of vehicle users are expected to adopt EVs."
    )

# =========================================================
# DATA TABLE
# =========================================================
with st.expander("📄 View Filtered Data"):
    st.dataframe(state_df)
