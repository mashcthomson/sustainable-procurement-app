"""Weighted ESG scoring and ranking for vendors.

Each vendor carries three sub-scores (environmental, social, governance)
on a 0-100 scale. The composite ESG score is a weighted average of the
three. The weights below came out of workshops with the client's
sustainability team -- environment carries slightly more weight than the
other two pillars for infrastructure procurement.
"""

import pandas as pd

# Default pillar weights (must sum to 1.0)
DEFAULT_WEIGHTS = {
    "env_score": 0.4,
    "social_score": 0.3,
    "gov_score": 0.3,
}


def compute_esg_scores(vendors: pd.DataFrame, weights: dict | None = None) -> pd.DataFrame:
    """Return a copy of the vendor table with a composite `esg_score` column.

    `weights` maps the three sub-score columns to their weight. Weights are
    normalised so they always sum to 1, which keeps the composite on the
    same 0-100 scale as the sub-scores.
    """
    weights = dict(weights or DEFAULT_WEIGHTS)
    total = sum(weights.values())
    if total <= 0:
        raise ValueError("ESG weights must sum to a positive number")
    weights = {col: w / total for col, w in weights.items()}

    scored = vendors.copy()
    scored["esg_score"] = sum(scored[col] * w for col, w in weights.items())
    scored["esg_score"] = scored["esg_score"].round(1)
    return scored


def rank_vendors(vendors: pd.DataFrame, weights: dict | None = None) -> pd.DataFrame:
    """Rank vendors by composite ESG score (best first)."""
    scored = compute_esg_scores(vendors, weights)
    ranked = scored.sort_values("esg_score", ascending=False).reset_index(drop=True)
    ranked.insert(0, "esg_rank", ranked.index + 1)
    return ranked
