import os
import secrets
from datetime import datetime, timedelta
from fastapi import HTTPException
from jose import jwt, JWTError
from sqlalchemy.orm import Session

# Import your system infrastructure tables
from app.models.user import User
from app.models.workspace import Workspace
from app.models.plan import Plan
from app.models.workspace_subscription import WorkspaceSubscription
from app.models.workspace_member import WorkspaceMember
from app.models.refresh_token import RefreshToken  # Our new table model link

from app.services.email_service import (
    send_verification_email,
    send_reset_password_email
)
from app.core.security import (
    hash_password,
    verify_password
)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

# ============================================
# IN-MEMORY RATE LIMITING SYSTEM BLOCK
# ============================================
# Tracks timestamp histories per client IP address without needing a separate Redis instance
RATE_LIMIT_STORAGE = {}

def check_rate_limit(client_ip: str, limit_type: str, max_requests: int, window_minutes: int):
    now = datetime.utcnow()
    window_start = now - timedelta(minutes=window_minutes)
    
    tracking_key = f"{client_ip}:{limit_type}"
    
    if tracking_key not in RATE_LIMIT_STORAGE:
        RATE_LIMIT_STORAGE[tracking_key] = []
        
    # Clean up timestamp footprints older than our rolling limit window boundary
    RATE_LIMIT_STORAGE[tracking_key] = [
        ts for ts in RATE_LIMIT_STORAGE[tracking_key] if ts > window_start
    ]
    
    if len(RATE_LIMIT_STORAGE[tracking_key]) >= max_requests:
        raise HTTPException(
            status_code=429,
            detail=f"Too many requests. Rate limit exceeded for {limit_type}. Try again later."
        )
        
    # Commit the current execution request timestamp to memory array
    RATE_LIMIT_STORAGE[tracking_key].append(now)

# ============================================
# SIGNUP LAYER
# ============================================

def signup_user(
    db: Session,
    request
):
    existing = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if existing:
        if existing.is_verified:
            raise HTTPException(
                status_code=400,
                detail="Email already exists"
            )

        # RESEND VERIFICATION EMAIL
        send_verification_email(
            to_email=existing.email,
            token=existing.email_verification_token
        )
        return {"message": "Verification email resent"}

    verification_token = secrets.token_urlsafe(32)
    verification_expiry = datetime.utcnow() + timedelta(hours=24)

    # CREATE USER
    user = User(
        name=request.name,
        email=request.email,
        password_hash=hash_password(request.password),
        is_verified=False,
        is_active=True,
        email_verification_token=verification_token,
        email_verification_expiry=verification_expiry
    )

    db.add(user)
    db.flush()

    # CREATE WORKSPACE
    workspace = Workspace(
        name=f"{request.name}'s Workspace",
        slug=f"{request.name.lower().replace(' ','-')}-{secrets.token_hex(3)}",
        type="personal",
        owner_id=user.id
    )

    db.add(workspace)
    db.flush()

    # CREATE MEMBERSHIP
    membership = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=user.id,
        role="admin"
    )
    db.add(membership)

    # FIND FREE PLAN
    free_plan = (
        db.query(Plan)
        .filter(Plan.name == "free")
        .first()
    )

    if not free_plan:
        raise HTTPException(
            status_code=500,
            detail="Free plan missing"
        )

    # CREATE SUBSCRIPTION
    subscription = WorkspaceSubscription(
        workspace_id=workspace.id,
        plan_id=free_plan.id,
        status="active"
    )
    db.add(subscription)

    db.commit()
    db.refresh(user)
    db.refresh(workspace)

    # SEND VERIFICATION EMAIL
    send_verification_email(
        to_email=user.email,
        token=verification_token
    )

    return {
        "message": "Signup successful. Please verify your email.",
        "user_id": str(user.id),
        "workspace_id": str(workspace.id),
        "role": "admin"
    }

# ============================================
# LOGIN LAYER (SECURED WITH SHORT LIVED ACCESS & DB REFRESH TOKENS)
# ============================================

def login_user(
    db: Session,
    request
):
    user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Account deactivated"
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Email not verified"
        )

    valid = verify_password(request.password, user.password_hash)

    if not valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    memberships = (
        db.query(WorkspaceMember)
        .filter(WorkspaceMember.user_id == user.id)
        .all()
    )

    if not memberships:
        raise HTTPException(
            status_code=403,
            detail="No workspace membership found"
        )

    workspace_list = []
    for member in memberships:
        workspace = (
            db.query(Workspace)
            .filter(Workspace.id == member.workspace_id)
            .first()
        )
        if workspace:
            workspace_list.append({
                "workspace_id": str(workspace.id),
                "workspace_name": workspace.name,
                "role": member.role
            })

    default_membership = memberships[0]

    # 1. Short-lived Access Token Payload (15 Minutes)
    access_payload = {
        "sub": str(user.id),
        "exp": datetime.utcnow() + timedelta(minutes=15)
    }
    token = jwt.encode(access_payload, SECRET_KEY, algorithm=ALGORITHM)

    # 2. Long-lived Refresh Token Storage Setup (7 Days)
    refresh_token_string = secrets.token_urlsafe(64)
    refresh_expiry = datetime.utcnow() + timedelta(days=7)

    # Commit refresh row record to Render PostgreSQL database
    db_refresh_token = RefreshToken(
        user_id=user.id,
        token_id=refresh_token_string,
        expires_at=refresh_expiry
    )
    db.add(db_refresh_token)
    db.commit()

    return {
        "access_token": token,
        "refresh_token": refresh_token_string,
        "token_type": "bearer",
        "user_id": str(user.id),
        "workspace_id": str(default_membership.workspace_id),
        "role": default_membership.role,
        "workspaces": workspace_list
    }

# ============================================
# VERIFY EMAIL
# ============================================

def verify_user_email(
    db: Session,
    token: str
):
    user = (
        db.query(User)
        .filter(User.email_verification_token == token)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid token"
        )

    if user.email_verification_expiry < datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail="Verification token expired"
        )

    user.is_verified = True
    user.email_verification_token = None
    user.email_verification_expiry = None
    db.commit()

    return {"message": "Email verified successfully"}

# ============================================
# REQUEST PASSWORD RESET
# ============================================

def request_password_reset(
    db: Session,
    request
):
    user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if not user:
        return {"message": "If the account exists, a password reset link has been sent"}

    token = secrets.token_urlsafe(48)
    expires = datetime.utcnow() + timedelta(hours=1)

    user.reset_password_token = token
    user.reset_password_expires = expires
    db.commit()

    send_reset_password_email(to_email=user.email, token=token)

    return {"message": "If the account exists, a password reset link has been sent"}

# ============================================
# RESET PASSWORD
# ============================================

def reset_password(
    db: Session,
    request
):
    user = (
        db.query(User)
        .filter(User.reset_password_token == request.token)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid reset token"
        )

    if not user.reset_password_expires:
        raise HTTPException(
            status_code=400,
            detail="Invalid reset token"
        )

    if user.reset_password_expires < datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail="Reset token expired"
        )

    user.password_hash = hash_password(request.new_password)
    user.reset_password_token = None
    user.reset_password_expires = None
    db.commit()

    return {"message": "Password reset successful"}

# ============================================
# REFRESH ACCESS TOKEN HANDSHAKE
# ============================================

def refresh_access_token(
    db: Session,
    refresh_token: str
):
    token_record = (
        db.query(RefreshToken)
        .filter(RefreshToken.token_id == refresh_token)
        .first()
    )

    if not token_record:
        raise HTTPException(status_code=401, detail="Refresh token invalid or missing")
    if token_record.revoked:
        raise HTTPException(status_code=401, detail="Refresh token has been revoked")
    if token_record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Refresh token expired")

    # Generate a brand new access token valid for another rolling 15 minutes
    new_access_payload = {
        "sub": str(token_record.user_id),
        "exp": datetime.utcnow() + timedelta(minutes=15)
    }
    new_access_token = jwt.encode(new_access_payload, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

# ============================================
# LOGOUT SYSTEM
# ============================================

def logout_user(
    db: Session,
    refresh_token: str
):
    token_record = (
        db.query(RefreshToken)
        .filter(RefreshToken.token_id == refresh_token)
        .first()
    )

    if token_record:
        token_record.revoked = True
        db.commit()

    return {"message": "Logged out successfully"}

# ============================================
# AUTHENTICATE USER
# ============================================

def authenticate_user(
    db: Session,
    token: str
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Account deactivated"
        )

    return user