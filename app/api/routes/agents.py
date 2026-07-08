from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    status
)
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.models.user import User
from app.models.agent import Agent  # Imported to execute the metadata updates
from app.schemas.agent import (
    AgentCreateRequest,
    AgentCreateResponse,
    AgentPolicyUpdateRequest,
    AgentUpdateRequest
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
from app.services.step_service import get_agent_pipeline_history


from app.utils.audit_handler import AuditLogRoute

router = APIRouter(route_class=AuditLogRoute)


# ============================================
# CREATE AGENT
# ============================================
@router.post(
    "/",
    response_model=AgentCreateResponse
)
def create_agent(
    request: AgentCreateRequest,
    workspace_id: str = Header(...),  # STRICT BOUNDARY: Mandatory Header
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        clean_ws_id = UUID(str(workspace_id).strip())
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid workspace_id UUID format.")

    # VALIDATE MEMBERSHIP
    membership = get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=clean_ws_id
    )

    # REQUIRE OPERATOR
    require_operator(membership)

    return create_agent_service(
        db=db,
        workspace_id=str(clean_ws_id),
        current_user=current_user,
        request=request
    )


# ============================================
# REGENERATE API KEY
# ============================================
@router.post(
    "/regenerate-key/{agent_id}"
)
def require_api_key(
    agent_id: str,
    workspace_id: str = Header(...),  # STRICT BOUNDARY: Mandatory Header
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        clean_ws_id = UUID(str(workspace_id).strip())
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid workspace_id UUID format.")

    # VALIDATE MEMBERSHIP
    membership = get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=clean_ws_id
    )

    # REQUIRE ADMIN
    require_admin(membership)

    return regenerate_agent_api_key(
        db=db,
        workspace_id=str(clean_ws_id),
        agent_id=agent_id
    )


# ============================================
# UPDATE AGENT POLICY
# ============================================
@router.put("/{agent_id}")
def update_agent(
    agent_id: str,
    request: AgentPolicyUpdateRequest,
    workspace_id: str = Header(...),  # STRICT BOUNDARY: Mandatory Header
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        clean_ws_id = UUID(str(workspace_id).strip())
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid workspace_id UUID format.")

    # VALIDATE MEMBERSHIP
    membership = get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=clean_ws_id
    )

    # REQUIRE OPERATOR
    require_operator(membership)

    return update_agent_policy_service(
        db=db,
        workspace_id=str(clean_ws_id),
        agent_id=agent_id,
        request=request
    )


# ============================================
# PATCH AGENT CONFIGURATIONS / METADATA
# ============================================
@router.patch("/{agent_id}", status_code=status.HTTP_200_OK)
def update_agent_settings(
    agent_id: str,
    request: AgentUpdateRequest,
    workspace_id: str = Header(...),  # STRICT BOUNDARY: Mandatory Header
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint for updating core agent basic metadata (like names/descriptions/model dropdown values) safely.
    All infrastructure provider keys are handled securely by the dedicated user_api_key routing system.
    """
    try:
        clean_ws_id = UUID(str(workspace_id).strip())
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid workspace_id UUID format.")

    # 1. VALIDATE MEMBERSHIP & SCOPE BOUNDARIES FIRST
    membership = get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=clean_ws_id
    )

    # REQUIRE OPERATOR
    require_operator(membership)

    # 2. FETCH THE REAL AGENT OBJECT 
    # Self-Healing Type-Cast Check: Supports database string representations or direct UUID structural formats safely.
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.workspace_id.in_([clean_ws_id, str(clean_ws_id).strip()])
    ).first()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Agent context missing or cross-workspace access forbidden."
        )

    # 3. DYNAMICALLY APPLY PRIMITIVE UPDATES FROM DROPDOWN/INPUTS
    update_data = request.dict(exclude_unset=True) # Only updates what the frontend explicitly passes
    
    for key, value in update_data.items():
        setattr(agent, key, value)

    db.commit()
    db.refresh(agent)

    return {
        "status": "success",
        "message": "Agent metadata settings updated successfully.",
        "agent": {
            "id": agent.id,
            "name": getattr(agent, "name", None),
            "model_name": getattr(agent, "model_name", None)
        }
    }

# ============================================
# FETCH AGENT PIPELINES PIPES MONITOR STREAM
# ============================================
@router.get("/{agent_id}/pipelines", status_code=status.HTTP_200_OK)
def read_agent_execution_pipelines(
    agent_id: str,
    status: str = None,
    search: str = None,
    workspace_id: str = Header(...), # Reuses your strict header validation gate
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ Exposes pipeline execution trails filtered by status/task names for the agent monitor panel """
    try:
        clean_ws_id = UUID(str(workspace_id).strip())
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid workspace_id UUID format.")

    # 1. Enforce active membership bounds check natively
    membership = get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=clean_ws_id
    )
    
    # 2. Reusing your built-in Operator clearance validator check
    require_operator(membership)
    
    # 3. Stream data right from our step history execution matrix layer
    return get_agent_pipeline_history(
        db=db,
        agent_id=agent_id,
        workspace_id=str(clean_ws_id),
        status=status,
        search=search
    )