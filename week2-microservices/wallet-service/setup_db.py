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