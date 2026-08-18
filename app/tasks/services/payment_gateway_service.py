import os
import razorpay
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.workspace_subscription import WorkspaceSubscription

# Initialize Razorpay Client with live environment configs
razorpay_client = razorpay.Client(
    auth=(os.getenv("RAZORPAY_KEY_ID", ""), os.getenv("RAZORPAY_KEY_SECRET", ""))
)

def create_gateway_checkout_session(db: Session, workspace_id: str, plan_name: str, gateway: str, billing_cycle: str = "monthly"):
    # SECURITY ASPECT: Guarantee reference workspace constraint validation
    subscription = (
        db.query(WorkspaceSubscription)
        .filter(WorkspaceSubscription.workspace_id == workspace_id)
        .first()
    )
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription workspace node not found.")

    if plan_name not in ["pro", "enterprise"]:
        raise HTTPException(status_code=400, detail="Invalid plan scope selection.")
        
    if billing_cycle not in ["monthly", "yearly"]:
        raise HTTPException(status_code=400, detail="Invalid billing cycle selection.")

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    success_url = f"{frontend_url}/dashboard/billing/success"
    cancel_url = f"{frontend_url}/dashboard/billing/cancel"

    # ============================================
    # GATEWAY ROUTING: RAZORPAY (INDIA - ₹ INR)
    # ============================================
    if gateway == "razorpay":
        # Dynamic INR Pricing mapped in total Paise units based on billing cycle
        if plan_name == "pro":
            # 💡 Fixed Parity: ₹2,740/mo or ₹26,085/yr (Perfect match with $29 and $23 plans)
            amount = 274000 if billing_cycle == "monthly" else 2608500  
        else:
            # 💡 Fixed Parity: ₹18,805/mo or ₹1,80,300/yr (Perfect match with $199 and $159 plans)
            amount = 1880500 if billing_cycle == "monthly" else 18030000  
        
        try:
            order_data = {
                "amount": amount,
                "currency": "INR",
                "receipt": f"rcpt_{str(workspace_id)[:20]}",
                "notes": {
                    "workspace_id": str(workspace_id),
                    "plan_name": plan_name,
                    "billing_cycle": billing_cycle  # Webhook will read this to set correct access duration
                }
            }
            razorpay_order = razorpay_client.order.create(data=order_data)
            
            return {
                "gateway": "razorpay",
                "order_id": razorpay_order["id"],
                "amount": razorpay_order["amount"],
                "currency": razorpay_order["currency"],
                "key_id": os.getenv("RAZORPAY_KEY_ID"),
                "success_url": success_url,
                "cancel_url": cancel_url
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Razorpay Order Fault: {str(e)}")

    # ============================================
    # GATEWAY ROUTING: PADDLE (GLOBAL - $ USD)
    # ============================================
    elif gateway == "paddle":
        # Fetch the distinct Paddle Price IDs based on both Plan and Billing Cycle
        if plan_name == "pro":
            price_id = (
                os.getenv("PADDLE_PRO_MONTHLY_PRICE_ID")
                if billing_cycle == "monthly"
                else os.getenv("PADDLE_PRO_YEARLY_PRICE_ID")
            )
        else:
            price_id = (
                os.getenv("PADDLE_ENTERPRISE_PRICE_ID")  # Defaults to standard monthly variable name if preferred
                if billing_cycle == "monthly"
                else os.getenv("PADDLE_ENTERPRISE_YEARLY_PRICE_ID")
            )

        if not price_id:
            raise HTTPException(
                status_code=500,
                detail=f"Paddle Price ID for '{plan_name}' ({billing_cycle}) missing inside environment variables."
            )

        # Return parameters for frontend Paddle.js initialization
        return {
            "gateway": "paddle",
            "environment": os.getenv("PADDLE_ENVIRONMENT", "sandbox"),
            "client_token": os.getenv("PADDLE_CLIENT_TOKEN"),
            "price_id": price_id,
            "success_url": success_url,
            "cancel_url": cancel_url,
            "custom_data": {
                "workspace_id": str(workspace_id),
                "plan_name": plan_name,
                "billing_cycle": billing_cycle  # Paddle pass-through metadata
            }
        }

    else:
        raise HTTPException(status_code=400, detail="Selected target gateway variation is unauthorized.")