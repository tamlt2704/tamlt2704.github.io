# Chapter 3: Indexes — The Right Tool for the Right Query

[← Chapter 2: EXPLAIN ANALYZE](chapter-02-explain-analyze.md) | [Chapter 4: The Planner →](chapter-04-planner.md)

---

## The Fire

Derek is back:

> "The leaderboard page takes 12 seconds. It shows top 100 players by ELO with their match count. Users are rage-quitting before the page loads."

You EXPLAIN the leaderboard query:

```sql
EXPLAIN ANALYZE
SELECT p.username, p.elo_rating, COUNT(m.id) AS wins
FROM players p
LEFT JOIN matches m ON m.winner_id = p.id
GROUP BY p.id, p.username, p.elo_rating
ORDER BY p.elo_rating DESC
LIMIT 100;
```

```
Limit  (actual time=18421.334..18421.340 rows=100)
  -> Sort  (actual time=18421.332..18421.335 rows=100)
        -> HashAggregate  (actual time=18102.445..18389.221 rows=2300000)
              -> Hash Left Join  (actual time=891.223..14521.667 rows=47000000)
                    Hash Cond: (m.winner_id = p.id)
                    -> Seq Scan on matches m  (actual time=0.009..4891.334 rows=47000000)
                    -> Hash  (actual time=889.112..889.112 rows=2300000)
                          -> Seq Scan on players p  (actual time=0.008..612.445 rows=2300000)
```

Two Seq Scans. No indexes on `winner_id`. The join reads all 47M matches. For a page that shows 100 rows.

---

## The Fix: B-tree Indexes

### Basic Index

```sql
-- Index on the foreign key (should have existed from day one)
CREATE INDEX idx_matches_winner_id ON matches (winner_id);
CREATE INDEX idx_matches_player1_id ON matches (player1_id);
CREATE INDEX idx_matches_player2_id ON matches (player2_id);
```

After creating `idx_matches_winner_id`:

```sql
EXPLAIN ANALYZE
SELECT * FROM matches WHERE winner_id = 42;
```

```
Index Scan using idx_matches_winner_id on matches
    (cost=0.56..124.89 rows=22 width=89)
    (actual time=0.028..0.091 rows=20 loops=1)
  Index Cond: (winner_id = 42)
Planning Time: 0.134 ms
Execution Time: 0.121 ms
```

From Seq Scan (4.3 seconds) to Index Scan (0.12ms).

### Composite Index (Multi-Column)

Derek's leaderboard also filters by game mode:

```sql
-- Players want "Top 100 in Ranked mode"
SELECT p.username, p.elo_rating
FROM players p
JOIN matches m ON m.winner_id = p.id
WHERE m.game_mode = 'ranked'
  AND m.status = 'completed'
GROUP BY p.id, p.username, p.elo_rating
ORDER BY p.elo_rating DESC
LIMIT 100;
```

A composite index handles both conditions:

```sql
CREATE INDEX idx_matches_mode_status_winner
ON matches (game_mode, status, winner_id);
```

Column order matters. Put the **equality conditions first**, then range/join columns:

```
game_mode = 'ranked'    → equality (first)
status = 'completed'    → equality (second)
winner_id               → used for the join (third)
```

### Covering Index (INCLUDE)

An **Index Only Scan** is faster than an Index Scan because it never touches the table. But it only works if all columns you SELECT are in the index.

```sql
-- The leaderboard only needs username and elo_rating from players
CREATE INDEX idx_players_elo_covering
ON players (elo_rating DESC)
INCLUDE (username);
```

```sql
EXPLAIN ANALYZE
SELECT username, elo_rating FROM players ORDER BY elo_rating DESC LIMIT 100;
```

```
Limit  (actual time=0.021..0.042 rows=100)
  -> Index Only Scan using idx_players_elo_covering on players
        (actual time=0.019..0.038 rows=100)
        Heap Fetches: 0
```

`Heap Fetches: 0` — it never touched the table. Pure index read.

### Partial Index

Most matches are completed. Active matches are rare but queried constantly:

```sql
-- Only index the rows that matter
CREATE INDEX idx_matches_active
ON matches (player1_id, player2_id)
WHERE status = 'active';
```

This index covers only ~0.1% of the table (active matches). It's tiny and fast:

```sql
EXPLAIN ANALYZE
SELECT * FROM matches
WHERE status = 'active' AND player1_id = 42;
```

```
Index Scan using idx_matches_active on matches
    (cost=0.29..8.31 rows=1 width=89)
    (actual time=0.015..0.016 rows=1 loops=1)
  Index Cond: (player1_id = 42)
```

Full index on `matches`: ~1.2 GB. Partial index on active matches: ~2 MB.

---

## Index-Only Scans: The Holy Grail

For an Index Only Scan to work:

1. All columns in SELECT must be in the index (or INCLUDEd)
2. The visibility map must be up-to-date (VACUUM keeps it fresh)

```sql
-- Check if your index supports index-only scans
EXPLAIN ANALYZE
SELECT player1_id, player2_id, status
FROM matches
WHERE game_mode = 'ranked' AND status = 'completed';
```

If you see `Heap Fetches: 47291` — that means the visibility map is stale. Run:

```sql
VACUUM matches;
```

Then re-run. `Heap Fetches` should drop to 0 (or near 0).

---

## When NOT to Index

Indexes aren't free. Each index:
- Takes disk space
- Slows down INSERT/UPDATE/DELETE (must update the index too)
- Can confuse the planner if there are too many choices

Don't index:
- Columns with very low cardinality (e.g., `status` with 4 values on a 47M row table — unless partial)
- Tables with fewer than 10,000 rows (Seq Scan is fine)
- Columns that are never in WHERE, JOIN, or ORDER BY

### Check Index Usage

```sql
-- Which indexes are never used?
SELECT
    schemaname, tablename, indexname,
    idx_scan AS times_used,
    pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexrelid NOT IN (
      SELECT conindid FROM pg_constraint WHERE contype IN ('p', 'u')
  )
ORDER BY pg_relation_size(indexrelid) DESC;
```

Unused indexes waste disk and slow writes. Drop them.

---

## The Leaderboard Fix (Complete)

```sql
-- 1. Index for the join
CREATE INDEX idx_matches_winner_id ON matches (winner_id);

-- 2. Covering index for the sort + display
CREATE INDEX idx_players_elo_covering
ON players (elo_rating DESC) INCLUDE (username);

-- 3. Partial index for active match lookups
CREATE INDEX idx_matches_active
ON matches (player1_id, player2_id) WHERE status = 'active';

-- 4. Composite for filtered leaderboards
CREATE INDEX idx_matches_mode_status_winner
ON matches (game_mode, status, winner_id);
```

Leaderboard query: 18 seconds → 45ms. Derek is happy.

---

## Quick Reference

| Index Type | Syntax | Use Case |
|-----------|--------|----------|
| Basic B-tree | `CREATE INDEX idx ON t(col)` | Single-column lookups |
| Composite | `CREATE INDEX idx ON t(a, b, c)` | Multi-column WHERE |
| Covering | `CREATE INDEX idx ON t(a) INCLUDE (b, c)` | Index-only scans |
| Partial | `CREATE INDEX idx ON t(a) WHERE condition` | Subset of rows |
| Unique | `CREATE UNIQUE INDEX idx ON t(a)` | Enforce uniqueness |
| Descending | `CREATE INDEX idx ON t(a DESC)` | ORDER BY DESC |

| Diagnostic | Purpose |
|-----------|---------|
| `pg_stat_user_indexes` | Check index usage (idx_scan) |
| `pg_relation_size(index)` | Index size on disk |
| `EXPLAIN ANALYZE` | Verify index is used |
| `Heap Fetches: 0` | Confirms index-only scan |

---

## Exercises

### Exercise 1: Foreign Key Indexes

The `game_events` table has `match_id` and `player_id` as foreign keys but no indexes. Create appropriate indexes and verify with EXPLAIN ANALYZE:

```sql
-- Your query to test:
SELECT * FROM game_events WHERE match_id = 12345 ORDER BY created_at;
```

### Exercise 2: Composite Index Order

You need to optimize this query:

```sql
SELECT * FROM matches
WHERE game_mode = 'ranked'
  AND status = 'completed'
  AND started_at > now() - interval '7 days'
ORDER BY started_at DESC;
```

What's the optimal column order for a composite index? Why?

### Exercise 3: Find Unused Indexes

Run the unused index query above on your database. If you find any, calculate how much disk space you'd save by dropping them.

---

## What Happens Next

You've added indexes. The leaderboard is fast. But Tuesday morning, Ops Olga reports:

> "The matchmaking query still does a Seq Scan. I can see the index exists. Why isn't Postgres using it?"

The planner has reasons. Next chapter: you learn why Postgres sometimes ignores your index — and what to do about it.

---

[← Chapter 2: EXPLAIN ANALYZE](chapter-02-explain-analyze.md) | [Chapter 4: The Planner →](chapter-04-planner.md)
