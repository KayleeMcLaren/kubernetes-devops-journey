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

Create the Pydantic Models by adding this to the `app/models.py`:

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

## Step 3: Create Database Layer

### Next create DynamoDB helper functions. Add the following to the `app/db.py` file:

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

This code creates the connection to the DynamoDB table (in the case of this project, that'll be local but it can also connect to AWS).  
It creates functions to handle CRUD operations on the `wallets_table` and creates transaction records in the `transaction_logs` table.


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
