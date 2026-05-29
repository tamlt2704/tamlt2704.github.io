---
title: "Chapter 8: Observability - Monitoring and Autoscaling"
date: 2026-05-29
series: ["kubernetes-local"]
chapter: 8
---

# Chapter 8: Observability

[Previous: Helm](../chapter-07-helm) | [Next: Projects](../chapter-09-projects)

---

## Resource Requests and Limits

Every container should declare resource requests and limits.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: resource-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: resource-app
  template:
    metadata:
      labels:
        app: resource-app
    spec:
      containers:
        - name: app
          image: nginx:1.25
          resources:
            requests:
              cpu: "100m"
              memory: "64Mi"
            limits:
              cpu: "250m"
              memory: "128Mi"
          ports:
            - containerPort: 80
```

- **requests**: scheduler uses this to place Pods on nodes
- **limits**: container gets killed (OOMKilled) or throttled if exceeded

```bash
kubectl apply -f resource-app.yaml
kubectl describe pod -l app=resource-app | grep -A 5 "Limits"
```

---

## Liveness and Readiness Probes

### Liveness Probe

Restarts the container if it fails.

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 80
  initialDelaySeconds: 5
  periodSeconds: 10
```

### Readiness Probe

Removes the Pod from Service endpoints if it fails (no traffic sent).

```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 80
  initialDelaySeconds: 3
  periodSeconds: 5
```

### Full example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: probed-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: probed
  template:
    metadata:
      labels:
        app: probed
    spec:
      containers:
        - name: app
          image: nginx:1.25
          ports:
            - containerPort: 80
          livenessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 5
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 3
            periodSeconds: 5
```

```bash
kubectl apply -f probed-app.yaml
kubectl describe pod -l app=probed | grep -A 3 "Liveness"
```

---

## kubectl top (Metrics Server)

### Install Metrics Server

**minikube:**

```bash
minikube addons enable metrics-server
```

**kind:**

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Patch for local clusters (no TLS verification)
kubectl patch deployment metrics-server -n kube-system \
  --type='json' \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'
```

Wait a minute for metrics to be collected, then:

```bash
kubectl top nodes
kubectl top pods
kubectl top pods -l app=resource-app
```

---

## Horizontal Pod Autoscaler (HPA)

HPA automatically scales Pods based on CPU/memory usage.

### Create an HPA

```bash
kubectl autoscale deployment resource-app --cpu-percent=50 --min=2 --max=10
```

Or as YAML:

```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: resource-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: resource-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 50
```

```bash
kubectl apply -f hpa.yaml
kubectl get hpa
```

### Generate load to trigger scaling

```bash
# Expose the deployment
kubectl expose deployment resource-app --port=80 --type=ClusterIP --name=resource-svc

# Generate load from inside the cluster
kubectl run load-gen --image=busybox --restart=Never -- /bin/sh -c "while true; do wget -q -O- http://resource-svc; done"

# Watch HPA react
kubectl get hpa --watch
kubectl get pods -l app=resource-app --watch
```

Stop the load:

```bash
kubectl delete pod load-gen
```

---

## Prometheus + Grafana Stack

### Install with Helm

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  --set prometheus.prometheusSpec.retention=24h
```

Wait for all pods to be ready:

```bash
kubectl get pods -n monitoring --watch
```

### Access Grafana

```bash
kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80
```

Open http://localhost:3000

- Username: `admin`
- Password: get it with:

```bash
kubectl get secret monitoring-grafana -n monitoring -o jsonpath="{.data.admin-password}" | base64 --decode
```

### Access Prometheus

```bash
kubectl port-forward svc/monitoring-kube-prometheus-prometheus -n monitoring 9090:9090
```

Open http://localhost:9090 and try queries:

```
container_cpu_usage_seconds_total
kube_pod_status_phase
```

### Pre-built dashboards

Grafana comes with dashboards for:

- Kubernetes cluster overview
- Node metrics
- Pod resource usage
- Namespace workloads

Navigate to Dashboards in the Grafana sidebar to explore them.

---

## Cleaning Up

```bash
kubectl delete hpa resource-app-hpa
kubectl delete deployment resource-app probed-app
kubectl delete svc resource-svc
helm uninstall monitoring -n monitoring
kubectl delete namespace monitoring
```

---

## Summary

- Set resource requests/limits on every container
- Liveness probes restart unhealthy containers
- Readiness probes remove unready Pods from traffic
- `kubectl top` shows real-time resource usage
- HPA scales Pods based on metrics
- Prometheus + Grafana gives full observability with minimal setup

---

[Previous: Helm](../chapter-07-helm) | [Next: Projects](../chapter-09-projects)
