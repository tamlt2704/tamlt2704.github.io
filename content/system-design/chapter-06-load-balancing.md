# Chapter 6: Load Balancing & Reverse Proxies

[← Chapter 5: API Design](/blog/system-design/chapter-05-api-design) | [Chapter 7: Microservices →](/blog/system-design/chapter-07-microservices)

---

## What is a Load Balancer?

A load balancer distributes incoming traffic across multiple backend servers to ensure no single server is overwhelmed.

```
                    ┌──────────────┐
                    │    Client    │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │Load Balancer │  ← single entry point
                    └──┬───┬───┬──┘
                       │   │   │
              ┌────────┘   │   └────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Server 1 │ │ Server 2 │ │ Server 3 │
        └──────────┘ └──────────┘ └──────────┘
```

**What it provides:**

- **High availability** — if one server dies, traffic goes to others
- **Scalability** — add more servers to handle more traffic
- **SSL termination** — decrypt HTTPS at the LB, backend uses plain HTTP
- **Health checking** — automatically remove unhealthy servers

---

## Load Balancing Algorithms

| Algorithm                | How It Works                                  | Best For                                     |
| ------------------------ | --------------------------------------------- | -------------------------------------------- |
| **Round Robin**          | Rotate through servers sequentially           | Equal-capacity servers, stateless apps       |
| **Weighted Round Robin** | Servers with higher weight get more requests  | Mixed-capacity servers                       |
| **Least Connections**    | Send to server with fewest active connections | Long-lived connections, varying request cost |
| **Least Response Time**  | Send to fastest-responding server             | When server performance varies               |
| **IP Hash**              | Hash client IP → always same server           | Session affinity without cookies             |
| **Consistent Hashing**   | Hash-ring based distribution                  | Cache servers, minimizes redistribution      |
| **Random**               | Pick a random server                          | Simple, surprisingly effective at scale      |

### Round Robin vs Least Connections

```
Round Robin (equal distribution):
Request 1 → Server A
Request 2 → Server B
Request 3 → Server C
Request 4 → Server A  (even if A is still processing request 1)

Least Connections (smart distribution):
Server A: 5 active connections
Server B: 2 active connections
Server C: 8 active connections
→ Next request goes to Server B
```

**Rule of thumb:** Use Least Connections for APIs with variable response times. Use Round Robin for uniform, fast requests.

---

## Layer 4 vs Layer 7 Load Balancing

```
OSI Model:
Layer 7 (Application): HTTP, HTTPS, WebSocket
Layer 4 (Transport):   TCP, UDP
```

| Aspect   | Layer 4 (TCP)             | Layer 7 (HTTP)                         |
| -------- | ------------------------- | -------------------------------------- |
| Inspects | IP + port only            | Full HTTP request (URL, headers, body) |
| Speed    | Faster (no parsing)       | Slower (must parse HTTP)               |
| Routing  | By connection             | By URL path, header, cookie            |
| SSL      | Pass-through or terminate | Always terminates                      |
| Use case | High throughput, non-HTTP | Content-based routing, API gateway     |

**Layer 7 routing examples:**

```nginx
# Route by URL path
/api/users/*    → user-service cluster
/api/orders/*   → order-service cluster
/static/*       → CDN / static file server

# Route by header
X-API-Version: 2  → v2-service cluster

# Route by cookie (canary deployment)
canary=true       → canary cluster (10% of servers)
```

---

## Reverse Proxy

A reverse proxy sits in front of your servers. A load balancer IS a reverse proxy, but a reverse proxy does more:

```
Client → [Reverse Proxy] → Backend Servers

Functions:
- Load balancing
- SSL termination
- Caching static content
- Compression (gzip/brotli)
- Rate limiting
- Request/response transformation
- Security (hide backend topology)
```

### Nginx as Reverse Proxy

```nginx
upstream backend {
    least_conn;
    server 10.0.0.1:8080 weight=3;
    server 10.0.0.2:8080 weight=2;
    server 10.0.0.3:8080 weight=1;
    server 10.0.0.4:8080 backup;  # only used when others are down
}

server {
    listen 443 ssl;
    server_name api.example.com;

    ssl_certificate /etc/ssl/cert.pem;
    ssl_certificate_key /etc/ssl/key.pem;

    location /api/ {
        proxy_pass http://backend;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_connect_timeout 5s;
        proxy_read_timeout 30s;
    }

    location /static/ {
        root /var/www;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

---

## Health Checks

The LB must know which servers are healthy:

### Passive Health Checks

Monitor responses from normal traffic:

- 3 consecutive 5xx responses → mark unhealthy
- 2 consecutive 200 responses → mark healthy again

### Active Health Checks

Periodically probe a dedicated endpoint:

```
Every 10 seconds:
  GET /health → 200 OK { "status": "UP", "db": "UP", "redis": "UP" }

If 3 consecutive failures → remove from pool
If 2 consecutive successes → add back to pool
```

```java
@RestController
public class HealthController {

    private final DataSource dataSource;
    private final RedisTemplate<String, String> redis;

    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        Map<String, String> status = new HashMap<>();
        boolean healthy = true;

        try {
            dataSource.getConnection().isValid(2);
            status.put("db", "UP");
        } catch (Exception e) {
            status.put("db", "DOWN");
            healthy = false;
        }

        try {
            redis.opsForValue().get("health-check");
            status.put("redis", "UP");
        } catch (Exception e) {
            status.put("redis", "DOWN");
            healthy = false;
        }

        status.put("status", healthy ? "UP" : "DEGRADED");
        return ResponseEntity.status(healthy ? 200 : 503).body(status);
    }
}
```

---

## SSL/TLS Termination

Decrypt HTTPS at the load balancer so backend servers don't need to handle encryption:

```
Client ──HTTPS──▶ Load Balancer ──HTTP──▶ Backend Servers
                  (decrypts here)         (plain HTTP, faster)
```

**Benefits:**

- Backend servers are simpler (no cert management)
- LB can inspect HTTP content for routing
- Centralized certificate renewal
- Hardware acceleration for SSL at the LB

**When to use end-to-end encryption instead:**

- Compliance requirements (PCI-DSS, HIPAA)
- Zero-trust network architecture
- Traffic between LB and backends crosses untrusted networks

---

## Sticky Sessions (Session Affinity)

Route the same user to the same server. Needed when servers hold session state.

```
Methods:
1. Cookie-based: LB sets a cookie with server ID
   Set-Cookie: SERVERID=server2; Path=/

2. IP-based: Hash client IP → same server
   (breaks with NAT, mobile networks)
```

**Better approach:** Make services stateless (store sessions in Redis) and avoid sticky sessions entirely. Sticky sessions prevent even load distribution and complicate failover.

---

## Global Server Load Balancing (GSLB)

Route users to the nearest datacenter:

```
User in Asia ──DNS──▶ asia.api.example.com ──▶ Tokyo DC
User in EU   ──DNS──▶ eu.api.example.com   ──▶ Frankfurt DC
User in US   ──DNS──▶ us.api.example.com   ──▶ Virginia DC
```

**Strategies:**

- **GeoDNS** — resolve to nearest datacenter IP based on client location
- **Anycast** — same IP advertised from multiple locations, BGP routes to nearest
- **Latency-based** — Route 53 measures latency, picks fastest

---

## Common Load Balancer Options

| Tool        | Type           | Best For                                        |
| ----------- | -------------- | ----------------------------------------------- |
| **Nginx**   | Software L7    | Reverse proxy, static files, small-medium scale |
| **HAProxy** | Software L4/L7 | High performance, TCP load balancing            |
| **AWS ALB** | Managed L7     | AWS apps, path-based routing, WebSocket         |
| **AWS NLB** | Managed L4     | Ultra-low latency, millions of connections      |
| **Envoy**   | Software L7    | Service mesh sidecar, gRPC, observability       |
| **Traefik** | Software L7    | Kubernetes ingress, auto-discovery              |

---

## Design Considerations

| Question                  | Guidance                                                        |
| ------------------------- | --------------------------------------------------------------- |
| Single LB = SPOF?         | Use active-passive pair or cloud-managed (AWS ALB handles this) |
| How many backend servers? | Start with 2 (redundancy), scale based on CPU/latency metrics   |
| Connection draining?      | On scale-down, finish in-flight requests before removing server |
| Timeouts?                 | Connect: 5s, Read: 30s, Idle: 60s (tune per service)            |
| WebSocket?                | Need L7 LB with connection upgrade support (ALB, Nginx)         |

---

[Chapter 7: Microservices Architecture →](/blog/system-design/chapter-07-microservices)
