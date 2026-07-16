"""Sample data viewer + Excel export of the solved plan."""

import io

import streamlit as st

from export.excel_export import export_results
from optimization.vendor_selector import (
    load_carbon_factors,
    load_vendors,
    optimise_selection,
    pareto_sweep,
)

st.set_page_config(page_title="Data", page_icon="♻️", layout="wide")

st.title("Data")
st.markdown(
    "The vendor pool and carbon factors below are **synthetic sample data** "
    "shipped with the repo -- realistic in shape, but not client data. "
    "Swap in your own CSVs with the same columns and everything else works "
    "unchanged."
)

vendors = load_vendors()
factors = load_carbon_factors()

st.subheader("Vendors")
st.caption("Composite ESG score = 0.4 x environmental + 0.3 x social + 0.3 x governance.")
st.dataframe(vendors, width="stretch", hide_index=True)

st.subheader("Carbon emission factors")
st.dataframe(factors, width="stretch", hide_index=True)

st.subheader("Excel export")
st.markdown(
    "Downloads the default-settings solve as a workbook (summary, vendor mix, "
    "and the Pareto sweep) for use in existing procurement workflows."
)

if st.button("Build workbook"):
    with st.spinner("Solving and writing workbook..."):
        result = optimise_selection(vendors)
        sweep = pareto_sweep(vendors)
        buffer = io.BytesIO()
        export_results(result, buffer, sweep=sweep)
    st.download_button(
        "Download procurement_plan.xlsx",
        data=buffer.getvalue(),
        file_name="procurement_plan.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
