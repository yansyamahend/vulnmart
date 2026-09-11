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
        "username": "victim",
        "email": "victim@vulnmart.local",
        "produk": "Login menggunakan akun victim untuk melihat produk",
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
    challenge = (
        db.query(H5Challenge)
        .filter(H5Challenge.user_id == current_user.id)
        .first()
    )

    accounts = [account.copy() for account in SUSPENDED_ACCOUNTS]

    # H5 flag is shown only when the current logged-in
    # user is the target account and the legacy V1 reset
    # challenge has been completed.
    if (
        current_user.username == "victim"
        and challenge is not None
        and challenge.completed
    ):
        for account in accounts:
            if account["username"] == "victim":
                account["produk"] = challenge.flag

    return accounts
