#!/usr/bin/env python3
"""
ETL Pipeline Script
Author: Data Engineer Assessment
Date: July 2025

This script demonstrates a complete ETL pipeline that:
1. Extracts data from multiple sources (CSV, JSON API, Database)
2. Transforms data according to business rules
3. Loads data into a target data warehouse
"""

import pandas as pd
import numpy as np
import requests
import logging
import argparse
import os
import sys
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Optional imports for database functionality
try:
    import psycopg2
    from sqlalchemy import create_engine, text
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    print("Database dependencies not available. Running in CSV-only mode.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl_pipeline.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ETLPipeline:
    """Main ETL Pipeline Class"""
    
    def __init__(self, config: Dict):
        """Initialize ETL pipeline with configuration"""
        self.config = config
        self.batch_size = config.get('batch_size', 1000)
        self.source_type = config.get('source_type', 'csv')
        self.target_type = config.get('target_type', 'csv')
        self.data_quality_issues = []
        
        # Database connection (if needed)
        if self.target_type == 'postgres':
            self.engine = self._create_db_connection()
        else:
            self.engine = None
    
    def _create_db_connection(self):
        """Create database connection"""
        if not DB_AVAILABLE:
            logger.warning("Database dependencies not available")
            return None
            
        try:
            connection_string = (
                f"postgresql://{self.config.get('db_user', 'postgres')}:"
                f"{self.config.get('db_password', 'password')}@"
                f"{self.config.get('db_host', 'localhost')}:"
                f"{self.config.get('db_port', 5432)}/"
                f"{self.config.get('db_name', 'datawarehouse')}"
            )
            engine = create_engine(connection_string)
            logger.info("Database connection established successfully")
            return engine
        except Exception as e:
            logger.error(f"Failed to create database connection: {e}")
            return None
    
    def extract_customer_data(self) -> pd.DataFrame:
        """Extract customer data from CSV source"""
        logger.info("Extracting customer data from CSV...")
        
        # Sample customer data (in real scenario, this would be from actual CSV file)
        sample_data = {
            'customer_id': range(1, 1001),
            'name': [f'Customer {i}' for i in range(1, 1001)],
            'email': [f'customer{i}@email.com' for i in range(1, 1001)],
            'city': np.random.choice(['Jakarta', 'Surabaya', 'Bandung', 'Medan', 'Yogyakarta'], 1000),
            'registration_date': pd.date_range('2023-01-01', periods=1000, freq='D')[:1000]
        }
        
        df = pd.DataFrame(sample_data)
        logger.info(f"Extracted {len(df)} customer records")
        return df
    
    def extract_order_data(self) -> pd.DataFrame:
        """Extract order data from JSON API or sample data"""
        logger.info("Extracting order data...")
        
        # Sample order data (in real scenario, this would be from API)
        np.random.seed(42)
        order_count = 5000
        
        sample_data = {
            'order_id': range(1, order_count + 1),
            'customer_id': np.random.randint(1, 1001, order_count),
            'order_date': pd.date_range('2024-01-01', periods=order_count, freq='H')[:order_count],
            'total_amount': np.round(np.random.uniform(10, 500, order_count), 2),
            'status': np.random.choice(['completed', 'pending', 'cancelled'], order_count, p=[0.8, 0.15, 0.05])
        }
        
        df = pd.DataFrame(sample_data)
        logger.info(f"Extracted {len(df)} order records")
        return df
    
    def extract_product_data(self) -> pd.DataFrame:
        """Extract product data"""
        logger.info("Extracting product data...")
        
        # Sample product data
        categories = ['Electronics', 'Clothing', 'Books', 'Home & Garden', 'Sports']
        product_count = 500
        
        sample_data = {
            'product_id': range(1, product_count + 1),
            'product_name': [f'Product {i}' for i in range(1, product_count + 1)],
            'category': np.random.choice(categories, product_count),
            'price': np.round(np.random.uniform(5, 200, product_count), 2)
        }
        
        df = pd.DataFrame(sample_data)
        logger.info(f"Extracted {len(df)} product records")
        return df
    
    def validate_data(self, df: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
        """Validate data quality and log issues"""
        logger.info(f"Validating {dataset_name} data...")
        
        initial_count = len(df)
        issues = []
        
        # Check for null values in critical columns
        if dataset_name == 'customers':
            critical_cols = ['customer_id', 'name', 'email']
            for col in critical_cols:
                null_count = df[col].isnull().sum()
                if null_count > 0:
                    issues.append(f"{col}: {null_count} null values")
            
            # Validate email format
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            invalid_emails = ~df['email'].str.match(email_pattern, na=False)
            if invalid_emails.sum() > 0:
                issues.append(f"email: {invalid_emails.sum()} invalid formats")
                df = df[~invalid_emails]  # Remove invalid emails
        
        elif dataset_name == 'orders':
            # Check for negative amounts
            negative_amounts = df['total_amount'] < 0
            if negative_amounts.sum() > 0:
                issues.append(f"total_amount: {negative_amounts.sum()} negative values")
                df = df[~negative_amounts]  # Remove negative amounts
        
        final_count = len(df)
        removed_count = initial_count - final_count
        
        if issues:
            self.data_quality_issues.extend(issues)
            logger.warning(f"{dataset_name} validation issues: {issues}")
            logger.warning(f"Removed {removed_count} invalid records")
        else:
            logger.info(f"{dataset_name} validation passed - no issues found")
        
        return df
    
    def transform_customer_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform customer data according to business rules"""
        logger.info("Transforming customer data...")
        
        # Standardize city names
        df['city'] = df['city'].str.title()
        
        # Normalize email addresses
        df['email'] = df['email'].str.lower()
        
        # Calculate days since registration
        df['days_since_registration'] = (
            pd.Timestamp.now() - pd.to_datetime(df['registration_date'])
        ).dt.days
        
        # Add customer segment based on registration date
        df['customer_segment'] = pd.cut(
            df['days_since_registration'],
            bins=[0, 30, 90, 365, float('inf')],
            labels=['New', 'Recent', 'Established', 'Veteran']
        )
        
        logger.info("Customer data transformation completed")
        return df
    
    def transform_order_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform order data according to business rules"""
        logger.info("Transforming order data...")
        
        # Convert order_date to proper datetime
        df['order_date'] = pd.to_datetime(df['order_date'])
        
        # Add derived fields
        df['order_year'] = df['order_date'].dt.year
        df['order_month'] = df['order_date'].dt.month
        df['order_day_of_week'] = df['order_date'].dt.day_name()
        
        # Categorize order amounts
        df['order_size'] = pd.cut(
            df['total_amount'],
            bins=[0, 50, 150, 300, float('inf')],
            labels=['Small', 'Medium', 'Large', 'Extra Large']
        )
        
        # Flag suspicious orders (very high amounts)
        df['is_suspicious'] = df['total_amount'] > 400
        
        logger.info("Order data transformation completed")
        return df
    
    def create_customer_summary(self, customers_df: pd.DataFrame, orders_df: pd.DataFrame) -> pd.DataFrame:
        """Create customer summary with aggregated metrics"""
        logger.info("Creating customer summary...")
        
        # Aggregate order metrics by customer
        order_summary = orders_df.groupby('customer_id').agg({
            'order_id': 'count',
            'total_amount': ['sum', 'mean', 'max'],
            'order_date': ['min', 'max'],
            'is_suspicious': 'sum'
        }).round(2)
        
        # Flatten column names
        order_summary.columns = [
            'total_orders', 'total_spent', 'avg_order_value', 'max_order_value',
            'first_order_date', 'last_order_date', 'suspicious_orders'
        ]
        
        # Merge with customer data
        customer_summary = customers_df.merge(
            order_summary, 
            left_on='customer_id', 
            right_index=True, 
            how='left'
        )
        
        # Fill null values for customers with no orders
        numeric_cols = ['total_orders', 'total_spent', 'avg_order_value', 'max_order_value', 'suspicious_orders']
        customer_summary[numeric_cols] = customer_summary[numeric_cols].fillna(0)
        
        # Calculate customer lifetime value (CLV)
        customer_summary['clv_score'] = (
            customer_summary['total_spent'] * 0.6 +
            customer_summary['total_orders'] * 10 * 0.3 +
            customer_summary['avg_order_value'] * 0.1
        ).round(2)
        
        # Determine value segment
        customer_summary['value_segment'] = pd.cut(
            customer_summary['total_spent'],
            bins=[0, 100, 500, 1000, float('inf')],
            labels=['Low Value', 'Medium Value', 'High Value', 'VIP']
        )
        
        logger.info(f"Customer summary created with {len(customer_summary)} records")
        return customer_summary
    
    def load_to_csv(self, df: pd.DataFrame, filename: str):
        """Load transformed data to CSV file"""
        logger.info(f"Loading data to CSV: {filename}")
        
        df.to_csv(filename, index=False)
        logger.info(f"Successfully saved {len(df)} records to {filename}")
    
    def load_to_database(self, df: pd.DataFrame, table_name: str):
        """Load transformed data to database"""
        if not self.engine or not DB_AVAILABLE:
            logger.error("Database connection not available")
            return
        
        logger.info(f"Loading data to database table: {table_name}")
        
        try:
            df.to_sql(
                table_name, 
                self.engine, 
                if_exists='replace', 
                index=False,
                chunksize=self.batch_size
            )
            logger.info(f"Successfully loaded {len(df)} records to {table_name}")
        except Exception as e:
            logger.error(f"Failed to load data to database: {e}")
    
    def generate_data_quality_report(self):
        """Generate data quality report"""
        logger.info("Generating data quality report...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_issues': len(self.data_quality_issues),
            'issues': self.data_quality_issues
        }
        
        with open('data_quality_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Data quality report generated with {len(self.data_quality_issues)} issues")
    
    def run_pipeline(self):
        """Execute the complete ETL pipeline"""
        logger.info("Starting ETL Pipeline execution...")
        start_time = datetime.now()
        
        try:
            # Extract phase
            logger.info("=== EXTRACT PHASE ===")
            customers_df = self.extract_customer_data()
            orders_df = self.extract_order_data()
            products_df = self.extract_product_data()
            
            # Validate phase
            logger.info("=== VALIDATION PHASE ===")
            customers_df = self.validate_data(customers_df, 'customers')
            orders_df = self.validate_data(orders_df, 'orders')
            products_df = self.validate_data(products_df, 'products')
            
            # Transform phase
            logger.info("=== TRANSFORM PHASE ===")
            customers_transformed = self.transform_customer_data(customers_df)
            orders_transformed = self.transform_order_data(orders_df)
            
            # Create aggregated datasets
            customer_summary = self.create_customer_summary(customers_transformed, orders_transformed)
            
            # Load phase
            logger.info("=== LOAD PHASE ===")
            if self.target_type == 'csv':
                self.load_to_csv(customer_summary, 'transformed_data.csv')
                self.load_to_csv(customers_transformed, 'customers_transformed.csv')
                self.load_to_csv(orders_transformed, 'orders_transformed.csv')
            elif self.target_type == 'postgres':
                self.load_to_database(customer_summary, 'customer_summary')
                self.load_to_database(customers_transformed, 'customers_dim')
                self.load_to_database(orders_transformed, 'orders_fact')
            
            # Generate reports
            self.generate_data_quality_report()
            
            # Pipeline completion
            end_time = datetime.now()
            duration = end_time - start_time
            
            logger.info("=== PIPELINE COMPLETED SUCCESSFULLY ===")
            logger.info(f"Total execution time: {duration}")
            logger.info(f"Records processed - Customers: {len(customers_transformed)}, Orders: {len(orders_transformed)}")
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            raise

def main():
    """Main function to run ETL pipeline"""
    parser = argparse.ArgumentParser(description='ETL Pipeline')
    parser.add_argument('--source', choices=['csv', 'api', 'database'], default='csv', help='Data source type')
    parser.add_argument('--target', choices=['csv', 'postgres'], default='csv', help='Target destination')
    parser.add_argument('--batch-size', type=int, default=1000, help='Batch size for processing')
    parser.add_argument('--full-refresh', action='store_true', help='Perform full data refresh')
    
    args = parser.parse_args()
    
    # Configuration
    config = {
        'source_type': args.source,
        'target_type': args.target,
        'batch_size': args.batch_size,
        'full_refresh': args.full_refresh,
        # Database configuration (update with actual values)
        'db_host': 'localhost',
        'db_port': 5432,
        'db_name': 'datawarehouse',
        'db_user': 'postgres',
        'db_password': 'password'
    }
    
    # Initialize and run pipeline
    pipeline = ETLPipeline(config)
    pipeline.run_pipeline()

if __name__ == "__main__":
    main()
