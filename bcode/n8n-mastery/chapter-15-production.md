# Chapter 15: Production Deployment — Self-Hosting n8n

[← Chapter 14: Monitoring & Observability](chapter-14-monitoring.md)

---

## The Problem

LaunchPad's automation runs on your laptop. Docker Desktop, single container, SQLite database. It works — until:

- Your laptop goes to sleep → scheduled workflows don't fire
- Docker crashes → all waiting executions (approvals, webhooks) are lost
- The SQLite file corrupts → all workflow definitions gone
- You go on vacation → nobody can restart it if it dies

Diana: "This automation is now business-critical. Payments depend on it. Reports depend on it. It cannot run on someone's laptop. Deploy it properly."

Time to move n8n to production infrastructure: Postgres for persistence, Redis for queuing, multiple workers for reliability, and proper backups.

## Architecture: Production n8n

```
                    ┌─────────────────────────────────────┐
                    │           Load Balancer (nginx)       │
                    │         (SSL termination)             │
                    └──────────────┬───────────────────────┘
                                   │
                    ┌──────────────┼───────────────────────┐
                    │              │                        │
              ┌─────▼─────┐  ┌────▼──────┐  ┌────────────┐
              │  n8n main  │  │ n8n worker│  │ n8n worker │
              │  (webhook  │  │    #1     │  │    #2      │
              │  + editor) │  │           │  │            │
              └─────┬──────┘  └─────┬─────┘  └─────┬──────┘
                    │               │               │
              ┌─────▼───────────────▼───────────────▼──────┐
              │              Redis (queue)                   │
              └─────────────────────┬───────────────────────┘
                                    │
              ┌─────────────────────▼───────────────────────┐
              │           PostgreSQL (persistence)           │
              └─────────────────────────────────────────────┘
```

- **Main process**: Handles the UI, webhooks, and triggers. Enqueues work.
- **Workers**: Execute workflows from the queue. Scale horizontally.
- **Redis**: Message queue between main and workers.
- **Postgres**: Stores workflows, credentials, execution data.

## Docker Compose: The Full Stack

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:16
    restart: always
    environment:
      POSTGRES_USER: n8n
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: n8n
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ['CMD-SHELL', 'pg_isready -U n8n']
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    restart: always
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    healthcheck:
      test: ['CMD', 'redis-cli', '-a', '${REDIS_PASSWORD}', 'ping']
      interval: 10s
      timeout: 5s
      retries: 5

  n8n:
    image: n8nio/n8n:latest
    restart: always
    ports:
      - '5678:5678'
    environment:
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=n8n
      - DB_POSTGRESDB_PASSWORD=${POSTGRES_PASSWORD}
      - EXECUTIONS_MODE=queue
      - QUEUE_BULL_REDIS_HOST=redis
      - QUEUE_BULL_REDIS_PORT=6379
      - QUEUE_BULL_REDIS_PASSWORD=${REDIS_PASSWORD}
      - N8N_ENCRYPTION_KEY=${ENCRYPTION_KEY}
      - WEBHOOK_URL=https://n8n.launchpad.io/
      - N8N_HOST=n8n.launchpad.io
      - N8N_PROTOCOL=https
      - GENERIC_TIMEZONE=America/New_York
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - n8n_data:/home/node/.n8n

  n8n-worker:
    image: n8nio/n8n:latest
    restart: always
    command: worker
    environment:
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=n8n
      - DB_POSTGRESDB_PASSWORD=${POSTGRES_PASSWORD}
      - EXECUTIONS_MODE=queue
      - QUEUE_BULL_REDIS_HOST=redis
      - QUEUE_BULL_REDIS_PORT=6379
      - QUEUE_BULL_REDIS_PASSWORD=${REDIS_PASSWORD}
      - N8N_ENCRYPTION_KEY=${ENCRYPTION_KEY}
      - GENERIC_TIMEZONE=America/New_York
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - '80:80'
      - '443:443'
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - ./certs:/etc/nginx/certs
    depends_on:
      - n8n

volumes:
  postgres_data:
  redis_data:
  n8n_data:
```

### Environment File

```bash
# .env
POSTGRES_PASSWORD=your-secure-password-here
REDIS_PASSWORD=your-redis-password-here
ENCRYPTION_KEY=your-32-char-encryption-key-here
```

The `N8N_ENCRYPTION_KEY` encrypts credentials at rest. **Never lose this key** — without it, all saved credentials are unrecoverable.

## Queue Mode: How It Works

In queue mode:
1. The **main process** receives triggers (webhooks, schedules, events)
2. It creates an execution and puts it on the **Redis queue**
3. A **worker** picks up the execution and runs it
4. Results are stored in **Postgres**

Benefits:
- Main process never blocks on long-running workflows
- Workers can be scaled independently (2, 5, 10 workers)
- If a worker crashes, the execution is re-queued
- Webhooks respond instantly (main process isn't busy executing)

### Scaling Workers

```bash
# Run 3 workers
docker compose up -d --scale n8n-worker=3
```

Scale based on load. Monitor the Redis queue length — if it grows, add workers.

## SSL with nginx

```nginx
# nginx.conf
server {
    listen 80;
    server_name n8n.launchpad.io;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name n8n.launchpad.io;

    ssl_certificate /etc/nginx/certs/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/privkey.pem;

    location / {
        proxy_pass http://n8n:5678;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (for the editor)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Use Let's Encrypt for free SSL certificates:

```bash
certbot certonly --standalone -d n8n.launchpad.io
```

## Backups

### Postgres Backups

```bash
#!/bin/bash
# backup.sh — run daily via cron
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/backups/n8n

docker exec launchpad-postgres pg_dump -U n8n n8n | gzip > $BACKUP_DIR/n8n_$TIMESTAMP.sql.gz

# Keep last 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

# Upload to S3
aws s3 cp $BACKUP_DIR/n8n_$TIMESTAMP.sql.gz s3://launchpad-backups/n8n/
```

### What's in the Backup

| Data | Stored In | Backup Method |
|---|---|---|
| Workflow definitions | Postgres | pg_dump |
| Credentials (encrypted) | Postgres | pg_dump + encryption key |
| Execution history | Postgres | pg_dump |
| n8n settings | Postgres | pg_dump |
| Encryption key | .env file | Separate secure backup |

### Restore

```bash
gunzip < n8n_20240115_090000.sql.gz | docker exec -i launchpad-postgres psql -U n8n n8n
```

## Production Checklist

### Security

- [ ] SSL/TLS enabled (no plain HTTP)
- [ ] n8n behind authentication (built-in or reverse proxy)
- [ ] Encryption key backed up securely (not in the same place as DB backups)
- [ ] Postgres not exposed to the internet (internal network only)
- [ ] Redis not exposed to the internet
- [ ] Webhook URLs use HTTPS
- [ ] Environment variables for all secrets (not hardcoded)

### Reliability

- [ ] Queue mode enabled (main + workers)
- [ ] At least 2 workers running
- [ ] Health checks on all services
- [ ] Automatic restart on failure (`restart: always`)
- [ ] Execution data persisted to Postgres (not SQLite)
- [ ] Waiting executions survive restarts

### Operations

- [ ] Daily Postgres backups to off-site storage
- [ ] Monitoring workflow running (Chapter 14)
- [ ] Log aggregation (Docker logs → CloudWatch/Datadog/etc.)
- [ ] Alerting on container crashes
- [ ] Execution data retention policy configured
- [ ] Resource limits set on containers

### Performance

- [ ] Postgres connection pooling (PgBouncer) for high-throughput
- [ ] Redis persistence configured (AOF or RDB)
- [ ] Worker count matched to workload
- [ ] Execution pruning for old data (prevent DB bloat)

## Deployment Commands

```bash
# Initial deployment
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f n8n
docker compose logs -f n8n-worker

# Scale workers
docker compose up -d --scale n8n-worker=3

# Update n8n version
docker compose pull
docker compose up -d

# Backup before update
docker exec launchpad-postgres pg_dump -U n8n n8n > backup_before_update.sql
```

## Monitoring the Infrastructure

Add a health check workflow that verifies the infrastructure itself:

```javascript
// Code node — infrastructure health
const checks = [];

// Check Postgres
try {
  const dbResult = $('Ping Postgres').first().json;
  checks.push({ service: 'Postgres', status: '🟢', latency: dbResult.latency });
} catch (e) {
  checks.push({ service: 'Postgres', status: '🔴', error: e.message });
}

// Check Redis (via queue stats)
try {
  const queueLength = $('Check Queue').first().json.waiting;
  checks.push({ service: 'Redis/Queue', status: queueLength < 100 ? '🟢' : '🟡', queue: queueLength });
} catch (e) {
  checks.push({ service: 'Redis/Queue', status: '🔴', error: e.message });
}

const allHealthy = checks.every(c => c.status === '🟢');

return [{ json: { 
  overall: allHealthy ? '🟢 All systems operational' : '🔴 Issues detected',
  checks 
} }];
```

## What You Learned

- **Queue mode** separates trigger handling (main) from execution (workers)
- **Docker Compose** orchestrates Postgres + Redis + n8n main + workers + nginx
- **Encryption key** protects credentials at rest — back it up separately
- **SSL termination** at nginx with WebSocket support for the editor
- **Scaling** — add workers to handle more concurrent executions
- **Backups** — daily pg_dump to S3, with the encryption key stored separately
- **Production checklist** — security, reliability, operations, performance

LaunchPad's automation now runs on proper infrastructure. Workers process executions in parallel. Postgres persists everything across restarts. SSL protects the editor and webhooks. Daily backups mean you can recover from disasters.

Diana's 30-hours-a-week of manual work is now handled by 15 workflows running on infrastructure that costs less than a single employee's monthly coffee budget. The automation is reliable, monitored, and maintainable.

You did it. The boring stuff is automated. Now go automate something interesting.

---

[← Chapter 14: Monitoring & Observability](chapter-14-monitoring.md)
