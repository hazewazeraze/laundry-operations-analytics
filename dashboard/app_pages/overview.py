import altair as alt

import streamlit as st

from data_loader import load_all, rp, stat

d = load_all()
kpi = d["kpi"]

with st.container(horizontal=True):
    st.metric(
        "Transaksi",
        f"{stat(kpi, 'Total Transactions'):,.0f}",
        border=True,
    )
    st.metric(
        "Pendapatan (observed)",
        rp(stat(kpi, "Total Revenue (observed)")),
        border=True,
    )
    st.metric(
        "Pelanggan teridentifikasi",
        f"{stat(kpi, 'Unique Customers'):,.0f}",
        border=True,
    )
    st.metric(
        "Cakupan revenue",
        f"{stat(kpi, 'Revenue Coverage (%)'):.1f}%",
        border=True,
    )

with st.container(horizontal=True):
    st.metric(
        "Tingkat repeat customer",
        f"{stat(kpi, 'Repeat Customer Rate (%)'):.1f}%",
        border=True,
    )
    st.metric(
        "Kontribusi top 20% pelanggan",
        f"{stat(kpi, 'Top 20% Revenue Share (%)'):.1f}%",
        border=True,
    )
    st.metric(
        "Tingkat on-time",
        f"{stat(kpi, 'On-time Rate (%)'):.1f}%",
        border=True,
    )
    st.metric(
        "Median turnaround",
        f"{stat(kpi, 'Median Turnaround (days)'):.1f} hari",
        border=True,
    )

st.info(
    "Pendapatan observed terkonsentrasi di segelintir pelanggan (top 20% → 57.7%). "
    "Janji pengiriman hanya dipenuhi 38% dari waktu — titik lemahnya ada di janji "
    "3 hari. Revenue tercatat di 66.2% transaksi, jadi semua angka keuangan adalah "
    "observed revenue."
)

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("Order per bulan")
        st.bar_chart(d["monthly"], x="order_month", y="orders", sort=False)

with col2:
    with st.container(border=True):
        st.subheader("Pendapatan observed per bulan")
        st.bar_chart(
            d["monthly"],
            x="order_month",
            y="revenue",
            sort=False,
            y_label="Revenue (Rp)",
        )

with st.container(border=True):
    st.subheader("Pola hari kerja vs ekspektasi")
    weekday = d["weekday"]

    bars = (
        alt.Chart(weekday)
        .mark_bar(color="#6aa8e8")
        .encode(
            x=alt.X("day:N", sort=None, title=None),
            y=alt.Y("observed:Q", title="Orders"),
            tooltip=[
                alt.Tooltip("day:N", title="Day"),
                alt.Tooltip("observed:Q", title="Orders"),
                alt.Tooltip("expected:Q", title="Expected", format=".1f"),
                alt.Tooltip("deviation_pct:Q", title="Deviation (%)", format="+.1f"),
            ],
        )
    )
    expected = (
        alt.Chart(weekday)
        .mark_line(color="#d95f4f", point=True, strokeWidth=2)
        .encode(x=alt.X("day:N", sort=None), y=alt.Y("expected:Q", title="Orders"))
    )
    st.altair_chart(bars + expected, width="stretch")

st.caption(
    "Senin +29.9% dan Jumat +27.3% di atas ekspektasi datar; Kamis −39.0%. "
    "Minggu libur, dikecualikan."
)
st.caption(
    "Alur data: 472 baris export → 467 transaksi valid → 447 teridentifikasi "
    "→ 155 pelanggan."
)
