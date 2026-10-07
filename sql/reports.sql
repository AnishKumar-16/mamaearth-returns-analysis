-- =========================================
-- REPORT A: Total orders, revenue and AOV
-- =========================================

SELECT
    COUNT(*) AS total_orders,

    ROUND(
        SUM(
            o.quantity * p.price *
            (1 - COALESCE(o.discount_pct, 0) / 100.0)
        ),
        2
    ) AS total_revenue,

    ROUND(
        AVG(
            o.quantity * p.price *
            (1 - COALESCE(o.discount_pct, 0) / 100.0)
        ),
        2
    ) AS avg_order_value

FROM orders o

JOIN products p
ON o.product_id = p.product_id;


-- =========================================
-- REPORT B: Missing ratings
-- =========================================

SELECT
    COUNT(*) AS total_orders,
    COUNT(rating) AS orders_with_rating,
    COUNT(*) - COUNT(rating) AS missing_rating
FROM orders;


-- =========================================
-- REPORT C: Customer with zero orders
-- =========================================

SELECT
    c.customer_id,
    c.name

FROM customers c

LEFT JOIN orders o
ON c.customer_id = o.customer_id

GROUP BY
    c.customer_id,
    c.name

HAVING COUNT(o.order_id) = 0;


-- =========================================
-- REPORT D: City return rate
-- =========================================

SELECT
    c.city,
    COUNT(*) AS total_orders,
    SUM(o.returned) AS returned_orders,

    ROUND(
        100.0 * SUM(o.returned) / COUNT(*),
        1
    ) AS return_rate_pct

FROM orders o

JOIN customers c
ON o.customer_id = c.customer_id

GROUP BY c.city

HAVING return_rate_pct > 20

ORDER BY return_rate_pct DESC;


-- =========================================
-- REPORT E: Top 5 customers by spending
-- =========================================

SELECT
    c.customer_id,
    c.name,

    ROUND(
        SUM(
            o.quantity * p.price *
            (1 - COALESCE(o.discount_pct, 0) / 100.0)
        ),
        2
    ) AS total_spend

FROM orders o

JOIN products p
ON o.product_id = p.product_id

JOIN customers c
ON o.customer_id = c.customer_id

GROUP BY
    c.customer_id,
    c.name

ORDER BY
    total_spend DESC,
    c.customer_id ASC

LIMIT 5;


-- =========================================
-- REPORT E2: Ranks 3 to 5
-- =========================================

SELECT
    c.customer_id,
    c.name,

    ROUND(
        SUM(
            o.quantity * p.price *
            (1 - COALESCE(o.discount_pct, 0) / 100.0)
        ),
        2
    ) AS total_spend

FROM orders o

JOIN products p
ON o.product_id = p.product_id

JOIN customers c
ON o.customer_id = c.customer_id

GROUP BY
    c.customer_id,
    c.name

ORDER BY
    total_spend DESC,
    c.customer_id ASC

LIMIT 3 OFFSET 2;


-- =========================================
-- REPORT F: Revenue by category
-- =========================================

SELECT
    p.category,

    COUNT(*) AS order_count,

    ROUND(
        SUM(
            o.quantity * p.price *
            (1 - COALESCE(o.discount_pct, 0) / 100.0)
        ),
        2
    ) AS category_revenue

FROM orders o

JOIN products p
ON o.product_id = p.product_id

JOIN customers c
ON o.customer_id = c.customer_id

GROUP BY p.category

ORDER BY category_revenue DESC;


-- =========================================
-- REPORT G: Customers whose names start with A
-- =========================================

SELECT
    customer_id,
    name
FROM customers
WHERE name LIKE 'A%'
ORDER BY customer_id;


-- =========================================
-- REPORT H: Distinct acquisition sources
-- =========================================

SELECT DISTINCT
    acquisition_source
FROM customers
ORDER BY acquisition_source;


-- =========================================
-- REPORT I: Loyalty tier
-- =========================================

ALTER TABLE customers
ADD COLUMN loyalty_tier VARCHAR(10);

UPDATE customers
SET loyalty_tier =
    CASE
        WHEN city_tier = 1 THEN 'Gold'
        ELSE 'Silver'
    END;

SELECT
    loyalty_tier,
    COUNT(*)
FROM customers
GROUP BY loyalty_tier;