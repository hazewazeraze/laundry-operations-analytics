# 03 VISUALIZATION


import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


pd.set_option(
    "display.max_columns",
    None
)


try:
    plt.style.use(
        "seaborn-v0_8-whitegrid"
    )
except OSError:
    pass


# =========================
# Load Dataset
# =========================

df = pd.read_csv(
    "../data/processed/laundry_clean.csv"
)

df["order_date"] = pd.to_datetime(
    df["order_date"]
)


# =========================
# Output folders
# =========================

chart_folder = "../outputs/charts"

kpi_folder = "../outputs/kpi"

os.makedirs(
    chart_folder,
    exist_ok=True
)

os.makedirs(
    kpi_folder,
    exist_ok=True
)


# =========================
# Helper function
# =========================

def add_labels(
    fmt="%.0f",
    padding=3,
):

    for container in plt.gca().containers:

        plt.bar_label(
            container,
            fmt=fmt,
            padding=padding,
        )


# =========================
# Customer preparation
# =========================

customer_df = df[
    df["customer_id"]
    !=
    "Customer_UNKNOWN"
]

customer_frequency = (
    customer_df
    .groupby("customer_id")
    .size()
    .sort_values(ascending=False)
)

repeat_customer = int(
    (customer_frequency > 1).sum()
)

one_time_customer = int(
    (customer_frequency == 1).sum()
)


customer_revenue = (
    customer_df
    .groupby("customer_id")["total_revenue"]
    .sum()
    .sort_values(ascending=False)
)

top20_n = int(
    np.ceil(0.2 * len(customer_revenue))
)

top20_share = (
    customer_revenue.head(top20_n).sum()
    /
    customer_revenue.sum()
    *
    100
)


sla = df[
    df["is_late"].notna()
]


# =========================
# KPI Summary
# =========================

kpi = pd.DataFrame(
    {
        "Metric": [
            "Total Transactions",

            "Total Revenue (observed)",

            "Revenue Coverage (%)",

            "Unique Customers",

            "Repeat Customer Rate (%)",

            "Top 20% Revenue Share (%)",

            "On-time Rate (%)",

            "Median Turnaround (days)",
        ],

        "Value": [
            len(df),

            df["total_revenue"].sum(),

            round(
                df["has_revenue"].mean() * 100,
                1
            ),

            len(customer_frequency),

            round(
                repeat_customer
                /
                len(customer_frequency)
                *
                100,
                2
            ),

            round(top20_share, 1),

            round(
                sla["is_late"].eq(False).sum()
                /
                len(sla)
                *
                100,
                1
            ),

            round(
                df["service_days"].median(),
                1
            ),
        ],
    }
)


kpi.to_csv(
    f"{kpi_folder}/dashboard_kpi.csv",
    index=False
)


# ==================================================
# 1. Revenue contribution (with coverage)
# ==================================================

revenue_service = (
    df
    .groupby("service_type")
    .agg(
        revenue=("total_revenue", "sum"),
        observed_n=("total_revenue", "count"),
        transactions=("no", "size"),
    )
    .sort_values("revenue", ascending=False)
)

revenue_service["coverage_pct"] = (
    revenue_service["observed_n"]
    /
    revenue_service["transactions"]
    *
    100
).round(0)


plt.figure(
    figsize=(8, 5)
)

ax = revenue_service["revenue"].plot(
    kind="bar"
)

plt.title(
    "Revenue Contribution by Service Type (observed)"
)

plt.xlabel(
    "Service Type"
)

plt.ylabel(
    "Revenue (IDR)"
)

plt.xticks(
    rotation=0
)

for i, (value, coverage) in enumerate(
    zip(
        revenue_service["revenue"],
        revenue_service["coverage_pct"],
    )
):

    plt.text(
        i,
        value,
        f"Rp{value / 1_000_000:.2f}M\n"
        f"(n={int(revenue_service['observed_n'].iloc[i])}, "
        f"cov {coverage:.0f}%)",
        ha="center",
        va="bottom",
        fontsize=9,
    )

plt.ylim(
    0,
    revenue_service["revenue"].max() * 1.25
)

plt.tight_layout()

plt.savefig(
    f"{chart_folder}/01_revenue_service.png",
    dpi=300
)

plt.close()


# ==================================================
# 2. Transaction volume by service
# ==================================================

service_volume = (
    df["service_type"]
    .value_counts()
)

plt.figure(
    figsize=(8, 5)
)

service_volume.plot(
    kind="bar"
)

plt.title(
    "Transaction Volume by Service Type"
)

plt.xlabel(
    "Service Type"
)

plt.ylabel(
    "Number of Transactions"
)

plt.xticks(
    rotation=0
)

add_labels()

plt.tight_layout()

plt.savefig(
    f"{chart_folder}/02_transaction_service.png",
    dpi=300
)

plt.close()


# ==================================================
# 3. Weekday pattern (with expected)
# ==================================================

weekday_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

weekly_orders = (
    df["order_day"]
    .value_counts()
    .reindex(weekday_order)
    .fillna(0)
)


date_range = pd.date_range(
    df["order_date"].min(),
    df["order_date"].max(),
    freq="D",
)

exposure = (
    pd.Series(
        date_range.day_name()
    )
    .value_counts()
    .reindex(weekday_order)
    .fillna(0)
)

open_days = weekday_order[:-1]

expected = (
    weekly_orders[open_days].sum()
    *
    exposure[open_days]
    /
    exposure[open_days].sum()
)


plt.figure(
    figsize=(8, 5)
)

weekly_orders.plot(
    kind="bar"
)

plt.plot(
    range(len(open_days)),
    expected.values,
    color="red",
    marker="o",
    linestyle="--",
    label="Expected (exposure-adjusted)",
)

plt.title(
    "Transaction Volume by Day"
)

plt.xlabel(
    "Day"
)

plt.ylabel(
    "Orders"
)

plt.xticks(
    rotation=45
)

plt.legend()

add_labels()

plt.annotate(
    "Sunday: closed",
    xy=(6, 2),
    xytext=(5.2, 45),
    arrowprops={"arrowstyle": "->"},
    fontsize=9,
)

plt.tight_layout()

plt.savefig(
    f"{chart_folder}/03_orders_by_day.png",
    dpi=300
)

plt.close()


# ==================================================
# 4. Turnaround distribution (boxplot)
# ==================================================

cw = df[
    df["service_days"]
    .notna()
]

groups = [
    g["service_days"].values
    for _, g in cw.groupby("service_type")
]

labels = [
    k
    for k, g in cw.groupby("service_type")
    if len(g) > 0
]


plt.figure(
    figsize=(8, 5)
)

plt.boxplot(
    groups,
    tick_labels=labels,
    showmeans=True,
)

plt.title(
    "Turnaround Distribution by Service Type"
)

plt.xlabel(
    "Service Type"
)

plt.ylabel(
    "Days"
)

for i, (_, g) in enumerate(
    cw.groupby("service_type")
):

    plt.text(
        i + 1,
        g["service_days"].max() + 0.3,
        f"n={len(g)}\nmedian={g['service_days'].median():.1f}",
        ha="center",
        fontsize=9,
    )

plt.ylim(
    0,
    cw["service_days"].max() + 2.5
)

plt.tight_layout()

plt.savefig(
    f"{chart_folder}/04_turnaround_boxplot.png",
    dpi=300
)

plt.close()


# ==================================================
# 5. On-time rate by promised time
# ==================================================

sla_by_promise = (
    sla
    .groupby("service_detail")
    .agg(
        orders=("no", "size"),
        on_time=(
            "is_late",
            lambda s: s.eq(False).sum(),
        ),
    )
)

sla_by_promise["on_time_pct"] = (
    sla_by_promise["on_time"]
    /
    sla_by_promise["orders"]
    *
    100
)


plt.figure(
    figsize=(8, 5)
)

sla_by_promise["on_time_pct"].plot(
    kind="bar"
)

plt.title(
    "On-Time Rate by Promised Turnaround"
)

plt.xlabel(
    "Promised Time"
)

plt.ylabel(
    "On-Time Rate (%)"
)

plt.xticks(
    rotation=0
)

plt.ylim(
    0,
    115
)

for i, (value, orders) in enumerate(
    zip(
        sla_by_promise["on_time_pct"],
        sla_by_promise["orders"],
    )
):

    plt.text(
        i,
        value + 2,
        f"{value:.0f}%\n(n={orders})",
        ha="center",
        va="bottom",
        fontsize=9,
    )

plt.tight_layout()

plt.savefig(
    f"{chart_folder}/05_on_time_rate.png",
    dpi=300
)

plt.close()


# ==================================================
# 6. Customer revenue Pareto
# ==================================================

rev_sorted = customer_revenue.sort_values(
    ascending=False
)

cum_share = (
    rev_sorted.cumsum()
    /
    rev_sorted.sum()
    *
    100
)

x_pct = (
    np.arange(1, len(rev_sorted) + 1)
    /
    len(rev_sorted)
    *
    100
)


plt.figure(
    figsize=(8, 5)
)

plt.plot(
    x_pct,
    cum_share.values,
    linewidth=2,
)

plt.axhline(
    80,
    color="red",
    linestyle="--",
    linewidth=1,
    label="80% revenue",
)

plt.axvline(
    20,
    color="gray",
    linestyle="--",
    linewidth=1,
    label="20% customers",
)

plt.title(
    "Customer Revenue Pareto Curve"
)

plt.xlabel(
    "Cumulative % of Customers"
)

plt.ylabel(
    "Cumulative % of Revenue"
)

plt.xlim(0, 100)

plt.ylim(0, 102)

plt.legend()

plt.tight_layout()

plt.savefig(
    f"{chart_folder}/06_pareto_customers.png",
    dpi=300
)

plt.close()


# =========================
# Export supporting tables
# =========================

revenue_service.to_csv(
    f"{kpi_folder}/revenue_by_service.csv"
)

service_volume.to_csv(
    f"{kpi_folder}/transaction_by_service.csv"
)

customer_frequency.to_csv(
    f"{kpi_folder}/customer_frequency.csv"
)

sla_by_promise.to_csv(
    f"{kpi_folder}/sla_by_promise.csv"
)

(
    pd.DataFrame(
        {
            "cum_pct_customers": x_pct.round(2),
            "cum_pct_revenue": cum_share.values.round(2),
        }
    )
).to_csv(
    f"{kpi_folder}/pareto_curve.csv",
    index=False,
)


print(
    "Visualization v2 completed."
)

print(
    "Charts and KPI files exported."
)
