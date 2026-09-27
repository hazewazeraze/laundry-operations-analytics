# 01 DATA PREPARATION


import os
import re

import numpy as np
import pandas as pd


pd.set_option(
    "display.max_columns",
    None
)


ERROR_TOKENS = [
    "#ERROR!",
    "#REF!",
    "#VALUE!",
    "#DIV/0!",
    "#NAME?",
    "#N/A",
    "N/A",
]


# =========================
# Load raw data
# =========================

df = pd.read_csv(
    "../data/raw/laundry_raw.csv",
    header=None
)

raw_rows = len(df)

df = df.dropna(
    how="all"
)

rows_with_data = len(df)


# =========================
# Assign column names
# =========================

df.columns = [
    "no",
    "customer_name",
    "order_status",
    "order_date",
    "completion_date",
    "service_type",
    "service_detail",
    "fragrance",
    "weight_kg",
    "notes",
    "unit_cost",
    "express_cost",
    "total_revenue",
    "voucher_amount",
    "voucher_code",
    "transfer_amount",
    "cash_payment",
    "customer_received",
    "extra_column",
]


df.drop(
    columns=["extra_column"],
    inplace=True
)


# =========================
# Remove spreadsheet errors
# =========================

try:
    string_columns = (
        df.select_dtypes(
            include=["object", "str"]
        )
        .columns
        .tolist()
    )
except TypeError:
    string_columns = (
        df.select_dtypes(include="object")
        .columns
        .tolist()
    )

for col in string_columns:

    df[col] = (
        df[col]
        .str.strip()
    )


df = df.replace(
    ERROR_TOKENS,
    np.nan
)


# =========================
# Date conversion
# =========================

df["order_date"] = pd.to_datetime(
    df["order_date"],
    format="%d/%m/%Y",
    errors="coerce"
)

df["completion_date"] = pd.to_datetime(
    df["completion_date"],
    format="%d/%m/%Y",
    errors="coerce"
)


df.loc[
    df["order_date"].dt.year < 2015,
    "order_date"
] = pd.NaT

df.loc[
    df["completion_date"].dt.year < 2015,
    "completion_date"
] = pd.NaT


# =========================
# Standardize text
# =========================

text_columns = [
    "order_status",
    "service_type",
    "service_detail",
    "fragrance",
    "voucher_code",
    "cash_payment",
    "customer_received",
]

for col in text_columns:

    df[col] = (
        df[col]
        .str.upper()
    )


# =========================
# Numeric conversion
# =========================

df["weight_kg"] = pd.to_numeric(
    df["weight_kg"],
    errors="coerce"
)


money_columns = [
    "unit_cost",
    "express_cost",
    "total_revenue",
    "voucher_amount",
    "transfer_amount",
]

for col in money_columns:

    cleaned = (
        df[col]
        .str.replace(
            r"[Rr][Pp]",
            "",
            regex=True
        )
        .str.replace(
            r"[\s.,]",
            "",
            regex=True
        )
    )

    df[col] = pd.to_numeric(
        cleaned,
        errors="coerce"
    )


# =========================
# Remove non-transaction rows
# =========================

no_numeric = pd.to_numeric(
    df["no"],
    errors="coerce"
)

section_header_rows = no_numeric.isna()

junk_rows = (
    df["service_type"].isna()
    &
    df["order_date"].isna()
    &
    df["customer_name"].isna()
)

junk_mask = (
    section_header_rows
    |
    junk_rows
)

rows_dropped_junk = int(
    junk_mask.sum()
)

df = df[~junk_mask].copy()

df["no"] = (
    pd.to_numeric(
        df["no"],
        errors="coerce"
    )
    .astype("Int64")
)


# =========================
# Create customer ID
# =========================

name_key = (
    df["customer_name"]
    .str.upper()
)

customer_map = {
    name: f"Customer_{i+1:03d}"
    for i, name in enumerate(
        sorted(
            name_key
            .dropna()
            .unique()
        )
    )
}

df["customer_id"] = (
    name_key
    .map(customer_map)
)

df["customer_id"] = (
    df["customer_id"]
    .fillna("Customer_UNKNOWN")
)


# =========================
# Remove duplicate transactions
# =========================

dup_keys = [
    "customer_id",
    "order_date",
    "completion_date",
    "service_type",
    "weight_kg",
    "total_revenue",
]

dup_candidates = (
    df["customer_id"]
    .ne("Customer_UNKNOWN")
    |
    df["order_date"]
    .notna()
)

dup_mask = pd.Series(
    False,
    index=df.index
)

dup_mask.loc[dup_candidates] = (
    df.loc[dup_candidates]
    .duplicated(
        subset=dup_keys,
        keep="first"
    )
)

rows_dropped_duplicates = int(
    dup_mask.sum()
)

df = df[~dup_mask].copy()


soft_keys = [
    "customer_id",
    "order_date",
    "completion_date",
    "weight_kg",
    "total_revenue",
]

ambiguous = (
    df["customer_id"]
    .eq("Customer_UNKNOWN")
    &
    (
        df["weight_kg"]
        .notna()
        |
        df["total_revenue"]
        .notna()
    )
)

df["possible_duplicate"] = False

df.loc[
    ambiguous,
    "possible_duplicate"
] = (
    df.loc[ambiguous]
    .duplicated(
        subset=soft_keys,
        keep=False)
)


# =========================
# Handle missing values
# =========================

df["voucher_amount"] = (
    df["voucher_amount"]
    .fillna(0)
)

df["voucher_code"] = (
    df["voucher_code"]
    .fillna("NO VOUCHER")
)

df["fragrance"] = (
    df["fragrance"]
    .fillna("NOT RECORDED")
)

df["order_status"] = (
    df["order_status"]
    .fillna("UNKNOWN")
)

df["service_detail"] = (
    df["service_detail"]
    .fillna("NOT SPECIFIED")
)


# =========================
# Data quality flags
# =========================

df["has_customer"] = (
    df["customer_name"]
    .notna()
)

df["has_revenue"] = (
    df["total_revenue"]
    .notna()
)

df["has_weight"] = (
    df["weight_kg"]
    .notna()
)

df["has_cost"] = (
    df["unit_cost"]
    .notna()
)

df["has_completion"] = (
    df["completion_date"]
    .notna()
)


def quality_check(row):

    issues = []

    if row["has_customer"] == False:
        issues.append("Customer")

    if pd.isna(
        row["order_date"]
    ):
        issues.append("Order Date")

    if row["has_completion"] == False:
        issues.append("Completion Date")

    if row["has_revenue"] == False:
        issues.append("Revenue")

    if row["has_weight"] == False:
        issues.append("Weight")

    if len(issues) == 0:
        return "Complete"

    return (
        "Missing "
        +
        ", ".join(issues)
    )


df["data_quality_flag"] = (
    df.apply(
        quality_check,
        axis=1
    )
)


df["customer_name"] = (
    df["customer_name"]
    .fillna("UNKNOWN CUSTOMER")
)


# =========================
# Create service category
# =========================

package_services = [
    "PCS",
    "PCL",
    "PS",
]

df["service_category"] = np.select(
    [
        df["service_type"]
        .isin(package_services),

        df["service_type"]
        .eq("SATUAN"),
    ],

    [
        "LAUNDRY PACKAGE",
        "PER ITEM",
    ],

    default="OTHER SERVICE"
)


df["is_weight_based"] = (
    ~df["service_type"]
    .isin(["SATUAN"])
    &
    df["weight_kg"]
    .gt(0)
)


# =========================
# Feature engineering
# =========================

raw_days = (
    df["completion_date"]
    -
    df["order_date"]
).dt.days

negative_turnaround_rows = int(
    (raw_days < 0)
    .sum()
)

df["service_days"] = raw_days.where(
    raw_days >= 0
)


df["revenue_per_kg"] = np.where(
    df["total_revenue"].notna()
    &
    df["weight_kg"].gt(0),

    df["total_revenue"]
    /
    df["weight_kg"],

    np.nan
)


df["order_day"] = (
    df["order_date"]
    .dt.day_name()
)

df["order_month"] = (
    df["order_date"]
    .dt.month_name()
)


def parse_promised_days(value):

    match = re.search(
        r"(\d+)",
        str(value)
    )

    if match is None:
        return np.nan

    number = float(
        match.group(1)
    )

    if "JAM" in str(value).upper():
        return number / 24.0

    return number


df["promised_days"] = (
    df["service_detail"]
    .apply(parse_promised_days)
)


df["is_late"] = (
    df["service_days"]
    >
    df["promised_days"]
).astype("boolean")


df.loc[
    df["service_days"].isna()
    |
    df["promised_days"].isna(),
    "is_late"
] = pd.NA


df["days_late"] = (
    df["service_days"]
    -
    df["promised_days"]
).where(
    df["service_days"].notna()
)


# =========================
# Remove original customer name
# =========================

df.drop(
    columns=["customer_name"],
    inplace=True
)


# =========================
# Coverage reports
# =========================

column_coverage = (
    df.notna()
    .mean()
    .mul(100)
    .round(2)
    .rename("coverage_pct")
    .reset_index()
    .rename(
        columns={"index": "column"}
    )
)


service_coverage = (
    df
    .groupby("service_type")
    .agg(
        transactions=("no", "size"),
        revenue_observed=("total_revenue", "count"),
        weight_observed=("weight_kg", "count"),
    )
)

service_coverage[
    "revenue_coverage_pct"
] = (
    service_coverage["revenue_observed"]
    /
    service_coverage["transactions"]
    *
    100
).round(1)


# =========================
# Final check
# =========================

print("\nReconciliation:")
print(f"  raw rows            : {raw_rows}")
print(f"  after empty-row drop: {rows_with_data}")
print(f"  dropped junk rows   : {rows_dropped_junk}")
print(f"  dropped duplicates  : {rows_dropped_duplicates}")
print(f"  final transactions  : {len(df)}")


print("\nIdentified customers:")
print(
    df[
        df["customer_id"]
        !=
        "Customer_UNKNOWN"
    ]["customer_id"]
    .nunique()
)


print("\nData quality summary:")
print(
    df["data_quality_flag"]
    .value_counts()
)


print("\nRevenue coverage by service:")
print(
    service_coverage
)


print("\nColumn coverage (% non-null):")
print(
    column_coverage
    .sort_values("coverage_pct")
    .head(10)
    .to_string(index=False)
)


print(
    f"\n  unit_cost coverage : "
    f"{df['has_cost'].mean() * 100:.1f}%"
    f"  -> margin/cost analysis not possible"
)

print(
    f"  negative turnaround : "
    f"{negative_turnaround_rows}"
)

print(
    f"  possible duplicates : "
    f"{int(df['possible_duplicate'].sum())}"
    f"  -> flagged, not removed"
)


print("\nService category summary:")
print(
    df["service_category"]
    .value_counts()
)


print("\nFinal columns:")
print(
    df.columns.tolist()
)


# =========================
# Save clean dataset
# =========================

output_folder = "../data/processed"

os.makedirs(
    output_folder,
    exist_ok=True
)


df.to_csv(
    f"{output_folder}/laundry_clean.csv",
    index=False
)


column_coverage.to_csv(
    f"{output_folder}/data_quality_report.csv",
    index=False
)


service_coverage.to_csv(
    f"{output_folder}/service_coverage_report.csv"
)


print(
    "\nDone. Clean dataset saved."
)
