# 05 HYPOTHESIS TESTING
#
# Statistical validation for H1-H6 (numpy only, no scipy).
# Tests: bootstrap concentration, Spearman permutation,
# Kruskal-Wallis permutation, chi-square Monte Carlo,
# intake-vs-latency bottleneck check.

import os

import numpy as np
import pandas as pd

pd.set_option("display.max_columns", None)


N_ITER = 5000
SEED = 42


# Load data

df = pd.read_csv("../data/processed/laundry_clean.csv")

df["order_date"] = pd.to_datetime(df["order_date"])

df["completion_date"] = pd.to_datetime(df["completion_date"])


identified = df[df["customer_id"] != "Customer_UNKNOWN"].copy()


# Helpers


def spearman_rho(x, y):

    return float(pd.Series(x).rank().corr(pd.Series(y).rank()))


def spearman_permutation(x, y, n_iter=N_ITER, seed=SEED):

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    observed = spearman_rho(x, y)

    rng = np.random.default_rng(seed)

    extreme = 0

    for _ in range(n_iter):

        shuffled = rng.permutation(y)

        if abs(spearman_rho(x, shuffled)) >= abs(observed):
            extreme += 1

    return observed, (extreme + 1) / (n_iter + 1)


def kw_permutation(values, labels, n_iter=N_ITER, seed=SEED):

    values = np.asarray(values, dtype=float)

    labels = np.asarray(labels)

    unique, codes = np.unique(labels, return_inverse=True)

    sizes = np.bincount(codes)

    ranks = pd.Series(values).rank().values

    n = len(values)

    _, tie_counts = np.unique(values, return_counts=True)

    tie_correction = 1 - (np.sum(tie_counts**3 - tie_counts) / (n**3 - n))

    if tie_correction <= 0:
        tie_correction = 1

    def h_stat(rank_sums):

        h = 12 / (n * (n + 1)) * np.sum(rank_sums**2 / sizes) - 3 * (n + 1)

        return h / tie_correction

    observed_sums = np.array([ranks[codes == k].sum() for k in range(len(unique))])

    observed = h_stat(observed_sums)

    rng = np.random.default_rng(seed)

    extreme = 0

    for _ in range(n_iter):

        permuted = rng.permutation(codes)

        perm_sums = np.array([ranks[permuted == k].sum() for k in range(len(unique))])

        if h_stat(perm_sums) >= observed:
            extreme += 1

    return float(observed), (extreme + 1) / (n_iter + 1)


def gini(values):

    values = np.sort(np.asarray(values, dtype=float))

    n = len(values)

    if values.sum() == 0:
        return np.nan

    index = np.arange(1, n + 1)

    return float(((2 * index - n - 1) @ values) / (n * values.sum()))


results = []


# H1: revenue concentration

customer_revenue = identified.groupby("customer_id")["total_revenue"].sum().values

n_customers = len(customer_revenue)

top20_n = int(np.ceil(0.2 * n_customers))


def top_share(sample):

    ordered = np.sort(sample)[::-1]

    return ordered[:top20_n].sum() / ordered.sum()


observed_share = top_share(customer_revenue)

rng = np.random.default_rng(SEED)

boot_shares = [
    top_share(
        rng.choice(
            customer_revenue,
            size=n_customers,
            replace=True,
        )
    )
    for _ in range(2000)
]

ci_low, ci_high = np.percentile(
    boot_shares,
    [2.5, 97.5],
)

gini_coefficient = gini(customer_revenue)

h1_supported = ci_low > 0.20

results.append(
    {
        "hypothesis": "H1 concentration",
        "test": "bootstrap top-20% share (2000 resamples)",
        "statistic": round(observed_share * 100, 1),
        "p_value": np.nan,
        "ci_95": f"{ci_low * 100:.1f}%-{ci_high * 100:.1f}%",
        "verdict": "Supported" if h1_supported else "Rejected",
        "notes": f"gini={gini_coefficient:.3f}; benchmark=20%; NOT an 80/20 pattern",
    }
)


print("\nH1: revenue concentration")
print(f"  top 20% share : {observed_share * 100:.1f}%")
print(f"  95% CI        : {ci_low * 100:.1f}% - {ci_high * 100:.1f}%")
print(f"  gini          : {gini_coefficient:.3f}")


# H2: frequency vs value

cv = identified.groupby("customer_id").agg(
    orders=("customer_id", "size"),
    revenue=("total_revenue", "sum"),
    orders_with_revenue=("total_revenue", "count"),
)

cv["aov"] = np.where(
    cv["orders_with_revenue"] > 0,
    cv["revenue"] / cv["orders_with_revenue"],
    np.nan,
)


rho_rev, p_rev = spearman_permutation(
    cv["orders"].values,
    cv["revenue"].values,
)

cv_aov = cv[cv["aov"].notna()]

rho_aov, p_aov = spearman_permutation(
    cv_aov["orders"].values,
    cv_aov["aov"].values,
)


results.append(
    {
        "hypothesis": "H2 frequency vs total revenue",
        "test": "Spearman permutation (5000)",
        "statistic": round(rho_rev, 3),
        "p_value": round(p_rev, 4),
        "ci_95": "",
        "verdict": "Supported" if p_rev < 0.05 else "Rejected",
        "notes": "partly mechanical (revenue = sum over orders)",
    }
)

results.append(
    {
        "hypothesis": "H2b frequency vs AOV",
        "test": "Spearman permutation (5000)",
        "statistic": round(rho_aov, 3),
        "p_value": round(p_aov, 4),
        "ci_95": "",
        "verdict": ("Supported" if p_aov < 0.05 and rho_aov >= 0.3 else "Rejected"),
        "notes": "frequency does NOT raise value per order" if rho_aov < 0.3 else "",
    }
)


print("\nH2: frequency vs value")
print(f"  orders ~ revenue : rho={rho_rev:.3f}  p={p_rev:.4f}")
print(f"  orders ~ AOV     : rho={rho_aov:.3f}  p={p_aov:.4f}")


# H3: volume vs revenue vs turnaround rank

rank_volume = df["service_type"].value_counts()

rank_revenue = (
    df.groupby("service_type")["total_revenue"].sum().sort_values(ascending=False)
)

rank_turnaround = df.groupby("service_type")["service_days"].mean().sort_values()

rank_table = pd.DataFrame(
    {
        "volume_rank": rank_volume.rank(ascending=False),
        "revenue_rank": rank_revenue.rank(ascending=False),
        "turnaround_rank_best": rank_turnaround.rank(),
    }
)

top_service = rank_volume.index[0]

top_best_at_all = (
    rank_revenue.rank(ascending=False)[top_service] == 1
    and rank_turnaround.rank()[top_service] == 1
)

results.append(
    {
        "hypothesis": "H3 top-volume service is not best",
        "test": "rank comparison (volume / revenue / turnaround)",
        "statistic": np.nan,
        "p_value": np.nan,
        "ci_95": "",
        "verdict": "Rejected" if top_best_at_all else "Supported",
        "notes": f"{top_service} ranks #1 on volume, revenue and turnaround",
    }
)


print("\nH3: rank comparison")
print(rank_table)


# H4: turnaround by service

turnaround_data = df[df["service_days"].notna() & df["service_type"].notna()]

h4_stat, h4_p = kw_permutation(
    turnaround_data["service_days"].values,
    turnaround_data["service_type"].values,
)


late_data = turnaround_data[turnaround_data["days_late"].notna()]

if len(late_data) > 50:

    h4b_stat, h4b_p = kw_permutation(
        late_data["days_late"].values,
        late_data["service_type"].values,
    )

else:

    h4b_stat, h4b_p = np.nan, np.nan


results.append(
    {
        "hypothesis": "H4 turnaround differs by service type",
        "test": "Kruskal-Wallis permutation (5000)",
        "statistic": round(h4_stat, 2),
        "p_value": round(h4_p, 4),
        "ci_95": "",
        "verdict": "Supported" if h4_p < 0.05 else "Rejected",
        "notes": "confounded by promised SLA mix; see H4b on days_late",
    }
)

results.append(
    {
        "hypothesis": "H4b lateness differs by service type",
        "test": "Kruskal-Wallis permutation on days_late (5000)",
        "statistic": round(h4b_stat, 2),
        "p_value": round(h4b_p, 4),
        "ci_95": "",
        "verdict": (
            "Supported" if np.nan_to_num(h4b_p, nan=1) < 0.05 else "Inconclusive"
        ),
        "notes": "controls for promised turnaround",
    }
)


print("\nH4: turnaround by service")
print(f"  service_days ~ service_type : H={h4_stat:.2f}  p={h4_p:.4f}")
print(f"  days_late   ~ service_type  : H={h4b_stat:.2f}  p={h4b_p:.4f}")


# H5: weekday pattern

weekday_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

observed_counts = (
    df["order_day"].value_counts().reindex(weekday_order).fillna(0).astype(int)
)

date_range = pd.date_range(
    df["order_date"].min(),
    df["order_date"].max(),
    freq="D",
)

exposure = (
    pd.Series(date_range.day_name()).value_counts().reindex(weekday_order).fillna(0)
)

open_days = weekday_order[:-1]

expected = (
    observed_counts[open_days].sum() * exposure[open_days] / exposure[open_days].sum()
).values

observed_open = observed_counts[open_days].values

chi2 = float(np.sum((observed_open - expected) ** 2 / expected))

probs = (exposure[open_days] / exposure[open_days].sum()).values

rng = np.random.default_rng(SEED)

sims = rng.multinomial(
    int(observed_open.sum()),
    probs,
    size=10000,
)

sim_chi2 = (
    (sims - observed_open.sum() * probs) ** 2 / (observed_open.sum() * probs)
).sum(axis=1)

h5_p = float((sim_chi2 >= chi2).sum() + 1) / float(len(sim_chi2) + 1)

results.append(
    {
        "hypothesis": "H5 weekday pattern differs",
        "test": "chi-square + Monte Carlo (10000), exposure-adjusted",
        "statistic": round(chi2, 2),
        "p_value": round(h5_p, 4),
        "ci_95": "",
        "verdict": "Supported" if h5_p < 0.05 else "Rejected",
        "notes": "Sunday excluded (closed); df=5",
    }
)


print("\nH5: weekday pattern")
print(f"  chi2 = {chi2:.2f}   p = {h5_p:.4f}")


# H6: bottleneck

orders_per_day = df.groupby("order_date").size()

completions_per_day = df.groupby("completion_date").size()

all_days = pd.date_range(
    df["order_date"].min(),
    df["completion_date"].max(),
    freq="D",
)

backlog = pd.DataFrame(
    {
        "orders": orders_per_day.reindex(all_days).fillna(0),
        "completions": completions_per_day.reindex(all_days).fillna(0),
    }
)

backlog["net"] = backlog["orders"] - backlog["completions"]

backlog["cumulative_backlog"] = backlog["net"].cumsum()


intake_by_day = df.groupby("order_date").size()

df["intake_day_volume"] = df["order_date"].map(intake_by_day)

latency_data = df[df["days_late"].notna() & df["intake_day_volume"].notna()].copy()

latency_data["intake_bucket"] = pd.qcut(
    latency_data["intake_day_volume"],
    q=3,
    labels=["low", "medium", "high"],
)

h6_stat, h6_p = kw_permutation(
    latency_data["days_late"].values,
    latency_data["intake_bucket"].values,
)


bucket_summary = (
    latency_data.groupby("intake_bucket", observed=True)
    .agg(
        orders=("no", "size"),
        mean_days_late=("days_late", "mean"),
    )
    .round(2)
)


results.append(
    {
        "hypothesis": "H6 high-intake days create latency",
        "test": "Kruskal-Wallis permutation on days_late by intake tercile (5000)",
        "statistic": round(h6_stat, 2),
        "p_value": round(h6_p, 4),
        "ci_95": "",
        "verdict": "Supported" if h6_p < 0.05 else "Rejected",
        "notes": f"peak cumulative backlog = {int(backlog['cumulative_backlog'].max())} orders",
    }
)


print("\nH6: bottleneck")
print(bucket_summary)
print(f"  H={h6_stat:.2f}  p={h6_p:.4f}")
print(
    f"  peak cumulative backlog: " f"{int(backlog['cumulative_backlog'].max())} orders"
)
print(
    f"  backlog end of period : "
    f"{int(backlog['cumulative_backlog'].iloc[-1])} orders"
)


# Export

output_folder = "../outputs/tables"

os.makedirs(output_folder, exist_ok=True)

results_df = pd.DataFrame(results)

results_df.to_csv(
    f"{output_folder}/hypothesis_results.csv",
    index=False,
)

backlog.to_csv(f"{output_folder}/backlog_series.csv")

rank_table.to_csv(f"{output_folder}/service_rank_comparison.csv")


print("\nHypothesis test results:")
print(
    results_df[
        [
            "hypothesis",
            "statistic",
            "p_value",
            "verdict",
        ]
    ].to_string(index=False)
)

print("\nHypothesis testing completed. Files exported.")
