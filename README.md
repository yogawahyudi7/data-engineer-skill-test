# Data Engineer Skill Test

This repository contains solutions for the Data Engineer Assessment covering SQL queries, ETL pipelines, real-time processing, data modeling, and performance optimization.

## Project Structure

```
data-engineer-skill-test/
├── README.md
├── sql/                        # SQL tasks and queries
│   ├── README.md
│   ├── task1_total_spending.sql
│   ├── task2_city_highest_orders.sql
│   └── task3_query_optimization.sql
├── etl-pipeline/              # ETL pipeline implementation
│   ├── task_instructions.md
│   ├── etl_script.py
│   ├── transformed_data.csv
│   └── requirements.txt
├── real-time-processing/      # Kafka real-time processing
│   ├── kafka_setup.md
│   ├── docker-compose.yml
│   ├── consumer_script.py
│   ├── processed_results.sql
│   └── requirements.txt
├── data-modeling/            # Data warehouse schema design
│   ├── schema_design.md
│   └── schema_diagram.png
└── debugging-optimization/   # Performance optimization
    ├── analysis.md
    ├── optimized_script.py
    └── requirements.txt
```

## How to Run

Each folder contains specific instructions for running the respective components:

1. **SQL Tasks**: Execute SQL files directly in your database environment
2. **ETL Pipeline**: Follow instructions in `etl-pipeline/task_instructions.md`
3. **Real-time Processing**: Setup Kafka using `real-time-processing/kafka_setup.md`
4. **Data Modeling**: Review schema design documentation
5. **Performance Optimization**: Analysis and optimized scripts provided

## Technologies Used

- **SQL**: PostgreSQL/MySQL compatible queries
- **Python**: ETL scripts, Kafka consumers, optimization
- **Apache Kafka**: Real-time data streaming
- **Docker**: Containerized services
- **Data Modeling**: Star schema design

## Author

Created for Data Engineer Assessment - July 2025
