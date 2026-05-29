---
title: "Chapter 4: Services and Networking"
date: 2026-05-29
series: ["kubernetes-local"]
chapter: 4
---

# Chapter 4: Services and Networking

[Previous: Deployments](../chapter-03-deployments) | [Next: Configuration](../chapter-05-config)

---

## Why Services?

Pods are ephemeral — they get new IPs when recreated. A Service provides a stable endpoint to reach a set of Pods.

---

## Setup: Deploy an App

```yaml
# app-deploy.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: web
          image: hashicorp/http-echo:0.2.3
          args:
            - "-text=Hello from Kubernetes"
          ports:
            - containerPort: 5678
```

```bash
kubectl apply -f app-deploy.yaml
```

---

## ClusterIP (Default)

Accessible only within the cluster.

```yaml
# service-clusterip.yaml
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  type: ClusterIP
  selector:
    app: web
  ports:
    - port: 80
      targetPort: 5678
```

```bash
kubectl apply -f service-clusterip.yaml
kubectl get svc web-service
```

Test from inside the cluster:

```bash
kubectl run curl-test --image=curlimages/curl --rm -it --restart=Never -- curl http://web-service:80
```

---

## NodePort

Exposes the service on a port on every node.

```yaml
# service-nodeport.yaml
apiVersion: v1
kind: Service
metadata:
  name: web-nodeport
spec:
  type: NodePort
  selector:
    app: web
  ports:
    - port: 80
      targetPort: 5678
      nodePort: 30080
```

```bash
kubectl apply -f service-nodeport.yaml

# minikube
minikube service web-nodeport --url

# Docker Desktop — http://localhost:30080
```

---

## LoadBalancer (with minikube tunnel)

```yaml
# service-lb.yaml
apiVersion: v1
kind: Service
metadata:
  name: web-lb
spec:
  type: LoadBalancer
  selector:
    app: web
  ports:
    - port: 80
      targetPort: 5678
```

```bash
kubectl apply -f service-lb.yaml
```

On minikube, LoadBalancer stays in "Pending" until you run:

```bash
minikube tunnel
```

Keep this running in a separate terminal. Then:

```bash
kubectl get svc web-lb
# EXTERNAL-IP will now show an IP you can curl
```

---

## DNS Within the Cluster

Kubernetes runs CoreDNS. Every Service gets a DNS name:

```
<service-name>.<namespace>.svc.cluster.local
```

Test it:

```bash
kubectl run dns-test --image=busybox --rm -it --restart=Never -- nslookup web-service
```

Cross-namespace access:

```
http://web-service.other-namespace.svc.cluster.local
```

---

## Ingress with nginx-ingress

Ingress provides HTTP routing (host-based, path-based) to Services.

### Install nginx-ingress controller

**minikube:**

```bash
minikube addons enable ingress
```

**kind** — create cluster with port mappings first:

```yaml
# kind-config.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
    kubeadmConfigPatches:
      - |
        kind: InitConfiguration
        nodeRegistration:
          kubeletExtraArgs:
            node-labels: "ingress-ready=true"
    extraPortMappings:
      - containerPort: 80
        hostPort: 80
      - containerPort: 443
        hostPort: 443
```

```bash
kind delete cluster --name local-lab
kind create cluster --name local-lab --config kind-config.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
```

Wait for readiness:

```bash
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s
```

### Create an Ingress resource

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-ingress
spec:
  rules:
    - host: myapp.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: web-service
                port:
                  number: 80
```

```bash
kubectl apply -f ingress.yaml
```

Add to your hosts file (`C:\Windows\System32\drivers\etc\hosts` on Windows, `/etc/hosts` on Linux/Mac):

```
127.0.0.1 myapp.local
```

Now `curl http://myapp.local` returns "Hello from Kubernetes".

---

## Cleaning Up

```bash
kubectl delete ingress web-ingress
kubectl delete svc web-service web-nodeport web-lb
kubectl delete deployment web-app
```

---

## Summary

- **ClusterIP**: internal only, default type
- **NodePort**: exposes on node IP + port
- **LoadBalancer**: external IP (use `minikube tunnel` locally)
- **Ingress**: HTTP routing with host/path rules
- Kubernetes DNS lets services find each other by name

---

[Previous: Deployments](../chapter-03-deployments) | [Next: Configuration](../chapter-05-config)
