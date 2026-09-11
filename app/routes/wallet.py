from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.models.wallet import Wallet

router = APIRouter(
    prefix="/api/wallet",
    tags=["Wallet"],
)


@router.get("/")
def get_wallets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wallets = (
        db.query(Wallet)
        .filter(Wallet.user_id == current_user.id)
        .all()
    )

    return {
        "wallets": [
            {
                "id": wallet.id,
                "currency": wallet.currency,
                "balance": wallet.balance,
            }
            for wallet in wallets
        ]
    }