# Chapter 10: 16GB Isn't Enough — Clustering

[← Chapter 9: Replication](chapter-09-replication.md) | [Chapter 11: The Intern Incident →](chapter-11-operational-safety.md)

---

## The Problem

PingPong has 2 million players. Each player profile is ~200 bytes. The leaderboard sorted set is ~100MB. Chat streams, rate limit counters, matchmaking queues — it all adds up. The primary is using 14GB of its 16GB limit.

CEO Chad: "Asia launch next month. 10 million users."

10 million players × 200 bytes = 2GB just for profiles. Plus leaderboards per region, chat streams, session data. You need 50-80GB. One server can't hold it.

Ops Olga: "We need to shard. Redis Cluster splits data across multiple nodes."

## Redis Cluster: The Concept

Redis Cluster divides the keyspace into **16,384 hash slots**. Each key is assigned to a slot using `CRC16(key) % 16384`. Each node in the cluster owns a subset of slots.

```
Node A: slots 0-5460       (keys hashing to these slots live here)
Node B: slots 5461-10922   (keys hashing to these slots live here)
Node C: slots 10923-16383  (keys hashing to these slots live here)
```

When you SET a key, the client computes the slot, routes to the correct node, and executes there. If you hit the wrong node, it responds with `MOVED slot ip:port` — the client redirects.

```
Client: SET player:alice:score 1500
        → CRC16("player:alice:score") % 16384 = 7231
        → Slot 7231 belongs to Node B
        → Route to Node B
        → OK
```

## Setting Up a Cluster

Minimum: 3 primary nodes (for quorum). Recommended: 3 primaries + 3 replicas (for failover).

```bash
# Create 6 Redis instances
for port in 7000 7001 7002 7003 7004 7005; do
  docker run -d --name redis-node-$port --net redis-cluster \
    -p $port:$port -p 1$port:1$port \
    redis:7-alpine redis-server \
    --port $port \
    --cluster-enabled yes \
    --cluster-config-file nodes.conf \
    --cluster-node-timeout 5000 \
    --appendonly yes
done

# Create the cluster (3 primaries + 3 replicas)
docker exec redis-node-7000 redis-cli --cluster create \
  redis-node-7000:7000 redis-node-7001:7001 redis-node-7002:7002 \
  redis-node-7003:7003 redis-node-7004:7004 redis-node-7005:7005 \
  --cluster-replicas 1
```

Or with Docker Compose:

```yaml
# docker-compose-cluster.yml
services:
  redis-node-7000:
    image: redis:7-alpine
    command: redis-server --port 7000 --cluster-enabled yes --cluster-config-file nodes.conf --cluster-node-timeout 5000 --appendonly yes
    ports:
      - "7000:7000"
    networks:
      - redis-cluster

  redis-node-7001:
    image: redis:7-alpine
    command: redis-server --port 7001 --cluster-enabled yes --cluster-config-file nodes.conf --cluster-node-timeout 5000 --appendonly yes
    ports:
      - "7001:7001"
    networks:
      - redis-cluster

  # ... repeat for 7002-7005

networks:
  redis-cluster:
    driver: bridge
```

### Verify the Cluster

```bash
docker exec redis-node-7000 redis-cli -p 7000 CLUSTER INFO
# cluster_state:ok
# cluster_slots_assigned:16384
# cluster_slots_ok:16384
# cluster_known_nodes:6
# cluster_size:3

docker exec redis-node-7000 redis-cli -p 7000 CLUSTER NODES
# abc123 redis-node-7000:7000@17000 myself,master - 0 0 1 connected 0-5460
# def456 redis-node-7001:7001@17001 master - 0 0 2 connected 5461-10922
# ghi789 redis-node-7002:7002@17002 master - 0 0 3 connected 10923-16383
# jkl012 redis-node-7003:7003@17003 slave abc123 0 0 4 connected
# mno345 redis-node-7004:7004@17004 slave def456 0 0 5 connected
# pqr678 redis-node-7005:7005@17005 slave ghi789 0 0 6 connected
```

## Connecting from Python

```python
from redis.cluster import RedisCluster

rc = RedisCluster(
    host='redis-node-7000',
    port=7000,
    decode_responses=True
)

# Works exactly like regular Redis
rc.set("player:alice:score", 1500)
rc.get("player:alice:score")  # "1500"

# The client handles routing automatically
rc.zadd("leaderboard:global", {"alice": 1500, "bob": 2100})
rc.zrevrank("leaderboard:global", "alice")
```

The cluster client discovers all nodes on startup and routes commands to the correct node based on the key's hash slot. Transparent to your application code.

## Hash Tags: Keeping Related Keys Together

Problem: `ZUNIONSTORE` combines multiple sorted sets. But in a cluster, those sets might live on different nodes. Multi-key commands only work when all keys are on the same node.

```redis
# This FAILS in a cluster if the keys are on different nodes:
ZUNIONSTORE leaderboard:combined 2 leaderboard:deathmatch leaderboard:capture
# (error) CROSSSLOT Keys in request don't hash to the same slot
```

Fix: **hash tags**. Redis only hashes the part inside `{}` to determine the slot:

```redis
# These all hash to the same slot (based on "leaderboard"):
{leaderboard}:deathmatch
{leaderboard}:capture
{leaderboard}:combined

# Now this works:
ZUNIONSTORE {leaderboard}:combined 2 {leaderboard}:deathmatch {leaderboard}:capture
# OK — all keys are on the same node
```

```python
# Player data that must be co-located
rc.hset("{player:42}:profile", mapping={"username": "alice", "level": "27"})
rc.zadd("{player:42}:matches", {"match-abc": time.time()})
rc.sadd("{player:42}:friends", "bob", "charlie")
# All three keys hash to the same slot → same node
```

### Hash Tag Strategy for PingPong

| Data | Key Pattern | Hash Tag | Why |
|---|---|---|---|
| Player data | `{player:42}:profile` | `player:42` | Profile + matches + friends co-located |
| Match data | `{match:abc}:state` | `match:abc` | Match state + chat on same node |
| Leaderboard | `{leaderboard}:global` | `leaderboard` | All leaderboard ops on one node |
| Per-region | `{region:asia}:leaderboard` | `region:asia` | Regional data co-located |

## MOVED and ASK: Redirections

If you send a command to the wrong node:

```redis
# Connected to Node A, but key lives on Node B
GET player:bob:score
# -MOVED 7231 redis-node-7001:7001
```

Smart clients (like `redis-py`'s `RedisCluster`) handle this automatically — they cache the slot-to-node mapping and route correctly. You'll only see MOVED during resharding or if the mapping is stale.

`ASK` is similar but temporary — it happens during slot migration (resharding). The client should try the target node once but not update its routing table.

## Resharding: Adding Nodes

PingPong grows. You need a 4th primary node.

```bash
# Add a new node to the cluster
docker run -d --name redis-node-7006 --net redis-cluster \
  -p 7006:7006 redis:7-alpine redis-server \
  --port 7006 --cluster-enabled yes --cluster-config-file nodes.conf

# Join the cluster
docker exec redis-node-7000 redis-cli -p 7000 \
  CLUSTER MEET redis-node-7006 7006

# Reshard: move 4096 slots from existing nodes to the new one
docker exec redis-node-7000 redis-cli --cluster reshard \
  redis-node-7000:7000 \
  --cluster-from abc123,def456,ghi789 \
  --cluster-to <new-node-id> \
  --cluster-slots 4096 \
  --cluster-yes
```

Resharding is live — no downtime. Keys are migrated slot by slot. During migration, clients get `ASK` redirections for keys in transit.

After resharding:
```
Node A: slots 0-4095        (was 0-5460)
Node B: slots 5461-9556     (was 5461-10922)
Node C: slots 10923-15017   (was 10923-16383)
Node D: slots 4096-5460, 9557-10922, 15018-16383  (new)
```

## Cluster Failover

Each primary has a replica. If a primary dies, its replica is automatically promoted:

```bash
# Kill Node B (primary for slots 5461-10922)
docker stop redis-node-7001

# Node B's replica (7004) is promoted to primary
docker exec redis-node-7000 redis-cli -p 7000 CLUSTER NODES
# ... redis-node-7004:7004 master - ... connected 5461-10922
```

No Sentinel needed — the cluster handles its own failover. Replicas vote among themselves, and the one with the most up-to-date data wins.

### Cluster Failure Conditions

The cluster goes into `FAIL` state (stops accepting writes) when:
- A primary is down AND has no replica to promote
- More than half the primaries are unreachable (split-brain protection)

This is why you need replicas for every primary.

## Cluster Limitations

| Feature | Works in Cluster? | Workaround |
|---|---|---|
| Multi-key commands | Only if same slot | Use hash tags |
| Transactions (MULTI) | Only if same slot | Use hash tags |
| Lua scripts | Only if all keys same slot | Use hash tags |
| KEYS / SCAN | Per-node only | Scan each node |
| Pub/Sub | Works (broadcast to all nodes) | No workaround needed |
| SELECT (multiple DBs) | No (only DB 0) | Use key prefixes |
| Large sorted sets | Works but lives on one node | Shard manually if too large |

## Cluster vs Sentinel: When to Use Which

| Criteria | Sentinel | Cluster |
|---|---|---|
| Data size | Fits in one node | Exceeds one node's RAM |
| Write scaling | No (single primary) | Yes (multiple primaries) |
| Read scaling | Yes (replicas) | Yes (replicas per shard) |
| Automatic failover | Yes | Yes (built-in) |
| Multi-key operations | Always work | Only within same slot |
| Complexity | Low | Medium-High |
| Minimum nodes | 1 primary + 2 replicas + 3 sentinels | 6 (3 primary + 3 replica) |

**Use Sentinel when:** Your data fits in one node and you just need HA.
**Use Cluster when:** You need more RAM or write throughput than one node provides.

For PingPong at 10 million users: Cluster. The data won't fit in 16GB.

## Monitoring the Cluster

```python
def cluster_health_check():
    info = rc.cluster_info()
    assert info["cluster_state"] == "ok"
    assert info["cluster_slots_ok"] == 16384

    nodes = rc.cluster_nodes()
    for node in nodes:
        if "master" in node["flags"]:
            assert "fail" not in node["flags"]

    return {"status": "healthy", "nodes": len(nodes), "slots_ok": info["cluster_slots_ok"]}
```

```bash
# Quick cluster health check
redis-cli -p 7000 CLUSTER INFO | grep cluster_state
# cluster_state:ok

# Check for failed nodes
redis-cli -p 7000 CLUSTER NODES | grep fail
# (empty = all healthy)
```

## What You Learned

- **Hash slots** — 16,384 slots distributed across nodes
- **Automatic routing** — clients compute slot and route to correct node
- **Hash tags** — `{tag}` forces related keys to the same slot
- **MOVED/ASK** — redirection when hitting the wrong node
- **Resharding** — live migration of slots to new nodes
- **Cluster failover** — automatic replica promotion (no Sentinel needed)
- **Limitations** — multi-key ops require same slot
- **Cluster vs Sentinel** — sharding vs simple HA

PingPong can now scale to 50GB+ across multiple nodes. Each node handles its share of the traffic. Failover is automatic. CEO Chad's Asia launch is feasible.

But there's one more disaster waiting. The intern has production access. And a curious nature.

That's Chapter 11.

---

[← Chapter 9: Replication](chapter-09-replication.md) | [Chapter 11: The Intern Incident →](chapter-11-operational-safety.md)
