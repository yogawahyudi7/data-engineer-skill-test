#!/usr/bin/env python3
"""
Kafka Consumer Script for Real-time Order Processing
Author: Data Engineer Assessment
Date: July 2025

This script demonstrates real-time processing of streaming data using Apache Kafka.
It consumes order events, processes them, and stores aggregated results.
"""

import json
import logging
import signal
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading
from collections import defaultdict, deque

# Kafka imports (with fallback for demo)
try:
    from kafka import KafkaConsumer, KafkaProducer
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    print("Kafka-python not available. Running in simulation mode.")

# Database imports (with fallback)
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    import redis
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    print("Database dependencies not available. Using in-memory storage.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('consumer.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class OrderProcessor:
    """Real-time order processing engine"""
    
    def __init__(self):
        self.processed_count = 0
        self.error_count = 0
        self.start_time = datetime.now()
        
        # In-memory aggregations (sliding windows)
        self.order_metrics = defaultdict(lambda: {
            'count': 0,
            'total_amount': 0.0,
            'avg_amount': 0.0,
            'max_amount': 0.0,
            'min_amount': float('inf')
        })
        
        # Time-based windows (last 5 minutes, 1 hour, 1 day)
        self.time_windows = {
            '5min': deque(maxlen=300),  # 5 minutes with 1-second resolution
            '1hour': deque(maxlen=3600),  # 1 hour with 1-second resolution
            '1day': deque(maxlen=86400)   # 1 day with 1-second resolution
        }
        
        # Customer behavior tracking
        self.customer_sessions = defaultdict(lambda: {
            'session_start': None,
            'order_count': 0,
            'total_spent': 0.0,
            'last_activity': None
        })
        
        # Fraud detection patterns
        self.fraud_patterns = {
            'high_velocity': defaultdict(list),  # Orders per customer per time window
            'large_amounts': [],  # Unusually large orders
            'geographic_anomalies': defaultdict(set)  # Customer location changes
        }
    
    def process_order_event(self, order_data: Dict) -> Dict:
        """Process individual order event"""
        try:
            # Extract order information
            order_id = order_data.get('order_id')
            customer_id = order_data.get('customer_id')
            amount = float(order_data.get('amount', 0))
            timestamp = order_data.get('timestamp')
            city = order_data.get('city', 'Unknown')
            
            # Validate required fields
            if not all([order_id, customer_id, amount, timestamp]):
                raise ValueError("Missing required fields in order data")
            
            # Parse timestamp
            order_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            # Update global metrics
            self.processed_count += 1
            
            # Update order metrics by city
            city_metrics = self.order_metrics[city]
            city_metrics['count'] += 1
            city_metrics['total_amount'] += amount
            city_metrics['avg_amount'] = city_metrics['total_amount'] / city_metrics['count']
            city_metrics['max_amount'] = max(city_metrics['max_amount'], amount)
            city_metrics['min_amount'] = min(city_metrics['min_amount'], amount)
            
            # Update time-based windows
            current_time = datetime.now()
            order_record = {
                'timestamp': current_time,
                'order_id': order_id,
                'customer_id': customer_id,
                'amount': amount,
                'city': city
            }
            
            for window in self.time_windows.values():
                window.append(order_record)
            
            # Update customer session
            session = self.customer_sessions[customer_id]
            if session['session_start'] is None:
                session['session_start'] = current_time
            
            session['order_count'] += 1
            session['total_spent'] += amount
            session['last_activity'] = current_time
            
            # Fraud detection
            self._detect_fraud_patterns(customer_id, amount, city, current_time)
            
            # Calculate derived metrics
            processed_data = {
                'order_id': order_id,
                'customer_id': customer_id,
                'amount': amount,
                'city': city,
                'timestamp': timestamp,
                'processed_at': current_time.isoformat(),
                'customer_order_count': session['order_count'],
                'customer_total_spent': session['total_spent'],
                'city_avg_amount': city_metrics['avg_amount'],
                'is_high_value': amount > 200,
                'session_duration_minutes': (current_time - session['session_start']).total_seconds() / 60
            }
            
            logger.info(f"Processed order {order_id} for customer {customer_id}: ${amount} in {city}")
            return processed_data
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error processing order: {e}")
            return {'error': str(e), 'raw_data': order_data}
    
    def _detect_fraud_patterns(self, customer_id: int, amount: float, city: str, timestamp: datetime):
        """Detect potential fraud patterns"""
        
        # High velocity detection (more than 5 orders in 1 minute)
        velocity_window = self.fraud_patterns['high_velocity'][customer_id]
        velocity_window.append(timestamp)
        
        # Keep only last minute
        one_minute_ago = timestamp - timedelta(minutes=1)
        velocity_window[:] = [t for t in velocity_window if t > one_minute_ago]
        
        if len(velocity_window) > 5:
            logger.warning(f"HIGH VELOCITY ALERT: Customer {customer_id} made {len(velocity_window)} orders in 1 minute")
        
        # Large amount detection
        if amount > 500:
            self.fraud_patterns['large_amounts'].append({
                'customer_id': customer_id,
                'amount': amount,
                'timestamp': timestamp,
                'city': city
            })
            logger.warning(f"LARGE AMOUNT ALERT: Customer {customer_id} order of ${amount}")
        
        # Geographic anomaly detection
        customer_cities = self.fraud_patterns['geographic_anomalies'][customer_id]
        customer_cities.add(city)
        
        if len(customer_cities) > 3:
            logger.warning(f"GEOGRAPHIC ALERT: Customer {customer_id} ordering from {len(customer_cities)} different cities")
    
    def get_real_time_metrics(self) -> Dict:
        """Get current real-time metrics"""
        current_time = datetime.now()
        uptime = current_time - self.start_time
        
        # Calculate throughput metrics
        throughput_per_second = self.processed_count / max(uptime.total_seconds(), 1)
        
        # Calculate windowed metrics
        windowed_stats = {}
        for window_name, window_data in self.time_windows.items():
            if window_data:
                amounts = [record['amount'] for record in window_data]
                windowed_stats[window_name] = {
                    'order_count': len(amounts),
                    'total_amount': sum(amounts),
                    'avg_amount': sum(amounts) / len(amounts),
                    'max_amount': max(amounts),
                    'min_amount': min(amounts)
                }
            else:
                windowed_stats[window_name] = {
                    'order_count': 0,
                    'total_amount': 0,
                    'avg_amount': 0,
                    'max_amount': 0,
                    'min_amount': 0
                }
        
        return {
            'timestamp': current_time.isoformat(),
            'uptime_seconds': uptime.total_seconds(),
            'total_processed': self.processed_count,
            'total_errors': self.error_count,
            'throughput_per_second': round(throughput_per_second, 2),
            'active_customers': len(self.customer_sessions),
            'cities_served': len(self.order_metrics),
            'windowed_metrics': windowed_stats,
            'fraud_alerts': {
                'high_velocity_customers': len(self.fraud_patterns['high_velocity']),
                'large_orders': len(self.fraud_patterns['large_amounts']),
                'geographic_anomalies': len(self.fraud_patterns['geographic_anomalies'])
            }
        }

class KafkaOrderConsumer:
    """Kafka consumer for order events"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.processor = OrderProcessor()
        self.running = False
        self.consumer = None
        self.producer = None
        
        # Database connections
        self.db_conn = None
        self.redis_conn = None
        
        if DB_AVAILABLE:
            self._setup_database_connections()
    
    def _setup_database_connections(self):
        """Setup database connections"""
        try:
            # PostgreSQL connection
            self.db_conn = psycopg2.connect(
                host=self.config.get('postgres_host', 'localhost'),
                port=self.config.get('postgres_port', 5432),
                database=self.config.get('postgres_db', 'analytics'),
                user=self.config.get('postgres_user', 'postgres'),
                password=self.config.get('postgres_password', 'password')
            )
            
            # Redis connection
            self.redis_conn = redis.Redis(
                host=self.config.get('redis_host', 'localhost'),
                port=self.config.get('redis_port', 6379),
                db=0,
                decode_responses=True
            )
            
            logger.info("Database connections established")
            
        except Exception as e:
            logger.error(f"Failed to setup database connections: {e}")
            self.db_conn = None
            self.redis_conn = None
    
    def _setup_kafka_consumer(self):
        """Setup Kafka consumer"""
        if not KAFKA_AVAILABLE:
            logger.warning("Kafka not available - running in simulation mode")
            return
        
        try:
            self.consumer = KafkaConsumer(
                'orders',
                'customer-events',
                bootstrap_servers=self.config.get('kafka_servers', ['localhost:9092']),
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id=self.config.get('group_id', 'order-processing-group'),
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                consumer_timeout_ms=1000,  # 1 second timeout for metrics updates
                max_poll_records=500,
                session_timeout_ms=30000,
                heartbeat_interval_ms=3000
            )
            
            self.producer = KafkaProducer(
                bootstrap_servers=self.config.get('kafka_servers', ['localhost:9092']),
                value_serializer=lambda x: json.dumps(x).encode('utf-8')
            )
            
            logger.info("Kafka consumer and producer initialized")
            
        except Exception as e:
            logger.error(f"Failed to setup Kafka consumer: {e}")
            self.consumer = None
            self.producer = None
    
    def save_processed_data(self, processed_data: Dict):
        """Save processed data to database"""
        if not self.db_conn:
            return
        
        try:
            with self.db_conn.cursor() as cursor:
                # Insert processed order
                insert_query = """
                INSERT INTO processed_orders 
                (order_id, customer_id, amount, city, timestamp, processed_at, 
                 customer_order_count, customer_total_spent, city_avg_amount, 
                 is_high_value, session_duration_minutes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (order_id) DO NOTHING
                """
                
                cursor.execute(insert_query, (
                    processed_data['order_id'],
                    processed_data['customer_id'],
                    processed_data['amount'],
                    processed_data['city'],
                    processed_data['timestamp'],
                    processed_data['processed_at'],
                    processed_data['customer_order_count'],
                    processed_data['customer_total_spent'],
                    processed_data['city_avg_amount'],
                    processed_data['is_high_value'],
                    processed_data['session_duration_minutes']
                ))
                
            self.db_conn.commit()
            
        except Exception as e:
            logger.error(f"Failed to save processed data: {e}")
            self.db_conn.rollback()
    
    def update_real_time_metrics(self):
        """Update real-time metrics in Redis"""
        if not self.redis_conn:
            return
        
        try:
            metrics = self.processor.get_real_time_metrics()
            
            # Store current metrics
            self.redis_conn.set('metrics:current', json.dumps(metrics))
            
            # Store historical metrics (with TTL)
            timestamp_key = f"metrics:history:{int(time.time())}"
            self.redis_conn.setex(timestamp_key, 3600, json.dumps(metrics))  # 1 hour TTL
            
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")
    
    def simulate_data_stream(self):
        """Simulate data stream for demo purposes"""
        import random
        
        logger.info("Starting data simulation mode...")
        
        cities = ['Jakarta', 'Surabaya', 'Bandung', 'Medan', 'Yogyakarta', 'Semarang']
        customer_ids = list(range(1, 101))  # 100 customers
        
        while self.running:
            try:
                # Generate random order
                order_data = {
                    'order_id': random.randint(10000, 99999),
                    'customer_id': random.choice(customer_ids),
                    'amount': round(random.uniform(10, 600), 2),
                    'city': random.choice(cities),
                    'timestamp': datetime.now().isoformat()
                }
                
                # Process the order
                processed_data = self.processor.process_order_event(order_data)
                
                if 'error' not in processed_data:
                    self.save_processed_data(processed_data)
                
                # Random delay between orders (0.1 to 2 seconds)
                time.sleep(random.uniform(0.1, 2.0))
                
            except Exception as e:
                logger.error(f"Error in simulation: {e}")
                time.sleep(1)
    
    def consume_messages(self):
        """Consume messages from Kafka"""
        if not self.consumer:
            logger.info("Kafka consumer not available - starting simulation")
            self.simulate_data_stream()
            return
        
        logger.info("Starting Kafka message consumption...")
        
        try:
            for message in self.consumer:
                if not self.running:
                    break
                
                try:
                    # Process the message
                    order_data = message.value
                    processed_data = self.processor.process_order_event(order_data)
                    
                    if 'error' not in processed_data:
                        # Save to database
                        self.save_processed_data(processed_data)
                        
                        # Send to processed topic
                        if self.producer:
                            self.producer.send('processed-orders', processed_data)
                    
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error in message consumption: {e}")
    
    def start_metrics_updater(self):
        """Start background thread for metrics updates"""
        def metrics_updater():
            while self.running:
                try:
                    self.update_real_time_metrics()
                    
                    # Log current metrics every 10 seconds
                    metrics = self.processor.get_real_time_metrics()
                    logger.info(f"Metrics: {metrics['total_processed']} processed, "
                              f"{metrics['throughput_per_second']:.2f}/sec, "
                              f"{metrics['active_customers']} customers, "
                              f"{metrics['cities_served']} cities")
                    
                    time.sleep(10)  # Update every 10 seconds
                    
                except Exception as e:
                    logger.error(f"Error updating metrics: {e}")
                    time.sleep(10)
        
        metrics_thread = threading.Thread(target=metrics_updater, daemon=True)
        metrics_thread.start()
        logger.info("Metrics updater thread started")
    
    def start(self):
        """Start the consumer"""
        logger.info("Starting Kafka Order Consumer...")
        
        self.running = True
        self._setup_kafka_consumer()
        
        # Start metrics updater in background
        self.start_metrics_updater()
        
        # Start consuming messages
        try:
            self.consume_messages()
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down...")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the consumer"""
        logger.info("Stopping consumer...")
        self.running = False
        
        if self.consumer:
            self.consumer.close()
        
        if self.producer:
            self.producer.close()
        
        if self.db_conn:
            self.db_conn.close()
        
        if self.redis_conn:
            self.redis_conn.close()
        
        logger.info("Consumer stopped")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("Received shutdown signal")
    sys.exit(0)

def main():
    """Main function"""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Configuration
    config = {
        'kafka_servers': ['localhost:9092'],
        'group_id': 'order-processing-group',
        'postgres_host': 'localhost',
        'postgres_port': 5432,
        'postgres_db': 'analytics',
        'postgres_user': 'postgres',
        'postgres_password': 'password',
        'redis_host': 'localhost',
        'redis_port': 6379
    }
    
    # Create and start consumer
    consumer = KafkaOrderConsumer(config)
    consumer.start()

if __name__ == "__main__":
    main()
