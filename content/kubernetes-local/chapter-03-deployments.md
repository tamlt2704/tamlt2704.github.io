---
title: "Chapter 3: Deployments - Scaling and Updates"
date: 2026-05-29
series: ["kubernetes-local"]
chapter: 3
---

# Chapter 3: Deployments

[Previous: Pods](../chapter-02-pods) | [Next: Services](../chapter-04-services)

---

## Why Deployments?

You rarely create Pods directly. Deployments manage Pods for you:

- Maintain a desired number of replicas
- Rolling updates with zero downtime
- Rollback to previous versions
- Self-healing (recreates failed Pods)

---

## Creating a Deployment

Create `deployment-nginx.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deploy
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
        - name: nginx
          image: nginx:1.25
          ports:
            - containerPort: 80
```

```bash
kubectl apply -f deployment-nginx.yaml
kubectl get deployments
kubectl get pods -l app=nginx
```

You should see 3 Pods running.

---

## How Deployments Work: ReplicaSets

A Deployment creates a ReplicaSet, which creates Pods.

```
Deployment -> ReplicaSet -> Pod, Pod, Pod
```

```bash
kubectl get replicasets
```

You never manage ReplicaSets directly — the Deployment handles them.

---

## Scaling

### Imperative scaling

```bash
kubectl scale deployment nginx-deploy --replicas=5
kubectl get pods -l app=nginx
```

### Declarative scaling

Edit the YAML and change `replicas: 5`, then:

```bash
kubectl apply -f deployment-nginx.yaml
```

### Scale down

```bash
kubectl scale deployment nginx-deploy --replicas=2
```

---

## Rolling Updates

Update the image version to trigger a rolling update:

```bash
kubectl set image deployment/nginx-deploy nginx=nginx:1.26
```

Watch the rollout:

```bash
kubectl rollout status deployment/nginx-deploy
```

What happens during a rolling update:

1. New ReplicaSet is created with new image
2. New Pods are gradually added
3. Old Pods are gradually terminated
4. At no point are zero Pods available

---

## Rollback

View rollout history:

```bash
kubectl rollout history deployment/nginx-deploy
```

Roll back to the previous version:

```bash
kubectl rollout undo deployment/nginx-deploy
```

Roll back to a specific revision:

```bash
kubectl rollout undo deployment/nginx-deploy --to-revision=1
```

Verify:

```bash
kubectl describe deployment nginx-deploy | grep Image
```

---

## Deployment Strategy

### RollingUpdate (default)

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
```

- `maxSurge: 1` — at most 1 extra Pod during update
- `maxUnavailable: 0` — never have fewer than desired Pods

### Recreate

```yaml
spec:
  strategy:
    type: Recreate
```

All old Pods are killed before new ones start. Use when your app cannot run two versions simultaneously (e.g., database migrations).

---

## Full Example with Strategy

Create `deployment-strategy.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-deploy
spec:
  replicas: 4
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
        - name: app
          image: hashicorp/http-echo:0.2.3
          args:
            - "-text=version-1"
          ports:
            - containerPort: 5678
```

```bash
kubectl apply -f deployment-strategy.yaml

# Trigger update
kubectl set image deployment/app-deploy app=hashicorp/http-echo:latest

# Watch pods cycling
kubectl get pods -l app=myapp --watch
```

---

## Cleaning Up

```bash
kubectl delete deployment nginx-deploy app-deploy
```

---

## Summary

- Deployments manage Pods via ReplicaSets
- Scale with `kubectl scale` or by changing `replicas` in YAML
- Rolling updates give zero-downtime deployments
- Rollback instantly with `kubectl rollout undo`
- Choose RollingUpdate (default) or Recreate strategy

---

[Previous: Pods](../chapter-02-pods) | [Next: Services](../chapter-04-services)
