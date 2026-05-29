[prev: Performance Tuning](chapter-07-performance.md) | [next: Backup & Recovery](chapter-09-backup.md)

# Chapter 8: Security

## Roles

PostgreSQL uses roles for both users and groups:

```sql
-- Create a login role (user)
CREATE ROLE app_user LOGIN PASSWORD 'secure_pass';

-- Create a group role (no login)
CREATE ROLE readonly;

-- Grant group membership
GRANT readonly TO app_user;

-- List roles
\du
```

### Role attributes

```sql
CREATE ROLE admin_user
    LOGIN
    PASSWORD 'admin_pass'
    SUPERUSER
    CREATEDB
    CREATEROLE;

-- Modify existing role
ALTER ROLE app_user SET statement_timeout = '30s';
```

## GRANT and REVOKE

```sql
-- Grant on database
GRANT CONNECT ON DATABASE myapp TO app_user;

-- Grant on schema
GRANT USAGE ON SCHEMA public TO readonly;

-- Grant on tables
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;

-- Grant specific operations
GRANT SELECT, INSERT, UPDATE ON orders TO app_user;
GRANT DELETE ON orders TO admin_user;

-- Revoke
REVOKE DELETE ON orders FROM app_user;

-- Default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT ON TABLES TO readonly;
```

## Row-Level Security (RLS)

Control which rows a user can see or modify:

```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    owner_id INT NOT NULL,
    title TEXT,
    content TEXT,
    is_public BOOLEAN DEFAULT false
);

-- Enable RLS on the table
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Policy: users see only their own docs + public docs
CREATE POLICY doc_select_policy ON documents
    FOR SELECT
    USING (owner_id = current_setting('app.user_id')::int OR is_public = true);

-- Policy: users can only insert their own docs
CREATE POLICY doc_insert_policy ON documents
    FOR INSERT
    WITH CHECK (owner_id = current_setting('app.user_id')::int);

-- Policy: users can only update their own docs
CREATE POLICY doc_update_policy ON documents
    FOR UPDATE
    USING (owner_id = current_setting('app.user_id')::int);
```

Using RLS in application:

```sql
-- Set the user context before queries
SET app.user_id = '42';

-- Now queries are automatically filtered
SELECT * FROM documents;  -- only sees user 42's docs + public
```

Force RLS on table owner too:

```sql
ALTER TABLE documents FORCE ROW LEVEL SECURITY;
```

## pg_hba.conf

Controls client authentication. Located at:

```sql
SHOW hba_file;
```

Format:

```
# TYPE   DATABASE  USER       ADDRESS          METHOD
local    all       postgres                    peer
host     myapp     app_user   10.0.0.0/8       scram-sha-256
host     all       all        192.168.1.0/24   scram-sha-256
hostssl  all       all        0.0.0.0/0        scram-sha-256
host     all       all        0.0.0.0/0        reject
```

Rules are evaluated top-to-bottom, first match wins.

After editing:

```sql
SELECT pg_reload_conf();
```

## SSL Connections

Generate self-signed certificates (for dev):

```bash
openssl req -new -x509 -days 365 -nodes \
  -out server.crt -keyout server.key \
  -subj "/CN=postgres"
chmod 600 server.key
```

In `postgresql.conf`:

```
ssl = on
ssl_cert_file = '/var/lib/postgresql/data/server.crt'
ssl_key_file = '/var/lib/postgresql/data/server.key'
```

Force SSL for remote connections in `pg_hba.conf`:

```
hostssl  all  all  0.0.0.0/0  scram-sha-256
```

Verify SSL from client:

```sql
SELECT ssl_is_used();
```

## Password Encryption (scram-sha-256)

Set in `postgresql.conf`:

```
password_encryption = scram-sha-256
```

Verify:

```sql
SHOW password_encryption;

-- Check stored password hash type
SELECT rolname, rolpassword FROM pg_authid WHERE rolname = 'app_user';
-- Should start with SCRAM-SHA-256$
```

## Audit Logging

### Basic logging in postgresql.conf

```
log_connections = on
log_disconnections = on
log_statement = 'ddl'          -- log CREATE, ALTER, DROP
log_line_prefix = '%t [%p] %u@%d '
```

### pgAudit extension (detailed audit)

```sql
CREATE EXTENSION pgaudit;
```

In `postgresql.conf`:

```
shared_preload_libraries = 'pgaudit'
pgaudit.log = 'write, ddl'
pgaudit.log_relation = on
```

This logs all INSERT, UPDATE, DELETE, and DDL statements with full detail.

### Custom audit with triggers

```sql
CREATE TABLE audit_trail (
    id SERIAL PRIMARY KEY,
    table_name TEXT,
    operation TEXT,
    user_name TEXT DEFAULT current_user,
    timestamp TIMESTAMP DEFAULT now(),
    old_row JSONB,
    new_row JSONB
);

CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_trail (table_name, operation, old_row, new_row)
    VALUES (
        TG_TABLE_NAME,
        TG_OP,
        CASE WHEN TG_OP IN ('UPDATE','DELETE') THEN to_jsonb(OLD) END,
        CASE WHEN TG_OP IN ('UPDATE','INSERT') THEN to_jsonb(NEW) END
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER orders_audit
AFTER INSERT OR UPDATE OR DELETE ON orders
FOR EACH ROW EXECUTE FUNCTION audit_trigger();
```

## Exercises

1. Create a `readonly` role that can only SELECT from all tables in a schema

2. Implement RLS on a `tasks` table so users only see their own tasks

3. Configure `pg_hba.conf` to reject all connections except from a specific subnet

4. Enable SSL and verify with `SELECT ssl_is_used()`

5. Set up a trigger-based audit trail and verify it captures changes

6. Create a role with `statement_timeout` of 5 seconds and test with `pg_sleep(10)`
