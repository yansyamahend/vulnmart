from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.models.wallet import Wallet
from app.schemas.user import UpdateProfileRequest


router = APIRouter(
    prefix="/api/users",
    tags=["Users"],
)


@router.get("/me")
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wallets = (
        db.query(Wallet)
        .filter(Wallet.user_id == current_user.id)
        .all()
    )

    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "bio": current_user.bio,
        "account_number": current_user.account_number,
        "wallets": [
            {
                "id": wallet.id,
                "currency": wallet.currency,
                "balance": wallet.balance,
            }
            for wallet in wallets
        ],
    }


@router.put("/me")
def update_my_profile(
    data: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user.full_name = data.full_name
    current_user.bio = data.bio

    db.commit()
    db.refresh(current_user)

    return {
        "message": "Profile updated",
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "role": current_user.role,
            "bio": current_user.bio,
            "account_number": current_user.account_number,
        },
    }