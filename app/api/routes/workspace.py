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
    UpdateRoleRequest,
    InviteMemberRequest,
    AcceptInviteRequest   
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
    remove_workspace_member,
    create_workspace_invitation,
    accept_workspace_invitation,
    get_active_workspace_invitations,
    expire_workspace_invitation
)

from app.utils.audit_handler import AuditLogRoute

router = APIRouter(route_class=AuditLogRoute)


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

# =========================
# GENERATE TEAM INVITATION
# =========================
@router.post("/invite-member")
def invite_member(
    payload: InviteMemberRequest,
    workspace_id: str = Header(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ Securely issues a workspace verification token loop and emails the teammate """
    # 1. Look up active membership parameters
    membership = get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=workspace_id
    )
    
    # 2. Reusing your strict built-in RBAC guard to enforce that only Admins can invite people!
    require_admin(membership)
    
    return create_workspace_invitation(
        db=db,
        workspace_id=workspace_id,
        inviter_id=current_user.id,
        payload=payload
    )


# =========================
# ACCEPT TEAM INVITATION (UPDATED & PUBLIC 🔓)
# =========================
@router.post("/accept-invite")
def accept_invite(
    payload: AcceptInviteRequest,
    db: Session = Depends(get_db)
    # 🟢 REMOVED: current_user dependency constraint parameter from here!
):
    """ Finalizes invitation handshakes without forcing a pre-authenticated session barrier """
    return accept_workspace_invitation(
        db=db,
        token=payload.token
        # 🟢 REMOVED: user_id and user_email pass-throughs
    )

# ==========================================
# GET ACTIVE PENDING INVITATIONS (ADMIN ONLY)
# ==========================================
@router.get("/invitations")
def get_workspace_invitations(
    workspace_id: str = Header(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ Fetches all unaccepted and unexpired invitations for this workspace """
    # 1. Reuse your built-in membership validator guard
    membership = get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=workspace_id
    )
    
    # 2. Reuse your absolute RBAC check to ensure only Admins can query this data stream
    require_admin(membership)
    
    return get_active_workspace_invitations(db=db, workspace_id=workspace_id)


# ==========================================
# REVOKE/EXPIRE PENDING INVITATION (ADMIN ONLY)
# ==========================================
@router.delete("/invitations/{invitation_id}")
def revoke_member_invitation(
    invitation_id: str,
    workspace_id: str = Header(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ Instantly revokes and soft-expires a pending workspace invitation link """
    # 1. Reuse your built-in membership validator guard
    membership = get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=workspace_id
    )
    
    # 2. Reuse your absolute RBAC check to ensure only Admins can run this deletion block
    require_admin(membership)
    
    return expire_workspace_invitation(
        db=db, 
        workspace_id=workspace_id, 
        invitation_id=invitation_id
    )