"""Vendor selection via Integer Linear Programming (PuLP).

The model picks a mix of vendors and how many units to buy from each, so
that per-category demand is met, spend stays within budget, and minimum
supplier-diversity rules hold. Two objectives are handled:

1. Minimise total carbon emissions of the selected mix
2. Maximise the (unit-weighted) composite ESG score

Because a linear program can only optimise one expression, both objectives
are combined two ways:

* `optimise_selection` -- weighted-sum objective. A `carbon_weight` slider
  between 0 and 1 blends normalised carbon against normalised ESG.
* `pareto_sweep` -- epsilon-constraint method. Carbon is minimised while
  the achieved ESG score is forced above a floor; sweeping the floor
  traces out the Pareto frontier of carbon vs ESG trade-offs.
"""

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
import pulp

from optimization.esg_scoring import compute_esg_scores

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Default procurement requirements (units per category) for the sample
# scenario -- roughly sized for one mid-size infrastructure package.
DEFAULT_DEMAND = {
    "steel": 400,       # tonnes
    "concrete": 600,    # m3
    "electrical": 250,  # packages
    "logistics": 300,   # deliveries
    "ppe": 500,         # kits
}

DEFAULT_BUDGET = 1_200_000
DEFAULT_MIN_SUPPLIERS = 6
DEFAULT_MIN_DIVERSE_SHARE = 0.25


def load_vendors(path: str | Path | None = None) -> pd.DataFrame:
    """Load the vendor dataset and attach composite ESG scores."""
    vendors = pd.read_csv(path or DATA_DIR / "vendors.csv")
    return compute_esg_scores(vendors)


def load_carbon_factors(path: str | Path | None = None) -> pd.DataFrame:
    """Load per-category baseline carbon emission factors."""
    return pd.read_csv(path or DATA_DIR / "carbon_factors.csv")


@dataclass
class SelectionResult:
    """Tidy container for one solved vendor-selection scenario."""

    status: str
    selection: pd.DataFrame = field(default_factory=pd.DataFrame)
    total_cost: float = 0.0
    total_carbon_kg: float = 0.0
    achieved_esg: float = 0.0
    budget: float = 0.0
    carbon_weight: float | None = None
    esg_floor: float | None = None

    @property
    def is_optimal(self) -> bool:
        return self.status == "Optimal"


def _build_base_model(vendors, demand, budget, min_suppliers, min_diverse_share):
    """Shared model skeleton: variables + constraints, no objective yet."""
    model = pulp.LpProblem("sustainable_procurement", pulp.LpMinimize)

    ids = vendors["vendor_id"].tolist()
    row = vendors.set_index("vendor_id")

    select = pulp.LpVariable.dicts("select", ids, cat="Binary")
    units = pulp.LpVariable.dicts("units", ids, lowBound=0, cat="Integer")

    # Linking: can only buy from a vendor if it is selected, up to capacity,
    # and a selected vendor must actually be used (at least one unit) so the
    # minimum-supplier rule can't be satisfied by empty selections
    for v in ids:
        model += units[v] <= row.loc[v, "capacity_units"] * select[v], f"capacity_{v}"
        model += units[v] >= select[v], f"min_order_{v}"

    # Per-category demand met exactly (procure what the project needs,
    # no more) -- an equality also stops the ESG objective "gaming" the
    # model by over-buying units from high-scoring vendors
    for cat, need in demand.items():
        cat_ids = row.index[row["category"] == cat].tolist()
        model += pulp.lpSum(units[v] for v in cat_ids) == need, f"demand_{cat}"

    # Budget cap
    spend = pulp.lpSum(row.loc[v, "unit_cost"] * units[v] for v in ids)
    model += spend <= budget, "budget"

    # Minimum number of distinct suppliers (avoids over-concentration)
    model += pulp.lpSum(select[v] for v in ids) >= min_suppliers, "min_suppliers"

    # Minimum share of spend going to diverse suppliers
    diverse_ids = row.index[row["is_diverse_supplier"] == 1].tolist()
    diverse_spend = pulp.lpSum(row.loc[v, "unit_cost"] * units[v] for v in diverse_ids)
    model += diverse_spend >= min_diverse_share * spend, "min_diverse_share"

    total_units = pulp.lpSum(units[v] for v in ids)
    total_carbon = pulp.lpSum(row.loc[v, "carbon_kg_per_unit"] * units[v] for v in ids)
    total_esg = pulp.lpSum(row.loc[v, "esg_score"] * units[v] for v in ids)

    return model, select, units, spend, total_units, total_carbon, total_esg


def _extract_result(model, vendors, select, units, **meta) -> SelectionResult:
    status = pulp.LpStatus[model.status]
    if status != "Optimal":
        return SelectionResult(status=status, **meta)

    rows = []
    for _, vendor in vendors.iterrows():
        v = vendor["vendor_id"]
        n = round(units[v].value() or 0)
        if select[v].value() and n > 0:
            rows.append({
                "vendor_id": v,
                "vendor_name": vendor["vendor_name"],
                "category": vendor["category"],
                "units": n,
                "unit_cost": vendor["unit_cost"],
                "cost": n * vendor["unit_cost"],
                "carbon_kg": n * vendor["carbon_kg_per_unit"],
                "esg_score": vendor["esg_score"],
                "is_diverse_supplier": vendor["is_diverse_supplier"],
            })
    selection = pd.DataFrame(rows)
    total_units = selection["units"].sum()
    return SelectionResult(
        status=status,
        selection=selection,
        total_cost=float(selection["cost"].sum()),
        total_carbon_kg=float(selection["carbon_kg"].sum()),
        achieved_esg=float((selection["esg_score"] * selection["units"]).sum() / total_units),
        **meta,
    )


def optimise_selection(
    vendors: pd.DataFrame,
    demand: dict | None = None,
    budget: float = DEFAULT_BUDGET,
    carbon_weight: float = 0.5,
    min_suppliers: int = DEFAULT_MIN_SUPPLIERS,
    min_diverse_share: float = DEFAULT_MIN_DIVERSE_SHARE,
    carbon_factors: pd.DataFrame | None = None,
) -> SelectionResult:
    """Solve the weighted-sum model.

    `carbon_weight` = 1 means care only about carbon, 0 means care only
    about ESG. The two terms are normalised so the slider behaves evenly:
    carbon is scaled by the demand-weighted baseline emission factors and
    ESG by its maximum possible value (100 per unit).
    """
    demand = demand or DEFAULT_DEMAND
    if carbon_factors is None:
        carbon_factors = load_carbon_factors()

    model, select, units, _, total_units_expr, total_carbon, total_esg = _build_base_model(
        vendors, demand, budget, min_suppliers, min_diverse_share
    )

    # Normalisers keep both terms on a comparable 0-1-ish scale
    baseline = carbon_factors.set_index("category")["baseline_kg_co2e_per_unit"]
    carbon_scale = sum(baseline[cat] * need for cat, need in demand.items())
    esg_scale = 100 * sum(demand.values())

    model += (
        carbon_weight * (total_carbon / carbon_scale)
        - (1 - carbon_weight) * (total_esg / esg_scale)
    ), "weighted_objective"

    model.solve(pulp.PULP_CBC_CMD(msg=False))
    return _extract_result(
        model, vendors, select, units, budget=budget, carbon_weight=carbon_weight
    )


def optimise_min_carbon(
    vendors: pd.DataFrame,
    esg_floor: float,
    demand: dict | None = None,
    budget: float = DEFAULT_BUDGET,
    min_suppliers: int = DEFAULT_MIN_SUPPLIERS,
    min_diverse_share: float = DEFAULT_MIN_DIVERSE_SHARE,
) -> SelectionResult:
    """Epsilon-constraint model: minimise carbon, ESG held above a floor.

    The floor applies to the unit-weighted average ESG of the whole mix,
    written linearly as  sum(esg * units) >= floor * sum(units).
    """
    demand = demand or DEFAULT_DEMAND
    model, select, units, _, total_units, total_carbon, total_esg = _build_base_model(
        vendors, demand, budget, min_suppliers, min_diverse_share
    )

    model += total_esg >= esg_floor * total_units, "esg_floor"
    model += total_carbon, "min_carbon"

    model.solve(pulp.PULP_CBC_CMD(msg=False))
    return _extract_result(
        model, vendors, select, units, budget=budget, esg_floor=esg_floor
    )


def pareto_sweep(
    vendors: pd.DataFrame,
    floors: list[float] | None = None,
    **kwargs,
) -> pd.DataFrame:
    """Trace the carbon-vs-ESG Pareto frontier.

    Runs the epsilon-constraint model over a range of ESG floors and
    collects the feasible solutions. Infeasible floors are skipped, so the
    returned frame naturally ends where the constraints can no longer be
    satisfied.
    """
    if floors is None:
        floors = [60 + 2 * i for i in range(15)]  # 60 .. 88

    points = []
    for floor in floors:
        result = optimise_min_carbon(vendors, esg_floor=floor, **kwargs)
        if result.is_optimal:
            points.append({
                "esg_floor": floor,
                "achieved_esg": round(result.achieved_esg, 2),
                "total_carbon_kg": result.total_carbon_kg,
                "total_cost": result.total_cost,
                "n_vendors": len(result.selection),
            })
    return pd.DataFrame(points)


if __name__ == "__main__":
    # Quick check that the model solves with the sample data + defaults
    vendors = load_vendors()

    result = optimise_selection(vendors)
    print(f"Status: {result.status}")
    print(f"Total cost:   ${result.total_cost:,.0f} (budget ${result.budget:,.0f})")
    print(f"Total carbon: {result.total_carbon_kg / 1000:,.1f} t CO2e")
    print(f"Achieved ESG: {result.achieved_esg:.1f} / 100")
    print(result.selection.to_string(index=False))

    print("\nPareto sweep (min carbon at each ESG floor):")
    print(pareto_sweep(vendors).to_string(index=False))
