import pandas as pd

import streamlit as st

from data_loader import load_all, sensitivity

d = load_all()
hyp = d["hypotheses"]

st.info(
    "**Where this comes from:** field records from Laundry Kampus — the campus "
    "laundry I used to work at. Names are anonymized and the records cleaned for "
    "this study case, so they are not a live operating mirror (confidentiality). "
    "Read the numbers as analysis work, not as a company report."
)

with st.container(border=True):
    st.markdown(
        "**Bottom line:** every claim here ships with its blind spot — revenue on "
        "66.2% of transactions, two months of history, no cost data at all. "
        "Supported, rejected, inconclusive: all three verdicts stay on the record."
    )

st.subheader("Column coverage")
st.bar_chart(
    d["quality"],
    x="column",
    y="coverage_pct",
    horizontal=True,
    sort=False,
    x_label="Coverage (%)",
)
st.caption(
    "Revenue 66.2% · weight 91.9% · cost fields essentially absent — which is "
    "why every financial figure reads *observed revenue*."
)

with st.container(border=True):
    st.subheader("Revenue coverage by service")
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
    st.subheader("Hypothesis tests")
    disp = pd.DataFrame(
        {
            "Hypothesis": hyp["hypothesis"],
            "Test": hyp["test"],
            "Statistic": hyp["statistic"].map(
                lambda v: "—" if pd.isna(v) else f"{v:.4g}"
            ),
            "p-value": hyp["p_value"].map(
                lambda v: "—" if pd.isna(v) else f"{v:.4f}"
            ),
            "95% CI": hyp["ci_95"].map(
                lambda v: "—" if pd.isna(v) or not str(v).strip() else str(v)
            ),
            "Verdict": hyp["verdict"],
            "Notes": hyp["notes"],
        }
    )

    VERDICT_COLORS = {
        "Supported": (
            "background-color: #3ecf8e; color: #053823; font-weight: 600;"
        ),
        "Rejected": "background-color: #ff9a8c; color: #57130a; font-weight: 600;",
        "Inconclusive": (
            "background-color: #ffc94f; color: #4a3300; font-weight: 600;"
        ),
    }
    styled = disp.style.map(
        lambda v: VERDICT_COLORS.get(v, ""), subset=["Verdict"]
    )
    st.dataframe(styled, hide_index=True, width="stretch")
    st.caption(
        "Permutation, bootstrap and Monte Carlo — no distribution assumptions. "
        "Raw file: `outputs/tables/hypothesis_results.csv`."
    )

with st.container(border=True):
    st.subheader("Segment shares vs the revenue gap")
    n_robust = int((d["customers"]["revenue_coverage"] >= 0.8).sum())
    st.dataframe(
        sensitivity(d["customers"]).rename(
            columns={
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
        f"Recomputed on the {n_robust} customers with ≥80% revenue coverage: "
        "the Premium share falls from 55.9% to 39.6%. Segment shares are a "
        "directional read, not a ranking."
    )

with st.expander("Limitations"):
    st.markdown(
        """
- **Incomplete revenue.** Every financial figure is observed revenue; about 30% of transaction value is estimated to be unrecorded.
- **Short window.** Two months (April–May 2026) — no seasonality, no lifetime-value claims.
- **No timestamps.** SLA is counted in whole working days, not hours (promises such as 3 HARI are handling days; Sunday stays closed). The raw calendar count (38%) is kept only as a reference in `sla_sensitivity_report.csv`.
- **Customer identity.** 20 transactions carry no name and sit outside customer-level analysis.
- **Segment sensitivity.** Segment shares shift on the high-coverage subset (table above).
- **No cost data.** `unit_cost` coverage is 0.6% — no margin analysis is possible.
"""
    )
