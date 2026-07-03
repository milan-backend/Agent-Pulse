from fastapi import APIRouter, Depends, HTTPException, Request, Response, Cookie
from sqlalchemy.orm import Session
from app.db.session import get_db

from app.schemas.auth import (
    SignupRequest,
    LoginRequest,
    ForgetPasswordRequest,
    ResetPasswordRequest,
    DeactivateAccountRequest,
    SSOLoginRequest
)

from app.services.user_auth_service import (
    signup_user,
    login_user,
    request_password_reset,
    reset_password,
    verify_user_email,
    refresh_access_token,
    logout_user,
    issue_websocket_ticket,
    check_rate_limit,
    login_or_register_sso_user
)

from app.api.deps_user import get_current_user
from app.models.user import User
from app.core.security import verify_password

router = APIRouter()

# ============================================
# SIGNUP ROUTE
# ============================================
@router.post("/signup")
def signup(
    request: SignupRequest,
    fastapi_req: Request,
    db: Session = Depends(get_db)
):
    client_ip = fastapi_req.client.host or "unknown"
    check_rate_limit(client_ip=client_ip, limit_type="signup", max_requests=3, window_minutes=1)
    return signup_user(db=db, request=request)

# ============================================
# LOGIN ROUTE (HTTPONLY SEEDING INJECTED)
# ============================================
@router.post("/login")
def login(
    request: LoginRequest,
    fastapi_req: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    client_ip = fastapi_req.client.host or "unknown"
    check_rate_limit(client_ip=client_ip, limit_type="login", max_requests=5, window_minutes=1)
    return login_user(db=db, request=request, response=response)

# ============================================
# ROTATED REFRESH ACCESS CONVERSION
# ============================================
@router.post("/refresh")
def refresh(
    response: Response,
    refresh_token: str = Cookie(None), # Automatically grabs token string out of http headers cookie container
    db: Session = Depends(get_db)
):
    return refresh_access_token(db=db, refresh_token=refresh_token, response=response)

# ============================================
# SECURE ONE-TIME WEBSOCKET TICKET HANDSHAKE ROUTE
# ============================================
@router.post("/ws-ticket")
def get_websocket_ticket(current_user: User = Depends(get_current_user)):
    """ Endpoint that issues a safe, short-lived ticket to securely connect to web sockets without exposing raw JWTs """
    ticket = issue_websocket_ticket(user_id=current_user.id)
    return {"ticket": ticket}

# ============================================
# SECURE SESSION LOGOUT
# ============================================
@router.post("/logout")
def logout(
    response: Response,
    refresh_token: str = Cookie(None),
    db: Session = Depends(get_db)
):
    return logout_user(db=db, refresh_token=refresh_token, response=response)

# ============================================
# VERIFY EMAIL
# ============================================
@router.get("/verify-email")
def verify_email(
    token: str,
    db: Session = Depends(get_db)
):
    return verify_user_email(db=db, token=token)

# ============================================
# FORGOT PASSWORD
# ============================================
@router.post("/forgot-password")
def forgot_password(
    request: ForgetPasswordRequest,
    db: Session = Depends(get_db)
):
    return request_password_reset(db=db, request=request)

# ============================================
# RESET PASSWORD
# ============================================
@router.post("/reset-password")
def reset_user_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    return reset_password(db=db, request=request)

# ============================================
# CURRENT USER INFO
# ============================================
@router.get("/me")
def me(
    current_user: User = Depends(get_current_user)
):
    return {
        "user_id": str(current_user.id),
        "name": current_user.name,
        "email": current_user.email,
        "is_verified": current_user.is_verified,
        "is_active": current_user.is_active
    }

# ============================================
# DEACTIVATE ACCOUNT
# ============================================
@router.delete("/deactivate-account")
def deactivate_account(
    request: DeactivateAccountRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    valid = verify_password(request.password, current_user.password_hash)
    if not valid:
        raise HTTPException(status_code=401, detail="Invalid password")

    current_user.is_active = False
    db.commit()
    return {"message": "Account deactivated successfully"}


# ============================================
# SINGLE SIGN-ON (SSO) CALLBACK HANDLER 🔮
# ============================================
@router.post("/sso/callback")
def sso_callback(
    request: SSOLoginRequest,
    fastapi_req: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """ Centralized endpoint to authenticate or register users logging in via Google/GitHub """
    client_ip = fastapi_req.client.host or "unknown"
    
    # Reusing your excellent built-in rate-limiting logic block!
    check_rate_limit(client_ip=client_ip, limit_type="sso", max_requests=10, window_minutes=1)
    
    return login_or_register_sso_user(
        db=db,
        sso_email=request.email,
        sso_name=request.name,
        provider=request.provider,
        provider_id=request.provider_id,
        response=response
    )