# Chapter 3: Volumes & Data Persistence

[← Images](./chapter-02-images.md) | [Next: Networking →](./chapter-04-networking.md)

---

## The Problem

Containers are ephemeral. When a container is removed, all data inside it is lost. Volumes solve this by persisting data outside the container's writable layer.

## Three Types of Storage

| Type       | Managed by Docker | Host path                  | Use case                       |
| ---------- | ----------------- | -------------------------- | ------------------------------ |
| Volume     | Yes               | `/var/lib/docker/volumes/` | Production data                |
| Bind mount | No                | Any host path              | Development (live code reload) |
| tmpfs      | N/A               | Memory only                | Sensitive data, temp files     |

## Named Volumes

```bash
# Create a volume
docker volume create my-data

# List volumes
docker volume ls

# Inspect a volume
docker volume inspect my-data

# Remove a volume
docker volume rm my-data

# Remove all unused volumes
docker volume prune
```

### Using volumes with containers

```bash
# Mount a named volume
docker run -d --name postgres \
  -v pgdata:/var/lib/postgresql/data \
  -e POSTGRES_PASSWORD=secret \
  postgres:16

# Data persists even after removing the container
docker rm -f postgres

# Start a new container with the same volume — data is still there
docker run -d --name postgres2 \
  -v pgdata:/var/lib/postgresql/data \
  -e POSTGRES_PASSWORD=secret \
  postgres:16
```

## Bind Mounts

Bind mounts map a host directory directly into the container. Ideal for development.

```bash
# Mount current directory into the container
docker run -d --name dev-app \
  -v ./src:/app/src \
  -p 3000:3000 \
  my-app:dev

# Read-only bind mount
docker run -d \
  -v ./config/nginx.conf:/etc/nginx/nginx.conf:ro \
  nginx
```

### Development workflow with bind mounts

```bash
docker run --rm -it \
  -v ./:/app \
  -w /app \
  -p 3000:3000 \
  node:20-alpine \
  sh -c "npm install && npm run dev"
```

## tmpfs Mounts

Data stored in memory only — never written to disk. Gone when the container stops.

```bash
docker run -d \
  --tmpfs /app/temp \
  --name secure-app \
  my-app
```

Use cases:

- Storing secrets that shouldn't persist on disk
- Temporary processing files
- Performance-sensitive scratch space

## Volume Drivers

Volume drivers allow storing data on remote hosts or cloud providers.

```bash
docker volume create --driver local \
  --opt type=nfs \
  --opt o=addr=192.168.1.100,rw \
  --opt device=:/path/to/dir \
  nfs-volume
```

## Backup Strategies

### Backup a volume to a tar file

```bash
docker run --rm \
  -v pgdata:/source:ro \
  -v ./backups:/backup \
  alpine \
  tar czf /backup/pgdata-backup.tar.gz -C /source .
```

### Restore from backup

```bash
docker run --rm \
  -v pgdata:/target \
  -v ./backups:/backup \
  alpine \
  sh -c "cd /target && tar xzf /backup/pgdata-backup.tar.gz"
```

### Copy files from a container

```bash
# Copy from container to host
docker cp my-container:/app/data ./local-backup

# Copy from host to container
docker cp ./config.json my-container:/app/config.json
```

## Sharing Volumes Between Containers

```bash
# Container 1 writes data
docker run -d --name writer \
  -v shared-data:/data \
  alpine sh -c "while true; do date >> /data/log.txt; sleep 5; done"

# Container 2 reads the same data
docker run --rm \
  -v shared-data:/data:ro \
  alpine cat /data/log.txt
```

## Exercises

1. Create a PostgreSQL container with a named volume, insert data, remove the container, recreate it, and verify data persists
2. Set up a bind mount for a Node.js project and verify code changes on the host are reflected in the container
3. Back up a named volume to a tar file and restore it to a new volume
4. Create two containers sharing a volume — one writes, one reads
5. Run a container with a tmpfs mount and verify data disappears after the container stops

---

[← Images](./chapter-02-images.md) | [Next: Networking →](./chapter-04-networking.md)
