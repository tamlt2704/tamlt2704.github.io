# Chapter 20: Launch Day

[← Ch 19](chapter-19-realtime.md)

---

## The Crisis (That Didn't Happen)

It's Friday. 6:00 PM. The podcast goes live at 7:00 PM Eastern.

**Mia** (in the war room, pacing):
> One hour. Are we ready?

**Omar** (at his laptop, three monitors):
> All systems green. Auto-scaling policies active. CDN warmed. Database headroom at 60%. I've been running load tests all day.

**Sana**:
> Feature flags are set. Kill switches ready. If anything non-critical starts failing, we shed load instantly.

**Kai**:
> Frontend is cached at the CDN. Static assets won't even hit our servers. The only dynamic calls are uploads, downloads, and API queries.

**You** (standing at the whiteboard with the final architecture diagram):
> Let's walk through the capacity plan one more time.

---

## Concept: Capacity Planning

### Traffic Estimation

```
Current state:
  - 12M registered users
  - 1.2M DAU (daily active users)
  - Peak concurrent: 180K users
  - Peak requests/sec: 12,000

Podcast impact (estimated):
  - 2M new signups in 48 hours
  - 3x peak concurrent: 540K users
  - 3x peak requests/sec: 36,000
  - Upload spike: 5x normal (new users trying the product)
```

### Resource Requirements

| Component | Current | Podcast Target | Headroom |
|-----------|---------|---------------|----------|
| App servers | 8 | 24 (auto-scale) | 3x |
| WebSocket servers | 12 | 20 | 1.7x |
| Database (write) | 3 shards | 3 shards | 60% capacity |
| Database (read) | 6 replicas | 9 replicas (auto) | 3x |
| Redis cache | 2 nodes | 4 nodes | 2x |
| Workers (processing) | 10 | 30 (auto-scale) | 3x |
| CDN | Unlimited | Unlimited | ∞ |

### Cost Estimate for Podcast Week

```
Normal monthly cost:     $4,200/mo
Podcast week (scaled):   $8,500/mo (temporary)
After stabilization:     $5,800/mo (new baseline)

Cost per user per month: $0.00048
Revenue per user:        $0.12 (freemium + pro upgrades)
Margin:                  Healthy
```

---

## Concept: Load Testing

### Tools

| Tool | Language | Best For |
|------|----------|----------|
| **k6** | JavaScript | Developer-friendly, CI integration |
| **Locust** | Python | Custom scenarios, distributed |
| **Gatling** | Scala | High throughput, detailed reports |
| **wrk** | C | Raw HTTP benchmarking |

### GhostDrop Load Test (k6)

```javascript
// load_test.js — simulates podcast traffic pattern
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

export const options = {
  scenarios: {
    // Ramp up like podcast traffic
    podcast_spike: {
      executor: 'ramping-vus',
      startVUs: 100,
      stages: [
        { duration: '5m', target: 1000 },   // Podcast starts
        { duration: '10m', target: 5000 },  // Word spreads
        { duration: '30m', target: 10000 }, // Peak
        { duration: '15m', target: 3000 },  // Settling
        { duration: '10m', target: 500 },   // After
      ],
    },
  },
  thresholds: {
    http_req_duration: ['p(99)<3000'],  // p99 < 3s
    errors: ['rate<0.01'],              // Error rate < 1%
  },
};

export default function () {
  const BASE_URL = 'https://staging.ghostdrop.io';
  
  // 40% of traffic: Browse/download (read-heavy)
  if (Math.random() < 0.4) {
    const res = http.get(`${BASE_URL}/api/files`);
    check(res, { 'file list 200': (r) => r.status === 200 });
    errorRate.add(res.status !== 200);
  }
  
  // 30% of traffic: View shared links
  else if (Math.random() < 0.7) {
    const res = http.get(`${BASE_URL}/s/test-link-${Math.floor(Math.random() * 1000)}`);
    check(res, { 'share link resolves': (r) => r.status === 200 || r.status === 302 });
    errorRate.add(res.status >= 500);
  }
  
  // 20% of traffic: Sign up (new users from podcast)
  else if (Math.random() < 0.9) {
    const res = http.post(`${BASE_URL}/api/auth/register`, JSON.stringify({
      email: `loadtest+${Date.now()}${Math.random()}@test.com`,
      password: 'TestPass123!',
    }), { headers: { 'Content-Type': 'application/json' } });
    check(res, { 'signup success': (r) => r.status === 201 });
    errorRate.add(res.status >= 500);
  }
  
  // 10% of traffic: Upload files
  else {
    const file = open('test_file_1mb.bin', 'b');
    const res = http.post(`${BASE_URL}/api/upload`, { file: http.file(file, 'test.bin') });
    check(res, { 'upload success': (r) => r.status === 200 || r.status === 201 });
    errorRate.add(res.status >= 500);
  }
  
  sleep(Math.random() * 2);
}
```

### Load Test Results

```
Running load test: podcast_spike scenario
  Peak VUs: 10,000
  Duration: 70 minutes

Results:
  ✓ http_req_duration p99 < 3000ms ... 2,847ms (PASS)
  ✓ error rate < 1% .................. 0.3% (PASS)
  
  Requests/sec (peak): 34,200
  Upload success rate: 99.7%
  Download p99 latency: 89ms
  API p99 latency: 245ms
  
  Auto-scaling triggered:
    App servers: 8 → 22 (at t+8min)
    Workers: 10 → 28 (at t+12min)
    Read replicas: 6 → 9 (at t+15min)
```

---

## The Production Checklist

### 24 Hours Before

```
□ Load test passed at 3x expected traffic
□ Auto-scaling policies verified (min/max/cooldown)
□ CDN cache warmed (popular assets pre-fetched)
□ Database vacuumed and analyzed
□ Redis memory headroom > 40%
□ Feature flags configured (kill switches ready)
□ Rollback plan documented and tested
□ On-call rotation confirmed (Omar primary, Sana secondary)
□ Status page ready (status.ghostdrop.io)
□ War room Slack channel created (#podcast-launch)
```

### 1 Hour Before

```
□ All dashboards open on war room monitors
□ PagerDuty escalation policy verified
□ No deploys in the last 2 hours
□ Database connection pool headroom verified
□ S3 bucket limits checked (no throttling risk)
□ DNS TTL lowered to 60s (for quick failover)
□ Team in war room (or on Slack)
```

### During the Podcast

```
□ Monitor error rate (< 0.5%)
□ Monitor p99 latency (< 3s)
□ Monitor auto-scaling (are new instances launching?)
□ Monitor queue depth (< 1000)
□ Monitor database CPU (< 70%)
□ Monitor signup rate (expected vs actual)
□ Communicate status every 15 minutes in #podcast-launch
```

### If Something Goes Wrong

```
Severity 1 (> 5% error rate):
  1. Check auto-scaling — are instances launching?
  2. Enable kill switches for non-critical features
  3. Check database — connection pool exhausted?
  4. Check Redis — memory full? Evictions?
  5. If unrecoverable: activate maintenance page

Severity 2 (degraded but functional):
  1. Identify the bottleneck (metrics/traces)
  2. Scale the bottleneck manually if auto-scale is slow
  3. Communicate ETA to team
  4. Post-incident review after podcast
```

---

## What We Built: The Final Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         GHOSTDROP ARCHITECTURE                        │
│                         12M users, 36K req/sec                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────┐     ┌─────────────┐     ┌──────────────────────────┐  │
│  │  Users  │────→│  CloudFront │────→│  Static Assets (S3)      │  │
│  │ (global)│     │  (CDN)      │     └──────────────────────────┘  │
│  └────┬────┘     └──────┬──────┘                                    │
│       │                  │                                           │
│       │           ┌──────┴──────┐                                    │
│       │           │  API Gateway │                                    │
│       │           │  (rate limit)│                                    │
│       │           └──────┬──────┘                                    │
│       │                  │                                           │
│       │    ┌─────────────┼─────────────┐                            │
│       │    │             │             │                             │
│       │    ▼             ▼             ▼                             │
│       │ ┌──────┐    ┌──────┐    ┌──────────┐                       │
│       │ │App×24│    │App×24│    │ WS ×12   │                       │
│       │ │Server│    │Server│    │ Servers  │                       │
│       │ └──┬───┘    └──┬───┘    └────┬─────┘                       │
│       │    │           │              │                              │
│       │    └─────┬─────┘              │                              │
│       │          │                    │                              │
│       │    ┌─────┴─────┐      ┌──────┴──────┐                      │
│       │    │   Redis    │      │ Redis Pub/Sub│                      │
│       │    │  (cache)   │      │ (real-time)  │                      │
│       │    └─────┬─────┘      └─────────────┘                      │
│       │          │                                                   │
│       │    ┌─────┴──────────────────────────┐                       │
│       │    │         PostgreSQL               │                       │
│       │    │  ┌────────┐┌────────┐┌────────┐│                       │
│       │    │  │Shard 0 ││Shard 1 ││Shard 2 ││                       │
│       │    │  │+ 3 repl││+ 3 repl││+ 3 repl││                       │
│       │    │  └────────┘└────────┘└────────┘│                       │
│       │    └─────────────────────────────────┘                       │
│       │                                                              │
│       │    ┌─────────────────────────────────┐                       │
│       │    │            Kafka                 │                       │
│       │    │  file.events │ share.events      │                       │
│       │    └──────────┬──────────────────────┘                       │
│       │               │                                              │
│       │    ┌──────────┼──────────────────────┐                       │
│       │    │          │          │           │                       │
│       │    ▼          ▼          ▼           ▼                       │
│       │ ┌──────┐ ┌──────┐ ┌────────┐ ┌──────────┐                  │
│       │ │Virus │ │Thumb │ │Notify  │ │Analytics │                  │
│       │ │Scan  │ │Gen   │ │Service │ │Service   │                  │
│       │ │×10   │ │×8    │ │×4      │ │×2        │                  │
│       │ └──────┘ └──────┘ └────────┘ └──────────┘                  │
│       │                                                              │
│       └──────────────────────────────────────────────────────────   │
│              ┌──────────────────────────────────┐                    │
│              │         S3 (File Storage)         │                    │
│              │  Unlimited. 11 nines durability.  │                    │
│              └──────────────────────────────────┘                    │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  OBSERVABILITY: Prometheus + Grafana + Jaeger + Structured   │    │
│  │  Logs + PagerDuty + SLO Dashboards                           │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## The Journey: From One Server to This

| Chapter | What Broke | What We Added |
|---------|-----------|---------------|
| 1 | CPU 97%, everything on one box | Identified bottleneck, planned horizontal |
| 2 | No redundancy | Load balancer (ALB) |
| 3 | Files on local disk | S3 + CloudFront |
| 4 | DB on app server | RDS (managed, Multi-AZ) |
| 5 | Every request hits DB | Redis caching |
| 6 | Uploads block workers | SQS + async workers |
| 7 | DB reads overwhelming | Read replicas |
| 8 | Monolith deploys 40 min | Service decomposition |
| 9 | Tokyo users: 800ms | CDN for static + dynamic |
| 10 | Bots hammering API | Rate limiting |
| 11 | Redis dies, cascade failure | Circuit breakers |
| 12 | Multi-step operations fail | Saga pattern, idempotency |
| 13 | Stale reads, inconsistency | Consistency models per feature |
| 14 | Deploys cause outages | Canary + feature flags |
| 15 | Can't see what's broken | Observability stack |
| 16 | Write bottleneck | Database sharding |
| 17 | Tight service coupling | Event-driven (Kafka) |
| 18 | Ugly share links | URL shortener, Snowflake IDs |
| 19 | No real-time updates | WebSockets + Pub/Sub |
| 20 | Will it hold? | Load testing + capacity planning |

---

## The Podcast

7:00 PM. The podcast goes live.

7:03 PM. Mia mentions GhostDrop. "Just upload and share. It's that simple."

7:05 PM. Traffic starts climbing.

```
7:05 PM:  Signups: 200/min    Requests: 15K/sec
7:15 PM:  Signups: 800/min    Requests: 24K/sec
7:30 PM:  Signups: 2,100/min  Requests: 34K/sec  ← Auto-scale triggers
7:45 PM:  Signups: 3,400/min  Requests: 41K/sec  ← Peak
8:00 PM:  Signups: 1,800/min  Requests: 32K/sec  ← Settling
```

**Omar** (8:15 PM):
> Peak was 41K req/sec. Error rate: 0.08%. p99 latency: 890ms at peak (within SLO). Auto-scaling worked perfectly. No pages. No incidents.

**Sana**:
> Zero data loss. All uploads processed. Queue peaked at 4,200 messages, drained in 8 minutes.

**Amir** (smiling):
> We did it.

**Mia** (from the podcast studio, texting):
> 🎉 Numbers look amazing. Drinks on me.

---

## Tradeoffs: The Full Picture

| What We Gained | What We Paid |
|---------------|-------------|
| 10M+ user capacity | $5,800/mo infrastructure (up from $200) |
| 99.95% availability | 20 components to monitor |
| Sub-100ms global latency | Eventual consistency in some features |
| Zero-downtime deploys | Complex deployment pipeline |
| Real-time features | 12 WebSocket servers |
| Horizontal scalability | Distributed systems complexity |

---

## Why Not Just...

**"Why not just use a PaaS (Heroku, Railway) and avoid all this?"**
PaaS works beautifully up to ~100K users. Beyond that, you hit platform limits, costs explode, and you need control over infrastructure decisions. GhostDrop outgrew PaaS at ~500K users.

**"Why not go serverless (Lambda + DynamoDB)?"**
Serverless is great for bursty, event-driven workloads. But GhostDrop has persistent WebSocket connections, needs PostgreSQL's relational model, and has predictable baseline traffic. Serverless cold starts would hurt upload latency.

**"Why not just throw money at bigger servers?"**
We tried. The biggest single server costs $20K/month and still can't handle 40K req/sec. Distributed architecture costs $5.8K/month and scales to 100K+ req/sec. Horizontal wins at scale.

---

## Exercise (Final)

You're designing the next phase: GhostDrop Enterprise. Requirements:
- Multi-tenant isolation (each company's data is separate)
- Compliance (data residency — EU data stays in EU)
- 99.99% SLA (not 99.95%)

1. How does multi-tenancy change the sharding strategy?
2. How do you implement data residency with the current architecture?
3. What's the difference between 99.95% and 99.99% in engineering terms?

<details>
<summary>Hint</summary>

1. Shard by tenant_id instead of (or in addition to) user_id. Large tenants get dedicated shards. Small tenants share shards. 2. Data residency: Deploy separate stacks per region (EU, US, APAC). Route users to their region's stack based on tenant config. Cross-region replication only for metadata, not file content. 3. 99.95% = 21.9 min downtime/month. 99.99% = 4.3 min downtime/month. Going from 99.95% to 99.99% requires: multi-region active-active, automated failover under 60 seconds, zero-downtime everything (including database maintenance). It's 5x harder and 3x more expensive.
</details>

---

## Quick Reference

| Term | Definition |
|------|-----------|
| **Capacity Planning** | Estimating resources needed for expected traffic |
| **Load Testing** | Simulating production traffic to find limits |
| **Auto-Scaling** | Automatically adding/removing resources based on demand |
| **War Room** | Dedicated space for monitoring during critical events |
| **Kill Switch** | Feature flag that instantly disables a feature |
| **Error Budget** | Allowed failures before freezing changes |
| **Runbook** | Step-by-step incident response guide |
| **Blast Radius** | Scope of impact when something fails |
| **Graceful Degradation** | Serving reduced functionality under stress |
| **Horizontal Scaling** | Adding more machines (vs bigger machines) |

---

## What's Next

The podcast is over. GhostDrop survived. 14M users and growing.

But the story doesn't end. Next challenges:
- **Multi-region** (active-active for true global low latency)
- **Machine learning** (smart file organization, duplicate detection)
- **Compliance** (GDPR, SOC2, data residency)
- **Cost optimization** (reserved instances, spot instances, right-sizing)
- **Team scaling** (from 4 engineers to 40 — how does architecture change?)

Every system design decision is a tradeoff. There's no perfect architecture — only the right architecture for your constraints today. The constraints will change. The architecture will evolve.

The whiteboard is never finished.

---

*"The best architectures are grown, not designed." — You, after surviving launch day.*

[← Ch 19](chapter-19-realtime.md)
