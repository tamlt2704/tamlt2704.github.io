# Chapter 15: Observability

[← Ch 14](chapter-14-deployments.md) | [Ch 16 →](chapter-16-sharding.md)

---

## The Crisis

Thursday night. Podcast is tomorrow.

**Omar** (Slack, 9:30 PM):
> I just realized: if something goes wrong during the podcast, how do we know? Our monitoring shows CPU, memory, disk. But if uploads are failing for users in Brazil, we won't see it until they tweet about it.

**Sana**:
> Last week a query was slow for 20 minutes. We only found out because Kai noticed the frontend was laggy. We have no alerting on application-level metrics.

**Amir**:
> During the podcast, we need to know within 60 seconds if anything is degraded. Not 20 minutes. Not when Twitter tells us.

**You**:
> We need three things: metrics (what's happening), traces (why it's slow), and logs (what went wrong). And we need alerts that fire before users notice.

---

## Concept: The Three Pillars of Observability

```
┌─────────────────────────────────────────────────────────┐
│                    OBSERVABILITY                          │
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   METRICS    │  │    TRACES    │  │     LOGS     │  │
│  │              │  │              │  │              │  │
│  │ "What is     │  │ "Why is this │  │ "What        │  │
│  │  happening?" │  │  request     │  │  happened?"  │  │
│  │              │  │  slow?"      │  │              │  │
│  │ Counters,    │  │ Distributed  │  │ Structured   │  │
│  │ gauges,      │  │ request      │  │ events with  │  │
│  │ histograms   │  │ flow         │  │ context      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Concept: Metrics (Prometheus)

Metrics are numeric measurements over time.

### Metric Types

| Type | Use Case | Example |
|------|----------|---------|
| **Counter** | Things that only go up | Total requests, errors, bytes transferred |
| **Gauge** | Current value (up or down) | Active connections, queue depth, CPU % |
| **Histogram** | Distribution of values | Request latency (p50, p95, p99) |

### GhostDrop Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# Counters
requests_total = Counter(
    'ghostdrop_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

uploads_total = Counter(
    'ghostdrop_uploads_total',
    'Total file uploads',
    ['status']  # success, failed, rejected
)

# Histograms
request_duration = Histogram(
    'ghostdrop_request_duration_seconds',
    'Request latency',
    ['endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

upload_size = Histogram(
    'ghostdrop_upload_size_bytes',
    'Upload file sizes',
    buckets=[1e4, 1e5, 1e6, 1e7, 1e8, 1e9]  # 10KB to 1GB
)

# Gauges
active_connections = Gauge(
    'ghostdrop_active_connections',
    'Current active connections'
)

queue_depth = Gauge(
    'ghostdrop_queue_depth',
    'Messages in processing queue'
)

# Middleware to record metrics
@app.middleware("http")
async def metrics_middleware(request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    
    requests_total.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    request_duration.labels(endpoint=request.url.path).observe(duration)
    
    return response
```

---

## Concept: Traces (Distributed Tracing)

A trace follows a single request across all services.

```
User uploads file → trace ID: abc-123

┌─ API Gateway (2ms) ─────────────────────────────────────────────┐
│  ┌─ Auth Service (15ms) ──┐                                     │
│  │  Validate JWT          │                                     │
│  └────────────────────────┘                                     │
│  ┌─ Upload Service (2,340ms) ──────────────────────────────────┐│
│  │  ┌─ S3 PutObject (2,100ms) ────────────────────────────┐   ││
│  │  │  Upload 50MB file                                     │   ││
│  │  └──────────────────────────────────────────────────────┘   ││
│  │  ┌─ PostgreSQL INSERT (12ms) ──┐                            ││
│  │  │  Save file metadata          │                            ││
│  │  └─────────────────────────────┘                            ││
│  │  ┌─ SQS SendMessage (45ms) ───┐                            ││
│  │  │  Queue processing job        │                            ││
│  │  └─────────────────────────────┘                            ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
Total: 2,402ms — S3 upload is 87% of the time
```

### Implementation with OpenTelemetry

```python
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.botocore import BotocoreInstrumentor

# Auto-instrument everything
FastAPIInstrumentor.instrument_app(app)
SQLAlchemyInstrumentor().instrument()
RedisInstrumentor().instrument()
BotocoreInstrumentor().instrument()

# Custom spans for business logic
tracer = trace.get_tracer("ghostdrop")

@app.post("/api/upload")
async def upload_file(file: UploadFile):
    with tracer.start_as_current_span("upload_file") as span:
        span.set_attribute("file.size", file.size)
        span.set_attribute("file.type", file.content_type)
        
        with tracer.start_as_current_span("validate_quota"):
            check_quota(user)
        
        with tracer.start_as_current_span("upload_to_s3"):
            s3_key = await upload_to_s3(file)
            span.set_attribute("s3.key", s3_key)
        
        with tracer.start_as_current_span("save_metadata"):
            file_record = save_to_db(s3_key, file.filename)
        
        return {"file_id": file_record.id}
```

---

## Concept: Structured Logs

Unstructured logs are useless at scale. Structured logs are searchable.

```python
# BAD: Unstructured
logger.info(f"User {user_id} uploaded file {filename} ({size} bytes)")

# GOOD: Structured (JSON)
logger.info("file_uploaded", extra={
    "user_id": user_id,
    "file_id": file_id,
    "filename": filename,
    "size_bytes": size,
    "duration_ms": duration,
    "trace_id": get_current_trace_id(),
    "region": request.headers.get("cf-ipcountry"),
})
```

Output:
```json
{
  "timestamp": "2024-01-18T14:23:45.123Z",
  "level": "info",
  "message": "file_uploaded",
  "user_id": "usr_4821",
  "file_id": "file_abc123",
  "filename": "report.pdf",
  "size_bytes": 5242880,
  "duration_ms": 2340,
  "trace_id": "abc-123-def-456",
  "region": "JP"
}
```

Now you can query: "Show me all uploads from Japan that took > 5 seconds in the last hour."

---

## Concept: SLOs, SLIs, and SLAs

| Term | Definition | GhostDrop Example |
|------|-----------|-------------------|
| **SLI** (Indicator) | The metric you measure | Upload success rate, p99 latency |
| **SLO** (Objective) | Your internal target | 99.9% upload success, p99 < 3s |
| **SLA** (Agreement) | Promise to customers (with penalties) | 99.5% uptime or credits |

### GhostDrop's SLOs

| Service | SLI | SLO | Measurement |
|---------|-----|-----|-------------|
| Uploads | Success rate | 99.9% | Successful uploads / total attempts |
| Downloads | p99 latency | < 500ms | Time to first byte |
| API | Availability | 99.95% | Successful responses / total requests |
| Share links | Resolution time | < 200ms | Time to resolve link to file |

### Error Budget

```
SLO: 99.9% availability
Monthly minutes: 43,200
Allowed downtime: 43.2 minutes/month (error budget)

Used this month: 4 minutes (the deploy outage)
Remaining budget: 39.2 minutes

If budget is exhausted: freeze deploys, focus on reliability
```

---

## Concept: Alerting

### Alert on SLOs, Not Symptoms

```yaml
# BAD: Alert on CPU (symptom)
- alert: HighCPU
  expr: cpu_usage > 80%
  # This fires constantly and doesn't mean users are affected

# GOOD: Alert on SLO breach (user impact)
- alert: UploadSuccessRateLow
  expr: |
    sum(rate(uploads_total{status="success"}[5m])) /
    sum(rate(uploads_total[5m])) < 0.999
  for: 2m
  labels:
    severity: critical
  annotations:
    summary: "Upload success rate below 99.9% for 2 minutes"
```

### Alert Severity Levels

| Severity | Criteria | Response | Example |
|----------|----------|----------|---------|
| **Critical** | Users impacted NOW | Page on-call, immediate response | Upload success < 99% |
| **Warning** | Approaching SLO breach | Investigate within 1 hour | p99 latency > 2s |
| **Info** | Notable but not urgent | Review next business day | Queue depth > 1000 |

---

## GhostDrop: Podcast Day Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│  GHOSTDROP — PODCAST DAY WAR ROOM                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Active Users: 847,231    Requests/sec: 12,450              │
│  Error Rate: 0.02%        Upload Success: 99.97%            │
│                                                              │
│  ┌─ Latency (p99) ──────────────────────────────────────┐  │
│  │  API:      45ms  ████░░░░░░░░░░░░░░░░  (target: 200) │  │
│  │  Upload:  2.1s   ████████████░░░░░░░░  (target: 5s)  │  │
│  │  Download: 35ms  ██░░░░░░░░░░░░░░░░░░  (target: 500) │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌─ Infrastructure ─────────────────────────────────────┐  │
│  │  App Servers: 8/8 healthy    DB CPU: 34%             │  │
│  │  Redis Hit Rate: 89%         Queue Depth: 47         │  │
│  │  CDN Hit Rate: 94%           Replica Lag: 12ms       │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌─ Error Budget ───────────────────────────────────────┐  │
│  │  Monthly: 43.2 min allowed │ Used: 4.0 min           │  │
│  │  Remaining: ████████████████████████████░░ 39.2 min  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Concept: On-Call for Podcast Day

```
Rotation:
  Primary:   Omar (SRE) — infrastructure, scaling
  Secondary: Sana (Backend) — application issues
  Escalation: Amir (CTO) — business decisions

Runbooks:
  - "Upload success < 99%"  → Check S3, check workers, check DB
  - "Latency spike"         → Check replica lag, cache hit rate
  - "Traffic 2x expected"   → Auto-scale triggered? Check limits
  - "Database CPU > 80%"    → Enable query throttling, add replica

Communication:
  - War room Slack channel: #podcast-day-ops
  - Status page: status.ghostdrop.io (auto-updates from alerts)
  - Escalation: PagerDuty → Slack → Phone call after 5 min
```

---

## Tradeoffs

| Decision | Gain | Cost |
|----------|------|------|
| Prometheus + Grafana | Industry standard, flexible | Self-hosted ops (or use managed) |
| Distributed tracing | Find slow spans across services | 5-10% performance overhead |
| Structured logging | Searchable, queryable | More verbose, storage cost |
| SLO-based alerting | Alert on user impact, not noise | Must define good SLIs |

---

## Why Not Just...

**"Why not just use CloudWatch for everything?"**
CloudWatch is fine for AWS infrastructure metrics. But application-level metrics (upload success rate, p99 by endpoint) need custom instrumentation. And CloudWatch's query language is limited compared to PromQL.

**"Why not alert on every error?"**
Alert fatigue. If you get 50 alerts/day, you ignore them all. Alert on SLO breaches — things that actually affect users. Individual errors are noise; error *rates* are signal.

**"Why not just check the dashboard manually?"**
During the podcast, you'll be watching. But at 3 AM on a Tuesday? Alerts catch problems when humans aren't watching. Dashboards are for investigation, not detection.

---

## Exercise

During the podcast, traffic spikes 5x. The dashboard shows:
- Upload success rate: 99.2% (below 99.9% SLO)
- p99 latency: 4.8s (below 5s target, but close)
- Queue depth: 12,000 (normally < 100)
- Worker CPU: 98%

1. What's the root cause?
2. What's your immediate action?
3. What's the 5-minute fix vs the proper fix?

<details>
<summary>Hint</summary>

Root cause: Workers can't keep up with the queue (CPU maxed). Uploads succeed (S3 + DB) but post-processing (virus scan, thumbnails) is backlogged. The 0.8% failures are likely timeouts on quota checks that depend on processing completion. Immediate action: auto-scale workers (if not already triggered). 5-minute fix: manually scale workers to 20. Proper fix: separate virus scanning (CPU-heavy) from thumbnail generation, scale independently.
</details>

---

## Quick Reference

| Term | Definition |
|------|-----------|
| **Metrics** | Numeric measurements over time (counters, gauges, histograms) |
| **Traces** | End-to-end request flow across services |
| **Structured Logs** | Machine-parseable log entries (JSON) |
| **SLI** | Service Level Indicator — what you measure |
| **SLO** | Service Level Objective — your internal target |
| **SLA** | Service Level Agreement — promise to customers |
| **Error Budget** | Allowed downtime before freezing changes |
| **p99 Latency** | 99th percentile response time |
| **On-Call** | Engineer responsible for responding to alerts |
| **Runbook** | Step-by-step guide for handling specific incidents |

---

## What Breaks Next

Observability is in place. Dashboards, alerts, traces, structured logs. You can see everything.

The podcast happens. Traffic spikes to 8M users. The system holds — mostly. But the database is at 78% CPU again. Read replicas help with reads, but writes are growing. Every upload writes metadata. Every share creates a record. The single primary database is becoming the bottleneck again.

"We can't scale writes with replicas," Sana says. "We need to split the database itself."

You need sharding.

[← Ch 14](chapter-14-deployments.md) | [Ch 16 →](chapter-16-sharding.md)
