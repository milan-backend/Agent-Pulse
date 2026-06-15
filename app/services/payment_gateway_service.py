import os
import razorpay
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.workspace_subscription import WorkspaceSubscription

# Initialize Razorpay Client with live environment configs
razorpay_client = razorpay.Client(
    auth=(os.getenv("RAZORPAY_KEY_ID", ""), os.getenv("RAZORPAY_KEY_SECRET", ""))
)

def create_gateway_checkout_session(db: Session, workspace_id: str, plan_name: str, gateway: str):
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

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    success_url = f"{frontend_url}/dashboard/billing/success"
    cancel_url = f"{frontend_url}/dashboard/billing/cancel"

    # ============================================
    # GATEWAY ROUTING: RAZORPAY (INDIA - ₹ INR)
    # ============================================
    if gateway == "razorpay":
        # INR Pricing mapped in total Paise units (₹2499 and ₹16999)
        amount = 249900 if plan_name == "pro" else 1699900  
        
        try:
            order_data = {
                "amount": amount,
                "currency": "INR",
                "receipt": f"rcpt_{str(workspace_id)[:20]}",
                "notes": {
                    "workspace_id": str(workspace_id),
                    "plan_name": plan_name
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
    # GATEWAY ROUTING: GUMROAD (GLOBAL - $ USD)
    # ============================================
    elif gateway == "gumroad":
        # Fetch your distinct static Gumroad redirect payment URLs from your environment variables
        if plan_name == "pro":
            gumroad_base_url = os.getenv("GUMROAD_PRO_PRODUCT_URL") # e.g. https://yourname.gumroad.com/l/proplan
        else:
            gumroad_base_url = os.getenv("GUMROAD_ENTERPRISE_PRODUCT_URL")

        if not gumroad_base_url:
            raise HTTPException(status_code=500, detail="Gumroad product string missing inside .env variables.")

        # Secure query parameter nesting context mapping
        checkout_url = f"{gumroad_base_url}?workspace_id={str(workspace_id)}&plan_name={plan_name}"
        
        return {
            "gateway": "gumroad",
            "checkout_url": checkout_url,
            "success_url": success_url,
            "cancel_url": cancel_url
        }

    else:
        raise HTTPException(status_code=400, detail="Selected target gateway variation is unauthorized.")