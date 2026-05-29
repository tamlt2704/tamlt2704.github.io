# Chapter 6: Docker Registries

[← Compose](./chapter-05-compose.md) | [Next: Production →](./chapter-07-production.md)

---

## What is a Registry?

A registry stores and distributes Docker images. When you `docker pull nginx`, you're pulling from Docker Hub — the default public registry.

## Docker Hub

```bash
# Login to Docker Hub
docker login

# Pull an image
docker pull nginx:1.25

# Tag your image for Docker Hub
docker tag my-app:1.0 yourusername/my-app:1.0

# Push to Docker Hub
docker push yourusername/my-app:1.0

# Logout
docker logout
```

### Docker Hub rate limits

- Anonymous: 100 pulls per 6 hours
- Authenticated (free): 200 pulls per 6 hours
- Pro/Team: unlimited

## Tagging Strategy

Tags identify specific versions of an image. A good tagging strategy is critical for production.

```bash
# Semantic versioning
docker tag my-app:latest my-app:1.0.0
docker tag my-app:latest my-app:1.0
docker tag my-app:latest my-app:1

# Git SHA for traceability
docker tag my-app:latest my-app:abc1234

# Environment tags
docker tag my-app:latest my-app:staging
docker tag my-app:latest my-app:production
```

### Recommended approach

```bash
# Build with git SHA and version
docker build -t my-app:1.2.3 -t my-app:abc1234 -t my-app:latest .
```

- Use `latest` only for development — never in production deployments
- Use semantic versions for releases
- Use git SHAs for CI/CD traceability

## GitHub Container Registry (GHCR)

```bash
# Login to GHCR
echo YOUR_GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# Tag for GHCR
docker tag my-app:1.0 ghcr.io/yourusername/my-app:1.0

# Push
docker push ghcr.io/yourusername/my-app:1.0

# Pull
docker pull ghcr.io/yourusername/my-app:1.0
```

### GitHub Actions integration

```yaml
# .github/workflows/publish.yml
name: Publish Docker Image

on:
  push:
    tags: ["v*"]

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v4

      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: github-username
          password: secrets.GITHUB_TOKEN

      - uses: docker/build-push-action@v5
        with:
          push: true
          tags: |
            ghcr.io/yourusername/my-app:latest
            ghcr.io/yourusername/my-app:github.sha
```

## Private Registry (Self-Hosted)

Run your own registry for internal images:

```bash
# Run a local registry
docker run -d -p 5000:5000 --name registry \
  -v registry-data:/var/lib/registry \
  registry:2

# Tag for local registry
docker tag my-app:1.0 localhost:5000/my-app:1.0

# Push to local registry
docker push localhost:5000/my-app:1.0

# Pull from local registry
docker pull localhost:5000/my-app:1.0
```

### Registry with authentication

```bash
# Create password file
docker run --rm --entrypoint htpasswd \
  httpd:2 -Bbn admin secretpassword > auth/htpasswd

# Run registry with auth
docker run -d -p 5000:5000 --name registry \
  -v registry-data:/var/lib/registry \
  -v ./auth:/auth \
  -e REGISTRY_AUTH=htpasswd \
  -e REGISTRY_AUTH_HTPASSWD_REALM="Registry Realm" \
  -e REGISTRY_AUTH_HTPASSWD_PATH=/auth/htpasswd \
  registry:2
```

## Other Registries

| Registry                 | URL                                     | Notes                            |
| ------------------------ | --------------------------------------- | -------------------------------- |
| Docker Hub               | hub.docker.com                          | Default, largest public registry |
| GHCR                     | ghcr.io                                 | Free for public repos            |
| AWS ECR                  | account-id.dkr.ecr.region.amazonaws.com | Integrated with AWS              |
| Google Artifact Registry | region-docker.pkg.dev                   | Integrated with GCP              |
| Azure ACR                | myregistry.azurecr.io                   | Integrated with Azure            |

## Managing Images in Registries

```bash
# List tags for an image (Docker Hub API)
curl -s "https://hub.docker.com/v2/repositories/library/node/tags?page_size=10" | jq '.results[].name'

# Remove local images
docker rmi my-app:1.0

# Remove dangling images (untagged)
docker image prune

# Remove all unused images
docker image prune -a
```

## Exercises

1. Create a Docker Hub account, tag a local image, and push it
2. Pull your pushed image on a different machine (or after removing it locally)
3. Set up a local registry, push an image to it, and pull it back
4. Implement a tagging strategy: tag the same image with a version, git SHA, and `latest`
5. Push an image to GitHub Container Registry using a personal access token

---

[← Compose](./chapter-05-compose.md) | [Next: Production →](./chapter-07-production.md)
