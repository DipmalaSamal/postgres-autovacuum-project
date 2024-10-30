import psycopg2
from faker import Faker
import random
import time

# Establish connection to PostgreSQL
conn = psycopg2.connect(
    dbname="test_db",
    user="dbtune_user",
    password="dbtune_pass",
    host="localhost",
    port="5432"
)
conn.autocommit = True
cur = conn.cursor()

# Initialize Faker for generating mock data
faker = Faker()

# Step 1: Create Schema, Tables, and Indexes
try:
    print("Creating initial schema...")
    cur.execute('''
        CREATE SCHEMA IF NOT EXISTS test_schema;
        CREATE TABLE IF NOT EXISTS test_schema.test_table (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            address VARCHAR(100),
            email VARCHAR(100),
            created_at TIMESTAMP DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_name ON test_schema.test_table (name);
        CREATE INDEX IF NOT EXISTS idx_created_at ON test_schema.test_table (created_at);
    ''')
    print("Schema and tables created successfully.")
except psycopg2.Error as e:
    print("Error creating schema and tables:", e)

# Step 2: Load Mock Data
try:
    print("Populating database with initial data...")
    for _ in range(10000):  # Adjust for amount of data
        cur.execute('''
            INSERT INTO test_schema.test_table (name, address, email) 
            VALUES (%s, %s, %s);
        ''', (faker.name(), faker.address(), faker.email()))
    print("Data population complete.")
except psycopg2.Error as e:
    print("Error populating data:", e)

# Step 3: Stress Autovacuum
try:
    print("Running autovacuum stress test...")
    for _ in range(10000):  # Number of rows to generate dead tuples
        # Insert rows
        cur.execute('''
            INSERT INTO test_schema.test_table (name, address, email) 
            VALUES (%s, %s, %s);
        ''', (faker.name(), faker.address(), faker.email()))
        
        # Delete rows to create dead tuples
        cur.execute('''
            DELETE FROM test_schema.test_table 
            WHERE id IN (SELECT id FROM test_schema.test_table ORDER BY random() LIMIT 100);
        ''')
        
        # Brief pause to allow autovacuum to catch up or lag behind
        time.sleep(0.1)
    print("Autovacuum stress test complete.")
except psycopg2.Error as e:
    print("Error during autovacuum stress test:", e)
finally:
    cur.close()
    conn.close()
