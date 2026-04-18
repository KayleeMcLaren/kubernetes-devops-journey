# kubernetes-devops-journey
This repository documents my hands-on journey transitioning from a backend/cloud engineer to a DevOps/SRE-focused engineer.

## Goals
- Build production-ready Kubernetes systems
- Implement CI/CD pipelines
- Add observability (Prometheus + Grafana)
- Apply everything to a real fintech system

---

## Day 1 — Kubernetes Setup (Minikube)

### Objective
Set up a local Kubernetes cluster using Minikube.

First intalled:
Minikube v1.38.1 
kubectl v1.35.3
Docker 29.4.0 
Docker Desktop
WSL 2
Chocolatey

Then
```
minikube start
```

Minikube failed with:
"This computer doesn't have VT-X/AMD-v enabled"

Caused by:
Cause
Windows virtualization (Hyper-V / VBS) conflicts with VirtualBox

Solution:
Switched to Docker driver

```
minikube delete
minikube start --driver=docker
```
Ensured Docker Desktop was running:
```

Result:
Cluster successfully running

```
kubectl get nodes
```
