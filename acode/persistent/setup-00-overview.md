# Setup: Quick Start Guide

Get PostgreSQL + Kafka + Schema Registry running in **one command**.

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- Java 17+ and Maven (for the Spring Boot app)

## 1. Start Everything

```bash
# Copy the docker-compose file to your project root
cp persistent/setup-docker-compose.yml docker-compose.yml

# Start all services
docker compose up -d
```

That's it. Wait ~30 seconds for everything to be healthy.

## 2. Verify

```bash
# Check all services are running
docker compose ps

# Test PostgreSQL
docker exec -it $(docker compose ps -q postgres) psql -U payflow -c "SELECT 1"

# Test Kafka — list topics
docker exec -it $(docker compose ps -q kafka) kafka-topics --bootstrap-server localhost:9092 --list

# Test Schema Registry
curl http://localhost:8081/subjects
```

## 3. Access Points

| Service | URL / Connection | Credentials |
|---|---|---|
| PostgreSQL | `localhost:5432/payflow` | `payflow` / `payflow` |
| Kafka | `localhost:9092` | — |
| Schema Registry | `http://localhost:8081` | — |
| Kafka UI | `http://localhost:8080` | — |

## 4. Stop / Clean Up

```bash
docker compose down          # Stop containers, keep data
docker compose down -v       # Stop containers AND delete data
```

## Detailed Guides

| Guide | What You'll Learn |
|---|---|
| [Docker Services Explained](setup-01-docker.md) | What each container does and why |
| [Spring Boot Config](setup-02-spring-boot.md) | `application.yml` and `pom.xml` to connect to everything |
