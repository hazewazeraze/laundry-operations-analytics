"""Shared data loading for the dashboard.

All summary tables are produced by the notebooks/ pipeline. Loaders are
cached with @st.cache_data so pages only pay the CSV read cost once.
"""

from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"


@st.cache_data
def load_all() -> dict[str, pd.DataFrame]:
    backlog = pd.read_csv(OUTPUTS / "tables" / "backlog_series.csv").rename(
        columns={"Unnamed: 0": "date"}
    )
    backlog["date"] = pd.to_datetime(backlog["date"])
    return {
        "kpi": pd.read_csv(OUTPUTS / "kpi" / "dashboard_kpi.csv"),
        "overview": pd.read_csv(PROCESSED / "overview_summary.csv"),
        "monthly": pd.read_csv(PROCESSED / "monthly_summary.csv"),
        "weekday": pd.read_csv(PROCESSED / "weekday_summary.csv"),
        "revenue_service": pd.read_csv(PROCESSED / "revenue_service_summary.csv"),
        "revenue_category": pd.read_csv(PROCESSED / "revenue_category_summary.csv"),
        "revenue_gap": pd.read_csv(PROCESSED / "revenue_gap_report.csv"),
        "pareto": pd.read_csv(OUTPUTS / "kpi" / "pareto_curve.csv"),
        "segments": pd.read_csv(OUTPUTS / "tables" / "segment_performance.csv"),
        "segment_sla": pd.read_csv(
            OUTPUTS / "customer_analysis" / "segment_sla_summary.csv"
        ),
        "customers": pd.read_csv(
            OUTPUTS / "customer_analysis" / "customer_value_summary.csv"
        ),
        "concentration": pd.read_csv(PROCESSED / "concentration_summary.csv"),
        "correlation": pd.read_csv(PROCESSED / "correlation_summary.csv"),
        "sla": pd.read_csv(PROCESSED / "sla_summary.csv"),
        "sla_promise": pd.read_csv(PROCESSED / "sla_by_promise_summary.csv"),
        "turnaround": pd.read_csv(PROCESSED / "turnaround_summary.csv"),
        "backlog": backlog,
        "coverage": pd.read_csv(PROCESSED / "coverage_report.csv"),
        "quality": pd.read_csv(PROCESSED / "data_quality_report.csv"),
        "hypotheses": pd.read_csv(OUTPUTS / "tables" / "hypothesis_results.csv"),
    }


def stat(table: pd.DataFrame, metric: str) -> float:
    """Look up a value in a Metric/Value summary table."""
    return float(table.loc[table["Metric"] == metric, "Value"].iloc[0])


def rp(value: float) -> str:
    """Rupiah without decimals, e.g. Rp 10,436,730."""
    return f"Rp {value:,.0f}"


SEGMENT_ORDER = [
    "Premium Customer",
    "Regular Customer",
    "High-Value Occasional",
    "Low Frequency Customer",
]


@st.cache_data
def sensitivity(customers: pd.DataFrame) -> pd.DataFrame:
    """Segment revenue share: all customers vs revenue coverage >= 80%.

    Recomputes the notebook's quartile segmentation rules on each subset so
    both columns are internally consistent.
    """

    def shares(frame: pd.DataFrame) -> pd.Series:
        rev_q75 = frame["total_revenue"].quantile(0.75)
        ord_q75 = frame["total_orders"].quantile(0.75)

        def label(row: pd.Series) -> str:
            if row["total_revenue"] >= rev_q75 and row["total_orders"] >= ord_q75:
                return "Premium Customer"
            if row["total_revenue"] >= rev_q75:
                return "High-Value Occasional"
            if row["total_orders"] >= 3:
                return "Regular Customer"
            return "Low Frequency Customer"

        labels = frame.apply(label, axis=1)
        return (
            frame["total_revenue"].groupby(labels).sum()
            / frame["total_revenue"].sum()
            * 100
        ).round(1)

    return pd.DataFrame(
        {
            "All customers (%)": shares(customers),
            "Revenue coverage >= 80% (%)": shares(
                customers[customers["revenue_coverage"] >= 0.8]
            ),
        }
    ).reindex(SEGMENT_ORDER)
