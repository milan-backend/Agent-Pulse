from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps_user import get_current_user
from app.db.session import get_db
from app.models.agent import Agent

router = APIRouter()


@router.post("/agents/kill")
async def kill_agents(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

   
    updated_count = db.query(Agent).update(
        {"is_killed": True},
        synchronize_session=False
    )

    db.commit()

    return {
        "message": "Emergency stop activated",
        "killed_agents": updated_count,
        "user": current_user.email
    }


@router.post("/agents/resume")
async def resume_agents(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    updated_count = db.query(Agent).update(
        {"is_killed": False},
        synchronize_session=False
    )

    db.commit()

    return {
        "message": "Agents resumed",
        "resumed_agents": updated_count,
        "user": current_user.email
    }