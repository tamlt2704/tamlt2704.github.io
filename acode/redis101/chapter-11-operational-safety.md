# Chapter 11: The Intern Runs FLUSHALL — Operational Safety

[← Chapter 10: Clustering](chapter-10-clustering.md) | [Chapter 12: Production Tuning →](chapter-12-production.md)

---

## The Incident

Friday, 4:47 PM. The intern is debugging a test environment issue. They open a terminal, connect to what they think is the staging Redis, and type:

```redis
FLUSHALL
```

It wasn't staging. It was production.

2 million player scores. Gone. Every cached profile. Gone. The matchmaking queue. Gone. Rate limit counters. Gone. The leaderboard that took months to build. Gone. In 200 milliseconds.

Ops Olga's phone explodes. CEO Chad calls an emergency meeting. The intern looks like they're about to cry.

The data is recoverable (AOF + RDB backups), but it takes 45 minutes to restore. 45 minutes of complete outage.

Marta, after the postmortem: "This should never have been possible. We need guardrails."

## ACLs: Access Control Lists

Redis 6+ has a built-in ACL system. Different users get different permissions.

### Default User (Dangerous)

By default, Redis has one user (`default`) with full access and no password. This is what the intern used.

```redis
ACL LIST
# user default on nopass ~* &* +@all
# Translation: user "default", enabled, no password, all keys, all channels, all commands
```

### Creating Restricted Users

```redis
# Application user: can read/write data keys, but NOT admin commands
ACL SETUSER app-backend on >SecurePassword123! ~player:* ~leaderboard:* ~match:* ~chat:* +@read +@write +@sortedset +@hash +@list +@stream -@admin -@dangerous

# Read-only user for analytics dashboards
ACL SETUSER analytics on >ReadOnlyPass456! ~* +@read -@write -@admin -@dangerous

# Admin user (Ops Olga only)
ACL SETUSER ops-admin on >SuperSecretOpsPass! ~* &* +@all

# Disable the default user
ACL SETUSER default off
```

### ACL Categories

| Category | Commands | Risk |
|---|---|---|
| `@read` | GET, HGET, ZRANGE, LRANGE, etc. | Low |
| `@write` | SET, HSET, ZADD, LPUSH, etc. | Medium |
| `@admin` | CONFIG, SHUTDOWN, REPLICAOF, etc. | High |
| `@dangerous` | FLUSHALL, FLUSHDB, KEYS, DEBUG | Critical |
| `@slow` | SORT, SMEMBERS on large sets | Performance risk |

### Key Patterns

Restrict which keys a user can access:

```redis
# Can only access player:* and leaderboard:* keys
ACL SETUSER matchmaker on >MatchPass ~player:* ~leaderboard:* ~matchmaking:* +@read +@write +@sortedset +@list

# Can only access chat:* keys
ACL SETUSER chat-service on >ChatPass ~chat:* +@read +@write +@stream
```

The matchmaker can't accidentally delete leaderboard data. The chat service can't touch player profiles. Blast radius is contained.

### Persisting ACLs

```redis
# Save ACLs to file
ACL SAVE

# Or configure in redis.conf:
# aclfile /etc/redis/users.acl
```

`users.acl`:
```
user app-backend on >SecurePassword123! ~player:* ~leaderboard:* ~match:* ~chat:* +@read +@write +@sortedset +@hash +@list +@stream -@admin -@dangerous
user analytics on >ReadOnlyPass456! ~* +@read -@write -@admin -@dangerous
user ops-admin on >SuperSecretOpsPass! ~* &* +@all
user default off
```

## Rename Dangerous Commands

Even with ACLs, you can add another layer: rename or disable dangerous commands entirely.

```
# redis.conf
rename-command FLUSHALL ""
rename-command FLUSHDB ""
rename-command KEYS ""
rename-command CONFIG "CONFIG_a8f3b2c1"
rename-command DEBUG ""
rename-command SHUTDOWN "SHUTDOWN_ops_only_7x9k"
```

`FLUSHALL` no longer exists. Even if someone bypasses ACLs, the command isn't there. `CONFIG` is renamed to a secret string only Ops Olga knows.

**Warning:** Don't rename commands that your client libraries use internally. `redis-py` uses `CONFIG` for some operations. Test thoroughly.

## Network Security

### Bind to Specific Interfaces

```
# redis.conf
bind 127.0.0.1 10.0.1.0
# Only accepts connections from localhost and the internal network
# NOT exposed to the internet
```

### Protected Mode

```
# redis.conf
protected-mode yes
# Rejects connections from non-localhost if no password is set
```

### TLS Encryption

```
# redis.conf
tls-port 6380
port 0  # Disable non-TLS port
tls-cert-file /etc/redis/tls/redis.crt
tls-key-file /etc/redis/tls/redis.key
tls-ca-cert-file /etc/redis/tls/ca.crt
tls-auth-clients yes
```

```python
import redis

r = redis.Redis(
    host='redis-prod',
    port=6380,
    ssl=True,
    ssl_certfile='/path/to/client.crt',
    ssl_keyfile='/path/to/client.key',
    ssl_ca_certs='/path/to/ca.crt',
    username='app-backend',
    password='SecurePassword123!'
)
```

## Monitoring and Alerting

### SLOWLOG: Finding Slow Commands

```redis
# Log commands taking longer than 10ms
CONFIG SET slowlog-log-slower-than 10000

# View slow commands
SLOWLOG GET 10
# 1) 1) (integer) 14          ← entry ID
#    2) (integer) 1705312800  ← timestamp
#    3) (integer) 15234       ← execution time (microseconds)
#    4) 1) "KEYS"             ← the command
#       2) "player:*"         ← arguments
#    5) "app-backend"         ← client name
```

`KEYS player:*` took 15ms. That's the command that blocks the event loop. Find it. Kill it. Replace with SCAN.

### INFO: The Dashboard

```redis
INFO all
# Server
redis_version:7.2.4
uptime_in_seconds:864000

# Clients
connected_clients:142
blocked_clients:3

# Memory
used_memory_human:2.1G
maxmemory_human:4G
mem_fragmentation_ratio:1.03

# Stats
total_commands_processed:1234567890
instantaneous_ops_per_sec:45000
keyspace_hits:98765432
keyspace_misses:1234567
hit_rate: 98.8%

# Replication
role:master
connected_slaves:2

# Keyspace
db0:keys=2500000,expires=1800000
```

### Key Metrics to Monitor

| Metric | Alert Threshold | Why |
|---|---|---|
| `used_memory` / `maxmemory` | > 80% | Approaching eviction |
| `instantaneous_ops_per_sec` | Sudden drop | Something is blocking |
| `connected_clients` | > 80% of `maxclients` | Connection exhaustion |
| `keyspace_misses` / total | > 20% | Cache is ineffective |
| `rdb_last_bgsave_status` | != ok | Persistence broken |
| `master_link_status` | != up (on replicas) | Replication broken |
| `blocked_clients` | > 10 | BRPOP/BLPOP pileup |
| `mem_fragmentation_ratio` | > 1.5 | Memory fragmentation |

### CLIENT LIST: Who's Connected

```redis
CLIENT LIST
# id=42 addr=10.0.1.5:52341 name=matchmaker-1 cmd=brpop idle=0
# id=43 addr=10.0.1.6:52342 name=leaderboard-api cmd=zrange idle=2
# id=44 addr=10.0.1.7:52343 name= cmd=keys idle=300  ← WHO IS THIS?
```

An unnamed client running `KEYS` and idle for 5 minutes. Suspicious. Kill it:

```redis
CLIENT KILL ID 44
```

### MONITOR: Live Command Stream

```redis
MONITOR
# 1705312800.123456 [0 10.0.1.5:52341] "BRPOP" "matchmaking:queue" "5"
# 1705312800.234567 [0 10.0.1.6:52342] "ZRANGE" "leaderboard:global" "0" "9" "REV"
# 1705312800.345678 [0 10.0.1.7:52343] "KEYS" "player:*"  ← FOUND YOU
```

**Warning:** MONITOR impacts performance (~50% throughput reduction). Use briefly for debugging, never in production permanently.

## Keyspace Notifications

Get notified when keys expire, are deleted, or are modified:

```redis
CONFIG SET notify-keyspace-events KEA
# K = keyspace events
# E = keyevent events
# A = all commands

# Subscribe to expiration events
SUBSCRIBE __keyevent@0__:expired
# Notifies when any key expires — useful for session cleanup
```

```python
def listen_for_expirations():
    pubsub = r.pubsub()
    pubsub.subscribe("__keyevent@0__:expired")
    for message in pubsub.listen():
        if message["type"] == "message":
            expired_key = message["data"]
            if expired_key.startswith("session:"):
                handle_session_expired(expired_key)
```

## The Postmortem Checklist

After the intern incident, the team implements:

1. ✅ **ACLs** — app users can't run FLUSHALL
2. ✅ **Renamed commands** — FLUSHALL doesn't exist
3. ✅ **Network binding** — Redis not exposed to internet
4. ✅ **TLS** — encrypted connections
5. ✅ **Separate environments** — prod/staging use different ports, passwords, and hostnames
6. ✅ **Color-coded terminals** — prod terminals have red backgrounds
7. ✅ **SLOWLOG monitoring** — alert on commands > 100ms
8. ✅ **Connection auditing** — CLIENT LIST reviewed weekly
9. ✅ **Backup verification** — monthly restore drills
10. ✅ **Runbook** — documented recovery procedures

The intern keeps their job. They also become the team's biggest advocate for operational safety. (They never run FLUSHALL again.)

## What You Learned

- **ACLs** — per-user permissions (commands, keys, channels)
- **rename-command** — disable or hide dangerous commands
- **Network security** — bind, protected-mode, TLS
- **SLOWLOG** — find and fix slow commands
- **INFO** — comprehensive server metrics
- **CLIENT LIST/KILL** — audit and manage connections
- **MONITOR** — live command stream (debugging only)
- **Keyspace notifications** — react to key events
- **Operational culture** — color-coded terminals, separate environments, runbooks

The platform is secure. The intern can't destroy production. Ops Olga has visibility into everything happening inside Redis.

One chapter left. CEO Chad's Asia launch is next week. 10 million users. 100,000 operations per second. Time to tune Redis for maximum performance.

That's Chapter 12.

---

[← Chapter 10: Clustering](chapter-10-clustering.md) | [Chapter 12: Production Tuning →](chapter-12-production.md)
