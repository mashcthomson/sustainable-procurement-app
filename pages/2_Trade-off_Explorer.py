"""Pareto frontier of carbon vs ESG, via an epsilon-constraint sweep."""

import streamlit as st

from optimization.vendor_selector import DEFAULT_BUDGET, load_vendors, pareto_sweep
from visualizations.dashboard import pareto_frontier_chart

st.set_page_config(page_title="Trade-off Explorer", page_icon="♻️", layout="wide")

st.title("Trade-off Explorer")
st.markdown(
    """
    What does a higher ESG target cost in carbon? Each point below is a
    separate ILP solve: total carbon is **minimised** while the achieved ESG
    score is held above a floor, and the floor is swept upwards until the
    scenario becomes infeasible. The resulting curve is the set of
    Pareto-optimal plans -- anything above the line is wasteful, anything
    below it is impossible under the current budget and diversity rules.
    """
)


@st.cache_data
def run_sweep(budget: float):
    vendors = load_vendors()
    return pareto_sweep(vendors, budget=budget)


budget = st.slider(
    "Budget ($)", 950_000, 1_600_000, DEFAULT_BUDGET, step=25_000, format="$%d",
)

with st.spinner("Sweeping ESG floors..."):
    sweep = run_sweep(budget)

if sweep.empty:
    st.error("No feasible plans at any ESG floor under this budget.")
    st.stop()

st.plotly_chart(pareto_frontier_chart(sweep), width="stretch")
st.caption(
    "The flat left-hand section is where the ESG floor is not binding -- the "
    "unconstrained minimum-carbon plan already clears it. Past the knee, every "
    "extra point of ESG costs real carbon."
)

st.subheader("Sweep detail")
st.dataframe(
    sweep.style.format({
        "achieved_esg": "{:.1f}",
        "total_carbon_kg": "{:,.0f}",
        "total_cost": "${:,.0f}",
    }),
    width="stretch",
    hide_index=True,
)
