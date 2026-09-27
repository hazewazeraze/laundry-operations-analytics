import streamlit as st

from data_loader import load_all, stat

d = load_all()
kpi = d["kpi"]
sla = d["sla"]

on_time_orders = stat(sla, "On-time orders")
measurable = stat(sla, "Orders with SLA measurable")
peak_backlog = float(d["backlog"]["cumulative_backlog"].max())

with st.container(horizontal=True):
    st.metric(
        "On-time rate",
        f"{stat(sla, 'On-time rate (%)'):.1f}%",
        border=True,
    )
    st.metric(
        "On-time orders",
        f"{on_time_orders:,.0f} / {measurable:,.0f}",
        border=True,
    )
    st.metric(
        "Avg days late",
        f"{stat(sla, 'Average days late (late orders)'):.2f}",
        border=True,
    )
    st.metric(
        "Median turnaround",
        f"{stat(kpi, 'Median Turnaround (days)'):.1f} days",
        border=True,
    )
    st.metric("Peak backlog", f"{peak_backlog:,.0f} orders", border=True)

st.info(
    "The weak point is the standard 3-day promise: 286 orders (64% of measurable "
    "orders) with only 26.6% on-time. The 1-day promise is kept 79.5% of the time. "
    "Daily intake volume does not predict lateness."
)

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("On-time rate by promised turnaround")
        st.bar_chart(
            d["sla_promise"],
            x="service_detail",
            y="on_time_pct",
            sort=False,
            y_label="On-time (%)",
        )

with col2:
    with st.container(border=True):
        st.subheader("Turnaround by service")
        st.dataframe(
            d["turnaround"].rename(
                columns={
                    "service_type": "Service",
                    "orders": "Orders",
                    "mean_days": "Mean (days)",
                    "median_days": "Median (days)",
                    "p90_days": "P90 (days)",
                }
            ),
            hide_index=True,
            column_config={
                "Mean (days)": st.column_config.NumberColumn(
                    "Mean (days)", format="%.2f"
                ),
                "Median (days)": st.column_config.NumberColumn(
                    "Median (days)", format="%.1f"
                ),
                "P90 (days)": st.column_config.NumberColumn(
                    "P90 (days)", format="%.1f"
                ),
            },
        )
        st.caption(
            "Turnaround differences between services are largely explained by "
            "their mix of promised turnaround (see Data quality page)."
        )

with st.container(border=True):
    st.subheader("Cumulative backlog")
    st.line_chart(
        d["backlog"],
        x="date",
        y="cumulative_backlog",
        y_label="Open orders",
    )

st.caption(
    "Backlog peaked at 30 open orders; lateness is structural to the promise "
    "design, not to daily volume spikes."
)
