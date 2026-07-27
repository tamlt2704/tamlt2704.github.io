# AWS Cloud Architecture — Step by Step

---

## The Big Picture

```
Level 1: Core Services (what everything is built on)
    ↓
Level 2: Networking (how things talk to each other)
    ↓
Level 3: Application Architecture (patterns for building apps)
    ↓
Level 4: Data Architecture (storage + databases)
    ↓
Level 5: Security (protecting everything)
    ↓
Level 6: Reliability & Scaling (handling failure + growth)
    ↓
Level 7: Cost Optimisation (not going broke)
```

---

## Level 1: Core Services

### The 6 Services That Cover 80% of Projects

| Service | What it is | Analogy |
|---------|-----------|---------|
| **EC2** | Virtual machines | Renting a computer |
| **S3** | Object storage (files) | Infinite hard drive |
| **RDS** | Managed databases (PostgreSQL, MySQL) | Database someone else maintains |
| **Lambda** | Run code without servers | Pay-per-use function |
| **ECS/EKS** | Run containers (Docker) | Docker but AWS manages the servers |
| **CloudFront** | CDN (content delivery) | Copies of your site worldwide |

### How They Relate

```
User → CloudFront (CDN) → S3 (static files: HTML, CSS, JS)
                        → ALB (load balancer) → ECS/EC2 (backend API)
                                                    → RDS (database)
                                                    → S3 (file uploads)
```

### EC2 — Virtual Machines

```
You choose:
  - Instance type (CPU + RAM): t3.micro, m5.large, c6g.xlarge
  - OS: Amazon Linux, Ubuntu, Windows
  - Storage: EBS volumes (SSDs attached to the instance)
  - Network: VPC, subnet, security group
```

**Instance type naming:**

```
m5.large
│ │  └── Size (nano → micro → small → medium → large → xlarge → 2xlarge...)
│ └── Generation (higher = newer, better price/performance)
└── Family: m=general, c=compute, r=memory, t=burstable, g=GPU
```

### S3 — Object Storage

```
Bucket: my-app-uploads
├── images/
│   ├── photo1.jpg
│   └── photo2.png
├── data/
│   └── report.csv
└── backups/
    └── db-2024-01.sql.gz
```

**Key concepts:**
- **Bucket** = a container (globally unique name)
- **Object** = a file (up to 5TB)
- **Key** = the file path (`images/photo1.jpg`)
- **Durability** = 99.999999999% (11 nines) — files basically never lost
- **Storage classes** = trade access speed for cost (Standard → Infrequent Access → Glacier)

### Lambda — Serverless Functions

```java
public class Handler implements RequestHandler<APIGatewayProxyRequestEvent, APIGatewayProxyResponseEvent> {

    @Override
    public APIGatewayProxyResponseEvent handleRequest(APIGatewayProxyRequestEvent event, Context context) {
        String body = event.getBody();
        // Process request...
        return new APIGatewayProxyResponseEvent()
            .withStatusCode(200)
            .withBody("{\"message\": \"Hello\"}");
    }
}
```

**When to use Lambda:**
- Event-driven (file uploaded → process it)
- Low traffic / spiky traffic (pay per invocation, not per hour)
- Simple API endpoints
- Scheduled tasks (cron jobs)

**When NOT to use:**
- Long-running processes (> 15 min)
- Need persistent connections (WebSockets long-lived)
- Very high, steady traffic (cheaper to run a container 24/7)

---

## Level 2: Networking

### VPC — Your Private Network

```
┌─────────────────── VPC (10.0.0.0/16) ───────────────────┐
│                                                           │
│  ┌─── Public Subnet (10.0.1.0/24) ───┐                  │
│  │  ALB (Load Balancer)               │                  │
│  │  NAT Gateway                       │ ← Internet       │
│  └────────────────────────────────────┘   accessible     │
│                                                           │
│  ┌─── Private Subnet (10.0.2.0/24) ──┐                  │
│  │  ECS Tasks (your app)              │                  │
│  │  Lambda functions                  │ ← NO internet    │
│  └────────────────────────────────────┘   access directly│
│                                                           │
│  ┌─── Private Subnet (10.0.3.0/24) ──┐                  │
│  │  RDS (database)                    │                  │
│  │  ElastiCache (Redis)               │ ← Most isolated  │
│  └────────────────────────────────────┘                  │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

**Key concepts:**

| Concept | What it is |
|---------|-----------|
| **VPC** | Your isolated network in AWS (like your own data center) |
| **Subnet** | A segment of the VPC (public = internet-facing, private = internal only) |
| **Security Group** | Firewall rules per resource (allow port 443 from anywhere) |
| **Internet Gateway** | Door to the internet for public subnets |
| **NAT Gateway** | Lets private subnet resources reach the internet (outbound only) |
| **Route Table** | Rules for where traffic goes |

### Security Groups vs NACLs

| | Security Group | NACL |
|-|---------------|------|
| Level | Per instance/resource | Per subnet |
| State | Stateful (allow out = auto-allow response back) | Stateless (must explicitly allow both directions) |
| Rules | Allow only | Allow + Deny |
| Use | Primary firewall | Subnet-level backstop |

### DNS — Route 53

```
user types: myapp.com
    → Route 53 resolves to CloudFront distribution
        → CloudFront routes /api/* to ALB
        → CloudFront routes /* to S3 (static site)
```

---

## Level 3: Application Architecture Patterns

### Pattern 1: Static Site (Your Current Project)

```
S3 (static files) → CloudFront (CDN) → Users
```

- Cheapest option (~$0.50/month for low traffic)
- What GitHub Pages does under the hood
- Good for: blogs, portfolios, documentation

### Pattern 2: Serverless API

```
API Gateway → Lambda → DynamoDB
                    → S3
                    → SQS → Lambda (async processing)
```

- No servers to manage
- Scales to zero (no traffic = no cost)
- Good for: APIs with spiky/low traffic, event processing

### Pattern 3: Containerised Microservices

```
ALB → ECS Fargate → Service A → RDS
                  → Service B → DynamoDB
                  → Service C → ElastiCache
```

- Predictable performance
- Good for: steady-traffic apps, complex backends

### Pattern 4: Full Modern Web App

```
┌─── Frontend ──────────────────────────────────┐
│  S3 + CloudFront (React/Next.js static)       │
└───────────────────────┬───────────────────────┘
                        │ API calls
┌─── Backend ───────────▼───────────────────────┐
│  API Gateway / ALB                             │
│       ↓                                        │
│  ECS Fargate (Java/Node containers)            │
│       ↓                                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │   RDS    │  │ DynamoDB │  │    S3    │    │
│  │(Postgres)│  │(sessions)│  │ (files)  │    │
│  └──────────┘  └──────────┘  └──────────┘    │
└────────────────────────────────────────────────┘
```

### How to Choose

| Factor | Serverless (Lambda) | Containers (ECS/EKS) | VMs (EC2) |
|--------|--------------------|--------------------|-----------|
| Traffic | Spiky / low | Steady / high | Steady / predictable |
| Cold starts | Yes (can be slow) | No | No |
| Max execution | 15 min | Unlimited | Unlimited |
| Scaling | Automatic | Auto (with config) | Manual / auto-scaling groups |
| Cost at low traffic | Cheapest | Moderate | Most expensive |
| Cost at high traffic | Can be expensive | Predictable | Cheapest |
| Operational burden | Least | Medium | Most |

---

## Level 4: Data Architecture

### Choosing a Database

| Need | Service | Type |
|------|---------|------|
| Structured data, relationships, transactions | **RDS** (PostgreSQL, MySQL) | Relational |
| Key-value, high throughput, flexible schema | **DynamoDB** | NoSQL |
| Caching, sessions, leaderboards | **ElastiCache** (Redis) | In-memory |
| Full-text search | **OpenSearch** | Search engine |
| Time-series (metrics, IoT) | **Timestream** | Time-series |
| Graph relationships | **Neptune** | Graph |
| Data warehouse (analytics) | **Redshift** | Columnar |

### RDS vs DynamoDB — The Big Decision

| | RDS (PostgreSQL) | DynamoDB |
|-|-----------------|----------|
| Query flexibility | Any query (SQL) | Must design access patterns upfront |
| Scaling | Vertical (bigger instance) | Horizontal (infinite) |
| Cost model | Per hour (instance running) | Per request + storage |
| Transactions | Full ACID | Limited (single table) |
| Schema | Enforced (migrations) | Flexible (schema-on-read) |
| Best for | Complex queries, reporting, relationships | High-traffic, simple access patterns, serverless |

**Rule of thumb:** If you'd use JOINs a lot → RDS. If your access patterns are simple and known upfront → DynamoDB.

### S3 as a Data Lake

```
Raw Data (landing zone)
    → S3 bucket: raw/
        └── 2024/01/15/events.json.gz

Processed Data
    → S3 bucket: processed/
        └── 2024/01/aggregated-metrics.parquet

Analytics
    → Athena queries S3 directly (SQL on files — no server)
    → Redshift for heavy analytics
```

---

## Level 5: Security

### The Shared Responsibility Model

```
┌─────────────────────────────────────┐
│  YOUR responsibility:                │
│  • App code security                 │
│  • IAM policies (who can do what)    │
│  • Data encryption                   │
│  • Network config (security groups)  │
│  • OS patching (EC2)                 │
│  • Secrets management                │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│  AWS responsibility:                 │
│  • Physical security (data centers)  │
│  • Hardware maintenance              │
│  • Network infrastructure            │
│  • Hypervisor patching               │
│  • Managed service internals         │
└─────────────────────────────────────┘
```

### IAM — Who Can Do What

```json
{
  "Effect": "Allow",
  "Action": ["s3:GetObject", "s3:PutObject"],
  "Resource": "arn:aws:s3:::my-bucket/uploads/*"
}
```

**Principle of least privilege:** Grant only the permissions needed, nothing more.

| Concept | What it is |
|---------|-----------|
| **User** | A person (login credentials) |
| **Role** | An identity for services (EC2, Lambda assume a role) |
| **Policy** | A document listing allowed/denied actions |
| **Group** | Collection of users sharing the same policies |

**Golden rules:**
- Never use root account for daily work
- Services get roles, not access keys
- No wildcards (`*`) in production policies
- Enable MFA on all human accounts

### Encryption

| Where | Service | Default? |
|-------|---------|----------|
| Data at rest (S3) | SSE-S3 or SSE-KMS | ✅ (since 2023) |
| Data at rest (RDS) | KMS encryption | Enable at creation |
| Data at rest (EBS) | KMS encryption | Enable at creation |
| Data in transit | TLS (HTTPS) | You configure via ACM certs |
| Secrets | Secrets Manager or SSM Parameter Store | You must use it |

### Secrets Management

```
❌ NEVER: hardcode in source, environment variables in plain text, .env files in git

✅ ALWAYS: AWS Secrets Manager or SSM Parameter Store
```

```java
// Fetch secret at runtime
SecretsManagerClient client = SecretsManagerClient.create();
String secret = client.getSecretValue(r -> r.secretId("my-db-credentials"))
    .secretString();
```

---

## Level 6: Reliability & Scaling

### High Availability — Survive Failures

```
Region: eu-west-1
├── AZ: eu-west-1a
│   ├── EC2 instance 1
│   └── RDS primary
├── AZ: eu-west-1b
│   ├── EC2 instance 2
│   └── RDS standby (auto-failover)
└── AZ: eu-west-1c
    └── EC2 instance 3
```

**Availability Zones (AZs)** = separate data centers in the same region. If one burns down, others keep running.

**Rule:** Always deploy across at least 2 AZs.

### Auto Scaling

```
Normal:    [Instance 1] [Instance 2]
Spike:     [Instance 1] [Instance 2] [Instance 3] [Instance 4]  ← auto-added
After:     [Instance 1] [Instance 2]                             ← auto-removed
```

Configure rules:
- If CPU > 70% for 5 minutes → add instance
- If CPU < 30% for 10 minutes → remove instance

### Load Balancing

```
Users → ALB (distributes traffic evenly)
         ├── Instance 1 (healthy ✓)
         ├── Instance 2 (healthy ✓)
         └── Instance 3 (unhealthy ✗ — ALB stops sending traffic)
```

| Type | Use for |
|------|---------|
| **ALB** (Application) | HTTP/HTTPS, path-based routing, WebSockets |
| **NLB** (Network) | TCP/UDP, ultra-low latency, static IPs |

### Well-Architected Framework — 6 Pillars

| Pillar | Key Question |
|--------|-------------|
| **Operational Excellence** | Can you monitor and improve? |
| **Security** | Can you protect data and systems? |
| **Reliability** | Can you recover from failure? |
| **Performance Efficiency** | Are you using the right resources? |
| **Cost Optimisation** | Are you spending wisely? |
| **Sustainability** | Are you minimising environmental impact? |

---

## Level 7: Cost Optimisation

### Where Money Goes (Typical App)

| Service | % of Bill | How to reduce |
|---------|-----------|--------------|
| EC2 / ECS | 40-60% | Right-size instances, Reserved Instances, Spot |
| RDS | 15-25% | Right-size, Reserved Instances, Aurora Serverless |
| Data Transfer | 10-20% | CloudFront caching, VPC endpoints, same-AZ traffic |
| S3 | 5-10% | Lifecycle policies (move old data to Glacier) |
| Lambda | 1-5% | Optimise memory/duration, reduce invocations |

### Cost Saving Strategies

| Strategy | Savings | Risk |
|----------|---------|------|
| **Reserved Instances** (1-3 year commit) | 30-60% | Locked in |
| **Spot Instances** (spare capacity) | 60-90% | Can be interrupted |
| **Savings Plans** (commit to spend/hour) | 30-50% | Less flexible |
| **Right-sizing** (use smaller instances) | 20-40% | None |
| **S3 lifecycle rules** (archive old data) | 50-80% on storage | Retrieval takes time |
| **Turn off dev/test at night** | 65% | None |

### Free Tier (For Learning)

| Service | Free Amount | Duration |
|---------|-------------|----------|
| EC2 | 750 hrs/month t2.micro | 12 months |
| S3 | 5 GB storage | 12 months |
| RDS | 750 hrs/month db.t2.micro | 12 months |
| Lambda | 1M requests/month | Always free |
| DynamoDB | 25 GB storage, 25 read/write units | Always free |
| CloudFront | 1 TB data transfer/month | 12 months |

---

## Architecture Diagrams — How to Think About It

### Start Simple, Add Complexity When Needed

```
V1 (prototype):
  S3 + CloudFront

V2 (need an API):
  S3 + CloudFront + API Gateway + Lambda + DynamoDB

V3 (need more power):
  S3 + CloudFront + ALB + ECS Fargate + RDS

V4 (need scale + reliability):
  Multi-AZ + Auto Scaling + ElastiCache + SQS + CloudWatch
```

Don't start at V4. Start at V1 and add when you hit a real problem.

---

## Certifications Path

| Cert | Level | Focus |
|------|-------|-------|
| **Cloud Practitioner** | Beginner | What services exist, billing basics |
| **Solutions Architect Associate** | Intermediate | Design architectures, choose services |
| **Developer Associate** | Intermediate | Build and deploy apps on AWS |
| **Solutions Architect Professional** | Advanced | Complex multi-account, migration, optimization |
| **DevOps Engineer Professional** | Advanced | CI/CD, automation, monitoring |

**Recommendation:** Start with **Solutions Architect Associate** — most useful, most recognised, covers architecture thinking.

---

## Practice Projects

| Project | Services Used |
|---------|-------------|
| **Static blog on S3 + CloudFront** | S3, CloudFront, Route 53, ACM |
| **Serverless REST API** | API Gateway, Lambda, DynamoDB |
| **Containerised web app** | ECS Fargate, ALB, RDS, ECR |
| **Image processing pipeline** | S3 event → Lambda → resize → S3 |
| **Real-time chat** | API Gateway WebSocket, Lambda, DynamoDB |
| **Data pipeline** | S3 → Lambda → DynamoDB → Athena |

---

## Resources

| Resource | What | Free? |
|----------|------|-------|
| [AWS Free Tier](https://aws.amazon.com/free/) | Hands-on practice | ✅ |
| [AWS Well-Architected Labs](https://wellarchitectedlabs.com) | Guided exercises | ✅ |
| [Adrian Cantrill's courses](https://learn.cantrill.io) | Best video courses | 💰 |
| [Stephane Maarek (Udemy)](https://www.udemy.com/user/stephane-maarek/) | Cert prep courses | 💰 |
| [AWS Architecture Center](https://aws.amazon.com/architecture/) | Reference architectures | ✅ |
| [The Amazon Builders' Library](https://aws.amazon.com/builders-library/) | How Amazon builds systems | ✅ |
| [AWS re:Invent videos (YouTube)](https://youtube.com/@AWSEventsChannel) | Deep dive talks | ✅ |
