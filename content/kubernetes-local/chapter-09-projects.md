---
title: "Chapter 9: Projects - Full-Stack Deployments"
date: 2026-05-29
series: ["kubernetes-local"]
chapter: 9
---

# Chapter 9: Projects

[Previous: Observability](../chapter-08-observability) | [Back to Overview](../chapter-00-overview)

---

## Project 1: Full-Stack App (Spring Boot + PostgreSQL + Redis)

### Namespace

```bash
kubectl create namespace fullstack
kubectl config set-context --current --namespace=fullstack
```

### PostgreSQL

```yaml
# postgres.yaml
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
  namespace: fullstack
type: Opaque
data:
  POSTGRES_PASSWORD: cG9zdGdyZXMxMjM=
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: fullstack
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:16
          ports:
            - containerPort: 5432
          env:
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: POSTGRES_PASSWORD
            - name: POSTGRES_DB
              value: appdb
          volumeMounts:
            - name: pg-data
              mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
    - metadata:
        name: pg-data
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 1Gi
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: fullstack
spec:
  clusterIP: None
  selector:
    app: postgres
  ports:
    - port: 5432
```

### Redis

```yaml
# redis.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: fullstack
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
        - name: redis
          image: redis:7-alpine
          ports:
            - containerPort: 6379
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: fullstack
spec:
  selector:
    app: redis
  ports:
    - port: 6379
```

### Spring Boot App

```yaml
# app.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: spring-app
  namespace: fullstack
spec:
  replicas: 2
  selector:
    matchLabels:
      app: spring-app
  template:
    metadata:
      labels:
        app: spring-app
    spec:
      containers:
        - name: app
          image: eclipse-temurin:21-jre
          command: ["sh", "-c", "echo 'Replace with your Spring Boot jar'; sleep 3600"]
          ports:
            - containerPort: 8080
          env:
            - name: SPRING_DATASOURCE_URL
              value: "jdbc:postgresql://postgres:5432/appdb"
            - name: SPRING_DATASOURCE_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: POSTGRES_PASSWORD
            - name: SPRING_REDIS_HOST
              value: "redis"
          resources:
            requests:
              cpu: "200m"
              memory: "256Mi"
            limits:
              cpu: "500m"
              memory: "512Mi"
          readinessProbe:
            httpGet:
              path: /actuator/health
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: spring-app
  namespace: fullstack
spec:
  type: ClusterIP
  selector:
    app: spring-app
  ports:
    - port: 80
      targetPort: 8080
```

### Deploy everything

```bash
kubectl apply -f postgres.yaml
kubectl apply -f redis.yaml
kubectl apply -f app.yaml

kubectl get all -n fullstack
kubectl port-forward svc/spring-app 8080:80 -n fullstack
```

---

## Project 2: Blue-Green Deployment

Blue-green deploys two versions simultaneously and switches traffic instantly.

### Deploy "blue" version

```yaml
# blue.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: blue
  template:
    metadata:
      labels:
        app: myapp
        version: blue
    spec:
      containers:
        - name: app
          image: hashicorp/http-echo:0.2.3
          args: ["-text=BLUE version"]
          ports:
            - containerPort: 5678
```

### Service pointing to blue

```yaml
# service-bg.yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-service
spec:
  selector:
    app: myapp
    version: blue
  ports:
    - port: 80
      targetPort: 5678
```

```bash
kubectl apply -f blue.yaml
kubectl apply -f service-bg.yaml

# Verify blue is serving
kubectl run test --image=curlimages/curl --rm -it --restart=Never -- curl http://myapp-service
# Output: BLUE version
```

### Deploy "green" version

```yaml
# green.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: green
  template:
    metadata:
      labels:
        app: myapp
        version: green
    spec:
      containers:
        - name: app
          image: hashicorp/http-echo:0.2.3
          args: ["-text=GREEN version"]
          ports:
            - containerPort: 5678
```

```bash
kubectl apply -f green.yaml

# Both versions running, but service still points to blue
kubectl get pods -l app=myapp
```

### Switch traffic to green

```bash
kubectl patch svc myapp-service -p '{"spec":{"selector":{"version":"green"}}}'

# Verify
kubectl run test2 --image=curlimages/curl --rm -it --restart=Never -- curl http://myapp-service
# Output: GREEN version
```

### Rollback to blue

```bash
kubectl patch svc myapp-service -p '{"spec":{"selector":{"version":"blue"}}}'
```

### Clean up old version

```bash
kubectl delete deployment app-blue
```

---

## Project 3: Canary Release

Canary sends a small percentage of traffic to the new version.

### Stable deployment (90% traffic)

```yaml
# stable.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-stable
spec:
  replicas: 9
  selector:
    matchLabels:
      app: webapp
      track: stable
  template:
    metadata:
      labels:
        app: webapp
        track: stable
    spec:
      containers:
        - name: app
          image: hashicorp/http-echo:0.2.3
          args: ["-text=STABLE"]
          ports:
            - containerPort: 5678
```

### Canary deployment (10% traffic)

```yaml
# canary.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-canary
spec:
  replicas: 1
  selector:
    matchLabels:
      app: webapp
      track: canary
  template:
    metadata:
      labels:
        app: webapp
        track: canary
    spec:
      containers:
        - name: app
          image: hashicorp/http-echo:0.2.3
          args: ["-text=CANARY"]
          ports:
            - containerPort: 5678
```

### Service selects both (by shared label)

```yaml
# service-canary.yaml
apiVersion: v1
kind: Service
metadata:
  name: webapp-service
spec:
  selector:
    app: webapp
  ports:
    - port: 80
      targetPort: 5678
```

```bash
kubectl apply -f stable.yaml
kubectl apply -f canary.yaml
kubectl apply -f service-canary.yaml

# Test multiple times — roughly 1 in 10 requests hits canary
for i in $(seq 1 20); do
  kubectl run "curl-$i" --image=curlimages/curl --rm -it --restart=Never -- curl -s http://webapp-service
done
```

### Promote canary

```bash
# Scale canary up, stable down
kubectl scale deployment app-canary --replicas=10
kubectl scale deployment app-stable --replicas=0
kubectl delete deployment app-stable
```

---

## Project 4: Local Dev Workflow with Skaffold

Skaffold automates build-deploy-test cycles for local Kubernetes development.

### Install Skaffold

```bash
# macOS
brew install skaffold

# Linux
curl -Lo skaffold https://storage.googleapis.com/skaffold/releases/latest/skaffold-linux-amd64
sudo install skaffold /usr/local/bin/

# Windows
choco install skaffold
```

### Project structure

```
my-app/
  Dockerfile
  k8s/
    deployment.yaml
    service.yaml
  skaffold.yaml
  src/
    ...
```

### skaffold.yaml

```yaml
apiVersion: skaffold/v4beta6
kind: Config
metadata:
  name: my-app
build:
  artifacts:
    - image: my-app
      docker:
        dockerfile: Dockerfile
deploy:
  kubectl:
    manifests:
      - k8s/*.yaml
```

### Development loop

```bash
# Watches for changes, rebuilds, redeploys automatically
skaffold dev

# One-time build and deploy
skaffold run

# Clean up
skaffold delete
```

Skaffold detects file changes, rebuilds the container, and redeploys — all in seconds.

---

## Alternative: Tilt

Tilt is another local dev tool with a web UI.

### Install

```bash
# macOS
brew install tilt-dev/tap/tilt

# Linux
curl -fsSL https://raw.githubusercontent.com/tilt-dev/tilt/master/scripts/install.sh | bash
```

### Tiltfile

Create a `Tiltfile` in your project root:

```python
docker_build('my-app', '.')
k8s_yaml(['k8s/deployment.yaml', 'k8s/service.yaml'])
k8s_resource('my-app', port_forwards=8080)
```

```bash
tilt up
```

Open the Tilt UI at http://localhost:10350 to see build status, logs, and resource health.

---

## Cleaning Up All Projects

```bash
kubectl delete namespace fullstack
kubectl delete deployment app-blue app-green app-stable app-canary
kubectl delete svc myapp-service webapp-service
```

---

## Summary

- Full-stack apps: combine StatefulSets, Deployments, Services, and Secrets
- Blue-green: instant traffic switch by changing Service selector
- Canary: gradual rollout using replica ratios
- Skaffold/Tilt: fast local dev loops with automatic rebuild and redeploy

---

[Previous: Observability](../chapter-08-observability) | [Back to Overview](../chapter-00-overview)
