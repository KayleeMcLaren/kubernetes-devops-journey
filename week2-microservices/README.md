# Week 2: Building Microservices

## Objective
Convert AWS Lambda functions from my Serverless Fintech Ecosystem into a 
containerized FastAPI microservice.

### What I Built
A production-grade Wallet Service microservice with:
- 5 RESTful API endpoints
- DynamoDB Local integration
- Transaction logging
- Auto-generated API documentation

### Architecture

**Before (AWS Serverless):**
```
API Gateway → 5 separate Lambda functions → DynamoDB
```

**After (Microservice):**
```
FastAPI app → 5 routes in single service → DynamoDB Local
```

## Build FastAPI Service

## **Step 1: Project Structure**

### Convert this:

```
5 separate Lambda functions:
├── get_wallet/handler.py
├── create_wallet/handler.py
├── credit_wallet/handler.py
├── debit_wallet/handler.py
└── get_wallet_transactions/handler.py
```

### Into this:

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


### Create the necessary project empty files:

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

**Not going to include a screenshot of the command line out put because it's very long.**  
**Instead I'm going to verify the structure of the wallet-service folder using this command:**

```
tree /F
```

### And the result is:

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/verify%20structure.png)

### Perfect!

## Step 2: Define the necessary dependencies in the requirements.txt file by adding the following to it

```
fastapi==0.115.0
uvicorn[standard]==0.32.0
boto3==1.35.0
pydantic==2.9.0
python-dotenv==1.0.1
```

### What are these things?
* fastapi - Web framework
* uvicorn - ASGI server (runs FastAPI)
* boto3 - AWS SDK (for DynamoDB)
* pydantic - Data validation
* python-dotenv - Load environment variables

---

## Step 3: Define the Data Models with Pydantic Models by adding this to the `app/models.py`

```
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime

class WalletCreate(BaseModel):
    """Request model for creating a wallet"""
    user_id: str
    currency: str = "USD"
    initial_balance: Decimal = Decimal("0.00")

class WalletResponse(BaseModel):
    """Response model for wallet data"""
    wallet_id: str
    user_id: str
    balance: Decimal
    currency: str
    created_at: str
    updated_at: str

class CreditRequest(BaseModel):
    """Request model for crediting a wallet"""
    amount: Decimal = Field(..., gt=0, description="Amount must be positive")
    description: Optional[str] = "Credit"
    reference_id: Optional[str] = None

class DebitRequest(BaseModel):
    """Request model for debiting a wallet"""
    amount: Decimal = Field(..., gt=0, description="Amount must be positive")
    description: Optional[str] = "Debit"
    reference_id: Optional[str] = None

class TransactionResponse(BaseModel):
    """Response model for transaction data"""
    transaction_id: str
    wallet_id: str
    transaction_type: str  # CREDIT, DEBIT
    amount: Decimal
    balance_after: Decimal
    description: str
    reference_id: Optional[str] = None
    created_at: str

class SuccessResponse(BaseModel):
    """Generic success response"""
    message: str
    wallet_id: str
    balance: Decimal
```

## Step 4: Create Database Layer with DynamoDB helper functions. Add the following to the `app/db.py` file

```
import boto3
import os
import uuid
from decimal import Decimal
from datetime import datetime
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

# Configuration
DYNAMODB_ENDPOINT = os.environ.get('DYNAMODB_ENDPOINT', 'http://localhost:8000')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
WALLETS_TABLE = os.environ.get('WALLETS_TABLE_NAME', 'wallets')
TRANSACTIONS_TABLE = os.environ.get('TRANSACTIONS_TABLE_NAME', 'transactions')

# Initialize DynamoDB
dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url=DYNAMODB_ENDPOINT,
    region_name=AWS_REGION,
    aws_access_key_id='dummy',      # DynamoDB Local doesn't validate
    aws_secret_access_key='dummy'   # DynamoDB Local doesn't validate
)

wallets_table = dynamodb.Table(WALLETS_TABLE)
transactions_table = dynamodb.Table(TRANSACTIONS_TABLE)

# Helper functions

def get_wallet(wallet_id: str):
    """Retrieve wallet by ID"""
    try:
        response = wallets_table.get_item(Key={'wallet_id': wallet_id})
        return response.get('Item')
    except ClientError as e:
        logger.error(f"Error getting wallet {wallet_id}: {e}")
        raise

def create_wallet(user_id: str, currency: str = "USD", initial_balance: Decimal = Decimal("0.00")):
    """Create a new wallet"""
    wallet_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    
    wallet = {
        'wallet_id': wallet_id,
        'user_id': user_id,
        'balance': initial_balance,
        'currency': currency,
        'created_at': now,
        'updated_at': now
    }
    
    try:
        wallets_table.put_item(Item=wallet)
        return wallet
    except ClientError as e:
        logger.error(f"Error creating wallet: {e}")
        raise

def update_wallet_balance(wallet_id: str, amount: Decimal, operation: str):
    """
    Update wallet balance
    operation: 'add' or 'subtract'
    """
    try:
        # Get current wallet
        wallet = get_wallet(wallet_id)
        if not wallet:
            return None
        
        current_balance = Decimal(str(wallet['balance']))
        
        # Calculate new balance
        if operation == 'add':
            new_balance = current_balance + amount
        elif operation == 'subtract':
            new_balance = current_balance - amount
            if new_balance < 0:
                raise ValueError("Insufficient funds")
        else:
            raise ValueError(f"Invalid operation: {operation}")
        
        # Update wallet
        now = datetime.utcnow().isoformat()
        response = wallets_table.update_item(
            Key={'wallet_id': wallet_id},
            UpdateExpression='SET balance = :balance, updated_at = :updated_at',
            ExpressionAttributeValues={
                ':balance': new_balance,
                ':updated_at': now
            },
            ReturnValues='ALL_NEW'
        )
        
        return response['Attributes']
    except ClientError as e:
        logger.error(f"Error updating wallet balance: {e}")
        raise

def create_transaction(
    wallet_id: str,
    transaction_type: str,
    amount: Decimal,
    balance_after: Decimal,
    description: str,
    reference_id: str = None
):
    """Create a transaction record"""
    transaction_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    
    transaction = {
        'transaction_id': transaction_id,
        'wallet_id': wallet_id,
        'transaction_type': transaction_type,
        'amount': amount,
        'balance_after': balance_after,
        'description': description,
        'reference_id': reference_id,
        'created_at': now
    }
    
    try:
        transactions_table.put_item(Item=transaction)
        return transaction
    except ClientError as e:
        logger.error(f"Error creating transaction: {e}")
        raise

def get_wallet_transactions(wallet_id: str, limit: int = 50):
    """Get transactions for a wallet"""
    try:
        # Query by wallet_id (requires GSI in production, but for local we'll scan)
        response = transactions_table.scan(
            FilterExpression='wallet_id = :wallet_id',
            ExpressionAttributeValues={':wallet_id': wallet_id},
            Limit=limit
        )
        
        # Sort by created_at descending
        items = response.get('Items', [])
        items.sort(key=lambda x: x['created_at'], reverse=True)
        
        return items
    except ClientError as e:
        logger.error(f"Error getting transactions: {e}")
        raise
```

**This code creates the connection to the DynamoDB table (in the case of this project, that'll be local but it can also connect to AWS).**  
**It creates functions to handle CRUD operations on the `wallets_table` with balance update validation and it creates transaction records in the `transaction_logs` table.**

---

## Step 5: Create the wallet API routes by adding this to the `app/routers/wallets.py` file

```
from fastapi import APIRouter, HTTPException, status
from app.models import (
    WalletCreate,
    WalletResponse,
    CreditRequest,
    DebitRequest,
    TransactionResponse,
    SuccessResponse
)
from app.db import (
    get_wallet,
    create_wallet as create_wallet_db,
    update_wallet_balance,
    create_transaction,
    get_wallet_transactions as get_transactions_db
)
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=WalletResponse, status_code=status.HTTP_201_CREATED)
async def create_wallet(wallet_data: WalletCreate):
    """Create a new wallet"""
    try:
        wallet = create_wallet_db(
            user_id=wallet_data.user_id,
            currency=wallet_data.currency,
            initial_balance=wallet_data.initial_balance
        )
        
        # Convert Decimal to float for response (Pydantic handles this)
        return WalletResponse(**wallet)
    except Exception as e:
        logger.error(f"Error creating wallet: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create wallet"
        )

@router.get("/{wallet_id}", response_model=WalletResponse)
async def get_wallet_by_id(wallet_id: str):
    """Get wallet by ID"""
    wallet = get_wallet(wallet_id)
    
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wallet {wallet_id} not found"
        )
    
    return WalletResponse(**wallet)

@router.post("/{wallet_id}/credit", response_model=SuccessResponse)
async def credit_wallet(wallet_id: str, credit_data: CreditRequest):
    """Add funds to wallet"""
    # Check wallet exists
    wallet = get_wallet(wallet_id)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wallet {wallet_id} not found"
        )
    
    try:
        # Update balance
        updated_wallet = update_wallet_balance(
            wallet_id=wallet_id,
            amount=credit_data.amount,
            operation='add'
        )
        
        # Create transaction record
        create_transaction(
            wallet_id=wallet_id,
            transaction_type='CREDIT',
            amount=credit_data.amount,
            balance_after=updated_wallet['balance'],
            description=credit_data.description,
            reference_id=credit_data.reference_id
        )
        
        return SuccessResponse(
            message="Wallet credited successfully",
            wallet_id=wallet_id,
            balance=updated_wallet['balance']
        )
    except Exception as e:
        logger.error(f"Error crediting wallet: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to credit wallet"
        )

@router.post("/{wallet_id}/debit", response_model=SuccessResponse)
async def debit_wallet(wallet_id: str, debit_data: DebitRequest):
    """Remove funds from wallet"""
    # Check wallet exists
    wallet = get_wallet(wallet_id)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wallet {wallet_id} not found"
        )
    
    try:
        # Update balance
        updated_wallet = update_wallet_balance(
            wallet_id=wallet_id,
            amount=debit_data.amount,
            operation='subtract'
        )
        
        # Create transaction record
        create_transaction(
            wallet_id=wallet_id,
            transaction_type='DEBIT',
            amount=debit_data.amount,
            balance_after=updated_wallet['balance'],
            description=debit_data.description,
            reference_id=debit_data.reference_id
        )
        
        return SuccessResponse(
            message="Wallet debited successfully",
            wallet_id=wallet_id,
            balance=updated_wallet['balance']
        )
    except ValueError as e:
        # Insufficient funds
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error debiting wallet: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to debit wallet"
        )

@router.get("/{wallet_id}/transactions", response_model=list[TransactionResponse])
async def get_wallet_transactions(wallet_id: str, limit: int = 50):
    """Get transaction history for wallet"""
    # Check wallet exists
    wallet = get_wallet(wallet_id)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wallet {wallet_id} not found"
        )
    
    try:
        transactions = get_transactions_db(wallet_id, limit)
        return [TransactionResponse(**tx) for tx in transactions]
    except Exception as e:
        logger.error(f"Error getting transactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transactions"
        )
```

**This defines all 5 endpoints and requests validation from Pydantic.**

## Step 6: Create the main app with the following code in the `app/main.py` file

```
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import wallets
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Wallet Service",
    description="Microservice for managing digital wallets",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(wallets.router, prefix="/wallets", tags=["wallets"])

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for K8s liveness/readiness probes"""
    return {
        "status": "healthy",
        "service": "wallet-service"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Wallet Service API",
        "version": "1.0.0",
        "docs": "/docs"
    }
```

**This code creates FastAPI application, adds Cross-Origin Resource Sharing (CORS) for frontend access, includes the wallet routes, a health check endpoint (for K8s probes) at `/health`, and creates auto-generated docs at a `/docs` endpoint.**

## Step 7: Create the Dockerfile

### Add this to the `Dockerfile `:

```
# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for Docker layer caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Create the `.dockerignore` file with this:

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv
*.log
.git
.gitignore
README.md
.DS_Store
```

## Step 8: Create the database setup script by adding this to the `setup_db.py` file

```
import boto3
import time
import os

DYNAMODB_ENDPOINT = os.environ.get('DYNAMODB_ENDPOINT', 'http://localhost:8000')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url=DYNAMODB_ENDPOINT,
    region_name=AWS_REGION,
    aws_access_key_id='dummy',
    aws_secret_access_key='dummy'
)

def create_wallets_table():
    """Create wallets table"""
    try:
        table = dynamodb.create_table(
            TableName='wallets',
            KeySchema=[
                {'AttributeName': 'wallet_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'wallet_id', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print("✅ Created 'wallets' table")
        return table
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        print("ℹ️  'wallets' table already exists")
        return dynamodb.Table('wallets')

def create_transactions_table():
    """Create transactions table"""
    try:
        table = dynamodb.create_table(
            TableName='transactions',
            KeySchema=[
                {'AttributeName': 'transaction_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'transaction_id', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print("✅ Created 'transactions' table")
        return table
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        print("ℹ️  'transactions' table already exists")
        return dynamodb.Table('transactions')

if __name__ == "__main__":
    print("🗄️  Setting up DynamoDB tables...")
    print(f"📍 Endpoint: {DYNAMODB_ENDPOINT}")
    
    create_wallets_table()
    create_transactions_table()
    
    print("\n✅ Database setup complete!")
    print("\nTables created:")
    print("  - wallets")
    print("  - transactions")
```

## Step 9: Test everything locally

### First start DynamoDB Local:

*Note: Remember to restart minikube!*

```
# Run DynamoDB Local in Docker
docker run -d -p 8000:8000 --name dynamodb-local amazon/dynamodb-local
```

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/remember%20to%20restart%20minikube.png)

### Verify that Docker is running - should see dynamodb-local running

```
docker ps
```

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/verify%20dynamodb-local.png)

### Install Python dependencies locally

```
# In wallet-service directory
pip install -r requirements.txt
```

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/install%20requirements.png)


###  Create the database tables

```
# Set environment variable
$env:DYNAMODB_ENDPOINT="http://localhost:8000"

# Run setup script
python setup_db.py
```

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/db%20setup.png)

### Run the FastAPI app

```
# Run app
uvicorn app.main:app --reload
```

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/main%20app.png)

### Open browser to: http://127.0.0.1:8000/docs to see the auto-generated documentation (this is Swagger UI from FastAPI) 

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/swagger%20UI.png)


### Test 1: Create a wallet
* Click on POST /wallets/
* Click "Try it out"
* Enter request body:
```
json{
  "user_id": "user123",
  "currency": "USD",
  "initial_balance": 100.00
}
```
* Click "Execute"

### Expected response: 201 Created with wallet_id

### Response:

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/create-wallet.png)

### Test 2: Get wallet
* Copy the wallet_id from response
* Click on GET /wallets/{wallet_id}
* Click "Try it out"
* Paste wallet_id
* Click "Execute"

### Expected response: 200 OK with wallet details

### Response:

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/get%20wallet.png)

### Test 3: Credit wallet
* Click on POST /wallets/{wallet_id}/credit
* Click "Try it out"
* Enter wallet_id and:
```
json{
  "amount": 50.00,
  "description": "Test credit"
}
```
* Click "Execute"

### Expected response: 200 OK, balance should be 150.00

### Response:

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/credit.png)

### Test 4: Get transactions
* Click on GET /wallets/{wallet_id}/transactions
* Click "Try it out"
* Enter wallet_id
* Click "Execute"

### Expected response: 200 OK with list of transactions

### Response:

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/get%20transactions.png)

## Step 10: Containerize the service

### Stop the local uvicorn server

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/shut%20down.png)

### Build the Docker image

```
# In wallet-service directory
docker build -t wallet-service:v1 .
```
### Expected Output:
```
[+] Building 25.3s (10/10) FINISHED
 => [internal] load build definition from Dockerfile
 => [internal] load .dockerignore
 => [1/5] FROM docker.io/library/python:3.12-slim
 => [2/5] WORKDIR /app
 => [3/5] COPY requirements.txt .
 => [4/5] RUN pip install --no-cache-dir -r requirements.txt
 => [5/5] COPY app/ ./app/
 => exporting to image
 => => naming to docker.io/library/wallet-service:v1
```

### Output:

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/docker%20build.png)

## Verify that the image was created

```
docker images | Select-String wallet-service
```

### Expected output:
```
wallet-service   v1      abc123def456   2 minutes ago   180MB
```

### Output:

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/verify%20docker%20image.png)

## Stepp 11: Run the wallet service container

```
docker run -d `
  --name wallet-service `
  -p 8000:8000 `
  -e DYNAMODB_ENDPOINT=http://host.docker.internal:8000 `
  wallet-service:v1
```

### What this does:

* -d = run in background (detached)
* --name wallet-service = give it a name
* -p 8000:8000 = map port 8000 (container) to 8000 (host)
* -e DYNAMODB_ENDPOINT=... = set environment variable  
    * host.docker.internal = Docker's way to access host machine
* wallet-service:v1 = the image to run

### Error:

**Port 8000 is already being used by the  DynamoDB Local container**

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/docker%20run%20error.png)

### Solution:

### Stop and remove the failed container first

```
docker rm wallet-service
```

### Run wallet-service on port 8001

```
docker run -d `
  --name wallet-service `
  -p 8001:8000 `
  -e DYNAMODB_ENDPOINT=http://host.docker.internal:8000 `
  wallet-service:v1
```

###  Check both containers are running

```
docker ps
```

### Result:

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/docker%20solution.png)

### What changed?
* -p 8001:8000 instead of -p 8000:8000
    * 8001 = port on the host machine (Windows)
    * 8000 = port inside the container (FastAPI still runs on 8000)

Now access your service at: http://127.0.0.1:8001/docs

### Port Mapping
Docker port mapping syntax: `-p HOST_PORT:CONTAINER_PORT`

```
-p 8001:8000
   ↑     ↑
   |     └─ Port 8000 inside container (FastAPI listening)
   └─ Port 8001 on your Windows machine (what you access in browser)
```

My setup:
```
Your Browser (Windows)
    ↓
localhost:8001  ← Access wallet service here
    ↓
Docker Host
    ↓
wallet-service container (port 8000 internally)
```

And:

```
Wallet Service Container
    ↓
host.docker.internal:8000  ← DynamoDB Local
    ↓
Docker Host
    ↓
dynamodb-local container (port 8000 internally)
```

### Test the wallet service
Open browser: http://127.0.0.1:8001/docs to see the Swagger UI

### Create a wallet to verify database connection
* POST /wallets/
* Request body:
```
json{
  "user_id": "docker-test",
  "currency": "USD",
  "initial_balance": 200.00
}
```

### Expect to get 201 Created response

### Response:

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/docker%20test%20wallet.png)

### Success!

## Step 12: Clean Up

### Check container logs

```
docker logs wallet-service
```

### Stop containers
```
docker stop wallet-service
docker stop dynamodb-local
```

### Remove containers
```
docker rm wallet-service
docker rm dynamodb-local
```

### But don't delete the images!

![alt text](https://github.com/KayleeMcLaren/kubernetes-devops-journey/blob/main/images/docker%20clean%20up.png)

## Next Steps:
✅ Deploy DynamoDB Local to K8s  
✅ Deploy wallet-service to K8s  
✅ Create K8s manifests (Deployments, Services, ConfigMaps)  
✅ Test everything works in K8s  
✅ Add Ingress for external access
