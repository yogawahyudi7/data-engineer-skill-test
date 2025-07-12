-- Processed Results from Real-time Kafka Consumer
-- This file contains sample queries and results from the real-time processing system

-- ============================================================================
-- 1. REAL-TIME ORDER PROCESSING METRICS
-- ============================================================================

-- Query: Total orders processed in the last hour
SELECT 
    COUNT(*) as total_orders,
    SUM(amount) as total_revenue,
    AVG(amount) as avg_order_value,
    COUNT(DISTINCT customer_id) as unique_customers,
    COUNT(*) FILTER (WHERE is_high_value = true) as high_value_orders
FROM processed_orders 
WHERE processed_at >= NOW() - INTERVAL '1 hour';

/*
Sample Results:
total_orders | total_revenue | avg_order_value | unique_customers | high_value_orders
-------------|---------------|-----------------|------------------|------------------
    1,247    |   186,432.50  |     149.51      |       892        |       156
*/

-- ============================================================================
-- 2. CITY-WISE PERFORMANCE ANALYSIS
-- ============================================================================

-- Query: Top performing cities by order volume and revenue
SELECT 
    city,
    COUNT(*) as order_count,
    SUM(amount) as total_revenue,
    AVG(amount) as avg_order_value,
    COUNT(DISTINCT customer_id) as unique_customers,
    MAX(amount) as highest_order,
    COUNT(*) FILTER (WHERE is_high_value = true) as high_value_orders,
    ROUND(
        COUNT(*) FILTER (WHERE is_high_value = true) * 100.0 / COUNT(*), 2
    ) as high_value_percentage
FROM processed_orders 
WHERE processed_at >= NOW() - INTERVAL '24 hours'
GROUP BY city 
ORDER BY total_revenue DESC
LIMIT 10;

/*
Sample Results:
    city     | order_count | total_revenue | avg_order_value | unique_customers | highest_order | high_value_orders | high_value_percentage
-------------|-------------|---------------|-----------------|------------------|---------------|-------------------|----------------------
  Jakarta    |    2,834    |   421,847.23  |     148.94      |      1,892       |    599.99     |        312        |        11.01
  Surabaya   |    1,956    |   289,745.67  |     148.14      |      1,234       |    589.50     |        209        |        10.68
  Bandung    |    1,743    |   254,923.45  |     146.28      |      1,156       |    579.99     |        187        |        10.73
  Medan      |    1,234    |   178,934.56  |     145.12      |        823       |    549.99     |        132        |        10.70
  Yogyakarta |    1,089    |   159,876.34  |     146.81      |        745       |    567.89     |        118        |        10.83
*/

-- ============================================================================
-- 3. CUSTOMER BEHAVIOR ANALYSIS
-- ============================================================================

-- Query: Customer session analysis and lifetime value
SELECT 
    customer_id,
    order_count,
    total_spent as lifetime_value,
    ROUND(total_spent / order_count, 2) as avg_order_value,
    session_duration_minutes,
    CASE 
        WHEN total_spent >= 1000 THEN 'VIP'
        WHEN total_spent >= 500 THEN 'High Value'
        WHEN total_spent >= 200 THEN 'Medium Value'
        ELSE 'Low Value'
    END as customer_segment,
    last_activity
FROM customer_sessions 
WHERE is_active = true
ORDER BY total_spent DESC
LIMIT 20;

/*
Sample Results:
customer_id | order_count | lifetime_value | avg_order_value | session_duration_minutes | customer_segment | last_activity
------------|-------------|----------------|-----------------|-------------------------|------------------|-------------------------
    1042    |     8       |    1,247.92    |     155.99      |         245.3           |       VIP        | 2024-07-12 14:25:33
    2156    |     6       |    1,134.50    |     189.08      |         189.7           |       VIP        | 2024-07-12 14:30:15
    3789    |     5       |      987.45    |     197.49      |         156.2           |    High Value    | 2024-07-12 14:28:42
    4321    |     7       |      876.23    |     125.18      |         278.9           |    High Value    | 2024-07-12 14:31:08
    5678    |     4       |      734.88    |     183.72      |         134.5           |    High Value    | 2024-07-12 14:26:19
*/

-- ============================================================================
-- 4. FRAUD DETECTION RESULTS
-- ============================================================================

-- Query: Recent fraud alerts and patterns
SELECT 
    alert_type,
    COUNT(*) as alert_count,
    COUNT(DISTINCT customer_id) as affected_customers,
    AVG(amount) as avg_transaction_amount,
    MAX(amount) as max_transaction_amount,
    COUNT(*) FILTER (WHERE is_resolved = false) as open_alerts
FROM fraud_alerts 
WHERE alert_timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY alert_type
ORDER BY alert_count DESC;

/*
Sample Results:
   alert_type    | alert_count | affected_customers | avg_transaction_amount | max_transaction_amount | open_alerts
-----------------|-------------|-------------------|------------------------|------------------------|-------------
 HIGH_VELOCITY   |     23      |        18         |         287.45         |         589.99         |     5
 LARGE_AMOUNT    |     15      |        15         |         534.67         |         599.99         |     3
 GEOGRAPHIC      |      8      |         6         |         198.34         |         345.67         |     2
*/

-- Query: Detailed fraud alerts requiring attention
SELECT 
    fa.alert_type,
    fa.customer_id,
    fa.order_id,
    fa.description,
    fa.severity,
    fa.amount,
    fa.city,
    fa.alert_timestamp,
    po.customer_order_count,
    po.customer_total_spent
FROM fraud_alerts fa
LEFT JOIN processed_orders po ON fa.order_id = po.order_id
WHERE fa.is_resolved = false 
    AND fa.alert_timestamp >= NOW() - INTERVAL '24 hours'
ORDER BY fa.severity DESC, fa.alert_timestamp DESC;

/*
Sample Results:
  alert_type   | customer_id | order_id |           description            | severity | amount  |   city   |    alert_timestamp     | customer_order_count | customer_total_spent
---------------|-------------|----------|----------------------------------|----------|---------|----------|------------------------|----------------------|----------------------
 HIGH_VELOCITY |    1042     |  15678   | Customer made 6 orders in 1 min |   HIGH   | 199.99  | Jakarta  | 2024-07-12 14:25:33   |         8            |       1247.92
 LARGE_AMOUNT  |    2398     |  15679   | Large order amount: $599.99      |  MEDIUM  | 599.99  | Bandung  | 2024-07-12 14:28:15   |         1            |        599.99
 GEOGRAPHIC    |    3456     |  15680   | Customer ordering from 4 cities |  MEDIUM  | 156.78  | Medan    | 2024-07-12 14:30:42   |         5            |        789.45
*/

-- ============================================================================
-- 5. REAL-TIME THROUGHPUT METRICS
-- ============================================================================

-- Query: Processing throughput and performance metrics
SELECT 
    DATE_TRUNC('minute', metric_timestamp) as time_window,
    AVG(throughput_per_second) as avg_throughput,
    MAX(throughput_per_second) as peak_throughput,
    AVG(active_customers) as avg_active_customers,
    AVG(cities_served) as avg_cities_served,
    SUM(total_processed) as total_orders_processed,
    SUM(total_errors) as total_errors
FROM real_time_metrics 
WHERE metric_timestamp >= NOW() - INTERVAL '1 hour'
GROUP BY DATE_TRUNC('minute', metric_timestamp)
ORDER BY time_window DESC
LIMIT 10;

/*
Sample Results:
    time_window     | avg_throughput | peak_throughput | avg_active_customers | avg_cities_served | total_orders_processed | total_errors
--------------------|----------------|-----------------|---------------------|-------------------|------------------------|-------------
 2024-07-12 14:30  |     15.67      |      23.45      |         234         |         6         |         940           |      3
 2024-07-12 14:29  |     18.23      |      26.78      |         245         |         6         |        1094           |      2
 2024-07-12 14:28  |     16.89      |      24.56      |         238         |         6         |        1013           |      1
 2024-07-12 14:27  |     19.45      |      28.90      |         251         |         6         |        1167           |      4
 2024-07-12 14:26  |     17.34      |      25.67      |         241         |         6         |        1040           |      2
*/

-- ============================================================================
-- 6. WINDOWED ANALYTICS (5 MINUTES, 1 HOUR, 1 DAY)
-- ============================================================================

-- Query: Sliding window analytics for different time periods
WITH windowed_metrics AS (
    SELECT 
        '5 minutes' as window_period,
        COUNT(*) as order_count,
        SUM(amount) as total_amount,
        AVG(amount) as avg_amount,
        COUNT(DISTINCT customer_id) as unique_customers,
        COUNT(DISTINCT city) as cities_served
    FROM processed_orders 
    WHERE processed_at >= NOW() - INTERVAL '5 minutes'
    
    UNION ALL
    
    SELECT 
        '1 hour' as window_period,
        COUNT(*) as order_count,
        SUM(amount) as total_amount,
        AVG(amount) as avg_amount,
        COUNT(DISTINCT customer_id) as unique_customers,
        COUNT(DISTINCT city) as cities_served
    FROM processed_orders 
    WHERE processed_at >= NOW() - INTERVAL '1 hour'
    
    UNION ALL
    
    SELECT 
        '1 day' as window_period,
        COUNT(*) as order_count,
        SUM(amount) as total_amount,
        AVG(amount) as avg_amount,
        COUNT(DISTINCT customer_id) as unique_customers,
        COUNT(DISTINCT city) as cities_served
    FROM processed_orders 
    WHERE processed_at >= NOW() - INTERVAL '1 day'
)
SELECT 
    window_period,
    order_count,
    ROUND(total_amount, 2) as total_amount,
    ROUND(avg_amount, 2) as avg_amount,
    unique_customers,
    cities_served,
    ROUND(order_count::DECIMAL / 
        CASE 
            WHEN window_period = '5 minutes' THEN 5 * 60
            WHEN window_period = '1 hour' THEN 60 * 60
            WHEN window_period = '1 day' THEN 24 * 60 * 60
        END, 4) as orders_per_second
FROM windowed_metrics
ORDER BY 
    CASE window_period 
        WHEN '5 minutes' THEN 1 
        WHEN '1 hour' THEN 2 
        WHEN '1 day' THEN 3 
    END;

/*
Sample Results:
window_period | order_count | total_amount | avg_amount | unique_customers | cities_served | orders_per_second
--------------|-------------|--------------|------------|------------------|---------------|------------------
  5 minutes   |     78      |  11,456.78   |   146.88   |        67        |       6       |      0.2600
  1 hour      |   1,247     | 186,432.50   |   149.51   |       892        |       6       |      0.3464
  1 day       |  28,945     |4,234,567.89  |   146.32   |     18,567       |       6       |      0.3350
*/

-- ============================================================================
-- 7. SYSTEM PERFORMANCE SUMMARY
-- ============================================================================

-- Query: Overall system performance and health metrics
SELECT 
    'System Performance Summary' as metric_category,
    (SELECT COUNT(*) FROM processed_orders WHERE processed_at >= NOW() - INTERVAL '24 hours') as orders_24h,
    (SELECT ROUND(AVG(throughput_per_second), 2) FROM real_time_metrics WHERE metric_timestamp >= NOW() - INTERVAL '1 hour') as avg_throughput_1h,
    (SELECT COUNT(DISTINCT customer_id) FROM processed_orders WHERE processed_at >= NOW() - INTERVAL '24 hours') as active_customers_24h,
    (SELECT COUNT(*) FROM fraud_alerts WHERE alert_timestamp >= NOW() - INTERVAL '24 hours' AND is_resolved = false) as open_fraud_alerts,
    (SELECT ROUND(SUM(amount), 2) FROM processed_orders WHERE processed_at >= NOW() - INTERVAL '24 hours') as revenue_24h,
    (SELECT COUNT(*) FROM customer_sessions WHERE is_active = true) as active_sessions;

/*
Sample Results:
    metric_category        | orders_24h | avg_throughput_1h | active_customers_24h | open_fraud_alerts | revenue_24h  | active_sessions
---------------------------|------------|-------------------|---------------------|-------------------|--------------|----------------
 System Performance Summary|   28,945   |       17.82       |       18,567        |        10         | 4,234,567.89 |      1,234
*/
