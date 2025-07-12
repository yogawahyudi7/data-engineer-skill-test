-- Task 3: Query Optimization Examples
-- This file demonstrates various SQL optimization techniques

-- ============================================================================
-- EXAMPLE 1: Index Usage and WHERE Clause Optimization
-- ============================================================================

-- BEFORE: Inefficient query without proper indexing consideration
-- SELECT * FROM orders WHERE YEAR(order_date) = 2024 AND status = 'completed';

-- AFTER: Optimized query with proper date range and index-friendly conditions
SELECT 
    order_id, 
    customer_id, 
    order_date, 
    total_amount, 
    status
FROM orders 
WHERE order_date >= '2024-01-01' 
    AND order_date < '2025-01-01' 
    AND status = 'completed';

-- Recommended indexes:
-- CREATE INDEX idx_orders_date_status ON orders(order_date, status);
-- CREATE INDEX idx_orders_status_date ON orders(status, order_date);

-- ============================================================================
-- EXAMPLE 2: JOIN Optimization and Subquery Elimination
-- ============================================================================

-- BEFORE: Inefficient correlated subquery
/*
SELECT c.customer_id, c.name,
    (SELECT COUNT(*) FROM orders o WHERE o.customer_id = c.customer_id) as order_count,
    (SELECT SUM(total_amount) FROM orders o WHERE o.customer_id = c.customer_id) as total_spent
FROM customers c;
*/

-- AFTER: Optimized with single JOIN
SELECT 
    c.customer_id, 
    c.name,
    COALESCE(COUNT(o.order_id), 0) as order_count,
    COALESCE(SUM(o.total_amount), 0) as total_spent
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name;

-- ============================================================================
-- EXAMPLE 3: Pagination Optimization for Large Result Sets
-- ============================================================================

-- BEFORE: Inefficient OFFSET for large datasets
-- SELECT * FROM orders ORDER BY order_date DESC OFFSET 10000 LIMIT 20;

-- AFTER: Cursor-based pagination using indexed column
SELECT 
    order_id, 
    customer_id, 
    order_date, 
    total_amount
FROM orders 
WHERE order_date < '2024-06-01 00:00:00'  -- Use last seen date as cursor
ORDER BY order_date DESC, order_id DESC
LIMIT 20;

-- ============================================================================
-- EXAMPLE 4: Aggregation Optimization with Materialized Views
-- ============================================================================

-- Create materialized view for frequently accessed aggregations
-- This is particularly useful for dashboard queries that don't need real-time data

CREATE MATERIALIZED VIEW mv_daily_sales_summary AS
SELECT 
    DATE(order_date) as sales_date,
    COUNT(*) as total_orders,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_order_value,
    COUNT(DISTINCT customer_id) as unique_customers
FROM orders 
WHERE status = 'completed'
GROUP BY DATE(order_date);

-- Refresh strategy (run daily)
-- REFRESH MATERIALIZED VIEW mv_daily_sales_summary;

-- Query using materialized view
SELECT * FROM mv_daily_sales_summary 
WHERE sales_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY sales_date DESC;

-- ============================================================================
-- EXAMPLE 5: Window Function Optimization
-- ============================================================================

-- BEFORE: Multiple passes through the data
/*
SELECT 
    customer_id,
    order_date,
    total_amount,
    (SELECT AVG(total_amount) FROM orders o2 WHERE o2.customer_id = o1.customer_id) as customer_avg
FROM orders o1;
*/

-- AFTER: Single pass with window function
SELECT 
    customer_id,
    order_date,
    total_amount,
    AVG(total_amount) OVER (PARTITION BY customer_id) as customer_avg,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) as order_rank,
    LAG(total_amount) OVER (PARTITION BY customer_id ORDER BY order_date) as previous_order_amount
FROM orders
ORDER BY customer_id, order_date DESC;

-- ============================================================================
-- EXAMPLE 6: EXISTS vs IN Optimization
-- ============================================================================

-- BEFORE: Using IN with subquery (can be slow with NULLs)
-- SELECT * FROM customers WHERE customer_id IN (SELECT customer_id FROM orders WHERE total_amount > 500);

-- AFTER: Using EXISTS (more efficient and NULL-safe)
SELECT c.*
FROM customers c
WHERE EXISTS (
    SELECT 1 
    FROM orders o 
    WHERE o.customer_id = c.customer_id 
        AND o.total_amount > 500
);

-- ============================================================================
-- RECOMMENDED INDEXES for optimization
-- ============================================================================

-- Primary indexes for frequent lookups
-- CREATE INDEX idx_orders_customer_id ON orders(customer_id);
-- CREATE INDEX idx_orders_date ON orders(order_date);
-- CREATE INDEX idx_orders_status ON orders(status);

-- Composite indexes for complex queries
-- CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date);
-- CREATE INDEX idx_orders_status_date_amount ON orders(status, order_date, total_amount);

-- Covering indexes to avoid table lookups
-- CREATE INDEX idx_orders_covering ON orders(customer_id, order_date) INCLUDE (total_amount, status);

-- ============================================================================
-- QUERY PERFORMANCE MONITORING
-- ============================================================================

-- Enable query performance monitoring (PostgreSQL example)
-- EXPLAIN (ANALYZE, BUFFERS) SELECT ...;

-- Sample performance analysis query
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT 
    c.name,
    COUNT(o.order_id) as order_count,
    SUM(o.total_amount) as total_spent
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE c.city = 'Jakarta'
    AND o.order_date >= '2024-01-01'
GROUP BY c.customer_id, c.name
ORDER BY total_spent DESC;
