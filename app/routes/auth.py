import secrets

from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.database import get_db
from app.models.user import User
from app.models.wallet import Wallet
from app.schemas.auth import LoginRequest, RegisterRequest


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


# ============================================================
# LOGIN
# ============================================================

@router.post("/login")
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.username == data.username)
        .first()
    )

    if not user or user.password != data.password:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    token = create_access_token(
        user_id=user.id,
        username=user.username,
        role=user.role,
        account_number=user.account_number,
    )

    response = JSONResponse(
        content={
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "account_number": user.account_number,
            },
        }
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60,
    )

    return response


# ============================================================
# LOGOUT
# ============================================================

@router.post("/logout")
def logout():
    response = JSONResponse(
        content={
            "message": "Logged out successfully"
        }
    )

    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="lax",
        secure=False,
    )

    return response


# ============================================================
# SET SESSION
#
# Dipakai untuk menyamakan JWT dari localStorage
# dengan cookie access_token.
#
# Base.html mengirim:
# Content-Type: application/x-www-form-urlencoded
# token=<JWT>
# ============================================================

@router.post("/set-session")
def set_session(
    token: str = Form(...),
):
    response = JSONResponse(
        content={
            "message": "Session updated"
        }
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60,
    )

    return response


# ============================================================
# REGISTER
# ============================================================

@router.post("/register")
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(User)
        .filter(
            (User.username == data.username)
            | (User.email == data.email)
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username or email already exists",
        )

    # Generate unique account number
    while True:
        account_number = str(
            secrets.randbelow(9_000_000_000)
            + 1_000_000_000
        )

        exists = (
            db.query(User)
            .filter(
                User.account_number == account_number
            )
            .first()
        )

        if not exists:
            break

    user = User(
        username=data.username,
        email=data.email,
        password=data.password,
        full_name=data.full_name,
        role="member",
        bio="",
        account_number=account_number,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    idr_wallet = Wallet(
        user_id=user.id,
        balance=100000,
        currency="IDR",
    )

    usd_wallet = Wallet(
        user_id=user.id,
        balance=0,
        currency="USD",
    )

    db.add_all([
        idr_wallet,
        usd_wallet,
    ])

    db.commit()

    return {
        "message": "Registration successful",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "account_number": user.account_number,
        },
    }