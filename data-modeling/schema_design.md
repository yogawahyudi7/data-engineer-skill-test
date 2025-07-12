# Data Warehouse Schema Design

## Overview

This document outlines the design of a star schema data warehouse for an e-commerce analytics platform. The schema is optimized for analytical queries and reporting while maintaining data integrity and performance.

## Business Requirements

The data warehouse needs to support:

1. **Sales Analytics**: Order trends, revenue analysis, customer behavior
2. **Customer Analytics**: Customer lifetime value, segmentation, retention
3. **Product Analytics**: Product performance, category analysis, inventory insights
4. **Geographic Analytics**: Regional performance, city-wise metrics
5. **Time-based Analytics**: Seasonal trends, monthly/quarterly reports
6. **Real-time Dashboards**: Current performance metrics, alerts

## Schema Design Approach

### Design Principles

1. **Star Schema**: Central fact table surrounded by dimension tables
2. **Kimball Methodology**: Bottom-up approach with conformed dimensions
3. **Performance Optimization**: Proper indexing and partitioning
4. **Data Quality**: Built-in validation and consistency checks
5. **Scalability**: Design for future growth and additional data sources

### Key Design Decisions

- **Slowly Changing Dimensions (SCD)**: Type 2 for customer and product changes
- **Surrogate Keys**: Integer-based keys for better performance
- **Grain Definition**: One row per order line item in fact table
- **Additive Measures**: Revenue, quantity, cost can be summed across all dimensions
- **Time Dimension**: Comprehensive time attributes for flexible analysis

## Star Schema Structure

```
                    ┌─────────────────┐
                    │   Fact_Orders   │
                    │                 │
                    │ OrderID (PK)    │
                    │ DateKey (FK)    │──────┐
                    │ CustomerKey(FK) │──┐   │
                    │ ProductKey (FK) │─┐│   │
                    │ StoreKey (FK)   │┐││   │
                    │ PaymentKey (FK) ││││   │
                    │                 ││││   │
                    │ Quantity        ││││   │
                    │ UnitPrice       ││││   │
                    │ LineTotal       ││││   │
                    │ Discount        ││││   │
                    │ Tax             ││││   │
                    │ Cost            ││││   │
                    └─────────────────┘│││   │
                                       │││   │
        ┌──────────────────────────────┘││   │
        │                               ││   │
        ▼                               ││   │
┌─────────────────┐                     ││   │
│ Dim_Customer    │                     ││   │
│                 │                     ││   │
│ CustomerKey(PK) │                     ││   │
│ CustomerID      │                     ││   │
│ FirstName       │                     ││   │
│ LastName        │                     ││   │
│ Email           │                     ││   │
│ Phone           │                     ││   │
│ Address         │                     ││   │
│ City            │                     ││   │
│ State           │                     ││   │
│ PostalCode      │                     ││   │
│ Country         │                     ││   │
│ CustomerSegment │                     ││   │
│ LifetimeValue   │                     ││   │
│ RegistrationDate│                     ││   │
│ IsActive        │                     ││   │
│ EffectiveDate   │                     ││   │
│ ExpiryDate      │                     ││   │
│ IsCurrent       │                     ││   │
└─────────────────┘                     ││   │
                                        ││   │
        ┌───────────────────────────────┘│   │
        │                                │   │
        ▼                                │   │
┌─────────────────┐                      │   │
│ Dim_Product     │                      │   │
│                 │                      │   │
│ ProductKey (PK) │                      │   │
│ ProductID       │                      │   │
│ ProductName     │                      │   │
│ ProductDesc     │                      │   │
│ CategoryL1      │                      │   │
│ CategoryL2      │                      │   │
│ CategoryL3      │                      │   │
│ Brand           │                      │   │
│ UnitCost        │                      │   │
│ ListPrice       │                      │   │
│ IsDiscontinued  │                      │   │
│ LaunchDate      │                      │   │
│ EffectiveDate   │                      │   │
│ ExpiryDate      │                      │   │
│ IsCurrent       │                      │   │
└─────────────────┘                      │   │
                                         │   │
        ┌────────────────────────────────┘   │
        │                                    │
        ▼                                    │
┌─────────────────┐                          │
│ Dim_Store       │                          │
│                 │                          │
│ StoreKey (PK)   │                          │
│ StoreID         │                          │
│ StoreName       │                          │
│ StoreType       │                          │
│ Address         │                          │
│ City            │                          │
│ State           │                          │
│ PostalCode      │                          │
│ Country         │                          │
│ Region          │                          │
│ District        │                          │
│ ManagerName     │                          │
│ OpenDate        │                          │
│ CloseDate       │                          │
│ IsActive        │                          │
│ SquareFootage   │                          │
└─────────────────┘                          │
                                             │
        ┌────────────────────────────────────┘
        │
        ▼
┌─────────────────┐
│ Dim_Date        │
│                 │
│ DateKey (PK)    │
│ Date            │
│ DayOfWeek       │
│ DayName         │
│ DayOfMonth      │
│ DayOfYear       │
│ WeekOfYear      │
│ Month           │
│ MonthName       │
│ Quarter         │
│ Year            │
│ IsWeekend       │
│ IsHoliday       │
│ HolidayName     │
│ FiscalYear      │
│ FiscalQuarter   │
│ Season          │
└─────────────────┘

        ┌─────────────────┐
        │ Dim_Payment     │
        │                 │
        │ PaymentKey (PK) │
        │ PaymentMethod   │
        │ PaymentType     │
        │ CardType        │
        │ ProcessorName   │
        │ IsSecure        │
        │ ProcessingFee   │
        └─────────────────┘
```

## Detailed Table Specifications

### Fact Table: Fact_Orders

**Purpose**: Core transaction data at order line item level
**Grain**: One row per product ordered per order

```sql
CREATE TABLE Fact_Orders (
    OrderID BIGINT PRIMARY KEY,
    OrderLineID BIGINT NOT NULL,
    DateKey INT NOT NULL,
    CustomerKey BIGINT NOT NULL,
    ProductKey BIGINT NOT NULL,
    StoreKey INT NOT NULL,
    PaymentKey INT NOT NULL,

    -- Measures (Additive)
    Quantity DECIMAL(10,2) NOT NULL,
    UnitPrice DECIMAL(10,2) NOT NULL,
    LineTotal DECIMAL(10,2) NOT NULL,
    Discount DECIMAL(10,2) DEFAULT 0,
    Tax DECIMAL(10,2) DEFAULT 0,
    ShippingCost DECIMAL(10,2) DEFAULT 0,

    -- Derived Measures
    UnitCost DECIMAL(10,2),
    Profit DECIMAL(10,2) GENERATED ALWAYS AS (LineTotal - (UnitCost * Quantity)) STORED,

    -- Audit Fields
    CreatedDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ModifiedDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ETLBatchID VARCHAR(50),

    -- Foreign Key Constraints
    FOREIGN KEY (DateKey) REFERENCES Dim_Date(DateKey),
    FOREIGN KEY (CustomerKey) REFERENCES Dim_Customer(CustomerKey),
    FOREIGN KEY (ProductKey) REFERENCES Dim_Product(ProductKey),
    FOREIGN KEY (StoreKey) REFERENCES Dim_Store(StoreKey),
    FOREIGN KEY (PaymentKey) REFERENCES Dim_Payment(PaymentKey)
);
```

### Dimension Tables

#### Dim_Customer

**Purpose**: Customer master data with SCD Type 2 support
**SCD Type**: Type 2 (Historical tracking of changes)

```sql
CREATE TABLE Dim_Customer (
    CustomerKey BIGINT PRIMARY KEY,
    CustomerID VARCHAR(50) NOT NULL,

    -- Customer Attributes
    FirstName VARCHAR(100),
    LastName VARCHAR(100),
    FullName VARCHAR(200) GENERATED ALWAYS AS (FirstName || ' ' || LastName) STORED,
    Email VARCHAR(200),
    Phone VARCHAR(20),

    -- Address Information
    Address VARCHAR(500),
    City VARCHAR(100),
    State VARCHAR(100),
    PostalCode VARCHAR(20),
    Country VARCHAR(100),
    Latitude DECIMAL(10,8),
    Longitude DECIMAL(11,8),

    -- Customer Analytics
    CustomerSegment VARCHAR(50), -- VIP, High Value, Medium Value, Low Value
    LifetimeValue DECIMAL(12,2),
    TotalOrders INT DEFAULT 0,
    RegistrationDate DATE,
    LastOrderDate DATE,

    -- Status
    IsActive BOOLEAN DEFAULT TRUE,

    -- SCD Type 2 Fields
    EffectiveDate DATE NOT NULL,
    ExpiryDate DATE DEFAULT '9999-12-31',
    IsCurrent BOOLEAN DEFAULT TRUE,

    -- Audit Fields
    CreatedDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ModifiedDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ETLBatchID VARCHAR(50)
);
```

#### Dim_Product

**Purpose**: Product master data with hierarchy and SCD Type 2
**SCD Type**: Type 2 (Track price and attribute changes)

```sql
CREATE TABLE Dim_Product (
    ProductKey BIGINT PRIMARY KEY,
    ProductID VARCHAR(50) NOT NULL,

    -- Product Information
    ProductName VARCHAR(200) NOT NULL,
    ProductDescription TEXT,
    SKU VARCHAR(100),
    UPC VARCHAR(50),

    -- Product Hierarchy
    CategoryL1 VARCHAR(100), -- Electronics
    CategoryL2 VARCHAR(100), -- Smartphones
    CategoryL3 VARCHAR(100), -- Android Phones
    Brand VARCHAR(100),

    -- Pricing
    UnitCost DECIMAL(10,2),
    ListPrice DECIMAL(10,2),
    WholesalePrice DECIMAL(10,2),

    -- Product Attributes
    Color VARCHAR(50),
    Size VARCHAR(50),
    Weight DECIMAL(8,2),
    Dimensions VARCHAR(100),

    -- Status
    IsDiscontinued BOOLEAN DEFAULT FALSE,
    LaunchDate DATE,
    DiscontinuedDate DATE,

    -- SCD Type 2 Fields
    EffectiveDate DATE NOT NULL,
    ExpiryDate DATE DEFAULT '9999-12-31',
    IsCurrent BOOLEAN DEFAULT TRUE,

    -- Audit Fields
    CreatedDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ModifiedDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ETLBatchID VARCHAR(50)
);
```

#### Dim_Date

**Purpose**: Time dimension for comprehensive date-based analysis
**Grain**: One row per day

```sql
CREATE TABLE Dim_Date (
    DateKey INT PRIMARY KEY, -- Format: YYYYMMDD
    Date DATE NOT NULL UNIQUE,

    -- Day Attributes
    DayOfWeek INT, -- 1-7
    DayName VARCHAR(10), -- Monday, Tuesday, etc.
    DayOfMonth INT, -- 1-31
    DayOfYear INT, -- 1-366

    -- Week Attributes
    WeekOfYear INT, -- 1-53
    WeekOfMonth INT, -- 1-6
    WeekStartDate DATE,
    WeekEndDate DATE,

    -- Month Attributes
    Month INT, -- 1-12
    MonthName VARCHAR(20), -- January, February, etc.
    MonthAbbr VARCHAR(3), -- Jan, Feb, etc.
    MonthStartDate DATE,
    MonthEndDate DATE,
    DaysInMonth INT,

    -- Quarter Attributes
    Quarter INT, -- 1-4
    QuarterName VARCHAR(10), -- Q1, Q2, Q3, Q4
    QuarterStartDate DATE,
    QuarterEndDate DATE,

    -- Year Attributes
    Year INT,
    YearName VARCHAR(10),

    -- Fiscal Calendar (if different from calendar year)
    FiscalYear INT,
    FiscalQuarter INT,
    FiscalMonth INT,

    -- Special Indicators
    IsWeekend BOOLEAN,
    IsHoliday BOOLEAN,
    HolidayName VARCHAR(100),
    IsBusinessDay BOOLEAN,
    Season VARCHAR(20), -- Spring, Summer, Fall, Winter

    -- Relative Indicators
    IsToday BOOLEAN DEFAULT FALSE,
    IsYesterday BOOLEAN DEFAULT FALSE,
    IsCurrentWeek BOOLEAN DEFAULT FALSE,
    IsCurrentMonth BOOLEAN DEFAULT FALSE,
    IsCurrentQuarter BOOLEAN DEFAULT FALSE,
    IsCurrentYear BOOLEAN DEFAULT FALSE
);
```

## Data Quality and Constraints

### Primary Key Constraints

```sql
-- Surrogate key sequences
CREATE SEQUENCE customer_key_seq START 1;
CREATE SEQUENCE product_key_seq START 1;
CREATE SEQUENCE store_key_seq START 1;
CREATE SEQUENCE payment_key_seq START 1;
```

### Data Quality Checks

```sql
-- Customer data quality
ALTER TABLE Dim_Customer ADD CONSTRAINT chk_customer_email
    CHECK (Email IS NULL OR Email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- Product data quality
ALTER TABLE Dim_Product ADD CONSTRAINT chk_product_price
    CHECK (ListPrice >= 0 AND UnitCost >= 0);

-- Order data quality
ALTER TABLE Fact_Orders ADD CONSTRAINT chk_order_quantity
    CHECK (Quantity > 0);
ALTER TABLE Fact_Orders ADD CONSTRAINT chk_order_price
    CHECK (UnitPrice >= 0);
```

### Indexing Strategy

```sql
-- Fact table indexes
CREATE INDEX idx_fact_orders_date ON Fact_Orders(DateKey);
CREATE INDEX idx_fact_orders_customer ON Fact_Orders(CustomerKey);
CREATE INDEX idx_fact_orders_product ON Fact_Orders(ProductKey);
CREATE INDEX idx_fact_orders_store ON Fact_Orders(StoreKey);
CREATE INDEX idx_fact_orders_composite ON Fact_Orders(DateKey, CustomerKey, ProductKey);

-- Dimension table indexes
CREATE INDEX idx_customer_id ON Dim_Customer(CustomerID);
CREATE INDEX idx_customer_current ON Dim_Customer(IsCurrent) WHERE IsCurrent = TRUE;
CREATE INDEX idx_product_id ON Dim_Product(ProductID);
CREATE INDEX idx_product_category ON Dim_Product(CategoryL1, CategoryL2);
CREATE INDEX idx_date_year_month ON Dim_Date(Year, Month);
```

## ETL Considerations

### Data Loading Strategy

1. **Incremental Loading**: Load only new/changed records
2. **SCD Processing**: Handle slowly changing dimensions appropriately
3. **Data Validation**: Comprehensive quality checks before loading
4. **Error Handling**: Robust error handling and logging
5. **Performance**: Optimize for bulk loading operations

### Sample ETL Pseudocode

```sql
-- Customer SCD Type 2 Processing
MERGE INTO Dim_Customer AS target
USING staging_customers AS source
ON target.CustomerID = source.CustomerID AND target.IsCurrent = TRUE
WHEN MATCHED AND (
    target.Email != source.Email OR
    target.City != source.City OR
    target.CustomerSegment != source.CustomerSegment
) THEN
    UPDATE SET
        IsCurrent = FALSE,
        ExpiryDate = CURRENT_DATE - 1
WHEN NOT MATCHED THEN
    INSERT (CustomerKey, CustomerID, ..., EffectiveDate, IsCurrent)
    VALUES (NEXT VALUE FOR customer_key_seq, source.CustomerID, ..., CURRENT_DATE, TRUE);
```

## Analytics Use Cases

### 1. Sales Performance Analysis

```sql
-- Monthly sales trends by category
SELECT
    d.Year,
    d.Month,
    p.CategoryL1,
    SUM(f.LineTotal) as Revenue,
    SUM(f.Quantity) as Units,
    COUNT(DISTINCT f.CustomerKey) as UniqueCustomers
FROM Fact_Orders f
JOIN Dim_Date d ON f.DateKey = d.DateKey
JOIN Dim_Product p ON f.ProductKey = p.ProductKey
WHERE d.Year = 2024
GROUP BY d.Year, d.Month, p.CategoryL1
ORDER BY d.Year, d.Month, Revenue DESC;
```

### 2. Customer Lifetime Value

```sql
-- Customer segmentation by lifetime value
SELECT
    c.CustomerSegment,
    COUNT(*) as CustomerCount,
    AVG(c.LifetimeValue) as AvgLifetimeValue,
    SUM(f.LineTotal) as TotalRevenue
FROM Dim_Customer c
LEFT JOIN Fact_Orders f ON c.CustomerKey = f.CustomerKey
WHERE c.IsCurrent = TRUE
GROUP BY c.CustomerSegment
ORDER BY AvgLifetimeValue DESC;
```

### 3. Product Performance

```sql
-- Top performing products by category
SELECT
    p.CategoryL1,
    p.CategoryL2,
    p.ProductName,
    SUM(f.LineTotal) as Revenue,
    SUM(f.Quantity) as UnitsSold,
    AVG(f.UnitPrice) as AvgPrice,
    SUM(f.Profit) as TotalProfit
FROM Fact_Orders f
JOIN Dim_Product p ON f.ProductKey = p.ProductKey
JOIN Dim_Date d ON f.DateKey = d.DateKey
WHERE d.Year = 2024 AND p.IsCurrent = TRUE
GROUP BY p.CategoryL1, p.CategoryL2, p.ProductName
ORDER BY Revenue DESC
LIMIT 20;
```

## Scalability and Performance

### Partitioning Strategy

```sql
-- Partition fact table by date
CREATE TABLE Fact_Orders (
    -- columns...
) PARTITION BY RANGE (DateKey);

-- Create monthly partitions
CREATE TABLE Fact_Orders_202401 PARTITION OF Fact_Orders
    FOR VALUES FROM (20240101) TO (20240201);
```

### Materialized Views

```sql
-- Pre-aggregate monthly sales summary
CREATE MATERIALIZED VIEW mv_monthly_sales AS
SELECT
    d.Year,
    d.Month,
    s.Region,
    p.CategoryL1,
    SUM(f.LineTotal) as Revenue,
    SUM(f.Quantity) as Units,
    COUNT(DISTINCT f.CustomerKey) as Customers
FROM Fact_Orders f
JOIN Dim_Date d ON f.DateKey = d.DateKey
JOIN Dim_Store s ON f.StoreKey = s.StoreKey
JOIN Dim_Product p ON f.ProductKey = p.ProductKey
GROUP BY d.Year, d.Month, s.Region, p.CategoryL1;
```

## Monitoring and Maintenance

### Data Quality Monitoring

```sql
-- Daily data quality checks
SELECT
    'Order Volume' as Metric,
    COUNT(*) as Value,
    CASE WHEN COUNT(*) < 1000 THEN 'ALERT' ELSE 'OK' END as Status
FROM Fact_Orders
WHERE DateKey = TO_CHAR(CURRENT_DATE, 'YYYYMMDD')::INT

UNION ALL

SELECT
    'Revenue Anomaly' as Metric,
    SUM(LineTotal) as Value,
    CASE WHEN SUM(LineTotal) < 10000 THEN 'ALERT' ELSE 'OK' END as Status
FROM Fact_Orders
WHERE DateKey = TO_CHAR(CURRENT_DATE, 'YYYYMMDD')::INT;
```

## Benefits of This Design

1. **Performance**: Star schema optimized for analytical queries
2. **Flexibility**: Easy to add new dimensions and facts
3. **Scalability**: Partitioning and indexing for large data volumes
4. **Data Quality**: Built-in constraints and validation
5. **Historical Tracking**: SCD Type 2 for dimension changes
6. **Business Intelligence**: Supports complex analytical requirements
7. **Maintainability**: Clear structure and documentation

## Future Enhancements

1. **Additional Dimensions**: Geographic, Time-of-Day, Promotion
2. **Additional Facts**: Inventory, Returns, Customer Service
3. **Real-time Updates**: Change data capture for near real-time analytics
4. **Data Lineage**: Track data flow from source to analytics
5. **Advanced Analytics**: Integration with ML/AI platforms
