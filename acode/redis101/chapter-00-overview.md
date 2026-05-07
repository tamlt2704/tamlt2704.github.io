# Chapter 0: Before You Start

[Chapter 1: Your First Key →](chapter-01-first-key.md)

---

## The Story

This is a series about Redis — but not the kind where you memorize "Redis is an in-memory data store" and move on.

You're a backend developer at **PingPong**, a real-time multiplayer gaming platform. The company started as a weekend hackathon project and somehow got 2 million users. The codebase is held together by duct tape and optimism. Every feature hits Postgres directly. Every page load runs 14 queries. The P95 latency is "whenever it feels like it."

Your tech lead, **Marta**, pulls you aside on Monday morning:

"The leaderboard page takes 8 seconds to load. The matchmaking queue is backed up. Players are rage-quitting before they even get into a game. We need caching. We need queues. We need something fast. Figure out Redis."

You nod. You've heard of Redis. Key-value store. Fast. How hard can it be?

Over the next 12 chapters, you'll take Redis from "I can SET and GET" to running a production cluster that handles 100,000 operations per second. Along the way, everything will break in instructive ways. The cache will serve stale data. The queue will lose messages. The pub/sub will miss events. A node will die during a tournament final. Someone will run `FLUSHALL` on production.

Each disaster teaches you something about data structures, persistence, replication, or operational safety that no documentation page could. You'll fix every bug, understand why it happened, and build the muscle memory to prevent it.

By the end, you'll have a production-grade Redis deployment with caching strategies, message queues, real-time pub/sub, rate limiting, distributed locks, Lua scripting, persistence, replication, clustering, and monitoring — and you'll understand *why* every configuration choice is there.

## How to Read This

Every chapter is the same loop:

1. Something is slow, broken, or on fire
2. You identify the problem
3. You learn the Redis concept that solves it
4. You implement the fix
5. You verify it works — then discover the next problem

No concept shows up before you need it. You won't hear about Redis Streams until your pub/sub drops messages during a server restart. You won't touch clustering until a single node runs out of memory during a tournament.

The problems come first. The theory follows.

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Backend Developer | Competent, slightly overwhelmed |
| **Marta** | Tech Lead | Pragmatic. "Ship it, but ship it right." |
| **Derek** | Frontend Lead | "The API is slow." (It's always the API.) |
| **Ops Olga** | SRE | Monitors everything. Trusts nothing. Sleeps with PagerDuty. |
| **CEO Chad** | Founder | "We're scaling to 10 million users next quarter." |
| **The Intern** | Summer hire | Ran `FLUSHALL` on prod. Once. |

## The Roadmap

| Ch | The Problem | What You Learn |
|---|---|---|
| 1 | Leaderboard takes 8 seconds | Redis basics — strings, SET/GET, TTL, CLI |
| 2 | Leaderboard needs ranking | Sorted sets, ZADD, ZRANGE, ZRANK |
| 3 | Player profiles hit DB every request | Hashes, caching patterns, cache-aside |
| 4 | Matchmaking queue is FIFO chaos | Lists, LPUSH/BRPOP, reliable queues |
| 5 | Chat messages vanish on restart | Pub/Sub, its limitations, Redis Streams |
| 6 | Spam bots flood the API | Rate limiting with INCR, sliding windows, Lua scripts |
| 7 | Two servers grant the same match | Distributed locks, Redlock, fencing tokens |
| 8 | Server crashes, data is gone | Persistence — RDB snapshots, AOF, hybrid |
| 9 | One node can't handle the load | Replication — read replicas, failover, Sentinel |
| 10 | 16GB isn't enough for 2M users | Clustering — hash slots, resharding, client routing |
| 11 | The intern runs FLUSHALL on prod | Operational safety — ACLs, rename-command, monitoring |
| 12 | Black Friday: 100K ops/sec | Production tuning — memory, eviction, connection pools, observability |

## Prerequisites

Three things: Docker, a terminal, and curiosity.

### Redis 7

Don't install Redis natively. Use Docker — it's cleaner and matches production.

```bash
docker run -d --name redis-dev -p 6379:6379 redis:7-alpine
```

Verify:

```bash
docker exec -it redis-dev redis-cli PING
```

```
PONG
```

If you see PONG, you're in business.

### redis-cli

The CLI comes with the container. You'll use it constantly:

```bash
docker exec -it redis-dev redis-cli
```

Or install it locally:

```bash
# macOS
brew install redis

# Ubuntu/Debian
sudo apt install redis-tools

# Windows (WSL recommended)
sudo apt install redis-tools
```

### A Programming Language

Examples use Python with the `redis-py` library, but every concept applies to any language. Install:

```bash
pip install redis
```

Quick check:

```python
import redis
r = redis.Redis()
r.ping()  # True
```

### Optional: RedisInsight

A GUI for exploring your data visually. Useful but not required.

```bash
docker run -d --name redisinsight -p 5540:5540 redis/redisinsight:latest
```

Open http://localhost:5540 and connect to `localhost:6379`.

### Quick Check

```bash
docker exec -it redis-dev redis-cli PING && echo "Ready to go"
```

If you see `PONG` followed by `Ready to go`, you're set.

Let's make the leaderboard fast.

---

[Chapter 1: Your First Key →](chapter-01-first-key.md)
