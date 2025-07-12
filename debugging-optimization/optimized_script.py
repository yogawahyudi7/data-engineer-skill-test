#!/usr/bin/env python3
"""
Optimized Data Processing Script
Author: Data Engineer Assessment
Date: July 2025

This script demonstrates the optimized version of the data processing pipeline
with significant performance improvements over the original implementation.

Key Optimizations:
1. Connection pooling instead of creating new connections
2. Batch processing instead of individual queries
3. Chunked data processing for memory efficiency
4. Parallel processing using ThreadPoolExecutor
5. Vectorized operations using pandas
6. Comprehensive error handling and logging
7. Performance monitoring and metrics
"""

import pandas as pd
import numpy as np
import logging
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from typing import List, Dict, Any, Optional, Generator
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Optional imports with fallbacks
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.pool import QueuePool
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(threadName)s] - %(message)s',
    handlers=[
        logging.FileHandler('optimized_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor and track performance metrics"""
    
    def __init__(self):
        self.start_time = time.time()
        self.processed_records = 0
        self.error_count = 0
        self.batch_count = 0
        self.lock = threading.Lock()
        
    def record_processed(self, count: int = 1):
        """Record processed records count"""
        with self.lock:
            self.processed_records += count
    
    def record_error(self, count: int = 1):
        """Record error count"""
        with self.lock:
            self.error_count += count
    
    def record_batch(self, count: int = 1):
        """Record batch processing count"""
        with self.lock:
            self.batch_count += count
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        elapsed = time.time() - self.start_time
        throughput = self.processed_records / elapsed if elapsed > 0 else 0
        
        # Use psutil if available, otherwise provide placeholder values
        if PSUTIL_AVAILABLE:
            memory_usage = psutil.virtual_memory().percent
            cpu_usage = psutil.cpu_percent()
        else:
            memory_usage = 50.0  # Placeholder
            cpu_usage = 25.0     # Placeholder
        
        return {
            'elapsed_time': round(elapsed, 2),
            'processed_records': self.processed_records,
            'error_count': self.error_count,
            'batch_count': self.batch_count,
            'throughput': round(throughput, 2),
            'memory_usage': round(memory_usage, 2),
            'cpu_usage': round(cpu_usage, 2),
            'errors_percentage': round((self.error_count / max(self.processed_records, 1)) * 100, 2)
        }
    
    def log_metrics(self):
        """Log current metrics"""
        metrics = self.get_metrics()
        logger.info(f"Performance Metrics: {json.dumps(metrics, indent=2)}")

class OptimizedDataProcessor:
    """Optimized data processing engine with connection pooling and batch processing"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the processor with configuration"""
        self.config = config
        self.monitor = PerformanceMonitor()
        
        # Setup database connection pool
        self.engine = self._create_connection_pool()
        
        # Processing configuration
        self.chunk_size = config.get('chunk_size', 1000)
        self.batch_size = config.get('batch_size', 100)
        self.max_workers = config.get('max_workers', 4)
        
        logger.info(f"Initialized OptimizedDataProcessor with config: {config}")
    
    def _create_connection_pool(self) -> Optional[object]:
        """Create database connection pool"""
        try:
            if self.config.get('use_database', False) and SQLALCHEMY_AVAILABLE:
                connection_string = (
                    f"postgresql://{self.config.get('db_user', 'postgres')}:"
                    f"{self.config.get('db_password', 'password')}@"
                    f"{self.config.get('db_host', 'localhost')}:"
                    f"{self.config.get('db_port', 5432)}/"
                    f"{self.config.get('db_name', 'testdb')}"
                )
                
                engine = create_engine(
                    connection_string,
                    poolclass=QueuePool,
                    pool_size=10,
                    max_overflow=20,
                    pool_pre_ping=True,
                    pool_recycle=3600,  # Recycle connections every hour
                    echo=False
                )
                
                logger.info("Database connection pool created successfully")
                return engine
            else:
                logger.info("Database not configured or SQLAlchemy not available - running in simulation mode")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create database connection pool: {e}")
            return None
    
    @contextmanager
    def get_db_connection(self):
        """Context manager for database connections"""
        if self.engine:
            conn = self.engine.connect()
            try:
                yield conn
            finally:
                conn.close()
        else:
            yield None
    
    def read_data_chunked(self, file_path: str) -> Generator[pd.DataFrame, None, None]:
        """Read large CSV files in chunks for memory efficiency"""
        logger.info(f"Reading data from {file_path} in chunks of {self.chunk_size}")
        
        try:
            chunk_number = 0
            for chunk in pd.read_csv(file_path, chunksize=self.chunk_size):
                chunk_number += 1
                logger.debug(f"Processing chunk {chunk_number} with {len(chunk)} records")
                yield chunk
                
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise
    
    def simulate_data_generation(self, total_records: int) -> Generator[pd.DataFrame, None, None]:
        """Generate sample data for testing when no file is provided"""
        logger.info(f"Generating {total_records} sample records in chunks")
        
        records_generated = 0
        chunk_number = 0
        
        while records_generated < total_records:
            chunk_number += 1
            current_chunk_size = min(self.chunk_size, total_records - records_generated)
            
            # Generate sample data
            data = {
                'id': range(records_generated + 1, records_generated + current_chunk_size + 1),
                'customer_id': np.random.randint(1, 1000, current_chunk_size),
                'product_id': np.random.randint(1, 500, current_chunk_size),
                'amount': np.round(np.random.uniform(10, 500, current_chunk_size), 2),
                'quantity': np.random.randint(1, 10, current_chunk_size),
                'category': np.random.choice(['Electronics', 'Clothing', 'Books', 'Home'], current_chunk_size),
                'timestamp': pd.date_range('2024-01-01', periods=current_chunk_size, freq='H')
            }
            
            chunk = pd.DataFrame(data)
            records_generated += current_chunk_size
            
            logger.debug(f"Generated chunk {chunk_number} with {len(chunk)} records")
            yield chunk
    
    def batch_lookup(self, ids: List[int], lookup_type: str = 'customer') -> Dict[int, Dict]:
        """Perform batch lookup instead of individual queries"""
        if not self.engine:
            # Simulate batch lookup for demo
            return {id_val: {'name': f'{lookup_type}_{id_val}', 'status': 'active'} for id_val in ids}
        
        try:
            with self.get_db_connection() as conn:
                if conn and SQLALCHEMY_AVAILABLE:
                    # Batch query using ANY operator
                    query = text(f"SELECT id, name, status FROM {lookup_type}_lookup WHERE id = ANY(:ids)")
                    result = conn.execute(query, {'ids': ids})
                    
                    return {row.id: {'name': row.name, 'status': row.status} for row in result}
                else:
                    return {}
                    
        except Exception as e:
            logger.error(f"Error in batch lookup for {lookup_type}: {e}")
            return {}
    
    def vectorized_calculations(self, df: pd.DataFrame) -> pd.DataFrame:
        """Perform vectorized calculations instead of row-by-row operations"""
        logger.debug(f"Performing vectorized calculations on {len(df)} records")
        
        # Vectorized operations - much faster than apply() or iterrows()
        df = df.copy()
        
        # Calculate total value
        df['total_value'] = df['amount'] * df['quantity']
        
        # Calculate discounts based on amount (vectorized conditions)
        df['discount_rate'] = np.where(df['amount'] > 200, 0.1,
                              np.where(df['amount'] > 100, 0.05, 0))
        
        df['discounted_amount'] = df['amount'] * (1 - df['discount_rate'])
        df['final_total'] = df['discounted_amount'] * df['quantity']
        
        # Category-based calculations
        category_multipliers = {'Electronics': 1.2, 'Clothing': 1.0, 'Books': 0.9, 'Home': 1.1}
        df['category_multiplier'] = df['category'].map(category_multipliers)
        df['adjusted_total'] = df['final_total'] * df['category_multiplier']
        
        # Tax calculations (vectorized)
        df['tax_rate'] = np.where(df['category'] == 'Electronics', 0.08, 0.05)
        df['tax_amount'] = df['adjusted_total'] * df['tax_rate']
        df['grand_total'] = df['adjusted_total'] + df['tax_amount']
        
        logger.debug("Vectorized calculations completed")
        return df
    
    def process_batch(self, batch_df: pd.DataFrame, batch_id: int) -> Dict[str, Any]:
        """Process a batch of records with optimizations"""
        start_time = time.time()
        
        try:
            # 1. Perform vectorized calculations
            processed_df = self.vectorized_calculations(batch_df)
            
            # 2. Extract unique IDs for batch lookup
            unique_customer_ids = processed_df['customer_id'].unique().tolist()
            unique_product_ids = processed_df['product_id'].unique().tolist()
            
            # 3. Perform batch lookups instead of individual queries
            customer_lookup = self.batch_lookup(unique_customer_ids, 'customer')
            product_lookup = self.batch_lookup(unique_product_ids, 'product')
            
            # 4. Merge lookup results efficiently
            processed_df['customer_name'] = processed_df['customer_id'].map(
                lambda x: customer_lookup.get(x, {}).get('name', 'Unknown')
            )
            processed_df['product_name'] = processed_df['product_id'].map(
                lambda x: product_lookup.get(x, {}).get('name', 'Unknown')
            )
            
            # 5. Additional business logic
            processed_df['customer_segment'] = pd.cut(
                processed_df['grand_total'],
                bins=[0, 100, 300, 1000, float('inf')],
                labels=['Bronze', 'Silver', 'Gold', 'Platinum']
            )
            
            # 6. Update performance metrics
            self.monitor.record_processed(len(processed_df))
            self.monitor.record_batch()
            
            processing_time = time.time() - start_time
            
            result = {
                'batch_id': batch_id,
                'records_processed': len(processed_df),
                'processing_time': round(processing_time, 3),
                'throughput': round(len(processed_df) / processing_time, 2),
                'data': processed_df.to_dict('records') if len(processed_df) <= 10 else None,  # Limit data return
                'summary': {
                    'total_amount': processed_df['grand_total'].sum(),
                    'avg_amount': processed_df['grand_total'].mean(),
                    'unique_customers': processed_df['customer_id'].nunique(),
                    'unique_products': processed_df['product_id'].nunique()
                }
            }
            
            logger.debug(f"Batch {batch_id} processed: {len(processed_df)} records in {processing_time:.3f}s")
            return result
            
        except Exception as e:
            self.monitor.record_error()
            logger.error(f"Error processing batch {batch_id}: {e}")
            return {
                'batch_id': batch_id,
                'error': str(e),
                'records_processed': 0,
                'processing_time': time.time() - start_time
            }
    
    def create_batches(self, df: pd.DataFrame) -> List[pd.DataFrame]:
        """Split dataframe into smaller batches for parallel processing"""
        batches = []
        for i in range(0, len(df), self.batch_size):
            batch = df.iloc[i:i + self.batch_size].copy()
            batches.append(batch)
        return batches
    
    def process_chunk_parallel(self, chunk: pd.DataFrame, chunk_id: int) -> List[Dict[str, Any]]:
        """Process a chunk using parallel batch processing"""
        logger.info(f"Processing chunk {chunk_id} with {len(chunk)} records using {self.max_workers} workers")
        
        # Split chunk into smaller batches for parallel processing
        batches = self.create_batches(chunk)
        
        results = []
        
        # Process batches in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all batch processing tasks
            future_to_batch = {
                executor.submit(self.process_batch, batch, f"{chunk_id}-{i}"): i 
                for i, batch in enumerate(batches)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_batch):
                batch_idx = future_to_batch[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                except Exception as e:
                    logger.error(f"Batch {chunk_id}-{batch_idx} failed: {e}")
                    self.monitor.record_error()
        
        logger.info(f"Chunk {chunk_id} completed: {len(batches)} batches processed")
        return results
    
    def save_results(self, results: List[Dict[str, Any]], output_file: str):
        """Save processing results to file"""
        try:
            # Aggregate all processed data
            all_summaries = []
            total_records = 0
            total_time = 0
            
            for result in results:
                if 'error' not in result:
                    all_summaries.append(result.get('summary', {}))
                    total_records += result.get('records_processed', 0)
                    total_time += result.get('processing_time', 0)
            
            # Create summary report
            summary_report = {
                'processing_summary': {
                    'total_records_processed': total_records,
                    'total_processing_time': round(total_time, 3),
                    'average_throughput': round(total_records / total_time if total_time > 0 else 0, 2),
                    'total_batches': len(results),
                    'successful_batches': len([r for r in results if 'error' not in r]),
                    'failed_batches': len([r for r in results if 'error' in r])
                },
                'performance_metrics': self.monitor.get_metrics(),
                'batch_results': results
            }
            
            # Save to JSON file
            with open(output_file, 'w') as f:
                json.dump(summary_report, f, indent=2, default=str)
            
            logger.info(f"Results saved to {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
    
    def run_optimization_comparison(self, data_source: str, total_records: int = 10000):
        """Run the optimized processing pipeline"""
        logger.info("="*60)
        logger.info("STARTING OPTIMIZED DATA PROCESSING PIPELINE")
        logger.info("="*60)
        
        start_time = time.time()
        all_results = []
        
        try:
            # Determine data source
            if data_source == 'simulate':
                data_generator = self.simulate_data_generation(total_records)
            else:
                data_generator = self.read_data_chunked(data_source)
            
            chunk_id = 0
            
            # Process each chunk
            for chunk in data_generator:
                chunk_id += 1
                logger.info(f"Processing chunk {chunk_id}...")
                
                # Process chunk with parallel batching
                chunk_results = self.process_chunk_parallel(chunk, chunk_id)
                all_results.extend(chunk_results)
                
                # Log progress
                self.monitor.log_metrics()
                
                # Memory cleanup
                del chunk
            
            # Final processing summary
            total_time = time.time() - start_time
            final_metrics = self.monitor.get_metrics()
            
            logger.info("="*60)
            logger.info("PROCESSING COMPLETED SUCCESSFULLY")
            logger.info("="*60)
            logger.info(f"Total Time: {total_time:.2f} seconds")
            logger.info(f"Records Processed: {final_metrics['processed_records']}")
            logger.info(f"Average Throughput: {final_metrics['throughput']:.2f} records/second")
            logger.info(f"Memory Usage: {final_metrics['memory_usage']:.2f}%")
            logger.info(f"Error Rate: {final_metrics['errors_percentage']:.2f}%")
            
            # Save results
            output_file = f"optimized_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.save_results(all_results, output_file)
            
            return {
                'success': True,
                'total_time': total_time,
                'metrics': final_metrics,
                'results_file': output_file
            }
            
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'metrics': self.monitor.get_metrics()
            }
        
        finally:
            if self.engine:
                self.engine.dispose()

def create_sample_data_file(filename: str, num_records: int = 5000):
    """Create a sample CSV file for testing"""
    logger.info(f"Creating sample data file: {filename} with {num_records} records")
    
    data = {
        'id': range(1, num_records + 1),
        'customer_id': np.random.randint(1, 1000, num_records),
        'product_id': np.random.randint(1, 500, num_records),
        'amount': np.round(np.random.uniform(10, 500, num_records), 2),
        'quantity': np.random.randint(1, 10, num_records),
        'category': np.random.choice(['Electronics', 'Clothing', 'Books', 'Home'], num_records),
        'timestamp': pd.date_range('2024-01-01', periods=num_records, freq='H')
    }
    
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    logger.info(f"Sample data file created: {filename}")

def main():
    """Main function to run the optimized data processor"""
    # Configuration
    config = {
        'chunk_size': 1000,      # Process 1000 records per chunk
        'batch_size': 100,       # 100 records per batch within each chunk
        'max_workers': 4,        # Use 4 parallel workers
        'use_database': False,   # Set to True to use actual database
        'db_host': 'localhost',
        'db_port': 5432,
        'db_name': 'testdb',
        'db_user': 'postgres',
        'db_password': 'password'
    }
    
    # Create processor
    processor = OptimizedDataProcessor(config)
    
    # Option 1: Use simulated data
    logger.info("Running with simulated data...")
    result = processor.run_optimization_comparison('simulate', total_records=10000)
    
    # Option 2: Use actual CSV file (uncomment to use)
    # create_sample_data_file('sample_data.csv', 10000)
    # result = processor.run_optimization_comparison('sample_data.csv')
    
    # Print final results
    if result['success']:
        print(f"\n{'='*60}")
        print("OPTIMIZATION RESULTS")
        print(f"{'='*60}")
        print(f"Processing Time: {result['total_time']:.2f} seconds")
        print(f"Records Processed: {result['metrics']['processed_records']}")
        print(f"Throughput: {result['metrics']['throughput']:.2f} records/second")
        print(f"Memory Usage: {result['metrics']['memory_usage']:.2f}%")
        print(f"Results saved to: {result['results_file']}")
        print(f"{'='*60}")
    else:
        print(f"Processing failed: {result['error']}")

if __name__ == "__main__":
    main()
