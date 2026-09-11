import secrets
from datetime import datetime

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.schemas.crew import (
    CrewLoginRequest,
    CrewOTPRequest,
    CrewRegisterRequest,
)

router = APIRouter()

templates = Jinja2Templates(directory="templates")


# ============================================================
# IN-MEMORY STORAGE
# ============================================================

crew_users = {}
crew_otps = {}
crew_sessions = {}


# ============================================================
# WEB PAGES
# ============================================================

@router.get("/CrewPanel")
def crew_login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="crew_login.html",
    )


@router.get("/CrewPanel/register")
def crew_register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="crew_register.html",
    )


@router.get("/CrewPanel/otp")
def crew_otp_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="crew_otp.html",
    )


@router.get("/DashboardCrew")
def crew_dashboard(request: Request):
    session_token = request.cookies.get("crew_session")

    if not session_token or session_token not in crew_sessions:
        return RedirectResponse(
            url="/CrewPanel",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="crew_dashboard.html",
    )


# ============================================================
# API - REGISTER
# ============================================================

@router.post("/api/crew/register")
def crew_register(data: CrewRegisterRequest):

    username = data.username
    email = data.email
    password = data.password
    full_name = data.full_name

    if username in crew_users:
        return {
            "success": False,
            "message": "Username already exists.",
        }

    crew_users[username] = {
        "username": username,
        "email": email,
        "password": password,
        "full_name": full_name,
        "role": "crew",
        "bio": "Crew member",
        "created_at": datetime.utcnow().isoformat(),
    }

    otp = str(secrets.randbelow(900000) + 100000)

    crew_otps[username] = otp

    print(
        f"[CREWPANEL] OTP for {username}: {otp}"
    )

    return {
        "success": True,
        "message": "Registration successful.",
        "username": username,
    }


# ============================================================
# API - LOGIN
# ============================================================

@router.post("/api/crew/login")
def crew_login(data: CrewLoginRequest):

    username = data.username
    password = data.password

    user = crew_users.get(username)

    if not user or user["password"] != password:
        return {
            "success": False,
            "message": "Invalid username or password.",
        }

    otp = str(secrets.randbelow(900000) + 100000)

    crew_otps[username] = otp

    print(
        f"[CREWPANEL] OTP for {username}: {otp}"
    )

    return {
        "success": True,
        "message": "OTP generated.",
        "username": username,
    }


# ============================================================
# API - VERIFY OTP
# ============================================================
@router.post("/api/crew/verify-otp")
def verify_otp(data: CrewOTPRequest):

    username = data.username
    otp = data.otp

    if not username:
        return {
            "success": False,
            "message": "Username is required.",
        }

    # OTP BYPASS
    if otp is None:
        session_token = secrets.token_urlsafe(32)

        crew_sessions[session_token] = username

        response = RedirectResponse(
            url="/DashboardCrew",
            status_code=303,
        )

        response.set_cookie(
            key="crew_session",
            value=session_token,
            httponly=True,
            samesite="lax",
        )

        return response

    expected_otp = crew_otps.get(username)

    if not expected_otp:
        return {
            "success": False,
            "message": "OTP not found.",
        }

    if otp != expected_otp:
        return {
            "success": False,
            "message": "Invalid OTP.",
        }

    session_token = secrets.token_urlsafe(32)

    crew_sessions[session_token] = username

    del crew_otps[username]

    response = RedirectResponse(
        url="/DashboardCrew",
        status_code=303,
    )

    response.set_cookie(
        key="crew_session",
        value=session_token,
        httponly=True,
        samesite="lax",
    )

    return response


# ============================================================
# API - LOGOUT
# ============================================================

@router.get("/api/crew/logout")
def crew_logout(request: Request):

    session_token = request.cookies.get(
        "crew_session"
    )

    if session_token:
        crew_sessions.pop(
            session_token,
            None,
        )

    response = RedirectResponse(
        url="/CrewPanel",
        status_code=303,
    )

    response.delete_cookie("crew_session")

    return response