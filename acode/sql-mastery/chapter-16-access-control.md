# Chapter 16: "We Need Role-Based Access"

[← Chapter 15: JSONB & Full-Text Search](chapter-15-jsonb-fulltext.md) | [Chapter 17: Schema Migrations →](chapter-17-migrations.md)

---

## The Request

Priya calls a meeting. "Three problems. The intern ran `DELETE FROM orders` in production last week. Hank can see customer emails he shouldn't. And our audit shows the analytics dashboard connects as the superuser."

"I want roles. The intern gets read-only. Sales sees revenue but not emails. The dashboard gets its own restricted account."

---

## Users and Roles

In PostgreSQL, users and roles are the same thing. A "user" is just a role with login permission.

```sql
-- Create roles (no login — these are permission groups)
CREATE ROLE readonly;
CREATE ROLE analyst;
CREATE ROLE sales_team;
CREATE ROLE app_backend;

-- Create users (with login)
CREATE USER intern WITH PASSWORD 'intern123' IN ROLE readonly;
CREATE USER maya WITH PASSWORD 'maya_secure' IN ROLE analyst;
CREATE USER hank WITH PASSWORD 'hank_sales' IN ROLE sales_team;
CREATE USER dashboard_svc WITH PASSWORD 'svc_token' IN ROLE readonly;
```

### Role Hierarchy

```
                    postgres (superuser)
                         │
            ┌────────────┼────────────┐
            ▼            ▼            ▼
        app_backend   analyst     sales_team
            │            │            │
            ▼            ▼            ▼
        (backend)     maya         hank
                                    
        readonly
            │
        ┌───┴───┐
        ▼       ▼
     intern  dashboard_svc
```

---

## GRANT: Giving Permissions

### Table-Level Permissions

```sql
-- Readonly: can SELECT on all tables
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;

-- Analyst: can SELECT and create views
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analyst;
GRANT CREATE ON SCHEMA public TO analyst;

-- Sales: can see orders and products, but NOT customer emails
GRANT SELECT ON orders, order_items, products TO sales_team;
GRANT SELECT (id, name, plan, country, signed_up) ON customers TO sales_team;
-- Note: column-level grant — email is excluded

-- App backend: full CRUD
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_backend;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_backend;
```

### Future Tables

Grants only apply to existing tables. For tables created later:

```sql
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT ON TABLES TO readonly;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_backend;
```

---

## REVOKE: Taking Permissions Away

```sql
-- Remove DELETE from intern (belt and suspenders)
REVOKE DELETE ON ALL TABLES IN SCHEMA public FROM readonly;

-- Remove all permissions from a role
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM sales_team;
-- Then re-grant only what they need
```

---

## Testing Permissions

```sql
-- Switch to a role to test (superuser only)
SET ROLE intern;

SELECT * FROM customers;  -- works (readonly has SELECT)
DELETE FROM orders WHERE id = 1;
-- ERROR: permission denied for table orders

RESET ROLE;  -- back to superuser
```

---

## Row-Level Security (RLS)

Column-level grants hide columns. RLS hides rows.

"Each sales rep should only see their own customers."

```sql
-- Add an owner column
ALTER TABLE customers ADD COLUMN account_owner TEXT;
UPDATE customers SET account_owner = 'hank' WHERE country = 'US';
UPDATE customers SET account_owner = 'maya' WHERE country != 'US';

-- Enable RLS on the table
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;

-- Policy: users can only see rows they own
CREATE POLICY customer_isolation ON customers
    FOR SELECT
    USING (account_owner = current_user);

-- Superusers bypass RLS by default. Force it:
ALTER TABLE customers FORCE ROW LEVEL SECURITY;
```

Now:

```sql
SET ROLE hank;
SELECT name, country FROM customers;
-- Only sees US customers (where account_owner = 'hank')

SET ROLE maya;
SELECT name, country FROM customers;
-- Only sees non-US customers

RESET ROLE;
```

### Multiple Policies

```sql
-- Analysts can see everything (override)
CREATE POLICY analyst_full_access ON customers
    FOR SELECT
    TO analyst
    USING (true);  -- no restriction

-- App backend can modify only their own rows
CREATE POLICY app_write_own ON customers
    FOR UPDATE
    TO app_backend
    USING (account_owner = current_user)
    WITH CHECK (account_owner = current_user);
```

### RLS for Multi-Tenant Applications

```sql
-- Each tenant only sees their own data
CREATE POLICY tenant_isolation ON orders
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant')::integer);

-- Application sets the tenant before queries:
SET app.current_tenant = '42';
SELECT * FROM orders;  -- only sees tenant 42's orders
```

---

## Schema Separation

For stronger isolation, use separate schemas:

```sql
-- Create schemas
CREATE SCHEMA analytics;
CREATE SCHEMA sales;

-- Move views to appropriate schemas
CREATE VIEW analytics.monthly_revenue AS ...;
CREATE VIEW sales.customer_pipeline AS ...;

-- Grant schema access
GRANT USAGE ON SCHEMA analytics TO analyst;
GRANT USAGE ON SCHEMA sales TO sales_team;

-- Deny cross-schema access
REVOKE ALL ON SCHEMA analytics FROM sales_team;
```

---

## Practical: The Dashboard Service Account

```sql
-- Create a minimal service account
CREATE USER dashboard_svc WITH PASSWORD 'rotate_me_monthly';

-- Only allow reading specific views
GRANT USAGE ON SCHEMA public TO dashboard_svc;
GRANT SELECT ON monthly_revenue, customer_ltv, open_tickets_summary TO dashboard_svc;

-- No access to raw tables
REVOKE SELECT ON customers, orders, tickets FROM dashboard_svc;

-- Connection limit (prevent abuse)
ALTER USER dashboard_svc CONNECTION LIMIT 5;
```

The dashboard can read pre-built views but can't access raw customer data or run arbitrary queries.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Command                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
CREATE ROLE name                │ Create a permission group
CREATE USER name WITH PASSWORD  │ Create a login role
GRANT SELECT ON table TO role   │ Give read access
GRANT SELECT (col) ON table     │ Column-level access
REVOKE perm ON table FROM role  │ Remove access
ALTER DEFAULT PRIVILEGES ...    │ Auto-grant on future objects
────────────────────────────────┼──────────────────────────────────────
ALTER TABLE ... ENABLE ROW LEVEL SECURITY │ Turn on RLS
CREATE POLICY name ON table     │ Define row visibility rules
USING (condition)               │ Which rows are visible
WITH CHECK (condition)          │ Which rows can be written
SET ROLE username               │ Test as another user
RESET ROLE                      │ Return to original user
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

The schema needs to change. A new column, a renamed table, a dropped constraint. But the app is running 24/7. You can't just `DROP TABLE` and recreate it.

Safe schema migrations. Zero-downtime changes.

---

[← Chapter 15: JSONB & Full-Text Search](chapter-15-jsonb-fulltext.md) | [Chapter 17: Schema Migrations →](chapter-17-migrations.md)
