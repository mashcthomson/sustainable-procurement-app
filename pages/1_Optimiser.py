"""Interactive optimiser -- adjust constraints, solve live, inspect the mix."""

import streamlit as st

from optimization.vendor_selector import (
    DEFAULT_BUDGET,
    DEFAULT_MIN_DIVERSE_SHARE,
    DEFAULT_MIN_SUPPLIERS,
    load_vendors,
    optimise_selection,
)
from visualizations.dashboard import (
    category_cost_carbon_bars,
    mix_breakdown_chart,
    vendor_tradeoff_scatter,
)

st.set_page_config(page_title="Optimiser", page_icon="♻️", layout="wide")

st.title("Optimiser")
st.markdown(
    "Set the constraints, and the ILP re-solves on every change. "
    "The weight slider trades carbon minimisation off against ESG maximisation "
    "in a single normalised objective."
)

vendors = load_vendors()

with st.sidebar:
    st.header("Scenario settings")
    budget = st.slider(
        "Budget ($)", 950_000, 1_600_000, DEFAULT_BUDGET, step=25_000, format="$%d",
    )
    carbon_weight = st.slider(
        "Objective weight", 0.0, 1.0, 0.5, step=0.05,
        help="1.0 = only minimise carbon, 0.0 = only maximise ESG",
    )
    min_suppliers = st.slider(
        "Minimum distinct suppliers", 5, 12, DEFAULT_MIN_SUPPLIERS,
    )
    min_diverse_share = st.slider(
        "Minimum diverse-supplier spend share", 0.0, 0.5, DEFAULT_MIN_DIVERSE_SHARE, step=0.05,
    )

result = optimise_selection(
    vendors,
    budget=budget,
    carbon_weight=carbon_weight,
    min_suppliers=min_suppliers,
    min_diverse_share=min_diverse_share,
)

if not result.is_optimal:
    st.error(
        f"No feasible plan under these settings (solver status: {result.status}). "
        "Try raising the budget or relaxing the diversity share."
    )
    st.stop()

diverse_share = (
    result.selection.loc[result.selection["is_diverse_supplier"] == 1, "cost"].sum()
    / result.total_cost
)

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Status", result.status)
col2.metric("Total cost", f"${result.total_cost:,.0f}",
            f"{100 * result.total_cost / budget:.0f}% of budget", delta_color="off")
col3.metric("Total carbon", f"{result.total_carbon_kg / 1000:,.1f} t CO2e")
col4.metric("Achieved ESG", f"{result.achieved_esg:.1f} / 100")
col5.metric("Diverse spend", f"{100 * diverse_share:.0f}%")

st.subheader("Selected vendor mix")
st.dataframe(
    result.selection.style.format({
        "unit_cost": "${:,.0f}", "cost": "${:,.0f}",
        "carbon_kg": "{:,.0f}", "esg_score": "{:.1f}",
    }),
    width="stretch",
    hide_index=True,
)

left, right = st.columns(2)
with left:
    st.plotly_chart(mix_breakdown_chart(result.selection), width="stretch")
with right:
    st.plotly_chart(category_cost_carbon_bars(result.selection), width="stretch")

st.subheader("Where the mix sits in the vendor pool")
st.plotly_chart(vendor_tradeoff_scatter(vendors, result.selection), width="stretch")
