"""Laundry Operations Analytics — dashboard entry point."""

import streamlit as st

st.set_page_config(
    page_title="Laundry Operations Analytics",
    page_icon=":material/local_laundry_service:",
    layout="wide",
)

QUESTIONS = {
    "Ikhtisar": "Apa yang terjadi?",
    "Pendapatan & layanan": "Pendapatan berasal dari mana?",
    "Pelanggan": "Siapa yang paling berharga?",
    "Operasional": "Bisa tepat waktu tidak?",
    "Kualitas data": "Seberapa yakin kita dengan hasil ini?",
}

page = st.navigation(
    [
        st.Page(
            "app_pages/overview.py",
            title="Ikhtisar",
            icon=":material/dashboard:",
        ),
        st.Page(
            "app_pages/revenue.py",
            title="Pendapatan & layanan",
            icon=":material/payments:",
        ),
        st.Page(
            "app_pages/customers.py",
            title="Pelanggan",
            icon=":material/groups:",
        ),
        st.Page(
            "app_pages/operations.py",
            title="Operasional",
            icon=":material/local_shipping:",
        ),
        st.Page(
            "app_pages/quality.py",
            title="Kualitas data",
            icon=":material/fact_check:",
        ),
    ],
    position="top",
)

with st.sidebar:
    st.markdown("**Laundry Operations Analytics**")
    st.caption(
        "467 transaksi valid · 1 Apr – 30 May 2026 · 155 pelanggan teridentifikasi"
    )
    st.caption(
        "Semua angka pendapatan adalah **observed revenue** — tercatat pada "
        "66.2% transaksi."
    )
    st.caption(
        "Sumber: catatan lapangan Laundry Kampus, dianonimkan dan tidak persis "
        "sama dengan kondisi aslinya (kerahasiaan)."
    )

st.title(f"{page.icon} {page.title}")
st.caption(QUESTIONS.get(page.title, ""))

page.run()
