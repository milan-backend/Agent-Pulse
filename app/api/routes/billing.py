from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.workspace_subscription import WorkspaceSubscription
from app.services.payment_gateway_service import create_gateway_checkout_session

router = APIRouter()

@router.post("/checkout/{plan_name}")
def create_checkout(
    plan_name: str,
    gateway: str,  # Passed dynamically via frontend execution query strings ("razorpay" or "paddle")
    workspace_id: str = Header(...),
    db: Session = Depends(get_db)
):
    return create_gateway_checkout_session(
        db=db,
        workspace_id=workspace_id,
        plan_name=plan_name,
        gateway=gateway
    )

@router.get("/current-plan")
def get_current_plan(workspace_id: str = Header(...), db: Session = Depends(get_db)):
    subscription = db.query(WorkspaceSubscription).filter(
        WorkspaceSubscription.workspace_id == workspace_id
    ).first()

    if not subscription:
        raise HTTPException(status_code=404, detail="No billing record discovered.")

    # Safe Lazy-Expiration Validation Check Loophole Safeguard
    from datetime import datetime
    if subscription.status == "active" and subscription.current_period_end:
        if datetime.utcnow() > subscription.current_period_end:
            from app.models.plan import Plan
            free_plan = db.query(Plan).filter(Plan.name == "free").first()
            subscription.status = "canceled"
            if free_plan:
                subscription.plan_id = free_plan.id
            subscription.stripe_subscription_id = None
            db.commit()

    plan = subscription.plan
    if not plan:
        raise HTTPException(status_code=404, detail="Plan configuration dropped.")

    return {
        "plan": plan.name,
        "status": subscription.status,
        "limits": plan.limits or {},
        "features": plan.features or {}
    }