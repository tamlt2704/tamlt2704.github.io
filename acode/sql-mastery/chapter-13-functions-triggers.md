# Chapter 13: "Automate the Nightly Cleanup"

[← Chapter 12: Transactions](chapter-12-transactions.md) | [Chapter 14: Partitioning →](chapter-14-partitioning.md)

---

## The Request

Maya: "Every night at 2 AM, three things need to happen: archive orders older than 1 year, recalculate MRR for each customer, and log a summary. Right now, a Python script does it. It breaks every other week."

"Can the database just... do it itself?"

---

## Functions: Reusable SQL Logic

A function takes inputs, does work, and returns a result. Like a stored procedure you can call from any query.

### Your First Function

```sql
CREATE OR REPLACE FUNCTION cents_to_dollars(cents INTEGER)
RETURNS NUMERIC AS $$
    SELECT cents / 100.0;
$$ LANGUAGE sql;
```

Use it:

```sql
SELECT name, cents_to_dollars(price_cents) AS price
FROM products;
```

### PL/pgSQL: Procedural Logic

For anything beyond a single SELECT — variables, loops, conditionals — use PL/pgSQL:

```sql
CREATE OR REPLACE FUNCTION get_customer_tier(customer_id INTEGER)
RETURNS TEXT AS $$
DECLARE
    total_spent NUMERIC;
BEGIN
    SELECT COALESCE(sum(total_cents), 0) / 100.0
    INTO total_spent
    FROM orders
    WHERE orders.customer_id = get_customer_tier.customer_id
      AND status = 'completed';

    RETURN CASE
        WHEN total_spent > 300 THEN 'platinum'
        WHEN total_spent > 100 THEN 'gold'
        WHEN total_spent > 0 THEN 'silver'
        ELSE 'bronze'
    END;
END;
$$ LANGUAGE plpgsql;
```

```sql
SELECT name, get_customer_tier(id) AS tier FROM customers;
```

```
      name       |   tier
-----------------+----------
 Acme Corp       | platinum
 TechStart       | silver
 MegaRetail      | platinum
 Solo Dev        | silver
 ...
```

### Function Anatomy

```sql
CREATE OR REPLACE FUNCTION function_name(param1 TYPE, param2 TYPE)
RETURNS return_type AS $$
DECLARE
    variable_name TYPE;          -- local variables
BEGIN
    -- logic here
    RETURN value;
END;
$$ LANGUAGE plpgsql;
```

| Part | Purpose |
|---|---|
| `CREATE OR REPLACE` | Create or update the function |
| Parameters | Input values |
| `RETURNS` | What type comes back |
| `DECLARE` | Local variables |
| `BEGIN...END` | The function body |
| `$$` | Dollar-quoting (avoids escaping single quotes) |

---

## Returning Sets: Table-Valued Functions

```sql
CREATE OR REPLACE FUNCTION get_top_customers(min_revenue NUMERIC)
RETURNS TABLE(name TEXT, plan TEXT, revenue NUMERIC) AS $$
BEGIN
    RETURN QUERY
    SELECT c.name, c.plan, sum(o.total_cents) / 100.0
    FROM customers c
    JOIN orders o ON o.customer_id = c.id
    WHERE o.status = 'completed'
    GROUP BY c.id, c.name, c.plan
    HAVING sum(o.total_cents) / 100.0 >= min_revenue
    ORDER BY sum(o.total_cents) DESC;
END;
$$ LANGUAGE plpgsql;
```

```sql
SELECT * FROM get_top_customers(200);
```

Use it like a table — filter, join, aggregate the results.

---

## Procedures: Side Effects Without Returns

Functions return values. Procedures perform actions (and can manage transactions).

```sql
CREATE OR REPLACE PROCEDURE archive_old_orders(cutoff_date DATE)
LANGUAGE plpgsql AS $$
DECLARE
    archived_count INTEGER;
BEGIN
    -- Move old orders to archive table
    INSERT INTO orders_archive
    SELECT * FROM orders
    WHERE order_date < cutoff_date
      AND status IN ('completed', 'cancelled', 'refunded');

    GET DIAGNOSTICS archived_count = ROW_COUNT;

    -- Delete from main table
    DELETE FROM orders
    WHERE order_date < cutoff_date
      AND status IN ('completed', 'cancelled', 'refunded');

    -- Log the operation
    INSERT INTO maintenance_log (operation, details, executed_at)
    VALUES ('archive_orders',
            format('Archived %s orders older than %s', archived_count, cutoff_date),
            now());

    RAISE NOTICE 'Archived % orders', archived_count;
END;
$$;
```

Call it:

```sql
CALL archive_old_orders('2023-01-01');
-- NOTICE: Archived 1247 orders
```

### Functions vs Procedures

| Feature | Function | Procedure |
|---|---|---|
| Returns a value | Yes | No |
| Used in SELECT | Yes | No |
| Transaction control | No | Yes (COMMIT/ROLLBACK inside) |
| Called with | `SELECT func()` | `CALL proc()` |

---

## Triggers: Automatic Reactions

A trigger fires automatically when data changes. No one has to remember to call it.

### Use Case: Auto-Update `updated_at`

```sql
-- The trigger function
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach it to a table
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON customers
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();
```

Now every `UPDATE` on `customers` automatically sets `updated_at` to the current time. No application code needed.

### Trigger Timing

| Timing | Fires | Use For |
|---|---|---|
| `BEFORE INSERT` | Before the row is written | Validation, default values |
| `AFTER INSERT` | After the row is written | Audit logs, notifications |
| `BEFORE UPDATE` | Before the update | Auto-set timestamps, validation |
| `AFTER UPDATE` | After the update | Audit trail, cascading logic |
| `BEFORE DELETE` | Before deletion | Soft delete, archiving |
| `AFTER DELETE` | After deletion | Cleanup, logging |

### Use Case: Audit Trail

```sql
CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    operation TEXT NOT NULL,
    row_id INTEGER,
    old_data JSONB,
    new_data JSONB,
    changed_at TIMESTAMPTZ DEFAULT now(),
    changed_by TEXT DEFAULT current_user
);

CREATE OR REPLACE FUNCTION audit_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (table_name, operation, row_id, new_data)
        VALUES (TG_TABLE_NAME, 'INSERT', NEW.id, to_jsonb(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (table_name, operation, row_id, old_data, new_data)
        VALUES (TG_TABLE_NAME, 'UPDATE', NEW.id, to_jsonb(OLD), to_jsonb(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (table_name, operation, row_id, old_data)
        VALUES (TG_TABLE_NAME, 'DELETE', OLD.id, to_jsonb(OLD));
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Apply to customers table
CREATE TRIGGER audit_customers
    AFTER INSERT OR UPDATE OR DELETE ON customers
    FOR EACH ROW EXECUTE FUNCTION audit_changes();
```

Now every change to `customers` is logged automatically:

```sql
UPDATE customers SET plan = 'enterprise' WHERE id = 2;

SELECT operation, old_data->>'plan' AS old_plan, new_data->>'plan' AS new_plan
FROM audit_log
WHERE table_name = 'customers' AND row_id = 2
ORDER BY changed_at DESC LIMIT 1;
```

```
 operation | old_plan | new_plan
-----------+----------+------------
 UPDATE    | pro      | enterprise
```

### Use Case: Prevent Dangerous Deletes

```sql
CREATE OR REPLACE FUNCTION prevent_enterprise_delete()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.plan = 'enterprise' THEN
        RAISE EXCEPTION 'Cannot delete enterprise customers. Use soft delete.';
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER protect_enterprise
    BEFORE DELETE ON customers
    FOR EACH ROW EXECUTE FUNCTION prevent_enterprise_delete();
```

---

## Maya's Nightly Job

Putting it all together:

```sql
CREATE OR REPLACE PROCEDURE nightly_maintenance()
LANGUAGE plpgsql AS $$
DECLARE
    archived INTEGER;
    mrr_updated INTEGER;
BEGIN
    -- Step 1: Archive old orders
    INSERT INTO orders_archive
    SELECT * FROM orders
    WHERE order_date < CURRENT_DATE - interval '1 year'
      AND status IN ('completed', 'cancelled', 'refunded');
    GET DIAGNOSTICS archived = ROW_COUNT;

    DELETE FROM order_items
    WHERE order_id IN (
        SELECT id FROM orders
        WHERE order_date < CURRENT_DATE - interval '1 year'
          AND status IN ('completed', 'cancelled', 'refunded')
    );

    DELETE FROM orders
    WHERE order_date < CURRENT_DATE - interval '1 year'
      AND status IN ('completed', 'cancelled', 'refunded');

    -- Step 2: Refresh materialized views
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_customer_ltv;

    -- Step 3: Log summary
    INSERT INTO maintenance_log (operation, details, executed_at)
    VALUES ('nightly_maintenance',
            format('Archived %s orders. Views refreshed.', archived),
            now());

    RAISE NOTICE 'Nightly maintenance complete. Archived: %', archived;
END;
$$;
```

Schedule it with pg_cron:

```sql
SELECT cron.schedule('nightly-maintenance', '0 2 * * *', 'CALL nightly_maintenance()');
```

Or call from an external scheduler (cron, Airflow, etc.):

```bash
psql -h localhost -U postgres -d datapulse -c "CALL nightly_maintenance();"
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
CREATE FUNCTION ... RETURNS ... │ Reusable logic that returns a value
CREATE PROCEDURE ...            │ Reusable logic with side effects
CALL procedure_name()           │ Execute a procedure
CREATE TRIGGER ... ON table     │ Auto-fire on INSERT/UPDATE/DELETE
BEFORE / AFTER                  │ When the trigger fires
FOR EACH ROW                    │ Fires once per affected row
NEW / OLD                       │ The new/old row data in triggers
TG_OP                           │ 'INSERT', 'UPDATE', or 'DELETE'
RAISE NOTICE / EXCEPTION        │ Print message / abort with error
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

The `orders` table hits 200 million rows. Queries slow down. VACUUM takes hours. Indexes bloat. Silent Sasha sends you a link to the PostgreSQL docs on partitioning.

---

[← Chapter 12: Transactions](chapter-12-transactions.md) | [Chapter 14: Partitioning →](chapter-14-partitioning.md)
