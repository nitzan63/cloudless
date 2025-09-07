from fastapi import APIRouter, HTTPException
from services.credit_service import CreditService
from typing import List
from pydantic import BaseModel

router = APIRouter()
credit_service = CreditService()

class SpendCreditsRequest(BaseModel):
    userId: str
    amount: int
    taskId: str
    description: str

class EarnCreditsRequest(BaseModel):
    userId: str
    amount: int
    jobId: str
    description: str

class CreditBalance(BaseModel):
    userId: str
    credits: int
    lastUpdated: str

class CreditTransaction(BaseModel):
    id: str
    userId: str
    amount: int
    type: str  # 'earn' or 'spend'
    description: str
    timestamp: str

@router.post("/spend")
def spend_credits(request: SpendCreditsRequest):
    """Spend credits on a task"""
    try:
        result = credit_service.spend_credits(
            user_id=request.userId,
            amount=request.amount,
            task_id=request.taskId,
            description=request.description
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/earn")
def earn_credits(request: EarnCreditsRequest):
    """Earn credits from processing a job"""
    try:
        result = credit_service.earn_credits(
            user_id=request.userId,
            amount=request.amount,
            job_id=request.jobId,
            description=request.description
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/balance/{user_id}")
def get_credit_balance(user_id: str):
    """Get user's credit balance"""
    try:
        balance = credit_service.get_credit_balance(user_id)
        return balance
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/transactions/{user_id}")
def get_transaction_history(user_id: str):
    """Get user's credit transaction history"""
    try:
        transactions = credit_service.get_transaction_history(user_id)
        return transactions
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
