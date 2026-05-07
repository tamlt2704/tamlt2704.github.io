# Chapter 6: Advanced Queries — CTEs, Recursive Queries, and LATERAL

[← Chapter 5: VACUUM](chapter-05-vacuum.md) | [Chapter 7: Window Functions →](chapter-07-window-functions.md)

---

## The Fire

Thursday. Marta needs a report for CEO Chad:

> "Show me the top 10 players by win rate, but only count players with at least 50 matches. Include their most recent match date and their average match duration. One query. The investors meeting is in 2 hours."

You try to write it as a single SELECT. It becomes a nested mess of subqueries. The query is 40 lines long and takes 90 seconds.

Marta glances at your screen:

> "Use a CTE. Break it into steps. Postgres optimizes them well since version 12."

---

## CTEs (Common Table Expressions)

A CTE is a named temporary result set. Think of it as a "query variable":

```sql
WITH player_stats AS (
    SELECT
        winner_id AS player_id,
        COUNT(*) AS wins
    FROM matches
    WHERE status = 'completed'
    GROUP BY winner_id
),
match_counts AS (
    SELECT
        p.id AS player_id,
        COUNT(m.id) AS total_matches
    FROM players p
    JOIN matches m ON m.player1_id = p.id OR m.player2_id = p.id
    WHERE m.status = 'completed'
    GROUP BY p.id
    HAVING COUNT(m.id) >= 50
)
SELECT
    p.username,
    ps.wins,
    mc.total_matches,
    round(ps.wins::numeric / mc.total_matches * 100, 1) AS win_rate_pct
FROM players p
JOIN player_stats ps ON ps.player_id = p.id
JOIN match_counts mc ON mc.player_id = p.id
ORDER BY win_rate_pct DESC
LIMIT 10;
```

Each CTE runs once, and subsequent CTEs (or the final SELECT) can reference earlier ones.

### CTE vs Subquery

```sql
-- Subquery (harder to read, same performance in most cases)
SELECT username, wins, total, round(wins::numeric / total * 100, 1)
FROM players p
JOIN (SELECT winner_id, COUNT(*) AS wins FROM matches WHERE status = 'completed' GROUP BY winner_id) ps
  ON ps.winner_id = p.id
JOIN (SELECT ... ) mc ON ...

-- CTE (readable, debuggable, same plan since PG 12)
WITH player_stats AS (...)
SELECT ...
```

Since PostgreSQL 12, CTEs are **inlined** by default (the planner can push filters into them). Before PG 12, CTEs were optimization fences.

### MATERIALIZED CTEs

If you *want* the CTE to execute once and cache results:

```sql
WITH MATERIALIZED expensive_calc AS (
    SELECT player_id, complex_aggregation(...)
    FROM game_events
    GROUP BY player_id
)
SELECT * FROM expensive_calc WHERE player_id IN (1, 2, 3);
```

Use `MATERIALIZED` when the CTE is referenced multiple times and is expensive to compute.

---

## Recursive CTEs

CEO Chad wants a "referral chain" feature — players who invited other players, forming a tree:

```sql
-- Assume players.profile->>'referred_by' stores the referrer's player ID
WITH RECURSIVE referral_chain AS (
    -- Base case: start with a specific player
    SELECT
        id,
        username,
        (profile->>'referred_by')::bigint AS referred_by,
        1 AS depth
    FROM players
    WHERE id = 42

    UNION ALL

    -- Recursive case: find who they referred
    SELECT
        p.id,
        p.username,
        (p.profile->>'referred_by')::bigint,
        rc.depth + 1
    FROM players p
    JOIN referral_chain rc ON (p.profile->>'referred_by')::bigint = rc.id
    WHERE rc.depth < 10  -- Safety limit!
)
SELECT * FROM referral_chain ORDER BY depth;
```

Output:

```
 id  | username    | referred_by | depth
-----+-------------+-------------+-------
  42 | ProGamer42  | NULL        |     1
 108 | NewbieNick  | 42          |     2
 291 | CasualCarl  | 42          |     2
 445 | SpeedySteve | 108         |     3
```

**Always include a depth limit** in recursive CTEs. Without it, circular references cause infinite loops.

### Recursive CTE for Match Streaks

Find the longest win streak for a player:

```sql
WITH ordered_matches AS (
    SELECT
        id,
        winner_id,
        player1_id,
        player2_id,
        ended_at,
        ROW_NUMBER() OVER (
            PARTITION BY CASE WHEN player1_id = 42 THEN 42 ELSE player2_id END
            ORDER BY ended_at
        ) AS match_num
    FROM matches
    WHERE (player1_id = 42 OR player2_id = 42)
      AND status = 'completed'
    ORDER BY ended_at
),
streaks AS (
    SELECT
        match_num,
        winner_id,
        match_num - ROW_NUMBER() OVER (ORDER BY match_num) AS streak_group
    FROM ordered_matches
    WHERE winner_id = 42
)
SELECT
    COUNT(*) AS streak_length,
    MIN(match_num) AS streak_start,
    MAX(match_num) AS streak_end
FROM streaks
GROUP BY streak_group
ORDER BY streak_length DESC
LIMIT 1;
```

---

## LATERAL Joins

A LATERAL join lets the subquery reference columns from preceding tables. It's like a "for each row" loop but optimized:

### Top 3 Recent Matches Per Player

```sql
-- "For each of the top 10 players, show their 3 most recent matches"
SELECT
    p.username,
    p.elo_rating,
    recent.started_at,
    recent.game_mode,
    recent.status
FROM players p
CROSS JOIN LATERAL (
    SELECT m.started_at, m.game_mode, m.status
    FROM matches m
    WHERE m.player1_id = p.id OR m.player2_id = p.id
    ORDER BY m.started_at DESC
    LIMIT 3
) recent
WHERE p.elo_rating > 2000
ORDER BY p.elo_rating DESC, recent.started_at DESC;
```

Without LATERAL, you'd need a window function or a correlated subquery. LATERAL is cleaner and often faster.

### LATERAL with Aggregates

```sql
-- For each player, get their stats from the last 30 days
SELECT
    p.username,
    stats.matches_played,
    stats.wins,
    stats.avg_duration
FROM players p
CROSS JOIN LATERAL (
    SELECT
        COUNT(*) AS matches_played,
        COUNT(*) FILTER (WHERE m.winner_id = p.id) AS wins,
        AVG(EXTRACT(EPOCH FROM (m.ended_at - m.started_at))) AS avg_duration
    FROM matches m
    WHERE (m.player1_id = p.id OR m.player2_id = p.id)
      AND m.started_at > now() - interval '30 days'
      AND m.status = 'completed'
) stats
WHERE p.elo_rating > 1800
ORDER BY stats.wins DESC
LIMIT 20;
```

---

## Subqueries in FROM

Sometimes a simple subquery in FROM is all you need:

```sql
-- Average match duration by game mode
SELECT
    game_mode,
    round(avg_duration_sec / 60.0, 1) AS avg_minutes,
    match_count
FROM (
    SELECT
        game_mode,
        AVG(EXTRACT(EPOCH FROM (ended_at - started_at))) AS avg_duration_sec,
        COUNT(*) AS match_count
    FROM matches
    WHERE status = 'completed'
      AND ended_at IS NOT NULL
    GROUP BY game_mode
) mode_stats
WHERE match_count > 1000
ORDER BY avg_minutes DESC;
```

---

## Marta's Report (Complete Solution)

```sql
WITH player_wins AS (
    SELECT winner_id AS player_id, COUNT(*) AS wins
    FROM matches
    WHERE status = 'completed'
    GROUP BY winner_id
),
player_matches AS (
    SELECT
        p.id AS player_id,
        COUNT(*) AS total_matches,
        MAX(m.ended_at) AS last_match,
        AVG(EXTRACT(EPOCH FROM (m.ended_at - m.started_at))) AS avg_duration_sec
    FROM players p
    JOIN matches m ON m.player1_id = p.id OR m.player2_id = p.id
    WHERE m.status = 'completed'
    GROUP BY p.id
    HAVING COUNT(*) >= 50
)
SELECT
    p.username,
    pw.wins,
    pm.total_matches,
    round(pw.wins::numeric / pm.total_matches * 100, 1) AS win_rate,
    pm.last_match,
    round(pm.avg_duration_sec / 60.0, 1) AS avg_match_minutes
FROM players p
JOIN player_wins pw ON pw.player_id = p.id
JOIN player_matches pm ON pm.player_id = p.id
ORDER BY win_rate DESC
LIMIT 10;
```

---

## Quick Reference

| Pattern | Syntax | Use Case |
|---------|--------|----------|
| CTE | `WITH name AS (SELECT ...) SELECT ...` | Break complex queries into steps |
| Materialized CTE | `WITH MATERIALIZED name AS (...)` | Force single execution |
| Recursive CTE | `WITH RECURSIVE name AS (base UNION ALL recursive)` | Trees, graphs, sequences |
| LATERAL | `CROSS JOIN LATERAL (SELECT ... WHERE ref)` | Per-row subqueries |
| Subquery in FROM | `FROM (SELECT ...) alias` | Inline derived tables |

| Tip | Detail |
|-----|--------|
| Always limit recursion depth | `WHERE depth < N` prevents infinite loops |
| CTEs inline since PG 12 | No performance penalty vs subqueries |
| LATERAL needs an index | The inner query runs per outer row |
| Use EXPLAIN on CTEs | Verify the planner inlines them |

---

## Exercises

### Exercise 1: Player Activity Report

Write a CTE-based query that shows:
- Each player's total matches, wins, and losses
- Their win rate (only for players with 20+ matches)
- Sorted by win rate descending

### Exercise 2: Recursive Depth

Using a recursive CTE, generate a series of "ELO brackets" (1000-1099, 1100-1199, ..., 2900-2999) and count how many players fall into each bracket.

### Exercise 3: LATERAL Top-N

For each game mode, find the top 5 players by win count using a LATERAL join. Compare the EXPLAIN plan to a window function approach.

---

## What Happens Next

CTEs handle the structure. But Marta's next request needs something CTEs can't do alone:

> "Show each player's rank within their ELO bracket, their percentile, and whether they're on a winning or losing streak compared to last week."

That's window functions territory.

---

[← Chapter 5: VACUUM](chapter-05-vacuum.md) | [Chapter 7: Window Functions →](chapter-07-window-functions.md)
