# Week 2: Building Microservices

## Goal
Convert AWS Lambda functions from my Serverless Fintech Ecosystem into a 
containerized FastAPI microservice.

## What I Built
A production-grade Wallet Service microservice with:
- 5 RESTful API endpoints
- DynamoDB Local integration
- Transaction logging
- Auto-generated API documentation

## Architecture

**Before (AWS Serverless):**
```
API Gateway → 5 separate Lambda functions → DynamoDB
```

**After (Microservice):**
```
FastAPI app → 5 routes in single service → DynamoDB Local
```

#  Build FastAPI Service

## Step 1: Project Structure

Convert this:

```
5 separate Lambda functions:
├── get_wallet/handler.py
├── create_wallet/handler.py
├── credit_wallet/handler.py
├── debit_wallet/handler.py
└── get_wallet_transactions/handler.py
```

Into this:

```
1 unified FastAPI service:
wallet-service/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app
│   ├── models.py         # Pydantic models
│   ├── db.py             # DynamoDB operations
│   └── routers/
│       └── wallets.py    # All wallet routes
├── Dockerfile
├── requirements.txt
├── setup_db.py           # Create DynamoDB tables
└── README.md
```

### First Create the directory structure
```
# Navigate to where you want to create this
cd C:\Users\YourUsername\

# Create project structure
mkdir wallet-service
cd wallet-service
mkdir app
mkdir app\routers
```

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/create%20new%20folder.png)


## Create the necessary project files:

```
# Create __init__.py files (marks directories as Python packages)
New-Item -Path "app\__init__.py" -ItemType File
New-Item -Path "app\routers\__init__.py" -ItemType File

# Create main files
New-Item -Path "app\main.py" -ItemType File
New-Item -Path "app\models.py" -ItemType File
New-Item -Path "app\db.py" -ItemType File
New-Item -Path "app\routers\wallets.py" -ItemType File
New-Item -Path "setup_db.py" -ItemType File
New-Item -Path "requirements.txt" -ItemType File
New-Item -Path "Dockerfile" -ItemType File
New-Item -Path "README.md" -ItemType File
New-Item -Path ".dockerignore" -ItemType File
```

Not going to include a screenshot of the command line out put because it's very long.  
Instead I'm going to verify the structure of the wallet-service folder using this command:

```
tree /F
```

And the result is:

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/verify%20structure.png)

Perfect!

## Next, define the necessary dependencies in the requirements.txt file by adding the following to it:

```
fastapi==0.115.0
uvicorn[standard]==0.32.0
boto3==1.35.0
pydantic==2.9.0
python-dotenv==1.0.1
```

## What are these things?
* fastapi - Web framework
* uvicorn - ASGI server (runs FastAPI)
* boto3 - AWS SDK (for DynamoDB)
* pydantic - Data validation
* python-dotenv - Load environment variables

---

## Step 2: Define Models

![alt text]()

## Step 3: Create Database Layer

![alt text]()

## Testing

### Create Wallet

![alt text]()

### Get Transactions

![alt text]()

## Key Learnings
- Lambda handlers vs web framework routes
- Pydantic for data validation
- FastAPI auto-generates API docs
- DynamoDB Local for development

## Next Steps
- Containerize with Docker
- Deploy to Kubernetes
- Add service-to-service communication
