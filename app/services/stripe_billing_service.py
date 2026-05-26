import os

import stripe

from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.models.workspace_subscription import (
    WorkspaceSubscription
)


stripe.api_key = os.getenv(
    "STRIPE_SECRET_KEY"
)


# ============================================
# CREATE CHECKOUT SESSION
# ============================================

def create_checkout_session(

    db: Session,

    workspace_id: str,

    plan_name: str

):

    subscription = (
        db.query(WorkspaceSubscription)
        .filter(
            WorkspaceSubscription.workspace_id
            == workspace_id
        )
        .first()
    )

    if not subscription:

        raise HTTPException(

            status_code=404,

            detail="Subscription not found"
        )

    # ============================================
    # PLAN PRICE IDS
    # ============================================

    if plan_name == "pro":

        price_id = os.getenv(
            "STRIPE_PRO_PRICE_ID"
        )

    elif plan_name == "enterprise":

        price_id = os.getenv(
            "STRIPE_ENTERPRISE_PRICE_ID"
        )

    else:

        raise HTTPException(

            status_code=400,

            detail="Invalid plan"
        )

    frontend_url = os.getenv(
        "FRONTEND_URL"
    )

    try:

        checkout_session = (
            stripe.checkout.Session.create(

                payment_method_types=[
                    "card"
                ],

                mode="subscription",

                line_items=[

                    {
                        "price":
                            price_id,

                        "quantity":
                            1
                    }
                ],

                success_url=(
                    f"{frontend_url}/"
                    "billing/success"
                ),

                cancel_url=(
                    f"{frontend_url}/"
                    "billing/cancel"
                ),

                metadata={

                    "workspace_id":
                        str(workspace_id),

                    "plan_name":
                        plan_name
                }
            )
        )

        return {

            "checkout_url":
                checkout_session.url
        }

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)
        )