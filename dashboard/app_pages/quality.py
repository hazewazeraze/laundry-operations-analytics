import streamlit as st

from data_loader import load_all, sensitivity

d = load_all()
hyp = d["hypotheses"]

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
    "Revenue: 66.2% · weight: 91.9% · cost fields: essentially absent. "
    "All financial conclusions are stated as observed revenue."
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
        "Permutation, bootstrap, and Monte Carlo tests — no parametric "
        "assumptions. Full results also live in "
        "`outputs/tables/hypothesis_results.csv`."
    )

with st.container(border=True):
    st.subheader("Robustness: segment shares vs revenue coverage")
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
        f"Recomputed on the {n_robust} customers with ≥80% revenue coverage. "
        "The Premium share falls from 55.9% to 39.6% — segment shares are "
        "directional, not exact rankings."
    )

with st.expander("Limitations"):
    st.markdown(
        """
- **Incomplete revenue.** All financial figures are observed revenue; ~30% of transaction value is estimated to be unrecorded.
- **Short window.** Two months (April–May 2026) — no seasonality or long-term cohort/CLV conclusions.
- **No timestamps.** SLA is measured in days, not hours.
- **Customer identity.** 20 transactions carry no customer name and are excluded from customer-level analysis.
- **Segment sensitivity.** Segment revenue shares shift on the high-coverage subset (table above).
- **No cost data.** `unit_cost` coverage is 0.6% — no margin analysis is possible.
"""
    )
