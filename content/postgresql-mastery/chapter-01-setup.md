[prev: Overview](chapter-00-overview.md) | [next: SQL Basics](chapter-02-sql-basics.md)

# Chapter 1: Setup & Installation

## Install PostgreSQL with Docker

The fastest way to get a PostgreSQL instance running:

```bash
docker run --name pg \
  -e POSTGRES_PASSWORD=secret \
  -p 5432:5432 \
  -d postgres:16
```

Verify it's running:

```bash
docker ps | grep pg
```

## Connect with psql

```bash
docker exec -it pg psql -U postgres
```

You should see:

```
psql (16.x)
Type "help" for help.

postgres=#
```

Useful psql commands:

| Command        | Description         |
| -------------- | ------------------- |
| `\l`           | List databases      |
| `\dt`          | List tables         |
| `\d tablename` | Describe table      |
| `\c dbname`    | Connect to database |
| `\q`           | Quit                |
| `\timing`      | Toggle query timing |

## pgAdmin

Run pgAdmin alongside PostgreSQL:

```bash
docker run --name pgadmin \
  -e PGADMIN_DEFAULT_EMAIL=admin@local.dev \
  -e PGADMIN_DEFAULT_PASSWORD=admin \
  -p 8080:80 \
  --link pg:pg \
  -d dpage/pgadmin4
```

Open `http://localhost:8080` and add a server connection:

- Host: `pg`
- Port: `5432`
- Username: `postgres`
- Password: `secret`

## Create Database and User

```sql
-- Create a new user
CREATE USER appuser WITH PASSWORD 'apppass123';

-- Create a database owned by that user
CREATE DATABASE myapp OWNER appuser;

-- Grant connect privilege
GRANT CONNECT ON DATABASE myapp TO appuser;
```

Verify:

```sql
\l
```

Output:

```
    Name    |  Owner   | Encoding
------------+----------+----------
 myapp      | appuser  | UTF8
 postgres   | postgres | UTF8
```

## Connection Strings

Format: `postgresql://user:password@host:port/database`

Examples:

```
postgresql://appuser:apppass123@localhost:5432/myapp
postgresql://postgres:secret@localhost:5432/postgres?sslmode=disable
```

In application code (e.g., Node.js):

```
DATABASE_URL=postgresql://appuser:apppass123@localhost:5432/myapp
```

## Basic Configuration (postgresql.conf)

Find the config file:

```sql
SHOW config_file;
```

Key settings for development:

```
# Connection
listen_addresses = '*'
port = 5432
max_connections = 100

# Memory
shared_buffers = 256MB
work_mem = 4MB
maintenance_work_mem = 64MB

# Logging
log_statement = 'all'
log_duration = on
log_min_duration_statement = 0
```

To edit inside Docker:

```bash
docker exec -it pg bash
cat /var/lib/postgresql/data/postgresql.conf
```

After changes, reload:

```sql
SELECT pg_reload_conf();
```

## pg_hba.conf (Client Authentication)

Controls who can connect and how:

```
# TYPE  DATABASE  USER      ADDRESS         METHOD
local   all       all                       trust
host    all       all       0.0.0.0/0       scram-sha-256
host    all       all       ::0/0           scram-sha-256
```

## Exercises

1. Start a PostgreSQL 16 container with Docker
2. Connect using `psql` and run `SELECT version();`
3. Create a database called `practice` and a user called `student`
4. Connect as `student` to the `practice` database
5. Change `log_statement` to `'all'` and reload the config
6. Verify logging works by running a query and checking Docker logs: `docker logs pg`
