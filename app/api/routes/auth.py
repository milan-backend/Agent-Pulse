from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.schemas.auth import (
    SignupRequest,
    LoginRequest,
    ForgetPasswordRequest,
    ResetPasswordRequest,
    DeactivateAccountRequest
)

from app.services.user_auth_service import (
    signup_user,
    login_user,
    request_password_reset,
    reset_password,
    verify_user_email
)

from app.api.deps_user import (
    get_current_user
)

from app.models.user import User

from app.core.security import (
    verify_password
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
# VERIFY EMAIL
# ============================================

@router.get("/verify-email")
def verify_email(
    token: str,
    db: Session = Depends(get_db)
):

    return verify_user_email(
        db=db,
        token=token
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
# CURRENT USER
# ============================================

@router.get("/me")
def me(
    current_user: User = Depends(
        get_current_user
    )
):

    return {

        "user_id":
            str(current_user.id),

        "name":
            current_user.name,

        "email":
            current_user.email,

        "is_verified":
            current_user.is_verified,

        "is_active":
            current_user.is_active
    }


# ============================================
# DEACTIVATE ACCOUNT
# ============================================

@router.delete("/deactivate-account")
def deactivate_account(

    request: DeactivateAccountRequest,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    # VERIFY PASSWORD AGAIN
    valid = verify_password(

        request.password,

        current_user.password_hash
    )

    if not valid:

        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )

    # SOFT DELETE ACCOUNT
    current_user.is_active = False

    db.commit()

    return {

        "message":
            "Account deactivated successfully"
    }
