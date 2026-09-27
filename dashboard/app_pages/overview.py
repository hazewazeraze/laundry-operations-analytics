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
        border=True,
    )
    st.metric(
        "Median turnaround",
        f"{stat(kpi, 'Median Turnaround (days)'):.1f} days",
        border=True,
    )

st.info(
    "Observed revenue concentrates in a smaller customer group (top 20% \u2192 57.7%). "
    "Delivery promises are kept only 38% of the time — mostly failing on the "
    "standard 3-day promise. Revenue is recorded on 66.2% of transactions, so "
    "every financial figure is observed revenue."
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
    "Monday +29.9% and Friday +27.3% above a flat expectation; Thursday −39.0%. "
    "Sunday is excluded (closed)."
)
st.caption(
    "Data funnel: 472 exported rows → 467 validated transactions → 447 identifiable "
    "→ 155 customers."
)
