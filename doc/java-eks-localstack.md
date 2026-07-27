# Java on EKS + LocalStack for Local Development

---

## What We're Building

```
LOCAL (your laptop):
  Docker Desktop → LocalStack (fake AWS) + Minikube/Kind (local K8s)
  Your Java app talks to "AWS" locally — no cloud costs, no internet needed

PRODUCTION (AWS):
  EKS (real Kubernetes) + real AWS services
  Same code, same config — just different endpoints
```

---

## Why This Setup?

| Problem | Solution |
|---------|----------|
| AWS costs money to develop against | LocalStack = free local AWS |
| EKS is expensive to run 24/7 for dev | Kind/Minikube = free local Kubernetes |
| "Works on my machine" → breaks in cloud | Same Docker images, same K8s manifests everywhere |
| Slow feedback loop (push → wait → test) | Run everything locally, iterate in seconds |

---

## Step 1: Install Local Tools

```bash
# Docker Desktop (required for everything)
# Download from https://docker.com/products/docker-desktop

# LocalStack (fake AWS services)
pip install localstack
# or
brew install localstack/tap/localstack-cli

# Kind (local Kubernetes cluster — lightweight)
# Alternatives: Minikube, k3d
brew install kind
# or download from https://kind.sigs.k8s.io

# kubectl (talk to Kubernetes)
brew install kubectl

# AWS CLI (talk to LocalStack same way you talk to real AWS)
brew install awscli

# Helm (Kubernetes package manager)
brew install helm
```

**On Windows (without brew):**

```powershell
# Docker Desktop — install from docker.com
# Kind
choco install kind
# kubectl
choco install kubernetes-cli
# AWS CLI
choco install awscli
# Helm
choco install kubernetes-helm
# LocalStack
pip install localstack
```

---

## Step 2: Start LocalStack

Create `docker-compose.yml` in your project root:

```yaml
version: "3.8"

services:
  localstack:
    image: localstack/localstack:latest
    ports:
      - "4566:4566"           # All AWS services on one port
      - "4510-4559:4510-4559" # External service ports
    environment:
      - SERVICES=s3,sqs,sns,secretsmanager,dynamodb,ecr
      - DEBUG=0
      - DOCKER_HOST=unix:///var/run/docker.sock
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock"
      - "./localstack-init:/etc/localstack/init/ready.d"  # init scripts
```

Start it:

```bash
docker compose up -d localstack
```

### Configure AWS CLI to point at LocalStack

Create `~/.aws/config` profile:

```ini
[profile localstack]
region = eu-west-1
output = json
endpoint_url = http://localhost:4566
```

Create `~/.aws/credentials`:

```ini
[localstack]
aws_access_key_id = test
aws_secret_access_key = test
```

Now use it:

```bash
# Create an S3 bucket on LocalStack
aws --profile localstack s3 mb s3://my-bucket

# Create an SQS queue
aws --profile localstack sqs create-queue --queue-name order-events

# Create a DynamoDB table
aws --profile localstack dynamodb create-table \
  --table-name GameScores \
  --attribute-definitions AttributeName=playerId,AttributeType=S AttributeName=gameId,AttributeType=S \
  --key-schema AttributeName=playerId,KeyType=HASH AttributeName=gameId,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST
```

### Init Scripts (Auto-Create Resources on Start)

Create `localstack-init/setup.sh`:

```bash
#!/bin/bash
echo "Creating LocalStack resources..."

awslocal s3 mb s3://my-app-uploads
awslocal sqs create-queue --queue-name order-events
awslocal sqs create-queue --queue-name notification-events
awslocal secretsmanager create-secret --name prod/db/password --secret-string "localdev123"

echo "LocalStack ready!"
```

`awslocal` = AWS CLI preconfigured for LocalStack. Resources recreate every time you restart.

---

## Step 3: Java App — Switching Between Local and AWS

### Spring Boot Profile Approach

`application.yml` (common):

```yaml
spring:
  application:
    name: my-service

server:
  port: 8080
```

`application-local.yml` (LocalStack):

```yaml
spring:
  cloud:
    aws:
      region:
        static: eu-west-1
      credentials:
        access-key: test
        secret-key: test
      endpoint: http://localhost:4566

  datasource:
    url: jdbc:postgresql://localhost:5432/mydb
    username: postgres
    password: <your-password>
```

`application-prod.yml` (real AWS):

```yaml
spring:
  cloud:
    aws:
      region:
        static: eu-west-1
      # No endpoint — uses real AWS
      # No credentials — uses IAM role from EKS pod

  datasource:
    url: ${DB_URL}
    username: ${DB_USER}
    password: ${DB_PASS}
```

Run locally:

```bash
mvn spring-boot:run -Dspring-boot.run.profiles=local
```

Run in AWS:

```bash
# SPRING_PROFILES_ACTIVE=prod set in K8s deployment
java -jar app.jar
```

### AWS SDK Client Configuration

```java
@Configuration
public class AwsConfig {

    @Bean
    @Profile("local")
    public S3Client localS3Client() {
        return S3Client.builder()
            .endpointOverride(URI.create("http://localhost:4566"))
            .region(Region.EU_WEST_1)
            .credentialsProvider(StaticCredentialsProvider.create(
                AwsBasicCredentials.create("test", "test")
            ))
            .forcePathStyle(true)  // Required for LocalStack S3
            .build();
    }

    @Bean
    @Profile("prod")
    public S3Client prodS3Client() {
        return S3Client.builder()
            .region(Region.EU_WEST_1)
            // Uses default credential chain (IAM role in EKS)
            .build();
    }
}
```

**Better — single bean with conditional endpoint:**

```java
@Configuration
public class AwsConfig {

    @Value("${aws.endpoint:}")
    private String endpoint;

    @Bean
    public S3Client s3Client() {
        var builder = S3Client.builder().region(Region.EU_WEST_1);

        if (!endpoint.isEmpty()) {
            builder.endpointOverride(URI.create(endpoint))
                   .credentialsProvider(StaticCredentialsProvider.create(
                       AwsBasicCredentials.create("test", "test")))
                   .forcePathStyle(true);
        }

        return builder.build();
    }
}
```

`application-local.yml`:
```yaml
aws:
  endpoint: http://localhost:4566
```

`application-prod.yml`: no `aws.endpoint` → uses real AWS.

---

## Step 4: Local Kubernetes with Kind

### Create a Cluster

```bash
kind create cluster --name my-app
```

This creates a single-node Kubernetes cluster inside Docker. Takes ~30 seconds.

### Verify

```bash
kubectl cluster-info --context kind-my-app
kubectl get nodes
```

### Load Your Docker Image into Kind

Kind runs inside Docker, so it can't pull from your local Docker directly. Load it:

```bash
# Build your image
docker build -t my-app:latest .

# Load into Kind cluster
kind load docker-image my-app:latest --name my-app
```

---

## Step 5: Kubernetes Manifests

### Namespace

`k8s/namespace.yml`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: my-app
```

### Deployment

`k8s/deployment.yml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  namespace: my-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
        - name: my-app
          image: my-app:latest
          imagePullPolicy: IfNotPresent  # Use local image in Kind
          ports:
            - containerPort: 8080
          env:
            - name: SPRING_PROFILES_ACTIVE
              value: "local"  # or "prod" in real EKS
            - name: DB_URL
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: url
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "1Gi"
              cpu: "500m"
          readinessProbe:
            httpGet:
              path: /actuator/health
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /actuator/health
              port: 8080
            initialDelaySeconds: 60
            periodSeconds: 30
```

### Service

`k8s/service.yml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app
  namespace: my-app
spec:
  selector:
    app: my-app
  ports:
    - port: 80
      targetPort: 8080
  type: ClusterIP
```

### Ingress (Route Traffic In)

`k8s/ingress.yml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app
  namespace: my-app
spec:
  rules:
    - host: my-app.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: my-app
                port:
                  number: 80
```

### Deploy Everything

```bash
kubectl apply -f k8s/namespace.yml
kubectl apply -f k8s/deployment.yml
kubectl apply -f k8s/service.yml

# Port-forward to access locally
kubectl port-forward -n my-app svc/my-app 8080:80
```

Now `http://localhost:8080` hits your app running in Kubernetes.

---

## Step 6: Connect Kind to LocalStack

Your app in Kind needs to reach LocalStack running in Docker. Since Kind runs inside Docker too, use Docker networking:

```bash
# Connect Kind to the same network as LocalStack
docker network connect kind localstack
```

Now from inside Kind pods, LocalStack is reachable at `http://localstack:4566`.

Update `application-local.yml`:

```yaml
# When running INSIDE Kind (pod)
aws:
  endpoint: http://localstack:4566

# When running OUTSIDE Kind (mvn spring-boot:run)
# aws:
#   endpoint: http://localhost:4566
```

**Or use an environment variable:**

```yaml
aws:
  endpoint: ${AWS_ENDPOINT:http://localhost:4566}
```

In the K8s deployment:

```yaml
env:
  - name: AWS_ENDPOINT
    value: "http://localstack:4566"
```

---

## Step 7: Full Local docker-compose

Run everything together — database, LocalStack, and your app (before moving to Kind):

```yaml
version: "3.8"

services:
  localstack:
    image: localstack/localstack:latest
    ports:
      - "4566:4566"
    environment:
      - SERVICES=s3,sqs,sns,secretsmanager,dynamodb
    volumes:
      - "./localstack-init:/etc/localstack/init/ready.d"

  postgres:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: <your-password>
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      SPRING_PROFILES_ACTIVE: local
      AWS_ENDPOINT: http://localstack:4566
      DB_URL: jdbc:postgresql://postgres:5432/mydb
      DB_USER: postgres
      DB_PASS: postgres
      REDIS_HOST: redis
    depends_on:
      - localstack
      - postgres
      - redis

volumes:
  pgdata:
```

```bash
docker compose up -d
```

Your entire backend runs locally. No cloud, no costs, fast iteration.

---

## Step 8: Production — Real EKS

### EKS Cluster Setup (one-time)

```bash
# Create cluster (takes ~15 minutes)
eksctl create cluster \
  --name my-app-cluster \
  --region eu-west-1 \
  --nodes 3 \
  --node-type t3.medium \
  --managed

# Configure kubectl to use EKS
aws eks update-kubeconfig --name my-app-cluster --region eu-west-1
```

### Key Differences from Local

| Local (Kind) | Production (EKS) |
|-------------|-----------------|
| `imagePullPolicy: IfNotPresent` | `imagePullPolicy: Always` |
| Image loaded with `kind load` | Image pulled from ECR |
| `SPRING_PROFILES_ACTIVE: local` | `SPRING_PROFILES_ACTIVE: prod` |
| LocalStack endpoint | No endpoint (real AWS) |
| No IAM | Service account with IAM role |
| No TLS | ACM certificate + ALB |
| `type: ClusterIP` + port-forward | ALB Ingress Controller |

### IAM Roles for Service Accounts (IRSA)

Instead of access keys, EKS pods assume IAM roles:

```yaml
# k8s/service-account.yml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app
  namespace: my-app
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789:role/my-app-role
```

The pod automatically gets temporary credentials — no secrets to manage.

### Push to ECR (Container Registry)

```bash
# Create repository
aws ecr create-repository --repository-name my-app

# Login
aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.eu-west-1.amazonaws.com

# Tag and push
docker tag my-app:latest 123456789.dkr.ecr.eu-west-1.amazonaws.com/my-app:v1.0.0
docker push 123456789.dkr.ecr.eu-west-1.amazonaws.com/my-app:v1.0.0
```

Update deployment to use ECR image:

```yaml
image: 123456789.dkr.ecr.eu-west-1.amazonaws.com/my-app:v1.0.0
```

---

## Step 9: Helm Chart (Package Your K8s Manifests)

Instead of raw YAML files, use Helm for templating:

```
helm/my-app/
├── Chart.yaml
├── values.yaml          ← defaults
├── values-local.yaml    ← local overrides
├── values-prod.yaml     ← production overrides
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    ├── ingress.yaml
    └── serviceaccount.yaml
```

`values.yaml`:

```yaml
replicaCount: 2
image:
  repository: my-app
  tag: latest
  pullPolicy: IfNotPresent
profile: local
aws:
  endpoint: "http://localstack:4566"
resources:
  requests:
    memory: 512Mi
    cpu: 250m
  limits:
    memory: 1Gi
    cpu: 500m
```

`values-prod.yaml`:

```yaml
replicaCount: 3
image:
  repository: 123456789.dkr.ecr.eu-west-1.amazonaws.com/my-app
  tag: v1.0.0
  pullPolicy: Always
profile: prod
aws:
  endpoint: ""
resources:
  requests:
    memory: 1Gi
    cpu: 500m
  limits:
    memory: 2Gi
    cpu: 1000m
```

Deploy:

```bash
# Local
helm install my-app ./helm/my-app -f helm/my-app/values-local.yaml -n my-app

# Production
helm install my-app ./helm/my-app -f helm/my-app/values-prod.yaml -n my-app
```

---

## Project Structure

```
my-java-app/
├── src/
│   └── main/
│       ├── java/com/myapp/
│       │   ├── Application.java
│       │   ├── config/
│       │   │   └── AwsConfig.java
│       │   ├── controller/
│       │   ├── service/
│       │   └── repository/
│       └── resources/
│           ├── application.yml
│           ├── application-local.yml
│           └── application-prod.yml
├── k8s/                          ← Raw manifests (simple projects)
│   ├── namespace.yml
│   ├── deployment.yml
│   └── service.yml
├── helm/                         ← Helm chart (complex projects)
│   └── my-app/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
├── localstack-init/
│   └── setup.sh                  ← Auto-create AWS resources
├── docker-compose.yml            ← Local dev environment
├── Dockerfile
├── pom.xml
└── Makefile                      ← Convenience commands
```

---

## Step 10: Makefile (Convenience Commands)

```makefile
.PHONY: local-up local-down build deploy-local deploy-prod

# Start local infrastructure
local-up:
	docker compose up -d
	kind create cluster --name my-app || true
	docker network connect kind localstack || true

# Stop everything
local-down:
	docker compose down
	kind delete cluster --name my-app

# Build Java app + Docker image
build:
	mvn clean package -DskipTests
	docker build -t my-app:latest .

# Deploy to local Kind
deploy-local: build
	kind load docker-image my-app:latest --name my-app
	kubectl apply -f k8s/ -n my-app

# Deploy to EKS
deploy-prod:
	mvn clean package
	docker build -t 123456789.dkr.ecr.eu-west-1.amazonaws.com/my-app:$(TAG) .
	docker push 123456789.dkr.ecr.eu-west-1.amazonaws.com/my-app:$(TAG)
	kubectl set image deployment/my-app my-app=123456789.dkr.ecr.eu-west-1.amazonaws.com/my-app:$(TAG) -n my-app

# Logs
logs:
	kubectl logs -f -l app=my-app -n my-app

# Port forward
forward:
	kubectl port-forward -n my-app svc/my-app 8080:80
```

Usage:

```bash
make local-up       # start everything
make deploy-local   # build and deploy to Kind
make forward        # access at localhost:8080
make logs           # tail logs
make local-down     # tear down
```

---

## The Development Loop

```
1. Write code (Java + Spring Boot)
2. `make deploy-local` (builds JAR → Docker → loads into Kind)
3. `make forward` (access at localhost:8080)
4. Test against LocalStack (S3, SQS, DynamoDB all work locally)
5. Iterate fast — no cloud deployments during development
6. When ready → `make deploy-prod` (same image, real AWS)
```

---

## Cheat Sheet

| Task | Command |
|------|---------|
| Start LocalStack | `docker compose up -d localstack` |
| Create Kind cluster | `kind create cluster --name my-app` |
| Build + load image | `docker build -t my-app . && kind load docker-image my-app --name my-app` |
| Deploy to Kind | `kubectl apply -f k8s/ -n my-app` |
| Access app | `kubectl port-forward -n my-app svc/my-app 8080:80` |
| See pods | `kubectl get pods -n my-app` |
| See logs | `kubectl logs -f -l app=my-app -n my-app` |
| Shell into pod | `kubectl exec -it <pod-name> -n my-app -- sh` |
| Talk to LocalStack S3 | `aws --endpoint-url=http://localhost:4566 s3 ls` |
| Restart deployment | `kubectl rollout restart deployment/my-app -n my-app` |

---

## Resources

| Resource | What | Free? |
|----------|------|-------|
| [LocalStack docs](https://docs.localstack.cloud) | All supported services, configuration | ✅ |
| [Kind docs](https://kind.sigs.k8s.io) | Local K8s cluster | ✅ |
| [EKS Best Practices](https://aws.github.io/aws-eks-best-practices/) | Production EKS guide | ✅ |
| [Spring Cloud AWS](https://docs.awspring.io) | Spring + AWS integration | ✅ |
| [eksctl docs](https://eksctl.io) | CLI for creating EKS clusters | ✅ |
| [Helm docs](https://helm.sh/docs/) | K8s package manager | ✅ |
