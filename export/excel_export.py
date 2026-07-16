"""Excel export of a solved procurement plan.

Procurement teams live in Excel, so the tool has to meet them there.
Writes a workbook with a summary sheet, the full vendor mix, and
(optionally) the Pareto sweep behind the trade-off chart.
"""

from pathlib import Path

import pandas as pd
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter


def _autofit(worksheet, df: pd.DataFrame) -> None:
    for i, col in enumerate(df.columns, start=1):
        width = max(len(str(col)), df[col].astype(str).str.len().max())
        worksheet.column_dimensions[get_column_letter(i)].width = min(width + 3, 40)


def _bold_header(worksheet) -> None:
    for cell in worksheet[1]:
        cell.font = Font(bold=True)


def export_results(result, path, sweep: pd.DataFrame | None = None) -> None:
    """Write a solved SelectionResult to `path` (.xlsx or file-like buffer)."""
    summary = pd.DataFrame({
        "Metric": [
            "Solver status",
            "Total cost ($)",
            "Budget ($)",
            "Budget utilisation (%)",
            "Total carbon (kg CO2e)",
            "Achieved ESG score (0-100)",
            "Vendors selected",
            "Diverse-supplier spend share (%)",
        ],
        "Value": [
            result.status,
            round(result.total_cost, 2),
            round(result.budget, 2),
            round(100 * result.total_cost / result.budget, 1) if result.budget else None,
            round(result.total_carbon_kg, 1),
            round(result.achieved_esg, 1),
            len(result.selection),
            round(
                100 * result.selection.loc[result.selection["is_diverse_supplier"] == 1, "cost"].sum()
                / result.total_cost, 1,
            ) if result.total_cost else None,
        ],
    })

    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        summary.to_excel(writer, sheet_name="Summary", index=False)
        result.selection.to_excel(writer, sheet_name="Vendor Mix", index=False)
        if sweep is not None and len(sweep):
            sweep.to_excel(writer, sheet_name="Pareto Sweep", index=False)

        for name, df in {
            "Summary": summary,
            "Vendor Mix": result.selection,
            **({"Pareto Sweep": sweep} if sweep is not None and len(sweep) else {}),
        }.items():
            ws = writer.sheets[name]
            _bold_header(ws)
            _autofit(ws, df)


if __name__ == "__main__":
    # Solve with defaults and dump a workbook, as a quick end-to-end check
    from optimization.vendor_selector import load_vendors, optimise_selection, pareto_sweep

    vendors = load_vendors()
    result = optimise_selection(vendors)
    sweep = pareto_sweep(vendors)

    out = Path(__file__).resolve().parent.parent / "exports"
    out.mkdir(exist_ok=True)
    target = out / "procurement_plan.xlsx"
    export_results(result, target, sweep=sweep)
    print(f"Wrote {target} ({result.status}, {len(result.selection)} vendors)")
