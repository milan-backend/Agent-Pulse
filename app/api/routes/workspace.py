from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Header
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_member import (
    WorkspaceMember
)

from app.schemas.workspace import (
    AddMemberRequest,
    UpdateRoleRequest
)

from app.api.deps_user import (
    get_current_user
)

from app.api.routes.workspace_access import (
    get_workspace_membership
)

from app.api.rbac import (
    require_admin
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

    # FIND TARGET USER

    target_user = (
        db.query(User)
        .filter(
            User.email == payload.email
        )
        .first()
    )

    if not target_user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # PREVENT DUPLICATE MEMBERSHIP

    existing = (
        db.query(WorkspaceMember)
        .filter(
            WorkspaceMember.workspace_id
            == workspace_id,

            WorkspaceMember.user_id
            == target_user.id
        )
        .first()
    )

    if existing:

        raise HTTPException(
            status_code=400,
            detail=(
                "User already added "
                "to workspace"
            )
        )

    # CREATE MEMBERSHIP

    member = WorkspaceMember(

        workspace_id=workspace_id,

        user_id=target_user.id,

        role=payload.role.value
    )

    db.add(member)

    db.commit()

    db.refresh(member)

    return {

        "success": True,

        "message":
            "Member added successfully",

        "member": {

            "email":
                target_user.email,

            "role":
                member.role
        }
    }


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

    # FIND TARGET USER

    target_user = (
        db.query(User)
        .filter(
            User.email == payload.email
        )
        .first()
    )

    if not target_user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # FIND MEMBERSHIP

    target_membership = (
        db.query(WorkspaceMember)
        .filter(
            WorkspaceMember.workspace_id
            == workspace_id,

            WorkspaceMember.user_id
            == target_user.id
        )
        .first()
    )

    if not target_membership:

        raise HTTPException(
            status_code=404,
            detail="Membership not found"
        )

    # UPDATE ROLE

    target_membership.role = (
        payload.role.value
    )

    db.commit()

    db.refresh(target_membership)

    return {

        "success": True,

        "message":
            "Role updated successfully",

        "email":
            target_user.email,

        "new_role":
            target_membership.role
    }


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

    # GET MEMBERS

    members = (
        db.query(WorkspaceMember)
        .filter(
            WorkspaceMember.workspace_id
            == workspace_id
        )
        .all()
    )

    result = []

    for member in members:

        user = (
            db.query(User)
            .filter(
                User.id == member.user_id
            )
            .first()
        )

        result.append({

            "user_id":
                str(user.id),

            "name":
                user.name,

            "email":
                user.email,

            "role":
                member.role
        })

    return {

        "success": True,

        "members": result
    }


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

    # FIND MEMBER

    member = (
        db.query(WorkspaceMember)
        .filter(
            WorkspaceMember.user_id
            == user_id,

            WorkspaceMember.workspace_id
            == workspace_id
        )
        .first()
    )

    if not member:

        raise HTTPException(
            status_code=404,
            detail="Member not found"
        )

    # PREVENT OWNER DELETE

    workspace = (
        db.query(Workspace)
        .filter(
            Workspace.id == workspace_id
        )
        .first()
    )

    if str(workspace.owner_id) == str(user_id):

        raise HTTPException(
            status_code=400,
            detail=(
                "Cannot remove "
                "workspace owner"
            )
        )

    db.delete(member)

    db.commit()

    return {

        "success": True,

        "message":
            "Member removed successfully"
    }