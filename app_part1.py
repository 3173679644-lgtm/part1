
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Regional Sales Pulse", page_icon="📈", layout="wide")

@st.cache_data
def load_data(path: str = "data/superstore.csv") -> pd.DataFrame:
    df = pd.read_csv(path, encoding="latin-1")
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    df["Margin"] = df["Profit"] / df["Sales"]
    return df


df = load_data()

REGIONS = sorted(df["Region"].dropna().unique())

st.title("Regional Sales Pulse")
st.caption(
    "Team: [your team name]  |  For the **Regional Sales Manager**. "
    "See where this region's profit is leaking and decide which product lines "
    "to push and which to reprice this week."
)

region = st.sidebar.selectbox("Region", REGIONS, index=REGIONS.index("Ontario") if "Ontario" in REGIONS else 0)
view = df[df["Region"] == region]

c1, c2, c3 = st.columns(3)
c1.metric("Sales (period)", f"${view['Sales'].sum():,.0f}")
c2.metric("Profit (period)", f"${view['Profit'].sum():,.0f}")
margin = view["Profit"].sum() / view["Sales"].sum() if view["Sales"].sum() else 0
c3.metric("Profit margin", f"{margin * 100:.1f}%")

st.subheader("Where the profit comes from — and where it leaks")
sub = (
    view.groupby("Product Sub-Category")["Profit"]
    .sum()
    .sort_values()
    .reset_index()
    .rename(columns={"Profit": "Profit (US$)"})
    .set_index("Product Sub-Category")
)
st.bar_chart(sub, color="#c0392b")
st.caption("Red bars below zero are product lines that sell but lose money — the first place to look.")

st.divider()
st.caption(
    "**Data: Jan 2009 – Dec 2012, Kaggle snapshot** (the dataset is frozen; "
    "in production this dashboard would refresh **nightly** from the order system, "
    "and the manager would review it **every Monday**.)"
)
