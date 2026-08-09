# Chapter 32: Kubernetes — Container Orchestration at Scale

## What you'll learn

- Kubernetes architecture: control plane, nodes, kubelet
- Core objects: Pods, Deployments, Services, Ingress
- Declarative configuration with YAML manifests
- Scaling, rolling updates, and rollbacks
- ConfigMaps, Secrets, and environment configuration
- Persistent storage with PersistentVolumes
- Networking: service discovery, DNS, load balancing
- Helm charts for packaging applications
- Monitoring and debugging: kubectl, logs, events
- Build: deploy the full stack (Next.js + Spring Boot + PostgreSQL) to Kubernetes

---

## PART 1: Architecture

## 32.1 What Kubernetes solves

Docker runs containers on ONE machine. Kubernetes runs containers across MANY machines and handles:

| Problem | Kubernetes solution |
|---------|-------------------|
| "Server crashed" | Automatic restart + reschedule to healthy node |
| "Need more capacity" | Horizontal auto-scaling (add pods) |
| "Deploy without downtime" | Rolling updates (replace pods one by one) |
| "Bad deploy, roll back" | Rollback to previous version in seconds |
| "Services need to find each other" | Built-in DNS + service discovery |
| "Load balance traffic" | Services + Ingress controllers |
| "Manage config across environments" | ConfigMaps + Secrets |
| "Persistent data" | PersistentVolumes (survive pod restarts) |

## 32.2 Cluster architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CONTROL PLANE                             │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐ │
│  │  API Server  │  │  Scheduler   │  │  Controller Manager    │ │
│  │  (kubectl    │  │  (assigns    │  │  (ensures desired      │ │
│  │   talks here)│  │   pods to    │  │   state = actual state)│ │
│  └──────────────┘  │   nodes)     │  └───────────────────────┘ │
│                     └──────────────┘                             │
│  ┌──────────────┐                                               │
│  │    etcd      │  ← Distributed key-value store (cluster state)│
│  └──────────────┘                                               │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
┌─────────────▼───┐ ┌────────▼────────┐ ┌────▼──────────────┐
│    NODE 1       │ │    NODE 2       │ │    NODE 3         │
│                 │ │                 │ │                   │
│ ┌─────────────┐ │ │ ┌─────────────┐ │ │ ┌─────────────┐  │
│ │   kubelet   │ │ │ │   kubelet   │ │ │ │   kubelet   │  │
│ │ (node agent)│ │ │ │ (node agent)│ │ │ │ (node agent)│  │
│ └─────────────┘ │ │ └─────────────┘ │ │ └─────────────┘  │
│                 │ │                 │ │                   │
│ ┌───┐ ┌───┐   │ │ ┌───┐ ┌───┐   │ │ ┌───┐ ┌───┐ ┌───┐│
│ │Pod│ │Pod│   │ │ │Pod│ │Pod│   │ │ │Pod│ │Pod│ │Pod││
│ └───┘ └───┘   │ │ └───┘ └───┘   │ │ └───┘ └───┘ └───┘│
└─────────────────┘ └─────────────────┘ └───────────────────┘
```

**Control Plane** — the brain:
- **API Server** — all communication goes through here (kubectl, controllers, nodes)
- **Scheduler** — decides WHICH node a new pod runs on (CPU/memory available?)
- **Controller Manager** — watches desired state vs actual state, takes corrective action
- **etcd** — stores ALL cluster state (the single source of truth)

**Nodes** — the workers:
- **kubelet** — agent on each node, manages pods assigned to that node
- **kube-proxy** — handles networking (routing traffic to the right pod)
- **Container runtime** — actually runs containers (containerd, CRI-O)

## 32.3 The declarative model

You tell Kubernetes WHAT you want (desired state). It figures out HOW to get there.

```yaml
# "I want 3 copies of my API running"
spec:
  replicas: 3
```

Kubernetes continuously reconciles:
```
Desired: 3 pods running
Actual:  2 pods running (one crashed)
Action:  Start 1 new pod → back to 3
```

You never say "start a pod" or "restart that container." You declare the end state, and controllers make it happen.

---

## PART 2: Core Objects

## 32.4 Pod — the smallest deployable unit

A Pod is one or more containers that share network and storage. Usually one container per pod.

```yaml
# pod.yaml — you rarely create pods directly (use Deployments instead)
apiVersion: v1
kind: Pod
metadata:
  name: my-api
  labels:
    app: task-api
spec:
  containers:
    - name: api
      image: myregistry/task-api:1.0.0
      ports:
        - containerPort: 8080
      env:
        - name: SPRING_PROFILES_ACTIVE
          value: "prod"
      resources:
        requests:
          memory: "256Mi"
          cpu: "250m"
        limits:
          memory: "512Mi"
          cpu: "500m"
```

**Resources explained:**
- `requests` — guaranteed minimum (scheduler uses this to place pods)
- `limits` — maximum allowed (container is killed if it exceeds memory limit)
- `250m` = 250 millicores = 0.25 CPU cores
- `256Mi` = 256 mebibytes

## 32.5 Deployment — manage pod replicas

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: task-api
  namespace: production
spec:
  replicas: 3                    # Run 3 copies
  selector:
    matchLabels:
      app: task-api              # Manages pods with this label
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1                # Max 1 extra pod during update
      maxUnavailable: 0          # Never have fewer than 3 running
  template:                      # Pod template
    metadata:
      labels:
        app: task-api
        version: "1.0.0"
    spec:
      containers:
        - name: api
          image: myregistry/task-api:1.0.0
          ports:
            - containerPort: 8080
          envFrom:
            - configMapRef:
                name: task-api-config
            - secretRef:
                name: task-api-secrets
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          readinessProbe:
            httpGet:
              path: /actuator/health
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /actuator/health/liveness
              port: 8080
            initialDelaySeconds: 60
            periodSeconds: 30
```

**Health probes:**
| Probe | Purpose | On failure |
|-------|---------|-----------|
| `readinessProbe` | "Can this pod handle traffic?" | Removed from Service (no traffic sent) |
| `livenessProbe` | "Is this pod alive?" | Container is restarted |
| `startupProbe` | "Is this pod still starting?" | Liveness/readiness checks disabled until pass |

## 32.6 Service — stable network endpoint

Pods are ephemeral (they get new IPs when restarted). A Service provides a stable DNS name and load-balances across matching pods.

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: task-api          # DNS: task-api.production.svc.cluster.local
  namespace: production
spec:
  selector:
    app: task-api          # Routes to pods with this label
  ports:
    - port: 80             # Service listens on port 80
      targetPort: 8080     # Routes to container port 8080
      protocol: TCP
  type: ClusterIP          # Internal only (default)
```

**Service types:**
| Type | Access | Use case |
|------|--------|----------|
| `ClusterIP` | Internal only | Service-to-service communication |
| `NodePort` | External via node IP:port | Development, testing |
| `LoadBalancer` | External via cloud LB (AWS ALB, GCP LB) | Production external access |

**Service discovery:** Any pod in the cluster can reach the API at `http://task-api.production.svc.cluster.local` (or just `task-api` within the same namespace).

## 32.7 Ingress — HTTP routing

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  namespace: production
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
    - hosts:
        - api.myapp.com
        - app.myapp.com
      secretName: app-tls-cert
  rules:
    - host: api.myapp.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: task-api
                port:
                  number: 80
    - host: app.myapp.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend
                port:
                  number: 80
```

Ingress is like nginx — routes external HTTP traffic to internal services based on hostname/path.

---

## PART 3: Configuration & Storage

## 32.8 ConfigMap — non-secret configuration

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: task-api-config
  namespace: production
data:
  SPRING_PROFILES_ACTIVE: "prod"
  SERVER_PORT: "8080"
  LOGGING_LEVEL_ROOT: "INFO"
  APP_FEATURE_FLAGS: |
    {
      "newDashboard": true,
      "betaExport": false
    }
```

**Use in pods:**
```yaml
# All keys as env vars
envFrom:
  - configMapRef:
      name: task-api-config

# Specific key
env:
  - name: LOG_LEVEL
    valueFrom:
      configMapKeyRef:
        name: task-api-config
        key: LOGGING_LEVEL_ROOT

# Mount as file
volumes:
  - name: config-vol
    configMap:
      name: task-api-config
volumeMounts:
  - name: config-vol
    mountPath: /app/config
```

## 32.9 Secrets — sensitive data

```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: task-api-secrets
  namespace: production
type: Opaque
data:
  DATABASE_URL: amRiYzpwb3N0Z3Jlc3FsOi8vZGI6NTQzMi90YXNrYXBp  # base64 encoded
  DATABASE_PASS: c3VwZXJzZWNyZXQ=                                  # base64 encoded
  JWT_SECRET: bXktMjU2LWJpdC1zZWNyZXQta2V5                        # base64 encoded
```

```bash
# Create secret from command line (auto-encodes)
kubectl create secret generic task-api-secrets \
  --from-literal=DATABASE_URL="jdbc:postgresql://db:5432/taskapi" \
  --from-literal=DATABASE_PASS="supersecret" \
  --from-literal=JWT_SECRET="my-256-bit-secret-key"
```

> **⚠️ Secrets are base64-encoded, NOT encrypted.** Anyone with cluster access can decode them. For real security, use:
> - AWS Secrets Manager + External Secrets Operator
> - HashiCorp Vault
> - Sealed Secrets (encrypted at rest in Git)

## 32.10 PersistentVolume — data that survives pod restarts

```yaml
# pvc.yaml — request storage
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-data
  namespace: production
spec:
  accessModes:
    - ReadWriteOnce      # One pod can write at a time
  resources:
    requests:
      storage: 20Gi
  storageClassName: gp3  # AWS EBS gp3 (or your cloud's storage class)
```

```yaml
# Use in a pod/deployment
spec:
  containers:
    - name: postgres
      image: postgres:16-alpine
      volumeMounts:
        - name: pgdata
          mountPath: /var/lib/postgresql/data
  volumes:
    - name: pgdata
      persistentVolumeClaim:
        claimName: postgres-data
```

---

## PART 4: Deploying the Full Stack

## 32.11 Complete manifests — Next.js + Spring Boot + PostgreSQL

**Namespace:**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: task-app
```

**PostgreSQL StatefulSet:**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: task-app
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
          image: postgres:16-alpine
          ports:
            - containerPort: 5432
          env:
            - name: POSTGRES_DB
              value: taskapi
            - name: POSTGRES_USER
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: username
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: password
          volumeMounts:
            - name: pgdata
              mountPath: /var/lib/postgresql/data
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
  volumeClaimTemplates:
    - metadata:
        name: pgdata
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 10Gi
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: task-app
spec:
  selector:
    app: postgres
  ports:
    - port: 5432
  clusterIP: None  # Headless service for StatefulSet
```

**Spring Boot API Deployment:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: task-api
  namespace: task-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: task-api
  template:
    metadata:
      labels:
        app: task-api
    spec:
      containers:
        - name: api
          image: myregistry/task-api:1.0.0
          ports:
            - containerPort: 8080
          env:
            - name: SPRING_PROFILES_ACTIVE
              value: "prod"
            - name: DATABASE_URL
              value: "jdbc:postgresql://postgres:5432/taskapi"
            - name: DATABASE_USER
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: username
            - name: DATABASE_PASS
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: password
          readinessProbe:
            httpGet:
              path: /actuator/health/readiness
              port: 8080
            initialDelaySeconds: 30
          livenessProbe:
            httpGet:
              path: /actuator/health/liveness
              port: 8080
            initialDelaySeconds: 60
          resources:
            requests:
              memory: "512Mi"
              cpu: "500m"
            limits:
              memory: "1Gi"
              cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: task-api
  namespace: task-app
spec:
  selector:
    app: task-api
  ports:
    - port: 80
      targetPort: 8080
```

**Next.js Frontend:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: task-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
        - name: frontend
          image: myregistry/task-frontend:1.0.0
          ports:
            - containerPort: 3000
          env:
            - name: NEXT_PUBLIC_API_URL
              value: "http://task-api"
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "256Mi"
              cpu: "250m"
---
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: task-app
spec:
  selector:
    app: frontend
  ports:
    - port: 80
      targetPort: 3000
```

## 32.12 HorizontalPodAutoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: task-api-hpa
  namespace: task-app
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: task-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70   # Scale up when avg CPU > 70%
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

---

## PART 5: Operations

## 32.13 Essential kubectl commands

```bash
# Context and cluster
kubectl config get-contexts           # list available clusters
kubectl config use-context prod       # switch cluster

# Get resources
kubectl get pods -n task-app          # list pods
kubectl get pods -o wide              # with node assignment + IP
kubectl get deploy,svc,ing -n task-app  # multiple resource types
kubectl get all -n task-app           # everything in namespace

# Describe (detailed info + events)
kubectl describe pod <pod-name> -n task-app
kubectl describe deploy task-api -n task-app

# Logs
kubectl logs <pod-name> -n task-app             # current logs
kubectl logs <pod-name> -f                       # follow (tail)
kubectl logs <pod-name> --previous              # logs from crashed container
kubectl logs -l app=task-api -n task-app        # all pods with label

# Shell into a pod
kubectl exec -it <pod-name> -n task-app -- sh

# Apply manifests
kubectl apply -f deployment.yaml                 # single file
kubectl apply -f k8s/                            # all files in directory
kubectl apply -f k8s/ --dry-run=client          # preview without applying

# Scaling
kubectl scale deploy task-api --replicas=5 -n task-app

# Rolling update
kubectl set image deploy/task-api api=myregistry/task-api:2.0.0 -n task-app

# Rollback
kubectl rollout undo deploy/task-api -n task-app
kubectl rollout history deploy/task-api -n task-app   # see revision history
kubectl rollout undo deploy/task-api --to-revision=3  # specific revision

# Delete
kubectl delete -f deployment.yaml
kubectl delete pod <pod-name> -n task-app        # pod restarts automatically (managed by Deployment)

# Port forward (access service locally)
kubectl port-forward svc/task-api 8080:80 -n task-app
# Now http://localhost:8080 reaches the service
```

## 32.14 Debugging failing pods

```bash
# Step 1: Check pod status
kubectl get pods -n task-app
# NAME                        READY   STATUS             RESTARTS   AGE
# task-api-7f8b9c4d5-x2k9l   0/1     CrashLoopBackOff   5          10m

# Step 2: Get events (why is it failing?)
kubectl describe pod task-api-7f8b9c4d5-x2k9l -n task-app
# Events:
#   Warning  BackOff  Container is crash-looping

# Step 3: Check logs (what error?)
kubectl logs task-api-7f8b9c4d5-x2k9l -n task-app --previous

# Step 4: Common causes:
# - CrashLoopBackOff → app crashes on startup (check logs for exception)
# - ImagePullBackOff → wrong image name or missing registry credentials
# - Pending → not enough resources (check node capacity)
# - OOMKilled → exceeded memory limit (increase limits)

# Step 5: Run debug pod in same namespace
kubectl run debug --rm -it --image=busybox -n task-app -- sh
# Can curl services, check DNS, test connectivity
```

## 32.15 Helm — package manager for Kubernetes

Helm packages Kubernetes manifests into reusable **charts** with configurable values.

```bash
# Install Helm
# (already available on most CI/CD systems)

# Add a chart repository
helm repo add bitnami https://charts.bitnami.com/bitnami

# Install PostgreSQL from a chart
helm install my-postgres bitnami/postgresql \
  --namespace task-app \
  --set auth.postgresPassword=secret \
  --set primary.persistence.size=20Gi

# Install your own app
helm install task-api ./helm/task-api \
  --namespace task-app \
  --values ./helm/task-api/values-prod.yaml
```

**Chart structure:**
```
helm/task-api/
├── Chart.yaml              # Chart metadata (name, version)
├── values.yaml             # Default configuration
├── values-prod.yaml        # Production overrides
└── templates/
    ├── deployment.yaml     # {{ .Values.replicas }}
    ├── service.yaml
    ├── ingress.yaml
    ├── configmap.yaml
    ├── secret.yaml
    └── hpa.yaml
```

```yaml
# values.yaml
replicaCount: 3
image:
  repository: myregistry/task-api
  tag: "1.0.0"
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"

# values-prod.yaml (overrides)
replicaCount: 5
image:
  tag: "2.1.0"
resources:
  requests:
    memory: "1Gi"
    cpu: "1000m"
```

---

## Summary

✅ Kubernetes architecture: control plane (API server, scheduler, controllers, etcd) + worker nodes (kubelet, pods)
✅ Core objects: Pod (container), Deployment (replicas + rolling updates), Service (stable endpoint + LB), Ingress (HTTP routing)
✅ Configuration: ConfigMaps (non-secret), Secrets (sensitive), environment variables
✅ Storage: PersistentVolumeClaims for data that survives pod restarts
✅ Full stack deployment: Next.js + Spring Boot + PostgreSQL with proper health probes
✅ Auto-scaling: HorizontalPodAutoscaler based on CPU/memory
✅ Operations: kubectl commands, debugging CrashLoopBackOff, rolling updates, rollbacks
✅ Helm: packaging manifests into configurable, reusable charts

## Key takeaways

**Kubernetes is declarative.** You say "I want 3 replicas, 512MB each, health-checked at /actuator/health" and Kubernetes makes it happen — now and forever. If a pod dies, it's recreated. If a node dies, pods are rescheduled.

**Deployments, not Pods.** Never create bare pods. Always use Deployments (or StatefulSets for databases). Deployments give you replicas, rolling updates, rollbacks, and self-healing.

**Services are the glue.** Pods come and go (new IPs every time). Services provide a stable DNS name (`task-api.task-app.svc.cluster.local`) that always routes to healthy pods. This is how services discover each other.

**Start simple.** You don't need Helm, Istio, ArgoCD, or Prometheus on day one. Start with: Deployment + Service + Ingress + ConfigMap + Secret. Add complexity when you need it.

---

→ [Back to Chapter 31: Three.js in Next.js](./31-THREEJS-NEXTJS.md)
