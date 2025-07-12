# Kafka Setup for Real-time Data Processing

## Overview

This setup provides a complete Apache Kafka environment for real-time data streaming and processing. We'll use Docker Compose to orchestrate the services.

## Architecture

```
Producer → Kafka Broker → Consumer → Database/Analytics
    ↓           ↓           ↓           ↓
 API Data   Topic: orders  Python    PostgreSQL
 Stream     Partitions    Consumer   Time-series
```

## Prerequisites

- Docker and Docker Compose installed
- Python 3.8+
- At least 4GB available RAM

## Quick Start

### 1. Start Kafka Services

```bash
docker-compose up -d
```

### 2. Verify Services are Running

```bash
docker-compose ps
```

### 3. Create Kafka Topics

```bash
# Create orders topic
docker-compose exec kafka kafka-topics --create \
  --topic orders \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1

# Create customer-events topic
docker-compose exec kafka kafka-topics --create \
  --topic customer-events \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1

# List topics to verify
docker-compose exec kafka kafka-topics --list \
  --bootstrap-server localhost:9092
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run Consumer

```bash
python consumer_script.py
```

## Docker Compose Configuration

The `docker-compose.yml` file includes:

- **Zookeeper**: Kafka cluster coordination
- **Kafka Broker**: Message streaming platform
- **Kafka UI**: Web interface for monitoring
- **PostgreSQL**: Database for processed results

### Kafka Configuration Details

- **Bootstrap Servers**: localhost:9092
- **Zookeeper**: localhost:2181
- **Kafka UI**: http://localhost:8080
- **PostgreSQL**: localhost:5432

### Environment Variables

```env
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_GROUP_ID=order-processing-group
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=analytics
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
```

## Topic Configuration

### Orders Topic

- **Partitions**: 3 (for scalability)
- **Replication Factor**: 1 (single broker setup)
- **Retention**: 7 days
- **Cleanup Policy**: delete

### Customer Events Topic

- **Partitions**: 3
- **Replication Factor**: 1
- **Retention**: 24 hours
- **Cleanup Policy**: delete

## Producer Examples

### Send Test Messages

```bash
# Send order event
docker-compose exec kafka kafka-console-producer \
  --topic orders \
  --bootstrap-server localhost:9092

# Then type JSON messages like:
{"order_id": 1001, "customer_id": 123, "amount": 99.99, "timestamp": "2024-07-12T10:30:00Z"}
```

### Python Producer Example

```python
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

# Send order event
order_data = {
    "order_id": 1001,
    "customer_id": 123,
    "amount": 99.99,
    "timestamp": "2024-07-12T10:30:00Z"
}

producer.send('orders', order_data)
producer.flush()
```

## Consumer Configuration

The consumer script (`consumer_script.py`) is configured to:

1. **Subscribe** to multiple topics (orders, customer-events)
2. **Process** messages in real-time
3. **Aggregate** data for analytics
4. **Store** results in PostgreSQL
5. **Handle** errors and retries

### Consumer Groups

- **Group ID**: order-processing-group
- **Auto Offset Reset**: earliest
- **Enable Auto Commit**: True
- **Session Timeout**: 30 seconds

## Monitoring and Management

### Kafka UI Interface

Access the web interface at http://localhost:8080 to:

- Monitor topic partitions and offsets
- View message throughput
- Manage consumer groups
- Browse message contents

### Command Line Tools

```bash
# Monitor consumer group lag
docker-compose exec kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --describe \
  --group order-processing-group

# View topic details
docker-compose exec kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --describe \
  --topic orders
```

## Performance Tuning

### Kafka Broker Settings

```properties
# Memory allocation
-Xmx1G -Xms1G

# Network settings
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600

# Log settings
log.retention.hours=168
log.segment.bytes=1073741824
```

### Consumer Optimization

```python
consumer = KafkaConsumer(
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='order-processing-group',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    max_poll_records=500,  # Batch size
    session_timeout_ms=30000,
    heartbeat_interval_ms=3000
)
```

## Scaling Considerations

### Horizontal Scaling

1. **Add More Partitions**

   ```bash
   kafka-topics --alter --topic orders --partitions 6 --bootstrap-server localhost:9092
   ```

2. **Multiple Consumer Instances**

   ```bash
   # Run multiple consumer processes
   python consumer_script.py &
   python consumer_script.py &
   ```

3. **Kafka Cluster**
   - Add more broker nodes
   - Increase replication factor
   - Use separate Zookeeper ensemble

### Vertical Scaling

- Increase JVM heap size
- Add more CPU cores
- Increase network bandwidth
- Use SSD storage

## Troubleshooting

### Common Issues

1. **Consumer Lag**

   ```bash
   # Check lag
   kafka-consumer-groups --bootstrap-server localhost:9092 --describe --group order-processing-group
   ```

2. **Connection Errors**

   ```bash
   # Test connectivity
   telnet localhost 9092
   ```

3. **Out of Memory**
   ```bash
   # Increase heap size in docker-compose.yml
   KAFKA_HEAP_OPTS: "-Xmx2G -Xms2G"
   ```

### Log Locations

- **Kafka Logs**: `/var/lib/kafka/data/`
- **Zookeeper Logs**: `/var/lib/zookeeper/`
- **Consumer Logs**: `./consumer.log`

## Security Considerations

### Production Setup

1. **Enable SSL/TLS**
2. **Configure SASL authentication**
3. **Set up ACLs for topic access**
4. **Network isolation**
5. **Monitor security logs**

### Development Setup

- Basic authentication disabled
- Open network access
- Plain text communication

## Cleanup

### Stop Services

```bash
docker-compose down
```

### Remove Data Volumes

```bash
docker-compose down -v
```

### Remove Everything

```bash
docker-compose down -v --rmi all
```

## Support and Resources

- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Kafka Python Client](https://kafka-python.readthedocs.io/)
- [Docker Compose Reference](https://docs.docker.com/compose/)

For issues or questions, check the logs and refer to the troubleshooting section above.
