from fastapi import (
    APIRouter,
    Depends,
    Header,
    status,
    HTTPException
)
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.models.user import User
from app.schemas.agent import (
    AgentCreateRequest,
    AgentCreateResponse,
    AgentPolicyUpdateRequest,
    AgentUpdateRequest  # Imported our new general settings payload class
)
from app.api.deps_user import get_current_user
from app.core.workspace_access import get_workspace_membership
from app.api.rbac import (
    require_admin,
    require_operator
)
from app.services.agent_service import (
    create_agent_service,
    regenerate_agent_api_key,
    update_agent_policy_service
)
from app.services.user_api_key_service import UserAPIKeyService  # Connected our key service layer

router = APIRouter()


# ============================================
# CREATE AGENT
# ============================================
@router.post(
    "/",
    response_model=AgentCreateResponse
)
def create_agent(
    request: AgentCreateRequest,
    workspace_id: str = Header(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # VALIDATE MEMBERSHIP
    membership = get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=workspace_id
    )

    # REQUIRE OPERATOR
    require_operator(membership)

    # 1. Execute base system agent registration service loop
    new_agent_response = create_agent_service(
        db=db,
        workspace_id=workspace_id,
        current_user=current_user,
        request=request
    )

    # 2. Intercept payload and store custom agent credentials immediately if provided
    if request.agent_api_key and request.api_provider:
        try:
            # Parse string tokens into clean database matching UUIDs
            clean_ws_id = UUID(workspace_id.strip())
            clean_agent_id = UUID(new_agent_response.id.strip())
            
            UserAPIKeyService.store_key(
                db=db,
                provider=request.api_provider,
                raw_key=request.agent_api_key,
                user_id=None,
                workspace_id=clean_ws_id,      # Keeps it locked to this workspace context
                agent_id=clean_agent_id,        # Binds it exclusively to this unique agent
                model_version=request.model_version
            )
        except Exception as key_err:
            # Prevent schema failure if parsing fails, ensuring basic agent is preserved
            print(f"⚠️ Warning: Failed to automatically store initialization agent keys: {str(key_err)}")

    return new_agent_response


# ============================================
# REGENERATE API KEY
# ============================================
@router.post(
    "/regenerate-key/{agent_id}"
)
def regenerate_api_key(
    agent_id: str,
    workspace_id: str = Header(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # VALIDATE MEMBERSHIP
    membership = get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=workspace_id
    )

    # REQUIRE ADMIN
    require_admin(membership)

    return regenerate_agent_api_key(
        db=db,
        workspace_id=workspace_id,
        agent_id=agent_id
    )


# ============================================
# UPDATE AGENT POLICY
# ============================================
@router.put("/{agent_id}")
def update_agent(
    agent_id: str,
    request: AgentPolicyUpdateRequest,
    workspace_id: str = Header(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # VALIDATE MEMBERSHIP
    membership = get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=workspace_id
    )

    # REQUIRE OPERATOR
    require_operator(membership)

    return update_agent_policy_service(
        db=db,
        workspace_id=workspace_id,
        agent_id=agent_id,
        request=request
    )


# ============================================
# PATCH AGENT CONFIGURATIONS / TASK SETTINGS
# ============================================
@router.patch("/{agent_id}", status_code=status.HTTP_200_OK)
def update_agent_settings(
    agent_id: str,
    request: AgentUpdateRequest,
    workspace_id: str = Header(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint for updating generic agent configurations and task level 
    API provider credentials safely inside a protected multi-tenant sandbox workspace.
    """
    # VALIDATE MEMBERSHIP
    membership = get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=workspace_id
    )

    # REQUIRE OPERATOR
    require_operator(membership)

    try:
        clean_ws_id = UUID(workspace_id.strip())
        clean_agent_id = UUID(agent_id.strip())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid workspace_id or agent_id structural UUID format."
        )

    # 1. Update infrastructure level routing keys if provided in settings body
    if request.agent_api_key and request.api_provider:
        # If a non-empty key token string is sent, store or refresh it cleanly
        UserAPIKeyService.store_key(
            db=db,
            provider=request.api_provider,
            raw_key=request.agent_api_key,
            user_id=None,
            workspace_id=clean_ws_id,
            agent_id=clean_agent_id,
            model_version=request.model_version
        )
    elif request.api_provider and request.agent_api_key == "":
        # If the key is an empty string, wipe out the record so it falls back to workspace settings
        UserAPIKeyService.remove_key(
            db=db,
            provider=request.api_provider,
            user_id=None,
            workspace_id=clean_ws_id,
            agent_id=clean_agent_id,
            model_version=request.model_version
        )

    # Note: If your agent model requires saving other primitive properties (like updating name),
    # call your database query operations or core repository update calls here!

    return {
        "status": "success",
        "message": "Agent task connection settings updated successfully."
    }