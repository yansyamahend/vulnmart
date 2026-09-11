import jwt

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.security import ALGORITHM, SECRET_KEY
from app.database import get_db
from app.models.user import User


router = APIRouter()

templates = Jinja2Templates(directory="templates")


# ============================================================
# WEB AUTH
#
# Priority:
# 1. Authorization: Bearer <JWT>
# 2. token query parameter
# 3. access_token cookie
# ============================================================

def get_web_user(
    request: Request,
    db: Session,
    token: str | None = None,
):
    jwt_token = None

    # --------------------------------------------------------
    # 1. Authorization header
    # --------------------------------------------------------

    authorization = request.headers.get("Authorization")

    if authorization:
        parts = authorization.split(" ", 1)

        if len(parts) == 2 and parts[0].lower() == "bearer":
            jwt_token = parts[1].strip()

    # --------------------------------------------------------
    # 2. Query parameter
    # --------------------------------------------------------

    if not jwt_token and token:
        jwt_token = token

    # --------------------------------------------------------
    # 3. Cookie
    # --------------------------------------------------------

    if not jwt_token:
        jwt_token = request.cookies.get("access_token")

    if not jwt_token:
        return None

    # --------------------------------------------------------
    # Decode JWT
    # --------------------------------------------------------

    try:
        payload = jwt.decode(
            jwt_token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
    except jwt.PyJWTError:
        return None

    user_id = payload.get("sub")

    if user_id is None:
        return None

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return None

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        return None

    # ========================================================
    # INTENTIONAL JWT TRUST
    #
    # Role berasal dari JWT.
    # Digunakan khusus untuk lab.
    # ========================================================

    jwt_role = payload.get("role")

    if jwt_role:
        user.role = jwt_role

    jwt_account_number = payload.get("account_number")

    if jwt_account_number:
        user.account_number = jwt_account_number

    return user


def require_login(
    request: Request,
    db: Session,
    token: str | None = None,
):
    return get_web_user(
        request,
        db,
        token,
    )


# ============================================================
# PUBLIC PAGES
# ============================================================

@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
    )


@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
    )


@router.get("/forgot-password")
def forgot_password_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="forgot_password.html",
    )


@router.get("/reset-password")
def reset_password_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="reset_password.html",
    )


@router.get("/products")
def products_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@router.get("/products/{product_id}")
def product_page(
    request: Request,
    product_id: int,
):
    return templates.TemplateResponse(
        request=request,
        name="product.html",
        context={
            "product_id": product_id,
        },
    )


# ============================================================
# PROTECTED USER PAGES
# ============================================================

@router.get("/profile")
def profile_page(
    request: Request,
    token: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    user = require_login(
        request,
        db,
        token,
    )

    if user is None:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="profile.html",
    )


@router.get("/cart")
def cart_page(
    request: Request,
    token: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    user = require_login(
        request,
        db,
        token,
    )

    if user is None:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="cart.html",
    )


@router.get("/orders")
def orders_page(
    request: Request,
    token: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    user = require_login(
        request,
        db,
        token,
    )

    if user is None:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="orders.html",
    )


@router.get("/orders/{order_id}")
def order_page(
    request: Request,
    order_id: int,
    token: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    user = require_login(
        request,
        db,
        token,
    )

    if user is None:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="order.html",
        context={
            "order_id": order_id,
        },
    )


@router.get("/exchange")
def exchange_page(
    request: Request,
    token: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    user = require_login(
        request,
        db,
        token,
    )

    if user is None:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="exchange.html",
    )


# ============================================================
# ADMIN PAGES
# ============================================================

@router.get("/admin")
def admin_page(
    request: Request,
    token: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    user = get_web_user(
        request,
        db,
        token,
    )

    if user is None:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    if user.role != "admin":
        return RedirectResponse(
            url="/profile",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
    )


@router.get("/admin/users/{user_id}")
def admin_user_page(
    request: Request,
    user_id: int,
    token: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    user = get_web_user(
        request,
        db,
        token,
    )

    if user is None:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    if user.role != "admin":
        return RedirectResponse(
            url="/profile",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="admin_user.html",
        context={
            "user_id": user_id,
        },
    )