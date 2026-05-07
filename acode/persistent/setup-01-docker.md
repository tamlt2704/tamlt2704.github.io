# Setup: Docker Services Explained

[← Quick Start](setup-00-overview.md) | [Next: Spring Boot Config →](setup-02-spring-boot.md)

---

## What's in the Docker Compose

```
┌─────────────────────────────────────────────────────┐
│                  Your Machine                        │
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌────────────────┐   │
│  │PostgreSQL│  │  Kafka   │  │Schema Registry │   │
│  │  :5432   │  │  :9092   │  │    :8081       │   │
│  └──────────┘  └──────────┘  └────────────────┘   │
│                                                     │
│  ┌──────────┐                                      │
│  │ Kafka UI │  ← Browse topics, messages, schemas  │
│  │  :8080   │                                      │
│  └──────────┘                                      │
│                                                     │
│  ┌──────────────────────────────────────────┐      │
│  │  Your Spring Boot App (runs on host)     │      │
│  │  Connects to localhost:5432, :9092, :8081│      │
│  └──────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────┘
```

## Service-by-Service Breakdown

### PostgreSQL 16

```yaml
postgres:
  image: postgres:16-alpine    # Alpine = smaller image (~80MB vs ~400MB)
  ports:
    - "5432:5432"              # Exposed on standard port
  environment:
    POSTGRES_DB: payflow       # Auto-creates this database on first start
    POSTGRES_USER: payflow
    POSTGRES_PASSWORD: payflow
  volumes:
    - pgdata:/var/lib/postgresql/data  # Data survives container restarts
```

**Why Alpine?** Same PostgreSQL, 5x smaller image. No downside for dev.

**The volume** (`pgdata`) means your data persists across `docker compose down` / `up`. Only `docker compose down -v` deletes it.

### Kafka (KRaft Mode)

```yaml
kafka:
  image: confluentinc/cp-kafka:7.6.0
  ports:
    - "9092:9092"              # Your app connects here
```

**KRaft mode** = no Zookeeper. Kafka 3.3+ can manage its own metadata. One less container, simpler setup.

Key environment variables explained:

| Variable | Value | Why |
|---|---|---|
| `KAFKA_PROCESS_ROLES` | `broker,controller` | Single node acts as both |
| `KAFKA_LISTENERS` | 3 listeners | Internal, controller, and external (your app) |
| `KAFKA_ADVERTISED_LISTENERS` | `kafka:29092`, `localhost:9092` | Internal uses container hostname, external uses localhost |
| `OFFSETS_TOPIC_REPLICATION_FACTOR` | `1` | Single broker, can't replicate. **Set to 3 in production.** |

**The two-listener trick**: Kafka needs different addresses for container-to-container (`kafka:29092`) vs host-to-container (`localhost:9092`) communication.

### Schema Registry

```yaml
schema-registry:
  image: confluentinc/cp-schema-registry:7.6.0
  ports:
    - "8081:8081"
  environment:
    SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS: kafka:29092  # Uses internal listener
  depends_on:
    kafka:
      condition: service_healthy  # Waits for Kafka to be ready
```

Stores Avro/JSON/Protobuf schemas in a Kafka topic (`_schemas`). Enforces compatibility rules so producers can't break consumers.

### Kafka UI

```yaml
kafka-ui:
  image: provectuslabs/kafka-ui:latest
  ports:
    - "8080:8080"
```

Open `http://localhost:8080` to:
- Browse topics and messages
- View consumer group lag
- Inspect schemas
- Create topics manually

This is optional but invaluable for learning. You can **see** messages flowing through topics in real time.

## Common Commands

```bash
# Create a topic manually
docker exec -it $(docker compose ps -q kafka) \
  kafka-topics --create --topic order-events \
  --partitions 3 --replication-factor 1 \
  --bootstrap-server localhost:9092

# Produce a test message
docker exec -it $(docker compose ps -q kafka) \
  kafka-console-producer --topic order-events \
  --bootstrap-server localhost:9092
# Type a message, press Enter, Ctrl+C to exit

# Consume messages
docker exec -it $(docker compose ps -q kafka) \
  kafka-console-consumer --topic order-events \
  --from-beginning --bootstrap-server localhost:9092

# Check consumer group lag
docker exec -it $(docker compose ps -q kafka) \
  kafka-consumer-groups --describe --group payment-service \
  --bootstrap-server localhost:9092

# Connect to PostgreSQL
docker exec -it $(docker compose ps -q postgres) psql -U payflow
```

## Troubleshooting

| Problem | Fix |
|---|---|
| Port 5432 already in use | Stop local PostgreSQL: `brew services stop postgresql` or change port to `5433:5432` |
| Port 9092 already in use | Stop local Kafka or change port to `9093:9092` (update `application.yml` too) |
| Kafka UI shows no brokers | Wait 30s, Kafka might still be starting. Check `docker compose logs kafka` |
| Schema Registry won't start | It needs Kafka healthy first. Run `docker compose up -d` again |

---

[← Quick Start](setup-00-overview.md) | [Next: Spring Boot Config →](setup-02-spring-boot.md)
