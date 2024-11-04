PostgreSQL Autovacuum Stress Test

This project sets up a PostgreSQL instance in Docker, loads mock data, and applies workload stress to the autovacuum process. Observability tools like Prometheus and Grafana are integrated to monitor database performance. The goal is to understand autovacuum behavior under high workload conditions and adjust PostgreSQL parameters.

Table of Contents

* Project Overview
* Prerequisites
* Project Structure
* Installation
* Usage
* Configuration
* Observability Tools
* Access
* Notes

Project Overview


The purpose of this project is to simulate a high workload on the autovacuum process in PostgreSQL. By creating dead tuples through inserts and deletes, we can observe the performance of autovacuum in real-time. Metrics are gathered using Prometheus and displayed in Grafana for comprehensive analysis.

Prerequisites
* Install Docker and Docker Compose on your system:
  * (https://docs.docker.com/desktop/install/mac-install/)
* Install Git, Python, psycopg2, and faker:
  * brew install python
  * brew install git
  * pip3 install psycopg2-binary
  * pip3 install faker
* Internet access to pull required Docker images.

Project Structure

```
postgres-autovacuum-project
├── autovacuum_stress_test.py       # Main script for stressing autovacuum
├── docker-compose.yml               # Docker setup for PostgreSQL, Prometheus, and Grafana
├── prometheus/                      # Prometheus configuration directory
│   └── prometheus.yml               # Prometheus configuration for scraping metrics
├── postgres-data/                   # Directory for PostgreSQL data storage
├── queries.yaml                     # Custom metrics for PostgreSQL monitoring
├── README.md                        # Project documentation
└── grafana/                         # Grafana dashboard configuration (JSON files)
```


Installation

* Start Docker Services: 
 * Run the following command to start PostgreSQL, Prometheus, Grafana, and other services defined in docker-compose.yml:
   * docker-compose up -d

Usage

* Populate the initial schema, load mock data, and generate dead tuples:
  * python autovacuum_stress.py

* Access Grafana Dashboard:
http://localhost:3000

Login: admin

Password: admin

Configuration
* Docker Compose Configuration: Modify docker-compose.yml to adjust service parameters.
* Prometheus Configuration: Customize prometheus.yml to change scraping intervals.
* Queries Configuration: The postgres_exporter serves as a monitoring sidecar, gathering metrics about the PostgreSQL database and exposing them to Prometheus. These metrics are defined in queries.yaml for custom metrics displayed in Grafana.


Observability Tools

* Prometheus: Collects metrics from the PostgreSQL exporter and serves them to Grafana.
* Grafana: Visualizes metrics for PostgreSQL tables, autovacuum operations, and dead tuple counts.


Access

PostgreSQL Users:

* User: postgres

Password: admin
* User: dbtune_user

Password: dbtune_pass
* Database Name: test_db
Access PostgreSQL using:

docker exec -it postgres psql -U postgres -d test_db
docker exec -it postgres psql -U dbtune_user -d test_db

Metrics Access:
* Postgres Exporter: http://localhost:9187/metrics
* Prometheus: http://localhost:9090
* Grafana: http://localhost:3000
  * User: admin
  * Password: admin

Notes

How do we see that the autovacuum is indeed failing to satisfactorily do its job?

To verify if autovacuum is not effectively handling dead tuples, look for the following metrics in Prometheus and Grafana:

* Dead Tuples Count (n_dead_tup):
Query pg_stat_user_tables for n_dead_tup on test_table. A rising count of dead tuples without subsequent reduction indicates that autovacuum is not keeping up with the workload.

* Disk Space Usage:
Dead tuples occupy storage space, and when autovacuum can’t keep up, disk usage grows significantly. Track overall database size using pg_database_size('db_name').

* CPU and Memory Usage:
High CPU usage indicates that PostgreSQL is devoting resources to autovacuum tasks but potentially not keeping up. As dead tuples accumulate, memory consumption can increase due to larger table sizes and indexing overhead. Track CPU and memory usage for the PostgreSQL container to observe spikes when autovacuum runs.

* Buffers Allocated (buffers_alloc):
Measures the total number of buffers allocated by the background writer. A high rate of buffer allocations might indicate frequent modifications (inserts, updates, or deletes), which could create dead tuples faster than autovacuum can clean them up.

* Checkpoint Time (checkpoint_time):
Tracks the total time spent in checkpoints. If checkpoint durations are high, it might mean I/O resources are being heavily utilized, potentially delaying autovacuum.

How can we reconfigure the PostgreSQL parameters to resolve this problem?

When autovacuum is unable to handle the workload, consider adjusting the following parameters in postgresql.conf or directly in the database session:

* Increase the Number of Autovacuum Workers:
  * Parameter: autovacuum_max_workers
  * Recommended Adjustment: Increase from default (3) to a higher value to allow more concurrent autovacuum jobs. 

* Autovacuum Nap Time:
  * Parameter: autovacuum_naptime
  * Recommended Adjustment: Decrease from default (1min) to a shorter interval (e.g., 10s) to ensure autovacuum checks for dead tuples more frequently.

* Autovacuum Thresholds:
  * Parameters: autovacuum_vacuum_threshold and autovacuum_vacuum_scale_factor
  * Recommended Adjustment: Reduce these values to trigger autovacuum more aggressively when fewer dead tuples accumulate (e.g., autovacuum_vacuum_threshold = 10, autovacuum_vacuum_scale_factor = 0.05). This makes autovacuum more responsive to changes.

* Autovacuum Cost Delay:
  * Parameter: autovacuum_vacuum_cost_delay
  * Recommended Adjustment: Lower the delay (e.g., from 2ms to 0ms) to make autovacuum run faster, at the cost of increased I/O load. This can help reduce dead tuples faster in high-activity environments.
