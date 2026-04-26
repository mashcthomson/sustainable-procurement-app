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
├── app.py                      # Main Streamlit application
├── optimization/
│   ├── vendor_selector.py      # PuLP optimisation model
│   └── esg_scoring.py          # ESG scoring algorithm
├── data/
│   ├── vendors.csv             # Sample vendor dataset
│   └── carbon_factors.csv      # Carbon emission factors
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
streamlit run app.py
```

---

## What I took away from this

Working with an actual industry partner changes everything about how you approach a project. You're not building for a marker — you're building for someone who has to present this to their team on Monday.

The optimisation side was genuinely interesting. Multi-objective linear programming is one of those things that sounds abstract until you realise it's exactly how a lot of real supply chain decisions get made. Connecting that to a proper UI that non-technical people could use without any explanation was the harder part.

---

*ACCIONA × RMIT WIL Project – Master of Data Science, 2024*
