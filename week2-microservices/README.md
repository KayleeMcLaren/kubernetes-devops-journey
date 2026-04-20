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

## Step 2: Define Models

## Step 3: Create Database Layer

## Testing

### Create Wallet

### Get Transactions

## Key Learnings
- Lambda handlers vs web framework routes
- Pydantic for data validation
- FastAPI auto-generates API docs
- DynamoDB Local for development

## Next Steps
- Containerize with Docker
- Deploy to Kubernetes
- Add service-to-service communication
