---
title: "Chapter 6: Storage - Persistence in Kubernetes"
date: 2026-05-29
series: ["kubernetes-local"]
chapter: 6
---

# Chapter 6: Storage

[Previous: Configuration](../chapter-05-config) | [Next: Helm](../chapter-07-helm)

---

## The Problem

Containers are ephemeral. When a Pod restarts, all data inside the container is lost. For databases, file uploads, or any stateful workload, you need persistent storage.

---

## Volume Types Overview

- **emptyDir**: temporary, lives with the Pod
- **hostPath**: maps a directory from the node (local dev only)
- **PersistentVolume (PV)**: cluster-level storage resource
- **PersistentVolumeClaim (PVC)**: a request for storage by a Pod

---

## PersistentVolume and PersistentVolumeClaim

### Create a PersistentVolume

On local clusters, use `hostPath` for the PV:

```yaml
# pv.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: local-pv
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: /tmp/k8s-data
```

### Create a PersistentVolumeClaim

```yaml
# pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: app-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 500Mi
```

```bash
kubectl apply -f pv.yaml
kubectl apply -f pvc.yaml
kubectl get pv,pvc
```

The PVC binds to the PV automatically.

### Use the PVC in a Pod

```yaml
# pod-with-pvc.yaml
apiVersion: v1
kind: Pod
metadata:
  name: storage-pod
spec:
  containers:
    - name: app
      image: busybox
      command: ["sh", "-c", "echo hello > /data/test.txt && sleep 3600"]
      volumeMounts:
        - name: data
          mountPath: /data
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName: app-pvc
```

```bash
kubectl apply -f pod-with-pvc.yaml
kubectl exec storage-pod -- cat /data/test.txt
```

Delete and recreate the Pod — the data persists:

```bash
kubectl delete pod storage-pod
kubectl apply -f pod-with-pvc.yaml
kubectl exec storage-pod -- cat /data/test.txt
# Still shows "hello"
```

---

## StorageClass

StorageClass enables dynamic provisioning — no need to manually create PVs.

minikube and kind come with a default StorageClass:

```bash
kubectl get storageclass
```

Use it in a PVC:

```yaml
# pvc-dynamic.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: dynamic-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: standard
  resources:
    requests:
      storage: 256Mi
```

```bash
kubectl apply -f pvc-dynamic.yaml
kubectl get pvc dynamic-pvc
# STATUS should be Bound, PV created automatically
```

---

## StatefulSets for Databases

StatefulSets provide:

- Stable network identities (pod-0, pod-1, pod-2)
- Ordered deployment and scaling
- Persistent storage per replica via volumeClaimTemplates

### Deploy PostgreSQL with StatefulSet

```yaml
# postgres-statefulset.yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres
spec:
  clusterIP: None
  selector:
    app: postgres
  ports:
    - port: 5432
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
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
              value: "mysecretpassword"
            - name: POSTGRES_DB
              value: "mydb"
          volumeMounts:
            - name: postgres-data
              mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
    - metadata:
        name: postgres-data
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 1Gi
```

```bash
kubectl apply -f postgres-statefulset.yaml
kubectl get statefulset postgres
kubectl get pods -l app=postgres
kubectl get pvc
```

### Test persistence

```bash
# Connect to PostgreSQL
kubectl exec -it postgres-0 -- psql -U postgres -d mydb -c "CREATE TABLE test (id serial, name text);"
kubectl exec -it postgres-0 -- psql -U postgres -d mydb -c "INSERT INTO test (name) VALUES ('hello');"

# Delete the pod (StatefulSet recreates it)
kubectl delete pod postgres-0

# Wait for it to come back
kubectl wait --for=condition=ready pod/postgres-0 --timeout=60s

# Data survives
kubectl exec -it postgres-0 -- psql -U postgres -d mydb -c "SELECT * FROM test;"
```

---

## Cleaning Up

```bash
kubectl delete statefulset postgres
kubectl delete svc postgres
kubectl delete pvc postgres-data-postgres-0
kubectl delete pod storage-pod
kubectl delete pvc app-pvc dynamic-pvc
kubectl delete pv local-pv
```

---

## Summary

- Use PersistentVolumeClaim to request storage
- StorageClass enables dynamic provisioning (no manual PV creation)
- StatefulSets give stable identities and per-replica persistent storage
- Perfect for databases and other stateful workloads

---

[Previous: Configuration](../chapter-05-config) | [Next: Helm](../chapter-07-helm)
