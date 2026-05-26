from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.schemas.auth import (
    SignupRequest,
    LoginRequest,
    ForgetPasswordRequest,
    ResetPasswordRequest
)

from app.services.user_auth_service import (
    signup_user,
    login_user,
    request_password_reset,
    reset_password
)


router = APIRouter()


# ============================================
# SIGNUP
# ============================================

@router.post("/signup")
def signup(
    request: SignupRequest,
    db: Session = Depends(get_db)
):

    return signup_user(
        db=db,
        request=request
    )


# ============================================
# LOGIN
# ============================================

@router.post("/login")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):

    return login_user(
        db=db,
        request=request
    )


# ============================================
# FORGOT PASSWORD
# ============================================

@router.post("/forgot-password")
def forgot_password(
    request: ForgetPasswordRequest,
    db: Session = Depends(get_db)
):

    return request_password_reset(
        db=db,
        request=request
    )


# ============================================
# RESET PASSWORD
# ============================================

@router.post("/reset-password")
def reset_user_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):

    return reset_password(
        db=db,
        request=request
    )


# ============================================
# TEST AUTH
# ============================================

@router.get("/me")
def me():

    return {
        "message":
            "Auth working"
    }