from enum import Enum

from pydantic import (
    BaseModel,
    EmailStr
)


# =========================
# WORKSPACE ROLE ENUM
# =========================

class WorkspaceRole(str, Enum):

    viewer = "viewer"

    operator = "operator"

    admin = "admin"


# =========================
# ADD MEMBER REQUEST
# =========================

class AddMemberRequest(BaseModel):

    email: EmailStr

    role: WorkspaceRole


# =========================
# UPDATE ROLE REQUEST
# =========================

class UpdateRoleRequest(BaseModel):

    email: EmailStr

    role: WorkspaceRole