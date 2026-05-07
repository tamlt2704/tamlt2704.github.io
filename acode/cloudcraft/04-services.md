# Chapter 4: "Users Can't Reach It"

[← Deployments](03-deployments.md) | [Next: Passwords Are in the Code →](05-config-secrets.md)

---

Ava walks over:

> "I have 3 Pods. Which one do I call? What's the IP?"

You check:

```bash
kubectl get pods -o wide
```

```
NAME                            IP           NODE
launchpad-app-7d4b8c6f9-abc12   172.17.0.4   minikube
launchpad-app-7d4b8c6f9-def34   172.17.0.5   minikube
launchpad-app-7d4b8c6f9-ghi56   172.17.0.6   minikube
```

Three IPs. All internal. They change every time a Pod restarts. You can't give Ava an IP that might not exist in 5 minutes.

Tomás draws on the whiteboard:

> "You need a **Service**. A stable front door that never changes, no matter how many Pods come and go behind it."

---

## What Is a Service?

```
Without a Service:              With a Service:

Ava → 172.17.0.4 (maybe dead?)  Ava → launchpad-service (stable)
Ava → 172.17.0.5 (maybe dead?)         │
Ava → 172.17.0.6 (maybe dead?)         ▼
                                 ┌──────────────┐
                                 │   Service    │
                                 │  (stable IP) │
                                 └──────┬───────┘
                                   load balances
                                 ┌──────┼───────┐
                                 ▼      ▼       ▼
                               Pod#1  Pod#2   Pod#3
```

A Service is a **stable address** that routes traffic to healthy Pods. Pods die and respawn — the Service doesn't care. It finds them by **labels**.

---

## Three Types of Services

| Type | Who Can Reach It | Analogy |
|---|---|---|
| **ClusterIP** | Only other Pods inside the cluster | Internal phone extension |
| **NodePort** | Anyone who knows the node's IP + a port | A side door with a specific number |
| **LoadBalancer** | The outside world via a cloud load balancer | The front entrance |

You'll start with ClusterIP, then graduate to NodePort for local testing.

---

## Your First Service

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: launchpad-service
spec:
  selector:
    app: launchpad
  ports:
    - port: 80
      targetPort: 8080
  type: ClusterIP
```

| Field | What It Means |
|---|---|
| `selector: app: launchpad` | "Find Pods with this label" |
| `port: 80` | The port the Service listens on |
| `targetPort: 8080` | The port on the Pod to forward to |
| `type: ClusterIP` | Internal only |

Apply it:

```bash
kubectl apply -f service.yaml
kubectl get services
```

```
NAME                TYPE        CLUSTER-IP     PORT(S)
launchpad-service   ClusterIP   10.96.45.123   80/TCP
```

Now any Pod in the cluster can call `http://launchpad-service:80` and reach one of your 3 Pods. Kubernetes handles the load balancing.

---

## But You're Not Inside the Cluster

You're on your laptop. ClusterIP is internal. You can't hit `10.96.45.123` from your browser.

**Option 1: Port-forward** (quick and dirty)

```bash
kubectl port-forward service/launchpad-service 8080:80
```

Now `http://localhost:8080` on your laptop → Service → Pod. Good for debugging. Not for real use.

**Option 2: NodePort** (expose on the node)

```yaml
# service-nodeport.yaml
apiVersion: v1
kind: Service
metadata:
  name: launchpad-nodeport
spec:
  selector:
    app: launchpad
  ports:
    - port: 80
      targetPort: 8080
      nodePort: 30080
  type: NodePort
```

```bash
kubectl apply -f service-nodeport.yaml
minikube service launchpad-nodeport --url
```

```
http://192.168.49.2:30080
```

Open that URL. Your app responds. From outside the cluster.

---

## How the Service Finds Pods

It's all labels. The same labels from Chapter 3.

```
Service selector:  app=launchpad
                        │
                        ▼ matches
         ┌────────────────────────────────┐
         │ Pod: app=launchpad  ← routed ✓ │
         │ Pod: app=launchpad  ← routed ✓ │
         │ Pod: app=launchpad  ← routed ✓ │
         │ Pod: app=other      ← ignored ✗│
         └────────────────────────────────┘
```

If a Pod crashes and a new one spawns with the same label, the Service automatically includes it. No config change needed.

---

## What You Learned

```
────────────────────┬──────────────────────────────────────
Concept             │ One-liner
────────────────────┼──────────────────────────────────────
Service             │ Stable address that routes to Pods
ClusterIP           │ Internal only — Pod-to-Pod
NodePort            │ Exposes on a fixed port on the node
LoadBalancer        │ Cloud-provided external IP
selector            │ Labels that connect Service → Pods
port-forward        │ Quick tunnel from laptop to cluster
────────────────────┴──────────────────────────────────────
```

---

## The Foreshadow

Your app is reachable. But Ava notices something in the code:

```java
@Value("${DB_PASSWORD}")
private String dbPassword;
```

The database password is in an environment variable. Which is hardcoded in the Deployment YAML. Which is committed to Git.

Tomás sees it and goes pale:

> "Secrets. In. Git. We need to fix this. Now."

---

[← Deployments](03-deployments.md) | [Next: Passwords Are in the Code →](05-config-secrets.md)
