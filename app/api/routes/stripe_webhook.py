import os
from datetime import datetime
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

        # Fetch additional subscription details using UTC timestamps
        current_period_end_dt = None

        if stripe_subscription_id:

            try:

                stripe_sub = stripe.Subscription.retrieve(
                    stripe_subscription_id
                )

                period_end_timestamp = stripe_sub.get(
                    "current_period_end"
                )

                if period_end_timestamp:

                    current_period_end_dt = (
                        datetime.utcfromtimestamp(
                            period_end_timestamp
                        )
                    )

            except Exception as e:

                print(
                    f"Failed to fetch stripe subscription details: {e}"
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

            if current_period_end_dt:

                subscription.current_period_end = (
                    current_period_end_dt
                )

        else:

            subscription = WorkspaceSubscription(

                workspace_id=workspace_id,

                plan_id=plan.id,

                status="active",

                stripe_customer_id=
                    stripe_customer_id,

                stripe_subscription_id=
                    stripe_subscription_id,

                current_period_end=current_period_end_dt
            )

            db.add(subscription)

        db.commit()

    # ============================================
    # SUBSCRIPTION UPDATED
    # ============================================

    elif event["type"] == "customer.subscription.updated":

        stripe_sub = event["data"]["object"]

        subscription = (
            db.query(WorkspaceSubscription)
            .filter(
                WorkspaceSubscription.stripe_subscription_id
                == stripe_sub["id"]
            )
            .first()
        )

        if subscription:

            subscription.status = (
                stripe_sub["status"]
            )

            if stripe_sub.get(
                "current_period_end"
            ):

                subscription.current_period_end = (
                    datetime.utcfromtimestamp(
                        stripe_sub[
                            "current_period_end"
                        ]
                    )
                )

            db.commit()

    # ============================================
    # SUBSCRIPTION DELETED
    # ============================================

    elif event["type"] == "customer.subscription.deleted":

        stripe_sub = event["data"]["object"]

        subscription = (
            db.query(WorkspaceSubscription)
            .filter(
                WorkspaceSubscription.stripe_subscription_id
                == stripe_sub["id"]
            )
            .first()
        )

        if subscription:

            free_plan = (
                db.query(Plan)
                .filter(
                    Plan.name == "free"
                )
                .first()
            )

            subscription.status = (
                "canceled"
            )

            if free_plan:

                subscription.plan_id = (
                    free_plan.id
                )

            db.commit()

    # ============================================
    # PAYMENT FAILED
    # ============================================

    elif event["type"] == "invoice.payment_failed":

        invoice = event["data"]["object"]

        stripe_subscription_id = (
            invoice.get(
                "subscription"
            )
        )

        if stripe_subscription_id:

            subscription = (
                db.query(
                    WorkspaceSubscription
                )
                .filter(
                    WorkspaceSubscription.stripe_subscription_id
                    == stripe_subscription_id
                )
                .first()
            )

            if subscription:

                subscription.status = (
                    "past_due"
                )

                db.commit()

    # ============================================
    # PAYMENT SUCCEEDED (RENEWAL SUCCESS)
    # ============================================

    elif event["type"] == "invoice.paid":

        invoice = event["data"]["object"]

        stripe_subscription_id = (
            invoice.get(
                "subscription"
            )
        )

        if stripe_subscription_id:

            subscription = (
                db.query(
                    WorkspaceSubscription
                )
                .filter(
                    WorkspaceSubscription.stripe_subscription_id
                    == stripe_subscription_id
                )
                .first()
            )

            if subscription:

                subscription.status = "active"

                try:

                    # Sync subscription period extension from Stripe on successful renewal payment

                    stripe_sub = stripe.Subscription.retrieve(
                        stripe_subscription_id
                    )

                    if stripe_sub.get(
                        "current_period_end"
                    ):

                        subscription.current_period_end = (
                            datetime.utcfromtimestamp(
                                stripe_sub[
                                    "current_period_end"
                                ]
                            )
                        )

                except Exception as e:

                    print(
                        f"Failed to refresh period end during invoice.paid: {e}"
                    )

                db.commit()

    return {
        "status": "success"
    }


# ============================================
# ACTIVE SUBSCRIPTION FETCHING HELPER
# ============================================

def get_active_subscription(
    workspace_id,
    db: Session
):
    """
    Fetches the workspace subscription details if active.
    Returns the subscription object if valid,
    otherwise returns None.
    """

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

    if not subscription:
        return None

    if subscription.status != "active":
        return None

    return subscription