import os
import stripe

from fastapi import (
    APIRouter,
    Request,
    HTTPException,
    Depends
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.models.plan import Plan

from app.models.workspace_subscription import (
    WorkspaceSubscription
)

router = APIRouter()

stripe.api_key = os.getenv(
    "STRIPE_SECRET_KEY"
)

endpoint_secret = os.getenv(
    "STRIPE_WEBHOOK_SECRET"
)


# ============================================
# STRIPE WEBHOOK
# ============================================

@router.post("/webhook")
async def stripe_webhook(

    request: Request,

    db: Session = Depends(get_db)
):

    payload = await request.body()

    sig_header = request.headers.get(
        "stripe-signature"
    )

    try:

        event = stripe.Webhook.construct_event(

            payload,

            sig_header,

            endpoint_secret
        )

    except Exception as e:

        raise HTTPException(

            status_code=400,

            detail=str(e)
        )

    # ============================================
    # CHECKOUT SESSION COMPLETED
    # ============================================

    if event["type"] == "checkout.session.completed":

        session = event["data"]["object"]

        metadata = session["metadata"]

        workspace_id_raw = metadata[
            "workspace_id"
        ]

        plan_name = metadata[
            "plan_name"
        ]

        import uuid

        workspace_id = uuid.UUID(
            workspace_id_raw
        )

        stripe_customer_id = (
            session["customer"]
        )

        stripe_subscription_id = (
            session["subscription"]
        )

        plan = (
            db.query(Plan)
            .filter(
                Plan.name == plan_name
            )
            .first()
        )

        if not plan:

            return {
                "status": "plan not found"
            }

        subscription = (
            db.query(
                WorkspaceSubscription
            )
            .filter(
                WorkspaceSubscription.workspace_id
                == workspace_id
            )
            .first()
        )

        if subscription:

            subscription.plan_id = plan.id

            subscription.status = "active"

            subscription.stripe_customer_id = (
                stripe_customer_id
            )

            subscription.stripe_subscription_id = (
                stripe_subscription_id
            )

        else:

            subscription = WorkspaceSubscription(

                workspace_id=workspace_id,

                plan_id=plan.id,

                status="active",

                stripe_customer_id=
                    stripe_customer_id,

                stripe_subscription_id=
                    stripe_subscription_id
            )

            db.add(subscription)

        db.commit()

    return {
        "status": "success"
    }