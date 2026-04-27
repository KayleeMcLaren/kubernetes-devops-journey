# Week 3: Kubernetes Deployment

## Objective
Deploy the containerized Wallet Service to Kubernetes with high availability, 
service discovery, and external access.

## What I Built
A production-grade Kubernetes deployment with:

* Multi-container application orchestration 
* High availability (2 wallet service replicas)
* Service discovery and load balancing 
* External access via Ingress controller 
* ConfigMaps for configuration management 
* Health checks and resource limits

## Architecture:

**Before (Docker):**
```
Docker Host
├── dynamodb-local container (port 8000)
└── wallet-service container (port 8001)
```

**After (Kubernetes):**
```
Ingress (nginx) → External access
    ↓
Service: wallet-service (Load Balancer, port 80)
    ↓           ↓
Pod 1       Pod 2  (wallet-service replicas)
    ↓           ↓
Service: dynamodb-local (Internal DNS, port 8000)
    ↓
Pod: dynamodb-local
```

**Components:**
- 2 Deployments (wallet-service, dynamodb-local)
- 2 Services (external access, internal DNS)
- 1 Ingress (external routing)
- ConfigMaps & Secrets (configuration)

---

## Step 1: Create Project Structure

### **1.1 Create K8s manifests folders:**
```
# Create k8s manifests folders
cd week3-kubernetes-deployment
mkdir k8s-manifests
mkdir k8s-manifests\dynamodb-local
mkdir k8s-manifests\wallet-service
```

### **1.2 Check the folder structure:**
```
tree /F
```

**Output:**

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/k8s%20manifests%20verify.png)

---

## Step 2: Deploy DynamoDB Local to K8s

### **2.1 Create DynamoDB Deployment:**  
**Navigate to the dynamodb-local folder and create the `dynamodb-deployment.yaml` file.**
```
cd k8s-manifests\dynamodb-local
notepad dynamodb-deployment.yaml
```

**Add this content to the newly created file:**
```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dynamodb-local
  labels:
    app: dynamodb-local
spec:
  replicas: 1
  selector:
    matchLabels:
      app: dynamodb-local
  template:
    metadata:
      labels:
        app: dynamodb-local
    spec:
      containers:
      - name: dynamodb-local
        image: amazon/dynamodb-local:latest
        ports:
        - containerPort: 8000
          name: dynamodb
        command: 
          - "java"
          - "-jar"
          - "DynamoDBLocal.jar"
          - "-sharedDb"
          - "-inMemory"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

**What is all of this?**
* Creates 1 DynamoDB pod 
* Uses amazon/dynamodb-local image 
* Exposes port 8000 
* Runs in-memory (data doesn't persist)
* Sets resource limits (good K8s practice)

### **2.2 Create the DynamoDB Service with the `dynamodb-service.yaml` file:** 
```
notepad dynamodb-service.yaml
```

**And then add the following content to that file:**
```
apiVersion: v1
kind: Service
metadata:
  name: dynamodb-local
  labels:
    app: dynamodb-local
spec:
  selector:
    app: dynamodb-local
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
    name: dynamodb
  type: ClusterIP
```

**What does this do?**
* Creates internal Service (ClusterIP)
* DNS name: `dynamodb-local` (other pods use this)
* Routes traffic to DynamoDB pod on port 8000


### **2.3 Deploy DynamoDB to K8s**  

**Check that Minikube is running:**
```
minikube status
```

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/minikube%20check%20and%20restart.png)

**Restart Minikube if needed:**
```
minikube start --driver=docker
```

**Then deploy DynamoDB:**
```
# From dynamodb-local folder
kubectl apply -f dynamodb-deployment.yaml
kubectl apply -f dynamodb-service.yaml
```

**Expected Output:**
```
deployment.apps/dynamodb-local created
service/dynamodb-local created
```

**Output:**

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/kubectl%20apply.png)

### **2.4 Check that DynamoDb is running:**
```
# Check deployment
kubectl get deployments

# Check pods
kubectl get pods

# Check service
kubectl get services
```

**Output:**
![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/kubectl%20checks.png)

**The pod shows Running which means that DynamoDB is ready!**

## **2.5 Then create the Database Tables in the K8s DynamoDB pod:**

**Create the `setup-db-job.yaml` file - a Kubernetes Job to create the wallets and transactions tables:**
```=
notepad setup-db-job.yaml
```

**And add the following to it:**
```
apiVersion: batch/v1
kind: Job
metadata:
  name: setup-dynamodb-tables
spec:
  template:
    spec:
      containers:
      - name: setup-db
        image: amazon/aws-cli:latest
        command:
        - /bin/sh
        - -c
        - |
          # Wait for DynamoDB to be ready
          sleep 5
          
          # Create wallets table
          aws dynamodb create-table \
            --table-name wallets \
            --attribute-definitions AttributeName=wallet_id,AttributeType=S \
            --key-schema AttributeName=wallet_id,KeyType=HASH \
            --billing-mode PAY_PER_REQUEST \
            --endpoint-url http://dynamodb-local:8000 \
            --region us-east-1 || true
          
          # Create transactions table
          aws dynamodb create-table \
            --table-name transactions \
            --attribute-definitions AttributeName=transaction_id,AttributeType=S \
            --key-schema AttributeName=transaction_id,KeyType=HASH \
            --billing-mode PAY_PER_REQUEST \
            --endpoint-url http://dynamodb-local:8000 \
            --region us-east-1 || true
          
          echo "Tables created successfully"
        env:
        - name: AWS_ACCESS_KEY_ID
          value: "dummy"
        - name: AWS_SECRET_ACCESS_KEY
          value: "dummy"
      restartPolicy: Never
  backoffLimit: 3
```

**Deploy the job:**
```
kubectl apply -f setup-db-job.yaml
```

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/deploy%20table%20job.png)

**Check job status:**
```
kubectl get jobs
```
![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/get%20jobs.png)

**Check the logs:**
```
kubectl logs job/setup-dynamodb-tables
```

**Expected output in logs:**
```
Tables created successfully
```

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/check%20logs%201.png)

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/check%20logs%202.png)

**DynamoDB is ready with tables!**

---

## Step 3: Load the Wallet Service image into Minikube  
**Minikube has its own Docker registry, so I need to build the image inside Minikube's environment.**  

## **3.1 First, point the Docker CLI to Minikube's Docker daemon:**
```
# Run this command
minikube docker-env | Invoke-Expression
# This makes Docker commands run inside Minikube
```

**3.2 Build the image inside Minikube:**
```
# Build image
docker build -t wallet-service:v1 .
```

### Error:
**Caused because I'm trying to build the Docker image from the wrong directory.**

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/Docker%20error.png)

**The command needs to be run in the same directory that the Dockerfile is in.**

### Solution:
**Navigate to where the Dockerfile is located and run the command again.**
```
# Navigate to wallet-service code directory
cd C:\Users\DevOps\Desktop\kubernetes-devops-journey\week2-microservices\wallet-service
```

### Result:

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/docker%20build%20working.png)

**3.3 Check that the image is in Minikube:**
```
docker images | Select-String wallet-service
```

**Expected Output:**
```
wallet-service   v1   ...
```

### Output:
![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/verify%20image%20is%20in%20minikube.png)

**Image is ready in Minikube!**

---

## Step 4: Deploy the Wallet Service to K8s

**4.1 First, navigate to the wallet-service folder and create ConfigMap for configuration:**
```
cd C:\Users\YourUsername\kubernetes-devops-journey\week3-kubernetes-deployment\k8s-manifests\wallet-service
notepad wallet-configmap.yaml
```

**Add this to it:**
```
apiVersion: v1
kind: ConfigMap
metadata:
  name: wallet-config
data:
  DYNAMODB_ENDPOINT: "http://dynamodb-local:8000"
  AWS_REGION: "us-east-1"
  WALLETS_TABLE_NAME: "wallets"
  TRANSACTIONS_TABLE_NAME: "transactions"
```

**What is this?**
* Stores configuration separately from code 
* Wallet pods will read these environment variables
* Easy to change without rebuilding image

**Deploy it:**
```
kubectl apply -f wallet-configmap.yaml
```

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/wallet-config%20deploy.png)

**4.2 Next create the Wallet Service Deployment by creating the `wallet-deployment.yaml` file:**
```
notepad wallet-deployment.yaml
```

**And add this to it:**
```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: wallet-service
  labels:
    app: wallet-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: wallet-service
  template:
    metadata:
      labels:
        app: wallet-service
    spec:
      containers:
      - name: wallet-service
        image: wallet-service:v1
        imagePullPolicy: Never
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: DYNAMODB_ENDPOINT
          valueFrom:
            configMapKeyRef:
              name: wallet-config
              key: DYNAMODB_ENDPOINT
        - name: AWS_REGION
          valueFrom:
            configMapKeyRef:
              name: wallet-config
              key: AWS_REGION
        - name: WALLETS_TABLE_NAME
          valueFrom:
            configMapKeyRef:
              name: wallet-config
              key: WALLETS_TABLE_NAME
        - name: TRANSACTIONS_TABLE_NAME
          valueFrom:
            configMapKeyRef:
              name: wallet-config
              key: TRANSACTIONS_TABLE_NAME
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
```

**What is this?**
* Creates 2 replicas (2 wallet service pods) for high availability
* Uses wallet-service:v1 image from Minikube 
* imagePullPolicy: Never (uses local image from Minikube)
* Reads environment variables from ConfigMap 
* Health checks:
  * Liveness probe: Kubernetes restarts pod if unhealthy 
  * Readiness probe: Kubernetes routes traffic only to ready pods
* Resource limits for efficient scheduling


**Deploy it:**
```
kubectl apply -f wallet-deployment.yaml
```

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/wallet-deployment%20created.png)

**4.3 Next, create the Wallet Service (for load balancing) by creating the following file:**
```
notepad wallet-service.yaml
```

**And adding this to it:**
```
apiVersion: v1
kind: Service
metadata:
  name: wallet-service
  labels:
    app: wallet-service
spec:
  selector:
    app: wallet-service
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
    name: http
  type: ClusterIP
```

**What this does:**
* Creates Service named `wallet-service`
* Load balances across 2 pods
* Port 80 (service) → Port 8000 (pods)
* ClusterIP = internal only (Ingress will expose externally)

**Deploy it:**
```
kubectl apply -f wallet-service.yaml
```

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/wallet-deployment%20created.png)

**4.4 Check that the wallet service is running:**
```
# Check deployment
kubectl get deployments

# Check pods
kubectl get pods

# Check services
kubectl get services
```

**Expected Output:**
```
NAME             READY   UP-TO-DATE   AVAILABLE   AGE
wallet-service   2/2     2            2           1m

NAME                              READY   STATUS    RESTARTS   AGE
wallet-service-xxxxxxxxxx-xxxxx   1/1     Running   0          1m
wallet-service-xxxxxxxxxx-yyyyy   1/1     Running   0          1m

NAME             TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
wallet-service   ClusterIP   10.96.234.56    <none>        80/TCP    1m
```

**Result:**

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/check%20wallet-service%20is%20running.png)

**wallet-service is 2/2 READY and both pods are Running = Success!**

---

## Step 5: Test internal connectivity (test that the wallet-service can reach DynamoDB)

**5.1 First, create a test pod:**

```
kubectl run test-pod --image=curlimages/curl:latest --rm -it -- sh
```

**This opens a shell inside a temporary pod.**

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/create%20test%20pod.png)

**Inside the pod, run:**
```
# Test DynamoDB is accessible
curl http://dynamodb-local:8000

# Test wallet service is accessible
curl http://wallet-service/health
```

**Expected output:**
```
# DynamoDB: Some error message (that's OK, it's running!)
# Wallet service: {"status":"healthy","service":"wallet-service"}
```

**Output:**

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/test%20pod.png)

**Getting the health response means that the connectivity works!**

**5.2 Next, check the wallet service logs:**
```
# Get pod names
kubectl get pods

# Check logs from one pod
kubectl logs <wallet-service-pod-name>
```

**Expected Output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Output:**

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/wallet%20service%20logs.png)

**Wallet service is running!**

---

## Step 6: Add Ingress to make wallet-service accessible from outside the cluster

**6.1 First, enable the Ingress addon in Minikube:**

```
minikube addons enable ingress
```

**Expected output:**
```
ingress is now enabled
```

**Output:**

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/enable%20ingress%20addon.png)


**Check the ingress-nginx-controller pod:**
```
kubectl get pods -n ingress-nginx
```

### Wait until you see:
```
NAME                                        READY   STATUS    RESTARTS   AGE
ingress-nginx-controller-xxxxxxxxxx-xxxxx   1/1     Running   0          1m
```

**Result:**

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/check%20ingress%20pod.png)


**6.2 Next, Create Ingress resource by creating the following file:**

```
notepad wallet-ingress.yaml
```

**And adding this content to it:**

```
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: wallet-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: wallet-service
            port:
              number: 80
```

**What does this do?**
* Creates external access point 
* Routes all traffic to wallet-service 
* Path / → wallet-service

**Now deploy it:**
```
kubectl apply -f wallet-ingress.yaml
```

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/deploy%20wallet-ingress.png)

**6.3 And get the Ingress URL:**
```
minikube service wallet-service --url
```
![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/minikube%20ip.png)

URL: http://127.0.0.1:54792

---

## Step 7: Test the Deployed Service

**7.1 Access the Swagger UI in the browser using the Minikube IP**  

**Result:**

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/test%20swagger%20ui.png)

**7.2 Now, create a test wallet:**
In Swagger UI:
* Click POST /wallets/
* Click "Try it out"
* Request body:
```
{
  "user_id": "k8s-test-user",
  "currency": "USD",
  "initial_balance": 500.00
}
```
* Click "Execute"

**Expected: 201 Created with wallet_id**

**Result:**

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/test%20create%20wallet.png)


**7.3 Test all the endpoints:**

**GET wallet:**
Use wallet_id from previous response

**Expected: 200 OK**

**Result:**

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/test%20get%20wallet.png)

**Credit wallet:**
Amount: 100.00
```
{
  "amount": 100,
  "description": "Credit",
  "reference_id": "string"
}
```

**Expected: 200 OK, balance = 600.00**

**Result:**

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/test%20credit%20wallet.png)

**Get transactions:**

**Expected: List with 1 transaction (CREDIT, 100.00)**

**Result:**

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/get%20transactions%20test.png)

**These tests all worked! The Microservice is running ion K8s!**

**Verify Complete Cluster State:**
```
kubectl get all
```
![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/kubectl%20get%20all.png)

**Result:**
* 2 wallet-service pods: Running ✅ 
* 1 dynamodb-local pod: Running ✅
* All services: Healthy ✅
* deployments: 2/2 or 1/1 READY ✅ 
* Job: Completed ✅

---

### What I Learned  

**Kubernetes Concepts**  
- **Deployments:** Manage pods, replicas, and rolling updates  
- **Services:** Provide stable endpoints and load balancing  
- **ConfigMaps:** Separate configuration from code  
- **Ingress:** External routing and access control  
- **Jobs:** Run-to-completion tasks (like database setup)  
- **Health Checks:** Liveness and readiness probes for self-healing  
- **Resource Limits:** CPU/memory requests and limits for scheduling    

**Production Patterns**  
- **High Availability:** 2 replicas ensure service remains available if 1 pod fails  
- **Service Discovery:** Pods find each other using DNS (dynamodb-local:8000)  
- **Load Balancing:** Kubernetes Service distributes traffic across pods  
- **12-Factor Apps:** Configuration via environment variables (ConfigMap)  
- **Self-Healing:** Health checks trigger automatic pod restarts  
- **Resource Management:** Limits prevent pods from consuming excessive resources    

**Troubleshooting**  
- **Port Conflicts:** Understood Docker vs Kubernetes networking  
- **Image Loading:** Learned Minikube has separate Docker registry  
- **Directory Navigation:** Built Docker image from correct location (week2-microservices)  
- **Service Communication:** Verified inter-pod connectivity before external access  

**DevOps Skills**  
- **Infrastructure as Code:** All infrastructure defined in YAML  
- **Declarative Configuration:** Kubernetes reconciles desired state  
- **Container Orchestration:** Automated deployment, scaling, and management  
- **Observability:** Logs, health checks, and cluster state inspection  

---

### Key Achievements  
✅ Deployed multi-container application to Kubernetes  
✅ Implemented high availability with 2 replicas  
✅ Configured service discovery for inter-pod communication  
✅ Set up load balancing across multiple pods  
✅ Used ConfigMaps for configuration management  
✅ Implemented health checks (liveness/readiness probes)  
✅ Set resource limits (CPU/memory)  
✅ Configured Ingress for external access  
✅ Created database tables via Kubernetes Job  
✅ Tested end-to-end functionality (all endpoints working)  
✅ Documented entire process with screenshots  

---

### Technologies Used  

**Container Orchestration:**  
- Kubernetes (Minikube)  
- kubectl  
- Docker  

**Application Stack:**  
- FastAPI (Python web framework)  
- DynamoDB Local (database)  
- Pydantic (data validation)  

**Infrastructure:**  
- ConfigMaps (configuration)  
- Services (networking)  
- Deployments (pod management)  
- Ingress (external access)  
- Jobs (initialization tasks)  

**Tooling:**  
- YAML (infrastructure definitions)  
- Bash/PowerShell (automation)  
- Git (version control)  

---

### Next Steps  
**Completed:**  
✅ Week 1: Kubernetes fundamentals  
✅ Week 2: Build FastAPI microservice  
✅ Week 3: Deploy to Kubernetes with HA 

**Coming Next:**  
🚧 Week 4: Observability (Prometheus + Grafana)  
🚧 Week 5: CI/CD pipelines (GitHub Actions → K8s)  
🚧 Week 6: Advanced patterns (blue-green deployments, GitOps)  

---

### Portfolio Value  
This project demonstrates:  

**For DevOps Engineer Roles:**  
- Container orchestration expertise  
- Production-grade Kubernetes deployments  
- Infrastructure as Code practices  
- Service discovery and networking  
- High availability patterns  
- Configuration management  
- Resource optimization  

**For Cloud Engineer Roles:**  
- Cloud-native architecture  
- Microservice deployment  
- Load balancing and scaling  
- Infrastructure automation  
- Monitoring and health checks  

**For Software Engineer Roles:**  
- Full-stack application development  
- RESTful API design  
- Database integration  
- Containerization  
- Production deployment experience  
