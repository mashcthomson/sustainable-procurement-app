# Sustainable Procurement App ♻️

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat-square&logo=plotly&logoColor=white)
![PuLP](https://img.shields.io/badge/PuLP-LinearProgramming-green?style=flat-square)

> ACCIONA × RMIT Work Integrated Learning (WIL) Project

---

## The context

This came out of RMIT's Work Integrated Learning program — a collaboration with ACCIONA, a global infrastructure and renewable energy company. Real client, real problem, actual deliverable.

The brief was roughly: help procurement teams make vendor decisions that account for environmental and social impact, not just cost. Easy to say, harder to actually build something useful around.

(Industry partner note: this was built during an RMIT WIL engagement with ACCIONA — no partner branding assets or client data are included in this repo, and the sample datasets are synthetic.)

---

## What we built

A vendor selection tool that uses **Integer Linear Programming** (Python PuLP) to simultaneously optimise for two things most tools treat as separate: minimising carbon emissions and maximising ESG performance scores. You can't just pick the cheapest vendor — the model finds the best mix given budget, capacity, and supplier diversity constraints.

On top of the optimisation engine, we built an interactive Streamlit + Plotly dashboard so procurement teams could actually explore the trade-offs visually. What happens to your carbon footprint if you allow one more supplier? What does hitting a higher ESG target cost you? The dashboard answers those questions in real time.

Excel export was added specifically because procurement teams live in Excel. No point building something they can't plug into their existing workflow.

---

## How the optimisation works

The vendor selection runs Integer Linear Programming to:

1. **Minimise** total carbon emissions across the selected vendor mix
2. **Maximise** weighted ESG performance score
3. **Subject to** budget constraints, capacity requirements, and minimum supplier diversity rules

It's multi-objective, which means you're not just optimising for one thing — you're finding Pareto-optimal solutions across both dimensions.

---

## Features

- Vendor scoring and ranking based on ESG criteria
- Real-time scenario analysis — adjust constraints and see results instantly
- Interactive Plotly charts showing carbon vs ESG trade-offs
- Excel export for integration with existing procurement workflows
- Sample vendor and carbon factor datasets included

---

## Tech stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.9+ |
| Optimisation | PuLP (Integer Linear Programming) |
| Web App | Streamlit |
| Visualisation | Plotly |
| Data Processing | Pandas, NumPy |
| Export | OpenPyXL (Excel) |

---

## Project structure

```
sustainable-procurement-app/
├── Home.py                     # Streamlit entry point (multipage app)
├── app.py                      # Thin launcher kept for backwards compat
├── pages/
│   ├── 1_Optimiser.py          # Live solve with adjustable constraints
│   ├── 2_Trade-off_Explorer.py # Carbon vs ESG Pareto frontier
│   └── 3_Data.py               # Data viewer + Excel export
├── optimization/
│   ├── vendor_selector.py      # PuLP optimisation model
│   └── esg_scoring.py          # ESG scoring algorithm
├── data/
│   ├── vendors.csv             # Sample vendor dataset (synthetic)
│   └── carbon_factors.csv      # Carbon emission factors (synthetic)
├── visualizations/
│   └── dashboard.py            # Plotly chart components
├── export/
│   └── excel_export.py         # Excel export functionality
├── requirements.txt
└── README.md
```

---

## Running it locally

```bash
git clone https://github.com/mashcthomson/sustainable-procurement-app.git
cd sustainable-procurement-app
pip install -r requirements.txt
streamlit run Home.py
```

(`streamlit run app.py` still works too — it just launches the same home page.)

---

## Example results

Running the optimiser with the default settings (budget $1,200,000, objective weight 0.5, minimum 6 suppliers, minimum 25% diverse-supplier spend) against the included **synthetic sample vendor dataset** — the original client vendor data isn't recoverable, so these numbers come purely from the sample CSVs:

| Metric | Value |
|--------|-------|
| Solver status | Optimal |
| Total cost | $1,126,850 (93.9% of budget) |
| Total carbon | 988.0 t CO₂e |
| Achieved ESG score | 75.3 / 100 |
| Vendors selected | 10 of 14 |
| Diverse-supplier spend share | 63.6% |

The Pareto sweep behind the Trade-off Explorer tells the more interesting story: the unconstrained minimum-carbon plan lands at **973.4 t CO₂e with an ESG score of 69.5**, so ESG floors up to ~68 change nothing. Past that knee, every extra point of ESG costs real carbon — pushing the floor to 76 drives emissions up to **1,006.9 t**, and anything above 76 is infeasible under the default budget and diversity rules. That's exactly the kind of trade-off the tool was built to make visible.

---

## What I took away from this

Working with an actual industry partner changes everything about how you approach a project. You're not building for a marker — you're building for someone who has to present this to their team on Monday.

The optimisation side was genuinely interesting. Multi-objective linear programming is one of those things that sounds abstract until you realise it's exactly how a lot of real supply chain decisions get made. Connecting that to a proper UI that non-technical people could use without any explanation was the harder part.

---

*ACCIONA × RMIT WIL Project – Master of Data Science, 2024*
