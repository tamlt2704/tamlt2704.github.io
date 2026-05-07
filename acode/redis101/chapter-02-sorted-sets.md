# Chapter 2: The Ranking Problem — Sorted Sets

[← Chapter 1: Your First Key](chapter-01-first-key.md) | [Chapter 3: Player Profiles →](chapter-03-hashes-caching.md)

---

## The Problem

Players want to know their rank. Not just "top 100" — their personal position among 2 million players. "Am I #4,521 or #4,522?"

With Postgres, that's:

```sql
SELECT COUNT(*) + 1 FROM players WHERE score > (
    SELECT score FROM players WHERE id = 42
);
```

Full table scan. Every time. For every player who checks. 50,000 times per hour.

Marta: "Redis has a data structure for this. Sorted sets. Look it up."

## Sorted Sets: The Perfect Leaderboard

A sorted set is a collection where every member has a score. Redis keeps them sorted by score automatically. You can:

- Add a member with a score: O(log N)
- Get a member's rank: O(log N)
- Get a range by rank: O(log N + M)
- Get a range by score: O(log N + M)

With 2 million members, `log₂(2,000,000)` ≈ 21 operations internally. That's why it's fast.

## ZADD: Adding Scores

```redis
ZADD leaderboard 1500 "alice"
ZADD leaderboard 2100 "bob"
ZADD leaderboard 1800 "charlie"
ZADD leaderboard 950 "derek"
ZADD leaderboard 2100 "eve"
```

Each member gets a floating-point score. If the member already exists, the score is updated. No duplicates — a sorted set is still a set.

### Bulk Add

```redis
ZADD leaderboard 1500 "alice" 2100 "bob" 1800 "charlie" 950 "derek"
# (integer) 4 — four members added
```

### Update Options

```redis
ZADD leaderboard GT 1600 "alice"
# GT — only update if new score is Greater Than current
# Alice's score updates from 1500 → 1600

ZADD leaderboard LT 1400 "alice"
# LT — only update if new score is Less Than current
# Alice stays at 1600 (1400 < 1600 is true, but LT means "update if lower")
# Wait — LT updates if new < current. So 1400 < 1600 → updates to 1400.
# Use GT for "high score" leaderboards where you only want increases.
```

For PingPong's leaderboard, scores always increase (you earn points, never lose them). Use `GT`:

```redis
ZADD leaderboard GT 1650 "alice"
# Only updates if 1650 > current score
```

## ZRANGE: Getting the Top Players

```redis
ZRANGE leaderboard 0 9 REV WITHSCORES
# Top 10 players (REV = highest score first)
# 1) "bob"
# 2) "2100"
# 3) "eve"
# 4) "2100"
# 5) "charlie"
# 6) "1800"
# 7) "alice"
# 8) "1600"
# 9) "derek"
# 10) "950"
```

`ZRANGE key start stop` returns members by rank index. `REV` reverses the order (highest first). `WITHSCORES` includes the scores.

### Pagination

```redis
# Page 1 (ranks 0-9)
ZRANGE leaderboard 0 9 REV WITHSCORES

# Page 2 (ranks 10-19)
ZRANGE leaderboard 10 19 REV WITHSCORES

# Page 3 (ranks 20-29)
ZRANGE leaderboard 20 29 REV WITHSCORES
```

O(log N + M) where M is the page size. For 10 results out of 2 million: ~21 internal operations + 10 reads. Microseconds.

## ZRANK and ZREVRANK: "What's My Rank?"

```redis
ZREVRANK leaderboard "alice"
# (integer) 3 — alice is rank #3 (0-indexed, so 4th place)

ZREVRANK leaderboard "derek"
# (integer) 4 — derek is last (5th place)

ZREVRANK leaderboard "nobody"
# (nil) — not in the set
```

`ZREVRANK` gives rank from highest score (0 = top player). `ZRANK` gives rank from lowest score.

For the player profile page:

```python
def get_player_rank(username):
    rank = r.zrevrank("leaderboard", username)
    if rank is None:
        return None
    return rank + 1  # Convert 0-indexed to 1-indexed

# "You are ranked #4,521 out of 2,000,000 players"
```

O(log N). For 2 million players: ~21 operations. Under 1ms.

## ZSCORE: Getting a Player's Score

```redis
ZSCORE leaderboard "alice"
# "1600"

ZSCORE leaderboard "nobody"
# (nil)
```

## ZINCRBY: Updating Scores

After a match, the winner gains points:

```redis
ZINCRBY leaderboard 50 "alice"
# "1650" — alice's new score

ZINCRBY leaderboard -25 "derek"
# "925" — derek lost points
```

Atomic. No read-modify-write race condition. Two concurrent matches updating the same player's score will both apply correctly.

## The Full Leaderboard API

```python
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

LEADERBOARD_KEY = "leaderboard:global"

def record_match_result(winner: str, loser: str, winner_gain: int = 25, loser_loss: int = 10):
    """Update scores after a match."""
    pipe = r.pipeline()
    pipe.zincrby(LEADERBOARD_KEY, winner_gain, winner)
    pipe.zincrby(LEADERBOARD_KEY, -loser_loss, loser)
    pipe.execute()

def get_top_players(page: int = 1, page_size: int = 10):
    """Get leaderboard page."""
    start = (page - 1) * page_size
    end = start + page_size - 1
    results = r.zrange(LEADERBOARD_KEY, start, end, desc=True, withscores=True)
    return [{"rank": start + i + 1, "username": name, "score": int(score)}
            for i, (name, score) in enumerate(results)]

def get_player_rank(username: str):
    """Get a specific player's rank and score."""
    pipe = r.pipeline()
    pipe.zrevrank(LEADERBOARD_KEY, username)
    pipe.zscore(LEADERBOARD_KEY, username)
    rank, score = pipe.execute()
    if rank is None:
        return None
    return {"rank": rank + 1, "username": username, "score": int(score)}

def get_players_around(username: str, context: int = 5):
    """Get players ranked near a specific player."""
    rank = r.zrevrank(LEADERBOARD_KEY, username)
    if rank is None:
        return []
    start = max(0, rank - context)
    end = rank + context
    results = r.zrange(LEADERBOARD_KEY, start, end, desc=True, withscores=True)
    return [{"rank": start + i + 1, "username": name, "score": int(score)}
            for i, (name, score) in enumerate(results)]

def get_total_players():
    """Total number of ranked players."""
    return r.zcard(LEADERBOARD_KEY)
```

### Usage

```python
# After a match
record_match_result("alice", "derek")

# Leaderboard page 1
get_top_players(page=1)
# [{"rank": 1, "username": "bob", "score": 2100}, ...]

# Player's own rank
get_player_rank("alice")
# {"rank": 4521, "username": "alice", "score": 1650}

# Players around alice (±5 ranks)
get_players_around("alice", context=5)
# Shows ranks 4516-4526

# Total players
get_total_players()
# 2000000
```

## Pipelines: Reducing Round-Trips

Notice the `r.pipeline()` calls above. A pipeline batches multiple commands into one network round-trip:

```python
# Without pipeline: 3 round-trips (~1.5ms)
r.zincrby("leaderboard:global", 25, "alice")
r.zincrby("leaderboard:global", -10, "derek")
r.incr("stats:matches:today")

# With pipeline: 1 round-trip (~0.5ms)
pipe = r.pipeline()
pipe.zincrby("leaderboard:global", 25, "alice")
pipe.zincrby("leaderboard:global", -10, "derek")
pipe.incr("stats:matches:today")
pipe.execute()  # Returns list of results
```

Pipelines don't provide atomicity (use transactions or Lua for that). They reduce network overhead. For the leaderboard update after a match, that's 3x fewer round-trips.

## ZRANGEBYSCORE: Score-Based Queries

"Show me all players with scores between 1500 and 2000":

```redis
ZRANGE leaderboard 1500 2000 BYSCORE WITHSCORES
# Members with scores in [1500, 2000]

ZRANGE leaderboard 1500 2000 BYSCORE WITHSCORES LIMIT 0 10
# First 10 members in that score range
```

Useful for matchmaking: find players within ±100 points of the current player.

```python
def find_opponents(username: str, range_points: int = 100):
    """Find players with similar skill for matchmaking."""
    score = r.zscore(LEADERBOARD_KEY, username)
    if score is None:
        return []
    low = score - range_points
    high = score + range_points
    candidates = r.zrangebyscore(LEADERBOARD_KEY, low, high)
    return [c for c in candidates if c != username]
```

## Multiple Leaderboards

PingPong has daily, weekly, and all-time leaderboards:

```python
from datetime import date

def record_score(username: str, points: int):
    """Update all leaderboard timeframes."""
    today = date.today()
    pipe = r.pipeline()
    pipe.zincrby("leaderboard:alltime", points, username)
    pipe.zincrby(f"leaderboard:daily:{today}", points, username)
    pipe.zincrby(f"leaderboard:weekly:{today.isocalendar()[1]}", points, username)
    pipe.execute()

    # Daily leaderboard expires at midnight + buffer
    r.expire(f"leaderboard:daily:{today}", 172800)  # 48h
    # Weekly expires after the week
    r.expire(f"leaderboard:weekly:{today.isocalendar()[1]}", 864000)  # 10 days
```

Daily leaderboards auto-delete after 48 hours. No cleanup cron needed.

## ZUNIONSTORE and ZINTERSTORE: Combining Leaderboards

"Show me the top players across all game modes combined":

```redis
# Combine scores from multiple game modes
ZUNIONSTORE leaderboard:combined 3 leaderboard:deathmatch leaderboard:capture leaderboard:racing WEIGHTS 1 1 1 AGGREGATE SUM

# Top 10 across all modes
ZRANGE leaderboard:combined 0 9 REV WITHSCORES
```

`ZUNIONSTORE` creates a new sorted set by combining others. `WEIGHTS` scales scores. `AGGREGATE` controls how ties are resolved (SUM, MIN, MAX).

## Performance: 2 Million Members

Let's verify the claims:

```python
import time

# Seed 2 million players
pipe = r.pipeline()
for i in range(2_000_000):
    pipe.zadd("leaderboard:bench", {f"player_{i}": i * 1.5})
    if i % 10000 == 0:
        pipe.execute()
        pipe = r.pipeline()
pipe.execute()

# Benchmark operations
start = time.time()
for _ in range(10000):
    r.zrevrank("leaderboard:bench", "player_999999")
elapsed = time.time() - start
print(f"ZREVRANK: {elapsed/10000*1000:.3f}ms per call")
# ~0.1ms per call

start = time.time()
for _ in range(10000):
    r.zrange("leaderboard:bench", 0, 9, desc=True, withscores=True)
elapsed = time.time() - start
print(f"ZRANGE top 10: {elapsed/10000*1000:.3f}ms per call")
# ~0.1ms per call
```

2 million members. Sub-millisecond for rank lookups and top-N queries. The skip list data structure makes this possible — it's like a linked list with express lanes.

## What You Learned

- **ZADD** — add members with scores, GT/LT for conditional updates
- **ZRANGE** — get members by rank (with REV, WITHSCORES, LIMIT)
- **ZREVRANK** — get a member's rank from the top
- **ZSCORE** — get a member's score
- **ZINCRBY** — atomic score increment
- **ZRANGEBYSCORE** — query by score range
- **ZUNIONSTORE** — combine multiple sorted sets
- **ZCARD** — count members
- **Pipelines** — batch commands to reduce round-trips

The leaderboard now answers "what's my rank?" in under 1ms for 2 million players. No more full table scans. Derek is ecstatic.

But now he wants player profile cards on the leaderboard. Username, avatar, country, last login. "Just fetch the profile for each of the top 100 players." That's 100 individual queries. Even with Redis, 100 round-trips add up.

You need a way to store structured player data — not just a score, but a whole object — and fetch it efficiently.

That's Chapter 3.

---

[← Chapter 1: Your First Key](chapter-01-first-key.md) | [Chapter 3: Player Profiles →](chapter-03-hashes-caching.md)
