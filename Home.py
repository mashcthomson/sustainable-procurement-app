"""PGRD -- sustainable procurement optimisation.

Streamlit entry point. Run with:  streamlit run Home.py
"""

import streamlit as st

from optimization.vendor_selector import (
    DEFAULT_BUDGET,
    load_vendors,
    optimise_selection,
)
from visualizations.dashboard import vendor_tradeoff_scatter


@st.cache_data
def get_vendors():
    return load_vendors()


def home_page() -> None:
    st.set_page_config(
        page_title="Sustainable Procurement App",
        page_icon="♻️",
        layout="wide",
    )

    st.title("Sustainable Procurement App")
    st.caption("Vendor selection that optimises carbon and ESG, not just cost.")

    st.markdown(
        """
        Most procurement tools rank vendors by price. This one runs an
        **Integer Linear Program** (PuLP) over the vendor pool to find the mix
        that minimises carbon emissions and maximises ESG performance --
        subject to budget, per-category demand, and supplier-diversity rules.

        Use the pages in the sidebar:

        - **Optimiser** -- set budget, objective weighting and diversity rules,
          solve live, and inspect the selected mix
        - **Trade-off Explorer** -- the carbon vs ESG Pareto frontier
        - **Data** -- the sample vendor dataset and Excel export
        """
    )

    vendors = get_vendors()

    st.subheader("Quick run (default settings)")
    result = optimise_selection(vendors)

    if result.is_optimal:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Solver status", result.status)
        col2.metric("Total cost", f"${result.total_cost:,.0f}",
                    f"budget ${DEFAULT_BUDGET:,.0f}", delta_color="off")
        col3.metric("Total carbon", f"{result.total_carbon_kg / 1000:,.1f} t CO2e")
        col4.metric("Achieved ESG", f"{result.achieved_esg:.1f} / 100")

        st.plotly_chart(vendor_tradeoff_scatter(vendors, result.selection), width="stretch")
        st.caption(
            "Every vendor in the pool, carbon intensity vs ESG score. "
            "Outlined markers are the vendors the optimiser selected."
        )
    else:
        st.error(f"Default scenario did not solve (status: {result.status}).")


if __name__ == "__main__":
    home_page()
