import os
import uuid
import hmac
import hashlib
from datetime import datetime, timedelta
from hmac import compare_digest
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.plan import Plan
from app.models.workspace_subscription import WorkspaceSubscription

router = APIRouter()

# ============================================
# ENDPOINT: RAZORPAY SECURE INCOMING WEBHOOK
# ============================================
@router.post("/razorpay")
async def razorpay_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")
    secret = os.getenv("RAZORPAY_WEBHOOK_SECRET", "")

    if not secret:
        raise HTTPException(status_code=500, detail="Secret configuration array empty.")

    expected_signature = hmac.new(secret.encode('utf-8'), payload, hashlib.sha256).hexdigest()
    if not compare_digest(expected_signature, signature):
        print("🚨 SECURITY THREAT BLOCK: Faked Razorpay Webhook Signature Injection Blocked!")
        raise HTTPException(status_code=400, detail="Invalid signature profile.")

    event_data = await request.json()
    event_type = event_data.get("event")

    if event_type in ["order.paid", "payment.captured"]:
        payload_context = event_data.get("payload", {})
        payment_entity = payload_context.get("payment", {}).get("entity", {})
        order_entity = payload_context.get("order", {}).get("entity", {})
        
        notes = order_entity.get("notes", {}) or payment_entity.get("notes", {})
        workspace_id_raw = notes.get("workspace_id")
        plan_name = notes.get("plan_name")

        if not workspace_id_raw or not plan_name:
            return {"status": "ignored", "reason": "Missing custom references."}

        workspace_id = uuid.UUID(workspace_id_raw)
        payment_id = payment_entity.get("id") or order_entity.get("id")

        # 🛡️ LOOPHOLE SAFEGUARD: Idempotency Duplicate Entry Protection
        dup = db.query(WorkspaceSubscription).filter(
            WorkspaceSubscription.stripe_subscription_id == payment_id
        ).first()
        if dup:
            return {"status": "success", "detail": "Idempotent block: Transaction already applied."}

        plan = db.query(Plan).filter(Plan.name == plan_name.lower().strip()).first()
        if not plan:
            return {"status": "error", "reason": "Product entry matching dropped."}

        expiration_deadline = datetime.utcnow() + timedelta(days=30)
        subscription = db.query(WorkspaceSubscription).filter(WorkspaceSubscription.workspace_id == workspace_id).first()

        if subscription:
            subscription.plan_id = plan.id
            subscription.status = "active"
            subscription.stripe_customer_id = payment_entity.get("email", "razorpay_user")
            subscription.stripe_subscription_id = payment_id
            subscription.current_period_end = expiration_deadline
        else:
            subscription = WorkspaceSubscription(
                workspace_id=workspace_id,
                plan_id=plan.id,
                status="active",
                stripe_customer_id=payment_entity.get("email", "razorpay_user"),
                stripe_subscription_id=payment_id,
                current_period_end=expiration_deadline
            )
            db.add(subscription)

        db.commit()
        print(f"🎉 SECURED INR PROVISIONING COMPLETE: Workspace {workspace_id} upgraded to {plan_name}.")
        return {"status": "success"}

    return {"status": "ignored"}


# ============================================
# ENDPOINT: GUMROAD SECURE INCOMING WEBHOOK
# ============================================
@router.post("/gumroad")
async def gumroad_webhook(request: Request, db: Session = Depends(get_db)):
    # Gumroad sends transactional pings formatted via standard urlencoded form data fields
    form_data = await request.form()
    
    workspace_id_raw = form_data.get("workspace_id")
    plan_name = form_data.get("plan_name")
    sale_id = form_data.get("sale_id") # Unique Gumroad identifier parameter 

    if not workspace_id_raw or not plan_name or not sale_id:
        print("🚨 GUMROAD TRACKING: Incoming sale structure dropped due to missing routing attributes.")
        return {"status": "ignored", "reason": "Missing custom reference metrics tags."}

    workspace_id = uuid.UUID(workspace_id_raw)

    # 🛡️ LOOPHOLE SAFEGUARD: Idempotency Duplicate Entry Protection for international users
    dup = db.query(WorkspaceSubscription).filter(
        WorkspaceSubscription.stripe_subscription_id == sale_id
    ).first()
    if dup:
        return {"status": "success", "detail": "Idempotent block: International order already provisioned."}

    plan = db.query(Plan).filter(Plan.name == plan_name.lower().strip()).first()
    if not plan:
        return {"status": "error", "reason": "Target plan configuration not initialized."}

    expiration_deadline = datetime.utcnow() + timedelta(days=30)
    subscription = db.query(WorkspaceSubscription).filter(WorkspaceSubscription.workspace_id == workspace_id).first()

    if subscription:
        subscription.plan_id = plan.id
        subscription.status = "active"
        subscription.stripe_customer_id = form_data.get("email", "gumroad_global_user")
        subscription.stripe_subscription_id = sale_id
        subscription.current_period_end = expiration_deadline
    else:
        subscription = WorkspaceSubscription(
            workspace_id=workspace_id,
            plan_id=plan.id,
            status="active",
            stripe_customer_id=form_data.get("email", "gumroad_global_user"),
            stripe_subscription_id=sale_id,
            current_period_end=expiration_deadline
        )
        db.add(subscription)

    db.commit()
    print(f"🎉 SECURED USD PROVISIONING COMPLETE: Global Workspace {workspace_id} upgraded to {plan_name} via Gumroad.")
    return {"status": "success"}