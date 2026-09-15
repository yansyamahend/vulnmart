import os
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.h5_challenge import H5Challenge
from app.models.password_reset import PasswordReset
from app.models.user import User
from app.schemas.password_reset import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
)

router = APIRouter(
    tags=["Password Reset"],
)


TARGET_USERNAME = os.getenv(
    "H5_TARGET_USERNAME",
    "victim",
)

H5_FLAG = os.getenv(
    "H5_FLAG",
    "flag{dummy3}",
)


def create_reset_token(
    user: User,
    db: Session,
) -> str:
    token = secrets.token_urlsafe(32)

    reset = PasswordReset(
        user_id=user.id,
        token=token,
        expires_at=datetime.now(timezone.utc)
        + timedelta(minutes=15),
    )

    db.add(reset)
    db.commit()

    return token


# ============================================================
# V3 - MODERN PASSWORD RESET
# ============================================================

@router.post(
    "/api/v3/auth/forgot-password",
    summary="Request password reset",
)
def forgot_password_v3(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    if user is not None:
        create_reset_token(user, db)

    return {
        "message": (
            "If the account exists, reset instructions "
            "have been sent."
        ),
    }


@router.post(
    "/api/v3/auth/reset-password",
    summary="Reset password",
)
def reset_password_v3(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    reset = (
        db.query(PasswordReset)
        .filter(
            PasswordReset.token == data.token
        )
        .first()
    )

    if reset is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid reset token",
        )

    now = datetime.now(timezone.utc)

    if (
        reset.expires_at.replace(
            tzinfo=timezone.utc
        )
        < now
    ):
        raise HTTPException(
            status_code=400,
            detail="Reset token expired",
        )

    user = (
        db.query(User)
        .filter(User.id == reset.user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    user.password = data.new_password

    db.delete(reset)
    db.commit()

    return {
        "message": "Password reset successful",
    }


# ============================================================
# V1 - LEGACY PASSWORD RESET
#
# INTENTIONALLY VULNERABLE FOR CTF:
# reset_token is exposed directly in the response.
# ============================================================

@router.post(
    "/api/v1/auth/forgot-password",
    summary="Legacy password reset",
    include_in_schema=False,
)
def forgot_password_v1(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    token = create_reset_token(user, db)

    return {
        "message": "Password reset request created",
        "reset_token": token,
        "api_version": "v1",
        "legacy": True,
    }


@router.post(
    "/api/v1/auth/reset-password",
    summary="Legacy password reset confirmation",
    include_in_schema=False,
)
def reset_password_v1(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    reset = (
        db.query(PasswordReset)
        .filter(
            PasswordReset.token == data.token
        )
        .first()
    )

    if reset is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid reset token",
        )

    now = datetime.now(timezone.utc)

    if (
        reset.expires_at.replace(
            tzinfo=timezone.utc
        )
        < now
    ):
        raise HTTPException(
            status_code=400,
            detail="Reset token expired",
        )

    user = (
        db.query(User)
        .filter(User.id == reset.user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    user.password = data.new_password

    # ========================================================
    # H5 COMPLETION
    #
    # H5 hanya dianggap selesai apabila target account
    # berhasil di-reset melalui legacy API V1.
    # ========================================================

    if user.username == TARGET_USERNAME:
        challenge = (
            db.query(H5Challenge)
            .filter(
                H5Challenge.user_id == user.id
            )
            .first()
        )

        if challenge is None:
            challenge = H5Challenge(
                user_id=user.id,
                completed=True,
                flag=H5_FLAG,
            )
            db.add(challenge)
        else:
            challenge.completed = True
            challenge.flag = H5_FLAG

    db.delete(reset)
    db.commit()

    return {
        "message": "Password reset successful",
        "api_version": "v1",
    }