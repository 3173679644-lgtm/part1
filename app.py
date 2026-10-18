"""
BANA409 — Assignment 4, Part 1
Data App: a Streamlit dashboard for the Regional Sales Manager.

Run locally:   streamlit run app.py
Built for one person: the Regional Sales Manager, who reviews it every Monday
to decide where to push next week's sales effort and which loss-making product
lines need repricing.
"""
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Regional Sales Pulse", page_icon="📈", layout="wide")

# ----------------------------------------------------------------------------
# Locate the CSV regardless of where the app is launched from.
# Primary layout (GitHub / Streamlit Cloud):  <repo>/app.py + <repo>/data/superstore.csv
# Fallback (someone dropped the CSV next to app.py): <dir>/superstore.csv
# ----------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
CANDIDATES = [
    HERE / "data" / "superstore.csv",
    HERE / "superstore.csv",
    Path.cwd() / "data" / "superstore.csv",
    Path.cwd() / "superstore.csv",
]


# ----------------------------------------------------------------------------
# Data (frozen Kaggle snapshot: Jan 2009 - Dec 2012)
# ----------------------------------------------------------------------------
@st.cache_data
def load_data(path: str | None = None) -> pd.DataFrame:
    if path is not None:
        csv_path = Path(path)
    else:
        csv_path = next((p for p in CANDIDATES if p.exists()), None)
    if csv_path is None or not Path(csv_path).exists():
        st.error(
            "Could not find `superstore.csv`.\n\n"
            "Expected it at `data/superstore.csv` next to `app.py` "
            "(a `superstore.csv` sitting beside `app.py` also works).\n\n"
            f"Looked in: {', '.join(str(p) for p in CANDIDATES)}"
        )
        st.stop()
    # The Kaggle/Tableau export is sometimes latin-1 (it contains "®"), so fall
    # back to latin-1 when the file is not valid UTF-8.
    try:
        df = pd.read_csv(csv_path, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(csv_path, encoding="latin-1")
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    df["Margin"] = df["Profit"] / df["Sales"]
    return df


df = load_data()

REGIONS = sorted(df["Region"].dropna().unique())

# ----------------------------------------------------------------------------
# Header: title + one-line caption (who it is for + what decision it supports)
# ----------------------------------------------------------------------------
st.title("Regional Sales Pulse")
st.caption(
    "Team: [your team name]  |  For the **Regional Sales Manager**. "
    "See where this region's profit is leaking and decide which product lines "
    "to push and which to reprice this week."
)

# ----------------------------------------------------------------------------
# Filter: the only one the manager actually needs — the region they own
# ----------------------------------------------------------------------------
region = st.sidebar.selectbox("Region", REGIONS, index=REGIONS.index("Ontario") if "Ontario" in REGIONS else 0)
view = df[df["Region"] == region]

# ----------------------------------------------------------------------------
# Headline metrics: the answer to "is anything wrong right now?" in five seconds
# ----------------------------------------------------------------------------
c1, c2, c3 = st.columns(3)
c1.metric("Sales (period)", f"${view['Sales'].sum():,.0f}")
c2.metric("Profit (period)", f"${view['Profit'].sum():,.0f}")
margin = view["Profit"].sum() / view["Sales"].sum() if view["Sales"].sum() else 0
c3.metric("Profit margin", f"{margin * 100:.1f}%")

# ----------------------------------------------------------------------------
# Supporting chart: WHY the margin is where it is — profit by sub-category
# ----------------------------------------------------------------------------
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

# ----------------------------------------------------------------------------
# Data period + intended refresh frequency (required line)
# ----------------------------------------------------------------------------
st.divider()
st.caption(
    "**Data: Jan 2009 – Dec 2012, Kaggle snapshot** (the dataset is frozen; "
    "in production this dashboard would refresh **nightly** from the order system, "
    "and the manager would review it **every Monday**.)"
)
