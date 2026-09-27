import altair as alt
import pandas as pd

import streamlit as st

from data_loader import load_all, rp, stat

d = load_all()
kpi = d["kpi"]
gap = d["revenue_gap"]
estimated_gap = float(gap["estimated_unrecorded_revenue"].sum())
observed = stat(kpi, "Total Revenue (observed)")

with st.container(horizontal=True):
    st.metric("Observed revenue", rp(observed), border=True)
    st.metric(
        "Revenue coverage",
        f"{stat(kpi, 'Revenue Coverage (%)'):.1f}%",
        border=True,
    )
    st.metric(
        "Estimated unrecorded",
        rp(estimated_gap),
        help=f"Modeled from observed per-service averages — about "
        f"{estimated_gap / observed * 100:.0f}% of observed revenue.",
        border=True,
    )
    st.metric(
        "Package services share",
        f"{float(d['revenue_category']['revenue_share_pct'].max()):.1f}%",
        border=True,
    )

st.caption(
    "Estimated unrecorded revenue is modeled from observed per-service averages "
    "— it is not tracked lost revenue."
)

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("Observed revenue by service")
        st.bar_chart(
            d["revenue_service"],
            x="service_type",
            y="revenue_observed",
            sort=False,
            y_label="Revenue (Rp)",
        )

with col2:
    with st.container(border=True):
        st.subheader("Orders by service")
        st.bar_chart(
            d["revenue_service"],
            x="service_type",
            y="transactions",
            sort=False,
        )

with st.container(border=True):
    st.subheader("Service breakdown")
    st.dataframe(
        d["revenue_service"].rename(
            columns={
                "service_type": "Service",
                "revenue_observed": "Observed revenue (Rp)",
                "transactions": "Orders",
                "revenue_observed_n": "Orders with revenue",
                "revenue_coverage_pct": "Revenue coverage (%)",
                "revenue_share_pct": "Revenue share (%)",
            }
        ),
        hide_index=True,
        column_config={
            "Observed revenue (Rp)": st.column_config.NumberColumn(
                "Observed revenue (Rp)", format="Rp %,.0f"
            ),
            "Revenue coverage (%)": st.column_config.NumberColumn(
                "Revenue coverage (%)", format="%.1f%%"
            ),
            "Revenue share (%)": st.column_config.NumberColumn(
                "Revenue share (%)", format="%.1f%%"
            ),
        },
    )

st.caption(
    "SATUAN (per-item) records revenue on 2.1% of orders — its 0.8% revenue share "
    "is an artifact of missing capture, not of low business value."
)

with st.container(border=True):
    st.subheader("Estimated revenue gap")
    st.dataframe(
        gap.rename(
            columns={
                "service_type": "Service",
                "orders_missing_revenue": "Orders missing revenue",
                "estimated_unrecorded_revenue": "Estimated unrecorded (Rp)",
                "share_of_observed_pct": "Share of observed (%)",
            }
        ),
        hide_index=True,
        column_config={
            "Estimated unrecorded (Rp)": st.column_config.NumberColumn(
                "Estimated unrecorded (Rp)", format="Rp %,.0f"
            ),
            "Share of observed (%)": st.column_config.NumberColumn(
                "Share of observed (%)", format="%.1f%%"
            ),
        },
    )

with st.container(border=True):
    st.subheader("Customer revenue concentration (Pareto)")
    pareto = d["pareto"]

    line = (
        alt.Chart(pareto)
        .mark_line(color="#4c9be8", strokeWidth=2)
        .encode(
            x=alt.X(
                "cum_pct_customers:Q",
                title="Customers (cumulative %)",
                scale=alt.Scale(domain=[0, 100]),
            ),
            y=alt.Y(
                "cum_pct_revenue:Q",
                title="Observed revenue (cumulative %)",
                scale=alt.Scale(domain=[0, 100]),
            ),
            tooltip=[
                alt.Tooltip("cum_pct_customers:Q", title="Customers (%)", format=".1f"),
                alt.Tooltip("cum_pct_revenue:Q", title="Revenue (%)", format=".1f"),
            ],
        )
        .properties(height=320)
    )

    ref_x = (
        alt.Chart(pd.DataFrame({"v": [20]}))
        .mark_rule(color="#d95f4f", strokeDash=[5, 5])
        .encode(x="v:Q")
    )
    ref_y = (
        alt.Chart(pd.DataFrame({"v": [57.7]}))
        .mark_rule(color="#d95f4f", strokeDash=[5, 5])
        .encode(y="v:Q")
    )
    point = (
        alt.Chart(pd.DataFrame({"x": [20], "y": [57.7]}))
        .mark_point(filled=True, size=90, color="#d95f4f")
        .encode(x="x:Q", y="y:Q")
    )
    st.altair_chart(ref_x + ref_y + point + line, width="stretch")

st.caption(
    "The top 20% of customers account for 57.7% of observed revenue "
    "(bootstrap 95% CI 52.2–63.5%) — concentrated, but not a strict 80/20 rule."
)
