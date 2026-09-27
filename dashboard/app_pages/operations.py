import streamlit as st

import charts
from data_loader import load_all, stat

d = load_all()
kpi = d["kpi"]
sla = d["sla"]
sens = d["sla_sensitivity"]

on_time_orders = stat(sla, "On-time orders")
measurable = stat(sla, "Orders with SLA measurable")
peak_backlog = float(d["backlog"]["cumulative_backlog"].max())

PROMISE_ORDER = ["10 JAM", "1 HARI", "2 HARI", "3 HARI", "4 HARI", "5 HARI"]
prom = d["sla_promise"].set_index("service_detail").reindex(PROMISE_ORDER).reset_index()
prom_mix = prom.assign(share=lambda t: t["orders"] / t["orders"].sum() * 100)

with st.container(horizontal=True):
    st.metric(
        "On-time rate",
        f"{stat(sla, 'On-time rate (%)'):.1f}%",
        help="Turnaround measured in working days (Monday–Saturday), Sunday closed.",
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
        help="Working days past the promise, late orders only.",
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
    st.markdown(
        "**Bottom line:** 75.5% of measurable orders land on time in working days — "
        "but the standard 3-day promise (286 orders, 64% of the total) sits at 70.6% "
        "against 93.2% for 1-day work. Volume is not the culprit: backlog peaked at "
        "30 open orders and heavy intake days do not predict lateness."
    )

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("Order mix by promise")
        st.altair_chart(
            charts.bars_v(
                prom_mix,
                "service_detail",
                "share",
                title_y="Share of orders (%)",
                fmt=".1f",
                highlight="3 HARI",
                sort=PROMISE_ORDER,
            ),
            width="stretch",
        )
        st.caption("286 of 445 measurable orders — 64% — choose the 3-day promise.")

with col2:
    with st.container(border=True):
        st.subheader("On-time by promise")
        st.altair_chart(
            charts.bars_v(
                prom,
                "service_detail",
                "on_time_pct",
                title_y="On-time (%)",
                fmt=".1f",
                highlight="3 HARI",
                y_max=104,
                sort=PROMISE_ORDER,
            ),
            width="stretch",
        )
        st.caption(
            "1-day work holds at 93.2%; the promise most customers pick is the "
            "one that slips (70.6%). 4 HARI is shoe cleaning and 5 HARI is bag "
            "cleaning, not standard laundry."
        )

if "Orders crossing a Sunday" in sens["Metric"].values:
    sunday_orders = stat(sens, "Orders crossing a Sunday")
    cal_rate = stat(sens, "On-time rate calendar days (%)")
    open_rate = stat(sens, "On-time rate open days (%)")
    open_plus1 = stat(sens, "On-time rate open days +1 day (%)")

    with st.container(border=True):
        st.subheader("Same orders, two clocks: 75.5% vs 38%")
        st.markdown(f"""
- A promise like **3 HARI means three working days**. Order in on Thursday → due Monday: Saturday counts, Sunday does not.
- The raw calendar count punishes every closed Sunday — **{sunday_orders:.0f} of {measurable:.0f} measurable orders cross one** — and reads **{cal_rate:.1f}%**.
- Counted the way the shop actually runs (Mon–Sat): **{open_rate:.1f}% on-time**. Add one working day of slack and it would be {open_plus1:.1f}% — so {open_rate:.1f}% is strict, not soft.
- Almost nothing records an early finish (5 of {measurable:.0f}): completion is logged at close-out, so genuinely fast jobs rarely reach the record.
""")
        st.caption(
            "Both readings computed in 02_exploratory_analysis.py and stored in "
            "data/processed/sla_sensitivity_report.csv."
        )

col3, col4 = st.columns(2)

with col3:
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
            "Calendar days. Services look different mainly because they carry "
            "different promises — not different speed. PCS, PCL and PS are "
            "clothing-related; SATUAN is per-item and also carries the shoe "
            "and bag cleaning orders."
        )

with col4:
    with st.container(border=True):
        st.subheader("Cumulative backlog")
        # The CSV keeps completions logged through early June for orders
        # placed inside the window; those tail rows would read as negative
        # open orders, so the chart stops at the study window (30 May).
        window = d["backlog"][d["backlog"]["date"] <= "2026-05-30"]
        st.altair_chart(
            charts.line_area(
                window,
                "date",
                "cumulative_backlog",
                title_y="Open orders",
            ),
            width="stretch",
        )

st.caption(
    "Backlog peaked at 30 open orders. Lateness is structural to the promise "
    "design, not to daily volume spikes."
)
