from fastapi import APIRouter, Cookie, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import ALGORITHM, SECRET_KEY
from app.database import get_db
from app.models.order import Order
from app.models.user import User
from app.core.dependencies import get_current_user

import jwt


router = APIRouter(
    prefix="/api/transactions",
    tags=["Transactions"],
)


def get_transaction_user(
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
        )

    try:
        payload = jwt.decode(
            access_token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

    user = (
        db.query(User)
        .filter(User.id == int(user_id))
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    return user


@router.get("/")
def get_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    transactions = (
        db.query(Order)
        .filter(Order.user_id == current_user.id)
        .order_by(Order.id.desc())
        .all()
    )

    return {
        "account_number": current_user.account_number,
        "transactions": [
            {
                "id": order.id,
                "type": "purchase",
                "amount": order.total_amount,
                "currency": order.currency,
                "status": order.status,
                "description": order.description,
                "created_at": order.created_at,
            }
            for order in transactions
        ],
    }


@router.get("/{account_number}")
def get_transaction(
    account_number: str,
    current_user: User = Depends(get_transaction_user),
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.account_number == account_number)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Account not found",
        )

    # H3 BOLA:
    # Sengaja tidak mengecek ownership.
    transactions = (
        db.query(Order)
        .filter(Order.user_id == user.id)
        .order_by(Order.id.desc())
        .all()
    )

    return {
        "account_number": user.account_number,
        "status": "success",
        "transactions": [
            {
                "id": order.id,
                "type": "purchase",
                "from_account": user.account_number,
                "to_account": "VULNMART",
                "amount": order.total_amount,
                "currency": order.currency,
                "description": order.description,
                "created_at": order.created_at,
            }
            for order in transactions
        ],
    }