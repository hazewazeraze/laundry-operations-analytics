"""Laundry Kampus Analytics — dashboard entry point."""

import streamlit as st

st.set_page_config(
    page_title="Laundry Kampus Analytics",
    page_icon=":material/local_laundry_service:",
    layout="wide",
)

QUESTIONS = {
    "Overview": "What happened?",
    "Revenue & services": "Where does revenue come from?",
    "Customers": "Who matters?",
    "Operations": "Can we deliver?",
    "Data quality": "How reliable are our conclusions?",
}

page = st.navigation(
    [
        st.Page(
            "app_pages/overview.py",
            title="Overview",
            icon=":material/dashboard:",
        ),
        st.Page(
            "app_pages/revenue.py",
            title="Revenue & services",
            icon=":material/payments:",
        ),
        st.Page(
            "app_pages/customers.py",
            title="Customers",
            icon=":material/groups:",
        ),
        st.Page(
            "app_pages/operations.py",
            title="Operations",
            icon=":material/local_shipping:",
        ),
        st.Page(
            "app_pages/quality.py",
            title="Data quality",
            icon=":material/fact_check:",
        ),
    ],
    position="top",
)

with st.sidebar:
    st.markdown("**Laundry Kampus Analytics**")
    st.caption(
        "467 validated transactions · 1 Apr – 30 May 2026 · 155 identified customers"
    )
    st.caption(
        "All revenue figures are **observed revenue** — recorded on 66.2% of "
        "transactions."
    )
    st.caption(
        "Source: field records from Laundry Kampus, anonymized and cleaned for a "
        "study case — not a verbatim copy of live operations."
    )

st.title(f"{page.icon} {page.title}")
st.caption(QUESTIONS.get(page.title, ""))

page.run()
