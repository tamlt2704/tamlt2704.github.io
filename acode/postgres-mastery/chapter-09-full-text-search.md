# Chapter 9: Full-Text Search — Finding Players Fast

[← Chapter 8: JSONB](chapter-08-jsonb.md) | [Chapter 10: JOINs & ORM →](chapter-10-joins-orm.md)

---

## The Fire

Derek's latest feature request:

> "Players want to search for friends by username. They type 'pro' and expect to see 'ProGamer42', 'TheProfessor', 'ProgPong'. Also, search player bios. And rank results by relevance. The current LIKE query takes 4 seconds."

The current implementation:

```sql
-- What the app does now (terrible)
SELECT * FROM players
WHERE username ILIKE '%pro%' OR profile->>'bio' ILIKE '%pro%';
```

```
Seq Scan on players  (cost=0.00..142891.00 rows=23000 width=312)
                     (actual time=0.045..3891.223 rows=18421 loops=1)
  Filter: ((username ~~* '%pro%') OR ((profile ->> 'bio') ~~* '%pro%'))
  Rows Removed by Filter: 2281579
```

3.9 seconds. Full table scan. No index can help `%prefix%` patterns with B-tree.

---

## The Solution: Full-Text Search

PostgreSQL has a built-in search engine. No Elasticsearch needed (for most cases).

### Core Concepts

```sql
-- tsvector: a document broken into searchable tokens
SELECT to_tsvector('english', 'The professional ping pong player');
-- 'ping':3 'player':5 'pong':4 'profession':2

-- tsquery: a search query
SELECT to_tsquery('english', 'professional & player');
-- 'profession' & 'player'

-- Match operator: @@
SELECT to_tsvector('english', 'The professional ping pong player')
    @@ to_tsquery('english', 'professional & player');
-- true
```

Notice: "The" is removed (stop word), "professional" becomes "profession" (stemming).

---

## Building the Search

### Step 1: Add a Search Vector Column

```sql
-- Add a tsvector column to players
ALTER TABLE players ADD COLUMN search_vector tsvector;

-- Populate it from username and bio
UPDATE players SET search_vector =
    setweight(to_tsvector('english', coalesce(username, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(profile->>'bio', '')), 'B');
```

Weights (A, B, C, D) control relevance ranking. Username matches rank higher than bio matches.

### Step 2: Create a GIN Index

```sql
CREATE INDEX idx_players_search ON players USING gin (search_vector);
```

### Step 3: Search!

```sql
SELECT
    username,
    profile->>'bio' AS bio,
    ts_rank(search_vector, query) AS rank
FROM players,
     to_tsquery('english', 'pro:*') AS query
WHERE search_vector @@ query
ORDER BY rank DESC
LIMIT 20;
```

```
 username      | bio                          | rank
---------------+------------------------------+--------
 ProGamer42    | Professional esports player  | 0.6079
 TheProfessor  | I teach the art of pong      | 0.3041
 ProgPong      | Programming + ping pong      | 0.2891
```

Execution time: **12ms** (vs 3.9 seconds before).

### Step 4: Keep It Updated (Trigger)

```sql
CREATE OR REPLACE FUNCTION players_search_trigger()
RETURNS trigger AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', coalesce(NEW.username, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(NEW.profile->>'bio', '')), 'B');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_players_search_update
BEFORE INSERT OR UPDATE ON players
FOR EACH ROW EXECUTE FUNCTION players_search_trigger();
```

---

## Search Query Syntax

```sql
-- Single word (with stemming)
to_tsquery('english', 'player')        -- matches "players", "playing"

-- Prefix matching (starts with)
to_tsquery('english', 'pro:*')         -- matches "pro", "professional", "programmer"

-- AND
to_tsquery('english', 'pro & gamer')   -- both must match

-- OR
to_tsquery('english', 'pro | gamer')   -- either matches

-- NOT
to_tsquery('english', 'pro & !bot')    -- "pro" but not "bot"

-- Phrase (adjacent words)
to_tsquery('english', 'ping <-> pong') -- "ping" immediately followed by "pong"

-- Proximity (within N words)
to_tsquery('english', 'ping <2> pong') -- "ping" within 2 words of "pong"
```

### User-Friendly Input

```sql
-- plainto_tsquery: simple text input (no operators needed)
SELECT * FROM players
WHERE search_vector @@ plainto_tsquery('english', 'pro gamer');
-- Treats as: 'pro' & 'gamer'

-- websearch_to_tsquery: Google-like syntax
SELECT * FROM players
WHERE search_vector @@ websearch_to_tsquery('english', '"pro gamer" -bot');
-- Treats as: 'pro' <-> 'gamer' & !'bot'
```

---

## Ranking and Highlighting

### ts_rank

```sql
SELECT
    username,
    ts_rank(search_vector, query) AS rank,
    ts_rank_cd(search_vector, query) AS rank_cd  -- cover density ranking
FROM players,
     websearch_to_tsquery('english', 'professional player') AS query
WHERE search_vector @@ query
ORDER BY rank DESC
LIMIT 10;
```

### ts_headline (Highlighting Matches)

```sql
SELECT
    username,
    ts_headline('english',
        coalesce(profile->>'bio', ''),
        websearch_to_tsquery('english', 'ping pong'),
        'StartSel=<b>, StopSel=</b>, MaxWords=30, MinWords=15'
    ) AS highlighted_bio
FROM players
WHERE search_vector @@ websearch_to_tsquery('english', 'ping pong')
LIMIT 5;
```

```
 username    | highlighted_bio
-------------+------------------------------------------
 PongMaster  | I love <b>ping</b> <b>pong</b> and...
 TableTennis | Professional <b>ping</b> <b>pong</b>...
```

---

## Search Configuration

Different languages have different stemming rules:

```sql
-- Check available configurations
SELECT cfgname FROM pg_ts_config;
-- simple, english, french, german, spanish, ...

-- 'simple' config: no stemming, no stop words (good for usernames)
SELECT to_tsvector('simple', 'ProGamer42');
-- 'progamer42':1

-- Use 'simple' for usernames, 'english' for bios
UPDATE players SET search_vector =
    setweight(to_tsvector('simple', coalesce(username, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(profile->>'bio', '')), 'B');
```

---

## Trigram Search (Fuzzy Matching)

For typo tolerance, use the `pg_trgm` extension:

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create a trigram index
CREATE INDEX idx_players_username_trgm
ON players USING gin (username gin_trgm_ops);

-- Similarity search (handles typos)
SELECT username, similarity(username, 'ProGmer') AS sim
FROM players
WHERE username % 'ProGmer'  -- % means similarity > threshold
ORDER BY sim DESC
LIMIT 10;
```

```
 username    | sim
-------------+------
 ProGamer42  | 0.58
 ProGamer99  | 0.55
```

### Combine FTS + Trigram

```sql
-- Full-text for bio search, trigram for username typo tolerance
SELECT username, profile->>'bio' AS bio
FROM players
WHERE search_vector @@ websearch_to_tsquery('english', 'competitive')
   OR username % 'competitiv'
ORDER BY
    ts_rank(search_vector, websearch_to_tsquery('english', 'competitive')) DESC,
    similarity(username, 'competitiv') DESC
LIMIT 10;
```

---

## Quick Reference

| Function | Purpose |
|----------|---------|
| `to_tsvector(config, text)` | Convert text to searchable vector |
| `to_tsquery(config, query)` | Parse search query |
| `plainto_tsquery(config, text)` | Simple text → query (AND) |
| `websearch_to_tsquery(config, text)` | Google-like syntax |
| `@@` | Match operator (vector @@ query) |
| `ts_rank(vector, query)` | Relevance score |
| `ts_headline(config, text, query)` | Highlight matches |
| `setweight(vector, 'A')` | Assign weight for ranking |

| Index Type | Use Case |
|-----------|----------|
| `GIN (tsvector_col)` | Full-text search |
| `GIN (col gin_trgm_ops)` | Fuzzy/similarity search |
| `GiST (tsvector_col)` | Smaller index, slower queries |

---

## Exercises

### Exercise 1: Multi-Table Search

Create a search that spans both `players.username` and `game_events.event_type`. Return results ranked by relevance with the source table indicated.

### Exercise 2: Autocomplete

Build an autocomplete query that:
1. Takes a partial username (e.g., "pro")
2. Returns the top 10 matches
3. Completes in under 5ms
4. Uses prefix matching (`pro:*`)

### Exercise 3: Fuzzy Username Search

Using `pg_trgm`, build a "did you mean?" feature. When a player searches for a username that doesn't exist exactly, suggest the 3 closest matches by similarity score.

---

## What Happens Next

Search is fast. Profiles are flexible. But Friday morning, Derek's code review reveals something ugly:

> "The match history endpoint makes 47 database queries per page load. One for the player, one for each match, one for each opponent's name..."

The N+1 problem. Time to fix the ORM.

---

[← Chapter 8: JSONB](chapter-08-jsonb.md) | [Chapter 10: JOINs & ORM →](chapter-10-joins-orm.md)
