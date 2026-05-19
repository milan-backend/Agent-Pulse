import os

from datetime import (
    datetime,
    timedelta
)

from dotenv import load_dotenv

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from jose import jwt

from passlib.hash import bcrypt

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.models.user import User
from app.models.agent import Agent
from app.models.workspace import Workspace
from app.models.workspace_member import (
    WorkspaceMember
)

from app.schemas.auth import SignupRequest

from app.core.security import (
    generate_api_key,
    hash_api_key
)


# LOAD ENV

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

ALGORITHM = os.getenv("ALGORITHM")


router = APIRouter()


# SIGNUP

@router.post("/signup")
def signup(
    request: SignupRequest,
    db: Session = Depends(get_db)
):

    # CHECK EXISTING USER

    existing = (
        db.query(User)
        .filter(
            User.email == request.email
        )
        .first()
    )

    if existing:

        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    # CREATE WORKSPACE

    workspace = Workspace(
        name=f"{request.name}'s Workspace",
        type="personal"
    )

    db.add(workspace)

    db.flush()

    # CREATE USER

    user = User(
        name=request.name,

        email=request.email,

        password_hash=bcrypt.hash(
            request.password
        )
    )

    db.add(user)

    db.flush()

    # SET WORKSPACE OWNER

    workspace.owner_id = user.id

    # CREATE MEMBERSHIP

    membership = WorkspaceMember(
        workspace_id=workspace.id,

        user_id=user.id,

        role="admin"
    )

    db.add(membership)

    # GENERATE API KEY

    raw_api_key, key_id = (
        generate_api_key()
    )

    # HASH API KEY

    hashed_api_key = hash_api_key(
        raw_api_key
    )

    # CREATE DEFAULT AGENT

    agent = Agent(
        name=f"{request.name}-agent",

        api_key_hash=hashed_api_key,

        key_id=key_id,

        user_id=user.id,

        workspace_id=workspace.id
    )

    db.add(agent)

    db.commit()

    db.refresh(user)

    db.refresh(workspace)

    return {

        "message":
            "Signup successful",

        "user_id":
            str(user.id),

        "workspace_id":
            str(workspace.id),

        "role":
            "admin",

        "api_key":
            raw_api_key
    }


# LOGIN

@router.post("/login")
def login(
    request: SignupRequest,
    db: Session = Depends(get_db)
):

    # FIND USER

    user = (
        db.query(User)
        .filter(
            User.email == request.email
        )
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    # VERIFY PASSWORD

    valid = bcrypt.verify(
        request.password,
        user.password_hash
    )

    if not valid:

        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    # GET ALL MEMBERSHIPS

    memberships = (
        db.query(WorkspaceMember)
        .filter(
            WorkspaceMember.user_id
            == user.id
        )
        .all()
    )

    if not memberships:

        raise HTTPException(
            status_code=403,
            detail="No workspace membership found"
        )

    # BUILD WORKSPACE LIST

    workspace_list = []

    for member in memberships:

        workspace = (
            db.query(Workspace)
            .filter(
                Workspace.id
                == member.workspace_id
            )
            .first()
        )

        if workspace:

            workspace_list.append({

                "workspace_id":
                    str(workspace.id),

                "workspace_name":
                    workspace.name,

                "role":
                    member.role
            })

    # DEFAULT WORKSPACE

    default_membership = memberships[0]

    # CREATE JWT PAYLOAD

    payload = {

        "sub":
            str(user.id),

        "exp":
            datetime.utcnow() +
            timedelta(days=7)
    }

    # GENERATE TOKEN

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {

        "access_token":
            token,

        "token_type":
            "bearer",

        "user_id":
            str(user.id),

        # DEFAULT ACTIVE WORKSPACE
        "workspace_id":
            str(
                default_membership.workspace_id
            ),

        "role":
            default_membership.role,

        # ALL WORKSPACES
        "workspaces":
            workspace_list
    }


# TEST AUTH

@router.get("/me")
def me():

    return {

        "message":
            "Auth working"
    }