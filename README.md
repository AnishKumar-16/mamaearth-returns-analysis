
# Mamaearth E-Commerce Growth Analytics Project

## 1. Project Overview

This project analyses Mamaearth e-commerce order data to
understand revenue performance, product returns and
data quality issues.

The project uses three connected technologies:

1. SQL - Database creation and business reporting
2. Python - Data cleaning, analysis and visualization
3. GenAI - Business narrative generation using Gemini API

## 2. Business Problem

Mamaearth's Growth Analytics team suspects that
product returns are affecting business performance.

The project answers two questions:

- Where are product returns coming from?
- What is the correct revenue picture after cleaning?

## 3. Project Structure

ecommerce-sql-project/
    README.md

    sql/
        schema.sql
        seed_data.sql
        reports.sql

    data/
        customers.csv
        products.csv
        orders.csv

    analysis/
        clean_and_eda.py
        visualize.py

    visualizations/
        return_rate_by_payment.png
        monthly_revenue_trend.png

    narrator/
        findings.json
        generate_narrative.py
        sample_output.txt

## 4. Part 1 - SQL Analysis

SQLite is used to create and analyse the database.

The dataset contains:

- 45 customers
- 16 products
- 180 raw orders

The SQL layer includes database schema creation,
data loading and nine business reports.

Raw SQL revenue: INR 99,860.20

## 5. Part 2 - Python Analysis

Python and pandas are used for data cleaning,
reconciliation and exploratory analysis.

Main cleaning steps:

- Standardize payment method values
- Remove five duplicate orders
- Fill missing discount and rating values
- Merge order, customer and product information
- Detect quantity outliers using IQR
- Analyse payment methods and city tiers
- Calculate monthly revenue trends

Results:

Raw orders: 180
Cleaned orders: 175

Raw revenue: INR 99,860.20
Cleaned revenue: INR 97,358.30

Duplicate reconciliation difference: INR 2,501.90

The two quantity outliers are O0011 and O0098.

## 6. Return Rate Analysis

Return rates by payment method:

- CARD: 14.7%
- UPI: 18.9%
- COD: 44.4%

COD has the highest overall return rate.

The highest-risk segment is COD in Tier 2 cities,
with a return rate of 54.5%.

This indicates that COD returns should be
prioritized for operational investigation.

## 7. Monthly Revenue Analysis

January 2026 apparent revenue: INR 29,582.10

January 2026 corrected revenue: INR 11,637.10

March 2026 corrected revenue: INR 20,318.90

March 2026 is the true peak revenue month
after excluding quantity outliers.

The duplicate-order reconciliation and January
quantity-outlier correction are separate issues.

## 8. Data Visualizations

Two visualizations are generated using Python:

1. return_rate_by_payment.png
   Compares return rates across CARD, COD and UPI.

2. monthly_revenue_trend.png
   Shows the outlier-corrected monthly revenue trend.

Both charts are saved in the visualizations folder.

## 9. Part 3 - GenAI Business Narrative

The Python analysis exports verified findings
automatically to narrator/findings.json.

The generate_narrative.py script reads this JSON
and sends the verified findings to Google's Gemini API.

Model used: gemini-3.6-flash

The narrative follows the SCR framework:

Situation:
Explains cleaned revenue and the true peak month.

Complication:
Explains duplicate orders, quantity outliers,
COD returns and high-risk segments.

Resolution:
Recommends actions for operations and finance.

The script uses:

- Separate system instructions
- Temperature 0.0
- Maximum output tokens 4096
- API timeout of 60 seconds
- Try/except error handling
- Automatic offline fallback

If Gemini is unavailable, the script generates
an offline SCR narrative using verified JSON values.

## 10. Narrative Validation

The script performs five numeric checks:

1. Cleaned revenue
2. COD return rate
3. Tier 2 COD return rate
4. Duplicate reconciliation
5. March peak revenue

It also checks three SCR headings:

- Situation
- Complication
- Resolution

The Gemini-generated narrative passed all eight
checks and was saved to narrator/sample_output.txt.

## 11. How to Run the Project

Open the project folder in VS Code.

Install the required Python packages:

    python -m pip install pandas matplotlib google-genai

Run the Python analysis:

    python analysis/clean_and_eda.py

Generate the charts:

    python analysis/visualize.py

Set the Gemini API key in PowerShell:

    $env:GEMINI_API_KEY = "YOUR_NEW_API_KEY"

Run the GenAI narrative:

    python narrator/generate_narrative.py

If the API key is missing or Gemini is unavailable,
the script automatically uses the offline fallback.

Do not commit real API keys to the repository.

## 12. Business Recommendations

- Investigate high COD return rates.
- Prioritize COD orders in Tier 2 cities.
- Review delivery confirmation and return reasons.
- Encourage prepaid payment options where appropriate.
- Prevent duplicate orders through data validation.
- Flag unusual bulk orders before revenue reporting.
- Use cleaned and outlier-corrected data for decisions.

## 13. Conclusion

The project demonstrates an end-to-end analytics
workflow connecting SQL, Python and Generative AI.

The analysis identifies COD returns as a major
operational concern and shows why data cleaning
is essential for accurate revenue reporting.

The Gemini-powered SCR narrative converts verified
analytical findings into actionable business insights.
