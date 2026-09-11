import os

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.h5_challenge import H5Challenge
from app.models.user import User

router = APIRouter(
    prefix="/api/accounts",
    tags=["Accounts"],
)


TARGET_USERNAME = os.getenv(
    "H5_TARGET_USERNAME",
    "victim",
)

TARGET_EMAIL = os.getenv(
    "H5_TARGET_EMAIL",
    "victim@vulnmart.local",
)


SUSPENDED_ACCOUNTS = [
    {
        "username": "raka01",
        "email": "raka01@mail.local",
        "produk": "Wireless gaming mouse",
    },
    {
        "username": "testuser",
        "email": "testuser@mail.local",
        "produk": "Mechanical keyboard",
    },
    {
        "username": TARGET_USERNAME,
        "email": TARGET_EMAIL,
        "produk": "Login menggunakan akun ini untuk melihat produk",
    },
    {
        "username": "demo_user",
        "email": "demo_user@mail.local",
        "produk": "Gaming headset",
    },
]


@router.get("/suspended")
def get_suspended_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    accounts = [
        account.copy()
        for account in SUSPENDED_ACCOUNTS
    ]

    challenge = (
        db.query(H5Challenge)
        .filter(
            H5Challenge.user_id == current_user.id
        )
        .first()
    )

    # Flag hanya ditampilkan ketika:
    # 1. User yang login adalah target account.
    # 2. Target account sudah menyelesaikan H5 melalui
    #    legacy password reset V1.
    if (
        current_user.username == TARGET_USERNAME
        and challenge is not None
        and challenge.completed
    ):
        for account in accounts:
            if account["username"] == TARGET_USERNAME:
                account["produk"] = challenge.flag
                break

    return accounts