---
title: "Chapter 2: Pods - The Smallest Deployable Unit"
date: 2026-05-29
series: ["kubernetes-local"]
chapter: 2
---

# Chapter 2: Pods

[Previous: Setup](../chapter-01-setup) | [Next: Deployments](../chapter-03-deployments)

---

## What is a Pod?

A Pod is the smallest deployable unit in Kubernetes. It wraps one or more containers that share:

- The same network namespace (localhost communication)
- The same storage volumes
- The same lifecycle (start together, stop together)

Most Pods run a single container. Multi-container Pods are used for sidecars, adapters, or ambassadors.

---

## Creating a Pod with kubectl run

The quickest way to create a Pod:

```bash
kubectl run my-nginx --image=nginx:1.25 --port=80
```

Check the Pod:

```bash
kubectl get pods
kubectl get pod my-nginx -o wide
```

---

## Pod YAML Manifest

Create a file `pod-nginx.yaml`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  labels:
    app: nginx
spec:
  containers:
    - name: nginx
      image: nginx:1.25
      ports:
        - containerPort: 80
```

Apply it:

```bash
kubectl apply -f pod-nginx.yaml
```

---

## Inspecting Pods

```bash
# Detailed info including events
kubectl describe pod nginx-pod

# Pod logs
kubectl logs nginx-pod

# Follow logs in real time
kubectl logs nginx-pod -f

# Get YAML representation of running pod
kubectl get pod nginx-pod -o yaml
```

---

## Executing Commands Inside a Pod

```bash
# Open a shell
kubectl exec -it nginx-pod -- /bin/bash

# Run a single command
kubectl exec nginx-pod -- cat /etc/nginx/nginx.conf

# Check networking from inside
kubectl exec nginx-pod -- curl -s localhost:80
```

---

## Port Forwarding

Access a Pod from your local machine without a Service:

```bash
kubectl port-forward pod/nginx-pod 8080:80
```

Open http://localhost:8080 — you will see the nginx welcome page.

Press Ctrl+C to stop port-forwarding.

---

## Pod Lifecycle and Restart Policies

Pods have phases: Pending, Running, Succeeded, Failed, Unknown.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: job-pod
spec:
  restartPolicy: Never
  containers:
    - name: worker
      image: busybox
      command: ["sh", "-c", "echo done && sleep 5"]
```

```bash
kubectl apply -f job-pod.yaml
kubectl get pod job-pod --watch
```

---

## Multi-Container Pod (Sidecar Pattern)

A common pattern: main app container + sidecar for logging, proxying, or syncing.

Create `sidecar-pod.yaml`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sidecar-demo
spec:
  containers:
    - name: app
      image: busybox
      command: ["sh", "-c", "while true; do date >> /var/log/app.log; sleep 5; done"]
      volumeMounts:
        - name: shared-logs
          mountPath: /var/log

    - name: log-reader
      image: busybox
      command: ["sh", "-c", "tail -f /var/log/app.log"]
      volumeMounts:
        - name: shared-logs
          mountPath: /var/log

  volumes:
    - name: shared-logs
      emptyDir: {}
```

```bash
kubectl apply -f sidecar-pod.yaml

# View logs from the sidecar container
kubectl logs sidecar-demo -c log-reader -f

# View logs from the app container
kubectl logs sidecar-demo -c app
```

Both containers share the `/var/log` volume. The app writes logs, the sidecar reads them.

---

## Cleaning Up

```bash
kubectl delete pod my-nginx nginx-pod job-pod sidecar-demo
```

---

## Summary

- Pods are the atomic unit of deployment
- Use `kubectl run` for quick Pods, YAML manifests for reproducibility
- `logs`, `exec`, `port-forward` are your debugging tools
- Multi-container Pods share network and volumes

---

[Previous: Setup](../chapter-01-setup) | [Next: Deployments](../chapter-03-deployments)
