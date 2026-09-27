# 04 CUSTOMER ANALYSIS

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# Paths

INPUT_FILE = "../data/processed/laundry_clean.csv"

OUTPUT_DIR = "../outputs/customer_analysis"

TABLE_DIR = "../outputs/tables"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

os.makedirs(
    TABLE_DIR,
    exist_ok=True
)


# Load data

df = pd.read_csv(INPUT_FILE)

df["order_date"] = pd.to_datetime(
    df["order_date"]
)

df = df[
    df["customer_id"]
    !=
    "Customer_UNKNOWN"
]

print("Dataset shape:")
print(df.shape)


# Basic customer value

customer_value = (
    df.groupby("customer_id")
    .agg(
        total_orders=("customer_id", "count"),
        orders_with_revenue=(
            "total_revenue",
            "count",
        ),
        total_revenue=("total_revenue", "sum"),
        total_weight=("weight_kg", "sum"),
        last_order_date=("order_date", "max"),
    )
)


customer_value["revenue_coverage"] = (
    customer_value["orders_with_revenue"]
    /
    customer_value["total_orders"]
)


customer_value["average_order_value"] = np.where(
    customer_value["orders_with_revenue"] > 0,

    customer_value["total_revenue"]
    /
    customer_value["orders_with_revenue"],

    np.nan,
)


snapshot_date = df["order_date"].max()

customer_value["recency_days"] = (
    snapshot_date
    -
    customer_value["last_order_date"]
).dt.days


customer_value = customer_value.fillna(
    {
        "total_revenue": 0,
        "total_weight": 0,
    }
)


print("\nCustomer Value Summary:")
print(
    customer_value
    .sort_values(
        "total_revenue",
        ascending=False,
    )
    .head(10)
    .drop(columns=["last_order_date"])
    .round(1)
)


# Customer segmentation

# Percentile thresholds (observed revenue)

revenue_q75 = customer_value[
    "total_revenue"
].quantile(0.75)

orders_q75 = customer_value[
    "total_orders"
].quantile(0.75)

orders_min_regular = 3


def customer_segment(row):

    # Premium:
    # top quartile revenue AND top quartile frequency

    if (
        row["total_revenue"] >= revenue_q75
        and
        row["total_orders"] >= orders_q75
    ):
        return "Premium Customer"

    # High-Value Occasional:
    # top quartile revenue but low frequency

    elif (
        row["total_revenue"] >= revenue_q75
    ):
        return "High-Value Occasional"

    # Regular:
    # frequency above threshold but revenue below top quartile

    elif (
        row["total_orders"]
        >= orders_min_regular
    ):
        return "Regular Customer"

    else:
        return "Low Frequency Customer"


customer_value["segment"] = (
    customer_value
    .apply(customer_segment, axis=1)
)


print("\nSegmentation thresholds:")
print(f"  revenue_q75          : {revenue_q75:,.0f}")
print(f"  orders_q75           : {orders_q75}")
print(f"  orders_min_regular   : {orders_min_regular}")


# Segment summary

segment_summary = (
    customer_value
    .groupby("segment")
    .agg(
        customers=("segment", "size"),
        orders=("total_orders", "sum"),
        revenue=("total_revenue", "sum"),
    )
)


segment_summary["customer_percentage"] = (
    segment_summary["customers"]
    /
    customer_value.shape[0]
    *
    100
)


segment_summary["revenue_percentage"] = (
    segment_summary["revenue"]
    /
    customer_value["total_revenue"].sum()
    *
    100
)

segment_summary = segment_summary.sort_values(
    "revenue",
    ascending=False,
)

segment_summary[
    "revenue_per_order"
] = (
    segment_summary["revenue"]
    /
    segment_summary["orders"]
).round(0)


print("\nSegment performance:")
print(
    segment_summary
    .round(2)
)


# Sensitivity check

high_coverage = customer_value[
    customer_value["revenue_coverage"]
    >= 0.8
]


def segment_share(table):

    q75_rev = table["total_revenue"].quantile(0.75)

    q75_ord = table["total_orders"].quantile(0.75)

    def rule(row):

        if (
            row["total_revenue"] >= q75_rev
            and
            row["total_orders"] >= q75_ord
        ):
            return "Premium Customer"

        elif row["total_revenue"] >= q75_rev:
            return "High-Value Occasional"

        elif row["total_orders"] >= orders_min_regular:
            return "Regular Customer"

        return "Low Frequency Customer"

    labels = table.apply(rule, axis=1)

    revenue = table["total_revenue"]

    return (
        revenue.groupby(labels)
        .sum()
        /
        revenue.sum()
        *
        100
    ).round(1)


share_all = segment_share(customer_value)

share_robust = segment_share(high_coverage)


sensitivity = pd.DataFrame(
    {
        "all_customers_pct": share_all,
        "coverage_ge_80pct_pct": share_robust,
    }
)


print("\nSensitivity (revenue share, all vs high-coverage customers):")
print(
    sensitivity
)


# Segment x SLA

segment_map = customer_value["segment"]

df["segment"] = df["customer_id"].map(
    segment_map
)

sla_df = df[
    df["is_late"]
    .notna()
]


segment_sla = (
    sla_df
    .groupby("segment")
    .agg(
        orders=("no", "size"),
        mean_days=("service_open_days", "mean"),
        on_time=(
            "is_late",
            lambda s: s.eq(False).sum(),
        ),
    )
)

segment_sla["on_time_pct"] = (
    segment_sla["on_time"]
    /
    segment_sla["orders"]
    *
    100
).round(1)

segment_sla = segment_sla.round(2)


print("\nSegment SLA (are high-value customers served better?):")
print(
    segment_sla
)


# Export tables

customer_value.to_csv(
    f"{OUTPUT_DIR}/customer_value_summary.csv"
)

segment_summary.to_csv(
    f"{OUTPUT_DIR}/customer_segment_summary.csv"
)

segment_sla.to_csv(
    f"{OUTPUT_DIR}/segment_sla_summary.csv"
)

customer_value.to_csv(
    f"{TABLE_DIR}/customer_value_summary.csv"
)

segment_summary.to_csv(
    f"{TABLE_DIR}/segment_performance.csv"
)


# Top customers by frequency

top_frequency = (
    customer_value
    .sort_values(
        "total_orders",
        ascending=False,
    )
    .head(10)
)


plt.figure(figsize=(10, 6))

plt.barh(
    top_frequency.index[::-1],
    top_frequency["total_orders"][::-1],
)

for i, v in enumerate(
    top_frequency["total_orders"][::-1]
):

    plt.text(
        v + 0.2,
        i,
        str(v),
        va="center",
    )


plt.title(
    "Top Customers by Purchase Frequency"
)

plt.xlabel(
    "Number of Orders"
)

plt.ylabel(
    "Customer ID"
)

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/top_customer_frequency.png",
    dpi=300,
)

plt.close()


# Top customers by revenue

top_revenue = (
    customer_value
    .sort_values(
        "total_revenue",
        ascending=False,
    )
    .head(10)
)


plt.figure(figsize=(10, 6))

plt.barh(
    top_revenue.index[::-1],
    top_revenue["total_revenue"][::-1],
)


for i, v in enumerate(
    top_revenue["total_revenue"][::-1]
):

    plt.text(
        v + 5000,
        i,
        f"Rp{v / 1000:.0f}K",
        va="center",
    )


plt.title(
    "Top Customers by Recorded Revenue"
)

plt.xlabel(
    "Revenue (IDR)"
)

plt.ylabel(
    "Customer ID"
)

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/top_customer_revenue.png",
    dpi=300,
)

plt.close()


# Segment distribution

segment_count = (
    customer_value["segment"]
    .value_counts()
)


plt.figure(figsize=(8, 5))

plt.bar(
    segment_count.index,
    segment_count.values,
)


for i, v in enumerate(
    segment_count.values
):

    plt.text(
        i,
        v + 2,
        str(v),
        ha="center",
    )


plt.title(
    "Customer Segment Distribution"
)

plt.ylabel(
    "Number of Customers"
)

plt.xticks(
    rotation=20
)

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/customer_segment_distribution.png",
    dpi=300,
)

plt.close()


# Revenue by segment

plt.figure(figsize=(8, 5))

plt.bar(
    segment_summary.index,
    segment_summary["revenue"],
)


for i, v in enumerate(
    segment_summary["revenue"]
):

    plt.text(
        i,
        v + 100000,
        f"Rp{v / 1e6:.1f}M",
        ha="center",
    )


plt.title(
    "Revenue Contribution by Customer Segment"
)

plt.ylabel(
    "Revenue (IDR)"
)

plt.xticks(
    rotation=20
)

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/revenue_by_segment.png",
    dpi=300,
)

plt.close()


# Revenue per order by segment

plt.figure(figsize=(8, 5))

plt.bar(
    segment_summary.index,
    segment_summary["revenue_per_order"],
)


for i, v in enumerate(
    segment_summary["revenue_per_order"]
):

    plt.text(
        i,
        v + 500,
        f"Rp{v / 1000:.0f}K",
        ha="center",
    )


plt.title(
    "Revenue per Order by Customer Segment"
)

plt.ylabel(
    "Revenue per Order (IDR)"
)

plt.xticks(
    rotation=20
)

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/revenue_per_order_segment.png",
    dpi=300,
)

plt.close()


# Frequency vs revenue scatter

colors = {
    "Premium Customer": "#1f77b4",
    "High-Value Occasional": "#2ca02c",
    "Regular Customer": "#ff7f0e",
    "Low Frequency Customer": "#d62728",
}


plt.figure(figsize=(9, 6))

for segment, group in customer_value.groupby(
    "segment"
):

    plt.scatter(
        group["total_orders"],
        group["total_revenue"],
        label=segment,
        alpha=0.7,
        color=colors.get(segment, "gray"),
    )


plt.axhline(
    revenue_q75,
    color="black",
    linestyle="--",
    linewidth=1,
)

plt.axvline(
    orders_q75,
    color="black",
    linestyle="--",
    linewidth=1,
)

plt.title(
    "Customer Segmentation: Frequency vs Revenue"
)

plt.xlabel(
    "Total Orders"
)

plt.ylabel(
    "Total Revenue (IDR)"
)

plt.legend(
    fontsize=8
)

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/segment_scatter.png",
    dpi=300,
)

plt.close()


# Final output

print("\nFinal segment summary:")
print(
    segment_summary
    .round(2)
)

print(
    f"\nCustomers with 0 recorded revenue : "
    f"{int((customer_value['total_revenue'] == 0).sum())}"
)

print(
    f"Customers below 80% coverage      : "
    f"{int((customer_value['revenue_coverage'] < 0.8).sum())}"
)

print(
    "\nCustomer analysis completed."
)
