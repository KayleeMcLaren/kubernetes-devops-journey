# kubernetes-devops-journey
This repository documents my hands-on journey transitioning from a backend/cloud engineer to a DevOps/SRE-focused engineer.

# Goals
- Build production-ready Kubernetes systems
- Implement CI/CD pipelines
- Add observability (Prometheus + Grafana)
- Apply everything to a real fintech system

---

# Step 1 — Kubernetes Setup (Minikube)

## Objective
Set up a local Kubernetes cluster using Minikube.

---

## **First, Environemnt Set Up:**

✅ Minikube v1.38.1 - tool that sets up a local, lightweight Kubernetes cluster for learning/testing 

✅ kubectl v1.35.3 - command line tool for interacting with your cluster via the Kubernetes API

✅ Docker 29.4.0 - OS‑level virtualization (or containerization) platform

✅ Docker Desktop - Docker desktop app that provides automatic configuration (WSL2 integration)

✅ WSL 2 - compatibility layer (translates foreign system calls into native host calls) to run Linux applications, utilities, and commands on Windows without needing a VM

---

## **Then start a single-node Kubernetes cluster:**
```
minikube start
```

### Error:
Minikube failed with:
"This computer doesn't have VT-X/AMD-v enabled."

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/minikube%20error.png)

### **Even though it is:**

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/BIOS.jpeg)


### **Caused by:**

Windows virtualization (Hyper-V / VBS) conflicts with VirtualBox.

### **Solution:**

Switched to Docker driver - more stable on Windows. 
This works because Docker operates at the OS level by sharing the host’s kernel.
Docker Desktop automatically launches a lightweight Linux VM in the background to provide that necessary kernel.
Windows uses the Windows Subsystem for Linux (WSL 2) to get near-native performance.

```
minikube delete
minikube start --driver=docker
```

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/docker%20driver.png)

### **Ensure Docker Desktop is running:**

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/docker%20desktop.png)

---

### **Check Kubernetes environment and connectivity:**
```
kubectl version --client
kubectl cluster-info
kubectl get nodes
```

### **Result:**

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/kubernetes%20checks.png)

✅ Kubernetes cluster is running (minikube node)

✅ Status is "Ready" (healthy)

✅ Control plane is working (can accept workloads)

✅ Running latest K8s version (v1.35.1)

---

### **Exploring a bit...**
```
# All running pods (system ones)
kubectl get pods --all-namespaces

# System services
kubectl get services --all-namespaces

# What's running in kube-system namespace
kubectl get all -n kube-system
```

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/exploring.png)

---

# Step 2: First Deployment

## Objective
Deploy something simple to understand K8s basics

---

## **First, make a folder for K8s files:**
```
mkdir k8s-learning
```

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/k8s-learning%20folder.png)

---

## **Create deployment file:**
```
notepad nginx-deployment.yaml
```

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/deployment%20file%20.png)

### **Content:**

*Note: K8s uses YAML to describe **desired state**.*
```
apiVersion: apps/v1          # K8s API version for Deployments
kind: Deployment             # Create a Deployment object
metadata:
  name: nginx-deployment     # Name of this deployment
  labels:
    app: nginx               # Label for organizing resources
spec:
  replicas: 2                # Run 2 copies (pods)
  selector:
    matchLabels:
      app: nginx             # This deployment manages pods with label "app: nginx"
template:                    # Template for the pods
    metadata:
      labels:
        app: nginx           # Pods get this label
    spec:
      containers:
      - name: nginx          # Container name
        image: nginx:1.27    # Docker image to use
        ports:
        - containerPort: 80  # Container listens on port 80
```
---

## **Deploy 2 nginx pods to K8s cluster:**
```
kubectl apply -f nginx-deployment.yaml
```

### **Error:**

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/nginx%20deployment%20error.png)

### **Restart minikube:**
```
minikube start --driver=docker
```
![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/restart%20minikube.png)


### **Retry deployment:**

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/successful%20deployment.png)

### **Success! Now to explore...**

---

### **Check deployment:**
```
kubectl get deployments
```

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/kubectl%20get%20deployment.png)

✅ READY 2/2 = 2 pods running out of 2 desired 

✅ UP-TO-DATE = latest version deployed

✅ AVAILABLE = ready to serve traffic

### **Check pods:**
```
kubectl get pods
```

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/kubectl%20get%20pods.png)


✅ 2 pods (because replicas: 2)

✅ Each has a unique name (deployment name + random suffix)

✅ Status is Running 

✅ READY 1/1 = 1 container running in the pod


### **Get detailed info about a pod:**
```
kubectl describe pod nginx-deployment-fd956d49d-7lshm
```

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/kubctl%20detailed%20pod%20info.png)


**Tons of info:**
* Pod IP address
* Node it's running on
* Container image
* Resource requests/limits
* Events (what happened to this pod)


### **Check logs for a pod:**

```
kubectl logs nginx-deployment-fd956d49d-7lshm
```

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/pod%20logs.png)


### **Get shell access to a pod:**

```
kubectl exec -it nginx-deployment-fd956d49d-7lshm -- /bin/bash
```

### **See nginx config:**
```
cat /etc/nginx/nginx.conf
```

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/pod%20shell%20access.png)


### **See processes:**
```
ps aux
```

### **Error:**

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/ps%20aux%20error.png)

### **Why?**
The nginx container image is minimal — it only includes what's needed to run nginx, nothing extra. ps is not needed to run nginx, so it's not included.

### **Try a different way:**
```
cat /proc/*/cmdline
```

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/alt%20processes%20cmd.png)

---

## **Next, expose the deployment:**
*Note: Right now the pods exist but can't be accessed from outside of the cluster*

## First, create a service: ##
```
notepad nginx-service.yaml
```

## Content: ##
```
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  type: NodePort	# Expose on a port on the node (for local testing)
  selector:
    app: nginx		# Route traffic to pods with label "app: nginx"
  ports:
  - protocol: TCP
    port: 80		# Service listens on port 80
    targetPort: 80	# Forward to pod's port 80
```

## Then apply the service:

```
kubectl apply -f nginx-service.yaml
```

## Check the service:

```
kubectl get services
```

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/create%20nginx%20service.png)

## Lastly, access nginx in the browser:

```
minikube service nginx-service
```
![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/nginx%20browser%201.png)

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/nginx%20browser%202.png)


---
