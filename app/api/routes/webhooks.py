import os
import uuid
import hmac
import hashlib
from datetime import datetime, timedelta
from hmac import compare_digest
from fastapi import APIRouter, Request, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.plan import Plan
from app.models.workspace_subscription import WorkspaceSubscription

router = APIRouter()

def verify_paddle_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Validates the cryptographic header hash sent by Paddle Sandbox to block fake injection attacks.
    Paddle signatures arrive formatted inside a standard 'ts=12345;h=hashvalue' structural array string.
    """
    if not signature or ":" not in signature:
        return False
        
    try:
        parts = dict(item.split("=") for item in signature.split(";"))
        timestamp = parts.get("ts")
        provided_hash = parts.get("h")
        
        if not timestamp or not provided_hash:
            return False
            
        # Re-verify the verification payload template sequence
        signed_payload = f"{timestamp}:{payload.decode('utf-8')}"
        computed_hash = hmac.new(
            secret.encode('utf-8'),
            signed_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return compare_digest(computed_hash, provided_hash)
    except Exception:
        return False


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
# ENDPOINT: PADDLE SECURE INCOMING WEBHOOK [REPLACED GUMROAD]
# ============================================
@router.post("/paddle")
async def paddle_webhook(
    request: Request, 
    paddle_signature: str = Header(None), 
    db: Session = Depends(get_db)
):
    raw_body = await request.body()
    webhook_secret = os.getenv("PADDLE_WEBHOOK_SECRET", "")

    if not webhook_secret:
        raise HTTPException(status_code=500, detail="Paddle verification webhook secret token missing inside server .env config arrays.")

    # 🛡️ COUNTERPART VALIDATION GUARD: Drop unverified faked network payload dispatches instantly
    if not verify_paddle_webhook_signature(raw_body, paddle_signature, webhook_secret):
        print("🚨 SECURITY THREAT BLOCK: Faked Paddle Webhook Verification Request Blocked!")
        raise HTTPException(status_code=401, detail="Invalid webhook signature provenance profile.")

    event_data = await request.json()
    event_type = event_data.get("event_type")

    # Capture both baseline checkout conversions and automatic cycle transaction executions
    if event_type in ["transaction.completed", "subscription.created"]:
        data_object = event_data.get("data", {})
        custom_data = data_object.get("custom_data", {})
        
        workspace_id_raw = custom_data.get("workspace_id")
        plan_name = custom_data.get("plan_name")
        paddle_id = data_object.get("id") # Unique dynamic transactional record handle string

        if not workspace_id_raw or not plan_name or not paddle_id:
            print("⚠️ PADDLE HOOK WARNING: Missing transaction contextual metadata identifiers.")
            return {"status": "ignored", "reason": "Missing operational context parameters attributes."}

        workspace_id = uuid.UUID(workspace_id_raw)

        # 🛡️ LOOPHOLE SAFEGUARD: Idempotency Entry Tracking Constraint Enforcement
        dup = db.query(WorkspaceSubscription).filter(
            WorkspaceSubscription.stripe_subscription_id == paddle_id
        ).first()
        if dup:
            return {"status": "success", "detail": "Idempotent block: Transaction already successfully evaluated."}

        plan = db.query(Plan).filter(Plan.name == plan_name.lower().strip()).first()
        if not plan:
            return {"status": "error", "reason": "Target global tier identifier dropped from system models configuration arrays."}

        expiration_deadline = datetime.utcnow() + timedelta(days=30)
        subscription = db.query(WorkspaceSubscription).filter(WorkspaceSubscription.workspace_id == workspace_id).first()

        customer_email = data_object.get("customer", {}).get("email", "paddle_global_user")

        if subscription:
            subscription.plan_id = plan.id
            subscription.status = "active"
            subscription.stripe_customer_id = customer_email
            subscription.stripe_subscription_id = paddle_id
            subscription.current_period_end = expiration_deadline
        else:
            subscription = WorkspaceSubscription(
                workspace_id=workspace_id,
                plan_id=plan.id,
                status="active",
                stripe_customer_id=customer_email,
                stripe_subscription_id=paddle_id,
                current_period_end=expiration_deadline
            )
            db.add(subscription)

        db.commit()
        print(f"🎉 SECURED USD PROVISIONING COMPLETE: Global Workspace {workspace_id} upgraded to {plan_name} via Paddle Sandbox.")
        return {"status": "success"}

    return {"status": "ignored", "message": f"Event type '{event_type}' unmapped inside execution router endpoints rules."}