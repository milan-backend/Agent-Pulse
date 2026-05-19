from fastapi import HTTPException


def require_admin(membership):

    if membership.role != "admin":

        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )


def require_operator(membership):

    if membership.role not in [
        "operator",
        "admin"
    ]:

        raise HTTPException(
            status_code=403,
            detail="Operator access required"
        )


def require_viewer(membership):

    if membership.role not in [
        "viewer",
        "operator",
        "admin"
    ]:

        raise HTTPException(
            status_code=403,
            detail="Viewer access required"
        )