# Chapter 2: "Run It in Kubernetes"

[← Containerize](01-containerize.md) | [Next: It Crashed. Bring It Back. →](03-deployments.md)

---

Nora walks to your desk with a napkin. On it:

```
"1 container = 1 point of failure. Fix that."
```

Tomás translates:

> "You need an **orchestrator**. Something that runs your containers, watches them, and restarts them if they die. That's Kubernetes. We call it K8s."

---

## What Is Kubernetes?

Tomás draws on the whiteboard:

> "Imagine you're a **restaurant manager**. You don't cook. You don't serve. You **decide**: which chef works which station, when to call in extra staff, what to do when someone calls in sick."

```
You (the developer):  "I need 3 copies of my app"
         │
         ▼
Kubernetes (the manager):
  "Got it. I'll put them on available machines,
   watch them, and replace any that crash."
         │
         ▼
┌────────┐ ┌────────┐ ┌────────┐
│ App #1 │ │ App #2 │ │ App #3 │
│ Node A │ │ Node A │ │ Node B │
└────────┘ └────────┘ └────────┘
```

You **declare** what you want. Kubernetes **makes it happen**.

---

## The Key Pieces

| Concept | Restaurant Analogy | What It Is |
|---|---|---|
| **Cluster** | The whole restaurant | A set of machines running Kubernetes |
| **Node** | A kitchen station | One machine (physical or virtual) |
| **Pod** | A plate of food | Smallest deployable unit — usually one container |
| **kubectl** | Your walkie-talkie | CLI tool to talk to the cluster |

A Pod is **not** a container. A Pod *wraps* one or more containers. In practice, it's almost always one container per Pod. Think of the Pod as the plate, the container as the food on it.

---

## Install Minikube

Minikube gives you a single-node Kubernetes cluster on your laptop.

```bash
# macOS
brew install minikube

# Windows
choco install minikube

# Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

Start it:

```bash
minikube start
```

That's it. You now have a Kubernetes cluster. One node. Running in Docker.

Verify:

```bash
kubectl get nodes
```

```
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   30s   v1.28.3
```

One node. Ready. You're in.

---

## Your First Pod

You could run `kubectl run` — but Tomás stops you.

> "In Kubernetes, we don't type commands. We write **manifests**. YAML files that describe what we want. Kubernetes reads them and makes it real."

```yaml
# pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: launchpad-app
spec:
  containers:
    - name: app
      image: launchpad-app:v1
      ports:
        - containerPort: 8080
```

| Field | What It Means |
|---|---|
| `kind: Pod` | "I want a Pod" |
| `metadata.name` | The Pod's name |
| `spec.containers` | List of containers in this Pod |
| `image` | Which Docker image to run |
| `containerPort` | The port the app listens on |

Apply it:

```bash
kubectl apply -f pod.yaml
```

Check it:

```bash
kubectl get pods
```

```
NAME            READY   STATUS    RESTARTS   AGE
launchpad-app   1/1     Running   0          10s
```

Running. One Pod. One container. On your laptop.

---

## Peek Inside

```bash
kubectl logs launchpad-app
```

You see Spring Boot starting up. The familiar banner. The app is alive inside Kubernetes.

Want a shell inside the container?

```bash
kubectl exec -it launchpad-app -- sh
```

You're inside. It's Alpine Linux. Your JAR is at `/app.jar`. Type `exit` to leave.

---

## The Lifecycle of a Pod

```
kubectl apply     Pod created
     │                │
     ▼                ▼
  Pending ──→ Running ──→ Succeeded
                │
                ▼
             Failed (crash, OOM, etc.)
```

A Pod is **ephemeral**. It's born, it runs, it dies. Kubernetes doesn't restart a bare Pod. If it crashes, it's gone.

Tomás looks at you:

> "Kill it."

```bash
kubectl delete pod launchpad-app
kubectl get pods
```

```
No resources found.
```

Gone. No restart. No recovery. Just... gone.

---

## What You Learned

```
────────────────────┬──────────────────────────────────────
Concept             │ One-liner
────────────────────┼──────────────────────────────────────
Cluster             │ A set of machines running K8s
Node                │ One machine in the cluster
Pod                 │ Wrapper around one or more containers
kubectl             │ CLI to talk to the cluster
Manifest (YAML)     │ Declarative description of what you want
kubectl apply       │ "Make this YAML real"
kubectl get pods    │ "Show me what's running"
kubectl logs        │ "Show me the output"
kubectl exec        │ "Let me inside"
────────────────────┴──────────────────────────────────────
```

---

## The Foreshadow

Your Pod runs. But when it dies, it stays dead.

Tomorrow, Nora will ask:

> "What happens when the app crashes at 3 AM? Who restarts it?"

The answer isn't "you." The answer is a **Deployment**.

---

[← Containerize](01-containerize.md) | [Next: It Crashed. Bring It Back. →](03-deployments.md)
