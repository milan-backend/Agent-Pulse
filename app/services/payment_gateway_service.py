import os
import razorpay
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.workspace_subscription import WorkspaceSubscription

# Initialize Razorpay Client with environment variables safely
razorpay_client = razorpay.Client(
    auth=(os.getenv("RAZORPAY_KEY_ID", ""), os.getenv("RAZORPAY_KEY_SECRET", ""))
)

def create_gateway_checkout_session(db: Session, workspace_id: str, plan_name: str, gateway: str):
    # EXACT LOGIC: Verify workspace subscription row exists first, matching your old Stripe code
    subscription = (
        db.query(WorkspaceSubscription)
        .filter(WorkspaceSubscription.workspace_id == workspace_id)
        .first()
    )
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # Guard check for plans
    if plan_name not in ["pro", "enterprise"]:
        raise HTTPException(status_code=400, detail="Invalid plan name")

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # EXACT SUCCESS AND CANCEL URL LOGIC FROM YOUR STRIPE FILE
    success_url = f"{frontend_url}/dashboard/billing/success"
    cancel_url = f"{frontend_url}/dashboard/billing/cancel"

    # ============================================
    # GATEWAY: RAZORPAY (FOR INDIA)
    # ============================================
    if gateway == "razorpay":
        # Amount in paise (e.g., ₹999 = 99900 paise, ₹4999 = 499900 paise)
        amount = 99900 if plan_name == "pro" else 499900  
        
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
            
            # Returning order details along with exact success/cancel landing URLs for your frontend modal callback
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
            raise HTTPException(status_code=500, detail=f"Razorpay Order Error: {str(e)}")

    # ============================================
    # GATEWAY: GUMROAD (FOR OUTSIDE INDIA)
    # ============================================
    elif gateway == "gumroad":
        # Pulling your custom product URLs generated from Gumroad Dashboard
        if plan_name == "pro":
            gumroad_base_url = os.getenv("GUMROAD_PRO_PRODUCT_URL") 
        else:
            gumroad_base_url = os.getenv("GUMROAD_ENTERPRISE_PRODUCT_URL")

        if not gumroad_base_url:
            raise HTTPException(status_code=500, detail="Gumroad product configuration missing in .env")

        # Appending custom fields so Gumroad passes them back to your webhook along with return logic
        checkout_url = f"{gumroad_base_url}?workspace_id={workspace_id}&plan_name={plan_name}"
        
        return {
            "gateway": "gumroad",
            "checkout_url": checkout_url,
            "success_url": success_url,
            "cancel_url": cancel_url
        }

    else:
        raise HTTPException(status_code=400, detail="Invalid payment gateway selected")