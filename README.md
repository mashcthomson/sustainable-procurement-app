# Sustainable Procurement App ♻️

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat-square&logo=plotly&logoColor=white)

> ACCIONA × RMIT Work Integrated Learning (WIL) Project

## Overview

An ESG-optimized vendor selection tool that minimizes carbon emissions and maximizes environmental, social, and governance (ESG) performance in global supply chains. Built for ACCIONA as part of RMIT's Work Integrated Learning program.

## Features

- Linear programming optimization using **Python PuLP** for vendor selection
- Multi-objective optimization: minimize carbon footprint while maximizing ESG scores
- Interactive real-time dashboard built with **Streamlit** and **Plotly**
- Excel export functionality for procurement teams
- Vendor scoring and ranking system
- Scenario analysis for different procurement strategies

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.9+ |
| Optimization | PuLP (Linear Programming) |
| Web App | Streamlit |
| Visualization | Plotly |
| Data Processing | Pandas, NumPy |
| Export | OpenPyXL (Excel) |

## Project Structure

```
sustainable-procurement-app/
├── app.py                    # Main Streamlit application
├── optimization/
│   ├── vendor_selector.py    # PuLP optimization model
│   └── esg_scoring.py        # ESG scoring algorithm
├── data/
│   ├── vendors.csv           # Sample vendor dataset
│   └── carbon_factors.csv    # Carbon emission factors
├── visualizations/
│   └── dashboard.py          # Plotly chart components
├── export/
│   └── excel_export.py       # Excel export functionality
├── requirements.txt
└── README.md
```

## Optimization Model

The vendor selection uses Integer Linear Programming (ILP) to:

1. **Minimize**: Total carbon emissions across selected vendors
2. **Maximize**: Weighted ESG performance score
3. **Subject to**: Budget constraints, capacity requirements, and minimum supplier diversity

## Key Outcomes

- Reduced theoretical carbon footprint by optimizing vendor mix
- Enabled data-driven ESG compliance reporting
- Provided procurement teams with actionable visual analytics
- Excel exports for integration with existing procurement workflows

## Context

This project was developed as part of RMIT University's Work Integrated Learning (WIL) program in collaboration with **ACCIONA**, a global leader in sustainable infrastructure and renewable energy.

---

*ACCIONA × RMIT WIL Project – Master of Data Science, 2024*
