from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.services.stripe_billing_service import (
    create_checkout_session
)

from app.models.workspace_subscription import (
    WorkspaceSubscription
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


@router.get("/current-plan")
def get_current_plan(
    workspace_id: str = Header(...),
    db: Session = Depends(get_db)
):

    subscription = (
        db.query(
            WorkspaceSubscription
        )
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
            status_code=404,
            detail="No active subscription"
        )

    plan = subscription.plan

    if not plan:

        raise HTTPException(
            status_code=404,
            detail="Plan not found"
        )

    return {

        "plan":
            plan.name,

        "status":
            subscription.status,

        "limits":
            plan.limits or {},

        "features":
            plan.features or {}
    }