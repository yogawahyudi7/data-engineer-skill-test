-- Database initialization script for analytics database
-- This script creates the necessary tables for storing processed real-time data

-- Create database (if running manually)
-- CREATE DATABASE analytics;

-- Connect to analytics database
\c analytics;

-- Create extension for UUID generation (if needed)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create processed_orders table
CREATE TABLE IF NOT EXISTS processed_orders (
    id SERIAL PRIMARY KEY,
    order_id INTEGER UNIQUE NOT NULL,
    customer_id INTEGER NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    city VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    processed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    customer_order_count INTEGER DEFAULT 1,
    customer_total_spent DECIMAL(10,2) NOT NULL,
    city_avg_amount DECIMAL(10,2),
    is_high_value BOOLEAN DEFAULT FALSE,
    session_duration_minutes DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_processed_orders_customer_id ON processed_orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_processed_orders_city ON processed_orders(city);
CREATE INDEX IF NOT EXISTS idx_processed_orders_timestamp ON processed_orders(timestamp);
CREATE INDEX IF NOT EXISTS idx_processed_orders_processed_at ON processed_orders(processed_at);
CREATE INDEX IF NOT EXISTS idx_processed_orders_amount ON processed_orders(amount);

-- Create real-time metrics summary table
CREATE TABLE IF NOT EXISTS real_time_metrics (
    id SERIAL PRIMARY KEY,
    metric_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    total_processed INTEGER NOT NULL,
    total_errors INTEGER NOT NULL,
    throughput_per_second DECIMAL(10,2) NOT NULL,
    active_customers INTEGER NOT NULL,
    cities_served INTEGER NOT NULL,
    avg_order_amount_5min DECIMAL(10,2),
    total_orders_5min INTEGER,
    avg_order_amount_1hour DECIMAL(10,2),
    total_orders_1hour INTEGER,
    fraud_alerts_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for time-based queries
CREATE INDEX IF NOT EXISTS idx_real_time_metrics_timestamp ON real_time_metrics(metric_timestamp);

-- Create customer sessions table for tracking
CREATE TABLE IF NOT EXISTS customer_sessions (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    session_start TIMESTAMP WITH TIME ZONE NOT NULL,
    session_end TIMESTAMP WITH TIME ZONE,
    order_count INTEGER DEFAULT 0,
    total_spent DECIMAL(10,2) DEFAULT 0,
    avg_order_value DECIMAL(10,2) DEFAULT 0,
    session_duration_minutes INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    last_activity TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for customer sessions
CREATE INDEX IF NOT EXISTS idx_customer_sessions_customer_id ON customer_sessions(customer_id);
CREATE INDEX IF NOT EXISTS idx_customer_sessions_active ON customer_sessions(is_active);
CREATE INDEX IF NOT EXISTS idx_customer_sessions_start ON customer_sessions(session_start);

-- Create fraud alerts table
CREATE TABLE IF NOT EXISTS fraud_alerts (
    id SERIAL PRIMARY KEY,
    alert_type VARCHAR(50) NOT NULL,
    customer_id INTEGER NOT NULL,
    order_id INTEGER,
    description TEXT NOT NULL,
    severity VARCHAR(20) DEFAULT 'MEDIUM',
    amount DECIMAL(10,2),
    city VARCHAR(100),
    alert_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for fraud alerts
CREATE INDEX IF NOT EXISTS idx_fraud_alerts_customer_id ON fraud_alerts(customer_id);
CREATE INDEX IF NOT EXISTS idx_fraud_alerts_type ON fraud_alerts(alert_type);
CREATE INDEX IF NOT EXISTS idx_fraud_alerts_timestamp ON fraud_alerts(alert_timestamp);
CREATE INDEX IF NOT EXISTS idx_fraud_alerts_resolved ON fraud_alerts(is_resolved);

-- Create city analytics table for aggregated city metrics
CREATE TABLE IF NOT EXISTS city_analytics (
    id SERIAL PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    date_hour TIMESTAMP WITH TIME ZONE NOT NULL,
    order_count INTEGER DEFAULT 0,
    total_amount DECIMAL(10,2) DEFAULT 0,
    avg_amount DECIMAL(10,2) DEFAULT 0,
    max_amount DECIMAL(10,2) DEFAULT 0,
    min_amount DECIMAL(10,2) DEFAULT 0,
    unique_customers INTEGER DEFAULT 0,
    high_value_orders INTEGER DEFAULT 0,
    fraud_alerts INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(city, date_hour)
);

-- Create indexes for city analytics
CREATE INDEX IF NOT EXISTS idx_city_analytics_city ON city_analytics(city);
CREATE INDEX IF NOT EXISTS idx_city_analytics_date_hour ON city_analytics(date_hour);

-- Create a view for easy querying of recent activity
CREATE OR REPLACE VIEW recent_activity AS
SELECT 
    po.order_id,
    po.customer_id,
    po.amount,
    po.city,
    po.timestamp,
    po.processed_at,
    po.is_high_value,
    cs.order_count as customer_total_orders,
    cs.total_spent as customer_lifetime_value,
    ca.order_count as city_hourly_orders,
    ca.avg_amount as city_hourly_avg
FROM processed_orders po
LEFT JOIN customer_sessions cs ON po.customer_id = cs.customer_id AND cs.is_active = TRUE
LEFT JOIN city_analytics ca ON po.city = ca.city 
    AND DATE_TRUNC('hour', po.timestamp) = ca.date_hour
WHERE po.processed_at >= NOW() - INTERVAL '24 hours'
ORDER BY po.processed_at DESC;

-- Create a view for fraud monitoring dashboard
CREATE OR REPLACE VIEW fraud_monitoring AS
SELECT 
    fa.alert_type,
    fa.customer_id,
    fa.order_id,
    fa.description,
    fa.severity,
    fa.amount,
    fa.city,
    fa.alert_timestamp,
    fa.is_resolved,
    po.customer_order_count,
    po.customer_total_spent
FROM fraud_alerts fa
LEFT JOIN processed_orders po ON fa.order_id = po.order_id
WHERE fa.alert_timestamp >= NOW() - INTERVAL '7 days'
ORDER BY fa.alert_timestamp DESC;

-- Create a materialized view for city performance
CREATE MATERIALIZED VIEW IF NOT EXISTS city_performance AS
SELECT 
    city,
    COUNT(*) as total_orders,
    SUM(amount) as total_revenue,
    AVG(amount) as avg_order_value,
    COUNT(DISTINCT customer_id) as unique_customers,
    COUNT(*) FILTER (WHERE is_high_value = TRUE) as high_value_orders,
    MAX(amount) as max_order,
    MIN(amount) as min_order,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount) as median_order,
    DATE_TRUNC('day', timestamp) as order_date
FROM processed_orders
WHERE timestamp >= NOW() - INTERVAL '30 days'
GROUP BY city, DATE_TRUNC('day', timestamp)
ORDER BY order_date DESC, total_revenue DESC;

-- Create index on materialized view
CREATE INDEX IF NOT EXISTS idx_city_performance_city_date ON city_performance(city, order_date);

-- Function to refresh materialized view (call this periodically)
CREATE OR REPLACE FUNCTION refresh_city_performance()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW city_performance;
END;
$$ LANGUAGE plpgsql;

-- Create function to clean old data (data retention)
CREATE OR REPLACE FUNCTION cleanup_old_data(retention_days INTEGER DEFAULT 90)
RETURNS void AS $$
BEGIN
    -- Clean processed_orders older than retention_days
    DELETE FROM processed_orders 
    WHERE timestamp < NOW() - (retention_days || ' days')::INTERVAL;
    
    -- Clean real_time_metrics older than retention_days
    DELETE FROM real_time_metrics 
    WHERE metric_timestamp < NOW() - (retention_days || ' days')::INTERVAL;
    
    -- Clean resolved fraud alerts older than retention_days
    DELETE FROM fraud_alerts 
    WHERE is_resolved = TRUE 
    AND resolved_at < NOW() - (retention_days || ' days')::INTERVAL;
    
    -- Clean inactive customer sessions older than 7 days
    DELETE FROM customer_sessions 
    WHERE is_active = FALSE 
    AND updated_at < NOW() - INTERVAL '7 days';
    
    -- Clean city_analytics older than retention_days
    DELETE FROM city_analytics 
    WHERE date_hour < NOW() - (retention_days || ' days')::INTERVAL;
    
    RAISE NOTICE 'Data cleanup completed for records older than % days', retention_days;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions (adjust as needed for your environment)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO analytics_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO analytics_user;

-- Insert some sample data for testing (optional)
INSERT INTO processed_orders (
    order_id, customer_id, amount, city, timestamp, 
    customer_order_count, customer_total_spent, is_high_value
) VALUES 
(1001, 101, 99.99, 'Jakarta', NOW() - INTERVAL '1 hour', 1, 99.99, false),
(1002, 102, 249.50, 'Surabaya', NOW() - INTERVAL '45 minutes', 1, 249.50, true),
(1003, 101, 79.99, 'Jakarta', NOW() - INTERVAL '30 minutes', 2, 179.98, false),
(1004, 103, 399.99, 'Bandung', NOW() - INTERVAL '15 minutes', 1, 399.99, true),
(1005, 104, 149.99, 'Medan', NOW() - INTERVAL '5 minutes', 1, 149.99, false)
ON CONFLICT (order_id) DO NOTHING;

-- Insert sample customer sessions
INSERT INTO customer_sessions (
    customer_id, session_start, order_count, total_spent, is_active, last_activity
) VALUES 
(101, NOW() - INTERVAL '1 hour', 2, 179.98, true, NOW() - INTERVAL '30 minutes'),
(102, NOW() - INTERVAL '45 minutes', 1, 249.50, true, NOW() - INTERVAL '45 minutes'),
(103, NOW() - INTERVAL '15 minutes', 1, 399.99, true, NOW() - INTERVAL '15 minutes'),
(104, NOW() - INTERVAL '5 minutes', 1, 149.99, true, NOW() - INTERVAL '5 minutes')
ON CONFLICT DO NOTHING;

-- Print completion message
SELECT 'Database initialization completed successfully!' as status;
