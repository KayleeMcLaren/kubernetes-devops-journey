# Kubernetes DevOps Journey

![Kubernetes](https://img.shields.io/badge/kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)
![Docker](https://img.shields.io/badge/docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Learning](https://img.shields.io/badge/Status-In%20Progress-yellow?style=for-the-badge)

> **A hands-on, documented journey from Cloud Engineer to DevOps/SRE Engineer**
---

## 🗓️ Learning Timeline

### Week 1: Kubernetes Fundamentals ✅ COMPLETE
- Set up local K8s cluster with Minikube
- Deployed first application (nginx)
- Learned pods, deployments, services, replica sets
- Explored self-healing, scaling, and rolling updates
- **[Detailed documentation →](week1-kubernetes-basics/README.md)**

### Key Learnings:
- Kubernetes architecture (pods, nodes, control plane)
- YAML manifest structure
- kubectl commands and cluster management
- Container orchestration fundamentals
- Self-healing and declarative configuration

**Skills Gained:** kubectl, YAML manifests, container orchestration basics

### Week 2: Building Microservices ✅ COMPLETE
- Converted 5 AWS Lambda functions to unified FastAPI microservice
- Integrated with DynamoDB Local for development
- Built production-grade wallet service with transaction logging
- Containerized application with Docker
- Debugged port conflicts and container networking
- **[Detailed documentation →](week2-microservices/README.md)**

### Key Learnings:
- FastAPI framework and RESTful API design
- Pydantic data validation
- Docker containerization and multi-container apps
- Port mapping and container networking
- DynamoDB integration
- Troubleshooting and debugging

**Skills Gained:** FastAPI, Pydantic, Docker, containerization, microservice architecture

---

### Week 3: Kubernetes Deployment ✅ COMPLETE
- Deployed DynamoDB Local to K8s cluster
- Deployed wallet service with high availability (2 replicas)
- Configured service discovery and networking
- Set up load balancing with Kubernetes Service
- Added ConfigMaps for 12-factor app configuration
- Configured Ingress controller for external routing
- Implemented health checks (liveness/readiness probes) and resource limits
- Created database tables via Kubernetes Job
- **[Detailed documentation →](week3-kubernetes-deployment/README.md)**

### Key Learnings:

- Kubernetes Deployments and replica management
- Service discovery via Kubernetes DNS
- Load balancing across multiple pods
- ConfigMaps for configuration management
- Health checks for self-healing
- Resource limits (CPU/memory)
- Ingress controllers for external access
- Jobs for initialization tasks

**Skills Gained:** Kubernetes deployments, services, ConfigMaps, Ingress, health checks, resource management, high availability patterns

---

### Week 4: Observability (🚧 In progress)
**Planned:** Prometheus + Grafana

### What I'll Build:
- Deploy Prometheus for metrics collection
- Set up Grafana for dashboards and visualization
- Create custom metrics for wallet service
- Implement alerting rules
- Monitor cluster and application health

**Skills to Gain:** Prometheus, Grafana, metrics collection, dashboards, alerting

---

## Project Architecture

### Current State (Week 3):

```
┌─────────────────────────────────────────────┐
│      Kubernetes Cluster (Minikube)          │
│                                             │
│  Ingress (nginx)                            │
│      ↓                                      │
│  Service: wallet-service                    │
│      ↓           ↓                          │
│   Pod 1       Pod 2    (2 replicas)         │
│      ↓           ↓                          │
│  Service: dynamodb-local                    │
│      ↓                                      │
│   Pod: dynamodb                             │
└─────────────────────────────────────────────┘
```

### Components:

- **Ingress:** External access and routing
- **Services:** Load balancing and service discovery
- **Pods:** Application containers
- **ConfigMaps:** Configuration management
- **Jobs:** Initialization tasks

---

## Skills Demonstrated
**DevOps**

- ✅ Container orchestration (Kubernetes)
- ✅ Infrastructure as Code (YAML manifests)
- ✅ CI/CD concepts (learning GitHub Actions)
- ✅ Configuration management (ConfigMaps)
- ✅ High availability patterns 
- ✅ Service discovery 
- ✅ Load balancing

**Cloud Engineering**

- ✅ AWS services (Lambda, DynamoDB, S3, etc.)
- ✅ Terraform (2 years production experience)
- ✅ Serverless architectures
- ✅ Cloud-native application design 
- ✅ Microservice patterns

**Software Development**

- ✅ Python (backend services, automation)
- ✅ FastAPI (RESTful APIs)
- ✅ React (dashboards)
- ✅ Git workflows
- ✅ Testing and debugging

**System Administration**

- ✅ Linux command line
- ✅ Container networking
- ✅ Resource management
- ✅ Troubleshooting
- ✅ Log analysis

---

## Repository Structure

```
kubernetes-devops-journey/
│
├── README.md                           # This file
├── images/                             # All screenshots (50+)
│
├── week1-kubernetes-basics/
│   ├── README.md                       # Detailed K8s setup documentation
│   └── k8s-manifests/                  # nginx deployment files
│
├── week2-microservices/
│   ├── README.md                       # FastAPI build documentation
│   └── wallet-service/                 # Complete microservice code
│       ├── app/                        # FastAPI application
│       ├── Dockerfile                  # Container definition
│       └── requirements.txt            # Python dependencies
│
├── week3-kubernetes-deployment/
│   ├── README.md                       # K8s deployment documentation
│   └── k8s-manifests/                  # All Kubernetes YAML files
│       ├── dynamodb-local/             # DynamoDB deployment
│       └── wallet-service/             # Wallet service deployment
│
└── week4-observability/
    └── README.md                       # Coming soon
```

  
