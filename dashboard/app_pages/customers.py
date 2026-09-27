import streamlit as st

from data_loader import load_all, stat

d = load_all()
kpi = d["kpi"]
segments = d["segments"]

with st.container(horizontal=True):
    st.metric(
        "Pelanggan teridentifikasi",
        f"{stat(kpi, 'Unique Customers'):,.0f}",
        border=True,
    )
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
    repeat_share = stat(d["concentration"], "Repeat share of revenue (%)")
    st.metric(
        "Kontribusi revenue repeat customer",
        f"{repeat_share:.1f}%",
        border=True,
    )

with st.container(border=True):
    st.subheader("Segment pelanggan (observed)")
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
        "Pola transaksi observed dalam jendela dua bulan — bukan nilai pelanggan "
        "seumur hidup. Revenue segment hanya mencakup order dengan nama pelanggan."
    )

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("Share pendapatan per segment")
        st.bar_chart(
            segments,
            x="segment",
            y="revenue_percentage",
            horizontal=True,
            sort=False,
            x_label="Share of observed revenue (%)",
        )

with col2:
    with st.container(border=True):
        st.subheader("Order vs pendapatan per pelanggan")
        st.scatter_chart(
            d["customers"],
            x="total_orders",
            y="total_revenue",
            color="segment",
            x_label="Orders",
            y_label="Observed revenue (Rp)",
            height=300,
        )

with st.container(border=True):
    st.subheader("Performa segment vs SLA")
    col_a, col_b = st.columns(2)

    with col_a:
        st.dataframe(
            d["segment_sla"].rename(
                columns={
                    "segment": "Segment",
                    "orders": "Measurable orders",
                    "mean_days": "Mean turnaround (days)",
                    "on_time": "On-time orders",
                    "on_time_pct": "On-time (%)",
                }
            ),
            hide_index=True,
            column_config={
                "Mean turnaround (days)": st.column_config.NumberColumn(
                    "Mean turnaround (days)", format="%.2f"
                ),
                "On-time (%)": st.column_config.NumberColumn(
                    "On-time (%)", format="%.1f%%"
                ),
            },
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
            "Frekuensi mendorong total pendapatan, tapi tidak nilai per order — "
            "asosiasi keduanya tidak beda secara signifikan dari nol."
        )

with st.expander("Top 10 pelanggan berdasarkan observed revenue"):
    top = d["customers"].nlargest(10, "total_revenue")[
        [
            "customer_id",
            "total_orders",
            "total_revenue",
            "average_order_value",
            "recency_days",
            "segment",
            "revenue_coverage",
        ]
    ].rename(
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
    "Uji robustness share segment terhadap cakupan revenue ada di halaman "
    "Kualitas data."
)
