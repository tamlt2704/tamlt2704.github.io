# Chapter 2: The Load Balancer

[← Ch 1](chapter-01-the-bottleneck.md) | [Ch 3 →](chapter-03-object-storage.md)

---

## The Crisis

You spun up two more app servers. Traffic is still hitting the original box.

**Kai** (Slack, 2:30 PM):
> How do users know which server to talk to? DNS round-robin?

**Ops Omar**:
> DNS round-robin has a TTL of 300 seconds. If a server dies, users hit a dead IP for 5 minutes. Also, browsers cache DNS forever.

**Sana**:
> We need something in front that knows which servers are alive and routes traffic to them.

**Amir**:
> A load balancer. But which kind? I've seen people spend weeks on this decision.

---

## Architecture (Before)

```
┌──────────┐         ┌──────────┐
│  Users   │────────→│ Server 1 │  (the only server)
└──────────┘         └──────────┘
                     Server 2, 3 exist but get no traffic
```

## Architecture (After)

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Users   │────→│    LB    │──┬─→│ Server 1 │
└──────────┘     └──────────┘  │  └──────────┘
                               ├─→┌──────────┐
                               │  │ Server 2 │
                               │  └──────────┘
                               └─→┌──────────┐
                                  │ Server 3 │
                                  └──────────┘
```

---

## Concept: L4 vs L7 Load Balancers

### Layer 4 (Transport)

Operates on TCP/UDP. Sees IP addresses and ports. Doesn't understand HTTP.

```
Client ──TCP──→ LB ──TCP──→ Server
         (LB sees: src IP, dst port)
         (LB doesn't see: URL, headers, cookies)
```

**Pros**: Fast (no parsing), low latency, handles any protocol
**Cons**: Can't route by URL path, can't do SSL termination, no cookie-based routing

### Layer 7 (Application)

Operates on HTTP. Sees URLs, headers, cookies, request bodies.

```
Client ──HTTPS──→ LB ──HTTP──→ Server
          (LB sees everything: path, headers, cookies)
          (LB terminates SSL)
```

**Pros**: Smart routing (path-based, header-based), SSL termination, can inject headers
**Cons**: Slightly higher latency (~1-2ms), must understand the protocol

### GhostDrop's Choice

**L7** — because:
- We need path-based routing (`/api/*` → app servers, `/files/*` → storage later)
- SSL termination at the LB simplifies server config
- We want to add sticky sessions for WebSocket connections later
- Health checks can hit a real HTTP endpoint, not just check TCP port

---

## Concept: Load Balancing Algorithms

| Algorithm | How It Works | Best For |
|-----------|-------------|----------|
| **Round Robin** | 1, 2, 3, 1, 2, 3... | Equal servers, stateless requests |
| **Weighted Round Robin** | Server A gets 3x, B gets 1x | Mixed instance sizes |
| **Least Connections** | Send to server with fewest active connections | Variable request duration |
| **IP Hash** | Hash client IP → consistent server | Session affinity without cookies |
| **Random** | Pick one randomly | Surprisingly effective at scale |

### GhostDrop's Choice

**Least Connections** — because file uploads take 5-30 seconds while metadata lookups take 50ms. Round robin would overload a server that got three concurrent uploads.

```
Server 1: 12 active connections  ← next request goes here? No.
Server 2: 3 active connections   ← YES, send it here
Server 3: 8 active connections
```

---

## Concept: Health Checks

The LB needs to know which servers are alive.

```python
# health_check.py — what the LB hits every 10 seconds
@app.get("/health")
def health():
    # Check critical dependencies
    try:
        db.execute("SELECT 1")
        redis.ping()
        return {"status": "healthy"}, 200
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 503
```

### Health Check Configuration

```
Interval:           10 seconds
Timeout:            5 seconds
Unhealthy threshold: 3 consecutive failures
Healthy threshold:   2 consecutive successes
```

**Why not check every 1 second?** Health checks are traffic too. 3 servers × 1 check/sec = 3 req/sec of overhead. At 10s intervals, it's 0.3 req/sec.

**Why 3 failures before marking unhealthy?** One timeout could be a network blip. Three in a row means it's really down.

---

## Concept: Sticky Sessions

Some requests need to go to the same server (WebSocket connections, file upload chunks).

### Methods

| Method | Mechanism | Tradeoff |
|--------|-----------|----------|
| Cookie-based | LB sets `SERVERID=srv2` cookie | Requires cookie support |
| IP Hash | Hash(client IP) → server | Breaks behind NAT/proxies |
| URL parameter | `?server=srv2` | Ugly, leaks infra details |

### GhostDrop's Approach

Cookie-based sticky sessions for upload endpoints only:

```
# ALB target group config
stickiness:
  enabled: true
  type: app_cookie
  cookie_name: GHOSTDROP_UPLOAD_SESSION
  duration: 3600  # 1 hour
```

Regular API calls? No stickiness. Stateless. Any server can handle them.

---

## Concept: LB Redundancy

**Omar**: "Wait. If the load balancer dies, everything dies. We replaced one SPOF with another."

Correct. You need redundant LBs.

```
┌──────────┐     ┌──────────┐
│  LB (A)  │     │  LB (B)  │   ← Active/Passive
│ (active) │     │(standby) │
└─────┬────┘     └─────┬────┘
      │                 │
      └────────┬────────┘
               │  (floating IP / DNS failover)
               ▼
         ┌──────────┐
         │  Servers  │
         └──────────┘
```

**Managed option (AWS ALB)**: AWS handles redundancy across AZs. You don't manage failover.

**Self-hosted (HAProxy/Nginx)**: You run two instances with keepalived and a floating VIP.

### GhostDrop's Choice

AWS ALB. We have 3 weeks. We're not debugging keepalived at 3 AM.

---

## GhostDrop Implementation

```yaml
# terraform/alb.tf (simplified)
resource "aws_lb" "ghostdrop" {
  name               = "ghostdrop-alb"
  internal           = false
  load_balancer_type = "application"
  subnets            = var.public_subnets
  security_groups    = [aws_security_group.alb.id]
}

resource "aws_lb_target_group" "app" {
  name     = "ghostdrop-app"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = var.vpc_id

  health_check {
    path                = "/health"
    interval            = 10
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }

  stickiness {
    type            = "app_cookie"
    cookie_name     = "GHOSTDROP_UPLOAD"
    cookie_duration = 3600
    enabled         = true
  }
}

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.ghostdrop.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = var.cert_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}
```

---

## Tradeoffs

| Decision | Gain | Cost |
|----------|------|------|
| L7 over L4 | Smart routing, SSL termination | ~1-2ms added latency |
| Least connections | Handles mixed request durations | Slightly more LB state |
| Managed ALB over self-hosted | No ops burden, built-in HA | $16/mo + $0.008/LCU-hr |
| Sticky sessions (uploads only) | Chunked uploads work | Uneven load if one user uploads a lot |

---

## Why Not Just...

**"Why not use DNS round-robin?"**
No health checks. Stale TTLs. Can't remove a dead server quickly. Fine for distributing across regions, terrible for server-level balancing.

**"Why not Nginx as a reverse proxy?"**
You could. But you'd manage the Nginx box, its redundancy, its config reloads, its SSL certs. ALB does all that for $16/month base.

**"Why not put the LB on the same box as the app?"**
Then it's not a load balancer. It's a reverse proxy on a single server. You still have one point of failure.

---

## Exercise

GhostDrop adds a WebSocket endpoint for real-time upload progress. The LB keeps closing WebSocket connections after 60 seconds.

1. Why is this happening?
2. What LB setting needs to change?
3. Should WebSocket traffic go through the same LB or a separate one?

<details>
<summary>Hint</summary>

ALBs have an idle timeout (default 60s). WebSocket connections are long-lived. Increase idle timeout to 3600s for the WebSocket target group. Consider a separate target group with different timeout settings rather than a separate LB.
</details>

---

## Quick Reference

| Term | Definition |
|------|-----------|
| **L4 LB** | Routes by IP/port, protocol-agnostic |
| **L7 LB** | Routes by HTTP content (path, headers, cookies) |
| **Round Robin** | Distribute requests sequentially across servers |
| **Least Connections** | Send to server with fewest active requests |
| **Health Check** | Periodic probe to verify server is alive |
| **Sticky Session** | Route same client to same server |
| **SSL Termination** | LB handles HTTPS, backends use HTTP |
| **SPOF** | Single Point of Failure |

---

## What Breaks Next

Load balancer is live. Three servers share the traffic. CPU drops from 97% to 35%.

Then a user uploads a 2GB file to Server 2. Another user requests that file and gets routed to Server 3. The file doesn't exist there.

Files live on local disk. With multiple servers, that's broken by design.

You need object storage.

[← Ch 1](chapter-01-the-bottleneck.md) | [Ch 3 →](chapter-03-object-storage.md)
