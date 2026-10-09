import os
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# TASK 11 - DATA PREPARATION FOR VISUALIZATIONS
# ============================================================

print("\n" + "=" * 60)
print("TASK 11 - VISUALIZATIONS")
print("=" * 60)


# ------------------------------------------------------------
# LOAD RAW CSV FILES
# ------------------------------------------------------------

orders = pd.read_csv("data/orders.csv")
customers = pd.read_csv("data/customers.csv")
products = pd.read_csv("data/products.csv")

print("\nRaw orders loaded:", orders.shape)


# ------------------------------------------------------------
# STANDARDIZE PAYMENT METHOD
# ------------------------------------------------------------

orders["payment_method"] = (
    orders["payment_method"]
    .str.strip()
    .str.upper()
)


# ------------------------------------------------------------
# REMOVE THE SAME 5 DUPLICATES AS clean_and_eda.py
# ------------------------------------------------------------

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

orders_clean = orders.drop_duplicates(
    subset=duplicate_columns,
    keep="first"
).copy()

print("Orders after duplicate removal:", orders_clean.shape)


# ------------------------------------------------------------
# IMPUTE MISSING VALUES
# ------------------------------------------------------------

orders_clean["discount_pct"] = (
    orders_clean["discount_pct"].fillna(0)
)

rating_median = orders_clean["rating"].median()

orders_clean["rating"] = (
    orders_clean["rating"].fillna(rating_median)
)


# ------------------------------------------------------------
# MERGE ORDERS + PRODUCTS + CUSTOMERS
# ------------------------------------------------------------

merged = orders_clean.merge(
    products,
    on="product_id",
    how="left"
)

merged = merged.merge(
    customers,
    on="customer_id",
    how="left"
)


# ------------------------------------------------------------
# CALCULATE ORDER VALUE
# ------------------------------------------------------------

merged["order_value"] = (
    merged["quantity"]
    * merged["price"]
    * (1 - merged["discount_pct"] / 100)
)


# ============================================================
# IDENTIFY QUANTITY OUTLIERS
# ============================================================

Q1 = merged["quantity"].quantile(0.25)
Q3 = merged["quantity"].quantile(0.75)

IQR = Q3 - Q1

lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

merged["is_outlier"] = (
    (merged["quantity"] < lower)
    | (merged["quantity"] > upper)
)

print(
    "Quantity outliers:",
    merged.loc[
        merged["is_outlier"],
        "order_id"
    ].tolist()
)


# ============================================================
# MAKE SURE VISUALIZATIONS FOLDER EXISTS
# ============================================================

os.makedirs(
    "visualizations",
    exist_ok=True
)


# ============================================================
# VISUALIZATION 1
# RETURN RATE BY PAYMENT METHOD
# ============================================================

print("\nCreating Visualization 1...")


payment_return_rate = (
    merged
    .groupby("payment_method")["returned"]
    .mean()
    .mul(100)
    .sort_values(ascending=False)
)


print("\nReturn rate by payment method:")

for payment, rate in payment_return_rate.items():
    print(f"{payment}: {rate:.1f}%")


# Create chart
fig, ax = plt.subplots(figsize=(8, 5))

bars = ax.bar(
    payment_return_rate.index,
    payment_return_rate.values
)


# Axis labels
ax.set_xlabel("Payment Method")
ax.set_ylabel("Return Rate (%)")


# Finding-focused title
ax.set_title(
    "COD Returns at 44.4% — 3x Card"
)


# Percentage labels on each bar
for bar, value in zip(
    bars,
    payment_return_rate.values
):

    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.7,
        f"{value:.1f}%",
        ha="center",
        va="bottom"
    )


# Give some space above tallest bar
ax.set_ylim(
    0,
    payment_return_rate.max() + 8
)


plt.tight_layout()


# Save PNG
plt.savefig(
    "visualizations/return_rate_by_payment.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


print(
    "\nCreated successfully:"
    "\nvisualizations/return_rate_by_payment.png"
)


# ============================================================
# VISUALIZATION 2
# OUTLIER-CORRECTED MONTHLY REVENUE
# ============================================================

print("\nCreating Visualization 2...")


# Convert order_date into datetime
merged["order_date"] = pd.to_datetime(
    merged["order_date"]
)


# Create year-month
merged["year_month"] = (
    merged["order_date"]
    .dt.to_period("M")
)


# IMPORTANT:
# Exclude Task 6 quantity outliers
monthly_revenue = (
    merged.loc[~merged["is_outlier"]]
    .groupby("year_month")["order_value"]
    .sum()
)


print("\nOutlier-corrected monthly revenue:")

for month, revenue in monthly_revenue.items():
    print(
        f"{month}: {revenue:.2f}"
    )


# Convert month values into strings for plotting
month_labels = (
    monthly_revenue.index.astype(str)
)


# Find peak month
peak_month = monthly_revenue.idxmax()
peak_revenue = monthly_revenue.max()

print(
    f"\nPeak month: {peak_month}"
)

print(
    f"Peak revenue: {peak_revenue:.2f}"
)


# Create line chart
fig, ax = plt.subplots(
    figsize=(10, 6)
)


ax.plot(
    month_labels,
    monthly_revenue.values,
    marker="o",
    linewidth=2
)


# Axis labels
ax.set_xlabel("Month")
ax.set_ylabel("Revenue (INR)")


# Finding-focused title
ax.set_title(
    "Outlier-Corrected Monthly Revenue — March 2026 Is the Peak"
)


# Add revenue value to every point
for month, revenue in zip(
    month_labels,
    monthly_revenue.values
):

    ax.annotate(
        f"{revenue:.2f}",
        (month, revenue),
        textcoords="offset points",
        xytext=(0, 8),
        ha="center"
    )


plt.xticks(rotation=45)

plt.tight_layout()


# Save PNG
plt.savefig(
    "visualizations/monthly_revenue_trend.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


print(
    "\nCreated successfully:"
    "\nvisualizations/monthly_revenue_trend.png"
)


# ============================================================
# FINAL MESSAGE
# ============================================================

print("\n" + "=" * 60)

print(
    "TASK 11 COMPLETED - BOTH VISUALIZATIONS CREATED"
)

print("=" * 60)