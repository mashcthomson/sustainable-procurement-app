"""Plotly chart components for the procurement dashboard.

Kept separate from the Streamlit pages so the same figures can be reused
(or exported) without dragging the UI along. Category colours are a fixed
mapping so a category always renders in the same colour regardless of
which vendors are on screen.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Fixed category -> colour assignment (Plotly qualitative palette)
CATEGORY_COLOURS = {
    "steel": "#636EFA",
    "concrete": "#EF553B",
    "electrical": "#00CC96",
    "logistics": "#AB63FA",
    "ppe": "#FFA15A",
}


def vendor_tradeoff_scatter(vendors: pd.DataFrame, selection: pd.DataFrame | None = None) -> go.Figure:
    """Carbon intensity vs ESG score for every vendor in the pool.

    Selected vendors (if a solved selection is passed) get a dark outline
    so you can see where the optimiser landed. Carbon is on a log axis
    because intensities span three orders of magnitude across categories
    (steel tonnes vs PPE kits).
    """
    df = vendors.copy()
    selected_ids = set(selection["vendor_id"]) if selection is not None and len(selection) else set()
    df["in_mix"] = df["vendor_id"].isin(selected_ids)

    fig = px.scatter(
        df,
        x="carbon_kg_per_unit",
        y="esg_score",
        color="category",
        color_discrete_map=CATEGORY_COLOURS,
        log_x=True,
        hover_name="vendor_name",
        hover_data={"unit_cost": ":$,.0f", "capacity_units": True, "in_mix": True},
        labels={
            "carbon_kg_per_unit": "Carbon intensity (kg CO2e per unit, log scale)",
            "esg_score": "Composite ESG score",
            "category": "Category",
        },
    )
    fig.update_traces(marker=dict(size=13, line=dict(width=0)))
    if selected_ids:
        picked = df[df["in_mix"]]
        fig.add_trace(go.Scatter(
            x=picked["carbon_kg_per_unit"],
            y=picked["esg_score"],
            mode="markers",
            marker=dict(size=17, color="rgba(0,0,0,0)", line=dict(width=2, color="#2a2a2a")),
            name="Selected",
            hoverinfo="skip",
        ))
    fig.update_layout(margin=dict(t=30, b=10), legend_title_text="")
    return fig


def pareto_frontier_chart(sweep: pd.DataFrame) -> go.Figure:
    """Carbon vs ESG Pareto frontier from the epsilon-constraint sweep."""
    fig = go.Figure(go.Scatter(
        x=sweep["achieved_esg"],
        y=sweep["total_carbon_kg"] / 1000,
        mode="lines+markers",
        marker=dict(size=9),
        line=dict(width=2, color="#636EFA"),
        hovertemplate=(
            "ESG floor %{customdata[0]}<br>"
            "Achieved ESG %{x:.1f}<br>"
            "Carbon %{y:,.1f} t CO2e<br>"
            "Cost $%{customdata[1]:,.0f}<extra></extra>"
        ),
        customdata=sweep[["esg_floor", "total_cost"]],
    ))
    fig.update_layout(
        xaxis_title="Achieved ESG score (unit-weighted average)",
        yaxis_title="Total carbon (t CO2e)",
        margin=dict(t=30, b=10),
    )
    return fig


def mix_breakdown_chart(selection: pd.DataFrame) -> go.Figure:
    """Spend per selected vendor, coloured by category."""
    df = selection.sort_values("cost", ascending=True)
    fig = px.bar(
        df,
        x="cost",
        y="vendor_name",
        color="category",
        color_discrete_map=CATEGORY_COLOURS,
        orientation="h",
        hover_data={"units": True, "carbon_kg": ":,.0f", "esg_score": True},
        labels={"cost": "Spend ($)", "vendor_name": "", "category": "Category"},
    )
    fig.update_layout(margin=dict(t=30, b=10), legend_title_text="")
    return fig


def category_cost_carbon_bars(selection: pd.DataFrame) -> go.Figure:
    """Cost and carbon totals per category, as two side-by-side panels.

    Two separate panels rather than a dual-axis chart -- the units
    (dollars vs kg) don't share a scale.
    """
    totals = selection.groupby("category", as_index=False)[["cost", "carbon_kg"]].sum()
    totals = totals.sort_values("cost", ascending=False)

    fig = make_subplots(rows=1, cols=2, subplot_titles=("Spend ($)", "Carbon (t CO2e)"), shared_yaxes=True)
    fig.add_trace(go.Bar(
        x=totals["cost"], y=totals["category"], orientation="h",
        marker_color="#636EFA", hovertemplate="%{y}: $%{x:,.0f}<extra></extra>",
    ), row=1, col=1)
    fig.add_trace(go.Bar(
        x=totals["carbon_kg"] / 1000, y=totals["category"], orientation="h",
        marker_color="#00CC96", hovertemplate="%{y}: %{x:,.1f} t<extra></extra>",
    ), row=1, col=2)
    fig.update_layout(showlegend=False, margin=dict(t=40, b=10))
    return fig
