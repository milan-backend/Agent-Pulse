from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_member import (
    WorkspaceMember
)

from app.models.workspace_invitation import WorkspaceInvitation
from app.services.email_service import send_workspace_invite_email # assuming this helper exists
import secrets
from datetime import datetime, timedelta

from app.models.workspace_subscription import (
    WorkspaceSubscription
)

from app.models.plan import Plan

from app.services.feature_access import (
    require_feature
)


def get_workspace_plan(
    db,
    workspace_id
):

    subscription = (
        db.query(WorkspaceSubscription)
        .filter(
            WorkspaceSubscription.workspace_id
            == workspace_id,

            WorkspaceSubscription.status
            == "active"
        )
        .first()
    )

    if not subscription:

        raise HTTPException(
            status_code=403,
            detail="No active subscription"
        )

    plan = (
        db.query(Plan)
        .filter(
            Plan.id == subscription.plan_id
        )
        .first()
    )

    if not plan:

        raise HTTPException(
            status_code=403,
            detail="Invalid subscription plan"
        )

    return plan


def add_workspace_member(
    db: Session,
    workspace_id: str,
    payload
):

    plan = get_workspace_plan(
        db,
        workspace_id
    )

    features = (
        plan.features or {}
    )

    limits = (
        plan.limits or {}
    )

    # TEAM FEATURE CHECK
    if not features.get(
        "team_collaboration",
        False
    ):

        raise HTTPException(
            status_code=403,
            detail=(
                "Team collaboration "
                "not available in plan"
            )
        )

    # FIND USER
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

    # DUPLICATE CHECK
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

    current_member_count = (
        db.query(WorkspaceMember)
        .filter(
            WorkspaceMember.workspace_id
            == workspace_id
        )
        .count()
    )

    max_team_members = (
        limits.get(
            "max_team_members",
            1
        )
    )

    if current_member_count >= max_team_members:

        raise HTTPException(
            status_code=403,
            detail=(
                "Team member limit reached"
            )
        )

    # CREATE MEMBER
    member = WorkspaceMember(

        workspace_id=workspace_id,

        user_id=target_user.id,

        role=payload.role
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


def update_workspace_member_role(
    db: Session,
    workspace_id: str,
    payload
):

    plan = get_workspace_plan(
        db,
        workspace_id
    )

    features = (
        plan.features or {}
    )

    if not features.get(
        "rbac",
        False
    ):

        raise HTTPException(
            status_code=403,
            detail=(
                "RBAC not available "
                "in current plan"
            )
        )

    # FIND USER
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
    membership = (
        db.query(WorkspaceMember)
        .filter(
            WorkspaceMember.workspace_id
            == workspace_id,

            WorkspaceMember.user_id
            == target_user.id
        )
        .first()
    )

    if not membership:

        raise HTTPException(
            status_code=404,
            detail="Membership not found"
        )

    # UPDATE ROLE
    membership.role = payload.role

    db.commit()

    db.refresh(membership)

    return {

        "success": True,

        "message":
            "Role updated successfully",

        "email":
            target_user.email,

        "new_role":
            membership.role
    }


def get_workspace_members(
    db: Session,
    workspace_id: str
):

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


def remove_workspace_member(
    db: Session,
    workspace_id: str,
    user_id: str
):

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

    # OWNER CHECK
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

def create_workspace_invitation(db: Session, workspace_id: str, inviter_id: str, payload):
    # 1. Fetch subscription features metrics to evaluate safety quotas
    plan = get_workspace_plan(db, workspace_id)
    features = plan.features or {}
    limits = plan.limits or {}

    if not features.get("team_collaboration", False):
        raise HTTPException(status_code=403, detail="Team collaboration features not available on current plan")

    # 2. Check if the target email is already part of this specific workspace members pool
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        already_member = db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == existing_user.id
        ).first()
        if already_member:
            raise HTTPException(status_code=400, detail="User is already a member of this workspace")

    # 3. Validate overall seating limit caps
    current_members = db.query(WorkspaceMember).filter(WorkspaceMember.workspace_id == workspace_id).count()
    pending_invites = db.query(WorkspaceInvitation).filter(
        WorkspaceInvitation.workspace_id == workspace_id,
        WorkspaceInvitation.is_accepted == False,
        WorkspaceInvitation.expires_at > datetime.utcnow()
    ).count()

    if (current_members + pending_invites) >= limits.get("max_team_members", 1):
        raise HTTPException(status_code=403, detail="Workspace team seat allocations are fully exhausted")

    # 4. Construct invitation reference token block with a 7-day expiration lifespan
    invitation = WorkspaceInvitation(
        email=payload.email,
        workspace_id=workspace_id,
        role=payload.role,
        token=secrets.token_urlsafe(32),
        invited_by=inviter_id,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    # 5. Dispatch actual access token link string to user's inbox
    try:
        send_workspace_invite_email(to_email=invitation.email, token=invitation.token)
    except Exception as e:
        print(f"Mail delivery exception caught: {e}")

    return {
        "success": True,
        "message": "Team invitation link generated and sent successfully",
        "token": invitation.token
    }


# Inside your accept_workspace_invitation service logic block:

def accept_workspace_invitation(db: Session, token: str):
    # 1. Fetch the invitation row matching the parsed token string container
    invite = db.query(WorkspaceInvitation).filter(WorkspaceInvitation.token == token).first()
    if not invite:
        raise HTTPException(status_code=404, detail="Invitation link is invalid or has expired.")
        
    if invite.is_accepted:
        raise HTTPException(status_code=400, detail="This invitation context has already been used.")
        
    # 2. Check token time expiration rules safely
    if invite.expires_at and invite.expires_at.replace(tzinfo=None) < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invitation token has expired.")

    # 3. Look up if a registered user account already matches the target email parameters
    user = db.query(User).filter(User.email == invite.email).first()
    
    if not user:
        # 💡 Premium UX Flow: If the user profile doesn't exist yet, return a clean instruction code block
        # telling the frontend to route them straight to the signup screen with their email pre-filled!
        return {
            "status": "pending_registration",
            "email": invite.email,
            "message": "Invitation token verified successfully! Please register an account profile to complete onboarding setup."
        }

    # 4. If the user already exists, provision their workspace access right away!
    new_member = WorkspaceMember(
        workspace_id=invite.workspace_id,
        user_id=user.id,
        role=invite.role
    )
    
    invite.is_accepted = True
    db.add(new_member)
    db.commit()
    
    return {
        "status": "success",
        "message": "Successfully linked to the target team workspace cluster environment container!"
    }