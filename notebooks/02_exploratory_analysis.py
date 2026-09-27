# 02 EXPLORATORY ANALYSIS


import numpy as np
import pandas as pd


pd.set_option(
    "display.max_columns",
    None
)


# =========================
# Load cleaned dataset
# =========================

df = pd.read_csv(
    "../data/processed/laundry_clean.csv"
)

df["order_date"] = pd.to_datetime(
    df["order_date"]
)

df["completion_date"] = pd.to_datetime(
    df["completion_date"]
)


print("Dataset shape:")
print(df.shape)


identified = df[
    df["customer_id"]
    !=
    "Customer_UNKNOWN"
].copy()


# =========================
# 1. Dataset overview
# =========================

weight_based = df[
    df["is_weight_based"]
]


overview = pd.DataFrame(
    {
        "Metric": [
            "Total Transactions",
            "Identified Transactions",
            "Identified Customers",
            "Total Weight (kg, weight-based only)",
            "Average Weight per Transaction (kg)",
            "Revenue Coverage (%)",
            "Weight Coverage (%)",
            "Cost Coverage (%)",
        ],

        "Value": [
            len(df),

            len(identified),

            identified[
                "customer_id"
            ].nunique(),

            round(
                weight_based[
                    "weight_kg"
                ].sum(),
                1
            ),

            round(
                weight_based[
                    "weight_kg"
                ].mean(),
                2
            ),

            round(
                df["has_revenue"].mean() * 100,
                1
            ),

            round(
                df["has_weight"].mean() * 100,
                1
            ),

            round(
                df["has_cost"].mean() * 100,
                1
            ),
        ],
    }
)


print("\nOverview Summary:")
print(overview)


print("\nData quality:")
print(
    df["data_quality_flag"]
    .value_counts()
)


# =========================
# 2. Revenue missingness (MNAR check)
# =========================

coverage = (
    df
    .groupby("service_type")
    .agg(
        transactions=("no", "size"),
        revenue_observed=("total_revenue", "count"),
        weight_observed=("weight_kg", "count"),
    )
)

coverage[
    "revenue_coverage_pct"
] = (
    coverage["revenue_observed"]
    /
    coverage["transactions"]
    *
    100
).round(1)


print("\nRevenue coverage by service (MNAR check):")
print(
    coverage
)

if coverage[
    "revenue_coverage_pct"
].min() < 50:

    print(
        "\nWARNING: revenue missingness is NOT random."
    )
    print(
        "Revenue-by-service comparisons must be read"
    )
    print(
        "together with the coverage column."
    )


# =========================
# 3. Customer KPI & concentration
# =========================

customer_orders = (
    identified
    .groupby("customer_id")
    .size()
    .sort_values(ascending=False)
)


repeat_customers = int(
    (customer_orders > 1).sum()
)

identified_customers = int(
    customer_orders.count()
)

repeat_rate = (
    repeat_customers
    /
    identified_customers
    *
    100
)


customer_kpi = pd.DataFrame(
    {
        "Metric": [
            "Identified Customers",
            "Repeat Customers",
            "One-time Customers",
            "Repeat Customer Rate (%)",
        ],

        "Value": [
            identified_customers,

            repeat_customers,

            identified_customers
            -
            repeat_customers,

            round(repeat_rate, 2),
        ],
    }
)


print("\nCustomer KPI:")
print(customer_kpi)


customer_revenue = (
    identified
    .groupby("customer_id")["total_revenue"]
    .sum()
    .sort_values(ascending=False)
)


total_identified_revenue = (
    customer_revenue.sum()
)

n_customers = len(customer_revenue)

top20_n = int(
    np.ceil(0.2 * n_customers)
)

top20_share = (
    customer_revenue.head(top20_n).sum()
    /
    total_identified_revenue
    *
    100
)


one_time_ids = customer_orders[
    customer_orders == 1
].index

repeat_ids = customer_orders[
    customer_orders > 1
].index

one_time_revenue = customer_revenue[
    customer_revenue.index.isin(one_time_ids)
].sum()

repeat_revenue = customer_revenue[
    customer_revenue.index.isin(repeat_ids)
].sum()


concentration = pd.DataFrame(
    {
        "Metric": [
            "Top 20% customers share of revenue (%)",
            "One-time customers",
            "One-time share of customers (%)",
            "One-time share of revenue (%)",
            "Repeat share of revenue (%)",
        ],

        "Value": [
            round(top20_share, 1),

            len(one_time_ids),

            round(
                len(one_time_ids)
                /
                n_customers
                *
                100,
                1
            ),

            round(
                one_time_revenue
                /
                total_identified_revenue
                *
                100,
                1
            ),

            round(
                repeat_revenue
                /
                total_identified_revenue
                *
                100,
                1
            ),
        ],
    }
)


print("\nRevenue concentration:")
print(concentration)


# =========================
# 4. Revenue analysis (with coverage)
# =========================

revenue_service = (
    df
    .groupby("service_type")
    .agg(
        revenue_observed=("total_revenue", "sum"),
        transactions=("no", "size"),
        revenue_observed_n=("total_revenue", "count"),
    )
)

revenue_service[
    "revenue_coverage_pct"
] = (
    revenue_service["revenue_observed_n"]
    /
    revenue_service["transactions"]
    *
    100
).round(1)

revenue_service[
    "revenue_share_pct"
] = (
    revenue_service["revenue_observed"]
    /
    revenue_service["revenue_observed"].sum()
    *
    100
).round(1)

revenue_service = revenue_service.sort_values(
    "revenue_observed",
    ascending=False,
)


print("\nRevenue contribution by service (observed only):")
print(
    revenue_service
)


revenue_total = df["total_revenue"].sum()

average_order_value = df[
    "total_revenue"
].mean()

revenue_summary = pd.DataFrame(
    {
        "Metric": [
            "Recorded Revenue (all rows)",
            "Recorded Revenue (identified customers)",
            "Average Order Value (observed rows)",
            "Highest Transaction",
            "Revenue Coverage (%)",
        ],

        "Value": [
            revenue_total,

            identified[
                "total_revenue"
            ].sum(),

            round(average_order_value, 0),

            df["total_revenue"].max(),

            round(
                df["has_revenue"].mean() * 100,
                1
            ),
        ],
    }
)


print("\nRevenue summary:")
print(revenue_summary)


revenue_category = (
    df
    .groupby("service_category")
    .agg(
        transactions=("no", "size"),
        revenue_observed=("total_revenue", "sum"),
        revenue_observed_n=("total_revenue", "count"),
    )
)

revenue_category[
    "revenue_share_pct"
] = (
    revenue_category["revenue_observed"]
    /
    revenue_category["revenue_observed"].sum()
    *
    100
).round(1)

revenue_category[
    "revenue_coverage_pct"
] = (
    revenue_category["revenue_observed_n"]
    /
    revenue_category["transactions"]
    *
    100
).round(1)


service_category_summary = (
    df["service_category"]
    .value_counts()
)


print("\nRevenue by service category:")
print(
    revenue_category
)


# potential unrecorded revenue (diagnostic only)

rate_by_service = (
    df.loc[
        df["revenue_per_kg"].notna()
    ]
    .groupby("service_type")["revenue_per_kg"]
    .median()
)

missing_rev = (
    df["total_revenue"].isna()
    &
    df["weight_kg"].gt(0)
    &
    df["service_type"]
    .isin(rate_by_service.index)
)

gap_df = df.loc[
    missing_rev
].copy()

gap_df["estimated_gap"] = (
    gap_df["weight_kg"]
    *
    gap_df["service_type"].map(rate_by_service)
)

revenue_gap = (
    gap_df
    .groupby("service_type")
    .agg(
        orders_missing_revenue=("no", "size"),
        estimated_unrecorded_revenue=("estimated_gap", "sum"),
    )
)

revenue_gap[
    "share_of_observed_pct"
] = (
    revenue_gap["estimated_unrecorded_revenue"]
    /
    revenue_total
    *
    100
).round(1)


print("\nPotential unrecorded revenue (weight x median rate):")
print(
    revenue_gap.round(0)
)


# =========================
# 5. Volume, weekday, trend
# =========================

daily_orders = (
    df["order_day"]
    .value_counts()
)

weekday_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

observed = (
    daily_orders
    .reindex(weekday_order)
    .fillna(0)
    .astype(int)
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


open_days = [
    d
    for d in weekday_order
    if d != "Sunday"
]

expected = (
    observed[open_days].sum()
    *
    exposure[open_days]
    /
    exposure[open_days].sum()
)


weekday_summary = pd.DataFrame(
    {
        "day": open_days,
        "observed": observed[open_days].values,
        "days_in_range": exposure[open_days].values,
        "expected": expected.round(1).values,
    }
)

weekday_summary["deviation_pct"] = (
    (
        weekday_summary["observed"]
        -
        weekday_summary["expected"]
    )
    /
    weekday_summary["expected"]
    *
    100
).round(1)


chi2 = (
    (
        weekday_summary["observed"]
        -
        weekday_summary["expected"]
    )
    ** 2
    /
    weekday_summary["expected"]
).sum()


rng = np.random.default_rng(42)

probs = (
    exposure[open_days]
    /
    exposure[open_days].sum()
).values

n_orders = int(observed[open_days].sum())

sims = rng.multinomial(
    n_orders,
    probs,
    size=10000
)

sim_chi2 = (
    (sims - n_orders * probs) ** 2
    / (n_orders * probs)
).sum(axis=1)

weekday_p = float(
    (sim_chi2 >= chi2).sum()
    +
    1
) / float(len(sim_chi2) + 1)


print("\nWeekday pattern (exposure-adjusted):")
print(
    weekday_summary.to_string(index=False)
)

print(
    f"\n  chi2 = {chi2:.2f}"
    f"  (Monte Carlo p = {weekday_p:.4f})"
)

print(
    "\n  Sunday: 0 transactions"
    " (day closed, excluded from test)"
)


monthly = (
    df
    .groupby("order_month")
    .agg(
        orders=("no", "size"),
        revenue=("total_revenue", "sum"),
        weight=("weight_kg", "sum"),
    )
)

monthly["revenue_per_order"] = (
    monthly["revenue"]
    /
    monthly["orders"]
).round(0)


print("\nMonthly trend:")
print(monthly)


# =========================
# 6. Operational & SLA
# =========================

turnaround = df["service_days"].dropna()

turnaround_stats = pd.DataFrame(
    {
        "Metric": [
            "Orders with turnaround recorded",
            "Mean (days)",
            "Median (days)",
            "P90 (days)",
            "Max (days)",
        ],

        "Value": [
            len(turnaround),

            round(turnaround.mean(), 2),

            round(turnaround.median(), 2),

            round(
                turnaround.quantile(0.9),
                2
            ),

            round(turnaround.max(), 2),
        ],
    }
)


print("\nTurnaround distribution:")
print(turnaround_stats)


turnaround_service = (
    df
    .groupby("service_type")
    .agg(
        orders=("service_days", "count"),
        mean_days=("service_days", "mean"),
        median_days=("service_days", "median"),
        p90_days=(
            "service_days",
            lambda s: s.quantile(0.9),
        ),
    )
    .round(2)
    .sort_values("median_days")
)


print("\nTurnaround by service:")
print(turnaround_service)


sla = df[
    df["is_late"].notna()
].copy()


sla_overall = pd.DataFrame(
    {
        "Metric": [
            "Orders with SLA measurable",
            "On-time orders",
            "On-time rate (%)",
            "Average days late (late orders)",
        ],

        "Value": [
            len(sla),

            int(
                sla["is_late"]
                .eq(False)
                .sum()
            ),

            round(
                sla["is_late"]
                .eq(False)
                .sum()
                /
                len(sla)
                *
                100,
                1
            ),

            round(
                sla.loc[
                    sla["is_late"] == True,
                    "days_late",
                ].mean(),
                2,
            ),
        ],
    }
)


print("\nSLA performance (actual vs promised):")
print(sla_overall)


sla_by_promise = (
    sla
    .groupby("service_detail")
    .agg(
        orders=("no", "size"),
        mean_days=("service_days", "mean"),
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
).round(1)

sla_by_promise = sla_by_promise.round(2)


print("\nSLA by promised time:")
print(
    sla_by_promise
)


sla_by_service = (
    sla
    .groupby("service_type")
    .agg(
        orders=("no", "size"),
        mean_days=("service_days", "mean"),
        on_time=(
            "is_late",
            lambda s: s.eq(False).sum(),
        ),
    )
)

sla_by_service["on_time_pct"] = (
    sla_by_service["on_time"]
    /
    sla_by_service["orders"]
    *
    100
).round(1)


print("\nSLA by service type:")
print(
    sla_by_service
)


# =========================
# 7. Frequency vs value
# =========================

def spearman(x, y):

    return float(
        pd.Series(x)
        .rank()
        .corr(
            pd.Series(y)
            .rank()
        )
    )


customer_value = (
    identified
    .groupby("customer_id")
    .agg(
        orders=("customer_id", "size"),
        revenue=("total_revenue", "sum"),
        orders_with_revenue=(
            "total_revenue",
            "count",
        ),
    )
)

customer_value["aov"] = np.where(
    customer_value["orders_with_revenue"] > 0,

    customer_value["revenue"]
    /
    customer_value["orders_with_revenue"],

    np.nan,
)


with_revenue = customer_value[
    customer_value["aov"]
    .notna()
]

rho_revenue = spearman(
    customer_value["orders"],
    customer_value["revenue"],
)

rho_aov = spearman(
    with_revenue["orders"],
    with_revenue["aov"],
)


correlation_summary = pd.DataFrame(
    {
        "Relationship": [
            "orders ~ total_revenue",
            "orders ~ average_order_value",
        ],

        "spearman_rho": [
            round(rho_revenue, 3),
            round(rho_aov, 3),
        ],

        "n_customers": [
            len(customer_value),
            len(with_revenue),
        ],
    }
)


print("\nCorrelation summary:")
print(correlation_summary)


# =========================
# 8. Voucher analysis
# =========================

df["voucher_used"] = (
    df["voucher_code"]
    .ne("NO VOUCHER")
)


voucher_summary = (
    df
    .groupby("voucher_used")
    .agg(
        orders=("no", "size"),
        revenue_observed=("total_revenue", "sum"),
        revenue_observed_n=("total_revenue", "count"),
        mean_revenue=("total_revenue", "mean"),
    )
    .round(0)
)

voucher_summary.index = [
    "Not Used" if not used else "Used"
    for used in voucher_summary.index
]

voucher_summary.index.name = "Voucher Status"


print("\nVoucher summary:")
print(
    voucher_summary
)


# =========================
# Export
# =========================

output_folder = "../data/processed"


overview.to_csv(
    f"{output_folder}/overview_summary.csv",
    index=False
)

customer_kpi.to_csv(
    f"{output_folder}/customer_kpi.csv",
    index=False
)

concentration.to_csv(
    f"{output_folder}/concentration_summary.csv",
    index=False
)

correlation_summary.to_csv(
    f"{output_folder}/correlation_summary.csv",
    index=False
)

customer_orders.to_csv(
    f"{output_folder}/customer_order_summary.csv"
)

(
    df["service_type"]
    .value_counts()
).to_csv(
    f"{output_folder}/service_summary.csv"
)

service_category_summary.to_csv(
    f"{output_folder}/service_category_summary.csv"
)

revenue_category.to_csv(
    f"{output_folder}/revenue_category_summary.csv"
)

voucher_summary.to_csv(
    f"{output_folder}/voucher_summary.csv"
)

coverage.to_csv(
    f"{output_folder}/coverage_report.csv"
)

revenue_summary.to_csv(
    f"{output_folder}/revenue_summary.csv",
    index=False
)

revenue_service.to_csv(
    f"{output_folder}/revenue_service_summary.csv"
)

revenue_gap.to_csv(
    f"{output_folder}/revenue_gap_report.csv"
)

weekday_summary.to_csv(
    f"{output_folder}/weekday_summary.csv",
    index=False
)

monthly.to_csv(
    f"{output_folder}/monthly_summary.csv"
)

daily_orders.to_csv(
    f"{output_folder}/daily_order_summary.csv"
)

turnaround_service.to_csv(
    f"{output_folder}/turnaround_summary.csv"
)

sla_overall.to_csv(
    f"{output_folder}/sla_summary.csv",
    index=False
)

sla_by_promise.to_csv(
    f"{output_folder}/sla_by_promise_summary.csv"
)


print("\nEDA v2 completed. Summary files exported.")
