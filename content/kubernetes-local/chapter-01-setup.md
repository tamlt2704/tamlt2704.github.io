---
title: "Chapter 1: Setup - Your First Local Cluster"
date: 2026-05-29
series: ["kubernetes-local"]
chapter: 1
---

# Chapter 1: Setup - Your First Local Cluster

[Previous: Overview](../chapter-00-overview) | [Next: Pods](../chapter-02-pods)

---

## Choose Your Local Kubernetes Tool

You only need ONE of these. Pick whichever suits your setup.

| Tool               | Best For                       | Requirements             |
| ------------------ | ------------------------------ | ------------------------ |
| minikube           | Learning, most features        | Docker or VM driver      |
| kind               | Fast, lightweight, CI-friendly | Docker only              |
| Docker Desktop K8s | Already using Docker Desktop   | Docker Desktop installed |

---

## Option A: minikube

### Install minikube

**Windows (winget):**

```powershell
winget install Kubernetes.minikube
```

**macOS (Homebrew):**

```bash
brew install minikube
```

**Linux:**

```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

### Start your cluster

```bash
minikube start
```

This creates a single-node cluster. Verify:

```bash
minikube status
```

### Enable the dashboard

```bash
minikube dashboard
```

This opens the Kubernetes Dashboard in your browser.

---

## Option B: kind (Kubernetes in Docker)

### Install kind

**Windows (winget):**

```powershell
winget install Kubernetes.kind
```

**macOS (Homebrew):**

```bash
brew install kind
```

**Linux:**

```bash
curl -Lo ./kind https://kind.sigs.k8s.io/dl/latest/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
```

### Create a cluster

```bash
kind create cluster --name local-lab
```

Verify:

```bash
kind get clusters
```

---

## Option C: Docker Desktop Kubernetes

1. Open Docker Desktop Settings
2. Go to **Kubernetes** tab
3. Check **Enable Kubernetes**
4. Click **Apply and Restart**
5. Wait for the green indicator showing Kubernetes is running

---

## Install kubectl

kubectl is the CLI for interacting with any Kubernetes cluster.

**Windows (winget):**

```powershell
winget install Kubernetes.kubectl
```

**macOS (Homebrew):**

```bash
brew install kubectl
```

**Linux:**

```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install kubectl /usr/local/bin/kubectl
```

### Verify kubectl connects to your cluster

```bash
kubectl cluster-info
kubectl get nodes
```

You should see one node in `Ready` state.

---

## kubectl Basics

```bash
# List all resources in default namespace
kubectl get all

# Get detailed info about a node
kubectl describe node <node-name>

# Check which context (cluster) you are using
kubectl config current-context

# List all contexts
kubectl config get-contexts

# Switch context (if you have multiple clusters)
kubectl config use-context <context-name>
```

---

## Namespaces

Namespaces isolate resources within a cluster.

```bash
# List namespaces
kubectl get namespaces

# Create a namespace for this course
kubectl create namespace k8s-lab

# Set as default namespace
kubectl config set-context --current --namespace=k8s-lab
```

---

## Quick Smoke Test

Deploy nginx to confirm everything works:

```bash
kubectl run smoke-test --image=nginx --port=80
kubectl get pods
kubectl port-forward pod/smoke-test 8080:80
```

Open http://localhost:8080 in your browser. You should see the nginx welcome page.

Clean up:

```bash
kubectl delete pod smoke-test
```

---

## Summary

- You have a running local Kubernetes cluster
- kubectl is installed and connected
- You can deploy and access a container

---

[Previous: Overview](../chapter-00-overview) | [Next: Pods](../chapter-02-pods)
