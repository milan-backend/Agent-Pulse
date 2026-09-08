import os
import chromadb
from fastapi import APIRouter, Depends, HTTPException, Header, Query
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
from app.tasks.schema_tasks import sync_database_schemas

router = APIRouter()

def validate_feature_access(db: Session, workspace_id: str, feature_name: str):
    from app.models.workspace import Workspace
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    require_feature(workspace, feature_name)

# ====================================================================
# SECURE CHROMA HTTP CLIENT HELPER 
# ====================================================================
def get_chroma_client():
    chroma_host = os.getenv("CHROMA_HOST")
    chroma_token = os.getenv("CHROMA_TOKEN")
    
    if not chroma_host:
        raise ValueError("CRITICAL CONFIGURATION ERROR: CHROMA_HOST environment variable is missing.")
    
    chroma_host = str(chroma_host).strip().rstrip("/")
    
    return chromadb.HttpClient(
        host=chroma_host,
        headers={"Authorization": f"Bearer {chroma_token}"} if chroma_token else None
    )

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


# ====================================================================
# 1. CREATE / UPDATE CONNECTION (POST)
# ====================================================================
@router.post("/connect")
def connect_live_database(
    payload: DBConnectionPayload,
    workspace_id: str = Header(...),
    agent_id: str = Query(..., description="The ID of the target agent"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. ROLE-BASED ACCESS CONTROL
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

    # 2. SUBSCRIPTION / PLAN CHECK
    validate_feature_access(
        db,
        workspace_id,
        "live_database_sync"
    )

    # 3. TABLE SCOPE VALIDATION
    if not payload.sync_all_tables and not payload.allowed_tables:
        raise HTTPException(
            status_code=400, 
            detail="If not syncing all tables, you must provide a list of specific allowed tables."
        )

    # 4. ENCRYPT PASSWORD
    encrypted_pass = encrypt_vault_secret(payload.db_password)

    # 5. SAVE TO CONFIG (Scoped to Workspace AND Agent)
    config = db.query(WorkspaceConfig).filter_by(
        workspace_id=workspace_id,
        agent_id=agent_id
    ).first()
    
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
            agent_id=agent_id,
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

    # Fire the background worker, passing the agent_id context
    sync_database_schemas.delay(workspace_id=workspace_id, agent_id=agent_id)

    return {
        "status": "success", 
        "message": "Database connected securely. AI is now indexing your schema."
    }


# ====================================================================
# 2. GET ACTIVE CONNECTIONS (GET)
# ====================================================================
@router.get("/connections")
def list_database_connections(
    workspace_id: str = Header(...),
    agent_id: str = Query(..., description="The ID of the target agent"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Enforce Operator-level access
    membership = get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=workspace_id
    )
    if membership.role not in ["admin", "operator"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions.")

    # Fetch connections scoped to Workspace AND Agent
    connections = db.query(WorkspaceConfig).filter_by(
        workspace_id=workspace_id,
        agent_id=agent_id
    ).all()
    
    # Strip sensitive data (Never send passwords to the frontend)
    safe_connections = []
    for conn in connections:
        safe_connections.append({
            "id": str(conn.id),
            "db_type": conn.db_type,
            "db_name": conn.db_name,
            "db_host": conn.db_host,
            "db_user": conn.db_username,
            "sync_all_tables": conn.sync_all_tables
        })
        
    return safe_connections


# ====================================================================
# 3. DELETE A CONNECTION (DELETE)
# ====================================================================
@router.delete("/connections/{connection_id}")
def delete_database_connection(
    connection_id: str,
    workspace_id: str = Header(...),
    agent_id: str = Query(..., description="The ID of the target agent"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Enforce Admin-only access for deletions
    membership = get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=workspace_id
    )
    if membership.role != "admin":
        raise HTTPException(status_code=403, detail="Only Admins can delete database connections.")
    
    # Verify connection belongs to this workspace and agent
    connection = db.query(WorkspaceConfig).filter_by(
        id=connection_id,
        workspace_id=workspace_id,
        agent_id=agent_id
    ).first()
    
    if not connection:
        raise HTTPException(status_code=404, detail="Database connection not found.")
        
    # Delete from PostgreSQL
    db.delete(connection)
    db.commit()
    
    # Clean up ChromaDB (Delete only this agent's schemas)
    try:
        chroma_client = get_chroma_client()
        collection = chroma_client.get_collection(name="rag_enterprise_vectors_v1")
        
        if collection:
            collection.delete(
                where={
                    "$and": [
                        {"workspace_id": str(workspace_id)},
                        {"agent_id": str(agent_id)},
                        {"content_type": "db_schema"}
                    ]
                }
            )
            print(f"✅ Successfully deleted agent schema vectors from ChromaDB for agent {agent_id}.")
        
    except Exception as e:
        print(f"⚠️ Warning: Failed to clean up ChromaDB schema vectors: {e}")
    
    return {"success": True, "message": "Database connection securely deleted."}