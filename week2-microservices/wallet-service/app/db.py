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
    aws_access_key_id='dummy',  # DynamoDB Local doesn't validate
    aws_secret_access_key='dummy'  # DynamoDB Local doesn't validate
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