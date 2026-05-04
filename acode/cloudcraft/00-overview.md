# CloudCraft: A Kubernetes & AWS Survival Story

You survived PayFlow. You survived EventStream. You thought you were done with 2 AM Slack messages.

Then **Nora**, the VP of Engineering at **LaunchPad** — a SaaS startup that sells project management tools — sends you a DM:

> "We're migrating to Kubernetes and AWS. Our monolith is dying. You start Monday."

You show up. The monolith is a single Spring Boot JAR running on an EC2 instance named `prod-please-dont-touch`. It has 47 environment variables, no health checks, and the deploy process is "SSH in and restart."

Your mission: containerize it, orchestrate it, and wire it to AWS services. Locally. Before anyone touches production.

---

## The Cast

| Character | Role | Personality |
|---|---|---|
| **You** | Platform Engineer | "I just wanted to write Java." |
| **Nora** | VP of Engineering | Draws architecture diagrams on napkins. Always right. |
| **Tomás** | DevOps Lead | Mass of tattoos. Mass of Terraform. Speaks in YAML. |
| **Ava** | Backend Dev | Wrote the monolith. Protective of it. "It works on my machine." |
| **Ghost of Prod** | The EC2 instance | Running since 2021. No one knows the root password. |

---

## The Tools

Everything runs on your laptop. No AWS account needed.

| Tool | What It Does |
|---|---|
| **Docker** | Builds container images |
| **Minikube** | Runs a local Kubernetes cluster |
| **kubectl** | Talks to Kubernetes |
| **LocalStack** | Fakes AWS services (S3, SQS, DynamoDB, Lambda, API Gateway) |
| **awslocal** | AWS CLI that points to LocalStack |

---

## How to Read This

Every chapter follows the same loop:

```
  📋 Nora assigns a task
   │
   ▼
  🤔 You learn the concept (with analogies, not docs)
   │
   ▼
  ⌨️  You do the minimal thing to make it work
   │
   ▼
  💥 Something breaks or surprises you
   │
   ▼
  🧠 You understand WHY
   │
   ▼
  📋 Nora assigns the next task
```

Minimal code. Maximum understanding. Every command you type, you understand *why* you're typing it.

---

## The Roadmap

### Part 1: Kubernetes — "Put It in a Box"

```
────┬────────────────────────────────────┬────────────────────────────────────
 Ch │ The Task                           │ What You Learn
────┼────────────────────────────────────┼────────────────────────────────────
 01 │ "Containerize the monolith"        │ Docker, images, containers, layers
────┼────────────────────────────────────┼────────────────────────────────────
 02 │ "Run it in Kubernetes"             │ Pods, nodes, kubectl, Minikube
────┼────────────────────────────────────┼────────────────────────────────────
 03 │ "It crashed. Bring it back."       │ Deployments, ReplicaSets, self-healing
────┼────────────────────────────────────┼────────────────────────────────────
 04 │ "Users can't reach it"             │ Services, ClusterIP, NodePort, LoadBalancer
────┼────────────────────────────────────┼────────────────────────────────────
 05 │ "Passwords are in the code"        │ ConfigMaps, Secrets, environment variables
────┼────────────────────────────────────┼────────────────────────────────────
 06 │ "Black Friday is coming"           │ Scaling, HPA, resource limits, requests
────┼────────────────────────────────────┼────────────────────────────────────
 07 │ "We need zero-downtime deploys"    │ Rolling updates, readiness/liveness probes
────┼────────────────────────────────────┼────────────────────────────────────
 08 │ "The data disappeared"             │ Volumes, PersistentVolumeClaims, StatefulSets
────┴────────────────────────────────────┴────────────────────────────────────
```

### Part 2: AWS with LocalStack — "Wire It to the Cloud"

```
────┬────────────────────────────────────┬────────────────────────────────────
 Ch │ The Task                           │ What You Learn
────┼────────────────────────────────────┼────────────────────────────────────
 09 │ "Store files somewhere"            │ S3 buckets, objects, presigned URLs
────┼────────────────────────────────────┼────────────────────────────────────
 10 │ "Decouple the email sender"        │ SQS queues, producers, consumers
────┼────────────────────────────────────┼────────────────────────────────────
 11 │ "We need a fast lookup table"      │ DynamoDB tables, keys, queries
────┼────────────────────────────────────┼────────────────────────────────────
 12 │ "Run code without a server"        │ Lambda functions, triggers, cold starts
────┼────────────────────────────────────┼────────────────────────────────────
 13 │ "Expose it as an API"              │ API Gateway, routes, Lambda integration
────┼────────────────────────────────────┼────────────────────────────────────
 14 │ "S3 upload should trigger resize"  │ Event-driven: S3 → Lambda → SQS
────┼────────────────────────────────────┼────────────────────────────────────
 15 │ "Secrets can't be in env vars"     │ Secrets Manager, Parameter Store
────┼────────────────────────────────────┼────────────────────────────────────
 16 │ Nora's final review                │ Architecture, production checklist
────┴────────────────────────────────────┴────────────────────────────────────
```

---

## Prerequisites

- **Docker Desktop** installed and running
- **Java 17+** (for the Spring Boot monolith)
- **A terminal** (bash, zsh, PowerShell — doesn't matter)
- **Patience** — Kubernetes YAML will test it

We'll install Minikube, kubectl, and LocalStack together in Chapter 1.

---

[Next: Chapter 1 — "Containerize the Monolith" →](01-containerize.md)
