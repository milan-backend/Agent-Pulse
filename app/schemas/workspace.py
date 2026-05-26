from pydantic import (
    BaseModel,
    EmailStr
)

from app.db.enums import WorkspaceRole


class AddMemberRequest(BaseModel):

    email: EmailStr

    role: WorkspaceRole


class UpdateRoleRequest(BaseModel):

    email: EmailStr

    role: WorkspaceRole