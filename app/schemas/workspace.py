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


from pydantic import EmailStr # Ensure this is imported if not already there

class InviteMemberRequest(BaseModel):
    email: EmailStr
    role: str          # Must pass your enum strings: "admin", "operator", or "viewer"

class AcceptInviteRequest(BaseModel):
    token: str         # The secure token string parsed from the invitation URL link