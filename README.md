# Serverless Event-Driven Cloud Application Deployment Framework Using Python for Real-Time Data Processing and Dynamic Auto-Scaling

## 1. Project overview
This academic and demonstrative project implements a **real-time, event-driven, serverless** data processing framework on **AWS**.

It demonstrates how IoT-like events can be:
- **Ingested in real time** (API Gateway → Lambda)
- **Buffered** (SQS)
- **Routed by priority** (Lambda-based router)
- **Batch-processed adaptively** (dynamic batching)
- **Executed serverlessly** (Python AWS Lambda)
- **Enriched with state** (DynamoDB state table)
- **Auto-scaled dynamically** (CloudWatch-driven controller adjusting concurrency)
- **Observed visually** (React dashboard + charts)
- **Streamed live** to the UI (API Gateway WebSocket + broadcast Lambda)

This work is **intended for academic evaluation and classroom demonstration**. It does **not** claim production-grade reliability, security hardening, or cost optimization. The emphasis is **architectural clarity**, **traceability**, and **measurable behavior under load**.

---

## 2. Problem statement
Modern real-time applications (IoT, telemetry, monitoring, clickstreams) generate bursts of events.
A cloud system must:
- handle spikes without manual provisioning,
- keep latency low,
- avoid overload (backpressure),
- and provide transparent observability.

This project presents a **serverless event-driven deployment framework** that is suitable for academic review because it explicitly illustrates:
- queue-based buffering,
- priority routing,
- adaptive batching,
- dynamic auto-scaling,
- stateful serverless processing,
- and real-time visualization.

---

## 3. Base paper reference (IEEE)
**ScalaSSC – CCGrid 2025 (IEEE)**
- Reference used as an academic inspiration for *serverless scheduling, scaling, and execution visibility*.
- This implementation is a **Python + AWS** educational adaptation.

### 3.1 Framework contribution relative to the base paper
This repository should be interpreted as a **framework-style demonstrator** rather than a re-implementation of ScalaSSC.
The primary contributions are:
- a concrete **AWS service mapping** of an event-driven serverless pipeline (API Gateway, SQS, Lambda, DynamoDB, CloudWatch),
- an explicit **end-to-end traceable event flow** (ingest → buffer → route → batch → execute → store → visualize),
- a **dynamic behavior layer** (adaptive batching + scheduled scaling controller) designed for observation and discussion,
- a **real-time visualization layer** (WebSocket live stream + charts) that makes system behavior reviewable.

The purpose is to support **learning outcomes** (architecture comprehension, trade-off discussion, and reproducible experiments) rather than to claim optimal scheduling or production efficiency.

(Place your formal citation here in your report format.)

---

## 4. High-level architecture

### 4.1 Event flow (fixed, no re-enqueue loop)
```
Event Source Simulator (local Python)
  → API Gateway HTTP API
    → EventIngestion Lambda
      → IngressQueue (SQS)            [NEW: separates ingestion from routing]
        → EventRouter Lambda
          → DefaultQueue (SQS) OR HighPriorityQueue (SQS)
            → AdaptiveBatcher Lambda
              → ExecutionEngine Lambda
                → ResultsTable (DynamoDB)
                → (optional) StatefulProcessor Lambda → StateTable (DynamoDB)

Additionally:
- EventIngestion and ExecutionEngine broadcast to WebSocket clients via WsBroadcast Lambda.
- Metrics are published to CloudWatch and retrieved by Metrics API for the dashboard.
- AutoScalingController runs on a schedule and adjusts Reserved Concurrency.
```

### 4.2 Why add an IngressQueue?
Without a dedicated ingress queue, a common failure mode in queue-driven designs is that the routing component both **consumes** and **publishes** to the same queue. This can unintentionally create a **re-enqueue loop**, duplicate processing, and unstable backlog metrics.

The introduced **IngressQueue** provides a clean separation of concerns:
- **Ingestion isolation:** the ingestion Lambda writes only to IngressQueue, which represents “events accepted by the system.”
- **Routing safety:** the router reads only from IngressQueue and writes only to downstream queues.
- **Metric interpretability:** backlog signals become easier to interpret because each queue has a distinct role (ingress vs processing).
- **Academic traceability:** reviewers can evaluate each stage independently (where delay accumulates, where prioritization occurs).

---

## 5. AWS service mapping table
| Requirement | AWS Service | Where used |
|---|---|---|
| Event ingestion endpoint | API Gateway (HTTP API) | `/events` |
| Real-time updates to UI | API Gateway (WebSocket API) | `$connect`, `$disconnect`, broadcast |
| Serverless compute | AWS Lambda (Python 3.11) | all backend modules |
| Buffering/backpressure | Amazon SQS | `IngressQueue`, `DefaultQueue`, `HighPriorityQueue` |
| Stateful storage | DynamoDB | `StateTable` |
| Results storage | DynamoDB | `ResultsTable` |
| Config storage | DynamoDB | `ConfigTable` |
| Connection registry | DynamoDB | `ConnectionsTable` |
| Metrics | CloudWatch Metrics | published by batcher/executor/state/scaler |
| Logs + queries | CloudWatch Logs Insights | `/logs` endpoint |
| Permissions | IAM roles/policies | minimal SAM managed policies |

---

## 6. Repository structure
```
/backend
  /src
    /common
    /functions
  /tools
  requirements.txt

/frontend
  /src
  package.json

/infrastructure
  template.yaml
  NOTES.md

/config
  deployment_config.json

README.md
```

---

## 7. Backend modules (12 required) — module-wise explanation

> Note: Some “modules” are implemented as Lambdas, some as AWS resources, and some as local tools.

### Module 1 — Event Source Simulator
- **File:** `backend/tools/event_source_simulator.py`
- **What it does:** Generates synthetic IoT events and posts them to the ingestion endpoint.
- **Why it exists (academic justification):** Provides a controlled workload to reproduce experiments (low rate vs bursty traffic) and observe scaling/batching behavior.

### Module 2 — Event Ingestion Service
- **File:** `backend/src/functions/event_ingestion/app.py`
- **AWS:** API Gateway HTTP API → Lambda
- **What it does:**
  - Validates/normalizes event structure
  - Pushes events to **IngressQueue**
  - Broadcasts to WebSocket (for live event stream page)
- **Why it exists (academic justification):** Demonstrates the boundary between external producers and internal event buffering, and provides an observable “ingestion” stage.

### Module 3 — Event Queue Manager
- **AWS:** SQS
- **Queues:** `IngressQueue`, `DefaultQueue`, `HighPriorityQueue`
- **What it does:** Buffers incoming workload and smooths traffic spikes.
- **Why it exists (academic justification):** SQS is used as the explicit backpressure mechanism, enabling repeatable measurement of queue depth vs processing throughput.

### Module 4 — Event Router
- **File:** `backend/src/functions/event_router/app.py`
- **Trigger:** IngressQueue (SQS event)
- **What it does:** Routes events by priority:
  - `high` → HighPriorityQueue
  - else → DefaultQueue
- **Why it exists (academic justification):** Enables discussion of prioritization policies and their observable impact on latency and backlog.

### Module 5 — Adaptive Batching Engine
- **File:** `backend/src/functions/adaptive_batcher/app.py`
- **Trigger:** DefaultQueue + HighPriorityQueue
- **What it does:**
  - Chooses an effective batch size (demo logic)
  - Invokes ExecutionEngine asynchronously
  - Publishes batching metrics to CloudWatch
- **Why it exists (academic justification):** Demonstrates how batching trades off per-invocation overhead vs end-to-end latency, and how those effects can be visualized.

### Module 6 — Serverless Execution Engine
- **File:** `backend/src/functions/execution_engine/app.py`
- **What it does:**
  - Applies a demo “user-defined function” to events
  - Stores processed outputs in DynamoDB ResultsTable
  - Publishes execution metrics
  - Broadcasts processed results via WebSocket
- **Why it exists (academic justification):** Represents the compute stage and provides measurable throughput/latency metrics for evaluation.

### Module 7 — Stateful Processing Layer
- **File:** `backend/src/functions/stateful_processor/app.py`
- **What it does:** Maintains per-device state in DynamoDB (e.g., total events, last-seen timestamp).
- **Why it exists (academic justification):** Demonstrates how state can be maintained in an otherwise stateless serverless runtime, supporting discussion of consistency and data modeling.

### Module 8 — Dynamic Auto-Scaling Controller
- **File:** `backend/src/functions/autoscaling_controller/app.py`
- **Trigger:** EventBridge schedule (`rate(1 minute)`)
- **What it does:**
  - Reads total SQS backlog (Ingress + Default + High)
  - Computes desired Reserved Concurrency
  - Updates ExecutionEngine reserved concurrency
  - Publishes scaling metrics
- **Why it exists (academic justification):** Provides a transparent, inspectable scaling decision path that can be graphed and explained during review.

### Module 9 — Monitoring & Metrics Collector
- **File:** `backend/src/functions/metrics_api/app.py`
- **What it does:** Reads CloudWatch metrics for the dashboard.
- **Why it exists (academic justification):** Establishes a measurable evaluation layer (latency, throughput, batch size, backlog, concurrency).

### Module 10 — Logging & Alerting Module
- **File:** `backend/src/functions/logs_api/app.py`
- **What it does:** Starts and reads CloudWatch Logs Insights queries (demo log analytics).
- **Why it exists (academic justification):** Enables reviewers to correlate functional behavior (events processed) with operational evidence (errors/warnings).

### Module 11 — Result Processing & Storage
- **File:** `backend/src/functions/results_api/app.py`
- **What it does:** Fetches stored processed results from DynamoDB.
- **Why it exists (academic justification):** Separates “compute output” from “visualization,” allowing independent verification of processing correctness.

### Module 12 — Deployment & Configuration Manager
- **File:** `backend/src/functions/config_api/app.py`
- **What it does:**
  - GET active config
  - POST updated config (stored in DynamoDB)
- **Why it exists (academic justification):** Enables controlled parameter changes (thresholds, limits) during demonstration, supporting experimental comparison.

---

## 8. Frontend dashboard (12 required pages) — page-wise explanation
The frontend is a React dashboard that uses:
- HTTP polling (near-real-time)
- WebSocket live feed (real-time stream + processed results)
- Charts via `recharts`

### Page 1 — System Overview Dashboard
- KPIs for queue depth + execution latency
- Shows WebSocket connection status
- **Justification:** Provides a single “at a glance” view suitable for reviewers to understand system health and activity.

### Page 2 — Real-Time Event Stream
- Displays live ingested events from WebSocket
- **Justification:** Demonstrates true real-time delivery from AWS WebSocket → browser, not only periodic polling.

### Page 3 — Event Ingestion Monitor
- Lets you POST a test event to `/events`
- **Justification:** Provides a simple controlled input channel for repeatable tests without external IoT hardware.

### Page 4 — Queue Depth Visualization
- Bar chart showing visible/in-flight messages from `/queues`
- **Justification:** Makes backpressure and buffering observable and measurable.

### Page 5 — Adaptive Batching Visualization
- Graphs `AdaptiveBatchSize` and `BatchDispatchCount` (CloudWatch)
- **Justification:** Links batching policy to measurable system behavior.

### Page 6 — Auto-Scaling Activity Dashboard
- Graphs `DesiredReservedConcurrency` and `TotalQueueDepth`
- **Justification:** Makes scaling decisions explicit and reviewable rather than implicit “autoscaling magic.”

### Page 7 — Serverless Execution View
- Graphs processed throughput + execution latency
- **Justification:** Supports evaluation of compute-stage performance under variable load.

### Page 8 — Stateful Data Visualization
- Table of device state from DynamoDB via `/state`
- **Justification:** Demonstrates stateful serverless patterns and validates that state updates occur.

### Page 9 — Performance Metrics Dashboard
- Combined metrics view for latency/batching/state updates
- **Justification:** Consolidates key metrics into an evaluation-oriented dashboard section for academic discussion.

### Page 10 — Logs & Alerts View
- Runs Logs Insights queries via `/logs`
- **Justification:** Provides operational evidence for failures and supports debugging during demonstrations.

### Page 11 — Processed Results View
- Live processed results via WebSocket + stored results via `/results`
- **Justification:** Separates “live stream” from “durable storage,” enabling reviewers to verify both real-time and stored outputs.

### Page 12 — Deployment Configuration Page
- Edit JSON config via `/config`
- **Justification:** Enables controlled experiments by changing framework parameters without redeploying.

---

## 9. Real-time visualization behavior
- **WebSocket** delivers:
  - `type=ingest` messages from EventIngestion Lambda
  - `type=processed` messages from ExecutionEngine Lambda
- **HTTP polling** provides stability:
  - metrics (`/metrics`), queue depth (`/queues`), results (`/results`), state (`/state`)

---

## 10. Setup instructions (step-by-step)

### 10.1 Prerequisites
- AWS Account
- AWS CLI configured (`aws configure`)
- AWS SAM CLI installed
- Node.js 18+
- Python 3.11+ (for local tools)

### 10.2 Deploy backend to AWS using SAM
From the `infrastructure/` folder:
1. Build:
   - `sam build`
2. Deploy (guided):
   - `sam deploy --guided`
3. After deploy, note the Outputs:
   - `HttpApiUrl`
   - `WebSocketUrl`

### 10.3 Run event simulator locally
- Install Python deps:
  - `pip install -r backend/requirements.txt`
- Run:
  - `python backend/tools/event_source_simulator.py --url <HttpApiUrl>/events --eps 5 --device device-1`

### 10.4 Run frontend locally
From `frontend/`:
1. Install:
   - `npm install`
2. Create `.env`:
   - `VITE_HTTP_API_BASE=<HttpApiUrl>`
   - `VITE_WS_URL=<WebSocketUrl>`
3. Start:
   - `npm run dev`

---

## 11. Demo walkthrough (for presentation)
1. Deploy backend with SAM.
2. Run frontend (`npm run dev`).
3. Open:
   - System Overview → confirm queue depth changes
4. Start simulator at low EPS (e.g., 2) and observe:
   - near-empty queues
   - low latency
   - small batch sizes
5. Increase EPS (e.g., 30) and observe:
   - queue depth grows
   - adaptive batch size increases
   - scaling controller increases reserved concurrency
6. Open Real-Time Event Stream + Processed Results to show live WebSocket updates.

---

## 12. Screenshots placeholders
Add screenshots here for your report:
- `docs/screenshots/01-overview.png`
- `docs/screenshots/02-stream.png`
- `docs/screenshots/06-autoscaling.png`
- `docs/screenshots/12-config.png`

---

## 13. Academic justification
This project is suitable for academic review because:
- It maps each conceptual module to a concrete AWS serverless component.
- It provides measurable metrics (latency, throughput, queue depth, concurrency).
- It visualizes adaptive behavior (batch size + scaling decisions).
- It is reproducible and explainable.

---

## 14. Limitations (explicitly not production-ready)
- Scaling controller is simplified and uses Reserved Concurrency directly.
- IAM policies are intentionally minimal and suitable for demonstration; they are not a hardened least-privilege design.
- No authentication/authorization layer for the dashboard.
- Polling-based dashboard metrics (not a streaming metrics pipeline).
- DynamoDB scan used for demo simplicity.

---

## 15. Future enhancements
- Replace polling with a streaming metrics pipeline (Kinesis/WebSocket push).
- Add EventBridge-based routing rules.
- Add authentication (Cognito) for dashboard.
- Add per-event trace visualization (X-Ray UI integration).
- Add DLQs for SQS and structured alerting.
