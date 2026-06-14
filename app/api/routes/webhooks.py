import os
import uuid
import hmac
import hashlib
from hmac import compare_digest
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.plan import Plan
from app.models.workspace_subscription import WorkspaceSubscription

router = APIRouter()

@router.post("/razorpay")
async def razorpay_webhook(request: Request, db: Session = Depends(get_db)):
    # 1. Capture Raw Request Elements
    payload = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")
    secret = os.getenv("RAZORPAY_WEBHOOK_SECRET", "")

    print(f"--- [WEBHOOK RECEIVE ENGINE] ---")
    print(f"Incoming Signature Header: {signature}")

    # 2. Secure Signature Verification Check
    if not secret:
        print("CRITICAL EXCEPTION: RAZORPAY_WEBHOOK_SECRET is completely missing from your .env settings!")
        raise HTTPException(status_code=500, detail="Webhook configuration error")

    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()

    if not compare_digest(expected_signature, signature):
        print("SECURITY ALERT: Webhook Signature Verification Failed! Check your RAZORPAY_WEBHOOK_SECRET.")
        raise HTTPException(status_code=400, detail="Invalid webhook signature mapping")

    print("SUCCESS: Webhook signature verified securely.")

    # 3. Parse Event Body safely
    event_data = await request.json()
    event_type = event_data.get("event")
    print(f"Triggered Event Type from Razorpay: {event_type}")

    # We match against payment.captured (or order.paid based on your Razorpay dashboard webhook event settings)
    if event_type in ["payment.captured", "order.paid"]:
        
        # Pulling details depending on payload source entity
        payment_entity = event_data["payload"].get("payment", {}).get("entity", {})
        
        # Fallback to look at order notes if payment notes are hidden
        notes = payment_entity.get("notes", {})
        if not notes:
            order_entity = event_data["payload"].get("order", {}).get("entity", {})
            notes = order_entity.get("notes", {})

        print(f"Extracted Metadata Notes from transaction: {notes}")

        workspace_id_raw = notes.get("workspace_id")
        plan_name = notes.get("plan_name")

        if not workspace_id_raw or not plan_name:
            print("ERROR: Transaction went through but 'workspace_id' or 'plan_name' missing from metadata notes!")
            return {"status": "ignored", "reason": "missing workspace routing metadata references"}

        # Convert back safely to Python UUID just like your original code logic did
        try:
            workspace_id = uuid.UUID(workspace_id_raw)
        except Exception as uuid_err:
            print(f"ERROR: Failed parsing workspace string into UUID: {uuid_err}")
            return {"status": "error", "reason": "invalid uuid context compilation"}

        print(f"Routing activation sequence to Workspace ID: {workspace_id} for Plan: {plan_name}")

        # 4. Local Database Update Pipeline
        plan = db.query(Plan).filter(Plan.name == plan_name.lower().strip()).first()
        if not plan:
            print(f"ERROR: Plan matching the name '{plan_name}' was not found in your database tables!")
            return {"status": "error", "reason": f"Plan '{plan_name}' does not exist locally"}

        # Lookup mapping constraints from original Stripe template script
        subscription = db.query(WorkspaceSubscription).filter(
            WorkspaceSubscription.workspace_id == workspace_id
        ).first()

        payment_id = payment_entity.get("id", f"rzp_pay_{str(uuid.uuid4())[:12]}")

        if subscription:
            print(f"Modifying existing record entry. Old Plan ID: {subscription.plan_id}")
            subscription.plan_id = plan.id
            subscription.status = "active"
            subscription.stripe_customer_id = payment_entity.get("email", "razorpay_buyer")
            subscription.stripe_subscription_id = payment_id
        else:
            print("Creating brand new WorkspaceSubscription entry row layout.")
            subscription = WorkspaceSubscription(
                workspace_id=workspace_id,
                plan_id=plan.id,
                status="active",
                stripe_customer_id=payment_entity.get("email", "razorpay_buyer"),
                stripe_subscription_id=payment_id
            )
            db.add(subscription)

        db.commit()
        print(f"SUCCESS: Local Database Committed securely! Plan updated to '{plan_name}' status.")
        return {"status": "success", "message": "plan status updated actively"}

    print(f"Event '{event_type}' processed safely with no mutation parameters required.")
    return {"status": "ignored"}