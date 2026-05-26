from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Header
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.models.user import User

from app.schemas.workspace import (
    AddMemberRequest,
    UpdateRoleRequest
)

from app.api.deps_user import (
    get_current_user
)

from app.core.workspace_access import (
    get_workspace_membership
)

from app.api.rbac import (
    require_admin
)

from app.services.workspace_service import (
    add_workspace_member,
    update_workspace_member_role,
    get_workspace_members,
    remove_workspace_member
)

router = APIRouter()


# =========================
# ADD MEMBER
# =========================

@router.post("/add-member")
def add_member(

    payload: AddMemberRequest,

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

    return add_workspace_member(
        db=db,
        workspace_id=workspace_id,
        payload=payload
    )


# =========================
# UPDATE MEMBER ROLE
# =========================

@router.patch("/members/role")
def update_member_role(

    payload: UpdateRoleRequest,

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

    return update_workspace_member_role(
        db=db,
        workspace_id=workspace_id,
        payload=payload
    )


# =========================
# GET MEMBERS
# =========================

@router.get("/members")
def get_members(

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

    # REQUIRE MEMBERSHIP

    if not membership:

        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    return get_workspace_members(
        db=db,
        workspace_id=workspace_id
    )


# =========================
# DELETE MEMBER
# =========================

@router.delete("/members/{user_id}")
def delete_workspace_member(

    user_id: str,

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

    return remove_workspace_member(
        db=db,
        workspace_id=workspace_id,
        user_id=user_id
    )