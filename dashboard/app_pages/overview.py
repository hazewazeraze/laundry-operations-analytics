import altair as alt

import streamlit as st

from data_loader import load_all, rp, stat

d = load_all()
kpi = d["kpi"]

with st.container(horizontal=True):
    st.metric(
        "Transactions",
        f"{stat(kpi, 'Total Transactions'):,.0f}",
        border=True,
    )
    st.metric(
        "Observed revenue",
        rp(stat(kpi, "Total Revenue (observed)")),
        border=True,
    )
    st.metric(
        "Identified customers",
        f"{stat(kpi, 'Unique Customers'):,.0f}",
        border=True,
    )
    st.metric(
        "Revenue coverage",
        f"{stat(kpi, 'Revenue Coverage (%)'):.1f}%",
        border=True,
    )

with st.container(horizontal=True):
    st.metric(
        "Repeat customer rate",
        f"{stat(kpi, 'Repeat Customer Rate (%)'):.1f}%",
        border=True,
    )
    st.metric(
        "Top 20% revenue share",
        f"{stat(kpi, 'Top 20% Revenue Share (%)'):.1f}%",
        border=True,
    )
    st.metric(
        "On-time rate",
        f"{stat(kpi, 'On-time Rate (%)'):.1f}%",
        help="Open days, Sunday closed.",
        border=True,
    )
    st.metric(
        "Median turnaround",
        f"{stat(kpi, 'Median Turnaround (days)'):.1f} days",
        help="Calendar days from order to completion.",
        border=True,
    )

with st.container(border=True):
    st.markdown(
        "**Bottom line:** April–May in one line — Rp 10.44M observed on 467 "
        "orders, the top 20% of customers take 57.7% of it, and only 66.2% of "
        "transactions record revenue at all. Promises hold 75.5% of the time "
        "when counted in working days; a raw calendar count would say 38% by "
        "counting closed Sundays as lateness."
    )

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("Orders by month")
        st.bar_chart(d["monthly"], x="order_month", y="orders", sort=False)

with col2:
    with st.container(border=True):
        st.subheader("Observed revenue by month")
        st.bar_chart(
            d["monthly"],
            x="order_month",
            y="revenue",
            sort=False,
            y_label="Revenue (Rp)",
        )

with st.container(border=True):
    st.subheader("Weekday demand vs expected")
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
    "Monday runs +29.9% over a flat week, Friday +27.3%, Thursday −39.0% — the "
    "week has a clear shape. Sunday is closed, so it never enters the baseline."
)
st.caption(
    "Data funnel: 472 exported rows → 467 validated transactions → 447 identifiable "
    "→ 155 customers."
)
