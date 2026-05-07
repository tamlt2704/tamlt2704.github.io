# Redis 101 — From First Key to Production Cluster

A narrative-driven Redis tutorial. You're a backend developer at PingPong, a real-time multiplayer gaming platform with 2 million users and a Postgres-only architecture that's falling apart. Over 12 chapters, you'll build a production-grade Redis deployment — one disaster at a time.

## Episodes

| # | Title | The Problem | What You Learn |
|---|---|---|---|
| 00 | [Before You Start](chapter-00-overview.md) | — | Setup, prerequisites, the cast |
| 01 | [Your First Key](chapter-01-first-key.md) | Leaderboard takes 8 seconds | SET/GET, TTL, INCR, cache-aside |
| 02 | [The Ranking Problem](chapter-02-sorted-sets.md) | "What's my rank?" is a full table scan | Sorted sets, ZADD, ZRANGE, ZREVRANK |
| 03 | [Player Profiles](chapter-03-hashes-caching.md) | 100 profile lookups per page | Hashes, caching patterns, thundering herd |
| 04 | [The Matchmaking Queue](chapter-04-lists-queues.md) | 15-second wait to find a match | Lists, BRPOP, reliable queues |
| 05 | [Chat Messages Vanish](chapter-05-pubsub-streams.md) | Disconnected players miss messages | Pub/Sub, Streams, consumer groups |
| 06 | [Spam Bots](chapter-06-rate-limiting.md) | 15,000 bot requests per second | Rate limiting, sliding windows, Lua scripts |
| 07 | [Two Servers, One Match](chapter-07-distributed-locks.md) | Double-booking in matchmaking | Distributed locks, Redlock, fencing tokens |
| 08 | [The Server Crashes](chapter-08-persistence.md) | Leaderboard resets to zero | RDB, AOF, hybrid persistence, eviction |
| 09 | [One Server Isn't Enough](chapter-09-replication.md) | 20-minute outage on hardware failure | Replication, Sentinel, automatic failover |
| 10 | [16GB Isn't Enough](chapter-10-clustering.md) | Can't fit 10M users in one node | Clustering, hash slots, resharding |
| 11 | [The Intern Incident](chapter-11-operational-safety.md) | FLUSHALL on production | ACLs, security, monitoring, SLOWLOG |
| 12 | [Black Friday](chapter-12-production.md) | 100K ops/sec target | Connection pools, pipelines, tuning |

## Prerequisites

- Docker
- Python 3.10+ with `redis-py` (`pip install redis`)
- A terminal

## Quick Start

```bash
docker run -d --name redis-dev -p 6379:6379 redis:7-alpine
docker exec -it redis-dev redis-cli PING
# PONG
```

## Philosophy

Every concept is introduced because something broke. No theory without a problem to solve first. The disasters come first. The understanding follows.
