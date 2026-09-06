from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.models.workspace_config import WorkspaceConfig
from app.core.encryption import encrypt_vault_secret

# Import your existing security boundaries
from app.api.deps_user import get_current_user
from app.core.workspace_access import get_workspace_membership
from app.services.feature_access import require_feature

router = APIRouter(tags=["Database Onboarding"])

# Helper function matching your dashboard.py logic
def validate_feature_access(db: Session, workspace_id: str, feature_name: str):
    from app.models.workspace import Workspace
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    require_feature(workspace, feature_name)

# ---------------------------------------------------------------------
# PAYLOAD SCHEMA
# ---------------------------------------------------------------------
class DBConnectionPayload(BaseModel):
    db_type: str
    db_host: str
    db_port: int
    db_name: str
    db_username: str
    db_password: str
    jwks_url: str
    sync_all_tables: bool
    allowed_tables: List[str] = []

# ---------------------------------------------------------------------
# THE ONBOARDING ENDPOINT
# ---------------------------------------------------------------------
@router.post("/connect")
def connect_live_database(
    payload: DBConnectionPayload,
    workspace_id: str = Header(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. 🛡️ ROLE-BASED ACCESS CONTROL (Admin or Operator only)
    membership = get_workspace_membership(
        db=db, 
        user_id=current_user.id, 
        workspace_id=workspace_id
    )
    
    if membership.role not in ["admin", "operator"]:
        raise HTTPException(
            status_code=403, 
            detail="Insufficient permissions. Only Admins and Operators can link live databases."
        )

    # 2. 💎 SUBSCRIPTION / PLAN CHECK
    # Ensure they are on a plan that allows the Live SQL Database feature
    validate_feature_access(
        db,
        workspace_id,
        "live_database_sync"  # Match this string to whatever you name the feature in your DB
    )

    # 3. 🚦 TABLE SCOPE VALIDATION
    if not payload.sync_all_tables and not payload.allowed_tables:
        raise HTTPException(
            status_code=400, 
            detail="If not syncing all tables, you must provide a list of specific allowed tables."
        )

    # 4. 🔒 ENCRYPT PASSWORD (Zero-Retention)
    encrypted_pass = encrypt_vault_secret(payload.db_password)

    # 5. 💾 SAVE TO WORKSPACE CONFIG
    config = db.query(WorkspaceConfig).filter_by(workspace_id=workspace_id).first()
    
    if config:
        config.db_type = payload.db_type
        config.db_host = payload.db_host
        config.db_port = payload.db_port
        config.db_name = payload.db_name
        config.db_username = payload.db_username
        config.db_password_encrypted = encrypted_pass
        config.jwks_url = payload.jwks_url
        config.sync_all_tables = payload.sync_all_tables
        config.allowed_tables = payload.allowed_tables
    else:
        config = WorkspaceConfig(
            workspace_id=workspace_id,
            db_type=payload.db_type,
            db_host=payload.db_host,
            db_port=payload.db_port,
            db_name=payload.db_name,
            db_username=payload.db_username,
            db_password_encrypted=encrypted_pass,
            jwks_url=payload.jwks_url,
            sync_all_tables=payload.sync_all_tables,
            allowed_tables=payload.allowed_tables
        )
        db.add(config)

    db.commit()

    return {
        "status": "success", 
        "message": "Database connected securely. AI is now indexing your schema."
    }