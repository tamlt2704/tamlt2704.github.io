# Chapter 8: JSONB — Flexible Data Without the Chaos

[← Chapter 7: Window Functions](chapter-07-window-functions.md) | [Chapter 9: Full-Text Search →](chapter-09-full-text-search.md)

---

## The Fire

Derek's sprint planning:

> "Players want custom profiles. Bio, social links, favorite color, preferred game settings, achievement badges. The design changes every two weeks. I can't keep adding columns."

The `players.profile` column is already JSONB. But nobody's querying it efficiently. The matchmaking service filters by `profile->>'preferred_mode'` and it's doing a Seq Scan on 2.3 million rows:

```sql
EXPLAIN ANALYZE
SELECT id, username FROM players
WHERE profile->>'preferred_mode' = 'ranked';
```

```
Seq Scan on players  (cost=0.00..89421.00 rows=11500 width=58)
                     (actual time=0.034..1891.445 rows=184201 loops=1)
  Filter: ((profile ->> 'preferred_mode'::text) = 'ranked'::text)
  Rows Removed by Filter: 2115799
```

1.9 seconds to find ranked players. Every time someone queues for a match.

---

## JSONB Operators

### Extraction Operators

```sql
-- -> returns JSONB (keeps the JSON type)
SELECT profile->'settings' FROM players WHERE id = 42;
-- {"theme": "dark", "sound": true}

-- ->> returns TEXT (extracts as string)
SELECT profile->>'preferred_mode' FROM players WHERE id = 42;
-- "ranked"

-- #> path extraction (nested)
SELECT profile#>'{settings,theme}' FROM players WHERE id = 42;
-- "dark"

-- #>> path extraction as text
SELECT profile#>>'{settings,theme}' FROM players WHERE id = 42;
-- dark
```

### Containment Operators

```sql
-- @> "contains" (left contains right)
SELECT * FROM players
WHERE profile @> '{"preferred_mode": "ranked"}';

-- <@ "is contained by"
SELECT * FROM players
WHERE '{"preferred_mode": "ranked", "level": "pro"}' <@ profile;

-- ? "key exists"
SELECT * FROM players WHERE profile ? 'social_links';

-- ?| "any key exists"
SELECT * FROM players WHERE profile ?| array['twitter', 'discord'];

-- ?& "all keys exist"
SELECT * FROM players WHERE profile ?& array['bio', 'avatar_url'];
```

### Modification

```sql
-- || merge (right overwrites left)
UPDATE players
SET profile = profile || '{"preferred_mode": "casual", "theme": "dark"}'
WHERE id = 42;

-- - remove key
UPDATE players
SET profile = profile - 'deprecated_field'
WHERE id = 42;

-- #- remove nested key
UPDATE players
SET profile = profile #- '{settings,old_option}'
WHERE id = 42;

-- jsonb_set (update nested value)
UPDATE players
SET profile = jsonb_set(profile, '{settings,theme}', '"light"')
WHERE id = 42;
```

---

## GIN Indexes on JSONB

The fix for the Seq Scan:

### Option 1: GIN Index (General)

```sql
-- Indexes ALL keys and values in the JSONB column
CREATE INDEX idx_players_profile_gin ON players USING gin (profile);
```

Now containment queries use the index:

```sql
EXPLAIN ANALYZE
SELECT id, username FROM players
WHERE profile @> '{"preferred_mode": "ranked"}';
```

```
Bitmap Heap Scan on players  (cost=412.23..8921.45 rows=184201 width=58)
                             (actual time=12.334..89.221 rows=184201 loops=1)
  Recheck Cond: (profile @> '{"preferred_mode": "ranked"}'::jsonb)
  -> Bitmap Index Scan on idx_players_profile_gin
        (cost=0.00..366.18 rows=184201 width=0)
        (actual time=11.891..11.891 rows=184201 loops=1)
```

From 1.9 seconds to 89ms.

### Option 2: Expression Index (Specific Key)

If you only query one key, a B-tree expression index is smaller and faster:

```sql
-- Index just the preferred_mode value
CREATE INDEX idx_players_preferred_mode
ON players ((profile->>'preferred_mode'));
```

```sql
EXPLAIN ANALYZE
SELECT id, username FROM players
WHERE profile->>'preferred_mode' = 'ranked';
```

```
Index Scan using idx_players_preferred_mode on players
    (cost=0.43..4821.23 rows=184201 width=58)
    (actual time=0.028..45.112 rows=184201 loops=1)
```

Even faster — 45ms. But only works for that specific key.

### Option 3: GIN with jsonb_path_ops

```sql
-- Smaller index, only supports @> operator
CREATE INDEX idx_players_profile_pathops
ON players USING gin (profile jsonb_path_ops);
```

`jsonb_path_ops` creates a smaller index but only supports `@>` (containment). No `?` or `?|` support.

---

## When to Use JSONB vs Normalized Columns

| Use JSONB When | Use Columns When |
|----------------|------------------|
| Schema changes frequently | Schema is stable |
| Data is optional/sparse | Data is required for most rows |
| You query by containment (`@>`) | You need range queries (`>`, `<`, `BETWEEN`) |
| Different rows have different keys | All rows have the same structure |
| You don't JOIN on the values | You JOIN or GROUP BY the values |

### The PingPong Rule

```sql
-- GOOD: profile is JSONB (varies per player, changes often)
players.profile = {
    "bio": "I love ping pong",
    "social": {"twitter": "@player42", "discord": "player42#1234"},
    "settings": {"theme": "dark", "sound_enabled": true},
    "achievements": ["first_win", "streak_10", "tournament_champion"]
}

-- BAD: match data as JSONB (structured, queried constantly, needs JOINs)
-- Don't do this:
matches.data = {"player1": 42, "player2": 99, "winner": 42, "mode": "ranked"}
-- Use proper columns instead
```

---

## Querying JSONB Arrays

The `game_events.payload` column stores event-specific data:

```sql
-- Example payloads:
-- {"score": 11, "opponent_score": 9, "rally_length": 23}
-- {"achievement": "first_win", "unlocked_at": "2024-01-15"}
-- {"items_used": ["speed_boost", "shield"], "duration": 45}

-- Find events where a specific item was used
SELECT * FROM game_events
WHERE payload->'items_used' ? 'speed_boost';

-- Find events with score > 10
SELECT * FROM game_events
WHERE (payload->>'score')::int > 10;

-- Expand array elements
SELECT
    ge.id,
    jsonb_array_elements_text(ge.payload->'items_used') AS item
FROM game_events ge
WHERE ge.event_type = 'power_up';
```

### Aggregate JSONB

```sql
-- Build a JSON summary per player
SELECT
    player_id,
    jsonb_object_agg(event_type, event_count) AS event_summary
FROM (
    SELECT player_id, event_type, COUNT(*) AS event_count
    FROM game_events
    GROUP BY player_id, event_type
) sub
GROUP BY player_id
LIMIT 5;
```

---

## Performance Patterns

### Pattern: Partial GIN Index

Only index profiles that have a specific key:

```sql
-- Only index players who have set a preferred_mode
CREATE INDEX idx_players_profile_mode_gin
ON players USING gin (profile)
WHERE profile ? 'preferred_mode';
```

### Pattern: Generated Column + Index

For frequently queried JSONB keys, extract to a generated column:

```sql
ALTER TABLE players
ADD COLUMN preferred_mode TEXT
GENERATED ALWAYS AS (profile->>'preferred_mode') STORED;

CREATE INDEX idx_players_pref_mode ON players (preferred_mode);
```

Now you can query it like a regular column with full B-tree index support.

---

## Quick Reference

| Operator | Purpose | Example |
|----------|---------|---------|
| `->` | Get JSONB value by key | `profile->'settings'` |
| `->>` | Get TEXT value by key | `profile->>'bio'` |
| `#>` | Get JSONB by path | `profile#>'{settings,theme}'` |
| `#>>` | Get TEXT by path | `profile#>>'{settings,theme}'` |
| `@>` | Contains | `profile @> '{"mode":"ranked"}'` |
| `?` | Key exists | `profile ? 'bio'` |
| `?|` | Any key exists | `profile ?| array['a','b']` |
| `?&` | All keys exist | `profile ?& array['a','b']` |
| `||` | Merge/concatenate | `profile || '{"new":"val"}'` |
| `-` | Remove key | `profile - 'old_key'` |

| Index Type | Supports | Size |
|-----------|----------|------|
| `GIN (col)` | `@>`, `?`, `?|`, `?&` | Large |
| `GIN (col jsonb_path_ops)` | `@>` only | Smaller |
| `B-tree ((col->>'key'))` | `=`, `<`, `>`, `BETWEEN` | Smallest |

---

## Exercises

### Exercise 1: Profile Search

Create a GIN index on `players.profile` and write a query that finds all players who:
- Have a Discord social link
- Prefer "ranked" mode
- Have the "tournament_champion" achievement

### Exercise 2: Event Payload Analysis

Write a query that finds the average score from `game_events` where `event_type = 'match_end'` and the payload contains a `score` key. Use an appropriate index.

### Exercise 3: JSONB vs Columns Decision

The team wants to add "player preferences" (language, timezone, notification settings). Should this be JSONB or separate columns? Write your reasoning and the schema you'd choose.

---

## What Happens Next

JSONB handles flexible data. But Derek has one more request:

> "Players want to search for other players by username. Partial matches, typo tolerance, relevance ranking. Like a search engine."

You could use `LIKE '%term%'` but that's a Seq Scan on 2.3M rows. Next chapter: full-text search with tsvector and GIN indexes.

---

[← Chapter 7: Window Functions](chapter-07-window-functions.md) | [Chapter 9: Full-Text Search →](chapter-09-full-text-search.md)
