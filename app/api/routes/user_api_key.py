from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from google import genai
from typing import Optional

from app.db.session import get_db
from app.models.user import User
from app.api.deps_user import get_current_user
from app.core.workspace_access import get_workspace_membership
from app.models.user_api_key import UserAPIKey 
from app.core.crypto import decrypt_api_key

# Import BOTH require_admin for locking down modifications and require_operator for internal verification helpers if needed
from app.api.rbac import require_admin

from app.schemas.user_api_key import UserAPIKeyCreate, UserAPIKeyResponse
from app.services.user_api_key_service import UserAPIKeyService

router = APIRouter()


# ============================================
# CONNECT API KEY (STRICT ADMIN ONLY FOR WS)
# ============================================
@router.post("/connect", response_model=UserAPIKeyResponse, status_code=status.HTTP_201_CREATED)
def connect_provider_key(
    payload: UserAPIKeyCreate,
    workspace_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint to validate, encrypt, and save an AI Provider API Key securely.
    STRICT SECURITY: Enforces that only an ADMIN can configure keys for a workspace.
    """
    provider_clean = payload.provider.lower().strip()
    
    # Enforce strict Admin RBAC if workspace header context is present
    if workspace_id:
        membership = get_workspace_membership(
            db=db,
            user_id=current_user.id,
            workspace_id=workspace_id
        )
        require_admin(membership)  # Only Workspace Admin can write/update keys

    # Live verification with Google GenAI SDK
    if provider_clean == "gemini":
        try:
            test_client = genai.Client(api_key=payload.api_key)
            test_client.models.list(page_size=1)  # Lightweight authorization handshake
        except Exception as auth_err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid Gemini API Key: Connection verification failed with Google. ({str(auth_err)})"
            )

    try:
        UserAPIKeyService.store_key(
            db=db,
            provider=payload.provider,
            raw_key=payload.api_key,
            user_id=current_user.id if not workspace_id else None,
            workspace_id=workspace_id if workspace_id else None
        )
        return {
            "provider": payload.provider,
            "message": f"Successfully validated and connected credentials for {payload.provider}."
        }
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_err))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal database failure: {str(e)}"
        )


# ============================================
# DISCONNECT API KEY (STRICT ADMIN ONLY FOR WS)
# ============================================
@router.delete("/disconnect", status_code=status.HTTP_200_OK)
def disconnect_provider_key(
    provider: str,
    workspace_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint to completely remove an encrypted AI credentials configuration row.
    STRICT SECURITY: Enforces that only an ADMIN can disconnect keys for a workspace.
    """
    if workspace_id:
        membership = get_workspace_membership(
            db=db,
            user_id=current_user.id,
            workspace_id=workspace_id
        )
        require_admin(membership)  # Only Workspace Admin can remove keys

    success = UserAPIKeyService.remove_key(
        db=db,
        provider=provider,
        user_id=current_user.id if not workspace_id else None,
        workspace_id=workspace_id if workspace_id else None
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active credentials found for provider '{provider}'."
        )
        
    return {"message": f"Successfully removed integration configurations for {provider}."}


# ============================================
# GET KEY CONFIGURATION STATUS METADATA
# ============================================
@router.get("/status", status_code=status.HTTP_200_OK)
def get_key_status(
    provider: Optional[str] = "GEMINI_API_KEY", # Added to let frontend request gemini or openai dynamically
    workspace_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns safe cryptographic metadata regarding saved keys.
    Admins, Operators, and Viewers can all check status. Never exposes raw decrypted tokens.
    """
    # Anyone can check status if they belong to the workspace
    if workspace_id:
        get_workspace_membership(db=db, user_id=current_user.id, workspace_id=workspace_id)
        
    from app.models.user_api_key import UserAPIKey 
    
    # Check what target provider string name to look for cleanly
    target_provider = "OPENAI_API_KEY" if "openai" in provider.lower() else "GEMINI_API_KEY"
    
    query = db.query(UserAPIKey).filter(UserAPIKey.provider.ilike(target_provider))
    if workspace_id:
        query = query.filter(UserAPIKey.workspace_id == workspace_id)
    else:
        query = query.filter(UserAPIKey.user_id == current_user.id)
        
    key_record = query.first()
    
    if not key_record:
        return {"connected": False, "provider": "openai" if target_provider == "OPENAI_API_KEY" else "gemini"}
        
    # Safe Mask Generation for Personal Settings view
    masked_key = "Connected"
    if not workspace_id and key_record.encrypted_api_key:
        try:
            from app.core.crypto import decrypt_api_key
            raw = decrypt_api_key(key_record.encrypted_api_key)
            if len(raw) > 10:
                masked_key = f"{raw[:6]}************{raw[-3:]}"
        except Exception:
            masked_key = "Connected"

    # Pull record dates cleanly if columns exist, otherwise fall back gracefully
    last_updated = "Recent"
    if hasattr(key_record, "updated_at") and key_record.updated_at:
        last_updated = key_record.updated_at.strftime("%d %b %Y")
    elif hasattr(key_record, "created_at") and key_record.created_at:
        last_updated = key_record.created_at.strftime("%d %b %Y")

    return {
        "connected": True,
        "provider": "openai" if target_provider == "OPENAI_API_KEY" else "gemini",
        "masked_key": masked_key,
        "last_updated": last_updated,
        "owner_context": current_user.full_name if not workspace_id else "Workspace Managed"
    }