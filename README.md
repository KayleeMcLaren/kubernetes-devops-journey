# kubernetes-devops-journey
This repository documents my hands-on journey transitioning from a backend/cloud engineer to a DevOps/SRE-focused engineer.

---

## Table of Contents
- [Goals](#goals)
- [Step 1: Kubernetes Setup (Minikube)](#step-1--kubernetes-setup-minikube)
- [Step 2: First Deployment](#step-2-first-deployment)
- [K8s Magic: Self-Healing & Scaling](#k8s-magic)
- [Visualizing with Dashboard](#use-kubernetes-dashboard-to-visualise-the-cluster)
- [Clean Up](#clean-up)
- [Key Learnings](#key-learnings) ← NEW
- [Next Steps](#next-steps) ← NEW

---

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
Using the Docker driver launches a local Kubernetes cluster by running the Minikube control plane inside a Docker container.
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

# K8s Magic:

## Self-healing:
```
kubectl get pods
kubectl delete pod nginx-deployment-fd956d49d-7lshm
kubectl get pods
```

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/self%20healing.png)

A new pod (nginx-deployment-fd956d49d-wdpgx) is automatically created to maintain `replicas: 2` in the nginx-deployment.yaml configuration file.

*In production, if a server dies, K8s replaces it automatically.*

## Scale up the deployment
```
kubectl scale deployment nginx-deployment --replicas=5
kubectl get pods
kubectl scale deployment nginx-deployment --replicas=2
kubectl get pods
```

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/scale%20up%20and%20down.png)

K8s constantly works to match actual state with the **desired state**.

The `kubectl scale deployment nginx-deployment --replicas=5` command immediately instructs the Kubernetes control plane to update the desired state of the application to 5 Pods.

If there are fewer than 5 Pods, the cluster will automatically start new ones to reach that target.

## Update the nginx version (rolling update)

Edit nginx-deployment.yaml and change: `image: nginx:1.27` to `image: nginx:1.26`.

Apply the change, watch the rollout, and then check the image.

```
kubectl apply -f nginx-deployment.yaml
kubectl rollout status deployment/nginx-deployment
kubectl describe pods | findstr Image:
```

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/nginx%20rolling%20update.png)

K8s:
* Created new pods with nginx:1.26
* Waited for them to be ready
* Terminated old pods with nginx:1.27
* All with zero downtime! 

## Use Kubernetes Dashboard to visualise the cluster:

### Run:
```
minikube dashboard
```

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/dashboard%20cmd.png)

### Result:
This opens a web UI showing:
* All deployments
* All pods
* All services
* Resource usage
* Logs
* Etc.

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/dashboard%20view.png)

## One command to see everything:
```
kubectl get all
```

### This shows:
* Pods (individual containers)
* Services (network endpoints)
* Deployments (pod managers)
* ReplicaSets (created by Deployment, manages pod replicas)

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/get%20all%20cmd.png)

## Clean up

Delete nginx-deployment.yaml and nginx-service.yaml files, confirm that they're gone (`kubectl get all` should only show the default kubernetes service), and pause the cluster.
```
kubectl delete -f nginx-deployment.yaml
kubectl delete -f nginx-service.yaml
kubectl get all
minikube stop
```

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/clean%20up.png)

---

## 🎓 Key Learnings

**Concepts Mastered:**
- ✅ Kubernetes fundamentals (Pods, Deployments, Services, ReplicaSets)
- ✅ kubectl CLI for cluster interaction
- ✅ Declarative configuration with YAML
- ✅ Self-healing and auto-scaling
- ✅ Rolling updates for zero-downtime deployments
- ✅ Container minimalism and debugging strategies

**Skills Developed:**
- Troubleshooting virtualization issues (VT-X → Docker driver)
- Understanding K8s architecture (control plane, nodes, pods)
- Using kubectl to inspect and debug resources
- Reading K8s manifests and understanding desired state

**Production Insights:**
- Kubernetes constantly reconciles actual state → desired state
- Containers are minimal by design (only what's needed)
- Self-healing eliminates manual intervention
- Rolling updates enable continuous deployment
