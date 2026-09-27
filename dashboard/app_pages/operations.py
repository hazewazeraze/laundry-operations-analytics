import streamlit as st

from data_loader import load_all, stat

d = load_all()
kpi = d["kpi"]
sla = d["sla"]
sens = d["sla_sensitivity"]

on_time_orders = stat(sla, "On-time orders")
measurable = stat(sla, "Orders with SLA measurable")
sunday_orders = stat(sens, "Orders crossing a Sunday")
cal_rate = stat(sens, "On-time rate calendar days (%)")
open_rate = stat(sens, "On-time rate open days (%)")
open_plus1 = stat(sens, "On-time rate open days +1 day (%)")
peak_backlog = float(d["backlog"]["cumulative_backlog"].max())

with st.container(horizontal=True):
    st.metric(
        "On-time rate",
        f"{stat(sla, 'On-time rate (%)'):.1f}%",
        help="Turnaround measured in open days (Monday–Saturday), Sunday closed.",
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
        help="Open days past the promise, late orders only.",
        border=True,
    )
    st.metric(
        "Median turnaround",
        f"{stat(kpi, 'Median Turnaround (days)'):.1f} days",
        help="Calendar days from order to completion.",
        border=True,
    )
    st.metric("Peak backlog", f"{peak_backlog:,.0f} orders", border=True)

with st.container(border=True):
    st.subheader("Why does a raw calendar count say 38%?")
    st.markdown(
        f"""
- Promises such as **3 HARI** are handling days, and the shop is closed on Sundays. Counted in raw calendar days, every closed Sunday becomes lateness — **{sunday_orders:.0f} of {measurable:.0f} measurable orders span at least one Sunday**.
- Measured in **open days (Monday–Saturday)**, on-time is **{open_rate:.1f}%**; the raw calendar count reads **{cal_rate:.1f}%**.
- Add one open day of slack and the rate would be {open_plus1:.1f}% — so {open_rate:.1f}% is a strict reading, not a generous one.
- Almost no order is recorded as finishing ahead of its promise (5 of 445), so genuinely fast jobs barely reach the record either.
"""
    )
    st.caption(
        "Both readings are computed in 02_exploratory_analysis.py and stored in "
        "data/processed/sla_sensitivity_report.csv."
    )

st.info(
    "The weak point is still the standard 3-day promise: 286 orders (64% of "
    "measurable orders) at 70.6% on-time. The 1-day promise holds at 93.2%. "
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
            "Turnaround here is calendar days. Differences between services are "
            "largely explained by their mix of promised turnaround (see Data "
            "quality page)."
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
