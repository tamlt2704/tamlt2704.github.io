# Chapter 18: Audit Trails — Who Changed That Row?

[← Chapter 17: Storage](chapter-17-storage.md) | [Chapter 19: Monitoring →](chapter-19-monitoring.md)

---

## The Fire

Tournament day, 3 PM. A top-ranked player files a complaint:

> "My ELO dropped from 2,450 to 1,200 after my last match. That's impossible — I WON. Someone messed with my data."

CEO Chad:

> "Can you tell me who changed it, when, and what the old value was?"

You check the `players` table. The current ELO is 1,200. But there's no history. No log. No trail. You have no idea what happened.

Marta:

> "We need an audit trail. Every change to critical tables should be logged — who, when, old value, new value. We'll use triggers."

---

## Trigger-Based Audit

### Step 1: Create the Audit Table

```sql
CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    row_id BIGINT NOT NULL,
    action TEXT NOT NULL,  -- INSERT, UPDATE, DELETE
    old_data JSONB,
    new_data JSONB,
    changed_fields TEXT[],
    changed_by TEXT DEFAULT current_user,
    changed_at TIMESTAMP DEFAULT now(),
    app_user TEXT,  -- Application-level user (set via session variable)
    transaction_id BIGINT DEFAULT txid_current()
);

CREATE INDEX idx_audit_table_row ON audit_log (table_name, row_id);
CREATE INDEX idx_audit_changed_at ON audit_log (changed_at);
```

### Step 2: Create the Audit Trigger Function

```sql
CREATE OR REPLACE FUNCTION audit_trigger_func()
RETURNS trigger AS $$
DECLARE
    old_json JSONB;
    new_json JSONB;
    changed TEXT[];
    col TEXT;
    app_user_val TEXT;
BEGIN
    -- Get application user from session variable (set by app)
    app_user_val := current_setting('app.current_user', true);

    IF TG_OP = 'DELETE' THEN
        old_json := to_jsonb(OLD);
        INSERT INTO audit_log (table_name, row_id, action, old_data, app_user)
        VALUES (TG_TABLE_NAME, OLD.id, 'DELETE', old_json, app_user_val);
        RETURN OLD;

    ELSIF TG_OP = 'INSERT' THEN
        new_json := to_jsonb(NEW);
        INSERT INTO audit_log (table_name, row_id, action, new_data, app_user)
        VALUES (TG_TABLE_NAME, NEW.id, 'INSERT', new_json, app_user_val);
        RETURN NEW;

    ELSIF TG_OP = 'UPDATE' THEN
        old_json := to_jsonb(OLD);
        new_json := to_jsonb(NEW);

        -- Find which fields changed
        FOR col IN SELECT key FROM jsonb_each(new_json)
        LOOP
            IF old_json->col IS DISTINCT FROM new_json->col THEN
                changed := array_append(changed, col);
            END IF;
        END LOOP;

        -- Only log if something actually changed
        IF changed IS NOT NULL THEN
            INSERT INTO audit_log (table_name, row_id, action, old_data, new_data, changed_fields, app_user)
            VALUES (TG_TABLE_NAME, NEW.id, 'UPDATE', old_json, new_json, changed, app_user_val);
        END IF;
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;
```

### Step 3: Attach to Critical Tables

```sql
CREATE TRIGGER audit_players
AFTER INSERT OR UPDATE OR DELETE ON players
FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();

CREATE TRIGGER audit_matches
AFTER INSERT OR UPDATE OR DELETE ON matches
FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();
```

### Step 4: Set Application User

```python
# In your application code, set the user before each request
def set_app_user(conn, username):
    with conn.cursor() as cur:
        cur.execute("SET LOCAL app.current_user = %s", (username,))
```

---

## Using hstore for Compact Change Tracking

For a more compact audit (only changed fields):

```sql
CREATE EXTENSION IF NOT EXISTS hstore;

CREATE OR REPLACE FUNCTION audit_changes_only()
RETURNS trigger AS $$
DECLARE
    changes hstore;
BEGIN
    IF TG_OP = 'UPDATE' THEN
        -- hstore difference: only changed key-value pairs
        changes := hstore(NEW) - hstore(OLD);

        IF changes != ''::hstore THEN
            INSERT INTO audit_log (table_name, row_id, action, old_data, new_data, changed_fields)
            VALUES (
                TG_TABLE_NAME,
                NEW.id,
                'UPDATE',
                hstore_to_jsonb(hstore(OLD) - (hstore(OLD) - changes)),  -- Only old values of changed fields
                hstore_to_jsonb(changes),  -- Only new values of changed fields
                akeys(changes)
            );
        END IF;
        RETURN NEW;
    END IF;
    -- ... handle INSERT/DELETE
END;
$$ LANGUAGE plpgsql;
```

---

## Querying the Audit Trail

### Find Who Changed the Player's ELO

```sql
SELECT
    changed_at,
    action,
    old_data->>'elo_rating' AS old_elo,
    new_data->>'elo_rating' AS new_elo,
    app_user,
    changed_by,
    transaction_id
FROM audit_log
WHERE table_name = 'players'
  AND row_id = 42
  AND 'elo_rating' = ANY(changed_fields)
ORDER BY changed_at DESC
LIMIT 10;
```

```
      changed_at       | action | old_elo | new_elo | app_user    | transaction_id
-----------------------+--------+---------+---------+-------------+----------------
 2024-03-16 15:02:33   | UPDATE | 2450    | 1200    | admin_bot   | 891234567
 2024-03-16 14:58:12   | UPDATE | 2425    | 2450    | match_svc   | 891234501
 2024-03-16 14:45:01   | UPDATE | 2400    | 2425    | match_svc   | 891234489
```

Found it. `admin_bot` changed the ELO from 2,450 to 1,200 at 15:02. That's a bug in the admin service.

### Full Row History

```sql
-- Reconstruct the complete history of a row
SELECT
    changed_at,
    action,
    CASE action
        WHEN 'INSERT' THEN new_data
        WHEN 'UPDATE' THEN new_data
        WHEN 'DELETE' THEN old_data
    END AS row_state
FROM audit_log
WHERE table_name = 'players' AND row_id = 42
ORDER BY changed_at;
```

---

## Logical Decoding (WAL-Based Audit)

Instead of triggers, you can read changes directly from the WAL:

```sql
-- Create a logical replication slot
SELECT pg_create_logical_replication_slot('audit_slot', 'wal2json');

-- Read changes
SELECT * FROM pg_logical_slot_get_changes('audit_slot', NULL, NULL);
```

Output (wal2json format):

```json
{
  "change": [
    {
      "kind": "update",
      "schema": "public",
      "table": "players",
      "columnnames": ["id", "username", "elo_rating"],
      "columnvalues": [42, "ProGamer42", 1200],
      "oldkeys": {"keynames": ["id"], "keyvalues": [42]}
    }
  ]
}
```

### Pros and Cons

| Approach | Pros | Cons |
|----------|------|------|
| Triggers | Simple, immediate, queryable | Adds write latency, same DB |
| Logical Decoding | No write overhead, captures all changes | Complex setup, external consumer needed |
| CDC (Debezium) | Real-time streaming, external storage | Infrastructure complexity |

---

## CDC with Debezium

For production-scale audit trails, stream changes to an external system:

```
PostgreSQL → Debezium → Kafka → Audit Service → Elasticsearch
```

### Debezium Configuration

```json
{
  "name": "pingpong-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "pg-primary",
    "database.port": "5432",
    "database.user": "debezium",
    "database.password": "secret",
    "database.dbname": "pingpong",
    "table.include.list": "public.players,public.matches",
    "plugin.name": "pgoutput",
    "slot.name": "debezium_slot",
    "publication.name": "debezium_pub"
  }
}
```

```sql
-- On PostgreSQL: create publication for Debezium
CREATE PUBLICATION debezium_pub FOR TABLE players, matches;
```

Debezium captures every INSERT, UPDATE, DELETE with before/after values and streams them to Kafka topics.

---

## Audit Table Maintenance

The audit table grows fast. Partition it by time:

```sql
-- Partitioned audit log
CREATE TABLE audit_log_partitioned (
    id BIGSERIAL,
    table_name TEXT NOT NULL,
    row_id BIGINT NOT NULL,
    action TEXT NOT NULL,
    old_data JSONB,
    new_data JSONB,
    changed_fields TEXT[],
    changed_by TEXT,
    changed_at TIMESTAMP DEFAULT now(),
    app_user TEXT,
    transaction_id BIGINT,
    PRIMARY KEY (id, changed_at)
) PARTITION BY RANGE (changed_at);

-- Monthly partitions
CREATE TABLE audit_log_2024_03 PARTITION OF audit_log_partitioned
    FOR VALUES FROM ('2024-03-01') TO ('2024-04-01');

-- Archive old audit data after 90 days
-- (same pattern as Chapter 17)
```

---

## Quick Reference

| Component | Purpose |
|-----------|---------|
| `audit_log` table | Stores all changes |
| `audit_trigger_func()` | Captures INSERT/UPDATE/DELETE |
| `app.current_user` session var | Tracks application-level user |
| `hstore(NEW) - hstore(OLD)` | Compact change detection |
| `pg_logical_slot_get_changes()` | WAL-based change capture |
| Debezium | External CDC streaming |

| Query Pattern | Use Case |
|--------------|----------|
| Filter by `table_name` + `row_id` | History of one row |
| Filter by `changed_fields` | Track specific column changes |
| Filter by `app_user` | Who made changes |
| Filter by `transaction_id` | All changes in one transaction |
| Filter by `changed_at` range | Changes in a time window |

---

## Exercises

### Exercise 1: Implement Audit

1. Create the audit table and trigger function
2. Attach it to the `players` table
3. Update a player's ELO rating
4. Query the audit log to see the change

### Exercise 2: Rollback from Audit

Write a function that "undoes" the last change to a row using the audit log:

```sql
-- Restore player 42 to their previous state
SELECT undo_last_change('players', 42);
```

### Exercise 3: Audit Report

Write a query that shows:
- The top 10 most-modified rows across all tables in the last 24 hours
- Which application user made the most changes
- Which fields are changed most frequently

---

## What Happens Next

The audit trail catches the bug. The admin bot had a miscalculation. The player's ELO is restored. But now you need to know: what else is going wrong that you can't see?

Ops Olga:

> "We need dashboards. I want to see lock waits, cache hit ratios, replication lag, and autovacuum progress. In real time. Before things break."

Next chapter: monitoring everything.

---

[← Chapter 17: Storage](chapter-17-storage.md) | [Chapter 19: Monitoring →](chapter-19-monitoring.md)
