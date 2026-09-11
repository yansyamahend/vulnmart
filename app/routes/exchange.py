from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.models.wallet import Wallet

router = APIRouter(
    prefix="/api/exchange",
    tags=["Exchange"],
)


NORMAL_RATE = 16000


@router.post("/")
def exchange_idr_to_usd(
    amount: int,
    rate: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Amount must be greater than zero",
        )

    idr_wallet = (
        db.query(Wallet)
        .filter(
            Wallet.user_id == current_user.id,
            Wallet.currency == "IDR",
        )
        .first()
    )

    usd_wallet = (
        db.query(Wallet)
        .filter(
            Wallet.user_id == current_user.id,
            Wallet.currency == "USD",
        )
        .first()
    )

    if not idr_wallet or not usd_wallet:
        raise HTTPException(
            status_code=400,
            detail="Wallet not found",
        )

    if idr_wallet.balance < amount:
        raise HTTPException(
            status_code=400,
            detail="Insufficient IDR balance",
        )

    # ========================================================
    # H4 BUSINESS LOGIC FLAW
    #
    # Normal:
    # 1 USD = 16,000 IDR
    #
    # Server seharusnya menggunakan NORMAL_RATE.
    # Namun client boleh mengirim "rate" sendiri.
    # ========================================================

    exchange_rate = rate if rate is not None else NORMAL_RATE

    if exchange_rate <= 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid exchange rate",
        )

    usd_received = amount // exchange_rate

    if usd_received <= 0:
        raise HTTPException(
            status_code=400,
            detail="Amount is too small for conversion",
        )

    idr_wallet.balance -= amount
    usd_wallet.balance += usd_received

    db.commit()

    return {
        "message": "Exchange successful",
        "from": "IDR",
        "to": "USD",
        "amount": amount,
        "exchange_rate": exchange_rate,
        "usd_received": usd_received,
        "remaining_idr": idr_wallet.balance,
        "usd_balance": usd_wallet.balance,
    }