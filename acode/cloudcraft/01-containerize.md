# Chapter 1: "Containerize the Monolith"

[← Overview](00-overview.md) | [Next: Run It in Kubernetes →](02-first-pod.md)

---

Your first morning. Tomás walks you to a whiteboard and draws a single box:

```
┌─────────────────────────────┐
│  prod-please-dont-touch     │
│  ┌───────────────────────┐  │
│  │  Java 11              │  │
│  │  Spring Boot 2.7      │  │
│  │  47 env vars          │  │
│  │  PostgreSQL driver     │  │
│  │  "It works on my      │  │
│  │   machine" — Ava      │  │
│  └───────────────────────┘  │
│  Ubuntu 20.04, 8GB RAM      │
└─────────────────────────────┘
```

> "This is production. One box. One JAR. If it dies, we die. Your job: put it in a container."

You ask why.

> "Because a container is a **promise**. It says: 'I will run exactly the same way on your laptop, in CI, and in production.' No more 'works on my machine.'"

---

## What Is a Container?

Tomás explains it like this:

> "Think of a **shipping container**. Before containers, every port had to figure out how to load bananas differently from cars differently from furniture. Chaos. Then someone invented a standard metal box. Now every crane, every ship, every truck handles the same box. They don't care what's inside."

```
Without containers:          With containers:
┌──────┐ ┌──────┐           ┌──────────┐ ┌──────────┐
│Java 8│ │Java17│           │ 📦 App A │ │ 📦 App B │
│Ubuntu│ │Alpine│           │ (Java 8) │ │ (Java17) │
│libX  │ │libY  │           └──────────┘ └──────────┘
└──┬───┘ └──┬───┘               Same host, isolated
   │ conflicts│
   └────💥────┘
```

A container packages your app + its dependencies into one unit. It shares the host OS kernel but is isolated from everything else.

---

## Docker: The Container Engine

Docker is the tool that builds and runs containers. Three concepts:

| Concept | Analogy | What It Is |
|---|---|---|
| **Image** | A recipe | Read-only blueprint. "Java 17 + my JAR + these configs" |
| **Container** | A dish made from the recipe | Running instance of an image |
| **Dockerfile** | The recipe card | Instructions to build the image |

An image can spawn many containers. Like one recipe can make many dishes.

---

## Your First Dockerfile

Ava reluctantly hands you the monolith's JAR. You write:

```dockerfile
FROM eclipse-temurin:17-jre-alpine
COPY app.jar /app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app.jar"]
```

Four lines. That's it. Let's break them down:

| Line | What It Does |
|---|---|
| `FROM` | Start from a base image (Java 17 runtime, tiny Alpine Linux) |
| `COPY` | Copy your JAR into the image |
| `EXPOSE` | Document which port the app listens on (doesn't actually open it) |
| `ENTRYPOINT` | The command that runs when the container starts |

---

## Build and Run

```bash
docker build -t launchpad-app:v1 .
docker run -p 8080:8080 launchpad-app:v1
```

| Command | What Happens |
|---|---|
| `docker build` | Reads the Dockerfile, creates an image, tags it `launchpad-app:v1` |
| `docker run` | Creates a container from the image, maps port 8080 |

You open `http://localhost:8080`. The app responds. Ava is unimpressed.

> "It ran on my machine too. Without Docker."

---

## Why Layers Matter

Tomás asks you to rebuild after changing one line of code.

```bash
docker build -t launchpad-app:v2 .
```

It takes 2 seconds. Not 30. Why?

> "Docker caches **layers**. Each Dockerfile instruction is a layer. If a layer hasn't changed, Docker reuses it."

```
Layer 1: FROM eclipse-temurin:17  ← cached ✓
Layer 2: COPY app.jar             ← changed, rebuild from here
Layer 3: EXPOSE 8080              ← rebuilt
Layer 4: ENTRYPOINT               ← rebuilt
```

**Rule**: Put things that change often (your code) at the bottom. Things that change rarely (base image, dependencies) at the top.

---

## The "It Works on My Machine" Test

Tomás pulls your image on his laptop:

```bash
docker pull launchpad-app:v1
docker run -p 8080:8080 launchpad-app:v1
```

Same image. Same behavior. No "but I have Java 11" or "my Ubuntu is different."

That's the promise.

---

## What You Learned

```
────────────────────┬──────────────────────────────────────
Concept             │ One-liner
────────────────────┼──────────────────────────────────────
Container           │ Isolated process with its own filesystem
Image               │ Read-only blueprint for a container
Dockerfile          │ Recipe to build an image
Layer               │ Cached step — put stable stuff first
docker build        │ Image from Dockerfile
docker run          │ Container from image
────────────────────┴──────────────────────────────────────
```

---

## The Foreshadow

You have a container. It runs. But it's still one box on one machine. If it crashes, it's gone. If traffic spikes, you can't clone it.

Tomorrow, Nora will say:

> "Run three copies. If one dies, bring it back automatically."

That's not a Docker problem. That's a **Kubernetes** problem.

---

[← Overview](00-overview.md) | [Next: Run It in Kubernetes →](02-first-pod.md)
