# kubernetes-devops-journey
This repository documents my hands-on journey transitioning from a backend/cloud engineer to a DevOps/SRE-focused engineer.

## Goals
- Build production-ready Kubernetes systems
- Implement CI/CD pipelines
- Add observability (Prometheus + Grafana)
- Apply everything to a real fintech system

---

## Step 1 — Kubernetes Setup (Minikube)

### Objective
Set up a local Kubernetes cluster using Minikube.

**First install:**

✅ Minikube v1.38.1 

✅ kubectl v1.35.3

✅ Docker 29.4.0 

✅ Docker Desktop

✅ WSL 2

✅ Chocolatey

---

**Then start a single-node Kubernetes cluster:**
```
minikube start
```

Minikube failed with:
"This computer doesn't have VT-X/AMD-v enabled."

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/minikube%20error.png)

**Even though it is:**

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/BIOS.jpeg)


**Caused by:**

Windows virtualization (Hyper-V / VBS) conflicts with VirtualBox.

**Solution:**

Switched to Docker driver.

```
minikube delete
minikube start --driver=docker
```

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/docker%20driver.png)

**Ensured Docker Desktop was running:**

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/docker%20desktop.png)

---

**Check Kubernetes environment and connectivity:**
```
kubectl version --client
kubectl cluster-info
kubectl get nodes
```

**Result:**

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/kubernetes%20checks.png)

✅ Kubernetes cluster is running (minikube node)

✅ Status is "Ready" (healthy)

✅ Control plane is working (can accept workloads)

✅ Running latest K8s version (v1.35.1)

