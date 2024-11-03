PostgreSQL Autovacuum Stress Test
This project sets up a PostgreSQL instance in Docker, loads mock data, and applies workload stress to the autovacuum process. Observability tools like Prometheus and Grafana are integrated to monitor database performance. The goal is to understand autovacuum behavior under high workload conditions and adjust PostgreSQL parameters if necessary.


Table of Contents
* Project Overview
* Prerequisites
* Instruction
* Observability Tools
* Code Walkthrough
* Access
* Notes


Project Overview
The purpose of this project is to simulate a high workload on the autovacuum process in PostgreSQL. By creating dead tuples through inserts and deletes, we can observe the performance of autovacuum in real time. Metrics are gathered using Prometheus and displayed in Grafana for comprehensive analysis.

Prerequisites
* Install Docker and Docker Compose on your system
https://docs.docker.com/desktop/install/mac-install/
* Install Git,Python,psycopg2 and faker
brew install python
brew install git
pip3 install psycopg2-binary
pip3 install faker
* Internet access to pull required Docker images.

Instruction
* Make directories to place below required files and directories:
README.md	grafana	 prometheus  autovacuum_stress.py	postgres-config	 docker-compose.yml	  postgres-data

* Start Docker Services: Run the following command to start PostgreSQL, Prometheus, Grafana, and other services defined in docker-compose.yml:
docker-compose up -d
* Populate Initial Schema: Execute the custom Python script to create a schema, load mock data, and generate dead tuples:
python autovacuum_stress.py
* Access Grafana Dashboard:
http://localhost:3000 password mentioned in Access Section.


Observability Tools
* Prometheus: Collects metrics from the PostgreSQL exporter and serves them to Grafana.
* Grafana: Visualizes metrics for PostgreSQL tables, autovacuum operations, and dead tuple counts.

Code Walkthrough
Docker Configuration
* The docker-compose.yml file sets up the PostgreSQL, Prometheus, and Grafana services.
* Postgres_exporter serves as a monitoring sidecar, gathering metrics about the PostgreSQL database and exposing them to Prometheus.
* Custom Metrics Queries are configured in queries.yaml to define the metrics that the exporter will monitor.
Python Script (autovacuum_stress.py)
1. Create Schema:
    * Defines the test_schema and test_table with sample columns and indexes.
2. Load Mock Data:
    * Uses the Faker library to generate realistic data.
    * Inserts initial rows into the table for baseline data.
3. Stress Autovacuum:
    * Continuously inserts and deletes rows to generate dead tuples.
    * Short pauses simulate real workload intervals.
Custom Prometheus Queries (in prometheus.yml)
* Metrics like pg_stat_user_tables and pg_settings_autovacuum are configured to provide insight into table statistics and autovacuum settings.

Access
user: postgres
password: admin
user: dbtune_user
password: dbtune_pass
database name: test_db

docker exec -it postgres psql -U postgres -d test_db
docker exec -it postgres psql -U dbtune_user -d test_db

postgres-exporter:
http://localhost:9187/metrics

prometheus:
http://localhost:9090

grafana:
user: admin
password: admin
http://localhost:3000

Notes
4. (Provide notes) How do we see that the autovacuum is indeed failing to satisfactorily do its job?
To verify if autovacuum is not effectively handling dead tuples, following metrics in Prometheus and Grafana to look into it:

* Dead Tuples Count (n_dead_tup):
Query: pg_stat_user_tables for n_dead_tup on test_table.
A rising count of dead tuples without subsequent reduction indicates that autovacuum is not keeping up with the workload.
* Disk Space Usage:
Dead tuples occupy storage space, and when autovacuum can’t keep up, disk usage grows significantly.
Track overall database size using pg_database_size('db_name').
* CPU and Memory Usage:
High CPU usage indicates that PostgreSQL is devoting resources to autovacuum tasks but potentially not keeping up.
As dead tuples accumulate, memory consumption can increase due to larger table sizes and indexing overhead.
Track CPU and memory usage for the PostgreSQL container to observe spikes when autovacuum runs.

5. (Provide notes) How can we reconfigure the Postgres parameters to resolve this problem?
When autovacuum is unable to handle the workload, adjusting the following parameters in postgresql.conf or directly in the database session for tuning:

* Increase the Number of Autovacuum Workers:
Parameter: autovacuum_max_workers
Recommended Adjustment: Increase from default (3) to a higher value to allow more concurrent autovacuum jobs. Useful in environments with heavy transactional loads.
* Parameter: autovacuum_naptime
Recommended Adjustment: Decrease from default (1min) to a shorter interval (e.g., 10s) to ensure autovacuum checks for dead tuples more frequently.
* Parameters: autovacuum_vacuum_threshold and autovacuum_vacuum_scale_factor
Recommended Adjustment: Reduce these values to trigger autovacuum more aggressively when fewer dead tuples accumulate (e.g., autovacuum_vacuum_threshold = 10, autovacuum_vacuum_scale_factor = 0.05). This makes autovacuum more responsive to changes.
* Parameter: autovacuum_vacuum_cost_delay
Recommended Adjustment: Lower the delay (e.g., from 2ms to 0ms) to make autovacuum run faster, albeit at the cost of increased I/O load. This can help in reducing dead tuples faster in high-activity environments.
Testing Parameter Changes:
After modifying parameters, restart the PostgreSQL service or reload the configuration to apply changes.
Re-run the autovacuum_stress.py script to simulate workload and monitor if dead tuple counts decrease as expected. Observe the Grafana dashboard to check if autovacuum performance improves under the new settings.