# SQL Tasks

This directory contains SQL solutions for various data analysis tasks.

## Tasks Overview

1. **Task 1**: Calculate total spending by customer (`task1_total_spending.sql`)
2. **Task 2**: Find city with highest number of orders (`task2_city_highest_orders.sql`)
3. **Task 3**: Query optimization examples (`task3_query_optimization.sql`)

## Assumptions

- Database tables follow standard e-commerce schema
- Proper indexes are available for optimization
- Data integrity constraints are in place

## How to Run

Execute each SQL file in your preferred database environment:

```sql
-- Example for PostgreSQL
\i task1_total_spending.sql
\i task2_city_highest_orders.sql
\i task3_query_optimization.sql
```

## Database Schema Assumptions

```sql
-- Customers table
customers (customer_id, name, email, city, registration_date)

-- Orders table
orders (order_id, customer_id, order_date, total_amount, status)

-- Order_items table
order_items (item_id, order_id, product_id, quantity, unit_price)

-- Products table
products (product_id, product_name, category, price)
```
