from fastapi import (
    APIRouter,
    Depends,
    Header
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.services.stripe_billing_service import (
    create_checkout_session
)

router = APIRouter()


# ============================================
# CREATE CHECKOUT SESSION
# ============================================

@router.post("/checkout/{plan_name}")
def create_checkout(

    plan_name: str,

    workspace_id: str = Header(...),

    db: Session = Depends(get_db)
):

    return create_checkout_session(

        db=db,

        workspace_id=workspace_id,

        plan_name=plan_name
    )