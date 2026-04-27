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