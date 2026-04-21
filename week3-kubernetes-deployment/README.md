# Week 3: Kubernetes Deployment

## Objective
Deploy the containerized Wallet Service to Kubernetes with high availability, 
service discovery, and external access.

## What We're Building

**Architecture:**

```
Ingress (nginx)
↓
Service: wallet-service (Load Balancer)
↓         ↓
Pod 1     Pod 2  (wallet-service replicas)
↓         ↓
Service: dynamodb-local (Internal DNS)
↓
Pod: dynamodb-local
```

**Components:**
- 2 Deployments (wallet-service, dynamodb-local)
- 2 Services (external access, internal DNS)
- 1 Ingress (external routing)
- ConfigMaps & Secrets (configuration)

---

## Deploy to Kubernetes

### Step 1: Prepare Minikube
[Steps here...]

### Step 2: Deploy DynamoDB Local
[Steps here...]

### Step 3: Deploy Wallet Service
[Steps here...]

[etc...]
