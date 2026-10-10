# GitOps with Argo CD

This document describes how the GitOps layer is set up and how to reproduce it.

## Overview

Argo CD watches the `main` branch of this repository and automatically applies
any change to `helm/devsecops-app/` into the Kind cluster. No manual `helm upgrade`
is needed; every merged change to Git becomes the desired cluster state.

```
Git push → Argo CD detects diff → applies Helm chart → cluster converges
```

## Prerequisites

- [Kind](https://kind.sigs.k8s.io/) v0.20+
- [kubectl](https://kubernetes.io/docs/tasks/tools/) v1.28+
- [Helm](https://helm.sh/docs/intro/install/) v3.12+
- Docker (for the local image)

## Setup

### 1. Create the Kind cluster and load the image

```bash
kind create cluster --name devsecops
docker build -t devsecops-app:local .
kind load docker-image devsecops-app:local --name devsecops
```

### 2. Install Argo CD (core install — no UI server, lower resource usage)

```bash
kubectl create namespace argocd
kubectl apply -n argocd \
  -f https://raw.githubusercontent.com/argoproj/argo-cd/v2.13.1/manifests/core-install.yaml

# Wait for all components to be ready
kubectl rollout status deployment/argocd-redis -n argocd --timeout=120s
kubectl rollout status deployment/argocd-repo-server -n argocd --timeout=180s
kubectl rollout status statefulset/argocd-application-controller -n argocd --timeout=180s
```

### 3. Bootstrap the default AppProject and apply the Application

```bash
kubectl apply -f argocd/appproject-default.yaml
kubectl apply -f argocd/application.yaml
```

### 4. Verify sync status

```bash
kubectl get application devsecops-app -n argocd
# Expected: SYNC STATUS=Synced  HEALTH STATUS=Healthy
```

### 5. Access the application

```bash
kubectl port-forward svc/devsecops-app 8080:80 -n default
curl http://localhost:8080/health
# {"status":"healthy"}
```

## Reconciliation demo (observed results)

| Step | Action | Observed result |
|------|--------|-----------------|
| 1 | Edit `helm/devsecops-app/values.yaml`: `replicaCount: 1 → 2`, push to `main` | Argo CD detected within ~1 poll cycle (~3 min), scaled to 2 pods, `Synced Healthy` |
| 2 | Edit `values.yaml`: `replicaCount: 2 → 1`, push to `main` | Argo CD pruned the extra pod, back to 1 pod, `Synced Healthy` |

Prune and self-heal are enabled. Any manual change to cluster resources will be
reverted to match Git on the next sync cycle.

## Files

| File | Purpose |
|------|---------|
| `argocd/application.yaml` | Argo CD Application — tracks this repo, branch `main`, path `helm/devsecops-app` |
| `argocd/appproject-default.yaml` | Default AppProject (required by core install) |
| `helm/devsecops-app/` | Helm chart managed by Argo CD |
