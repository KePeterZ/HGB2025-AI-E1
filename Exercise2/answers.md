# Activity 1 — Debezium CDC with PostgreSQL and Kafka

## What Debezium CDC Does

* Debezium uses **PostgreSQL logical replication** to capture database changes
* Monitors INSERT, UPDATE, and DELETE operations without querying tables
* Converts each change into an **event** and publishes it to Kafka
* Kafka topics represent change streams for database tables
* PostgreSQL remains the **source of truth** (OLTP workload is unaffected)

---

## Why This Architecture Is Relevant in the Big Data & AI Era

* Enables **real-time data pipelines** instead of batch ETL jobs
* Decouples data producers (databases) from multiple consumers
* Supports **high-throughput and scalable** event distribution
* Allows AI/ML systems to consume **fresh, up-to-date data**
* Prevents heavy analytical workloads from impacting transactional databases
* Aligns with **event-driven and streaming-first architectures**

---

## Architectural Benefits

* **Scalability:** Kafka supports many consumers independently
* **Reliability:** Events are persisted and replayable
* **Fault tolerance:** Consumers can recover from failures using offsets
* **Ordering guarantees:** Per-partition ordering is preserved
* **Loose coupling:** New consumers can be added without database changes

---

## Typical Use Cases

* Real-time analytics and dashboards
* Streaming feature generation for machine learning models
* Fraud detection and anomaly detection
* Data synchronization between microservices
* Audit logs and change history
* Cache invalidation and search index updates

---

## Why Not Traditional Batch Processing

* Batch ETL introduces latency and stale data
* Periodic polling increases database load
* Difficult to scale with many consumers
* Not suitable for real-time or near real-time AI systems

---

✅ **Conclusion:**
Debezium CDC with Kafka provides a **scalable, reliable, and real-time data streaming architecture** that is well suited for Big Data and AI use cases, enabling multiple downstream systems to react to database changes without impacting transactional performance.


# Activity 2 — Temperature Logging System

## Part 1 — Architectural Choice

**Chosen architecture:**

* **Direct batch access to PostgreSQL** (scheduled query / polling)

**Rationale:**

* Data volume is very low (1 row per minute)
* Only one consumer (reporting script)
* No real-time or near-real-time requirements
* Simpler than introducing Kafka or CDC
* Reduces operational and infrastructure overhead
* PostgreSQL already stores all required data reliably
* A scheduled query every 10 minutes is sufficient to compute averages

**Typical implementation:**

* Python script
* PostgreSQL connection using `psycopg2` or `sqlalchemy`
* SQL query with time-based filtering (`NOW() - INTERVAL '10 minutes'`)
* Cron job or loop with sleep interval

---

## Part 2 — Implementation Approach

**Data flow:**

* `temperature_data_producer.py`

  * Inserts sensor readings into PostgreSQL once per minute
* `temperature_data_consumer.py` (extended)

  * Connects directly to PostgreSQL
  * Queries last 10 minutes of data
  * Computes average temperature
  * Outputs or stores the result

**Consumer logic (high level):**

* Establish PostgreSQL connection
* Execute SQL query:

  * Filter records from the last 10 minutes
* Compute average temperature in SQL
* Repeat every 10 minutes

**Why no Kafka / Debezium:**

* Streaming infrastructure is unnecessary
* Adds complexity without clear benefits
* Polling cost is negligible at this scale

---

## Part 3 — Architecture Discussion

### Resource Efficiency

* Very low CPU and memory usage
* No additional brokers, connectors, or topics
* Minimal storage overhead

### Operability

* Easy to understand and debug
* Fewer moving parts
* Standard PostgreSQL monitoring tools apply

### Deployment Complexity

* Simple deployment (PostgreSQL + Python script)
* No Kafka, Zookeeper, or Connect cluster needed
* Easy local and production setup

### Trade-offs

* Not suitable for high-frequency or real-time use cases
* Polling would not scale well with many consumers
* Acceptable and optimal for the given constraints
