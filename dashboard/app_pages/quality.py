import streamlit as st

from data_loader import load_all, sensitivity

d = load_all()
hyp = d["hypotheses"]

st.info(
    "**Sumber data:** catatan lapangan sebuah laundry kampus (Laundry Kampus). "
    "Nama pelanggan sudah dianonimkan dan catatan dibersihkan sehingga tidak "
    "selalu persis dengan kondisi lapangan asli — demi menjaga kerahasiaan. "
    "Angka-angka di sini dipakai untuk studi kasus analitik, bukan sebagai "
    "laporan kinerja operasional yang sebenarnya."
)

st.subheader("Cakupan kolom")
st.bar_chart(
    d["quality"],
    x="column",
    y="coverage_pct",
    horizontal=True,
    sort=False,
    x_label="Coverage (%)",
)
st.caption(
    "Revenue: 66.2% · berat: 91.9% · kolom biaya: praktis kosong. Semua "
    "kesimpulan keuangan dinyatakan sebagai observed revenue."
)

with st.container(border=True):
    st.subheader("Cakupan revenue per layanan")
    st.dataframe(
        d["coverage"].rename(
            columns={
                "service_type": "Service",
                "transactions": "Orders",
                "revenue_observed": "Orders with revenue",
                "weight_observed": "Orders with weight",
                "revenue_coverage_pct": "Revenue coverage (%)",
            }
        ),
        hide_index=True,
        column_config={
            "Revenue coverage (%)": st.column_config.NumberColumn(
                "Revenue coverage (%)", format="%.1f%%"
            ),
        },
    )

with st.container(border=True):
    st.subheader("Uji hipotesis")
    renamed = hyp.rename(
        columns={
            "hypothesis": "Hypothesis",
            "test": "Test",
            "statistic": "Statistic",
            "p_value": "p-value",
            "ci_95": "95% CI",
            "verdict": "Verdict",
            "notes": "Notes",
        }
    )

    def verdict_style(value: str) -> str:
        if value == "Supported":
            return "background-color: #d7ecd9"
        if value == "Rejected":
            return "background-color: #f6d4d0"
        return "background-color: #fdf0cd"

    styled = renamed.style.map(verdict_style, subset=["Verdict"])
    st.dataframe(styled, hide_index=True, width="stretch")
    st.caption(
        "Permutation, bootstrap, dan Monte Carlo — tanpa asumsi parametrik. "
        "Hasil lengkap juga ada di `outputs/tables/hypothesis_results.csv`."
    )

with st.container(border=True):
    st.subheader("Robustness: share segment vs cakupan revenue")
    n_robust = int((d["customers"]["revenue_coverage"] >= 0.8).sum())
    st.dataframe(
        sensitivity(d["customers"]).rename(
            columns={
                "All customers (%)": "All customers (%)",
                "Revenue coverage >= 80% (%)": "Coverage ≥ 80% (%)",
            }
        ),
        column_config={
            "All customers (%)": st.column_config.NumberColumn(
                "All customers (%)", format="%.1f%%"
            ),
            "Coverage ≥ 80% (%)": st.column_config.NumberColumn(
                "Coverage ≥ 80% (%)", format="%.1f%%"
            ),
        },
    )
    st.caption(
        f"Dihitung ulang pada {n_robust} pelanggan dengan cakupan revenue ≥80%. "
        "Share Premium turun dari 55.9% ke 39.6% — share segment bersifat arah, "
        "bukan peringkat pasti."
    )

with st.expander("Keterbatasan"):
    st.markdown(
        """
- **Revenue belum lengkap.** Semua angka keuangan adalah observed revenue; ~30% nilai transaksi diperkirakan belum tercatat.
- **Jendela pendek.** Dua bulan (April–Mei 2026) — tanpa kesimpulan musiman atau CLV.
- **Tanpa timestamp.** SLA diukur dalam hari, bukan jam; hitung tanggal mentah tanpa toleransi membuat on-time rate konservatif (38%, lihat halaman Operasional).
- **Identitas pelanggan.** 20 transaksi tanpa nama pelanggan, dikecualikan dari analisis per pelanggan.
- **Sensitivitas segment.** Share segment bergeser di subset cakupan tinggi (tabel di atas).
- **Tanpa data biaya.** Cakupan `unit_cost` 0.6% — analisis margin tidak mungkin.
"""
    )
