"""Thin launcher kept for backwards compatibility.

The multipage app lives in Home.py + pages/; `streamlit run app.py`
still works and shows the same home page.
"""

from Home import home_page

home_page()
