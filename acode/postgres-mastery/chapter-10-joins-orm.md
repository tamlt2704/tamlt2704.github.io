# Chapter 10: JOINs & the ORM — Killing the N+1

[← Chapter 9: Full-Text Search](chapter-09-full-text-search.md) | [Chapter 11: Partitioning →](chapter-11-partitioning.md)

---

## The Fire

Friday code review. You open the match history endpoint and see this in the ORM logs:

```
Query 1: SELECT * FROM players WHERE id = 42
Query 2: SELECT * FROM matches WHERE player1_id = 42 OR player2_id = 42 LIMIT 20
Query 3: SELECT * FROM players WHERE id = 108   -- opponent for match 1
Query 4: SELECT * FROM players WHERE id = 291   -- opponent for match 2
Query 5: SELECT * FROM players WHERE id = 445   -- opponent for match 3
...
Query 22: SELECT * FROM players WHERE id = 1892 -- opponent for match 20
```

**22 queries** to load one page. Each match fetches its opponent separately. This is the **N+1 problem**: 1 query for the list + N queries for related data.

Marta sees your screen:

> "The ORM is lazy-loading. It fetches related objects one at a time. You need to teach it to JOIN — or write the SQL yourself."

---

## The N+1 Problem Explained

```python
# ORM pseudocode (the problem)
player = Player.get(id=42)
matches = Match.filter(player1=player).limit(20)

for match in matches:
    opponent = Player.get(id=match.player2_id)  # ← 1 query per match!
    print(f"{player.username} vs {opponent.username}")
```

Each iteration fires a separate query. 20 matches = 20 extra queries.

### The Fix: One Query with JOINs

```sql
-- Replace 22 queries with 1
SELECT
    m.id AS match_id,
    m.started_at,
    m.status,
    m.game_mode,
    p1.username AS player1_name,
    p2.username AS player2_name,
    w.username AS winner_name
FROM matches m
JOIN players p1 ON p1.id = m.player1_id
JOIN players p2 ON p2.id = m.player2_id
LEFT JOIN players w ON w.id = m.winner_id
WHERE m.player1_id = 42 OR m.player2_id = 42
ORDER BY m.started_at DESC
LIMIT 20;
```

One query. One round trip. All data.

---

## JOIN Types Refresher

```sql
-- INNER JOIN: only rows that match in both tables
SELECT p.username, m.id
FROM players p
INNER JOIN matches m ON m.winner_id = p.id;
-- Only players who have won at least one match

-- LEFT JOIN: all rows from left table, NULLs for non-matches
SELECT p.username, m.id
FROM players p
LEFT JOIN matches m ON m.winner_id = p.id;
-- All players, including those who never won

-- RIGHT JOIN: all rows from right table (rarely used)
-- FULL OUTER JOIN: all rows from both tables
```

### JOIN Performance

The planner chooses between three join strategies:

| Strategy | When Used | Good For |
|----------|-----------|----------|
| **Nested Loop** | Small outer table, indexed inner | Selective joins, LIMIT |
| **Hash Join** | Medium tables, no useful index | Equality joins |
| **Merge Join** | Both sides sorted | Large sorted datasets |

```sql
-- Check which join strategy is used
EXPLAIN ANALYZE
SELECT p.username, COUNT(m.id)
FROM players p
JOIN matches m ON m.winner_id = p.id
GROUP BY p.username;
```

---

## EXISTS vs IN vs JOIN

Three ways to write "players who have won a match":

```sql
-- Method 1: IN (subquery)
SELECT username FROM players
WHERE id IN (SELECT DISTINCT winner_id FROM matches);

-- Method 2: EXISTS (correlated subquery)
SELECT username FROM players p
WHERE EXISTS (SELECT 1 FROM matches m WHERE m.winner_id = p.id);

-- Method 3: JOIN
SELECT DISTINCT p.username
FROM players p
JOIN matches m ON m.winner_id = p.id;
```

Performance comparison:

| Method | Best When | Watch Out |
|--------|-----------|-----------|
| `IN` | Subquery returns few rows | Large subquery results can be slow |
| `EXISTS` | Checking existence only | Stops at first match (efficient) |
| `JOIN` | You need data from both tables | May produce duplicates (use DISTINCT) |

**Rule of thumb**: Use `EXISTS` for existence checks. Use `JOIN` when you need columns from both tables.

### Anti-Join: "Players Who Never Won"

```sql
-- NOT EXISTS (usually fastest)
SELECT username FROM players p
WHERE NOT EXISTS (SELECT 1 FROM matches m WHERE m.winner_id = p.id);

-- LEFT JOIN + IS NULL (same plan, different syntax)
SELECT p.username
FROM players p
LEFT JOIN matches m ON m.winner_id = p.id
WHERE m.id IS NULL;

-- NOT IN (dangerous with NULLs!)
SELECT username FROM players
WHERE id NOT IN (SELECT winner_id FROM matches);
-- ⚠️ If winner_id has ANY NULL values, this returns ZERO rows!
```

**Never use NOT IN with a nullable column.** Use NOT EXISTS instead.

---

## Fixing the ORM

### Strategy 1: Eager Loading

```python
# Most ORMs support eager loading
# SQLAlchemy:
matches = session.query(Match)\
    .options(joinedload(Match.player1), joinedload(Match.player2))\
    .filter(or_(Match.player1_id == 42, Match.player2_id == 42))\
    .limit(20).all()

# Django:
matches = Match.objects.select_related('player1', 'player2', 'winner')\
    .filter(Q(player1_id=42) | Q(player2_id=42))[:20]

# Prisma:
const matches = await prisma.match.findMany({
    where: { OR: [{ player1Id: 42 }, { player2Id: 42 }] },
    include: { player1: true, player2: true, winner: true },
    take: 20
});
```

### Strategy 2: Raw SQL for Complex Queries

```python
# When the ORM generates bad SQL, write it yourself
query = """
    SELECT
        m.id, m.started_at, m.game_mode,
        p1.username AS player1_name,
        p2.username AS player2_name,
        CASE WHEN m.winner_id = %s THEN 'won' ELSE 'lost' END AS result
    FROM matches m
    JOIN players p1 ON p1.id = m.player1_id
    JOIN players p2 ON p2.id = m.player2_id
    WHERE m.player1_id = %s OR m.player2_id = %s
    ORDER BY m.started_at DESC
    LIMIT 20
"""
results = db.execute(query, [player_id, player_id, player_id])
```

### Strategy 3: Database Views

```sql
-- Create a view that the ORM can query as a single "table"
CREATE VIEW match_details AS
SELECT
    m.id,
    m.started_at,
    m.ended_at,
    m.status,
    m.game_mode,
    p1.username AS player1_name,
    p1.elo_rating AS player1_elo,
    p2.username AS player2_name,
    p2.elo_rating AS player2_elo,
    w.username AS winner_name
FROM matches m
JOIN players p1 ON p1.id = m.player1_id
JOIN players p2 ON p2.id = m.player2_id
LEFT JOIN players w ON w.id = m.winner_id;
```

---

## Detecting N+1 in Production

```sql
-- Find repeated similar queries (sign of N+1)
SELECT
    substring(query, 1, 80) AS pattern,
    calls,
    round(mean_exec_time::numeric, 3) AS mean_ms,
    rows / calls AS rows_per_call
FROM pg_stat_statements
WHERE calls > 1000
  AND rows / NULLIF(calls, 0) <= 1  -- Returns 1 row per call = likely N+1
ORDER BY calls DESC
LIMIT 10;
```

If you see a query called 50,000 times that returns 1 row each time — that's an N+1.

---

## Quick Reference

| Pattern | SQL | Use When |
|---------|-----|----------|
| Inner Join | `JOIN t ON condition` | Need matching rows from both |
| Left Join | `LEFT JOIN t ON condition` | Keep all left rows |
| EXISTS | `WHERE EXISTS (SELECT 1 ...)` | Existence check (fast) |
| NOT EXISTS | `WHERE NOT EXISTS (...)` | Anti-join (safe with NULLs) |
| IN | `WHERE col IN (SELECT ...)` | Small subquery results |

| ORM Fix | Method |
|---------|--------|
| Eager loading | `select_related` / `joinedload` / `include` |
| Batch loading | `prefetch_related` / `subqueryload` |
| Raw SQL | For complex queries the ORM can't optimize |
| Views | Encapsulate JOINs for ORM consumption |

| N+1 Detection | Signal |
|---------------|--------|
| High `calls`, low `rows/call` | Repeated single-row fetches |
| ORM debug log shows many queries | Lazy loading in a loop |
| `pg_stat_statements` patterns | Same query template, thousands of calls |

---

## Exercises

### Exercise 1: Rewrite the N+1

The leaderboard endpoint runs these queries:
1. `SELECT * FROM players ORDER BY elo_rating DESC LIMIT 50`
2. For each player: `SELECT COUNT(*) FROM matches WHERE winner_id = ?`

Rewrite as a single query using a JOIN and GROUP BY.

### Exercise 2: EXISTS vs IN

Write both versions of "find all players who played a match in the last 24 hours." Compare their EXPLAIN plans. Which is faster?

### Exercise 3: ORM Audit

Look at `pg_stat_statements` and find queries that:
- Are called more than 10,000 times
- Return 1 row per call
- Have a mean time under 1ms

These are likely N+1 candidates. Write the equivalent single JOIN query.

---

## What Happens Next

Week one is done. The database is faster. But the `game_events` table keeps growing — 890 million rows and counting. Queries on old events are slowing down queries on recent events.

Ops Olga:

> "The game_events table is 890 million rows. It grows 3 million per day. We can't keep scanning the whole thing."

Time to partition.

---

[← Chapter 9: Full-Text Search](chapter-09-full-text-search.md) | [Chapter 11: Partitioning →](chapter-11-partitioning.md)
