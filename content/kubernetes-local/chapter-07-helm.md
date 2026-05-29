---
title: "Chapter 7: Helm - Package Manager for Kubernetes"
date: 2026-05-29
series: ["kubernetes-local"]
chapter: 7
---

# Chapter 7: Helm

[Previous: Storage](../chapter-06-storage) | [Next: Observability](../chapter-08-observability)

---

## What is Helm?

Helm is the package manager for Kubernetes. A Helm **chart** is a bundle of YAML templates that define a complete application deployment.

Benefits:

- Package complex apps into a single installable unit
- Parameterize deployments with values.yaml
- Version and rollback releases
- Share charts via repositories

---

## Install Helm

**Windows (winget):**

```powershell
winget install Helm.Helm
```

**macOS (Homebrew):**

```bash
brew install helm
```

**Linux:**

```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

Verify:

```bash
helm version
```

---

## Helm Concepts

- **Chart**: a package of Kubernetes manifests + templates
- **Release**: an installed instance of a chart
- **Repository**: a collection of charts
- **values.yaml**: configuration for a chart

---

## Using Chart Repositories

```bash
# Add the Bitnami repo
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Search for charts
helm search repo nginx
helm search repo postgresql
```

---

## Install a Chart

```bash
# Install nginx
helm install my-nginx bitnami/nginx

# Check the release
helm list
kubectl get all -l app.kubernetes.io/instance=my-nginx
```

### Install with custom values

```bash
helm install my-nginx bitnami/nginx --set service.type=ClusterIP --set replicaCount=2
```

Or create a `values.yaml`:

```yaml
# my-values.yaml
replicaCount: 2
service:
  type: ClusterIP
```

```bash
helm install my-nginx bitnami/nginx -f my-values.yaml
```

---

## Upgrade a Release

```bash
helm upgrade my-nginx bitnami/nginx --set replicaCount=3
helm list
```

---

## Rollback

```bash
# View history
helm history my-nginx

# Rollback to revision 1
helm rollback my-nginx 1

# Verify
helm list
```

---

## Uninstall

```bash
helm uninstall my-nginx
```

---

## Creating Your Own Chart

```bash
helm create myapp
```

This generates:

```
myapp/
  Chart.yaml          # Chart metadata
  values.yaml         # Default values
  templates/          # Kubernetes manifest templates
    deployment.yaml
    service.yaml
    ingress.yaml
    _helpers.tpl      # Template helpers
```

### Edit values.yaml

```yaml
# myapp/values.yaml
replicaCount: 2
image:
  repository: hashicorp/http-echo
  tag: "0.2.3"
service:
  type: ClusterIP
  port: 80
containerPort: 5678
appArgs:
  - "-text=Hello from my Helm chart"
```

### Edit templates/deployment.yaml

The template uses Go templating. Key parts:

```yaml
spec:
  replicas: {{ .Values.replicaCount }}
  ...
  containers:
    - name: {{ .Chart.Name }}
      image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
      args: {{ toYaml .Values.appArgs | nindent 8 }}
      ports:
        - containerPort: {{ .Values.containerPort }}
```

### Test your chart

```bash
# Render templates without installing (dry run)
helm template myapp ./myapp

# Install
helm install myapp-release ./myapp

# Verify
kubectl get all -l app.kubernetes.io/instance=myapp-release
```

### Package your chart

```bash
helm package ./myapp
# Creates myapp-0.1.0.tgz
```

---

## Chart Repositories

### Host on GitHub Pages or any HTTP server

```bash
helm package ./myapp
helm repo index . --url https://your-username.github.io/helm-charts/
# Upload index.yaml and .tgz to your hosting
```

### Use a local repo for testing

```bash
# Serve charts locally
helm serve --repo-path ./charts
# Or use chartmuseum
```

---

## Useful Helm Commands

```bash
# See what a chart will install
helm show values bitnami/nginx

# Dry run an install
helm install test bitnami/nginx --dry-run

# Get the manifests of an installed release
helm get manifest my-nginx

# List all releases
helm list --all-namespaces
```

---

## Summary

- Helm packages Kubernetes apps as charts
- Install, upgrade, and rollback with simple commands
- Customize deployments with values.yaml
- Create your own charts for reusable deployments
- Share charts via repositories

---

[Previous: Storage](../chapter-06-storage) | [Next: Observability](../chapter-08-observability)
