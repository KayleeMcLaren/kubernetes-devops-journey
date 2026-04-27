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