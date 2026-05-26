from fastapi import HTTPException


ROLE_HIERARCHY = {
    "viewer": 1,
    "operator": 2,
    "admin": 3
}


def require_role(
    membership,
    minimum_role: str
):

    user_level = ROLE_HIERARCHY.get(
        membership.role,
        0
    )

    required_level = ROLE_HIERARCHY.get(
        minimum_role,
        0
    )

    if user_level < required_level:

        raise HTTPException(
            status_code=403,
            detail=f"{minimum_role.capitalize()} access required"
        )


def require_viewer(
    membership
):
    require_role(
        membership,
        "viewer"
    )


def require_operator(
    membership
):
    require_role(
        membership,
        "operator"
    )


def require_admin(
    membership
):
    require_role(
        membership,
        "admin"
    )