from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from sqlalchemy.orm import Session
from google import genai
from typing import Optional
from uuid import UUID

from app.db.session import get_db
from app.models.user import User
from app.api.deps_user import get_current_user
from app.core.workspace_access import get_workspace_membership
from app.models.user_api_key import UserAPIKey 
from app.core.crypto import decrypt_api_key
from app.api.rbac import require_admin, require_operator

from app.schemas.user_api_key import UserAPIKeyCreate, UserAPIKeyResponse
from app.services.user_api_key_service import UserAPIKeyService

router = APIRouter()


# ============================================
# CONNECT API KEY (Admin / Operator required)
# ============================================
@router.post("/connect", response_model=UserAPIKeyResponse, status_code=status.HTTP_201_CREATED)
def connect_provider_key(
    payload: UserAPIKeyCreate,               # JSON body: provider, api_key, model_version
    workspace_id: str = Header(...),         # STRICT BOUNDARY: Made strictly mandatory
    agent_id: Optional[str] = Query(None),   # agent_id is purely a URL parameter
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint to validate, encrypt, and save an AI Provider API Key securely.
    """
    # 1. Clean and convert provider strings to simple lowercase ('openai' / 'gemini')
    raw_provider = payload.provider.strip().lower()
    target_provider = "openai" if "openai" in raw_provider else "gemini"

    # 2. Enforce absolute workspace UUID parsing
    try:
        clean_ws_id = UUID(str(workspace_id).strip())
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid workspace_id UUID format.")

    clean_agent_id = None
    if agent_id and str(agent_id).strip() not in ["", "null", "None"]:
        try:
            clean_agent_id = UUID(str(agent_id).strip())
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid agent_id UUID format.")

    # 3. Validate membership and role parameters strictly to prevent unauthorized access
    membership = get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=clean_ws_id
    )
    # Require Operator or Admin role permissions to add or update workspace configurations
    require_operator(membership)

    # 4. Google GenAI SDK Verification Handshake
    if target_provider == "gemini":
        try:
            test_client = genai.Client(api_key=payload.api_key)
            test_client.models.list() 
        except Exception as auth_err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid Gemini API Key: Connection verification failed. ({str(auth_err)})"
            )

    # 5. Route through service layer matching our architectural model updates
    try:
        saved_key = UserAPIKeyService.store_key(
            db=db,
            provider=target_provider, 
            raw_key=payload.api_key,
            user_id=current_user.id,
            workspace_id=clean_ws_id,
            agent_id=clean_agent_id,          
            model_version=payload.model_version
        )
        
        return {
            "id": saved_key.id,
            "provider": saved_key.provider,
            "message": f"Successfully validated and connected credentials for {saved_key.provider}.",
            "model_version": saved_key.model_version,
            "workspace_id": saved_key.workspace_id,
            "agent_id": saved_key.agent_id,
            "is_default": saved_key.is_default
        }
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_err))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal database failure: {str(e)}"
        )


# ============================================
# GET KEY CONFIGURATION STATUS METADATA
# ============================================
@router.get("/status", status_code=status.HTTP_200_OK)
def get_key_status(
    provider: str = Query("gemini"),
    workspace_id: str = Header(...),         # STRICT BOUNDARY: Made strictly mandatory
    agent_id: Optional[str] = Query(None),
    model_version: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns safe cryptographic metadata regarding saved keys matching the active provider string.
    """
    try:
        clean_ws_id = UUID(str(workspace_id).strip())
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid workspace_id UUID format.")

    clean_agent_id = None
    if agent_id and str(agent_id).strip() not in ["", "null", "None"]:
        try:
            clean_agent_id = UUID(str(agent_id).strip())
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid agent_id UUID format.")

    # Enforce clear data visibility barriers across scopes
    get_workspace_membership(db=db, user_id=current_user.id, workspace_id=clean_ws_id)
        
    raw_provider = str(provider).strip().lower()
    target_provider = "openai" if "openai" in raw_provider else "gemini"
    
    # Structural isolation lookup query matching step_tasks processing flow
    query = db.query(UserAPIKey).filter(
        UserAPIKey.provider == target_provider,
        UserAPIKey.workspace_id == clean_ws_id
    )
    
    if clean_agent_id:
        query = query.filter(UserAPIKey.agent_id == clean_agent_id)
    else:
        query = query.filter(UserAPIKey.agent_id == None)
        if model_version and model_version.strip() not in ["", "null", "None"]:
            query = query.filter(UserAPIKey.model_version == model_version.strip())
        
    key_record = query.first()
    
    if not key_record:
        return {
            "connected": False, 
            "provider": target_provider,
            "model_version": model_version,
            "agent_id": agent_id
        }
        
    masked_key = "Connected"
    if key_record.encrypted_api_key:
        try:
            raw = decrypt_api_key(key_record.encrypted_api_key)
            if len(raw) > 10:
                masked_key = f"{raw[:6]}************{raw[-3:]}"
        except Exception:
            masked_key = "Connected"

    last_updated = "Recent"
    if hasattr(key_record, "updated_at") and key_record.updated_at:
        last_updated = key_record.updated_at.strftime("%d %b %Y")

    return {
        "id": key_record.id,
        "connected": True,
        "provider": key_record.provider,
        "model_version": key_record.model_version,
        "masked_key": masked_key,
        "last_updated": last_updated,
        "is_default": key_record.is_default,
        "workspace_id": key_record.workspace_id,
        "agent_id": key_record.agent_id,
        "owner_context": "Workspace Managed"
    }


# ============================================
# DISCONNECT API KEY (Admin / Operator required)
# ============================================
@router.delete("/disconnect", status_code=status.HTTP_200_OK)
def disconnect_provider_key(
    provider: str,
    workspace_id: str = Header(...),         # STRICT BOUNDARY: Made strictly mandatory
    agent_id: Optional[str] = Query(None),
    model_version: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    raw_provider = provider.strip().lower()
    target_provider = "openai" if "openai" in raw_provider else "gemini"

    try:
        clean_ws_id = UUID(str(workspace_id).strip())
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid workspace_id UUID format.")

    clean_agent_id = None
    if agent_id and str(agent_id).strip() not in ["", "null", "None"]:
        try:
            clean_agent_id = UUID(str(agent_id).strip())
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid agent_id UUID format.")

    # Validate deletion authorizations safely
    membership = get_workspace_membership(db=db, user_id=current_user.id, workspace_id=clean_ws_id)
    require_operator(membership)

    success = UserAPIKeyService.remove_key(
        db=db,
        provider=target_provider,
        workspace_id=clean_ws_id,
        agent_id=clean_agent_id,
        model_version=model_version.strip() if model_version else None
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active credentials found for provider '{target_provider}' matching requested scope."
        )
        
    return {"message": f"Successfully removed integration configurations for {target_provider}."}


# ============================================
# SET DEFAULT PROVIDER CONFIGURATION (Admin required)
# ============================================
@router.patch("/set-default", status_code=status.HTTP_200_OK)
def set_default_provider(
    provider: str,
    workspace_id: str = Header(...),         # STRICT BOUNDARY: Made strictly mandatory
    model_version: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        clean_ws_id = UUID(str(workspace_id).strip())
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid workspace_id UUID format.")

    # Require explicit admin membership status to execute global fallback changes
    membership = get_workspace_membership(db=db, user_id=current_user.id, workspace_id=clean_ws_id)
    require_admin(membership)

    raw_provider = str(provider).strip().lower()
    target_provider = "openai" if "openai" in raw_provider else "gemini"

    # Standardize updating the database context smoothly
    base_query = db.query(UserAPIKey).filter(
        UserAPIKey.agent_id == None,
        UserAPIKey.workspace_id == clean_ws_id
    )

    # Wipe existing active defaults across the workspace scope smoothly
    base_query.update({"is_default": False}, synchronize_session=False)

    target_query = base_query.filter(UserAPIKey.provider == target_provider)
    if model_version and model_version.strip() not in ["", "null", "None"]:
        target_query = target_query.filter(UserAPIKey.model_version == model_version.strip())
        
    target_record = target_query.first()

    if not target_record:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cannot set default active layer. No connected key found for provider: '{target_provider}'"
        )

    target_record.is_default = True
    db.commit()

    return {
        "status": "success",
        "message": f"{target_provider} designated as default pipeline platform.",
        "provider": target_record.provider,
        "model_version": target_record.model_version
    }