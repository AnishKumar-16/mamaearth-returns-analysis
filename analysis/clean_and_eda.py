import pandas as pd


# ============================================================
# PART 2 - PYTHON/PANDAS DATA WRANGLING & EDA
# ============================================================


# ============================================================
# TASK 1 - LOAD AND INSPECT DATA
# ============================================================

print("\n" + "=" * 60)
print("TASK 1 - LOAD AND INSPECT")
print("=" * 60)

orders = pd.read_csv("data/orders.csv")
customers = pd.read_csv("data/customers.csv")
products = pd.read_csv("data/products.csv")

print("Orders shape before cleaning:", orders.shape)
print("Customers shape:", customers.shape)
print("Products shape:", products.shape)

print("\nFirst 5 orders:")
print(orders.head())

print("\nMissing values in orders:")
print(orders.isnull().sum())


# ============================================================
# TASK 2 - STANDARDIZE PAYMENT METHOD
# ============================================================

print("\n" + "=" * 60)
print("TASK 2 - STANDARDIZE PAYMENT METHOD")
print("=" * 60)

# Show payment methods before cleaning
raw_payment_methods = orders["payment_method"].unique()

print("Payment methods before cleaning:")
print(raw_payment_methods)

print("Number of raw payment methods:", len(raw_payment_methods))

# Standardize payment method
orders["payment_method"] = (
    orders["payment_method"]
    .str.strip()
    .str.upper()
)

print("\nPayment methods after cleaning:")
print(orders["payment_method"].unique())

print("\nPayment method counts:")
print(orders["payment_method"].value_counts())

print(
    "Number of payment methods after cleaning:",
    orders["payment_method"].nunique()
)


# ============================================================
# TASK 3 - REMOVE DUPLICATE ORDERS
# ============================================================

print("\n" + "=" * 60)
print("TASK 3 - REMOVE DUPLICATE ORDERS")
print("=" * 60)

# Natural key excludes order_id because duplicated orders
# intentionally have different order IDs.
duplicate_columns = [
    "customer_id",
    "product_id",
    "order_date",
    "quantity",
    "discount_pct",
    "payment_method",
    "rating",
    "returned"
]

duplicate_mask = orders.duplicated(
    subset=duplicate_columns,
    keep="first"
)

duplicate_orders = orders.loc[duplicate_mask].copy()

print("Number of duplicate orders:", duplicate_mask.sum())

print("\nDropped order IDs:")
print(duplicate_orders["order_id"].tolist())

# Keep only first occurrence
orders_clean = orders.loc[~duplicate_mask].copy()

print("\nShape after removing duplicates:")
print(orders_clean.shape)


# ============================================================
# TASK 4 - IMPUTE MISSING VALUES
# ============================================================

print("\n" + "=" * 60)
print("TASK 4 - IMPUTE MISSING VALUES")
print("=" * 60)

# Count missing discounts before filling
missing_discount = orders_clean["discount_pct"].isna().sum()

print("Missing discount_pct before imputation:")
print(missing_discount)

# Business rule:
# Missing discount means no promotional discount was applied.
orders_clean["discount_pct"] = (
    orders_clean["discount_pct"].fillna(0)
)

# Count missing ratings
missing_rating = orders_clean["rating"].isna().sum()

print("\nMissing ratings before imputation:")
print(missing_rating)

# Calculate median BEFORE filling missing ratings
rating_median = orders_clean["rating"].median()

print("Rating median before imputation:")
print(rating_median)

# Fill missing ratings with median
orders_clean["rating"] = (
    orders_clean["rating"].fillna(rating_median)
)

print("\nMissing values after imputation:")
print(
    orders_clean[
        ["discount_pct", "rating"]
    ].isnull().sum()
)


# ============================================================
# TASK 5 - MERGE AND RECONCILE
# ============================================================

print("\n" + "=" * 60)
print("TASK 5 - MERGE AND RECONCILE")
print("=" * 60)

# Merge orders with products
merged = orders_clean.merge(
    products,
    on="product_id",
    how="left"
)

# Merge with customers
merged = merged.merge(
    customers,
    on="customer_id",
    how="left"
)

# Calculate cleaned order value
merged["order_value"] = (
    merged["quantity"]
    * merged["price"]
    * (1 - merged["discount_pct"] / 100)
)

clean_revenue = merged["order_value"].sum()

print(f"Cleaned total revenue: {clean_revenue:.2f}")


# ------------------------------------------------------------
# Independently calculate value of the 5 removed duplicates
# ------------------------------------------------------------

duplicate_check = duplicate_orders.merge(
    products,
    on="product_id",
    how="left"
)

# Missing discounts mean 0% discount
duplicate_check["discount_pct"] = (
    duplicate_check["discount_pct"].fillna(0)
)

duplicate_check["order_value"] = (
    duplicate_check["quantity"]
    * duplicate_check["price"]
    * (1 - duplicate_check["discount_pct"] / 100)
)

duplicate_value = duplicate_check["order_value"].sum()

print(f"Value of 5 duplicate orders: {duplicate_value:.2f}")

raw_sql_revenue = 99860.20
difference = raw_sql_revenue - clean_revenue

print(f"Part 1 raw SQL revenue: {raw_sql_revenue:.2f}")
print(f"Difference after duplicate removal: {difference:.2f}")

print(
    "\nReconciliation Note: "
    f"Part 1 reported raw revenue of Rs {raw_sql_revenue:.2f}, "
    f"while the cleaned 175-order dataset reports Rs {clean_revenue:.2f}. "
    f"The exact difference is Rs {difference:.2f}. "
    f"This difference is caused by the 5 duplicate orders removed in Task 3, "
    f"whose combined order value is Rs {duplicate_value:.2f}. "
    "Discount and rating imputation does not cause this revenue difference: "
    "missing discounts are treated as 0% in both calculations, and rating "
    "is not used in the order_value formula."
)


# ============================================================
# TASK 6 - IQR OUTLIER DETECTION
# ============================================================

print("\n" + "=" * 60)
print("TASK 6 - IQR OUTLIER DETECTION")
print("=" * 60)

Q1 = merged["quantity"].quantile(0.25)
Q3 = merged["quantity"].quantile(0.75)

IQR = Q3 - Q1

lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

print("Q1:", Q1)
print("Q3:", Q3)
print("IQR:", IQR)
print("Lower bound:", lower)
print("Upper bound:", upper)

# Flag rather than delete the outliers
merged["is_outlier"] = (
    (merged["quantity"] < lower)
    | (merged["quantity"] > upper)
)

outliers = merged.loc[
    merged["is_outlier"],
    ["order_id", "quantity"]
]

print("\nNumber of quantity outliers:")
print(merged["is_outlier"].sum())

print("\nOutlier orders:")
print(outliers.to_string(index=False))


# ============================================================
# TASK 7 - HYPOTHESIS TEST
# ============================================================

print("\n" + "=" * 60)
print("TASK 7 - COD RETURN RATE HYPOTHESIS")
print("=" * 60)

print(
    "Hypothesis: COD orders have a higher return rate "
    "than CARD and UPI orders."
)

payment_returns = (
    merged
    .groupby("payment_method")["returned"]
    .agg(["count", "mean"])
)

payment_returns["return_rate_pct"] = (
    payment_returns["mean"] * 100
).round(1)

print("\nReturn rate by payment method:")
print(payment_returns)

print(
    "\nConclusion: Confirmed - COD has the highest return rate "
    "at 44.4%, compared with CARD at 14.7% and UPI at 18.9%."
)


# ============================================================
# TASK 8 - MULTI-LEVEL SEGMENTATION
# ============================================================

print("\n" + "=" * 60)
print("TASK 8 - PAYMENT METHOD + CITY TIER SEGMENTATION")
print("=" * 60)

segment = (
    merged
    .groupby(["payment_method", "city_tier"])["returned"]
    .agg(["count", "mean"])
    .reset_index()
)

segment["return_rate_pct"] = (
    segment["mean"] * 100
).round(1)

print("\nReturn rates by payment method and city tier:")
print(
    segment[
        [
            "payment_method",
            "city_tier",
            "count",
            "return_rate_pct"
        ]
    ].to_string(index=False)
)

highest_risk = segment.loc[
    segment["return_rate_pct"].idxmax()
]

print(
    "\nHighest-risk segment: "
    f"{highest_risk['payment_method']} + Tier-"
    f"{int(highest_risk['city_tier'])} cities at "
    f"{highest_risk['return_rate_pct']:.1f}%."
)

print(
    "COD risk is not uniform across city tiers: "
    "Tier-1 has 32 COD orders with a 37.5% return rate, "
    "while Tier-2 has 22 COD orders with a 54.5% return rate."
)


# ============================================================
# TASK 9 - CORRELATION ANALYSIS
# ============================================================

print("\n" + "=" * 60)
print("TASK 9 - CORRELATION ANALYSIS")
print("=" * 60)

correlation_columns = [
    "rating",
    "returned",
    "discount_pct",
    "quantity"
]

correlation_matrix = merged[
    correlation_columns
].corr()

print("\nCorrelation matrix:")
print(correlation_matrix.round(3))


# Function to classify correlation strength
def correlation_strength(value):
    absolute_value = abs(value)

    if absolute_value < 0.20:
        return "negligible"
    elif absolute_value < 0.40:
        return "weak"
    elif absolute_value < 0.70:
        return "moderate"
    else:
        return "strong"


print("\nPairwise correlation strength:")

for i in range(len(correlation_columns)):
    for j in range(i + 1, len(correlation_columns)):

        col1 = correlation_columns[i]
        col2 = correlation_columns[j]

        value = correlation_matrix.loc[col1, col2]

        strength = correlation_strength(value)

        print(
            f"{col1} vs {col2}: "
            f"r = {value:.3f} -> {strength}"
        )


discount_return_corr = correlation_matrix.loc[
    "discount_pct",
    "returned"
]

print(
    "\nHypothesis: Higher discounts reduce returns."
)

print(
    f"discount_pct vs returned correlation = "
    f"{discount_return_corr:.2f}"
)

print(
    "Conclusion: Busted - the correlation is negligible, "
    "so the data does not show a meaningful relationship "
    "between higher discounts and lower returns."
)


# ============================================================
# TASK 10 - OUTLIER-CORRECTED TIME SERIES
# ============================================================

print("\n" + "=" * 60)
print("TASK 10 - MONTHLY REVENUE")
print("=" * 60)

# Convert order date to datetime
merged["order_date"] = pd.to_datetime(
    merged["order_date"]
)

# Extract year-month
merged["year_month"] = (
    merged["order_date"]
    .dt.to_period("M")
)


# Revenue INCLUDING outliers
monthly_with_outliers = (
    merged
    .groupby("year_month")["order_value"]
    .sum()
)

print("\nMonthly revenue INCLUDING quantity outliers:")

for month, revenue in monthly_with_outliers.items():
    print(f"{month}: {revenue:.2f}")


# Revenue EXCLUDING outliers
monthly_without_outliers = (
    merged.loc[~merged["is_outlier"]]
    .groupby("year_month")["order_value"]
    .sum()
)

print("\nMonthly revenue EXCLUDING quantity outliers:")

for month, revenue in monthly_without_outliers.items():
    print(f"{month}: {revenue:.2f}")


highest_month = monthly_without_outliers.idxmax()
highest_revenue = monthly_without_outliers.max()

print(
    "\nTime-Series Finding: January's apparent revenue lead is "
    "an artifact of the two bulk quantity orders: "
    "O0011 on 2026-01-28 (quantity 25) and "
    "O0098 on 2026-01-10 (quantity 30). "
    f"After excluding these two flagged outliers, {highest_month} "
    f"is the genuine peak month with revenue of "
    f"Rs {highest_revenue:.2f}. Therefore, March is the true "
    "highest-revenue month after outlier correction."
)


print("\n" + "=" * 60)
print("PART 2 TASKS 1-10 COMPLETED")
print("=" * 60)


# ============================================================
# PART 3 - TASK 1: EXPORT VERIFIED FINDINGS TO JSON
# ============================================================

import json
from pathlib import Path

print("\n" + "=" * 60)
print("PART 3 - EXPORT FINDINGS TO JSON")
print("=" * 60)

# STEP 1: Set project paths
project_folder = Path(__file__).resolve().parent.parent

data_folder = project_folder / "data"
narrator_folder = project_folder / "narrator"

# Create narrator folder if it does not exist
narrator_folder.mkdir(exist_ok=True)


# STEP 2: Load original CSV files
raw_orders = pd.read_csv(data_folder / "orders.csv")
raw_products = pd.read_csv(data_folder / "products.csv")
raw_customers = pd.read_csv(data_folder / "customers.csv")

print("\nOriginal orders:", len(raw_orders))


# STEP 3: Standardize payment methods
raw_orders["payment_method"] = (
    raw_orders["payment_method"]
    .str.strip()
    .str.upper()
)


# STEP 4: Remove duplicate orders
duplicate_columns = [
    "customer_id",
    "product_id",
    "order_date",
    "quantity",
    "discount_pct",
    "payment_method",
    "rating",
    "returned"
]

clean_orders = raw_orders.drop_duplicates(
    subset=duplicate_columns,
    keep="first"
).copy()

print("Orders after cleaning:", len(clean_orders))


# STEP 5: Fill missing values
raw_orders["discount_pct"] = (
    raw_orders["discount_pct"].fillna(0)
)

clean_orders["discount_pct"] = (
    clean_orders["discount_pct"].fillna(0)
)

clean_orders["rating"] = (
    clean_orders["rating"].fillna(
        clean_orders["rating"].median()
    )
)


# STEP 6: Calculate raw revenue
raw_data = raw_orders.merge(
    raw_products[["product_id", "price"]],
    on="product_id",
    how="left"
)

raw_data["order_value"] = (
    raw_data["quantity"]
    * raw_data["price"]
    * (1 - raw_data["discount_pct"] / 100)
)

raw_revenue = round(
    float(raw_data["order_value"].sum()), 2
)


# STEP 7: Calculate cleaned revenue
clean_data = clean_orders.merge(
    raw_products[["product_id", "price"]],
    on="product_id",
    how="left"
)

clean_data = clean_data.merge(
    raw_customers[["customer_id", "city_tier"]],
    on="customer_id",
    how="left"
)

clean_data["order_value"] = (
    clean_data["quantity"]
    * clean_data["price"]
    * (1 - clean_data["discount_pct"] / 100)
)

clean_revenue = round(
    float(clean_data["order_value"].sum()), 2
)

revenue_difference = round(
    raw_revenue - clean_revenue, 2
)


# STEP 8: Calculate payment return rates
payment_rates = (
    clean_data.groupby("payment_method")["returned"]
    .mean()
    .mul(100)
    .round(1)
    .to_dict()
)


# STEP 9: Identify highest-risk segment
segment_rates = (
    clean_data.groupby(
        ["payment_method", "city_tier"]
    )["returned"]
    .mean()
    .mul(100)
    .reset_index(name="return_rate_pct")
)

highest_segment = (
    segment_rates.sort_values(
        "return_rate_pct",
        ascending=False
    ).iloc[0]
)


# STEP 10: Identify quantity outliers
q1 = clean_data["quantity"].quantile(0.25)
q3 = clean_data["quantity"].quantile(0.75)

iqr = q3 - q1

lower_limit = q1 - 1.5 * iqr
upper_limit = q3 + 1.5 * iqr

outlier_mask = (
    (clean_data["quantity"] < lower_limit)
    | (clean_data["quantity"] > upper_limit)
)


# STEP 11: Calculate monthly revenue
clean_data["month"] = pd.to_datetime(
    clean_data["order_date"]
).dt.strftime("%Y-%m")

monthly_with_outliers = (
    clean_data.groupby("month")["order_value"]
    .sum()
)

monthly_without_outliers = (
    clean_data.loc[~outlier_mask]
    .groupby("month")["order_value"]
    .sum()
)


# STEP 12: Find true peak and inflated month
true_peak_month = monthly_without_outliers.idxmax()

inflated_month = monthly_with_outliers.idxmax()


# STEP 13: Prepare findings JSON
findings = {
    "cleaned_total_revenue_inr": clean_revenue,

    "raw_total_revenue_inr": raw_revenue,

    "duplicate_reconciliation_delta_inr": revenue_difference,

    "return_rate_by_payment": {
        key: float(value)
        for key, value in payment_rates.items()
    },

    "highest_risk_segment": {
        "payment_method": str(
            highest_segment["payment_method"]
        ),
        "city_tier": int(
            highest_segment["city_tier"]
        ),
        "return_rate_pct": round(
            float(highest_segment["return_rate_pct"]), 1
        )
    },

    "true_peak_month": {
        "month": str(true_peak_month),
        "revenue_inr": round(
            float(
                monthly_without_outliers[true_peak_month]
            ), 2
        )
    },

    "outlier_inflated_month": {
        "month": str(inflated_month),
        "apparent_revenue_inr": round(
            float(
                monthly_with_outliers[inflated_month]
            ), 2
        ),
        "corrected_revenue_inr": round(
            float(
                monthly_without_outliers[inflated_month]
            ), 2
        )
    }
}


# STEP 14: Save findings to JSON
output_path = narrator_folder / "findings.json"

with open(output_path, "w", encoding="utf-8") as file:
    json.dump(findings, file, indent=4)


# STEP 15: Print the results
print("\n" + "=" * 60)
print("PART 3 - FINDINGS EXPORTED SUCCESSFULLY")
print("=" * 60)

print(json.dumps(findings, indent=4))

print("\nJSON file saved to:")
print(output_path)
