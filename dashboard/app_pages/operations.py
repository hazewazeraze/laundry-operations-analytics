import streamlit as st

from data_loader import load_all, stat

d = load_all()
kpi = d["kpi"]
sla = d["sla"]
sens = d["sla_sensitivity"]

on_time_orders = stat(sla, "On-time orders")
measurable = stat(sla, "Orders with SLA measurable")
late_total = stat(sens, "Late orders")
late_1d = stat(sens, "Late by at most 1 day")
strict_rate = stat(sens, "On-time rate strict (%)")
plus1_rate = stat(sens, "On-time rate +1 day (%)")
peak_backlog = float(d["backlog"]["cumulative_backlog"].max())

with st.container(horizontal=True):
    st.metric(
        "Tingkat on-time",
        f"{stat(sla, 'On-time rate (%)'):.1f}%",
        border=True,
    )
    st.metric(
        "Order on-time",
        f"{on_time_orders:,.0f} / {measurable:,.0f}",
        border=True,
    )
    st.metric(
        "Rata-rata keterlambatan",
        f"{stat(sla, 'Average days late (late orders)'):.2f} hari",
        border=True,
    )
    st.metric(
        "Median turnaround",
        f"{stat(kpi, 'Median Turnaround (days)'):.1f} hari",
        border=True,
    )
    st.metric("Puncak backlog", f"{peak_backlog:,.0f} order", border=True)

with st.container(border=True):
    st.subheader("Kenapa angkanya cuma 38%?")
    st.markdown(
        f"""
- Angka 38% dihitung dari **tanggal mentah**: order dianggap telat begitu selisih tanggal selesai melewati janji — tanpa jam, tanpa toleransi.
- Dari **{late_total:.0f} order telat**, **{late_1d:.0f} ({late_1d / late_total * 100:.0f}%) hanya meleset 1 hari**; sisanya meleset 2 hari atau lebih.
- Beri toleransi 1 hari, tingkat on-time naik dari **{strict_rate:.1f}% → {plus1_rate:.1f}%**.
- `completion_date` adalah tanggal pencatatan selesai/ambil, bukan jam selesai. Order janji 3 hari hampir semuanya baru tercatat selesai di hari ke-3 sampai ke-5 — yang lebih cepat nyaris tidak terekam.
"""
    )
    st.caption(
        "Jadi 38% itu angka konservatif dari pengukuran tanggal, bukan cerita "
        "utuh di lapangan. Detail angka: data/processed/sla_sensitivity_report.csv."
    )

st.info(
    "Titik lemahnya ada di janji standar 3 hari: 286 order (64% dari order "
    "terukur) dengan on-time hanya 26.6%. Janji 1 hari terpenuhi 79.5% dari "
    "waktunya. Volume order harian tidak memprediksi keterlambatan."
)

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("On-time rate per janji turnaround")
        st.bar_chart(
            d["sla_promise"],
            x="service_detail",
            y="on_time_pct",
            sort=False,
            y_label="On-time (%)",
        )

with col2:
    with st.container(border=True):
        st.subheader("Turnaround per layanan")
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
            "Perbedaan turnaround antar layanan sebagian besar dijelaskan oleh "
            "campuran janji turnaround-nya (lihat halaman Kualitas data)."
        )

with st.container(border=True):
    st.subheader("Backlog kumulatif")
    st.line_chart(
        d["backlog"],
        x="date",
        y="cumulative_backlog",
        y_label="Open orders",
    )

st.caption(
    "Backlog pernah menyentuh 30 order terbuka; keterlambatan bersifat "
    "struktural pada desain janji, bukan pada lonjakan harian."
)
