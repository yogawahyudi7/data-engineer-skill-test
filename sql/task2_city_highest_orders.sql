-- Task 2: Find city with highest number of orders
-- This query identifies the city with the most orders and provides detailed analysis

WITH city_order_stats AS (
    SELECT 
        c.city,
        COUNT(o.order_id) as total_orders,
        COUNT(DISTINCT c.customer_id) as unique_customers,
        SUM(o.total_amount) as total_revenue,
        AVG(o.total_amount) as avg_order_value,
        MIN(o.order_date) as first_order,
        MAX(o.order_date) as latest_order
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.status != 'cancelled'  -- Exclude cancelled orders
    GROUP BY c.city
),
city_rankings AS (
    SELECT 
        city,
        total_orders,
        unique_customers,
        ROUND(total_revenue, 2) as total_revenue,
        ROUND(avg_order_value, 2) as avg_order_value,
        first_order,
        latest_order,
        -- Calculate orders per customer ratio
        ROUND(total_orders::DECIMAL / unique_customers, 2) as orders_per_customer,
        -- Rank cities by different metrics
        RANK() OVER (ORDER BY total_orders DESC) as orders_rank,
        RANK() OVER (ORDER BY total_revenue DESC) as revenue_rank,
        RANK() OVER (ORDER BY unique_customers DESC) as customers_rank
    FROM city_order_stats
)
SELECT 
    city,
    total_orders,
    unique_customers,
    total_revenue,
    avg_order_value,
    orders_per_customer,
    first_order,
    latest_order,
    orders_rank,
    revenue_rank,
    customers_rank,
    -- Overall performance score (weighted average)
    ROUND(
        (orders_rank * 0.4 + revenue_rank * 0.4 + customers_rank * 0.2), 2
    ) as performance_score
FROM city_rankings
ORDER BY total_orders DESC, total_revenue DESC;

-- Additional query: Top city with highest orders
SELECT 
    city as highest_orders_city,
    total_orders,
    unique_customers,
    total_revenue,
    orders_per_customer
FROM city_rankings
WHERE orders_rank = 1;
