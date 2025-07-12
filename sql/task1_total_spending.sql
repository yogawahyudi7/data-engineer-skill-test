-- Task 1: Calculate total spending by customer
-- This query calculates the total amount spent by each customer
-- including customer details and ranking by spending

WITH customer_spending AS (
    SELECT 
        c.customer_id,
        c.name,
        c.email,
        c.city,
        SUM(o.total_amount) as total_spending,
        COUNT(o.order_id) as total_orders,
        AVG(o.total_amount) as avg_order_value,
        MIN(o.order_date) as first_order_date,
        MAX(o.order_date) as last_order_date
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.status != 'cancelled'  -- Exclude cancelled orders
    GROUP BY c.customer_id, c.name, c.email, c.city
)
SELECT 
    customer_id,
    name,
    email,
    city,
    total_spending,
    total_orders,
    ROUND(avg_order_value, 2) as avg_order_value,
    first_order_date,
    last_order_date,
    -- Calculate days between first and last order
    CASE 
        WHEN total_orders > 1 THEN 
            EXTRACT(DAY FROM (last_order_date - first_order_date))
        ELSE 0 
    END as customer_lifetime_days,
    -- Rank customers by total spending
    RANK() OVER (ORDER BY total_spending DESC) as spending_rank,
    -- Categorize customers by spending level
    CASE 
        WHEN total_spending >= 1000 THEN 'High Value'
        WHEN total_spending >= 500 THEN 'Medium Value'
        WHEN total_spending >= 100 THEN 'Low Value'
        ELSE 'Minimal Value'
    END as customer_segment
FROM customer_spending
WHERE total_spending > 0  -- Only include customers who made purchases
ORDER BY total_spending DESC, total_orders DESC;
