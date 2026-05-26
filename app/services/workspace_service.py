from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_member import (
    WorkspaceMember
)

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