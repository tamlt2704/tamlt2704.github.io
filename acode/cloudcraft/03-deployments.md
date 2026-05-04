# Chapter 3: "It Crashed. Bring It Back."

[← First Pod](02-first-pod.md) | [Next: Users Can't Reach It →](04-services.md)

---

3 AM. Your phone buzzes. Nora in Slack:

> "App is down. Pod crashed. Nobody restarted it."

You SSH in. The Pod is gone. You `kubectl apply` the pod.yaml again. The app comes back. You go back to sleep.

6 AM. It crashes again. You restart it again.

9 AM. Nora is at your desk:

> "I don't want humans restarting Pods. I want Kubernetes to do it. Automatically. Forever."

---

## The Problem with Bare Pods

A bare Pod (what you created in Chapter 2) is like hiring a contractor with no contract:

- They show up once
- If they quit, nobody replaces them
- If you need three of them, you create three separate Pods by hand

You need a **manager** that says: "I always want 3 copies running. If one dies, make a new one."

That manager is a **Deployment**.

---

## What Is a Deployment?

```
You say:  "I want 3 replicas of my app"
              │
              ▼
Deployment:  "Got it. I'll create a ReplicaSet."
              │
              ▼
ReplicaSet:  "I maintain exactly 3 Pods at all times."
              │
              ▼
         ┌────────┐ ┌────────┐ ┌────────┐
         │ Pod #1 │ │ Pod #2 │ │ Pod #3 │
         └────────┘ └────────┘ └────────┘
                         │
                     Pod #2 crashes 💥
                         │
ReplicaSet:  "Only 2 running. Spinning up Pod #4."
                         │
         ┌────────┐ ┌────────┐ ┌────────┐
         │ Pod #1 │ │ Pod #4 │ │ Pod #3 │
         └────────┘ └────────┘ └────────┘
```

You never create Pods directly again. You create Deployments. The Deployment creates the Pods for you — and **keeps them alive**.

---

## Your First Deployment

Delete the old bare Pod first:

```bash
kubectl delete pod launchpad-app --ignore-not-found
```

Now create a Deployment:

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: launchpad-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: launchpad
  template:
    metadata:
      labels:
        app: launchpad
    spec:
      containers:
        - name: app
          image: launchpad-app:v1
          ports:
            - containerPort: 8080
```

| Field | What It Means |
|---|---|
| `replicas: 3` | "Always keep 3 Pods running" |
| `selector.matchLabels` | How the Deployment finds its Pods |
| `template` | The Pod blueprint — every replica looks like this |
| `labels` | Tags on the Pod — like sticky notes |

Apply it:

```bash
kubectl apply -f deployment.yaml
kubectl get pods
```

```
NAME                            READY   STATUS    RESTARTS   AGE
launchpad-app-7d4b8c6f9-abc12   1/1     Running   0          5s
launchpad-app-7d4b8c6f9-def34   1/1     Running   0          5s
launchpad-app-7d4b8c6f9-ghi56   1/1     Running   0          5s
```

Three Pods. Automatically. The random suffixes are Kubernetes naming them.

---

## The Self-Healing Test

Kill one:

```bash
kubectl delete pod launchpad-app-7d4b8c6f9-abc12
kubectl get pods
```

```
NAME                            READY   STATUS    RESTARTS   AGE
launchpad-app-7d4b8c6f9-def34   1/1     Running   0          2m
launchpad-app-7d4b8c6f9-ghi56   1/1     Running   0          2m
launchpad-app-7d4b8c6f9-xyz99   1/1     Running   0          3s   ← new!
```

You killed one. Kubernetes made a new one. Instantly. No human involved.

This is **self-healing**. The Deployment constantly compares "how many Pods do I want?" (3) vs "how many are running?" (2) and fixes the gap.

---

## Labels: How Kubernetes Connects Things

Labels are key-value pairs stuck on resources. They're how everything in Kubernetes finds everything else.

```
Deployment says: "I manage Pods with label app=launchpad"
                          │
                          ▼
         ┌────────────────────────────────┐
         │ Pod: app=launchpad             │  ← matches ✓
         │ Pod: app=launchpad             │  ← matches ✓
         │ Pod: app=launchpad             │  ← matches ✓
         │ Pod: app=something-else        │  ← ignored ✗
         └────────────────────────────────┘
```

Labels are just strings. No magic. But they're the **glue** of Kubernetes.

---

## The Hierarchy

```
Deployment
  └── creates → ReplicaSet
                  └── creates → Pod
                                 └── runs → Container
```

You interact with the Deployment. You almost never touch ReplicaSets or Pods directly.

```bash
kubectl get deployments
kubectl get replicasets
kubectl get pods
```

Three levels. The Deployment is your interface. Everything below is managed for you.

---

## What You Learned

```
────────────────────┬──────────────────────────────────────
Concept             │ One-liner
────────────────────┼──────────────────────────────────────
Deployment          │ "Keep N replicas running, always"
ReplicaSet          │ The thing that actually counts Pods
replicas            │ Desired number of identical Pods
Labels              │ Key-value tags that connect resources
Self-healing        │ K8s replaces dead Pods automatically
────────────────────┴──────────────────────────────────────
```

---

## The Foreshadow

You have 3 Pods. They're alive. They self-heal.

But nobody can reach them. The Pods have internal IPs that change every time they restart. There's no stable address.

Ava tries to call the API:

> "What's the URL?"

You don't have one. Yet. That's a **Service** problem.

---

[← First Pod](02-first-pod.md) | [Next: Users Can't Reach It →](04-services.md)
