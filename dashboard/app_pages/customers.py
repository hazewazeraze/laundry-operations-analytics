import streamlit as st

import charts
from data_loader import load_all, stat

d = load_all()
kpi = d["kpi"]
segments = d["segments"]

with st.container(horizontal=True):
    st.metric(
        "Identified customers",
        f"{stat(kpi, 'Unique Customers'):,.0f}",
        border=True,
    )
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
    repeat_share = stat(d["concentration"], "Repeat share of revenue (%)")
    st.metric("Repeat customer revenue share", f"{repeat_share:.1f}%", border=True)

with st.container(border=True):
    st.markdown(
        "**Bottom line:** frequency buys volume, not price. The 8 High-Value "
        "Occasional customers average Rp 43,426 an order — 2.7× a Regular — "
        "while the 31 Premium customers carry 55.9% of observed revenue. "
        "In this dataset, keeping the top tier beats chasing new names."
    )

with st.container(border=True):
    st.subheader("Observed segments")
    st.dataframe(
        segments.rename(
            columns={
                "segment": "Segment",
                "customers": "Customers",
                "customer_percentage": "Customers (%)",
                "orders": "Orders",
                "revenue": "Observed revenue (Rp)",
                "revenue_percentage": "Revenue share (%)",
                "revenue_per_order": "Revenue per order (Rp)",
            }
        ),
        hide_index=True,
        column_config={
            "Customers (%)": st.column_config.NumberColumn(
                "Customers (%)", format="%.1f%%"
            ),
            "Observed revenue (Rp)": st.column_config.NumberColumn(
                "Observed revenue (Rp)", format="Rp %,.0f"
            ),
            "Revenue share (%)": st.column_config.NumberColumn(
                "Revenue share (%)", format="%.1f%%"
            ),
            "Revenue per order (Rp)": st.column_config.NumberColumn(
                "Revenue per order (Rp)", format="Rp %,.0f"
            ),
        },
    )
    st.caption(
        "Observed transaction patterns in the two-month window — not lifetime "
        "value. Segment revenue covers named-customer orders only "
        "(Rp 10,170,825 of the Rp 10,436,730 observed total)."
    )

with st.container(border=True):
    st.subheader("What each segment means")
    s = segments.set_index("segment")
    st.markdown(f"""
- **Premium Customer** — top quartile on **both** observed revenue and order frequency. Orders often and spends most: **{int(s.loc["Premium Customer", "customers"])} customers, {s.loc["Premium Customer", "revenue_percentage"]:.1f}% of observed revenue**. The core worth protecting.
- **High-Value Occasional** — top-quartile revenue on low frequency. Few orders, fat tickets: **Rp {s.loc["High-Value Occasional", "revenue_per_order"]:,.0f} per order**, the highest rate of any segment.
- **Regular Customer** — frequent but mid-ticket: **{int(s.loc["Regular Customer", "orders"])} orders at Rp {s.loc["Regular Customer", "revenue_per_order"]:,.0f} each**, {s.loc["Regular Customer", "revenue_percentage"]:.1f}% of revenue. The dependable middle.
- **Low Frequency Customer** — occasional and small: **{int(s.loc["Low Frequency Customer", "customers"])} customers ({s.loc["Low Frequency Customer", "customer_percentage"]:.1f}%)** driving {s.loc["Low Frequency Customer", "revenue_percentage"]:.1f}% of revenue. Cheap to serve, low stakes.
""")
    st.caption(
        "Quartile rules on two-month observed revenue and order count — "
        "behaviour inside this window, not a verdict on customer worth."
    )

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("Revenue share by segment")
        st.altair_chart(
            charts.bars_h(
                segments,
                "segment",
                "revenue_percentage",
                title_x="Share of observed revenue (%)",
                fmt=".1f",
                color_field="segment",
            ),
            width="stretch",
        )

with col2:
    with st.container(border=True):
        st.subheader("Orders vs revenue per customer")
        st.altair_chart(
            charts.scatter_segments(
                d["customers"],
                x="total_orders",
                y="total_revenue",
                title_x="Orders",
                title_y="Observed revenue (Rp)",
            ),
            width="stretch",
        )

with st.container(border=True):
    st.subheader("Segment performance vs SLA")
    col_a, col_b = st.columns(2)

    with col_a:
        st.dataframe(
            d["segment_sla"].rename(
                columns={
                    "segment": "Segment",
                    "orders": "Measurable orders",
                    "mean_days": "Mean turnaround (open days)",
                    "on_time": "On-time orders",
                    "on_time_pct": "On-time (%)",
                }
            ),
            hide_index=True,
            column_config={
                "Mean turnaround (open days)": st.column_config.NumberColumn(
                    "Mean turnaround (open days)", format="%.2f"
                ),
                "On-time (%)": st.column_config.NumberColumn(
                    "On-time (%)", format="%.1f%%"
                ),
            },
        )
        st.caption(
            "High-Value Occasional also keeps its promises best (86.4%, n=22); "
            "the other three segments sit within a few points of each other."
        )

    with col_b:
        corr = d["correlation"].rename(
            columns={
                "Relationship": "Relationship",
                "spearman_rho": "Spearman ρ",
                "n_customers": "Customers (n)",
            }
        )
        st.dataframe(
            corr,
            hide_index=True,
            column_config={
                "Spearman ρ": st.column_config.NumberColumn(
                    "Spearman ρ", format="%.3f"
                ),
            },
        )
        st.caption(
            "Frequency drives total revenue, but not value per order — "
            "the latter association is not statistically distinguishable from zero."
        )

with st.expander("Top 10 customers by observed revenue"):
    top = (
        d["customers"]
        .nlargest(10, "total_revenue")[
            [
                "customer_id",
                "total_orders",
                "total_revenue",
                "average_order_value",
                "recency_days",
                "segment",
                "revenue_coverage",
            ]
        ]
        .rename(
            columns={
                "customer_id": "Customer",
                "total_orders": "Orders",
                "total_revenue": "Observed revenue (Rp)",
                "average_order_value": "Revenue per order (Rp)",
                "recency_days": "Recency (days)",
                "segment": "Segment",
                "revenue_coverage": "Revenue coverage",
            }
        )
    )
    st.dataframe(
        top,
        hide_index=True,
        column_config={
            "Observed revenue (Rp)": st.column_config.NumberColumn(
                "Observed revenue (Rp)", format="Rp %,.0f"
            ),
            "Revenue per order (Rp)": st.column_config.NumberColumn(
                "Revenue per order (Rp)", format="Rp %,.0f"
            ),
            "Revenue coverage": st.column_config.NumberColumn(
                "Revenue coverage", format="percent"
            ),
        },
    )

st.caption(
    "Robustness of segment shares against revenue coverage is checked on the "
    "Data quality page."
)
