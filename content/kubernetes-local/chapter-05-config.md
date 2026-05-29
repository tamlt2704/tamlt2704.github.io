---
title: "Chapter 5: Configuration - ConfigMaps and Secrets"
date: 2026-05-29
series: ["kubernetes-local"]
chapter: 5
---

# Chapter 5: Configuration

[Previous: Services](../chapter-04-services) | [Next: Storage](../chapter-06-storage)

---

## Why Externalize Configuration?

Hardcoding config in container images means rebuilding for every environment. Kubernetes provides ConfigMaps and Secrets to inject configuration at runtime.

---

## ConfigMaps

### Create from literal values

```bash
kubectl create configmap app-config \
  --from-literal=APP_ENV=development \
  --from-literal=LOG_LEVEL=debug

kubectl get configmap app-config -o yaml
```

### Create from a file

Create `app.properties`:

```
database.host=postgres
database.port=5432
cache.ttl=300
```

```bash
kubectl create configmap app-config-file --from-file=app.properties
```

### Create from YAML

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-settings
data:
  APP_ENV: "development"
  LOG_LEVEL: "debug"
  config.json: |
    {
      "port": 8080,
      "debug": true
    }
```

```bash
kubectl apply -f configmap.yaml
```

---

## Using ConfigMaps as Environment Variables

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: config-env-pod
spec:
  containers:
    - name: app
      image: busybox
      command: ["sh", "-c", "echo APP_ENV=$APP_ENV LOG_LEVEL=$LOG_LEVEL && sleep 3600"]
      envFrom:
        - configMapRef:
            name: app-settings
```

```bash
kubectl apply -f config-env-pod.yaml
kubectl logs config-env-pod
```

### Select specific keys

```yaml
env:
  - name: MY_ENV
    valueFrom:
      configMapKeyRef:
        name: app-settings
        key: APP_ENV
```

---

## Using ConfigMaps as Volume Mounts

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: config-vol-pod
spec:
  containers:
    - name: app
      image: busybox
      command: ["sh", "-c", "cat /etc/config/config.json && sleep 3600"]
      volumeMounts:
        - name: config-volume
          mountPath: /etc/config
  volumes:
    - name: config-volume
      configMap:
        name: app-settings
```

```bash
kubectl apply -f config-vol-pod.yaml
kubectl exec config-vol-pod -- ls /etc/config
kubectl exec config-vol-pod -- cat /etc/config/config.json
```

---

## Secrets

Secrets store sensitive data (passwords, tokens, keys). They are base64-encoded (not encrypted by default).

### Create a Secret

```bash
kubectl create secret generic db-credentials \
  --from-literal=username=admin \
  --from-literal=password=s3cr3tP@ss
```

### Secret YAML

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
type: Opaque
data:
  username: YWRtaW4=
  password: czNjcjN0UEBzcw==
```

Values are base64-encoded. Encode with:

```bash
echo -n "admin" | base64
echo -n "s3cr3tP@ss" | base64
```

---

## Using Secrets in Pods

### As environment variables

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secret-env-pod
spec:
  containers:
    - name: app
      image: busybox
      command: ["sh", "-c", "echo user=$DB_USER && sleep 3600"]
      env:
        - name: DB_USER
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: username
        - name: DB_PASS
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: password
```

### As volume mounts

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secret-vol-pod
spec:
  containers:
    - name: app
      image: busybox
      command: ["sh", "-c", "cat /etc/secrets/password && sleep 3600"]
      volumeMounts:
        - name: secret-volume
          mountPath: /etc/secrets
          readOnly: true
  volumes:
    - name: secret-volume
      secret:
        secretName: db-credentials
```

---

## Sealed Secrets for Git

Regular Secrets cannot be committed to git (they are only base64-encoded). Sealed Secrets encrypt them so they are safe to store in version control.

### Install Sealed Secrets

```bash
# Install the controller in your cluster
helm repo add sealed-secrets https://bitnami-labs.github.io/sealed-secrets
helm install sealed-secrets sealed-secrets/sealed-secrets -n kube-system

# Install kubeseal CLI
# macOS
brew install kubeseal
# Linux
wget https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/kubeseal-0.24.0-linux-amd64.tar.gz
tar -xvzf kubeseal-0.24.0-linux-amd64.tar.gz
sudo install kubeseal /usr/local/bin/
```

### Create a Sealed Secret

```bash
# Create a regular secret YAML (do not apply it)
kubectl create secret generic my-secret \
  --from-literal=api-key=abc123 \
  --dry-run=client -o yaml > my-secret.yaml

# Seal it
kubeseal --format yaml < my-secret.yaml > my-sealed-secret.yaml

# Now safe to commit my-sealed-secret.yaml to git
kubectl apply -f my-sealed-secret.yaml
```

The controller decrypts it in-cluster and creates the actual Secret.

---

## Cleaning Up

```bash
kubectl delete pod config-env-pod config-vol-pod secret-env-pod secret-vol-pod
kubectl delete configmap app-config app-config-file app-settings
kubectl delete secret db-credentials
```

---

## Summary

- ConfigMaps for non-sensitive configuration
- Secrets for sensitive data (base64, not encrypted at rest by default)
- Inject via environment variables or volume mounts
- Use Sealed Secrets to safely store secrets in git

---

[Previous: Services](../chapter-04-services) | [Next: Storage](../chapter-06-storage)
