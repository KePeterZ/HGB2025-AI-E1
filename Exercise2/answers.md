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

Below is a **concise, bullet-point based answer for Activity 3**, written in the same **assignment-style** as Activities 1 and 2.

---

# Activity 3 — High-Scale Fraud Detection System

## Part 1 — Architectural Choice

**Chosen architecture:**
**PostgreSQL (OLTP) → Debezium CDC → Kafka → Multiple independent consumer agents**

**Rationale:**

* PostgreSQL remains the **system of record** with strong consistency
* Debezium captures database changes **without polling**
* Kafka enables **high-throughput, low-latency event streaming**
* Multiple fraud detection agents can consume the same data independently
* Near real-time processing is required
* Decouples data ingestion from fraud logic

---

## Part 2 — Consumer Implementation (Conceptual)

**Data flow:**

* Fraud transactions are written at very high rate to PostgreSQL
* Debezium streams row-level changes to Kafka topics
* Each fraud detection agent:

  * Subscribes to the Kafka CDC topic
  * Maintains in-memory state
  * Applies its own detection logic
  * Produces alerts or logs results

**Agents implemented:**

* **Agent 1:** User spending behavior anomaly detection
* **Agent 2:** Velocity + transaction amount scoring

**Key design points:**

* Each agent runs as a **standalone Kafka consumer**
* Agents use **separate consumer groups**
* Failure of one agent does not affect others
* New agents can be added without touching PostgreSQL

---

## Part 3 — Architecture Discussion

### Resource Efficiency

* OLTP database is protected from analytical load
* Kafka efficiently handles high-throughput ingestion
* Consumers scale horizontally
* In-memory state kept bounded (sliding windows, capped history)

### Operability

* Clear separation of responsibilities
* Kafka offsets allow replay and recovery
* Easy to monitor lag, throughput, and consumer health
* Fault isolation between producers and consumers

### Maintainability

* Fraud logic is isolated per agent
* Each agent can evolve independently
* Supports different fraud models and heuristics
* Enables gradual rollout of new detection strategies

### Deployment Complexity

* Higher than simple batch or JDBC polling
* Requires Kafka, Kafka Connect, and Debezium
* Complexity justified by scale and real-time requirements

### Performance & Scalability

* Supports hundreds of thousands of events per second
* Low latency compared to batch ingestion
* Scales with:

  * More Kafka partitions
  * More consumer instances
* Handles increasing data volume without degrading OLTP performance

---

## Part 4 — Comparison with Spark JDBC (Previous Exercise)

### CDC + Kafka (This Architecture)

* Near real-time processing
* Event-driven and continuous
* Multiple independent consumers
* Low latency
* Better suited for fraud detection
* More complex infrastructure

### Spark JDBC Polling

* Batch-oriented
* Higher latency
* Heavy load on PostgreSQL
* Less suitable for real-time alerts
* Simpler to deploy
* Better for large analytical batch jobs

**Conclusion:**

* **Kafka + Debezium** is superior for real-time, high-scale fraud detection
* **Spark JDBC** is better suited for offline analytics and batch processing