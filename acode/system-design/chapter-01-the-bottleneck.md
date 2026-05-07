# Chapter 1: The Bottleneck

[← Ch 0](chapter-00-overview.md) | [Ch 2 →](chapter-02-load-balancer.md)

---

## The Crisis

It's 7:14 AM. Your phone buzzes.

**Ops Omar** (Slack, 7:14 AM):
> Server CPU at 97%. Response times over 4 seconds. I've been up since 3 AM.

**Sana** (Slack, 7:16 AM):
> Upload endpoint is timing out. Users are retrying, which makes it worse.

**Kai** (Slack, 7:18 AM):
> Frontend is showing spinners everywhere. Users are tweeting screenshots.

You open Grafana. The single r5.2xlarge instance — 8 vCPUs, 64GB RAM — is drowning. But *what* is drowning it?

**Amir** (standing behind you, coffee in hand):
> "Before you fix anything, tell me what's actually broken. Is it CPU? Memory? Disk? Network? I don't want to throw money at the wrong thing."

---

## The Architecture (Before)

```
┌─────────────────────────────────────────────────────┐
│            Single EC2 Instance (r5.2xlarge)           │
│                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │  Django  │  │  Postgres │  │  Redis   │           │
│  │ 4 workers│  │  (local)  │  │ (local)  │           │
│  └──────────┘  └──────────┘  └──────────┘           │
│                                                       │
│  CPU: 97%  │  RAM: 58GB/64GB  │  Disk I/O: 89%      │
│  Network: 2.1 Gbps / 5 Gbps cap                      │
└─────────────────────────────────────────────────────┘
```

---

## Concept: Bottleneck Analysis

Every system has exactly one bottleneck at any given time. Fix it, and the next one reveals itself. The four suspects:

### The Four Resources

| Resource | Symptoms | How to Check |
|----------|----------|--------------|
| **CPU** | High load average, slow computation, workers maxed | `top`, `htop`, `mpstat` |
| **Memory** | Swapping, OOM kills, high RSS | `free -m`, `vmstat`, dmesg |
| **Disk I/O** | Slow reads/writes, high iowait | `iostat`, `iotop` |
| **Network** | Bandwidth saturation, packet drops | `iftop`, `nethogs`, `ss` |

### GhostDrop's Diagnosis

```
$ mpstat -P ALL 1
CPU    %usr   %sys   %iowait   %idle
all    62.3   14.1    18.4       5.2
```

- **62% user CPU**: Django workers processing requests + Postgres queries
- **18% iowait**: Disk thrashing — Postgres and file uploads competing for I/O
- **5% idle**: Almost nothing left

The bottleneck isn't one thing. It's *everything on one box competing for the same resources*.

---

## Concept: Vertical vs Horizontal Scaling

### Vertical Scaling (Scale Up)

Buy a bigger box.

```
r5.2xlarge (current)     →    r5.4xlarge
8 vCPU, 64GB RAM              16 vCPU, 128GB RAM
$0.504/hr                     $1.008/hr
```

**Pros**: No code changes. No distributed systems headaches.
**Cons**: There's a ceiling. The biggest EC2 instance is 448 vCPUs. And it's a single point of failure.

### Horizontal Scaling (Scale Out)

Add more boxes.

```
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Server 1 │  │ Server 2 │  │ Server 3 │
└──────────┘  └──────────┘  └──────────┘
```

**Pros**: No ceiling. Redundancy built in.
**Cons**: Distributed state, network complexity, consistency problems.

### Why Not Just Scale Up?

**Amir**: "Can't we just buy a bigger server?"

You can. For now. But:
- Cost scales super-linearly (2x CPU ≠ 2x price, it's often 2.5x)
- Single point of failure remains
- You hit a hard ceiling eventually
- At 10M users, no single box handles it

---

## Concept: Amdahl's Law

Not everything parallelizes. If 20% of your workload is serial (database writes, file locks), then:

```
Speedup = 1 / (S + (1-S)/N)

Where:
  S = serial fraction (0.2 for GhostDrop)
  N = number of processors/servers

N=1:   Speedup = 1.0x
N=2:   Speedup = 1.67x
N=4:   Speedup = 2.5x
N=10:  Speedup = 3.57x
N=100: Speedup = 4.63x
N=∞:   Speedup = 5.0x  (max!)
```

Even with infinite servers, you only get 5x improvement if 20% is serial. The serial parts become the new bottleneck.

**Lesson**: Before adding servers, reduce the serial fraction. Move files off the box. Separate the database. Make the app stateless.

---

## The First Decision

You stand at the whiteboard. Omar, Sana, and Amir are watching.

**You**: "Here's the plan. We can't just scale up — we'll hit the same wall in two weeks. We need to scale out. But we can't scale out until the app is stateless. Right now three things pin us to this one box:"

```
1. Files live on local disk        → Move to object storage
2. Database runs locally           → Separate to managed DB
3. Sessions stored in memory       → Already in Redis (good)
```

**You**: "Step one: put a load balancer in front. Step two: move files to S3. Step three: move Postgres to RDS. Then we can run N app servers."

**Amir**: "How long?"

**You**: "Load balancer today. Object storage by Wednesday. Database separation by Friday."

**Mia** (from the doorway): "The podcast is in 19 days."

---

## The Architecture (After — Target)

```
                    ┌──────────┐
                    │    LB    │
                    └────┬─────┘
              ┌──────────┼──────────┐
              ▼          ▼          ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Server 1 │ │ Server 2 │ │ Server 3 │
        └──────────┘ └──────────┘ └──────────┘
              │          │          │
              ▼          ▼          ▼
        ┌──────────┐         ┌──────────┐
        │ Postgres │         │  Redis   │
        │ (RDS)    │         │(Elasti.) │
        └──────────┘         └──────────┘
              │
              ▼
        ┌──────────┐
        │    S3    │
        │ (files)  │
        └──────────┘
```

---

## Tradeoffs

| Decision | Gain | Cost |
|----------|------|------|
| Horizontal over vertical | No ceiling, redundancy | Distributed complexity |
| Separate DB | Independent scaling | Network latency (~1ms) |
| Object storage | Unlimited file storage | API calls cost money |
| Load balancer | Redundancy, scaling | Another component to manage |

---

## Why Not Just...

**"Why not just upgrade to a bigger instance?"**
You'd buy 2 weeks. Then you're back here. And you still have a single point of failure.

**"Why not go straight to microservices?"**
You have 3 weeks and 4 engineers. Microservices add network calls, deployment complexity, and distributed debugging. Separate the data first, split services later.

**"Why not move to Kubernetes immediately?"**
K8s solves orchestration, not architecture. If your app is stateful and monolithic, K8s just runs a stateful monolith in a container.

---

## Exercise

GhostDrop's metrics show:
- 70% of requests are file downloads
- 20% are metadata lookups (file info, user profile)
- 10% are uploads

If you could only fix ONE thing today, what would give the most relief? Why?

<details>
<summary>Hint</summary>

Downloads are 70% of traffic and they're reading from local disk, saturating I/O and network. Moving downloads to a CDN/object storage removes 70% of the load from your server in one move.
</details>

---

## Quick Reference

| Term | Definition |
|------|-----------|
| **Bottleneck** | The single resource limiting system throughput |
| **Vertical scaling** | Bigger machine (scale up) |
| **Horizontal scaling** | More machines (scale out) |
| **Amdahl's Law** | Serial fraction limits parallel speedup |
| **Stateless app** | App servers hold no local state — can be replaced freely |
| **iowait** | CPU time spent waiting for disk I/O |
| **Single point of failure** | One component whose failure kills the system |

---

## What Breaks Next

You add the load balancer (Chapter 2). Traffic splits across 3 servers. CPU drops to 40%. You breathe.

Then Kai messages: "Users are uploading to Server 1 but downloading from Server 2. The file isn't there."

The files are still on local disk. You need object storage.

[← Ch 0](chapter-00-overview.md) | [Ch 2 →](chapter-02-load-balancer.md)
