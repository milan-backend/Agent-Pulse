import os
import secrets
from datetime import datetime, timedelta
from fastapi import HTTPException, Response
from jose import jwt, JWTError
from sqlalchemy.orm import Session

# Import your system infrastructure tables
from app.models.user import User
from app.models.workspace import Workspace
from app.models.plan import Plan
from app.models.workspace_subscription import WorkspaceSubscription
from app.models.workspace_member import WorkspaceMember
from app.models.refresh_token import RefreshToken
from datetime import timezone

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

# Dynamic global cache container memory allocation for secure short-lived WebSocket tokens
WEBSOCKET_TICKET_STORE = {}

# ============================================
# IN-MEMORY RATE LIMITING SYSTEM BLOCK
# ============================================
RATE_LIMIT_STORAGE = {}

def check_rate_limit(client_ip: str, limit_type: str, max_requests: int, window_minutes: int):
    now = datetime.utcnow()
    window_start = now - timedelta(minutes=window_minutes)
    
    tracking_key = f"{client_ip}:{limit_type}"
    
    if tracking_key not in RATE_LIMIT_STORAGE:
        RATE_LIMIT_STORAGE[tracking_key] = []
        
    RATE_LIMIT_STORAGE[tracking_key] = [
        ts for ts in RATE_LIMIT_STORAGE[tracking_key] if ts > window_start
    ]
    
    if len(RATE_LIMIT_STORAGE[tracking_key]) >= max_requests:
        raise HTTPException(
            status_code=429,
            detail=f"Too many requests. Rate limit exceeded for {limit_type}. Try again later."
        )
        
    RATE_LIMIT_STORAGE[tracking_key].append(now)

# ============================================
# COOKIE MANAGEMENT HELPER
# ============================================
def set_secure_refresh_cookie(response: Response, token_string: str):
    expire_time = datetime.now(timezone.utc) + timedelta(days=7)

    # ✅ FIXED FOR CROSS-SITE PRODUCTION ECOSYSTEMS:
    # Setting samesite="none" allows your Vercel frontend to pass cookies back to your Render backend safely.
    response.set_cookie(
        key="refresh_token",
        value=token_string,
        httponly=True,
        secure=True,         # strictly required when samesite is declared as none
        samesite="none",     # Allows cross-domain cookie context transportation pipelines
        max_age=604800,      # 7 Days lifespan
        expires=expire_time, 
        path="/"            
    )

# ============================================
# SIGNUP LAYER
# ============================================
def signup_user(db: Session, request):
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

        send_verification_email(
            to_email=existing.email,
            token=existing.email_verification_token
        )
        return {"message": "Verification email resent"}

    verification_token = secrets.token_urlsafe(32)
    verification_expiry = datetime.utcnow() + timedelta(hours=24)

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

    workspace = Workspace(
        name=f"{request.name}'s Workspace",
        slug=f"{request.name.lower().replace(' ','-')}-{secrets.token_hex(3)}",
        type="personal",
        owner_id=user.id
    )

    db.add(workspace)
    db.flush()

    membership = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=user.id,
        role="admin"
    )
    db.add(membership)

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

    subscription = WorkspaceSubscription(
        workspace_id=workspace.id,
        plan_id=free_plan.id,
        status="active"
    )
    db.add(subscription)

    db.commit()
    db.refresh(user)
    db.refresh(workspace)

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
# LOGIN LAYER
# ============================================
def login_user(db: Session, request, response: Response):
    user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account deactivated")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")

    memberships = (
        db.query(WorkspaceMember)
        .filter(WorkspaceMember.user_id == user.id)
        .all()
    )

    if not memberships:
        raise HTTPException(status_code=403, detail="No workspace membership found")

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

    access_payload = {
        "sub": str(user.id),
        "exp": datetime.utcnow() + timedelta(minutes=15)
    }
    access_token = jwt.encode(access_payload, SECRET_KEY, algorithm=ALGORITHM)

    refresh_token_string = secrets.token_urlsafe(64)
    refresh_expiry = datetime.utcnow() + timedelta(days=7)

    db_refresh_token = RefreshToken(
        user_id=user.id,
        token_id=refresh_token_string,
        expires_at=refresh_expiry,
        created_at=datetime.utcnow() # Guarantees base metrics tracking hooks are available
    )
    db.add(db_refresh_token)
    db.commit()

    set_secure_refresh_cookie(response, refresh_token_string)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(user.id),
        "workspace_id": str(default_membership.workspace_id),
        "role": default_membership.role,
        "workspaces": workspace_list,
        "message": "Authentication successful"
    }

# ============================================
# REFRESH TOKEN ROTATION (RTR) 🛡️
# ============================================
def refresh_access_token(db: Session, refresh_token: str, response: Response):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token cookie missing")

    token_record = (
        db.query(RefreshToken)
        .filter(RefreshToken.token_id == refresh_token)
        .first()
    )

    if not token_record:
        raise HTTPException(status_code=401, detail="Refresh token invalid or missing")

    # ✅ FIXED FOR DASHBOARD CONCURRENCY RACE CONDITIONS:
    # If a token has already been revoked, check if it happened in the last 10 seconds.
    # If yes, treat this as a safe concurrent dashboard loading request and pass it through smoothly.
    if token_record.revoked:
        updated_time = getattr(token_record, "updated_at", None) or getattr(token_record, "created_at", datetime.utcnow())
        if datetime.utcnow() - updated_time > timedelta(seconds=10):
            db.query(RefreshToken).filter(RefreshToken.user_id == token_record.user_id).update({"revoked": True})
            db.commit()
            raise HTTPException(status_code=401, detail="Security Warning: Token reuse detected. Session revoked.")
        
        # Safe Pass-Through Loop: Query and return a fresh access payload mapping to the same user credentials
        new_access_payload = {
            "sub": str(token_record.user_id),
            "exp": datetime.utcnow() + timedelta(mminutes=15)
        }
        return {
            "access_token": jwt.encode(new_access_payload, SECRET_KEY, algorithm=ALGORITHM),
            "token_type": "bearer"
        }

    if token_record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Refresh token expired")

    # Update active record states cleanly
    token_record.revoked = True
    if hasattr(token_record, "updated_at"):
        token_record.updated_at = datetime.utcnow()
    db.flush()

    new_refresh_string = secrets.token_urlsafe(64)
    new_refresh_expiry = datetime.utcnow() + timedelta(days=7)

    new_db_token = RefreshToken(
        user_id=token_record.user_id,
        token_id=new_refresh_string,
        expires_at=new_refresh_expiry,
        created_at=datetime.utcnow()
    )
    db.add(new_db_token)
    db.commit()

    set_secure_refresh_cookie(response, new_refresh_string)

    new_access_payload = {
        "sub": str(token_record.user_id),
        "exp": datetime.utcnow() + timedelta(minutes=15)
    }
    return {
        "access_token": jwt.encode(new_access_payload, SECRET_KEY, algorithm=ALGORITHM),
        "token_type": "bearer"
    }

# ============================================
# SECURE WEBSOCKET ONE-TIME TICKET ENGINE
# ============================================
def issue_websocket_ticket(user_id: str) -> str:
    ticket = secrets.token_urlsafe(32)
    WEBSOCKET_TICKET_STORE[ticket] = {
        "user_id": str(user_id),
        "expires_at": datetime.utcnow() + timedelta(seconds=10)
    }
    return ticket

# ============================================
# LOGOUT SYSTEM
# ============================================
def logout_user(db: Session, refresh_token: str, response: Response):
    if refresh_token:
        token_record = (
            db.query(RefreshToken)
            .filter(RefreshToken.token_id == refresh_token)
            .first()
        )
        if token_record:
            token_record.revoked = True
            db.commit()

    # ✅ FIXED FOR LOGOUT SEPARATION: Clear using matching samesite configuration fields
    response.delete_cookie(
        key="refresh_token", 
        path="/",
        samesite="none",
        secure=True
    )
    return {"message": "Logged out successfully"}

# ============================================
# VERIFY EMAIL
# ============================================
def verify_user_email(db: Session, token: str):
    user = (
        db.query(User)
        .filter(User.email_verification_token == token)
        .first()
    )

    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")

    if user.email_verification_expiry < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Verification token expired")

    user.is_verified = True
    user.email_verification_token = None
    user.email_verification_expiry = None
    db.commit()

    return {"message": "Email verified successfully"}

# ============================================
# REQUEST PASSWORD RESET (FORGOT PASSWORD)
# ============================================
def request_password_reset(db: Session, request):
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
def reset_password(db: Session, request):
    user = (
        db.query(User)
        .filter(User.reset_password_token == request.token)
        .first()
    )

    if not user:
        raise HTTPException(status_code=400, detail="Invalid reset token")

    if not user.reset_password_expires or user.reset_password_expires < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Reset token expired or invalid")

    user.password_hash = hash_password(request.new_password)
    user.reset_password_token = None
    user.reset_password_expires = None
    db.commit()

    return {"message": "Password reset successful"}

# ============================================
# AUTHENTICATE USER
# ============================================
def authenticate_user(db: Session, token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User unauthorized or deactivated")

    return user