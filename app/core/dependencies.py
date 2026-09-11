import jwt

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import ALGORITHM, SECRET_KEY
from app.database import get_db
from app.models.user import User


bearer_scheme = HTTPBearer()


def decode_token(token: str):
    try:
        return jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    payload = decode_token(credentials.credentials)

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    # --------------------------------------------------------
    # LAB INTENTIONAL JWT TRUST
    #
    # Authorization membaca role dari JWT.
    # Bukan dari database.
    #
    # Ini sengaja vulnerable untuk challenge JWT.
    # --------------------------------------------------------

    jwt_role = payload.get("role")

    if jwt_role:
        user.role = jwt_role

    jwt_account_number = payload.get("account_number")

    if jwt_account_number:
        user.account_number = jwt_account_number

    return user


    