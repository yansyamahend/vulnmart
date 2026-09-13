import os
import urllib.error
import urllib.request
from urllib.parse import urlencode

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.models.wallet import Wallet
from app.schemas.user import UpdateProfileRequest
from fastapi import BackgroundTasks


router = APIRouter(
    prefix="/api/users",
    tags=["Users"],
)


ADMIN_BOT_URL = os.getenv(
    "ADMIN_BOT_URL",
    "http://vulnmart-admin-bot:9000",
).rstrip("/")

BOT_TRIGGER_SECRET = os.getenv(
    "BOT_TRIGGER_SECRET",
    "change-this-secret",
)


def trigger_admin_review(
    user_id: int,
) -> None:
    try:
        query = urlencode(
            {
                "user_id": user_id,
            }
        )

        request = urllib.request.Request(
            f"{ADMIN_BOT_URL}/review?{query}",
            method="POST",
            headers={
                "X-Bot-Secret": BOT_TRIGGER_SECRET,
            },
        )

        with urllib.request.urlopen(
            request,
            timeout=5,
        ) as response:
            response.read()

    except (
        urllib.error.URLError,
        TimeoutError,
    ) as exc:
        print(
            f"[ADMIN BOT] Failed to queue "
            f"user {user_id}: {exc}"
        )


@router.get("/me")
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wallets = (
        db.query(Wallet)
        .filter(
            Wallet.user_id == current_user.id
        )
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
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user.full_name = data.full_name
    current_user.bio = data.bio

    db.commit()
    db.refresh(current_user)

    # Automatically ask the admin reviewer bot
    # to inspect this user's profile.
    background_tasks.add_task(
        trigger_admin_review,
        current_user.id,
    )

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