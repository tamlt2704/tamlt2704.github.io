# Chapter 7: Window Functions — Rank, Streak, and Running Totals

[← Chapter 6: Advanced Queries](chapter-06-advanced-queries.md) | [Chapter 8: JSONB →](chapter-08-jsonb.md)

---

## The Fire

CEO Chad wants a "Player Stats" page for the tournament:

> "I want to see each player's rank in their bracket, their percentile, their current win/loss streak, and a sparkline of matches per week. The investors love sparklines."

Derek translates:

> "So... ROW_NUMBER, PERCENT_RANK, LAG for streaks, and a running count partitioned by week. Can Postgres do that in one query?"

Marta smiles:

> "Window functions. One pass over the data, multiple calculations."

---

## Window Functions: The Basics

A window function computes a value across a set of rows **without collapsing them** (unlike GROUP BY):

```sql
-- GROUP BY: collapses rows
SELECT game_mode, COUNT(*) FROM matches GROUP BY game_mode;
-- Returns 4 rows (one per game_mode)

-- Window function: keeps all rows, adds a computed column
SELECT
    id, game_mode, started_at,
    COUNT(*) OVER (PARTITION BY game_mode) AS mode_total
FROM matches;
-- Returns 47M rows, each with its mode's total count
```

---

## ROW_NUMBER, RANK, DENSE_RANK

### Player Rankings Within ELO Brackets

```sql
SELECT
    username,
    elo_rating,
    CASE
        WHEN elo_rating BETWEEN 1000 AND 1499 THEN 'Bronze'
        WHEN elo_rating BETWEEN 1500 AND 1799 THEN 'Silver'
        WHEN elo_rating BETWEEN 1800 AND 2099 THEN 'Gold'
        ELSE 'Diamond'
    END AS bracket,
    ROW_NUMBER() OVER (
        PARTITION BY CASE
            WHEN elo_rating BETWEEN 1000 AND 1499 THEN 'Bronze'
            WHEN elo_rating BETWEEN 1500 AND 1799 THEN 'Silver'
            WHEN elo_rating BETWEEN 1800 AND 2099 THEN 'Gold'
            ELSE 'Diamond'
        END
        ORDER BY elo_rating DESC
    ) AS rank_in_bracket
FROM players
WHERE elo_rating >= 1000;
```

The differences:

| Function | Ties | Gaps | Example (scores: 100, 100, 90) |
|----------|------|------|-------------------------------|
| `ROW_NUMBER()` | Breaks ties arbitrarily | No gaps | 1, 2, 3 |
| `RANK()` | Same rank for ties | Gaps after ties | 1, 1, 3 |
| `DENSE_RANK()` | Same rank for ties | No gaps | 1, 1, 2 |

```sql
-- Percentile ranking
SELECT
    username,
    elo_rating,
    PERCENT_RANK() OVER (ORDER BY elo_rating) AS percentile,
    NTILE(100) OVER (ORDER BY elo_rating) AS percentile_bucket
FROM players;
```

---

## LAG and LEAD — Comparing Adjacent Rows

### ELO Change From Previous Match

```sql
-- Show each player's ELO change after each match
WITH match_results AS (
    SELECT
        m.id AS match_id,
        m.winner_id,
        m.ended_at,
        p.id AS player_id,
        p.elo_rating
    FROM matches m
    JOIN players p ON p.id = m.winner_id
    WHERE m.status = 'completed'
      AND m.winner_id = 42
    ORDER BY m.ended_at
)
SELECT
    match_id,
    ended_at,
    elo_rating,
    LAG(elo_rating) OVER (ORDER BY ended_at) AS prev_elo,
    elo_rating - LAG(elo_rating) OVER (ORDER BY ended_at) AS elo_change
FROM match_results;
```

```
 match_id |      ended_at       | elo_rating | prev_elo | elo_change
----------+---------------------+------------+----------+------------
    12001 | 2024-01-15 10:22:00 |       1450 |     NULL |       NULL
    12089 | 2024-01-15 11:05:00 |       1465 |     1450 |         15
    12201 | 2024-01-15 14:30:00 |       1458 |     1465 |         -7
    12445 | 2024-01-16 09:12:00 |       1472 |     1458 |         14
```

### Win/Loss Streak Detection

```sql
WITH player_matches AS (
    SELECT
        m.id,
        m.ended_at,
        CASE WHEN m.winner_id = 42 THEN 'W' ELSE 'L' END AS result
    FROM matches m
    WHERE (m.player1_id = 42 OR m.player2_id = 42)
      AND m.status = 'completed'
    ORDER BY m.ended_at DESC
    LIMIT 20
),
streaks AS (
    SELECT
        result,
        ended_at,
        ROW_NUMBER() OVER (ORDER BY ended_at DESC) -
        ROW_NUMBER() OVER (PARTITION BY result ORDER BY ended_at DESC) AS streak_group
    FROM player_matches
)
SELECT
    result,
    COUNT(*) AS streak_length
FROM streaks
WHERE streak_group = 0
GROUP BY result, streak_group
ORDER BY MIN(ended_at) DESC
LIMIT 1;
```

---

## Running Totals and Moving Averages

### Matches Per Week (Running Total)

```sql
SELECT
    date_trunc('week', started_at) AS week,
    COUNT(*) AS matches_this_week,
    SUM(COUNT(*)) OVER (ORDER BY date_trunc('week', started_at)) AS cumulative_matches
FROM matches
WHERE status = 'completed'
  AND started_at > now() - interval '12 weeks'
GROUP BY date_trunc('week', started_at)
ORDER BY week;
```

### 7-Day Moving Average of Match Duration

```sql
SELECT
    date_trunc('day', ended_at) AS day,
    round(AVG(EXTRACT(EPOCH FROM (ended_at - started_at)) / 60.0), 1) AS avg_minutes,
    round(
        AVG(AVG(EXTRACT(EPOCH FROM (ended_at - started_at)) / 60.0))
        OVER (ORDER BY date_trunc('day', ended_at) ROWS BETWEEN 6 PRECEDING AND CURRENT ROW),
        1
    ) AS moving_avg_7d
FROM matches
WHERE status = 'completed' AND ended_at IS NOT NULL
GROUP BY date_trunc('day', ended_at)
ORDER BY day DESC
LIMIT 30;
```

---

## Frame Clauses

The `OVER` clause can specify exactly which rows to include:

```sql
-- Syntax
function() OVER (
    PARTITION BY ...
    ORDER BY ...
    ROWS BETWEEN start AND end
)
```

| Frame | Meaning |
|-------|---------|
| `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` | All rows from start to here (default for ORDER BY) |
| `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` | Last 7 rows (sliding window) |
| `ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING` | Here to end |
| `RANGE BETWEEN ...` | Based on value ranges, not row counts |

### Example: Best 5-Match Stretch

```sql
-- Find the 5-match window with the highest win rate for player 42
WITH player_results AS (
    SELECT
        m.ended_at,
        CASE WHEN m.winner_id = 42 THEN 1 ELSE 0 END AS won
    FROM matches m
    WHERE (m.player1_id = 42 OR m.player2_id = 42)
      AND m.status = 'completed'
    ORDER BY m.ended_at
)
SELECT
    ended_at,
    won,
    SUM(won) OVER (ORDER BY ended_at ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS wins_in_5,
    ROW_NUMBER() OVER (ORDER BY ended_at) AS match_num
FROM player_results
ORDER BY wins_in_5 DESC NULLS LAST
LIMIT 1;
```

---

## PARTITION BY — Separate Windows

```sql
-- Rank players within each game mode by win count
SELECT
    p.username,
    m.game_mode,
    COUNT(*) AS wins,
    RANK() OVER (PARTITION BY m.game_mode ORDER BY COUNT(*) DESC) AS mode_rank
FROM matches m
JOIN players p ON p.id = m.winner_id
WHERE m.status = 'completed'
GROUP BY p.username, m.game_mode
HAVING COUNT(*) >= 10;
```

---

## Chad's Player Stats Page (Complete)

```sql
WITH player_data AS (
    SELECT
        p.id,
        p.username,
        p.elo_rating,
        COUNT(m.id) AS total_matches,
        COUNT(m.id) FILTER (WHERE m.winner_id = p.id) AS wins
    FROM players p
    JOIN matches m ON m.player1_id = p.id OR m.player2_id = p.id
    WHERE m.status = 'completed'
    GROUP BY p.id, p.username, p.elo_rating
    HAVING COUNT(m.id) >= 20
)
SELECT
    username,
    elo_rating,
    total_matches,
    wins,
    round(wins::numeric / total_matches * 100, 1) AS win_rate,
    RANK() OVER (ORDER BY elo_rating DESC) AS global_rank,
    PERCENT_RANK() OVER (ORDER BY elo_rating) AS percentile,
    NTILE(4) OVER (ORDER BY elo_rating) AS quartile
FROM player_data
ORDER BY elo_rating DESC
LIMIT 100;
```

---

## Quick Reference

| Function | Purpose | Example |
|----------|---------|---------|
| `ROW_NUMBER()` | Unique sequential number | Pagination, deduplication |
| `RANK()` | Rank with gaps | Leaderboards |
| `DENSE_RANK()` | Rank without gaps | Bracket placement |
| `PERCENT_RANK()` | Percentile (0-1) | "Top 5% of players" |
| `NTILE(n)` | Divide into n buckets | Quartiles, deciles |
| `LAG(col, n)` | Value n rows back | Previous match result |
| `LEAD(col, n)` | Value n rows ahead | Next scheduled match |
| `SUM() OVER (ORDER BY ...)` | Running total | Cumulative stats |
| `AVG() OVER (ROWS BETWEEN ...)` | Moving average | Trend lines |
| `FIRST_VALUE()` / `LAST_VALUE()` | First/last in window | Season opener/closer |

---

## Exercises

### Exercise 1: Leaderboard with Rank

Write a query that shows the top 50 players with their global rank, win count, and the ELO difference from the player ranked above them (use LAG).

### Exercise 2: Weekly Growth

Calculate the week-over-week growth rate of new player signups. Show each week's count, the previous week's count (LAG), and the percentage change.

### Exercise 3: Streak Finder

Find the top 10 longest win streaks across all players. Show the player's username, streak length, and the dates of the streak's first and last match.

---

## What Happens Next

The stats page is live. But Derek has another request:

> "Players want custom profiles — favorite color, bio, social links, preferred game settings. The schema changes every sprint. Can we just use JSON?"

Next chapter: JSONB — when to use it, how to query it, and how to index it.

---

[← Chapter 6: Advanced Queries](chapter-06-advanced-queries.md) | [Chapter 8: JSONB →](chapter-08-jsonb.md)
