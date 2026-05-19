from fastapi import HTTPException

from app.models.workspace_member import (
    WorkspaceMember
)


def get_workspace_membership(
    db,
    user_id,
    workspace_id
):

    membership = (
        db.query(WorkspaceMember)
        .filter(
            WorkspaceMember.user_id == user_id,
            WorkspaceMember.workspace_id == workspace_id
        )
        .first()
    )

    if not membership:

        raise HTTPException(
            status_code=403,
            detail="Not part of workspace"
        )

    return membership