# Chapter 4: Container Networking

[← Volumes](./chapter-03-volumes.md) | [Next: Docker Compose →](./chapter-05-compose.md)

---

## Network Drivers

| Driver  | Description                           | Use case                            |
| ------- | ------------------------------------- | ----------------------------------- |
| bridge  | Default. Isolated network on the host | Single-host container communication |
| host    | Container shares host's network stack | Performance-critical apps           |
| none    | No networking                         | Maximum isolation                   |
| overlay | Multi-host networking                 | Docker Swarm                        |

## The Default Bridge Network

When you run a container without specifying a network, it joins the default `bridge` network.

```bash
# See default networks
docker network ls

# Inspect the bridge network
docker network inspect bridge
```

Containers on the default bridge can communicate via IP but **not** by container name.

## Custom Bridge Networks

Custom networks provide automatic DNS resolution between containers.

```bash
# Create a custom network
docker network create my-network

# Run containers on the custom network
docker run -d --name api --network my-network nginx
docker run -d --name db --network my-network -e POSTGRES_PASSWORD=secret postgres:16

# Containers can reach each other by name
docker exec api ping db
```

### Why custom networks are better

- Automatic DNS: containers resolve each other by name
- Better isolation: only containers on the same network can communicate
- Can be connected/disconnected at runtime

## Port Mapping

```bash
# Map host port 8080 to container port 80
docker run -d -p 8080:80 nginx

# Map to a specific host interface
docker run -d -p 127.0.0.1:8080:80 nginx

# Map a random host port
docker run -d -p 80 nginx

# Map multiple ports
docker run -d -p 8080:80 -p 8443:443 nginx

# Check mapped ports
docker port my-container
```

## Container-to-Container Communication

### On a custom network (recommended)

```bash
docker network create app-net

docker run -d --name redis --network app-net redis:7

docker run --rm --network app-net redis:7 \
  redis-cli -h redis ping
# Output: PONG
```

### Connecting a running container to a network

```bash
docker network connect app-net existing-container
docker network disconnect app-net existing-container
```

## Host Network Mode

The container shares the host's network directly. No port mapping needed.

```bash
docker run -d --network host nginx
# nginx is now accessible on host's port 80 directly
```

Note: Host mode is not supported on Docker Desktop for Windows/macOS (only Linux).

## None Network Mode

Completely disables networking.

```bash
docker run --rm --network none alpine ping google.com
# This will fail — no network access
```

## DNS and Service Discovery

On custom networks, Docker runs an embedded DNS server at `127.0.0.11`.

```bash
docker network create backend

docker run -d --name db --network backend -e POSTGRES_PASSWORD=secret postgres:16
docker run -d --name cache --network backend redis:7

# From any container on 'backend':
# "db" resolves to the postgres container's IP
# "cache" resolves to the redis container's IP
```

### Network aliases

```bash
docker run -d --name postgres-primary \
  --network backend \
  --network-alias db \
  -e POSTGRES_PASSWORD=secret \
  postgres:16

# Other containers can reach it via "db" or "postgres-primary"
```

## Cleanup

```bash
# Remove a network
docker network rm my-network

# Remove all unused networks
docker network prune
```

## Exercises

1. Create a custom network, run nginx and a curl container on it, and fetch the nginx homepage by container name
2. Run Redis on a custom network and connect from another container using `redis-cli -h redis`
3. Demonstrate that containers on the default bridge cannot resolve each other by name
4. Run a container with `--network none` and verify it has no network access
5. Connect a running container to a second network and verify it can communicate on both

---

[← Volumes](./chapter-03-volumes.md) | [Next: Docker Compose →](./chapter-05-compose.md)
