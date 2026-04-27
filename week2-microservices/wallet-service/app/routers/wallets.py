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
