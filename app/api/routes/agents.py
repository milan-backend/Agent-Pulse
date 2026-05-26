from fastapi import (
    APIRouter,
    Depends,
    Header
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.models.user import User

from app.schemas.agent import (
    AgentCreateRequest,
    AgentCreateResponse,
    AgentPolicyUpdateRequest
)

from app.api.deps_user import (
    get_current_user
)

from app.core.workspace_access import (
    get_workspace_membership
)

from app.api.rbac import (
    require_admin,
    require_operator
)

from app.services.agent_service import (
    create_agent_service,
    regenerate_agent_api_key,
    update_agent_policy_service
)

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

    current_user: User = Depends(
        get_current_user
    )
):

    # VALIDATE MEMBERSHIP

    membership = (
        get_workspace_membership(
            db=db,
            user_id=current_user.id,
            workspace_id=workspace_id
        )
    )

    # REQUIRE OPERATOR

    require_operator(membership)

    return create_agent_service(
        db=db,
        workspace_id=workspace_id,
        current_user=current_user,
        request=request
    )


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

    current_user: User = Depends(
        get_current_user
    )
):

    # VALIDATE MEMBERSHIP

    membership = (
        get_workspace_membership(
            db=db,
            user_id=current_user.id,
            workspace_id=workspace_id
        )
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

    current_user: User = Depends(
        get_current_user
    )
):

    # VALIDATE MEMBERSHIP

    membership = (
        get_workspace_membership(
            db=db,
            user_id=current_user.id,
            workspace_id=workspace_id
        )
    )

    # REQUIRE OPERATOR

    require_operator(membership)

    return update_agent_policy_service(
        db=db,
        workspace_id=workspace_id,
        agent_id=agent_id,
        request=request
    )